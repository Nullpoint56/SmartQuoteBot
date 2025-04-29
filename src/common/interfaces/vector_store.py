from abc import ABC, abstractmethod
from typing import List, Dict
import numpy as np

class VectorStore(ABC):
    """Abstract Base Class for a vector database backend."""

    @abstractmethod
    def add(self, embeddings: np.ndarray, metadatas: List[Dict]) -> None:
        """Add embeddings and associated metadata."""
        ...

    @abstractmethod
    def search(self, embedding: np.ndarray, top_n: int = 3) -> List[Dict]:
        """Search top-N embeddings and return metadata."""
        ...

    @abstractmethod
    def delete(self, id_: int) -> None:
        """Delete embedding by ID."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset the entire vector store."""
        ...
