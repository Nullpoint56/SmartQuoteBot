from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    token: str = Field(default="your_api_token",
                       description="Discord bot token used to authenticate the bot with the Discord API.")
    command_prefix: str = Field(default="/", description="Prefix used for bot commands.")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )