"""Deterministic stand-in for the Anthropic client used in demo mode.

`MockAnthropic.messages.create()` mimics the parts of the SDK response that
`run_agent` reads (`.stop_reason`, `.content` blocks) and emits the SAME tool
calls the real model would — get_order_status / escalate_to_human /
flag_not_understood — so order lookup, escalation, the 2-fallback rule, ticket
creation, and transcript persistence all run through the real code paths.

Multi-turn state is derived from the `messages` history that run_agent passes
in (the previous assistant turn), so no Session changes are required.
"""

from __future__ import annotations

import re
from types import SimpleNamespace

from app import intent

# Canonical copy (mirrors the knowledge base / brief mock data).
_RETURNS_REPLY = (
    "Our return policy is straightforward: you have 30 days to return unused "
    "items in their original packaging. You can start a return here: "
    "https://northstar.example/returns. Anything else I can help with?"
)
_SHIPPING_REPLY = (
    "We offer two options: standard shipping (3–5 business days) and expedited "
    "shipping (1–2 business days). Want me to check a specific order for you?"
)
_GREETING_REPLY = (
    "Hi! I'm the North Star Guide. I can track an order, explain returns and "
    "shipping, recommend gear, or connect you with a human. What do you need?"
)
_CLARIFY_RECO = (
    "Happy to help you find the right gear! What are you heading out for "
    "(backpacking, car camping, or day hikes), and what conditions — summer, "
    "shoulder-season, or deep cold?"
)
_ORDER_ASK = "Sure — what's your order number? (Try #111, #222, or #333.)"
_FALLBACK_LINE = (
    "Sorry, I didn't quite catch that. I can help with order tracking, returns "
    "and exchanges, shipping, product recommendations, or connecting you with a "
    "human. Which would you like?"
)
_AMBIGUOUS_CLARIFY = (
    "Happy to help! Is that about an order, a return, shipping, or a product "
    "recommendation?"
)

# Small in-code catalog for semantic recommendation (mirrors products.md).
# (name, price, category, blurb) — category mirrors the products.md sections.
_CATALOG = [
    ("Wildwood 3P Tent", 349, "Tents", "a three-season, two-vestibule shelter under 5 lbs — great for backpacking and car camping in summer to shoulder-season"),
    ("Polaris -10° Bag", 219, "Sleeping Bags", "a mummy-cut down sleeping bag rated for frosty nights — best for deep cold and shoulder-season backpacking"),
    ("Summit Down Parka", 289, "Insulated Jackets", "an 800-fill down parka for alpine cold — best for deep-cold conditions"),
    ("Aurora Base Layer", 64, "Insulated Jackets", "a versatile merino base layer for any trip"),
    ("Granite GTX Boots", 199, "Hiking Footwear", "waterproof leather mids with a grippy sole — great for day hikes and rugged, wet terrain"),
    ("Trailhead 45 Pack", 179, "Backpacks", "a ventilated weekend pack — ideal for two-to-three-day backpacking trips"),
]

# Category keyword patterns, word-bounded so "backpacking" does NOT match "pack".
# Checked in order; first hit wins.
_CATEGORY_PATTERNS = [
    ("Tents", r"\btents?\b|\bshelters?\b"),
    ("Sleeping Bags", r"\bsleeping bags?\b|\bsleeping\b|\bbags?\b"),
    ("Insulated Jackets", r"\bjackets?\b|\bparkas?\b|\bdown\b|\bbase ?layers?\b|\blayers?\b|\binsulat"),
    ("Hiking Footwear", r"\bboots?\b|\bfootwear\b|\bshoes?\b"),
    ("Backpacks", r"\bbackpacks?\b|\bpacks?\b|\bdaypacks?\b"),
]


def _detect_category(text: str) -> str | None:
    """Return the catalog category the shopper explicitly named, if any."""
    low = (text or "").lower()
    for category, pattern in _CATEGORY_PATTERNS:
        if re.search(pattern, low):
            return category
    return None


def _text(text: str):
    return SimpleNamespace(type="text", text=text)


def _tool(name: str, tool_id: str, **inputs):
    return SimpleNamespace(type="tool_use", name=name, id=tool_id, input=inputs)


def _resp(stop_reason: str, content: list):
    return SimpleNamespace(stop_reason=stop_reason, content=content)


def _last_user_text(messages: list) -> str:
    for m in reversed(messages):
        if m.get("role") == "user" and isinstance(m.get("content"), str):
            return m["content"]
    return ""


def _prev_assistant_text(messages: list) -> str:
    """Assistant text from the most recent assistant turn (for multi-turn flow)."""
    for m in reversed(messages):
        if m.get("role") == "assistant" and isinstance(m.get("content"), str):
            return m["content"]
    return ""


def _is_tool_result_turn(messages: list) -> bool:
    last = messages[-1] if messages else {}
    content = last.get("content")
    return (
        last.get("role") == "user"
        and isinstance(content, list)
        and bool(content)
        and isinstance(content[0], dict)
        and content[0].get("type") == "tool_result"
    )


