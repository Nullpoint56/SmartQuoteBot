from vector_store_service.service import VectorStoreService


class QuoteManager:
    """High-level service for managing quotes using the vector storage service."""

    def __init__(self, vector_store_service: VectorStoreService):
        """
        Args:
            vector_store_service (VectorStoreService): The service managing vector storage/search.
        """
        self.vector_store_service = vector_store_service

    def add_quote(self, text: str, label: str = None) -> None:
        """Add a new quote to the vector database."""
        self.vector_store_service.add_vectors(
            texts=[text],
            labels=[label]
        )

    def search_quotes(self, query: str, top_n: int = 3) -> list[dict]:
        """Search for quotes similar to a given query."""
        return self.vector_store_service.search_vectors(
            query=query,
            top_n=top_n
        )

    def delete_quote(self, quote_id: int) -> None:
        """Delete a quote by its database ID."""
        self.vector_store_service.delete_vector(quote_id)
