from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from common.config import DatabaseConfig


class VectorStoreServiceConfig(BaseSettings):
    """Configuration for the vector store service."""
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)

    model_config = SettingsConfigDict(env_file=".env")

