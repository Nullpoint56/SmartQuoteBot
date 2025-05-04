import numpy as np

def l2_normalize(vectors: np.ndarray, axis: int = 1, eps: float = 1e-10) -> np.ndarray:
    """
    Apply L2 normalization to a batch of vectors.

    Args:
        vectors (np.ndarray): Array of shape (batch_size, dimension).
        axis (int): Axis along which to compute norms (default: 1).
        eps (float): Small value to avoid division by zero.

    Returns:
        np.ndarray: L2-normalized vectors, dtype=float32.
    """
    if not isinstance(vectors, np.ndarray):
        raise TypeError("Input must be a numpy ndarray.")
    if vectors.ndim != 2:
        raise ValueError(f"Expected 2D array (batch of vectors), got {vectors.ndim}D.")

    norms = np.linalg.norm(vectors, ord=2, axis=axis, keepdims=True)
    normalized = vectors / np.clip(norms, eps, None)

    return normalized.astype(np.float32)