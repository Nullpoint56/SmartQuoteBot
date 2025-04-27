from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from vector_store_service.embedders import SentenceTransformerEmbedder
from vector_store_service.vector_stores import PgVectorVectorStore


class AIManager:
    """Bootstraps AI modules: Embedder, VectorStore."""

    def __init__(self, config):
        self.config = config
        self.embedder = None
        self.vector_store = None
        self.db_engine = None
        self.db_session = None

    def boot(self):
        """Load all AI resources: models, database connections."""
        # 1. Create Embedder
        self.embedder = SentenceTransformerEmbedder(model_name=self.config.ai.model_name)

        # 2. Create DB Engine
        self.db_engine = create_engine(self.config.db.pgvector_url)

        # 3. Create DB Session
        SessionLocal = sessionmaker(bind=self.db_engine)
        self.db_session = SessionLocal()

        # 4. Create VectorStore
        self.vector_store = PgVectorVectorStore(
            db_session=self.db_session,
            dimension=self.config.ai.embedding_dimension
        )

    def shutdown(self):
        """Clean up AI resources."""
        if self.db_session:
            self.db_session.close()
