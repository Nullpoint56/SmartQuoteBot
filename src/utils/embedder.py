from typing import List, Optional
import numpy as np
from numpy.typing import NDArray
from sentence_transformers import SentenceTransformer

from src.utils.math import l2_normalize


class SentenceTransformerEmbedder:
    """SentenceTransformer-based embedder with lazy model loading and L2 normalization."""

    def __init__(self, model_name: str):
        """

        Prepare the embedder without loading the heavy model yet.

        Args:
            model_name (str): Name of the SentenceTransformer model to load.
        """
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None

    def embed(self, texts: List[str]) -> NDArray[np.float32]:
        """
        Embed a batch of texts into L2-normalized np.ndarray(float32).

        Args:
            texts (List[str]): List of input texts.

        Returns:
            np.ndarray: Array of normalized embeddings, dtype=float32.
        """
        if self.model is None:
            raise RuntimeError("Embedder model not loaded. Call `boot()` first.")

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=False
        ).astype(np.float32)

        normalized_embeddings = l2_normalize(embeddings)

        if not isinstance(normalized_embeddings, np.ndarray):
            raise TypeError("Embedder must return a numpy ndarray.")

        if normalized_embeddings.dtype != np.float32:
            raise TypeError(f"Embedder output must have dtype float32, got {normalized_embeddings.dtype}.")

        return normalized_embeddings

    def boot(self):
        """Load the transformer model into memory."""
        self.model = SentenceTransformer(self.model_name)
