# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: API key authentication dependency.
# Date: 2026-04-19
# ---------------------------------------------------------------------------
"""API key authentication dependency."""
from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import APIKeyHeader

from kg.config import get_settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# Function: _problem
def _problem(status: int, title: str, detail: str) -> dict:
    return {"type": f"urn:kg:error:{title.lower().replace(' ', '-')}", "title": title, "status": status, "detail": detail}


# Function: require_api_key
async def require_api_key(
    request: Request,
    api_key: Annotated[str | None, Depends(_api_key_header)] = None,
) -> None:
    """Raise 401 if X-API-Key is missing or does not match KG_API_KEY."""
    settings = get_settings()
    if api_key is None or not secrets.compare_digest(api_key, settings.kg_api_key):
        raise HTTPException(
            status_code=401,
            detail=_problem(401, "Unauthorized", "Missing or invalid X-API-Key header"),
            headers={"WWW-Authenticate": "ApiKey"},
        )
