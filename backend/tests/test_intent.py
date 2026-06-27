"""Intent classifier: deterministic signals, semantic routing, and a labeled
accuracy bar so robustness is measured, not asserted."""

from app.intent import IntentDecision, classify, extract_order_number

# (message, expected_intent) — paraphrases + adversarial off-topic cases.
EVAL_SET = [
    # order
    ("Where is order #111?", "order"),
    ("track my package 222", "order"),
    ("what's the status of my order", "order"),
    ("has 333 shipped yet", "order"),
    ("I need an update on order number 111", "order"),
    ("when will my delivery arrive", "order"),
    # returns
    ("I want to return this jacket", "returns"),
    ("how do refunds work", "returns"),
    ("can I exchange the boots for a bigger size", "returns"),
    ("what's your return policy", "returns"),
    ("this tent doesn't fit my needs, can I send it back", "returns"),
    # shipping
    ("how long does shipping take", "shipping"),
    ("what are my delivery options", "shipping"),
    ("do you offer expedited shipping", "shipping"),
    ("how much is standard delivery", "shipping"),
    # recommend
    ("what tent should I buy", "recommend"),
    ("recommend a sleeping bag for cold weather", "recommend"),
    ("I need a gift for a hiker", "recommend"),
    ("suggest some gear for backpacking", "recommend"),
    ("what do you have for car camping in summer", "recommend"),
    # greeting
    ("hi there", "greeting"),
    ("hello", "greeting"),
    ("hey, good morning", "greeting"),
    # handoff
    ("let me talk to a human", "handoff"),
    ("I want to speak to a person", "handoff"),
    ("connect me with an agent", "handoff"),
    ("get me a representative", "handoff"),
    # fallback / off-topic
    ("what's the capital of France", "fallback"),
    ("tell me a joke", "fallback"),
    ("asdfghjkl", "fallback"),
    ("what's the weather tomorrow", "fallback"),
    ("do you sell car insurance", "fallback"),
]


def test_routing_accuracy_meets_bar():
    correct = sum(classify(m).intent == expected for m, expected in EVAL_SET)
    accuracy = correct / len(EVAL_SET)
    assert accuracy >= 0.90, f"routing accuracy {accuracy:.2%} below 90% bar"


def test_order_number_extraction():
    assert extract_order_number("where is #111") == "111"
    assert extract_order_number("order number 222 please") == "222"
    assert extract_order_number("no number here") == ""


def test_explicit_handoff_is_deterministic():
    # Beats any semantic guess: explicit request always wins.
    assert classify("can I talk to a human please").intent == "handoff"


def test_off_topic_is_fallback():
    assert classify("what's the capital of France").intent == "fallback"


def test_returns_decision_has_confidence():
    d = classify("how do returns work")
    assert isinstance(d, IntentDecision)
    assert d.intent == "returns"
    assert d.confidence > 0
