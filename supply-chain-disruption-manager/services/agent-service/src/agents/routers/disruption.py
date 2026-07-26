# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: POST /disruption — manual incident trigger endpoint.
# Date: 2025-08-16
# ---------------------------------------------------------------------------
"""POST /disruption — manual incident trigger endpoint."""
from __future__ import annotations

import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from agents.auth import require_api_key

router = APIRouter(tags=["disruption"])


class DisruptionRequest(BaseModel):
    source_event_id: str = Field(..., description="Unique event ID from source system")
    type: str | None = Field(None, description="Pre-classified disruption type (optional)")
    event_type: str | None = Field(None, description="Raw event type (e.g. supplier.po.delayed)")
    root_node_id: str | None = None
    root_node_kind: str | None = None
    correlation_id: str | None = None
    payload: dict = Field(default_factory=dict)


# Function: _run_orchestrator
async def _run_orchestrator(event: dict, redis_client) -> str:
    """Background function that runs the orchestrator pipeline."""
    from agents.orchestrator.agent import Orchestrator
    orchestrator = Orchestrator(redis_client=redis_client)
    return await orchestrator.handle_event(event)


# Function: trigger_disruption
@router.post(
    "/disruption",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_api_key)],
)
async def trigger_disruption(
    body: DisruptionRequest,
    background_tasks: BackgroundTasks,
    request: Request,
) -> dict:
    """
    Manually trigger a disruption incident.
    The orchestrator runs asynchronously — returns 202 with incident_id immediately.
    """
    event = {
        "source_event_id": body.source_event_id,
        "event_type": body.event_type or body.type,
        "disruption_type": body.type,
        "root_node_id": body.root_node_id,
        "root_node_kind": body.root_node_kind,
        "correlation_id": body.correlation_id,
        "payload": body.payload,
        "source_system": "manual_trigger",
    }

    redis_client = getattr(request.app.state, "redis", None)

    # Run orchestrator synchronously to get the incident_id
    try:
        from agents.orchestrator.agent import Orchestrator
        orchestrator = Orchestrator(redis_client=redis_client)
        incident_id = await orchestrator.handle_event(event)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Orchestration failed: {exc}",
        )

    return {"incident_id": incident_id, "status": "accepted"}
