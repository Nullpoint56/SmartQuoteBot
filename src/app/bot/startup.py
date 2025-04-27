# src/app/startup.py

from logging.handlers import RotatingFileHandler
import logging
import os

from common.utils.connection_providers import PostgresConnectionProvider
from config import AppConfig
from sentry_sdk.integrations.logging import LoggingIntegration
import sentry_sdk

from app.managers.quote_manager import QuoteManager
from common.interfaces.connection_provider import ConnectionProvider
from vector_store_service.service import VectorStoreService


class AppContext:
    def __init__(self):
        self.logger = None
        self.config = AppConfig()

        self.vector_store_service: VectorStoreService = None
        self.quote_manager: QuoteManager = None

    def boot(self):
        """Initialize all app services."""
        self._init_logging()
        self._init_sentry()
        self._bootstrap_data()
        self._init_ai_services()

    def shutdown(self):
        """Gracefully shut down."""
        self.logger.info("Shutting down Rodof Bot.")

        if self.vector_store_service:
            self.vector_store_service.shutdown()

    def _init_logging(self):
        os.makedirs(self.config.paths.logs_dir, exist_ok=True)

        self.logger = logging.getLogger("rodof")
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.stream.reconfigure(encoding="utf-8")
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

    def _bootstrap_data(self):
        """For now keep this to prepare data folders, later might move DB migration here."""
        if not self.config.paths.data_dir.exists():
            self.config.paths.data_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info("Created data directory")

        # We might remove quotes.json handling later — not needed if purely DB

    def _init_ai_services(self):
        """Initialize AI related services: vector store + quote manager."""
        self.logger.info("Bootstrapping AI services...")

        # Connection Provider (PostgreSQL for now)
        conn_provider: ConnectionProvider = PostgresConnectionProvider(self.config.pgvector.db_url)

        # Vector Store Service
        self.vector_store_service = VectorStoreService(
            connection_provider=conn_provider,
            model_name=self.config.ai.embedding_model,
            dimension=self.config.ai.embedding_dimension
        )
        self.vector_store_service.boot()

        # Quote Manager
        self.quote_manager = QuoteManager(
            vector_store_service=self.vector_store_service
        )

        self.logger.info("AI services initialized successfully.")

# Singleton-style access
app_ctx = AppContext()
