import psycopg
from common.interfaces.connection_provider import ConnectionProvider


class PostgresConnectionProvider(ConnectionProvider):
    """Provides a psycopg3 Postgres connection."""

    def __init__(self, db_url: str):
        self.db_url = db_url
        self.conn: psycopg.Connection = None

    def connect(self) -> psycopg.Connection:
        """Establish and return the psycopg3 connection."""
        if not self.conn:
            self.conn = psycopg.connect(self.db_url)
        return self.conn

    def shutdown(self) -> None:
        """Close the connection."""
        if self.conn:
            self.conn.close()
