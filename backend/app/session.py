"""In-memory per-conversation state.

Holds the chat history, the live-agent flag, and the consecutive-fallback
counter that drives auto-escalation. Ephemeral by design — cleared on restart
or via ``POST /reset``. (Tickets, unlike sessions, are persisted; see models.py.)
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Session:
    session_id: str
    history: list[dict] = field(default_factory=list)  # [{role, content}], text only
    live_agent: bool = False
    fallback_count: int = 0


class SessionStore:
    """Process-local session registry."""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def get(self, session_id: str) -> Session:
        if session_id not in self._sessions:
            self._sessions[session_id] = Session(session_id=session_id)
        return self._sessions[session_id]

    def reset(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)


# Module-level singleton used by the chat router.
store = SessionStore()
