from __future__ import annotations

import numpy as np

from sklearn.cluster import DBSCAN


class TicketClusterer:
    """
    Aplica la agrupación DBSCAN a las incrustaciones de tickets normalizadas.

    La clase contiene únicamente la lógica operativa de agrupación.

    La búsqueda en cuadrícula experimental y la evaluación de la verdad fundamental permanecen fuera del proceso operativo.
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
        Usamos DBSCAN de forma diferida utilizando los parámetros configurados.
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
        Asignamos un identificador de clúster a cada incrustación.
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
        Devuelve estadísticas básicas de agrupación operativa.
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