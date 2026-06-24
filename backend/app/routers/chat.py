"""Chat endpoints: POST /chat and POST /reset.

On handoff (explicit or auto), the linked ticket is created or flipped to
In Progress server-side; when a ticket is involved, the turn's messages are
persisted to its transcript so the frontend reflects real state.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app import agent, tickets_service as svc
from app.db import get_session
from app.models import Message
from app.retriever import get_retriever
from app.schemas import ChatRequest, ChatResponse, ResetRequest
from app.session import store

router = APIRouter(tags=["chat"])


def _now_label() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M")


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, session: Session = Depends(get_session)) -> ChatResponse:
    convo = store.get(req.session_id)
    chunks = get_retriever().query(req.message)
    kb_context = "\n\n".join(c.text for c in chunks)

    result = agent.run_agent(agent.get_client(), convo, req.message, kb_context=kb_context)

    # Resolve or create the linked ticket.
    ticket = svc.get_ticket(session, req.ticket_id) if req.ticket_id else None
    if result.handoff and ticket is None:
        ticket = svc.create_ticket(
            session,
            subject="Requested a live agent",
            topic="Human handoff",
            status="in_progress",
        )

    if ticket is not None:
        if result.handoff and ticket.status != "in_progress":
            svc.update_status(session, ticket, "in_progress")
        when = _now_label()
        svc.append_messages(
            session,
            ticket,
            [
                Message(role="user", text=req.message, time=when),
                Message(role="bot", text=result.reply, time=when),
            ],
        )

    return ChatResponse(
        reply=result.reply,
        state=result.state,
        handoff=result.handoff,
        intent=result.intent,
        ticket_id=ticket.id if ticket else None,
    )


@router.post("/reset")
def reset(req: ResetRequest) -> dict[str, str]:
    store.reset(req.session_id)
    return {"session_id": req.session_id}
