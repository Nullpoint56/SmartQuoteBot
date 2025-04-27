from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    token: str
    command_prefix: str = "/"

    model_config = SettingsConfigDict(env_nested_delimiter="__")


class SentrySettings(BaseSettings):
    enable: bool = False
    dsn: Optional[str] = None
    send_pii: bool = False
    traces_sample_rate: float = 0.0
    profiling_sample_rate: float = 0.0

    model_config = SettingsConfigDict(env_nested_delimiter="__")


class AppConfig:
    """Composition-only AppConfig. Doesn't load env directly."""

    def __init__(self):
        self.bot = BotSettings()
        self.sentry = SentrySettings()
