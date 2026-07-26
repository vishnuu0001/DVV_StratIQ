# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Application configuration via pydantic-settings.
# Date: 2025-11-01
# ---------------------------------------------------------------------------
"""Application configuration via pydantic-settings."""
from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    postgres_url: str = "postgresql+asyncpg://sc_admin:sc_secret@localhost:5432/disruption_mgr"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # KG Service
    kg_base_url: str = "http://localhost:8001"
    kg_api_key: str = "kg-dev-key"

    # Auth
    agent_api_key: str = "agent-dev-key"

    # LLM (local Ollama)
    ollama_base_url: str = "http://localhost:11434"
    orchestrator_model: str = "llama3.1:8b"
    specialist_model: str = "llama3.1:8b"
    mock_agents: bool = True

    # Logging
    log_level: str = "INFO"
    log_json: bool = True

    # App
    environment: str = "development"
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    # Function: normalise_log_level
    @field_validator("log_level")
    @classmethod
    def normalise_log_level(cls, v: str) -> str:
        return v.upper()

    # Function: use_mock
    @property
    def use_mock(self) -> bool:
        """True when MOCK_AGENTS=true. Live mode calls the local Ollama model."""
        return self.mock_agents


_settings: Settings | None = None


# Function: get_settings
def get_settings() -> Settings:
    global _settings  # noqa: PLW0603
    if _settings is None:
        _settings = Settings()
    return _settings
