"""Deterministic intent classification for demo mode.

Three layers, first match wins, in precedence order:

1. L1 — exact signals: order-number regex / order keywords -> "order";
   explicit handoff keywords -> "handoff". The brief defines handoff as an
   EXPLICIT request, so keyword matching (not semantics) is correct here.
2. L2 — semantic: embed the message with the shared model and score it against
   prototype phrases per intent. Route on the best intent only if it clears a
   threshold AND beats the runner-up by a margin; a thin margin asks for
   clarification instead of guessing.
3. L3 — fallback.

If the embedder can't load, L2 degrades to keyword matching so the demo never
hard-fails.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_ORDER_RE = re.compile(r"#?\b\d{2,}\b")
_ORDER_HINTS = ("order", "track", "package", "delivery status", "where is my", "where's my", "shipped yet", "arrive")
_HANDOFF_PATTERNS = (
    "human", "real person", "a person", "representative", "agent",
    "speak to someone", "talk to someone", "talk to a person", "live agent",
)

# 8–12 prototype phrases per semantic intent. Mean-of-top-3 similarity scores it.
_PROTOTYPES: dict[str, list[str]] = {
    "returns": [
        "I want to return this", "how do refunds work", "can I exchange it",
        "what is your return policy", "send this back for a refund",
        "return an item", "exchange for a different size", "money back",
        "this doesn't fit can I return it", "start a return",
    ],
    "shipping": [
        "how long does shipping take", "delivery options", "when will it arrive",
        "do you offer expedited shipping", "shipping cost", "how fast is delivery",
        "standard shipping time", "how much for faster delivery",
    ],
    "recommend": [
        "what should I buy", "recommend a tent", "suggest a sleeping bag",
        "I need gear for backpacking", "gift for a hiker", "best jacket for cold",
        "what do you have for car camping", "help me pick a backpack",
        "recommend gear for a winter trip", "which boots for day hikes",
    ],
    "greeting": [
        "hi", "hello", "hey there", "good morning", "howdy", "hi there",
    ],
}

# Chosen to clear the labeled-accuracy bar in tests/test_intent.py.
_CLEAR_THRESHOLD = 0.30
_MARGIN = 0.05


@dataclass
class IntentDecision:
    intent: str
    confidence: float
    needs_clarification: bool = False


def extract_order_number(message: str) -> str:
    """First 2+ digit run, '#' stripped; '' if none."""
    match = re.search(r"\d{2,}", message or "")
    return match.group(0) if match else ""


def _has_order_signal(text: str) -> bool:
    if _ORDER_RE.search(text):
        return True
    return any(hint in text for hint in _ORDER_HINTS)


def _semantic_scores(message: str) -> dict[str, float]:
    """Mean-of-top-3 cosine similarity per intent. {} if embedding unavailable."""
    try:
        from app.embeddings import get_embedder

        model = get_embedder()
        flat: list[str] = []
        owners: list[str] = []
        for intent, phrases in _PROTOTYPES.items():
            flat.extend(phrases)
            owners.extend([intent] * len(phrases))
        proto_vecs = _proto_cache(model, tuple(flat))
        q = model.encode([message], normalize_embeddings=True)[0]
        sims = proto_vecs @ q  # cosine on normalized vectors
        by_intent: dict[str, list[float]] = {k: [] for k in _PROTOTYPES}
        for owner, s in zip(owners, sims):
            by_intent[owner].append(float(s))
        return {k: sum(sorted(v, reverse=True)[:3]) / min(3, len(v)) for k, v in by_intent.items()}
    except Exception:  # noqa: BLE001 — degrade to keyword matching, never crash the demo
        return {}


# Prototype embeddings depend only on the (immutable) phrase list; cache them.
from functools import lru_cache  # noqa: E402 — kept near its use


@lru_cache(maxsize=1)
def _proto_cache(model, flat: tuple[str, ...]):
    return model.encode(list(flat), normalize_embeddings=True)


def _keyword_fallback(text: str) -> IntentDecision:
    """Used when embeddings are unavailable."""
    table = {
        "returns": ("return", "refund", "exchange"),
        "shipping": ("ship", "delivery", "deliver"),
        "recommend": ("recommend", "suggest", "buy", "gift", "gear"),
        "greeting": ("hi", "hello", "hey"),
    }
    for intent, words in table.items():
        if any(w in text for w in words):
            return IntentDecision(intent, 0.5)
    return IntentDecision("fallback", 0.0)


def classify(message: str) -> IntentDecision:
    text = (message or "").lower().strip()
    if not text:
        return IntentDecision("fallback", 0.0)

    # L1 — deterministic, highest precedence.
    if any(p in text for p in _HANDOFF_PATTERNS):
        return IntentDecision("handoff", 1.0)
    if _has_order_signal(text):
        return IntentDecision("order", 1.0)

    # L2 — semantic with margin logic.
    scores = _semantic_scores(text)
    if not scores:
        return _keyword_fallback(text)
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    best_intent, best = ranked[0]
    runner = ranked[1][1] if len(ranked) > 1 else 0.0
    if best >= _CLEAR_THRESHOLD:
        if best - runner < _MARGIN:
            return IntentDecision(best_intent, best, needs_clarification=True)
        return IntentDecision(best_intent, best)

    # L3 — fallback.
    return IntentDecision("fallback", best)
