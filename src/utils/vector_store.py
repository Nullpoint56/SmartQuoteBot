from typing import List, Dict

from numpy import ndarray
from psycopg import sql
from psycopg.rows import dict_row


class PgVectorStore:
    def __init__(self, connection, dimension: int = 384):
        self.conn = connection
        self.dimension = dimension

    def add(self, embeddings: ndarray, texts: List[str]) -> None:
        if embeddings.ndim != 2 or embeddings.shape[1] != self.dimension:
            raise ValueError(f"Invalid embedding dimensions: expected (*, {self.dimension}), got {embeddings.shape}.")

        with self.conn.cursor() as cur:
            for embedding, text in zip(embeddings, texts):
                cur.execute(
                    "INSERT INTO vectors (text, embedding) VALUES (%s, %s)",
                    (text, list(embedding))
                )
            self.conn.commit()

    def search(self, embedding: ndarray, top_n: int = 3, metric: str = "cosine", threshold: float = None) -> List[Dict]:
        if embedding.ndim != 2 or embedding.shape[1] != self.dimension:
            raise ValueError(
                f"Invalid query embedding dimensions: expected (*, {self.dimension}), got {embedding.shape}.")

        query_vector = list(embedding[0])

        operator_map = {
            "cosine": "<=>",
            "euclidean": "<->",
            "inner_product": "<#>"
        }

        operator = operator_map.get(metric)
        if not operator:
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
            if metric == "cosine":
                threshold = 1 - threshold
            rows = [row for row in rows if row["distance"] <= threshold]

        return [{"id": row["id"], "text": row["text"], "distance": row["distance"]} for row in rows]

    def delete(self, id_: int) -> None:
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM vectors WHERE id = %s", (id_,))
            self.conn.commit()

    def reset(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM vectors")
            self.conn.commit()

    def count(self) -> int:
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM vectors")
            return cur.fetchone()[0]

    def ensure_vectors_table(self, dimension: int):
        if not isinstance(dimension, int) or not (1 <= dimension <= 10000):
            raise ValueError(f"Unsafe or invalid vector dimension: {dimension}")

        query = sql.SQL(
            """
            CREATE TABLE IF NOT EXISTS vectors
            (
                id
                SERIAL
                PRIMARY
                KEY,
                text
                TEXT
                NOT
                NULL,
                embedding
                VECTOR(
            {}
            ));
            """
        ).format(sql.Literal(dimension))

        with self.conn.cursor() as cur:
            cur.execute(query)
            self.conn.commit()

    def list_all(self) -> List[Dict]:
        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT id, text FROM vectors ORDER BY id")
            return cur.fetchall()
