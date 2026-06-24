"""Seeding is correct and idempotent."""

from sqlmodel import select

from app.db import _seed
from app.models import Message, Ticket


def test_seed_inserts_three_mock_tickets(session):
    _seed(session)
    tickets = session.exec(select(Ticket)).all()
    ids = {t.id for t in tickets}
    assert ids == {"NS-1063", "NS-1057", "NS-1042"}
    statuses = {t.id: t.status for t in tickets}
    assert statuses["NS-1063"] == "in_progress"
    assert statuses["NS-1057"] == "open"
    assert statuses["NS-1042"] == "closed"


def test_seed_is_idempotent(session):
    _seed(session)
    _seed(session)  # second call must be a no-op
    assert len(session.exec(select(Ticket)).all()) == 3


def test_seed_persists_transcripts(session):
    _seed(session)
    handoff = session.get(Ticket, "NS-1063")
    assert len(handoff.transcript) == 3
    assert handoff.transcript[0].role == "user"
    assert all(isinstance(m, Message) for m in handoff.transcript)
