# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Redis Streams publisher with retry and DLQ support.
# Date: 2025-08-01
# ---------------------------------------------------------------------------
"""Redis Streams publisher with retry and DLQ support."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

import structlog
from redis.asyncio import Redis

logger = structlog.get_logger(__name__)

# All known streams
DOMAIN_STREAMS = [
    "supplier",
    "logistics",
    "warehouse",
    "production",
    "demand",
    "disruption.supplier",
    "disruption.logistics",
    "disruption.warehouse",
    "disruption.quality",
    "disruption.production",
    "disruption.demand",
]

SYSTEM_STREAMS = [
    "events.invalid",
    "events.dlq",
    "incident.created",
    "incident.updated",
    "incident.resolved",
]

ALL_STREAMS = DOMAIN_STREAMS + SYSTEM_STREAMS

STREAM_MAXLEN = 100_000


class RedisStreamsPublisher:
    """Async Redis Streams publisher used by the normalizer pipeline."""

    # Function: __init__
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    # Function: publish
    async def publish(
        self,
        stream: str,
        data: dict[str, Any],
        max_retries: int = 3,
    ) -> str | None:
        """XADD data to stream. Retries up to max_retries with exponential backoff.
        On persistent failure, writes to events.dlq and returns None.
        Returns the Redis stream entry ID on success.
        """
        # Redis XADD requires flat string values
        flat = _flatten(data)
        last_exc: Exception | None = None

        for attempt in range(max_retries):
            try:
                entry_id = await self._redis.xadd(
                    stream,
                    flat,
                    maxlen=STREAM_MAXLEN,
                    approximate=True,
                )
                logger.debug(
                    "stream.published",
                    stream=stream,
                    entry_id=entry_id,
                    attempt=attempt,
                )
                return entry_id  # type: ignore[return-value]
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                wait = 0.1 * (2**attempt)
                logger.warning(
                    "stream.publish_failed",
                    stream=stream,
                    attempt=attempt,
                    error=str(exc),
                    retry_in=wait,
                )
                await asyncio.sleep(wait)

        # All retries exhausted — write to DLQ
        logger.error(
            "stream.dlq",
            stream=stream,
            error=str(last_exc),
        )
        try:
            dlq_payload = {
                **flat,
                "_dlq_original_stream": stream,
                "_dlq_error": str(last_exc),
                "_dlq_at": datetime.now(timezone.utc).isoformat(),
            }
            await self._redis.xadd(
                "events.dlq",
                dlq_payload,
                maxlen=STREAM_MAXLEN,
                approximate=True,
            )
        except Exception:  # noqa: BLE001
            logger.exception("stream.dlq_write_failed")

        return None

    # Function: publish_invalid
    async def publish_invalid(self, data: dict[str, Any], errors: list[str]) -> None:
        """Publish an invalid event to events.invalid stream."""
        payload = {
            **data,
            "_validation_errors": json.dumps(errors),
        }
        await self.publish("events.invalid", payload)

    # Function: ping
    async def ping(self) -> bool:
        """Return True if Redis is reachable."""
        try:
            return await self._redis.ping()  # type: ignore[return-value]
        except Exception:  # noqa: BLE001
            return False


# Function: _flatten
def _flatten(data: dict[str, Any], prefix: str = "") -> dict[str, str]:
    """Recursively flatten a dict to string key-value pairs for Redis."""
    result: dict[str, str] = {}
    for k, v in data.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            result.update(_flatten(v, key))
        elif isinstance(v, (list, tuple)):
            result[key] = json.dumps(v)
        elif isinstance(v, datetime):
            result[key] = v.isoformat()
        elif v is None:
            result[key] = ""
        else:
            result[key] = str(v)
    return result
