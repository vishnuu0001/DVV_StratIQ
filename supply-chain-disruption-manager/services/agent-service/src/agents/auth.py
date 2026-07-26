# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: API key authentication dependency.
# Date: 2026-04-05
# ---------------------------------------------------------------------------
"""API key authentication dependency."""
from __future__ import annotations

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader, APIKeyQuery

from agents.config import get_settings

_API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
_API_KEY_QUERY = APIKeyQuery(name="api_key", auto_error=False)


# Function: require_api_key
async def require_api_key(
    header_key: str | None = Security(_API_KEY_HEADER),
    query_key: str | None = Security(_API_KEY_QUERY),
) -> str:
    """FastAPI dependency that validates the API key from the X-API-Key header
    or an api_key query param (needed for EventSource, which cannot set headers)."""
    settings = get_settings()
    api_key = header_key or query_key
    if not api_key or api_key != settings.agent_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return api_key