def _last_tool_name(messages: list) -> str:
    """Name of the tool_use in the preceding assistant turn."""
    for m in reversed(messages):
        if m.get("role") == "assistant":
            for block in m.get("content", []):
                if getattr(block, "type", None) == "tool_use":
                    return block.name
            break
    return ""


def _request_before_clarify(messages: list) -> str:
    """The user's original ask that triggered our clarifying question.

    The recommendation depends on both turns: the request names the category
    ("a tent"), the answer gives the conditions ("summer backpacking"). Embedding
    only the answer loses the category, so we recover the request that came just
    before the _CLARIFY_RECO assistant turn.
    """
    clarify_idx = None
    for i in range(len(messages) - 1, -1, -1):
        m = messages[i]
        if m.get("role") == "assistant" and m.get("content") == _CLARIFY_RECO:
            clarify_idx = i
            break
    if clarify_idx is None:
        return ""
    for j in range(clarify_idx - 1, -1, -1):
        mj = messages[j]
        if mj.get("role") == "user" and isinstance(mj.get("content"), str):
            return mj["content"]
    return ""


def _recommend(request: str, answer: str) -> str:
    """Pick the best catalog item from the whole exchange (original request +
    clarifying answer). If the shopper named a category, stay within it."""
    category = _detect_category(request) or _detect_category(answer)
    candidates = [c for c in _CATALOG if category is None or c[2] == category]
    if not candidates:  # named a category we don't stock — fall back to all
        candidates = _CATALOG
    query = f"{request}. {answer}".strip()
    idx = 0
    try:
        from app.embeddings import get_embedder

        model = get_embedder()
        descs = [f"{name}: {blurb}" for name, _price, _cat, blurb in candidates]
        vecs = model.encode(descs, normalize_embeddings=True)
        q = model.encode([query], normalize_embeddings=True)[0]
        idx = int((vecs @ q).argmax())
    except Exception:  # noqa: BLE001 — degrade to first candidate, never crash
        idx = 0
    name, price, _cat, blurb = candidates[idx]
    return f"Based on that, I'd suggest the {name} (${price}) — {blurb}. Want more detail or another option?"


class _Messages:
    def __init__(self, outer: "MockAnthropic") -> None:
        self._outer = outer

    def create(self, **kwargs):
        return self._outer._create(**kwargs)


class MockAnthropic:
    """Drop-in for `anthropic.Anthropic` in demo mode (only `.messages.create`)."""

    def __init__(self) -> None:
        self.messages = _Messages(self)

    def _create(self, *, messages, **_kw):
        # Second leg of a tool round-trip: produce the final user-facing text.
        if _is_tool_result_turn(messages):
            tool_name = _last_tool_name(messages)
            if tool_name == "get_order_status":
                status = messages[-1]["content"][0]["content"]
                return _resp("end_turn", [_text(status)])
            # handoff / fallback already emitted their text alongside the tool.
            return _resp("end_turn", [_text("")])

        user = _last_user_text(messages)
        prev = _prev_assistant_text(messages)

        # Multi-turn: this turn answers a clarifying question we just asked.
        if prev == _CLARIFY_RECO:
            follow = intent.classify(user)
            # A clear pivot to another topic re-routes; otherwise treat this turn as
            # the answer to our clarifying question and recommend.
            if follow.intent == "handoff" or (follow.intent == "order" and intent.extract_order_number(user)) or follow.intent in ("returns", "shipping"):
                pass  # fall through to the normal classification handling below
            else:
                request = _request_before_clarify(messages)
                return _resp("end_turn", [_text(_recommend(request, user))])
        if prev == _ORDER_ASK and intent.extract_order_number(user):
            num = intent.extract_order_number(user)
            return _resp("tool_use", [_tool("get_order_status", "m_order", order_number=num)])

        decision = intent.classify(user)

        if decision.intent == "order":
            num = intent.extract_order_number(user)
            if num:
                return _resp("tool_use", [_tool("get_order_status", "m_order", order_number=num)])
            return _resp("end_turn", [_text(_ORDER_ASK)])

        if decision.intent == "handoff":
            return _resp("tool_use", [
                _text("Of course — connecting you with a teammate now."),
                _tool("escalate_to_human", "m_handoff"),
            ])

        if decision.needs_clarification:
            return _resp("end_turn", [_text(_AMBIGUOUS_CLARIFY)])

        if decision.intent == "returns":
            return _resp("end_turn", [_text(_RETURNS_REPLY)])
        if decision.intent == "shipping":
            return _resp("end_turn", [_text(_SHIPPING_REPLY)])
        if decision.intent == "recommend":
            return _resp("end_turn", [_text(_CLARIFY_RECO)])
        if decision.intent == "greeting":
            return _resp("end_turn", [_text(_GREETING_REPLY)])

        # fallback — emit the line WITH the tool so an empty follow-up can't blank it.
        return _resp("tool_use", [
            _text(_FALLBACK_LINE),
            _tool("flag_not_understood", "m_fallback"),
        ])
