"""
Application configuration using pydantic-settings.
All settings are loaded from environment variables / .env file.
"""

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ─── App ───────────────────────────────────────────────────────────────
    APP_NAME: str = "APK Manager"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ─── Database ─────────────────────────────────────────────────────────
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "apk_user"
    DB_PASS: str = "apk_pass"
    DB_NAME: str = "apk_manager"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # ─── JWT ──────────────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # ─── Storage ──────────────────────────────────────────────────────────
    STORAGE_PATH: str = "/storage"
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500 MB

    # ─── CORS ─────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "*"


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
