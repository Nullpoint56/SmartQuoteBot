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
    logs_dir: Optional[Path] = Field(default=None, validation_alias="LOGS_DIR")

    def resolve_defaults(self):
        if self.logs_dir is None:
            self.logs_dir = self.base_dir / "logs"

class VectorStoreSettings(BaseModel):
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    dbname: str = Field(default="mydb")
    user: str = Field(default="myuser")
    password: str = Field(default="mypassword")
    dimension: int = Field(default=384)
    metric: str = Field(default="cosine")
    threshold: float = Field(default=0.5)


class EmbedderSettings(BaseModel):
    model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class AppConfig(BaseSettings):
    bot: BotSettings
    sentry: SentrySettings = SentrySettings()
    paths: PathSettings = PathSettings()
    embedder: EmbedderSettings = EmbedderSettings()
    vector_store: VectorStoreSettings = VectorStoreSettings()

    def model_post_init(self, __context):
        self.paths.resolve_defaults()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__"
    )
