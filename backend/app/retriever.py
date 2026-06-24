"""Semantic-embedding retrieval over the local knowledge base.

Loads the markdown docs in ``knowledge_base/``, splits them into chunks, embeds
them with a local sentence-transformers model (``all-MiniLM-L6-v2``), and answers
queries by cosine similarity. No external service or API key — everything runs
locally.

The embedding model is loaded lazily on first query so importing this module (or
the app) stays cheap and offline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.config import get_settings


@dataclass
class Chunk:
    text: str
    source: str  # originating filename, e.g. "returns.md"
    score: float = 0.0


def _split_into_chunks(doc: str, source: str) -> list[Chunk]:
    """Split a markdown doc into paragraph-sized chunks.

    Paragraphs are separated by blank lines. Standalone heading lines are merged
    into the following paragraph so each chunk keeps its section context.
    """
    chunks: list[Chunk] = []
    pending_heading = ""
    for block in re.split(r"\n\s*\n", doc):
        block = block.strip()
        if not block:
            continue
        # A block that is only a heading prefixes the next real paragraph.
        if block.startswith("#") and "\n" not in block:
            pending_heading = block.lstrip("# ").strip()
            continue
        text = f"{pending_heading}: {block}" if pending_heading else block
        pending_heading = ""
        chunks.append(Chunk(text=text, source=source))
    return chunks


class Retriever:
    """Embeds the knowledge base once and answers similarity queries."""

    def __init__(self, kb_dir: Path, model_name: str):
        self._model_name = model_name
        self._model = None  # loaded lazily
        self._embeddings = None  # numpy array, set on first query
        self.chunks: list[Chunk] = []
        for path in sorted(Path(kb_dir).glob("*.md")):
            self.chunks.extend(_split_into_chunks(path.read_text(), path.name))
        if not self.chunks:
            raise RuntimeError(f"No knowledge-base documents found in {kb_dir}")

    def _ensure_embedded(self) -> None:
        if self._embeddings is not None:
            return
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(self._model_name)
        self._embeddings = self._model.encode(
            [c.text for c in self.chunks],
            normalize_embeddings=True,
        )

    def query(self, text: str, top_k: int = 3) -> list[Chunk]:
        """Return the ``top_k`` most relevant chunks, highest score first."""
        self._ensure_embedded()
        query_vec = self._model.encode([text], normalize_embeddings=True)[0]
        # Cosine similarity == dot product on normalized vectors.
        scores = self._embeddings @ query_vec
        ranked = sorted(
            (Chunk(c.text, c.source, float(s)) for c, s in zip(self.chunks, scores)),
            key=lambda c: c.score,
            reverse=True,
        )
        return ranked[:top_k]


@lru_cache
def get_retriever() -> Retriever:
    settings = get_settings()
    return Retriever(settings.knowledge_base_dir, settings.embedding_model)
