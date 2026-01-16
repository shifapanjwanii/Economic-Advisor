"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Configuration
    openai_api_key: str = ""

    # API Keys for external services
    fred_api_key: str = ""
    news_api_key: str = ""
    exchange_rate_api_key: str = ""

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
