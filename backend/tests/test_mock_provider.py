"""MockAnthropic drives the real run_agent loop end-to-end with no API key."""

from app.agent import run_agent
from app.mock_provider import MockAnthropic
from app.session import Session


def _run(session, message):
    return run_agent(MockAnthropic(), session, message)


def test_order_tracking_returns_canonical_status():
    r = _run(Session(session_id="o"), "where is order #111")
    assert r.intent == "order"
    assert "tomorrow" in r.reply.lower()  # #111 -> arriving tomorrow


def test_invalid_order_is_not_fabricated():
    r = _run(Session(session_id="o2"), "track order 999")
    assert r.intent == "order"
    assert "111" in r.reply  # nudges to the valid numbers, no fake status


def test_returns_policy_quoted():
    r = _run(Session(session_id="r"), "how do returns work")
    low = r.reply.lower()
    assert "30" in low and "return" in low


def test_shipping_options_quoted():
    r = _run(Session(session_id="s"), "how long does shipping take")
    assert "3" in r.reply and "5" in r.reply  # standard 3–5 days


def test_recommendation_clarifies_then_recommends():
    session = Session(session_id="rec")
    first = _run(session, "what tent should I buy")
    assert first.reply.endswith("?")  # asks a clarifying question
    second = _run(session, "three-season backpacking in summer")
    assert "wildwood" in second.reply.lower()  # the 3-season tent


def test_explicit_handoff_escalates():
    r = _run(Session(session_id="h"), "I want to talk to a human")
    assert r.handoff is True
    assert r.state == "live_agent"


def test_two_fallbacks_auto_escalate():
    session = Session(session_id="fb")
    first = _run(session, "what's the capital of France")
    assert first.intent == "fallback"
    assert first.handoff is False
    second = _run(session, "tell me a joke")
    assert second.handoff is True  # 2-consecutive-fallback rule
    assert second.state == "live_agent"
