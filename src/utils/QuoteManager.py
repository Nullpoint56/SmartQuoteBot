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
        self.vector_store.add(embeddings=embedding, texts=[text])

    def remove_quote_by_id(self, quote_id: int):
        self.vector_store.delete(quote_id)

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

    def list_quotes(self)-> List[Dict]:
        return self.vector_store.list_all()

