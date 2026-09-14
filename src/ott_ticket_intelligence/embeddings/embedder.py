from __future__ import annotations

from typing import Iterable

import numpy as np
from sentence_transformers import SentenceTransformer


class TicketEmbedder:
    """
    Generates normalized semantic embeddings for ticket texts.

    The class encapsulates model loading and batch inference so that
    Fabric notebooks only need to provide input texts and configuration.
    """

    def __init__(
        self,
        model_path: str,
        model_name: str,
        batch_size: int = 32,
        device: str = "cpu",
    ):
        self.model_path = model_path
        self.model_name = model_name
        self.batch_size = batch_size
        self.device = device

        self._model: SentenceTransformer | None = None

    @property
    def model(self) -> SentenceTransformer:
        """
        Lazy-load the SentenceTransformer model.

        The model is loaded only when first required.
        """

        if self._model is None:
            self._model = SentenceTransformer(
                self.model_path,
                device=self.device,
            )

        return self._model

    @property
    def embedding_dimension(self) -> int:
        """
        Return the dimensionality of the configured embedding model.
        """

        return int(
            self.model.get_sentence_embedding_dimension()
        )

    def encode(
        self,
        texts: Iterable[str],
    ) -> np.ndarray:
        """
        Generate normalized embeddings for a collection of texts.
        """

        texts = list(texts)

        if not texts:
            raise ValueError(
                "No texts were provided for embedding generation."
            )

        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=True,
            normalize_embeddings=True,
        )

        embeddings = np.asarray(
            embeddings,
            dtype=np.float32,
        )

        if embeddings.ndim != 2:
            raise ValueError(
                "Expected a two-dimensional embedding matrix."
            )

        if embeddings.shape[0] != len(texts):
            raise ValueError(
                "The number of generated embeddings does not "
                "match the number of input texts."
            )

        if embeddings.shape[1] != self.embedding_dimension:
            raise ValueError(
                "Unexpected embedding dimension."
            )

        return embeddings