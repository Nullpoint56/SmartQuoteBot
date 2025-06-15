from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, BaseModel


class BotSettings(BaseModel):
    model_config = {
        "env_nested_delimiter": "__"  # Enables nested env loading like BOT__TOKEN
    }
    token: str
    command_prefix: str = "/"


class SentrySettings(BaseModel):
    enable: bool = False
    dsn: Optional[str] = None
    send_pii: bool = False
    traces_sample_rate: float = 0.0
    profiling_sample_rate: float = 0.0


class PathSettings(BaseModel):
    base_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[1])
    data_dir: Optional[Path] = Field(default=None, validation_alias="DATA_DIR")
    logs_dir: Optional[Path] = Field(default=None, validation_alias="LOGS_DIR")
    quotes_file: Optional[Path] = Field(default=None, validation_alias="QUOTES_FILE")
    quotes_index_file: Optional[Path] = Field(default=None, validation_alias="QUOTES_INDEX_FILE")

    def resolve_defaults(self):
        if self.data_dir is None:
            self.data_dir = self.base_dir / "data"
        if self.logs_dir is None:
            self.logs_dir = self.base_dir / "logs"
        if self.quotes_file is None:
            self.quotes_file = self.data_dir / "quotes.json"
        if self.quotes_index_file is None:
            self.quotes_index_file = self.data_dir / "quotes.index"


class AISettings(BaseModel):
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class AppConfig(BaseSettings):
    bot: BotSettings
    sentry: SentrySettings = SentrySettings()
    paths: PathSettings = PathSettings()
    ai: AISettings = AISettings()

    def model_post_init(self, __context):
        self.paths.resolve_defaults()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__"
    )
