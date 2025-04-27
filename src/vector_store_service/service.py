from common.interfaces.connection_provider import ConnectionProvider
from common.utils.math import l2_normalize
from vector_store_service.embedders import SentenceTransformerEmbedder
from vector_store_service.vector_store_factory import create_vector_store
from common.config import VectorStoreServiceConfig


class VectorStoreService:
    """Service for embedding texts and managing vector storage/search."""

    def __init__(self, connection_provider: ConnectionProvider, config: VectorStoreServiceConfig):
        """
        Args:
            connection_provider (ConnectionProvider): Object providing DB/storage connections.
            config (VectorStoreServiceConfig): Configurations for the vector store service.
        """
        self.connection_provider = connection_provider
        self.config = config

        self.embedder = None
        self.vector_store = None
        self.conn = None

    def boot(self) -> None:
        """Load model, connect database/storage, and initialize vector store."""
        self.conn = self.connection_provider.connect()

        self.embedder = SentenceTransformerEmbedder(model_name=self.config.embedding_model)

        self.vector_store = create_vector_store(
            conn=self.conn,
            dimension=self.config.embedding_dimension
        )

    def shutdown(self) -> None:
        """Shutdown and clean up resources."""
        self.connection_provider.shutdown()

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of texts into vectors (normalized)."""
        embeddings = self.embedder.embed(texts)
        normalized = l2_normalize(embeddings)
        return normalized.tolist()

    def add_vectors(self, texts: list[str], labels: list[str] = None) -> None:
        """Add embedded vectors and associated metadata."""
        if labels is None:
            labels = [None] * len(texts)

        vectors = self.embed(texts)
        metadatas = [{"text": text, "label": label} for text, label in zip(texts, labels)]

        self.vector_store.add(
            embeddings=vectors,
            metadatas=metadatas
        )

    def search_vectors(self, query: str, top_n: int = 3) -> list[dict]:
        """Search for similar vectors given a query text."""
        query_vec = self.embed([query])
        results = self.vector_store.search(query_vec, top_n=top_n)
        return results

    def delete_vector(self, id_: int) -> None:
        """Delete a vector by its ID."""
        self.vector_store.delete(id_)
