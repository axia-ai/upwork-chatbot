"""Application settings, loaded from environment variables.

The Anthropic API key is read from the environment and never hardcoded. Importing
this module never requires the key — only a real Claude call does — so the app
and the test suite import cleanly without it.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Anthropic — the bot model is the sample-tier Sonnet, never Opus.
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-6"

    # Demo mode forces the deterministic mock provider even when a key is set.
    demo_mode: bool = False

    # Local RAG.
    embedding_model: str = "all-MiniLM-L6-v2"
    knowledge_base_dir: Path = _BACKEND_DIR / "app" / "knowledge_base"
    retrieval_top_k: int = 3

    # Persistence — local SQLite file, no external service.
    database_url: str = f"sqlite:///{_BACKEND_DIR / 'northstar.db'}"

    # CORS — the Vite dev server.
    frontend_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


def current_mode() -> str:
    """'demo' when no key is set or DEMO_MODE is on; otherwise 'live'."""
    s = get_settings()
    return "demo" if (s.demo_mode or not s.anthropic_api_key) else "live"
