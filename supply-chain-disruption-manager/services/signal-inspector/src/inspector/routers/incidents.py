# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: GET /incidents, GET /incidents/stream — proxy to agent-service.
# Date: 2026-02-05
# ---------------------------------------------------------------------------
"""GET /incidents, GET /incidents/stream — proxy to agent-service."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, AsyncGenerator

import httpx
import structlog
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from inspector.config import get_settings

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["incidents"])


# Function: _agent_headers
def _agent_headers() -> dict[str, str]:
    settings = get_settings()
    return {"X-API-Key": settings.agent_api_key}


# Function: list_incidents
@router.get("/incidents")
async def list_incidents(request: Request) -> Any:
    """Proxy GET /incidents to agent-service."""
    settings = get_settings()
    http_client: httpx.AsyncClient = request.app.state.http_client

    # Forward all query parameters
    params = dict(request.query_params)

    try:
        resp = await http_client.get(
            f"{settings.agent_base_url}/incidents",
            params=params,
            headers=_agent_headers(),
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=exc.response.text,
        ) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("incidents.proxy_error")
        raise HTTPException(status_code=502, detail=f"Agent service unavailable: {exc}") from exc


# Function: stream_incidents
@router.get("/incidents/stream")
async def stream_incidents(request: Request) -> StreamingResponse:
    """SSE proxy to agent-service /incidents/stream."""
    settings = get_settings()
    http_client: httpx.AsyncClient = request.app.state.http_client

    # Function: event_generator
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            async with http_client.stream(
                "GET",
                f"{settings.agent_base_url}/incidents/stream",
                headers={**_agent_headers(), "Accept": "text/event-stream"},
                timeout=None,
            ) as resp:
                async for line in resp.aiter_lines():
                    if await request.is_disconnected():
                        break
                    yield f"{line}\n"
        except Exception:  # noqa: BLE001
            logger.exception("incidents.stream_error")
            ts = datetime.now(timezone.utc).isoformat()
            yield f'event: error\ndata: {{"ts": "{ts}", "error": "upstream disconnected"}}\n\n'

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
