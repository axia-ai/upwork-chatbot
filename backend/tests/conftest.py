"""Shared test fixtures.

Tests run fully offline: the Anthropic client is mocked at the agent layer
(added with the agent tests) and persistence uses a throwaway in-memory SQLite
database so nothing touches the real ``northstar.db``.
"""

from __future__ import annotations

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool


@pytest.fixture
def session():
    """A fresh in-memory SQLite session per test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
