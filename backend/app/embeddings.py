"""Shared sentence-transformers model.

Both the knowledge-base retriever and the demo-mode intent classifier embed
text with the same local model. Loading it once here keeps memory and startup
cost down. Lazy + cached: importing this module never loads the model.
"""

from __future__ import annotations

from functools import lru_cache

from app.config import get_settings


@lru_cache
def get_embedder():
    """Return the process-wide SentenceTransformer, loaded on first use."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(get_settings().embedding_model)
