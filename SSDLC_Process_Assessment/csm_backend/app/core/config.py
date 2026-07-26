# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — csm_backend/app/core (config.py)
# Date: 2025-08-14
# ---------------------------------------------------------------------------
from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

APP_ENV: str = os.getenv("APP_ENV", "development")
APP_PORT: int = int(os.getenv("APP_PORT", "8092"))
APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

CORS_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
]

_extra_origins = os.getenv("CORS_ORIGINS", "")
if _extra_origins:
    for _o in _extra_origins.split(","):
        _o = _o.strip()
        if _o and _o not in CORS_ORIGINS:
            CORS_ORIGINS.append(_o)

MODULE_NAME = "Consolidation Savings Model"
API_PREFIX = "/api"
