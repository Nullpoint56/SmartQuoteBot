from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

from common.interfaces.embedder import Embedder
from common.utils.math import l2_normalize


class SentenceTransformerEmbedder(Embedder):
    """SentenceTransformer-based embedder with L2 normalization."""

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize the embedder.

        Args:
            model_name (str): Name of the SentenceTransformer model to load.
        """
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> np.ndarray:
        """
        Embed a batch of texts into L2-normalized vectors.

        Args:
            texts (List[str]): List of input texts.

        Returns:
            np.ndarray: Array of normalized embeddings.
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True).astype(np.float32)
        return l2_normalize(embeddings)

    def batch_size_hint(self) -> int:
        """Recommended batch size for this embedder."""
        return 32  # SentenceTransformer can typically handle 16–64 depending on model

    def device(self) -> str:
        """Backend device info (cpu or cuda)."""
        return str(self.model.device)
