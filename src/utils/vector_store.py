from typing import List, Dict

from numpy import ndarray
from psycopg import Connection, sql
from psycopg.rows import dict_row


class PgVectorStore:
    """Vector store using PostgreSQL with pgvector extension, pure psycopg3."""

    def __init__(self, connection: Connection, dimension: int = 384):
        """
        Prepare the vector store.

        Args:
            dimension (int): Embedding dimension.
        """
        self.dimension = dimension
        self.conn: Connection = connection

    def add(self, embeddings: ndarray, texts: List[str]) -> None:
        """Add quotes and their embeddings to the vector store."""

        if embeddings.ndim != 2 or embeddings.shape[1] != self.dimension:
            raise ValueError(
                f"Invalid embedding dimensions: expected (*, {self.dimension}), "
                f"got {embeddings.shape}."
            )

        with self.conn.cursor() as cur:
            for embedding, text in zip(embeddings, texts):
                cur.execute(
                    """
                    INSERT INTO vectors (text, embedding)
                    VALUES (%s, %s)
                    """,
                    (text, list(embedding))
                )
            self.conn.commit()

    def search(
            self,
            embedding: ndarray,
            top_n: int = 3,
            metric: str = "cosine",
            threshold: float = None
    ) -> List[Dict]:
        if embedding.ndim != 2 or embedding.shape[1] != self.dimension:
            raise ValueError(
                f"Invalid query embedding dimensions: expected (*, {self.dimension}), "
                f"got {embedding.shape}."
            )

        query_vector = list(embedding[0])

        # pgvector operator depends on metric type
        if metric == "cosine":
            operator = "<=>"
        elif metric == "euclidean":
            operator = "<->"
        elif metric == "inner_product":
            operator = "<#>"
        else:
            raise ValueError(f"Unsupported metric: {metric}")

        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"""
                SELECT id, text, embedding {operator} %s::vector AS distance
                FROM vectors
                ORDER BY distance
                LIMIT %s
                """,
                (query_vector, top_n)
            )
            rows = cur.fetchall()

        if threshold is not None:
            rows = [row for row in rows if row["distance"] <= threshold]
        return [
            {"id": row["id"], "text": row["text"], "distance": row["distance"]}
            for row in rows
        ]

    def delete(self, id_: int) -> None:
        """Delete a vector by its ID."""

        with self.conn.cursor() as cur:
            cur.execute(
                """
                DELETE
                FROM vectors
                WHERE id = %s
                """,
                (id_,)
            )
            self.conn.commit()

    def reset(self) -> None:
        """Reset (delete) all vectors in the database."""

        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM vectors")
            self.conn.commit()

    def count(self) -> int:
        """Return the total number of stored quotes."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM vectors")
            return cur.fetchone()[0]

    def ensure_vectors_table(self, dimension: int):
        if not isinstance(dimension, int) or not (1 <= dimension <= 10000):
            raise ValueError(f"Unsafe or invalid vector dimension: {dimension}")

        query = sql.SQL(
            """
            CREATE TABLE IF NOT EXISTS vectors 
            (id SERIAL PRIMARY KEY, text TEXT NOT NULL, embedding VECTOR({}));
            """
        ).format(sql.Literal(dimension))  # Safe insertion of a literal

        with self.conn.cursor() as cur:
            cur.execute(query)
            self.conn.commit()

    def list_all(self) -> List[Dict]:
        """Return all stored quotes with their IDs and text."""
        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT id, text FROM vectors ORDER BY id")
            return cur.fetchall()
