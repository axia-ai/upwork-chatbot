"""The shared embedder is a single cached instance reused across callers."""

from app.embeddings import get_embedder


def test_embedder_is_cached_singleton():
    a = get_embedder()
    b = get_embedder()
    assert a is b  # same object — model loaded once


def test_embedder_encodes_normalized_vectors():
    import numpy as np

    vecs = get_embedder().encode(["hello world"], normalize_embeddings=True)
    assert vecs.shape[0] == 1
    assert np.isclose(np.linalg.norm(vecs[0]), 1.0, atol=1e-3)
