# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: GET /events, GET /events/stream, GET /event/{event_id}, POST /event/{event_id}/replay.
# Date: 2026-04-02
# ---------------------------------------------------------------------------
"""GET /events, GET /events/stream, GET /event/{event_id}, POST /event/{event_id}/replay."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, AsyncGenerator

import structlog
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from inspector.normalizer import publish as pub_module
from inspector.store.database import get_session_factory
from inspector.store.event_repo import EventRepo
from inspector.store.models import CanonicalEventModel

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["events"])

SSE_HEARTBEAT_INTERVAL = 15  # seconds


# Function: _model_to_dict
def _model_to_dict(m: CanonicalEventModel) -> dict[str, Any]:
    return {
        "event_id": m.event_id,
        "schema_version": m.schema_version,
        "correlation_id": m.correlation_id,
        "event_type": m.event_type,
        "original_event_type": m.original_event_type,
        "severity": m.severity,
        "source_system": m.source_system,
        "source_event_id": m.source_event_id,
        "ingested_at": m.ingested_at.isoformat() if m.ingested_at else None,
        "source_timestamp": m.source_timestamp.isoformat() if m.source_timestamp else None,
        "root_node_id": m.root_node_id,
        "related_node_ids": m.related_node_ids,
        "payload": m.payload,
        "tags": m.tags,
        "stream_name": m.stream_name,
        "publish_status": m.publish_status,
        "validation_status": m.validation_status,
        "validation_errors": m.validation_errors,
        "replay_count": m.replay_count,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }


# Function: list_events
@router.get("/events")
async def list_events(
    event_type: str | None = Query(None),
    source_system: str | None = Query(None),
    severity: str | None = Query(None),
    publish_status: str | None = Query(None),
    validation_status: str | None = Query(None),
    from_dt: datetime | None = Query(None, alias="from"),
    to_dt: datetime | None = Query(None, alias="to"),
    node_id: str | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
) -> dict[str, Any]:
    """Paginated event list with optional filters."""
    factory = get_session_factory()
    async with factory() as session:
        repo = EventRepo(session)
        records = await repo.list_events(
            event_type=event_type,
            source_system=source_system,
            severity=severity,
            publish_status=publish_status,
            validation_status=validation_status,
            from_dt=from_dt,
            to_dt=to_dt,
            node_id=node_id,
            cursor=cursor,
            limit=limit,
        )

    items = [_model_to_dict(r) for r in records]
    next_cursor = items[-1]["event_id"] if len(items) == limit else None

    return {
        "items": items,
        "count": len(items),
        "limit": limit,
        "next_cursor": next_cursor,
    }


# Function: stream_events
@router.get("/events/stream")
async def stream_events(request: Request) -> StreamingResponse:
    """SSE live tail of canonical events.

    Sends last 50 events on connect, then streams new events.
    Heartbeat every 15 seconds.
    """
    # Fetch recent events for initial burst
    factory = get_session_factory()
    async with factory() as session:
        repo = EventRepo(session)
        recent = await repo.get_recent(limit=50)

    recent_dicts = [_model_to_dict(r) for r in reversed(recent)]

    # Register SSE queue for live events
    queue: asyncio.Queue = asyncio.Queue(maxsize=500)
    pub_module.register_sse_queue(queue)

    # Function: event_generator
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            # Send recent events first
            for item in recent_dicts:
                yield f"event: canonical_event\ndata: {json.dumps(item)}\n\n"

            # Stream live events + heartbeats
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=SSE_HEARTBEAT_INTERVAL)
                    data = json.loads(event.model_dump_json())
                    yield f"event: canonical_event\ndata: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    ts = datetime.now(timezone.utc).isoformat()
                    yield f'event: heartbeat\ndata: {{"ts": "{ts}"}}\n\n'
                except asyncio.CancelledError:
                    break
        finally:
            pub_module.unregister_sse_queue(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# Function: get_event
@router.get("/event/{event_id}")
async def get_event(event_id: str) -> dict[str, Any]:
    """Fetch a single event by ULID event_id."""
    factory = get_session_factory()
    async with factory() as session:
        repo = EventRepo(session)
        record = await repo.get_by_event_id(event_id)

    if not record:
        raise HTTPException(status_code=404, detail="Event not found")

    return _model_to_dict(record)


# Function: get_event_compat
@router.get("/events/{event_id}")
async def get_event_compat(event_id: str) -> dict[str, Any]:
    return await get_event(event_id)


class ReplayRequest(BaseModel):
    target_stream: str | None = None
    replayed_by: str | None = None


# Function: replay_event
@router.post("/event/{event_id}/replay")
async def replay_event(
    event_id: str,
    request: Request,
    body: ReplayRequest | None = None,
) -> dict[str, Any]:
    """Re-publish a stored event to its original (or specified) Redis stream."""
    from inspector.envelope import CanonicalEvent

    factory = get_session_factory()

    # ── Fetch event record ─────────────────────────────────────────────────
    async with factory() as session:
        repo = EventRepo(session)
        record = await repo.get_by_event_id(event_id)

    if not record:
        raise HTTPException(status_code=404, detail="Event not found")

    body = body or ReplayRequest()
    target_stream = body.target_stream or record.stream_name
    if not target_stream:
        raise HTTPException(status_code=400, detail="No stream to replay to")

    publisher = request.app.state.publisher
    pub_status: str

    # ── Re-publish to Redis ────────────────────────────────────────────────
    try:
        canonical = CanonicalEvent(
            event_id=record.event_id,
            schema_version=record.schema_version or 1,
            correlation_id=record.correlation_id,
            event_type=record.event_type,
            severity=record.severity,  # type: ignore[arg-type]
            source_system=record.source_system,
            source_event_id=record.source_event_id,
            ingested_at=record.ingested_at,
            source_timestamp=record.source_timestamp or record.ingested_at,
            root_node_id=record.root_node_id,
            related_node_ids=record.related_node_ids or [],
            payload=record.payload or {},
            tags=record.tags or {},
        )
        pub_status = await pub_module.publish_event(publisher, canonical, target_stream)

        async with factory() as write_session:
            write_repo = EventRepo(write_session)
            await write_repo.increment_replay_count(event_id)
            await write_repo.record_replay(
                event_id=event_id,
                target_stream=target_stream,
                result=pub_status,
                replayed_by=body.replayed_by,
            )
            await write_session.commit()

    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("replay.error", event_id=event_id)
        async with factory() as err_session:
            err_repo = EventRepo(err_session)
            await err_repo.record_replay(
                event_id=event_id,
                target_stream=target_stream,
                result="error",
                error=str(exc),
                replayed_by=body.replayed_by,
            )
            await err_session.commit()
        raise HTTPException(status_code=500, detail=f"Replay failed: {exc}") from exc

    return {
        "event_id": event_id,
        "stream": target_stream,
        "publish_status": pub_status,
    }


# Function: replay_event_compat
@router.post("/events/{event_id}/replay")
async def replay_event_compat(
    event_id: str,
    request: Request,
    body: ReplayRequest | None = None,
) -> dict[str, Any]:
    return await replay_event(event_id, request, body)
