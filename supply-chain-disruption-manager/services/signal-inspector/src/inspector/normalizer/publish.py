# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Stage 6: Publish CanonicalEvent to Redis stream and SSE queues.
# Date: 2026-05-16
# ---------------------------------------------------------------------------
"""Stage 6: Publish CanonicalEvent to Redis stream and SSE queues."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import structlog

from inspector.bus.redis_streams import RedisStreamsPublisher
from inspector.envelope import CanonicalEvent

logger = structlog.get_logger(__name__)

# Global registry of active SSE queues (event_id -> asyncio.Queue)
_sse_queues: list[asyncio.Queue[CanonicalEvent]] = []


# Function: register_sse_queue
def register_sse_queue(q: asyncio.Queue[CanonicalEvent]) -> None:
    """Register a queue to receive live CanonicalEvent objects for SSE."""
    _sse_queues.append(q)


# Function: unregister_sse_queue
def unregister_sse_queue(q: asyncio.Queue[CanonicalEvent]) -> None:
    """Remove a queue from the SSE registry."""
    try:
        _sse_queues.remove(q)
    except ValueError:
        pass


# Function: publish_event
async def publish_event(
    publisher: RedisStreamsPublisher,
    event: CanonicalEvent,
    stream_name: str,
) -> str:
    """XADD event to stream. Also fan-out to SSE queues.

    Returns publish status: "ok" | "dlq" | "failed".
    """
    data = json.loads(event.model_dump_json())
    entry_id = await publisher.publish(stream_name, data)

    # Fan-out to live SSE queues
    for q in list(_sse_queues):
        try:
            q.put_nowait(event)
        except asyncio.QueueFull:
            logger.warning("sse.queue_full")
        except Exception:  # noqa: BLE001
            logger.exception("sse.queue_error")

    if entry_id is None:
        return "dlq"

    return "ok"
