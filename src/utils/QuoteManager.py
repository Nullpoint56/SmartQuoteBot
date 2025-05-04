from typing import List, Dict
import numpy as np
from numpy.typing import NDArray

from src.utils.vector_store import PgVectorStore
from src.utils.embedder import SentenceTransformerEmbedder


class QuoteManager:
    def __init__(self, vector_store: PgVectorStore, embedder: SentenceTransformerEmbedder):
        self.vector_store = vector_store
        self.embedder = embedder

    def add_quote(self, text: str):
        embedding: NDArray[np.float32] = self.embedder.embed([text])
        self.vector_store.add(embeddings=embedding, metadatas=[{"text": text, "label": "quote"}])

    def remove_quote(self, index: int):
        quotes = self.list_quotes()
        if not (0 <= index < len(quotes)):
            raise IndexError("Invalid quote index")
        id_to_delete = quotes[index]["id"]
        self.vector_store.delete(id_to_delete)

    def list_quotes(self) -> List[Dict]:
        # Dummy embedding to list everything (can be replaced with SQL scan later)
        # For now, fetch more than enough to simulate "list all"
        all_results = self.vector_store.search(self.embedder.embed(["dummy"]), top_n=1000)
        return all_results

    def query(self, text: str, top_n: int = 1, threshold: float = None, metric: str = "cosine") -> List[Dict]:
        embedding: NDArray[np.float32] = self.embedder.embed([text])
        return self.vector_store.search(
            embedding=embedding,
            top_n=top_n,
            metric=metric,
            threshold=threshold
        )

    def count_quotes(self) -> int:
        return self.vector_store.count()

