import numpy as np
import pytest

import ott_ticket_intelligence.embeddings.TicketEmbedder as embedder_module
from ott_ticket_intelligence.embeddings.TicketEmbedder import TicketEmbedder


class FakeSentenceTransformer:
    def __init__(self, model_path, device="cpu"):
        self.model_path = model_path
        self.device = device

    def get_sentence_embedding_dimension(self):
        return 3

    def encode(self, texts, batch_size=32, show_progress_bar=True, normalize_embeddings=True):
        rows = []
        for i, _ in enumerate(texts, start=1):
            v = np.array([float(i), 1.0, 0.5], dtype=np.float32)
            if normalize_embeddings:
                v = v / np.linalg.norm(v)
            rows.append(v)
        return np.vstack(rows)


def test_model_is_loaded_lazily(monkeypatch):
    monkeypatch.setattr(embedder_module, "SentenceTransformer", FakeSentenceTransformer)

    embedder = TicketEmbedder("/fake/model", "fake-model")

    assert embedder._model is None
    _ = embedder.model
    assert embedder._model is not None


def test_embedding_dimension(monkeypatch):
    monkeypatch.setattr(embedder_module, "SentenceTransformer", FakeSentenceTransformer)

    embedder = TicketEmbedder("/fake/model", "fake-model")

    assert embedder.embedding_dimension == 3


def test_encode_returns_expected_shape_and_normalized_vectors(monkeypatch):
    monkeypatch.setattr(embedder_module, "SentenceTransformer", FakeSentenceTransformer)

    embedder = TicketEmbedder("/fake/model", "fake-model")
    embeddings = embedder.encode(["a", "b", "c"])

    assert embeddings.shape == (3, 3)
    assert np.allclose(np.linalg.norm(embeddings, axis=1), 1.0, atol=1e-6)


def test_encode_rejects_empty_input(monkeypatch):
    monkeypatch.setattr(embedder_module, "SentenceTransformer", FakeSentenceTransformer)

    embedder = TicketEmbedder("/fake/model", "fake-model")

    with pytest.raises(ValueError, match="No texts"):
        embedder.encode([])
