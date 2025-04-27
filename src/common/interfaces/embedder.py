from typing import Protocol, List

import numpy as np


class Embedder(Protocol):
    """Protocol for text-to-vector embedding models."""

    def embed(self, texts: List[str]) -> np.ndarray:
        """Embed a batch of texts into vectors."""
        ...

    def batch_size_hint(self) -> int:
        """Recommended batch size for this embedder (optional)."""
        ...

    def device(self) -> str:
        """Return backend device info (optional)."""
        ...