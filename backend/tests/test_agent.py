"""Agent tool-calling, handoff, and fallback behavior — Claude fully mocked."""

from types import SimpleNamespace

from app.agent import run_agent
from app.session import Session


def _text(text):
    return SimpleNamespace(type="text", text=text)


def _tool(name, tool_id, **inputs):
    return SimpleNamespace(type="tool_use", name=name, id=tool_id, input=inputs)


def _resp(stop_reason, content):
    return SimpleNamespace(stop_reason=stop_reason, content=content)


class FakeClient:
    """Returns queued responses; records the messages of each create() call."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.calls.append(kwargs["messages"])
        return self._responses.pop(0)


def test_order_tool_dispatch_returns_mock_status():
    client = FakeClient([
        _resp("tool_use", [_tool("get_order_status", "t1", order_number="#111")]),
        _resp("end_turn", [_text("Order #111 has shipped and arrives tomorrow.")]),
    ])
    session = Session(session_id="s1")
    result = run_agent(client, session, "Where is order #111?")

    assert result.intent == "order"
    assert result.handoff is False
    # The tool_result fed back to the model carries the deterministic mock status.
    tool_result = client.calls[1][-1]["content"][0]["content"]
    assert "shipped" in tool_result.lower()
    assert "arriving tomorrow" in tool_result.lower()


def test_explicit_handoff_sets_live_agent():
    client = FakeClient([
        _resp("tool_use", [_tool("escalate_to_human", "t1")]),
        _resp("end_turn", [_text("Connecting you with a teammate now.")]),
    ])
    session = Session(session_id="s2")
    result = run_agent(client, session, "I want to talk to a human")

    assert result.handoff is True
    assert result.intent == "handoff"
    assert result.state == "live_agent"
    assert session.live_agent is True


def test_two_consecutive_fallbacks_auto_escalate():
    def fallback_client():
        return FakeClient([
            _resp("tool_use", [_tool("flag_not_understood", "t1")]),
            _resp("end_turn", [_text("I didn't catch that — I can help with orders, returns, gear, or a human.")]),
        ])

    session = Session(session_id="s3")

    first = run_agent(fallback_client(), session, "asdfghjkl")
    assert first.intent == "fallback"
    assert first.handoff is False
    assert first.state == "bot"
    assert session.fallback_count == 1

    second = run_agent(fallback_client(), session, "qwerty")
    assert second.handoff is True  # auto-escalation
    assert second.state == "live_agent"
    assert session.fallback_count == 2


def test_successful_intent_resets_fallback_counter():
    session = Session(session_id="s4")
    session.fallback_count = 1  # one prior fallback

    client = FakeClient([
        _resp("end_turn", [_text("We offer 30-day returns on unused items.")]),
    ])
    result = run_agent(client, session, "How do returns work?")

    assert result.handoff is False
    assert session.fallback_count == 0
    assert session.live_agent is False
