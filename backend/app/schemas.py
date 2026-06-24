"""Pydantic DTOs for the chat and ticket APIs."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

TicketStatus = Literal["open", "in_progress", "closed"]
Intent = Literal["order", "returns", "recommend", "handoff", "fallback"]


# --- Chat ---
class ChatRequest(BaseModel):
    session_id: str
    message: str
    ticket_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    state: Literal["bot", "live_agent"]
    handoff: bool
    intent: Intent
    ticket_id: Optional[str] = None


class ResetRequest(BaseModel):
    session_id: str


# --- Tickets ---
class MessageRead(BaseModel):
    id: str
    role: Literal["user", "bot"]
    text: str
    time: str


class TicketSummary(BaseModel):
    id: str
    subject: str
    status: TicketStatus
    topic: str
    updated: datetime


class TicketRead(TicketSummary):
    transcript: list[MessageRead]


class TicketCreate(BaseModel):
    subject: str
    topic: str
    status: TicketStatus = "open"


class TicketUpdate(BaseModel):
    status: TicketStatus
