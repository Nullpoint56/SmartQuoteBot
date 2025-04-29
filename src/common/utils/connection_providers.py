import psycopg
from common.config import DatabaseConfig
from common.interfaces.connection_provider import ConnectionProvider

class PostgresConnectionProvider(ConnectionProvider):
    def __init__(self, db_config: DatabaseConfig) -> None:
        self.db_config = db_config
        self.conn: psycopg.Connection = None

    def connect(self) -> psycopg.Connection:
        """Establish and return the psycopg3 connection."""
        if not self.conn:
            conn_url = self._build_conn_url()
            self.conn = psycopg.connect(conn_url)
        return self.conn

    def shutdown(self) -> None:
        """Gracefully close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def _build_conn_url(self) -> str:
        """Build database URL for PostgreSQL."""
        db = self.db_config
        return f"postgresql://{db.user}:{db.password}@{db.host}:{db.port}/{db.database}"
