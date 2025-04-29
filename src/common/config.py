from typing import Optional
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class SentrySettings(BaseSettings):
    enable: bool = Field(default=False, description="Enable or disable Sentry error tracking.")
    dsn: Optional[str] = Field(default=None, description="Sentry DSN (Data Source Name) URL for reporting errors.")
    send_pii: bool = Field(default=False,
                           description="Allow sending personally identifiable information (PII) to Sentry.")
    traces_sample_rate: float = Field(default=0.0,
                                      description="Sampling rate for Sentry transaction tracing (0.0 to 1.0).")
    profiling_sample_rate: float = Field(default=0.0,
                                         description="Sampling rate for Sentry profiling sessions (0.0 to 1.0).")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

class DatabaseConfig(BaseModel):
    """Generic database configuration (PostgreSQL, etc.)."""
    user: str = Field(default="postgres", description="Database username")
    password: str = Field(default="postgres", description="Database password")
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    database: str = Field(default="vectorstore", description="Database name")
