"""POST /chat and /reset contract — agent and retriever stubbed (offline)."""

import pytest

from app import agent


@pytest.fixture(autouse=True)
def stub_agent(monkeypatch):
    monkeypatch.setattr(
        agent,
        "run_agent",
        lambda *a, **k: agent.AgentResult(
            reply="Sure — what's your order number?",
            intent="order",
            handoff=False,
            state="bot",
        ),
    )


def test_chat_returns_contract(client):
    resp = client.post("/chat", json={"session_id": "s1", "message": "track my order"})
    assert resp.status_code == 200
    body = resp.json()
    assert set(body) == {"reply", "state", "handoff", "intent", "ticket_id"}
    assert body["intent"] == "order"
    assert body["state"] == "bot"
    assert body["ticket_id"] is None  # no handoff, no ticket supplied


def test_reset_ok(client):
    resp = client.post("/reset", json={"session_id": "s1"})
    assert resp.status_code == 200
    assert resp.json() == {"session_id": "s1"}


def test_chat_degrades_to_503_on_agent_failure(client, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("anthropic exploded")

    monkeypatch.setattr(agent, "run_agent", boom)  # overrides the autouse stub
    resp = client.post("/chat", json={"session_id": "s1", "message": "hi"})
    assert resp.status_code == 503
    assert "unavailable" in resp.json()["detail"].lower()
