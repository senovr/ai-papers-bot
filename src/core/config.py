"""Application configuration with Pydantic settings."""

from functools import lru_cache
from typing import Annotated

from pydantic import Field,from pydantic_settings import BaseSettings,SettingsConfigDict


from pydantic import PostgresDsn


from typing import Any


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    telegram_bot_token: str = Field(..., description="Telegram Bot Token")
    database_url: PostgresDsn = Field(
        ...,
        description="PostgreSQL connection URL with asyncpg driver",
    )
    database_pool_size: int = Field(default=10, description="Database connection pool size")
    database_max_overflow: int = Field(default=20, description="Database pool max overflow")
    anthropic_api_key: str = Field(..., description="Anthropic API key")
    gemini_api_key: str | None = Field(default=None, description="Google Gemini API key")
    redis_url: str | None = Field(default=None, description="Redis connection URL")
    app_env: str = Field(default="development", description="Application environment")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    webhook_url: str | None = Field(default=None, description="Webhook base URL")
    webhook_port: int = Field(default=8443, description="Webhook server port")
    webhook_path: str = Field(default="/webhook", description="Webhook path")
    admin_user_ids: list[int] = Field(default_factory=list, description="Admin user Telegram IDs")
    @field_validator("database_url", mode="before")
    @classmethod
    def convert_to_async_url(cls, v: PostgresDsn | str) -> PostgresDsn:
        """Convert postgres:// to postgres+asyncpg://"""
        url_str = str(v)
        if url_str.startswith("postgresql://") and not url_str.startswith("postgresql+asyncpg://"):
            url_str = url_str.replace("postgresql://", "postgresql+asyncpg://", 1)
        return PostgresDsn(url_str)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get or create settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


settings = get_settings()
