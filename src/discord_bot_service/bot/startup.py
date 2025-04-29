# src/discord_bot_service/startup.py

from logging.handlers import RotatingFileHandler
import logging
import os
from pathlib import Path

from common.config import VectorStoreServiceConfig, AppConfig
from common.utils.connection_providers import PostgresConnectionProvider
from sentry_sdk.integrations.logging import LoggingIntegration
import sentry_sdk

from discord_bot_service.managers.quote_manager import QuoteManager
from common.interfaces.connection_provider import ConnectionProvider
from vector_store_service.service import VectorStoreService


class AppContext:
    def __init__(self):
        self.logger = None
        self.config = AppConfig()

        self.vector_store_service: VectorStoreService = None
        self.quote_manager: QuoteManager = None

    def boot(self):
        """Initialize all discord_bot_service services."""
        self._init_logging()
        self._init_sentry()
        self._init_vector_store_services()

    def shutdown(self):
        """Gracefully shut down."""
        self.logger.info("Shutting down Rodof Bot.")

        if self.vector_store_service:
            self.vector_store_service.shutdown()

    def _init_logging(self):
        """Initialize logging: console + rotating file handler."""

        # Determine base directory (safely climb up 2 levels)
        base_dir = Path(__file__).resolve()
        for _ in range(2):
            if base_dir.parent != base_dir:
                base_dir = base_dir.parent
            else:
                break
        logs_dir = base_dir / "logs"
        os.makedirs(logs_dir, exist_ok=True)

        self.logger = logging.getLogger("rodof")
        self.logger.setLevel(logging.INFO)

        # Clear previous handlers to avoid duplicates
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        try:
            console_handler.stream.reconfigure(encoding="utf-8")
        except AttributeError:
            pass
        self.logger.addHandler(console_handler)

        # File handler
        file_handler = RotatingFileHandler(
            logs_dir / "bot.log",
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

    def _init_vector_store_services(self):
        """Initialize Vector Store service."""
        self.logger.info("Bootstrapping Vector Store service...")

        # Load Vector Store config from environment
        vector_store_config = VectorStoreServiceConfig()

        # Connection Provider (PostgreSQL for now)
        conn_provider: ConnectionProvider = PostgresConnectionProvider(vector_store_config.db_url)

        # Vector Store Service
        self.vector_store_service = VectorStoreService(
            connection_provider=conn_provider,
            config=vector_store_config
        )
        self.vector_store_service.boot()

        # Quote Manager
        self.quote_manager = QuoteManager(
            vector_store_service=self.vector_store_service
        )

        self.logger.info("Vector Store service initialized successfully.")


# Singleton-style access
app_ctx = AppContext()
