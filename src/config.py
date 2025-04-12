from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class AppConfig(BaseSettings):
    # Bot
    token: str
    command_prefix: str = "/"

    # Sentry
    enable_sentry: bool = False
    sentry_dsn: Optional[str] = None
    sentry_send_pii: bool = False
    sentry_traces_sample_rate: float = 0.0
    sentry_profiling_sample_rate: float = 0.0

    # Paths (env-overridable)
    base_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[1])
    data_dir: Optional[Path] = Field(default=None, validation_alias="DATA_DIR")
    logs_dir: Optional[Path] = Field(default=None, validation_alias="LOGS_DIR")
    quotes_file: Optional[Path] = Field(default=None, validation_alias="QUOTES_FILE")

    def model_post_init(self, __context):
        if self.data_dir is None:
            self.data_dir = self.base_dir / "data"
        if self.logs_dir is None:
            self.logs_dir = self.base_dir / "logs"
        if self.quotes_file is None:
            self.quotes_file = self.data_dir / "quotes.json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
