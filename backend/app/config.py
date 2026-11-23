from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed application settings."""

    model_config = SettingsConfigDict(
        env_prefix="SENTINEL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Sentinel Explorer API"
    app_version: str = "0.1.0"
    cursor_encryption_key: SecretStr | None = Field(default=None, repr=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
