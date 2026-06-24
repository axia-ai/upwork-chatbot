"""Ticket CRUD and the chat-handoff -> ticket link, against a throwaway DB."""

from app import agent


def test_list_returns_seeded_tickets(client):
    resp = client.get("/tickets")
    assert resp.status_code == 200
    ids = {t["id"] for t in resp.json()}
    assert ids == {"NS-1063", "NS-1057", "NS-1042"}


def test_list_is_newest_first(client):
    resp = client.get("/tickets")
    ids = [t["id"] for t in resp.json()]
    assert ids == ["NS-1063", "NS-1057", "NS-1042"]  # by updated_at desc


def test_get_returns_transcript(client):
    resp = client.get("/tickets/NS-1042")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "closed"
    assert len(body["transcript"]) == 5
    assert body["transcript"][0]["role"] == "user"


def test_get_missing_is_404(client):
    assert client.get("/tickets/NS-9999").status_code == 404


def test_create_persists(client):
    resp = client.post("/tickets", json={"subject": "Boot sizing", "topic": "Recommendations"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "open"
    assert body["id"].startswith("NS-")
    # It now appears in the list.
    assert any(t["id"] == body["id"] for t in client.get("/tickets").json())


def test_patch_updates_status(client):
    resp = client.patch("/tickets/NS-1057", json={"status": "closed"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "closed"
    assert client.get("/tickets/NS-1057").json()["status"] == "closed"


def test_patch_missing_is_404(client):
    assert client.patch("/tickets/NS-9999", json={"status": "closed"}).status_code == 404


def test_handoff_creates_in_progress_ticket(client, monkeypatch):
    monkeypatch.setattr(
        agent,
        "run_agent",
        lambda *a, **k: agent.AgentResult(
            reply="Connecting you with a teammate now.",
            intent="handoff",
            handoff=True,
            state="live_agent",
        ),
    )
    resp = client.post("/chat", json={"session_id": "s1", "message": "I want a human"})
    body = resp.json()
    assert body["handoff"] is True
    new_id = body["ticket_id"]
    assert new_id is not None

    ticket = client.get(f"/tickets/{new_id}").json()
    assert ticket["status"] == "in_progress"
    # The turn's messages were persisted to the transcript.
    roles = [m["role"] for m in ticket["transcript"]]
    assert roles == ["user", "bot"]


def test_handoff_flips_existing_ticket(client, monkeypatch):
    monkeypatch.setattr(
        agent,
        "run_agent",
        lambda *a, **k: agent.AgentResult(
            reply="Connecting you now.", intent="handoff", handoff=True, state="live_agent"
        ),
    )
    resp = client.post(
        "/chat", json={"session_id": "s2", "message": "human please", "ticket_id": "NS-1057"}
    )
    assert resp.json()["ticket_id"] == "NS-1057"
    assert client.get("/tickets/NS-1057").json()["status"] == "in_progress"
