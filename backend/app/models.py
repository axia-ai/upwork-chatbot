"""SQLModel tables for persisted tickets and their transcripts."""

from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ticket_id: str = Field(foreign_key="ticket.id", index=True)
    role: str  # "user" | "bot"
    text: str
    time: str  # display label, e.g. "10:02"
    created_at: datetime = Field(default_factory=_utcnow)

    ticket: "Ticket" = Relationship(back_populates="transcript")


class Ticket(SQLModel, table=True):
    id: str = Field(primary_key=True)  # e.g. "NS-1063"
    subject: str
    status: str = "open"  # "open" | "in_progress" | "closed"
    topic: str
    updated_at: datetime = Field(default_factory=_utcnow)

    transcript: list[Message] = Relationship(
        back_populates="ticket",
        sa_relationship_kwargs={
            "order_by": "Message.id",
            "cascade": "all, delete-orphan",
        },
    )
