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
    second = _run(session, "a three-season tent for summer backpacking")
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


def test_clarify_then_handoff_escalates():
    session = Session(session_id="clarify_handoff")
    _run(session, "what tent should I buy")
    second = _run(session, "actually get me a human")
    assert second.handoff is True
    assert second.state == "live_agent"


def test_clarify_then_returns_pivot():
    session = Session(session_id="clarify_returns")
    _run(session, "what tent should I buy")
    second = _run(session, "what's your return policy")
    reply = second.reply
    assert "30" in reply and "return" in reply.lower()


def test_recommend_keeps_requested_category():
    """A tent request stays a tent even when the trip answer omits 'tent' and
    leans on 'backpacking' (which otherwise pulls the Trailhead pack)."""
    session = Session(session_id="rec_cat")
    _run(session, "what tent should I buy?")
    second = _run(session, "three-season backpacking in summer")
    low = second.reply.lower()
    assert "wildwood" in low  # a Tent
    assert "trailhead" not in low  # not the backpack


def test_recommend_without_named_category_still_responds():
    """No explicit category named — still returns a concrete product."""
    session = Session(session_id="rec_nocat")
    _run(session, "I need some gear")
    second = _run(session, "deep cold winter camping")
    names = ("wildwood", "polaris", "summit", "aurora", "granite", "trailhead")
    assert any(n in second.reply.lower() for n in names)
