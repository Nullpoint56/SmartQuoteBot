from logging.handlers import RotatingFileHandler
import logging
import os
from psycopg import connect
from sentry_sdk.integrations.logging import LoggingIntegration
import sentry_sdk

from src.config import AppConfig
from src.utils.QuoteManager import QuoteManager
from src.utils.embedder import SentenceTransformerEmbedder
from src.utils.vector_store import PgVectorStore


class AppContext:
    def __init__(self):
        self.logger = None
        self.config: AppConfig = AppConfig()
        self.vector_store: PgVectorStore = None
        self.embedder: SentenceTransformerEmbedder = None
        self.quote_manager: QuoteManager = None

    def boot(self):
        try:
            self._init_logging()
            self._init_sentry()
            self._init_vector_db()
            self._init_embedder()
            self._init_quote_manager()
        except Exception as e:
            print(f"An Exception occurred while booting the bot: {e}")

    def shutdown(self):
        self.logger.info("Shutting down Rodof Bot")

    def _init_logging(self):
        os.makedirs(self.config.paths.logs_dir, exist_ok=True)

        self.logger = logging.getLogger("rodof")
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.stream.reconfigure(encoding='utf-8')
        self.logger.addHandler(console_handler)

        file_handler = RotatingFileHandler(
            self.config.paths.logs_dir / "bot.log",
            maxBytes=5_000_000,
            backupCount=3
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def _init_sentry(self):
        sentry_cfg = self.config.sentry
        if sentry_cfg.enable and sentry_cfg.dsn:
            sentry_logging = LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            )

            sentry_sdk.init(
                dsn=sentry_cfg.dsn,
                integrations=[sentry_logging],
                send_default_pii=sentry_cfg.send_pii,
                traces_sample_rate=sentry_cfg.traces_sample_rate,
                profile_session_sample_rate=sentry_cfg.profiling_sample_rate,
            )
            self.logger.info("Sentry initialized")
        else:
            self.logger.info("Sentry not enabled")

    def _init_vector_db(self):
        cfg = self.config.vector_store
        try:
            conn = connect(
                host=cfg.host,
                port=cfg.port,
                dbname=cfg.dbname,
                user=cfg.user,
                password=cfg.password,
            )
            self.vector_store = PgVectorStore(connection=conn, dimension=cfg.dimension)
            self.vector_store.ensure_vectors_table(dimension=cfg.dimension)
            self.logger.info("Vector store initialized")
        except Exception as e:
            self.logger.error("Failed to initialize vector store", exc_info=e)
            raise

    def _init_embedder(self):
        self.embedder = SentenceTransformerEmbedder(self.config.embedder.model_name)
        self.embedder.boot()
        self.logger.info("Embedder model loaded")

    def _init_quote_manager(self):
        self.quote_manager = QuoteManager(
            vector_store=self.vector_store,
            embedder=self.embedder,
        )


# Singleton-style access
app_ctx = AppContext()
