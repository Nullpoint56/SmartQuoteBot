from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EmbeddingServiceConfig(BaseSettings):
    """Configuration for the embedding model service."""
    embedding_model: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        description="Name of the embedding model"
    )
    embedding_dimension: int = Field(
        default=384,
        description="Dimension of the embedding output"
    )

    model_config = SettingsConfigDict(env_file=".env")