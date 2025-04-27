from typing import List, Dict
import numpy as np
import psycopg

class PgVectorVectorStore:
    """Vector store using PostgreSQL with pgvector extension, pure psycopg3."""

    def __init__(self, conn: psycopg.Connection, dimension: int = 384):
        """
        Args:
            conn (psycopg.Connection): psycopg3 DB connection.
            dimension (int): Dimension of the embeddings.
        """
        self.conn = conn
        self.dimension = dimension

    def add(self, embeddings: np.ndarray, metadatas: List[Dict]) -> None:
        """Add embeddings and associated metadata to the vector store."""
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
