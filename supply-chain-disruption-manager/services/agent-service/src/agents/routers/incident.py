# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Incident management endpoints + SSE stream.
# Date: 2026-04-26
# ---------------------------------------------------------------------------
"""Incident management endpoints + SSE stream."""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from agents.auth import require_api_key
from agents.store.database import get_session
from agents.store.incident_repo import get_repo, InvalidTransitionError
from agents.store.models import IncidentState

router = APIRouter(tags=["incidents"])


# ------------------------------------------------------------------ #
# SSE broadcaster — simple asyncio.Queue fan-out                       #
# ------------------------------------------------------------------ #

class SSEBroadcaster:
    """Fan-out broadcaster for SSE consumers."""

    # Function: __init__
    def __init__(self) -> None:
        self._queues: list[asyncio.Queue] = []
        self.redis = None  # injected at startup

    # Function: subscribe
    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._queues.append(q)
        return q

    # Function: unsubscribe
    def unsubscribe(self, q: asyncio.Queue) -> None:
        try:
            self._queues.remove(q)
        except ValueError:
            pass

    # Function: publish
    async def publish(self, event_type: str, data: dict) -> None:
        payload = {"event": event_type, "data": data}
        dead = []
        for q in self._queues:
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                dead.append(q)
        for q in dead:
            self.unsubscribe(q)


sse_broadcaster = SSEBroadcaster()


# Function: _serialize_incident
def _serialize_incident(incident) -> dict:
    return {
        "incident_id": incident.id,
        "state": incident.state,
        "type": incident.type,
        "severity": incident.severity,
        "confidence": float(incident.confidence) if incident.confidence else None,
        "root_node_id": incident.root_node_id,
        "source_event_id": incident.source_event_id,
        "blast_radius_node_count": len((incident.blast_radius or {}).get("nodes", [])),
        "owners": incident.owners,
        "plan": incident.plan,
        "specialist_runs": incident.specialist_runs,
        "human_decisions": incident.human_decisions,
        "final_summary": incident.final_summary,
        "created_at": incident.created_at.isoformat() if incident.created_at else None,
        "updated_at": incident.updated_at.isoformat() if incident.updated_at else None,
        "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None,
    }


# ------------------------------------------------------------------ #
# GET /incidents                                                        #
# ------------------------------------------------------------------ #

# Function: list_incidents
@router.get("/incidents", dependencies=[Depends(require_api_key)])
async def list_incidents(
    state: str | None = Query(None),
    severity: str | None = Query(None),
    type: str | None = Query(None, alias="type"),
    limit: int = Query(50, ge=1, le=200),
    cursor: str | None = Query(None),
) -> dict:
    async with get_session() as session:
        repo = get_repo(session)
        incidents = await repo.list_incidents(
            state=state,
            severity=severity,
            incident_type=type,
            limit=limit,
            cursor=cursor,
        )

    items = [_serialize_incident(i) for i in incidents]

    next_cursor = None
    if len(items) == limit and items:
        last = incidents[-1]
        if last.created_at:
            next_cursor = f"{last.created_at.isoformat()}|{last.id}"

    return {"items": items, "count": len(items), "next_cursor": next_cursor}


# ------------------------------------------------------------------ #
# GET /incident/{id}                                                   #
# ------------------------------------------------------------------ #

# Function: get_incident
@router.get("/incident/{incident_id}", dependencies=[Depends(require_api_key)])
async def get_incident(incident_id: str) -> dict:
    async with get_session() as session:
        repo = get_repo(session)
        incident = await repo.get(incident_id)
        if incident is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        runs = await repo.get_agent_runs(incident_id)

    result = _serialize_incident(incident)
    result["agent_runs"] = [
        {
            "id": r.id,
            "agent_name": r.agent_name,
            "agent_role": r.agent_role,
            "status": r.status,
            "findings": r.findings,
            "recommendation": r.recommendation,
            "confidence": float(r.confidence) if r.confidence else None,
            "duration_ms": r.duration_ms,
            "blockers": r.blockers,
            "token_input": r.token_input,
            "token_output": r.token_output,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
        }
        for r in runs
    ]
    return result


# ------------------------------------------------------------------ #
# GET /incident/{id}/timeline                                          #
# ------------------------------------------------------------------ #

