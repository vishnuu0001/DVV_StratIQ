# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Application configuration via pydantic-settings.
# Date: 2026-02-25
# ---------------------------------------------------------------------------
"""Application configuration via pydantic-settings."""
from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neo4j"
    kg_api_key: str = "dev-key"
    kg_seed_enabled: bool = True
    cors_origins: str = "http://localhost,http://localhost:5173,http://127.0.0.1:5173"
    log_level: str = "INFO"
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    # Function: normalise_log_level
    @field_validator("log_level")
    @classmethod
    def normalise_log_level(cls, v: str) -> str:
        return v.upper()


_settings: Settings | None = None


# Function: get_settings
def get_settings() -> Settings:
    global _settings  # noqa: PLW0603
    if _settings is None:
        _settings = Settings()
    return _settings
