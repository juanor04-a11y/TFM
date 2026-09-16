import numpy as np
import pytest

from ott_ticket_intelligence.clustering.TicketClusterer import TicketClusterer


def test_clusterer_rejects_invalid_eps():
    with pytest.raises(ValueError, match="eps"):
        TicketClusterer(eps=0, min_samples=3)


def test_clusterer_rejects_invalid_min_samples():
    with pytest.raises(ValueError, match="min_samples"):
        TicketClusterer(eps=0.25, min_samples=0)


def test_fit_predict_returns_one_label_per_embedding():
    X = np.array([[1.0, 0.0], [0.99, 0.01], [0.0, 1.0], [0.01, 0.99]], dtype=np.float32)
    clusterer = TicketClusterer(eps=0.05, min_samples=2, metric="cosine")

    labels = clusterer.fit_predict(X)

    assert len(labels) == len(X)


def test_fit_predict_rejects_empty_matrix():
    clusterer = TicketClusterer()

    with pytest.raises(ValueError, match="No embeddings"):
        clusterer.fit_predict(np.empty((0, 2), dtype=np.float32))


def test_statistics_counts_clusters_and_noise():
    labels = np.array([0, 0, 1, 1, -1])

    stats = TicketClusterer.statistics(labels)

    assert stats["cluster_count"] == 2
    assert stats["noise_count"] == 1
    assert stats["ticket_count"] == 5
