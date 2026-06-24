"""SQLite engine, schema creation, and idempotent seeding.

Uses a local SQLite file (no external service). On startup the schema is created
and, if empty, seeded with the three mock tickets that mirror the frontend so the
demo opens with realistic data.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlmodel import Session, SQLModel, create_engine, select

from app.config import get_settings
from app.models import Message, Ticket

_settings = get_settings()
engine = create_engine(
    _settings.database_url,
    connect_args={"check_same_thread": False},
)


def get_session():
    with Session(engine) as session:
        yield session


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _seed(session)


def _seed(session: Session) -> None:
    """Insert the mock tickets once. No-op if any ticket already exists."""
    if session.exec(select(Ticket).limit(1)).first():
        return

    now = datetime.now(timezone.utc)
    tickets = [
        Ticket(
            id="NS-1063",
            subject="Damaged tent pole on arrival",
            status="in_progress",
            topic="Human handoff",
            updated_at=now - timedelta(hours=2),
            transcript=[
                Message(role="user", time="10:02",
                        text="My new tent arrived with a cracked pole. I want to talk to a person."),
                Message(role="bot", time="10:02",
                        text="I'm sorry about the damaged pole, Riley. I'm connecting you with a "
                             "live agent now — your ticket is open and a teammate will jump in shortly."),
                Message(role="bot", time="10:05",
                        text="Live agent Dana has joined the conversation."),
            ],
        ),
        Ticket(
            id="NS-1057",
            subject="Return a jacket that runs small",
            status="open",
            topic="Returns & exchanges",
            updated_at=now - timedelta(days=1),
            transcript=[
                Message(role="user", time="16:41", text="How do I return a jacket?"),
                Message(role="bot", time="16:41",
                        text="Happy to help! We offer 30-day returns on unused items in their "
                             "original packaging. You can start your return here: "
                             "northstar.example.com/returns"),
                Message(role="user", time="16:42", text="Great, thanks!"),
            ],
        ),
        Ticket(
            id="NS-1042",
            subject="Where is order #111?",
            status="closed",
            topic="Order tracking",
            updated_at=now - timedelta(days=3),
            transcript=[
                Message(role="user", time="09:12", text="Where is my order?"),
                Message(role="bot", time="09:12",
                        text="I can track that for you — what's your order number?"),
                Message(role="user", time="09:13", text="#111"),
                Message(role="bot", time="09:13",
                        text="Good news! Order #111 has shipped and is arriving tomorrow. "
                             "Anything else I can help with?"),
                Message(role="user", time="09:14", text="That's all, thanks!"),
            ],
        ),
    ]
    session.add_all(tickets)
    session.commit()
