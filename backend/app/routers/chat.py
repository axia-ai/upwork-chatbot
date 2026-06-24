"""Chat endpoints: POST /chat and POST /reset."""

from __future__ import annotations

from fastapi import APIRouter

from app import agent
from app.retriever import get_retriever
from app.schemas import ChatRequest, ChatResponse, ResetRequest
from app.session import store

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    session = store.get(req.session_id)
    chunks = get_retriever().query(req.message)
    kb_context = "\n\n".join(c.text for c in chunks)

    result = agent.run_agent(
        agent.get_client(), session, req.message, kb_context=kb_context
    )
    return ChatResponse(
        reply=result.reply,
        state=result.state,
        handoff=result.handoff,
        intent=result.intent,
        ticket_id=req.ticket_id,
    )


@router.post("/reset")
def reset(req: ResetRequest) -> dict[str, str]:
    store.reset(req.session_id)
    return {"session_id": req.session_id}