# Function: get_incident_timeline
@router.get("/incident/{incident_id}/timeline", dependencies=[Depends(require_api_key)])
async def get_incident_timeline(incident_id: str) -> dict:
    async with get_session() as session:
        repo = get_repo(session)
        incident = await repo.get(incident_id)
        if incident is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        events = await repo.get_timeline(incident_id)

    return {
        "incident_id": incident_id,
        "events": [
            {
                "id": e.id,
                "event_type": e.event_type,
                "payload": e.payload,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in events
        ],
    }


# Function: get_incident_timeline_compat
@router.get("/incidents/{incident_id}/timeline", dependencies=[Depends(require_api_key)])
async def get_incident_timeline_compat(incident_id: str) -> dict:
    return await get_incident_timeline(incident_id)


# ------------------------------------------------------------------ #
# POST /incident/{id}/approve                                          #
# ------------------------------------------------------------------ #

class DecisionBody(BaseModel):
    reason: str | None = None
    decided_by: str | None = None


# Function: approve_incident
@router.post("/incident/{incident_id}/approve", dependencies=[Depends(require_api_key)])
async def approve_incident(
    incident_id: str,
    body: DecisionBody,
    request: Request,
) -> dict:
    async with get_session() as session:
        repo = get_repo(session)
        incident = await repo.get(incident_id)
        if incident is None:
            raise HTTPException(status_code=404, detail="Incident not found")

        if incident.state != IncidentState.AWAITING_APPROVAL.value:
            raise HTTPException(
                status_code=400,
                detail=f"Incident is in state {incident.state}, not AWAITING_APPROVAL",
            )

        try:
            await repo.record_decision(
                incident_id,
                "approved",
                body.reason,
                body.decided_by,
            )
            await repo.transition(
                incident_id,
                IncidentState.RESOLVED,
                payload={"reason": body.reason, "decided_by": body.decided_by},
            )
        except InvalidTransitionError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    # Broadcast SSE
    await sse_broadcaster.publish(
        "incident_state",
        {
            "incident_id": incident_id,
            "state": "RESOLVED",
            "decided_by": body.decided_by,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    # Redis emit
    redis_client = getattr(request.app.state, "redis", None)
    if redis_client:
        try:
            await redis_client.xadd(
                "incident.resolved",
                {"incident_id": incident_id, "state": "RESOLVED", "decision": "approved"},
            )
        except Exception:
            pass

    return {"incident_id": incident_id, "state": "RESOLVED", "decision": "approved"}


# Function: approve_incident_compat
@router.post("/incidents/{incident_id}/approve", dependencies=[Depends(require_api_key)])
async def approve_incident_compat(
    incident_id: str,
    body: DecisionBody,
    request: Request,
) -> dict:
    return await approve_incident(incident_id, body, request)


# ------------------------------------------------------------------ #
# POST /incident/{id}/reject                                           #
# ------------------------------------------------------------------ #

# Function: reject_incident
@router.post("/incident/{incident_id}/reject", dependencies=[Depends(require_api_key)])
async def reject_incident(
    incident_id: str,
    body: DecisionBody,
    request: Request,
) -> dict:
    async with get_session() as session:
        repo = get_repo(session)
        incident = await repo.get(incident_id)
        if incident is None:
            raise HTTPException(status_code=404, detail="Incident not found")

        if incident.state != IncidentState.AWAITING_APPROVAL.value:
            raise HTTPException(
                status_code=400,
                detail=f"Incident is in state {incident.state}, not AWAITING_APPROVAL",
            )

        try:
            await repo.record_decision(
                incident_id,
                "rejected",
                body.reason,
                body.decided_by,
            )
            await repo.transition(
                incident_id,
                IncidentState.REJECTED,
                payload={"reason": body.reason, "decided_by": body.decided_by},
            )
        except InvalidTransitionError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    # Broadcast SSE
    await sse_broadcaster.publish(
        "incident_state",
        {
            "incident_id": incident_id,
            "state": "REJECTED",
            "decided_by": body.decided_by,
            "rejection_reason": body.reason,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    # Re-trigger orchestrator planning with rejection context
    redis_client = getattr(request.app.state, "redis", None)
    try:
        from agents.orchestrator.agent import Orchestrator
        orch = Orchestrator(redis_client=redis_client)
        await orch.replan_after_rejection(incident_id, body.reason or "No reason provided")
    except Exception:
        pass

    return {"incident_id": incident_id, "state": "REJECTED", "decision": "rejected"}


# Function: reject_incident_compat
@router.post("/incidents/{incident_id}/reject", dependencies=[Depends(require_api_key)])
async def reject_incident_compat(
    incident_id: str,
    body: DecisionBody,
    request: Request,
) -> dict:
    return await reject_incident(incident_id, body, request)


# ------------------------------------------------------------------ #
# GET /incidents/stream  (SSE)                                         #
# ------------------------------------------------------------------ #

# Function: incidents_stream
@router.get("/incidents/stream", dependencies=[Depends(require_api_key)])
async def incidents_stream(request: Request) -> EventSourceResponse:
    """SSE stream of incident state changes."""

    # Function: event_generator
    async def event_generator() -> AsyncGenerator[dict, None]:
        # Send last 10 incidents on connect
        try:
            async with get_session() as session:
                repo = get_repo(session)
                recent = await repo.list_incidents(limit=10)
            for incident in reversed(recent):
                yield {
                    "event": "incident_state",
                    "data": json.dumps({
                        "incident_id": incident.id,
                        "state": incident.state,
                        "type": incident.type,
                        "severity": incident.severity,
                        "updated_at": incident.updated_at.isoformat() if incident.updated_at else None,
                    }),
                }
        except Exception:
            pass

        # Subscribe to broadcast queue
        queue = sse_broadcaster.subscribe()
        heartbeat_interval = 15.0
        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=heartbeat_interval)
                    yield {
                        "event": payload["event"],
                        "data": json.dumps(payload["data"]),
                    }
                except asyncio.TimeoutError:
                    # Send heartbeat
                    yield {
                        "event": "heartbeat",
                        "data": json.dumps({"ts": datetime.now(timezone.utc).isoformat()}),
                    }
        finally:
            sse_broadcaster.unsubscribe(queue)

    return EventSourceResponse(event_generator())
