"""Ticket CRUD endpoints, scoped to the single mock user."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app import tickets_service as svc
from app.db import get_session
from app.models import Ticket
from app.schemas import MessageRead, TicketCreate, TicketRead, TicketSummary, TicketUpdate

router = APIRouter(prefix="/tickets", tags=["tickets"])


def _summary(ticket: Ticket) -> TicketSummary:
    return TicketSummary(
        id=ticket.id,
        subject=ticket.subject,
        status=ticket.status,
        topic=ticket.topic,
        updated=ticket.updated_at,
    )


def _read(ticket: Ticket) -> TicketRead:
    return TicketRead(
        **_summary(ticket).model_dump(),
        transcript=[
            MessageRead(id=str(m.id), role=m.role, text=m.text, time=m.time)
            for m in ticket.transcript
        ],
    )


@router.get("", response_model=list[TicketSummary])
def list_tickets(session: Session = Depends(get_session)) -> list[TicketSummary]:
    return [_summary(t) for t in svc.list_tickets(session)]


@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket(ticket_id: str, session: Session = Depends(get_session)) -> TicketRead:
    ticket = svc.get_ticket(session, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return _read(ticket)


@router.post("", response_model=TicketRead, status_code=201)
def create_ticket(body: TicketCreate, session: Session = Depends(get_session)) -> TicketRead:
    ticket = svc.create_ticket(
        session, subject=body.subject, topic=body.topic, status=body.status
    )
    return _read(ticket)


@router.patch("/{ticket_id}", response_model=TicketRead)
def update_ticket(
    ticket_id: str, body: TicketUpdate, session: Session = Depends(get_session)
) -> TicketRead:
    ticket = svc.get_ticket(session, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    svc.update_status(session, ticket, body.status)
    return _read(ticket)
