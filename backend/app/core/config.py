from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="SGA-EDU")
    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = False
    database_url: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/sga")
    secret_key: str = Field(default="change-me-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expire_minutes: int = Field(default=480)
    default_rede_id: int = 1
    cors_origins: str = Field(default="http://localhost:5173,http://127.0.0.1:5173,http://localhost,http://127.0.0.1")


@lru_cache
def get_settings() -> Settings:
    return Settings()
