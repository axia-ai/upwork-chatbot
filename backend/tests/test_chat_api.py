"""POST /chat and /reset contract — agent and retriever stubbed (offline)."""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app import agent
from app.routers import chat as chat_router


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(chat_router, "get_retriever", lambda: SimpleNamespace(query=lambda q: []))
    monkeypatch.setattr(agent, "get_client", lambda: object())
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
    from app.main import app

    with TestClient(app) as c:
        yield c


def test_chat_returns_contract(client):
    resp = client.post("/chat", json={"session_id": "s1", "message": "track my order"})
    assert resp.status_code == 200
    body = resp.json()
    assert set(body) == {"reply", "state", "handoff", "intent", "ticket_id"}
    assert body["intent"] == "order"
    assert body["state"] == "bot"


def test_chat_echoes_ticket_id(client):
    resp = client.post(
        "/chat", json={"session_id": "s1", "message": "hi", "ticket_id": "NS-1063"}
    )
    assert resp.json()["ticket_id"] == "NS-1063"


def test_reset_ok(client):
    resp = client.post("/reset", json={"session_id": "s1"})
    assert resp.status_code == 200
    assert resp.json() == {"session_id": "s1"}
