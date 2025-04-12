from logging.handlers import RotatingFileHandler
import logging
import os
import json

from config import AppConfig
from sentry_sdk.integrations.logging import LoggingIntegration
import sentry_sdk

from utils.data_collector import MessageCollector
from utils.faiss_handler import QuoteSearch


class AppContext:
    def __init__(self):
        self.logger = None
        self.config = AppConfig()
        self.quote_search = QuoteSearch(
            index_path=self.config.paths.quotes_index_file,
            json_path=self.config.paths.quotes_file,
            model_name=self.config.ai.embedding_model
        )
        self.collector = MessageCollector(self.config.data_dir / "collected_messages.jsonl")

    def boot(self):
        self._init_logging()
        self._init_sentry()
        self._bootstrap_data()

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

    def _bootstrap_data(self):
        if not self.config.paths.data_dir.exists():
            self.config.paths.data_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info("Created data directory")

        if not self.config.paths.quotes_file.exists():
            self.logger.warning("quotes.json not found — creating with empty list.")
            with open(self.config.paths.quotes_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)
        else:
            try:
                with open(self.config.paths.quotes_file, "r", encoding="utf-8") as f:
                    quotes = json.load(f)
                    self.logger.info("quotes.json exists. Loaded %d quotes.", len(quotes))
                    preview = quotes[:3]
                    self.logger.debug("Preview: %s", preview)
            except Exception:
                self.logger.exception("Failed to inspect existing quotes.json:")

# Singleton-style access
app_ctx = AppContext()
