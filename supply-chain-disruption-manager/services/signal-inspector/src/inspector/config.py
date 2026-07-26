# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Application configuration loaded from environment variables.
# Date: 2026-02-26
# ---------------------------------------------------------------------------
"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Root of the service directory.
SERVICE_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ---- Database ----
    postgres_url: str = (
        "postgresql+asyncpg://sc_admin:sc_secret@localhost:5432/disruption_mgr"
    )

    # ---- Redis ----
    redis_url: str = "redis://localhost:6379/0"

    # ---- KG Service ----
    kg_base_url: str = "http://kg-service:8001"
    kg_api_key: str = "kg-dev-key-change-in-prod"

    # ---- Agent Service ----
    agent_base_url: str = "http://agent-service:8002"
    agent_api_key: str = "agent-dev-key-change-in-prod"

    # ---- ERP HMAC ----
    inspector_erp_hmac_secret: str = "erp-hmac-secret-change-in-prod"

    # ---- MQTT ----
    mqtt_broker: str = "localhost"
    mqtt_port: int = 1883
    mes_mqtt_enabled: bool = False

    # ---- WMS Poll ----
    wms_poll_url: str = ""
    wms_poll_interval_seconds: int = 30

    # ---- Logging ----
    log_level: str = "INFO"
    log_json: bool = True

    # ---- App ----
    environment: str = "development"
    debug: bool = False
    cors_origins: str = "http://localhost,http://localhost:5173,http://127.0.0.1:5173"

    # ---- Paths ----
    schemas_dir: Path = SERVICE_ROOT / "schemas" / "events"
    config_dir: Path = SERVICE_ROOT / "config"

    # Function: validate_postgres_url
    @field_validator("postgres_url", mode="before")
    @classmethod
    def validate_postgres_url(cls, v: str) -> str:
        # Ensure asyncpg driver
        if v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


# Function: get_settings
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
