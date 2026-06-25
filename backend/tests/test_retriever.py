"""Retrieval relevance over the knowledge base.

Loads the real local embedding model (downloaded once, then cached). No network
or API key is needed beyond the one-time model download.
"""

from app.retriever import get_retriever


def test_returns_query_retrieves_returns_doc():
    top = get_retriever().query("How do I return a jacket?", top_k=3)
    assert top[0].source == "returns.md"
    assert "30-day" in top[0].text or "30 days" in top[0].text


def test_shipping_query_retrieves_shipping_doc():
    top = get_retriever().query("How long does delivery take?", top_k=3)
    assert any(c.source == "shipping.md" for c in top)


def test_scores_are_sorted_descending():
    top = get_retriever().query("recommend a tent for backpacking", top_k=3)
    scores = [c.score for c in top]
    assert scores == sorted(scores, reverse=True)
