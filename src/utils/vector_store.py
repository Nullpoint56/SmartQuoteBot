from typing import  List, Dict
from psycopg import Connection
from psycopg.rows import dict_row
from numpy import ndarray


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

    def add(self, embeddings: ndarray, metadatas: List[Dict]) -> None:
        """Add embeddings and associated metadata to the vector store."""

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
                SELECT id, text, label, embedding {operator} %s AS distance
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
            {"id": row["id"], "text": row["text"], "label": row["label"], "distance": row["distance"]}
            for row in rows
        ]

    def delete(self, id_: int) -> None:
        """Delete a vector by its ID."""

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

        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM vectors")
            self.conn.commit()

    def count(self) -> int:
        """Return the total number of stored quotes."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM vectors WHERE label = 'quote'")
            return cur.fetchone()[0]



