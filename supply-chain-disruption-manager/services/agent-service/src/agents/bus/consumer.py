# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Redis Streams consumer — reads disruption events and dispatches orchestrator.
# Date: 2026-04-27
# ---------------------------------------------------------------------------
"""Redis Streams consumer — reads disruption events and dispatches orchestrator."""
from __future__ import annotations

import asyncio
import json
from typing import Any

import redis.asyncio as aioredis
import structlog

from agents.config import get_settings

log = structlog.get_logger(__name__)

CONSUMER_GROUP = "agents-orchestrator"
CONSUMER_NAME = "agent-service-1"

DISRUPTION_STREAMS = [
    "disruption.supplier",
    "disruption.logistics",
    "disruption.warehouse",
    "disruption.quality",
    "disruption.production",
    "disruption.demand",
]

DLQ_STREAM = "disruption.dlq"

MAX_RETRIES = 3
RETRY_DELAYS = [1.0, 2.0, 4.0]  # exponential backoff in seconds
BLOCK_MS = 5000


class StreamConsumer:
    """Consumes disruption events from Redis Streams and calls the Orchestrator."""

    # Function: __init__
    def __init__(self, redis_client: aioredis.Redis) -> None:
        self._redis = redis_client
        self._settings = get_settings()
        self._running = False

    # Function: run
    async def run(self) -> None:
        """Main consumer loop."""
        self._running = True
        await self._ensure_groups()

        log.info("stream_consumer_running", streams=DISRUPTION_STREAMS, group=CONSUMER_GROUP)

        while self._running:
            try:
                await self._poll_once()
            except asyncio.CancelledError:
                log.info("stream_consumer_cancelled")
                break
            except Exception as exc:
                log.error("stream_consumer_error", error=str(exc))
                await asyncio.sleep(1.0)

        self._running = False
        log.info("stream_consumer_stopped")

    # Function: stop
    async def stop(self) -> None:
        self._running = False

    # Function: _ensure_groups
    async def _ensure_groups(self) -> None:
        """Create consumer groups if they don't exist."""
        for stream in DISRUPTION_STREAMS:
            try:
                await self._redis.xgroup_create(stream, CONSUMER_GROUP, id="0", mkstream=True)
                log.info("consumer_group_created", stream=stream, group=CONSUMER_GROUP)
            except aioredis.ResponseError as e:
                if "BUSYGROUP" in str(e):
                    pass  # already exists
                else:
                    log.warning("consumer_group_error", stream=stream, error=str(e))

    # Function: _poll_once
    async def _poll_once(self) -> None:
        """One round of XREADGROUP across all streams."""
        stream_ids = {s: ">" for s in DISRUPTION_STREAMS}
        try:
            results = await self._redis.xreadgroup(
                CONSUMER_GROUP,
                CONSUMER_NAME,
                streams=stream_ids,
                count=10,
                block=BLOCK_MS,
            )
        except asyncio.CancelledError:
            raise
        except (aioredis.TimeoutError, asyncio.TimeoutError):
            # Normal: the BLOCK window expired with no new messages.
            # The outer loop will call _poll_once again immediately.
            return
        except Exception as exc:
            log.warning("xreadgroup_failed", error=str(exc))
            await asyncio.sleep(1.0)
            return

        if not results:
            return

        for stream_name, messages in results:
            for msg_id, fields in messages:
                await self._process_message(stream_name, msg_id, fields)

    # Function: _process_message
    async def _process_message(
        self,
        stream: str,
        msg_id: str,
        fields: dict[str, str],
    ) -> None:
        """Process a single Redis Stream message with retry + DLQ."""
        log.info("message_received", stream=stream, msg_id=msg_id)

        try:
            event = self._parse_fields(fields)
        except Exception as exc:
            log.error("message_parse_failed", stream=stream, msg_id=msg_id, error=str(exc))
            await self._send_to_dlq(stream, msg_id, fields, f"parse_error: {exc}")
            await self._ack(stream, msg_id)
            return

        # Idempotency check
        source_event_id = event.get("source_event_id", "")
        if await self._already_processed(source_event_id):
            log.info("duplicate_event_skipped", source_event_id=source_event_id, msg_id=msg_id)
            await self._ack(stream, msg_id)
            return

        # Retry loop
        last_exc: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                from agents.orchestrator.agent import Orchestrator
                orchestrator = Orchestrator(redis_client=self._redis)
                incident_id = await orchestrator.handle_event(event)
                log.info(
                    "event_processed",
                    stream=stream,
                    msg_id=msg_id,
                    source_event_id=source_event_id,
                    incident_id=incident_id,
                )
                await self._ack(stream, msg_id)
                return
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                last_exc = exc
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAYS[attempt]
                    log.warning(
                        "event_processing_retry",
                        stream=stream,
                        msg_id=msg_id,
                        attempt=attempt + 1,
                        delay=delay,
                        error=str(exc),
                    )
                    await asyncio.sleep(delay)

        # All retries exhausted
        log.error(
            "event_processing_failed",
            stream=stream,
            msg_id=msg_id,
            source_event_id=source_event_id,
            error=str(last_exc),
        )
        await self._send_to_dlq(stream, msg_id, fields, str(last_exc))
        await self._ack(stream, msg_id)

    # Function: _parse_fields
    def _parse_fields(self, fields: dict[str, str]) -> dict:
        """Parse Redis Stream fields into a structured event dict."""
        event: dict[str, Any] = {}
        for k, v in fields.items():
            try:
                event[k] = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                event[k] = v
        return event

    # Function: _already_processed
    async def _already_processed(self, source_event_id: str) -> bool:
        """Check if we already created an incident for this source_event_id."""
        if not source_event_id:
            return False
        try:
            from agents.store.database import get_session
            from agents.store.incident_repo import get_repo
            async with get_session() as session:
                repo = get_repo(session)
                existing = await repo.get_by_source_event(source_event_id)
                return existing is not None
        except Exception as exc:
            log.warning("idempotency_check_failed", error=str(exc))
            return False

    # Function: _ack
    async def _ack(self, stream: str, msg_id: str) -> None:
        try:
            await self._redis.xack(stream, CONSUMER_GROUP, msg_id)
        except Exception as exc:
            log.warning("xack_failed", stream=stream, msg_id=msg_id, error=str(exc))

    # Function: _send_to_dlq
    async def _send_to_dlq(
        self,
        original_stream: str,
        msg_id: str,
        fields: dict,
        error: str,
    ) -> None:
        try:
            await self._redis.xadd(
                DLQ_STREAM,
                {
                    "original_stream": original_stream,
                    "original_msg_id": msg_id,
                    "error": error,
                    "fields": json.dumps(fields),
                    "failed_at": "2026-06-27T00:00:00Z",
                },
            )
            log.info("sent_to_dlq", original_stream=original_stream, msg_id=msg_id)
        except Exception as exc:
            log.error("dlq_send_failed", error=str(exc))
