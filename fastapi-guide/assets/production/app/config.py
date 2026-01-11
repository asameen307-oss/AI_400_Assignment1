"""Application configuration using pydantic-settings."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Application
    app_name: str = "FastAPI App"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./database.db"

    # Security
    secret_key: str = "change-this-in-production"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
