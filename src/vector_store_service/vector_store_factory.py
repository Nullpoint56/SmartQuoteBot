from typing import TYPE_CHECKING

from common.interfaces.vector_store import VectorStore
from vector_stores.postgres import PgVectorVectorStore

if TYPE_CHECKING:
    from typing import Any


def create_vector_store(conn: "Any", dimension: int = 384) -> VectorStore:
    """
    Factory method to create the correct VectorStore backend.

    Args:
        conn (Any): A database connection or client object.
        dimension (int): Embedding dimension.

    Returns:
        VectorStore: An implementation matching the VectorStore protocol.
    """
    return PgVectorVectorStore(conn=conn, dimension=dimension)
