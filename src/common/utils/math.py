import numpy as np

def l2_normalize(vectors: np.ndarray, axis: int = 1, eps: float = 1e-10) -> np.ndarray:
    """Apply L2 normalization to a batch of vectors."""
    norms = np.linalg.norm(vectors, ord=2, axis=axis, keepdims=True)
    return vectors / np.clip(norms, eps, None)
