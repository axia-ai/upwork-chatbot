"""Persistence helpers for tickets, shared by the tickets router and chat link."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.models import Message, Ticket

_BASE_ID = 1100  # new tickets start above the seeded NS-104x/105x/106x range


def _now() -> datetime:
    return datetime.now(timezone.utc)


def next_ticket_id(session: Session) -> str:
    """Allocate the next NS-#### id, one above the current maximum."""
    highest = _BASE_ID
    for ticket in session.exec(select(Ticket)).all():
        match = re.search(r"(\d+)", ticket.id)
        if match:
            highest = max(highest, int(match.group(1)))
    return f"NS-{highest + 1}"


def list_tickets(session: Session) -> list[Ticket]:
    tickets = session.exec(select(Ticket)).all()
    return sorted(tickets, key=lambda t: t.updated_at, reverse=True)


def get_ticket(session: Session, ticket_id: str) -> Ticket | None:
    return session.get(Ticket, ticket_id)


def create_ticket(
    session: Session, *, subject: str, topic: str, status: str = "open"
) -> Ticket:
    ticket = Ticket(
        id=next_ticket_id(session),
        subject=subject,
        topic=topic,
        status=status,
        updated_at=_now(),
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


def update_status(session: Session, ticket: Ticket, status: str) -> Ticket:
    ticket.status = status
    ticket.updated_at = _now()
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


def append_messages(session: Session, ticket: Ticket, messages: list[Message]) -> Ticket:
    """Append messages to a ticket's transcript and bump its updated_at."""
    for message in messages:
        message.ticket_id = ticket.id
        session.add(message)
    ticket.updated_at = _now()
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket
