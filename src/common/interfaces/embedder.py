from abc import ABC, abstractmethod
from typing import List
import numpy as np
from numpy.typing import NDArray

class Embedder(ABC):
    """Abstract Base Class for text-to-vector embedding models."""

    @abstractmethod
    def embed(self, texts: List[str]) -> NDArray[np.float32]:
        """Embed a batch of texts into vectors."""
        ...

    @abstractmethod
    def batch_size_hint(self) -> int:
        """Recommended batch size for this embedder."""
        ...

    @abstractmethod
    def device(self) -> str:
        """Return backend device info (optional)."""
        ...
