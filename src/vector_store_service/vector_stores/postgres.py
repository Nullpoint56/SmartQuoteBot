from typing import List, Dict, Optional
import numpy as np
import psycopg

from common.interfaces.vector_store import VectorStore


class PgVectorVectorStore(VectorStore):
    """Vector store using PostgreSQL with pgvector extension, pure psycopg3."""

    def __init__(self, dimension: int = 384):
        """
        Prepare the vector store.

        Args:
            dimension (int): Embedding dimension.
        """
        self.dimension = dimension
        self.conn: Optional[psycopg.Connection] = None

    def boot(self, conn: psycopg.Connection) -> None:
        """Inject the database connection."""
        self.conn = conn

    def add(self, embeddings: np.ndarray, metadatas: List[Dict]) -> None:
        """Add embeddings and associated metadata to the vector store."""
        self._check_connection()

        # 🔥 Validate embedding dimensions
        if embeddings.ndim != 2 or embeddings.shape[1] != self.dimension:
            raise ValueError(
                f"Invalid embedding dimensions: expected (*, {self.dimension}), "
                f"got {embeddings.shape}."
            )

        with self.conn.cursor() as cur:
            for embedding, metadata in zip(embeddings, metadatas):
                cur.execute(
                    """
                    INSERT INTO vectors (text, label, embedding)
                    VALUES (%s, %s, %s)
                    """,
                    (
                        metadata.get("text"),
                        metadata.get("label"),
                        list(embedding)  # psycopg3 automatically adapts list[float] for pgvector
                    )
                )
            self.conn.commit()

    def search(self, embedding: np.ndarray, top_n: int = 3) -> List[Dict]:
        """Search for the top-N most similar vectors given an input embedding."""
        self._check_connection()

        if embedding.ndim != 2 or embedding.shape[1] != self.dimension:
            raise ValueError(
                f"Invalid query embedding dimensions: expected (*, {self.dimension}), "
                f"got {embedding.shape}."
            )

        with self.conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            query_embedding = list(embedding[0])

            cur.execute(
                """
                SELECT id, text, label
                FROM vectors
                ORDER BY embedding <=> %s
                LIMIT %s
                """,
                (query_embedding, top_n)
            )

            rows = cur.fetchall()

        return [
            {"id": row["id"], "text": row["text"], "label": row["label"]}
            for row in rows
        ]

    def delete(self, id_: int) -> None:
        """Delete a vector by its ID."""
        self._check_connection()

        with self.conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM vectors
                WHERE id = %s
                """,
                (id_,)
            )
            self.conn.commit()

    def reset(self) -> None:
        """Reset (delete) all vectors in the database."""
        self._check_connection()

        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM vectors")
            self.conn.commit()

    def _check_connection(self) -> None:
        """Ensure that the connection has been initialized."""
        if self.conn is None:
            raise RuntimeError("Database connection not initialized. Call boot(conn) first.")
