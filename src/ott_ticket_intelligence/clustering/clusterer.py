from __future__ import annotations

import numpy as np

from sklearn.cluster import DBSCAN


class TicketClusterer:
    """
    Applies DBSCAN clustering to normalized ticket embeddings.

    The class contains only operational clustering logic.
    Experimental grid search and ground-truth evaluation remain
    outside the operational pipeline.
    """

    def __init__(
        self,
        eps: float = 0.25,
        min_samples: int = 3,
        metric: str = "cosine",
    ):
        if eps <= 0:
            raise ValueError(
                "eps must be greater than zero."
            )

        if min_samples < 1:
            raise ValueError(
                "min_samples must be at least 1."
            )

        self.eps = float(eps)
        self.min_samples = int(min_samples)
        self.metric = metric

        self._model: DBSCAN | None = None

    @property
    def model(self) -> DBSCAN:
        """
        Create DBSCAN lazily using the configured parameters.
        """

        if self._model is None:
            self._model = DBSCAN(
                eps=self.eps,
                min_samples=self.min_samples,
                metric=self.metric,
            )

        return self._model

    def fit_predict(
        self,
        embeddings: np.ndarray,
    ) -> np.ndarray:
        """
        Assign a cluster identifier to every embedding.
        """

        embeddings = np.asarray(
            embeddings,
            dtype=np.float32,
        )

        if embeddings.ndim != 2:
            raise ValueError(
                "Expected a two-dimensional embedding matrix."
            )

        if embeddings.shape[0] == 0:
            raise ValueError(
                "No embeddings were provided for clustering."
            )

        labels = self.model.fit_predict(
            embeddings
        )

        return labels.astype(int)

    @staticmethod
    def statistics(
        labels: np.ndarray,
    ) -> dict:
        """
        Return basic operational clustering statistics.
        """

        labels = np.asarray(labels)

        real_clusters = {
            int(label)
            for label in labels
            if int(label) != -1
        }

        noise_count = int(
            np.sum(labels == -1)
        )

        return {
            "cluster_count": len(real_clusters),
            "noise_count": noise_count,
            "ticket_count": len(labels),
        }