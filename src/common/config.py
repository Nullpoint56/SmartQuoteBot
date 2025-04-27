from pydantic_settings import SettingsConfigDict, BaseSettings


class VectorStoreServiceConfig(BaseSettings):
    db_url: str
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dimension: int = 384

    model_config = SettingsConfigDict(env_nested_delimiter="__")