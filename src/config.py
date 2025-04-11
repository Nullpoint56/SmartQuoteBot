import os
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", "development").lower()

# Discord
TOKEN = os.getenv("DISCORD_TOKEN", "your-bot-token")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")

# Sentry
SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_SEND_PII = os.getenv("SENTRY_SEND_PII", "false").lower() == "true"
SENTRY_TRACES_SAMPLE_RATE = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0"))
SENTRY_PROFILING_SAMPLE_RATE = float(os.getenv("SENTRY_PROFILING_SAMPLE_RATE", "0.0"))
