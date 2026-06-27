"""/health reports the active mode so the UI can badge demo mode."""

from fastapi.testclient import TestClient

from app import config, main


def test_health_reports_demo_when_no_key(monkeypatch):
    config.get_settings.cache_clear()
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.setattr(main, "init_db", lambda: None)
    with TestClient(main.app) as c:
        body = c.get("/health").json()
    assert body["status"] == "ok"
    assert body["mode"] == "demo"
    config.get_settings.cache_clear()
