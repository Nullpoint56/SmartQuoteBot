from typing import List
import numpy as np

from common.interfaces.service_manager import BootableService
from embedding_service.embedders.sentence_transformer import SentenceTransformerEmbedder
from embedding_service.config import EmbeddingServiceConfig


class EmbeddingService(BootableService):
    """Service to manage text embedding using a selected embedder."""

    def __init__(self, config: EmbeddingServiceConfig = None):
        """
        Initialize the embedding service.

        Args:
            config (EmbeddingServiceConfig): Configuration for embedding model.
        """
        self.config = config or EmbeddingServiceConfig()

        # Pass model name from config
        self.embedder = SentenceTransformerEmbedder(model_name=self.config.embedding_model)

    def boot(self) -> None:
        """Boot the embedder (load model, prepare resources)."""
        self.embedder.boot()

    def shutdown(self) -> None:
        """Shutdown the embedder (free resources)."""
        # Optional, currently nothing to shutdown
        pass

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Embed a list of texts into L2-normalized vectors."""
        return self.embedder.embed(texts)

    def device(self) -> str:
        """Return backend device info (cpu or cuda)."""
        return self.embedder.device()

    def batch_size_hint(self) -> int:
        """Recommended batch size for efficient inference."""
        return self.embedder.batch_size_hint()

    def health_check(self) -> bool:
        """Check if model is loaded."""
        return self.embedder.is_ready()
