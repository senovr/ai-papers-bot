"""Application configuration with Pydantic settings."""

from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Required settings (with defaults for development)
    telegram_bot_token: str = Field(default="DEV_TOKEN", description="Telegram Bot Token")
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/ai_papers_bot",
        description="PostgreSQL connection URL with asyncpg driver",
    )

    # LLM API keys
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    google_api_key: Optional[str] = Field(default=None, description="Google Gemini API key")
    gemini_api_key: Optional[str] = Field(default=None, description="Google Gemini API key (alias)")

    # Optional settings
    redis_url: Optional[str] = Field(default=None, description="Redis connection URL")
    app_env: str = Field(default="development", description="Application environment")
    debug: bool = Field(default=True, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # Database connection pool settings
    database_pool_size: int = Field(default=5, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, description="Database max overflow connections")
    database_pool_recycle: int = Field(
        default=3600, description="Database connection recycle time (seconds)"
    )

    # Webhook settings
    webhook_url: Optional[str] = Field(default=None, description="Webhook base URL")
    webhook_port: int = Field(default=8443, description="Webhook server port")
    webhook_path: str = Field(default="/webhook", description="Webhook path")

    # Admin settings
    admin_user_ids: list[int] = Field(default_factory=list, description="Admin user Telegram IDs")

    # Database pool settings
    database_pool_size: int = Field(default=5, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, description="Max overflow connections")
    database_pool_recycle: int = Field(
        default=3600, description="Recycle connections after N seconds"
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def convert_to_async_url(cls, v: str) -> str:
        """Convert postgres:// to postgres+asyncpg://"""
        if v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @lru_cache(maxsize=1)
    def get_settings(cls) -> "Settings":
        """Get or create settings singleton."""
        global _settings
        if _settings is None:
            _settings = Settings()
        return _settings

    def __hash__(self) -> int:
        return hash((self.telegram_bot_token, self.database_url))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Settings):
            return False
        return (
            self.telegram_bot_token == other.telegram_bot_token
            and self.database_url == other.database_url
        )


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Convenience alias
settings: Settings = get_settings()
