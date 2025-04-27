from typing import List, Dict, Protocol

import numpy as np


class VectorStore(Protocol):
    """Protocol for a vector database backend."""

    def add(self, embeddings: np.ndarray, metadatas: List[Dict]) -> None:
        """Add embeddings and associated metadata."""
        ...

    def search(self, embedding: np.ndarray, top_n: int = 3) -> List[Dict]:
        """Search top-N embeddings and return metadata."""
        ...

    def delete(self, id_: int) -> None:
        """Delete embedding by ID."""
        ...

    def reset(self) -> None:
        """Reset the entire vector store."""
        ...

