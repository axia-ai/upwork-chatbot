"""Shared test fixtures.

Tests run fully offline: the Anthropic client is mocked at the agent layer
(added with the agent tests) and persistence uses a throwaway in-memory SQLite
database so nothing touches the real ``northstar.db``.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool


def _make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def session():
    """A fresh in-memory SQLite session per test."""
    engine = _make_engine()
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def api_engine():
    """A throwaway in-memory DB seeded with the mock tickets, shared per test."""
    from app.db import _seed

    engine = _make_engine()
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        _seed(s)
    return engine


@pytest.fixture
def client(api_engine, monkeypatch):
    """TestClient wired to the throwaway DB; retriever and Claude stubbed."""
    from fastapi.testclient import TestClient

    from app import agent, main
    from app.db import get_session
    from app.routers import chat as chat_router

    # Don't let the lifespan touch the real northstar.db.
    monkeypatch.setattr(main, "init_db", lambda: None)
    monkeypatch.setattr(chat_router, "get_retriever", lambda: SimpleNamespace(query=lambda q: []))
    monkeypatch.setattr(agent, "get_client", lambda: object())

    def override_session():
        with Session(api_engine) as s:
            yield s

    main.app.dependency_overrides[get_session] = override_session
    with TestClient(main.app) as c:
        yield c
    main.app.dependency_overrides.clear()
