"""Application configuration."""

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Telegram Bot
    telegram_bot_token: str = Field(..., description="Telegram Bot Token")

    # Database
    database_url: PostgresDsn = Field(
        ...,
        description="PostgreSQL connection URL with asyncpg driver",
    )
    database_pool_size: int = Field(default=10, description="Database connection pool size")
    database_max_overflow: int = Field(default=20, description="Database pool max overflow")

    # LLM APIs
    anthropic_api_key: str = Field(..., description="Anthropic API key")
    gemini_api_key: str | None = Field(default=None, description="Google Gemini API key")

    # Redis (optional)
    redis_url: str | None = Field(default=None, description="Redis connection URL")

    # Application
    app_env: str = Field(default="development", description="Application environment")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # Webhook (production)
    webhook_url: str | None = Field(default=None, description="Webhook base URL")
    webhook_port: int = Field(default=8443, description="Webhook server port")
    webhook_path: str = Field(default="/webhook", description="Webhook path")

    # Bot settings
    admin_user_ids: list[int] = Field(default_factory=list, description="Admin user Telegram IDs")

    @field_validator("database_url", mode="before")
    @classmethod
    def convert_to_async_url(cls, v: PostgresDsn) -> PostgresDsn:
        """Convert postgres:// to postgres+asyncpg://"""
        if v and v.scheme == "postgresql":
            return PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=v.username,
                password=v.password,
                host=v.host,
                port=v.port,
                path=v.path,
            )
        return v
