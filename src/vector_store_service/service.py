from common.interfaces.connection_provider import ConnectionProvider
from common.interfaces.service_manager import BootableService
from common.utils.connection_providers import PostgresConnectionProvider

from vector_store_service.config import VectorStoreServiceConfig
from vector_store_service.vector_stores.postgres import PgVectorVectorStore

import numpy as np  # Only if you still want to accept np.ndarray


class VectorStoreService(BootableService):
    """Service for managing vector storage/search."""

    def __init__(self):
        """Initialize service by loading config and setting up dependencies."""
        self.config = VectorStoreServiceConfig()
        self.connection_provider: ConnectionProvider = PostgresConnectionProvider(self.config.db)

        self.vector_store = PgVectorVectorStore(dimension=self.config.embedding_dimension)

    def boot(self) -> None:
        """Connect database/storage and initialize vector store."""
        conn = self.connection_provider.connect()
        self.vector_store.boot(conn)

    def shutdown(self) -> None:
        """Shutdown and clean up resources."""
        if self.connection_provider:
            self.connection_provider.shutdown()

    def add_vectors(self, embeddings: list[list[float]], metadatas: list[dict]) -> None:
        """Add pre-computed embeddings and associated metadata."""
        embeddings_np = np.array(embeddings, dtype=np.float32)  # <-- fix here
        self.vector_store.add(
            embeddings=embeddings_np,
            metadatas=metadatas
        )

    def search_vectors(self, query_vector: list[float], top_n: int = 3) -> list[dict]:
        """Search for similar vectors given a query embedding."""
        results = self.vector_store.search(np.array([query_vector], dtype=np.float32), top_n=top_n)
        return results

    def delete_vector(self, id_: int) -> None:
        """Delete a vector by its ID."""
        self.vector_store.delete(id_)

    def health_check(self) -> bool:
        """Basic health check: verify if database connection is alive."""
        try:
            if not self.connection_provider.conn:
                return False
            # Perform a lightweight DB query
            with self.connection_provider.conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                return result is not None
        except Exception as e:
            print(f"[Health Check] Exception: {e}")
            return False