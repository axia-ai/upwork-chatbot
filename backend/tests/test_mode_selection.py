"""Mode selection: auto-detect by key presence, with an explicit override."""

import pytest

from app import agent, config
from app.mock_provider import MockAnthropic


# These tests set ANTHROPIC_API_KEY and DEMO_MODE via monkeypatch.setenv; OS env vars take precedence over the .env file in pydantic-settings, so backend/.env cannot shadow them.
@pytest.fixture(autouse=True)
def _clear_caches():
    config.get_settings.cache_clear()
    agent.get_client.cache_clear()
    yield
    config.get_settings.cache_clear()
    agent.get_client.cache_clear()


def test_no_key_is_demo(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    monkeypatch.setenv("DEMO_MODE", "false")
    assert config.current_mode() == "demo"
    assert isinstance(agent.get_client(), MockAnthropic)


def test_key_without_flag_is_live(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("DEMO_MODE", "false")
    assert config.current_mode() == "live"
    assert not isinstance(agent.get_client(), MockAnthropic)


def test_key_with_demo_flag_is_demo(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("DEMO_MODE", "true")
    assert config.current_mode() == "demo"
    assert isinstance(agent.get_client(), MockAnthropic)
