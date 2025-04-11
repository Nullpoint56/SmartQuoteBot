from logging.handlers import RotatingFileHandler
import logging
import os
import json

from config import (
    ENV,
    SENTRY_DSN,
    SENTRY_SEND_PII,
    SENTRY_TRACES_SAMPLE_RATE,
    SENTRY_PROFILING_SAMPLE_RATE
)
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from paths import DATA_DIR, QUOTES_FILE, LOGS_DIR


class AppContext:
    def __init__(self):
        self.logger = None

    def boot(self):
        self._init_logging()
        self._init_sentry()
        self._bootstrap_data()
        self.logger.info(f"🚀 Rodof Bot starting in {ENV.upper()} mode")

    def shutdown(self):
        self.logger.info("👋 Shutting down Rodof Bot")

    def _init_logging(self):
        os.makedirs(LOGS_DIR, exist_ok=True)

        self.logger = logging.getLogger("rodof")
        log_level = logging.DEBUG if ENV == "development" else logging.INFO
        self.logger.setLevel(log_level)

        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        file_handler = RotatingFileHandler(
            os.path.join(LOGS_DIR, "bot.log"),
            maxBytes=5_000_000,
            backupCount=3
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def _init_sentry(self):
        if SENTRY_DSN and ENV == "production":
            sentry_logging = LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            )

            sentry_sdk.init(
                dsn=SENTRY_DSN,
                integrations=[sentry_logging],
                send_default_pii=SENTRY_SEND_PII,
                traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
                profile_session_sample_rate=SENTRY_PROFILING_SAMPLE_RATE
            )
            self.logger.info("✅ Sentry initialized")
        else:
            self.logger.info(f"ℹ️ Sentry not enabled (ENV={ENV})")

    def _bootstrap_data(self):
        if not DATA_DIR.exists():
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            self.logger.info("📁 Created data directory")

        if not QUOTES_FILE.exists():
            self.logger.warning("🆕 quotes.json not found — creating with empty list.")
            with open(QUOTES_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)
        else:
            try:
                with open(QUOTES_FILE, "r", encoding="utf-8") as f:
                    quotes = json.load(f)
                    self.logger.info("📖 quotes.json exists. Loaded %d quotes.", len(quotes))
                    if ENV == "development":
                        preview = quotes[:3]
                        self.logger.debug("📝 Preview: %s", preview)
            except Exception:
                self.logger.exception("💥 Failed to inspect existing quotes.json:")


# Singleton-style access
app_ctx = AppContext()
