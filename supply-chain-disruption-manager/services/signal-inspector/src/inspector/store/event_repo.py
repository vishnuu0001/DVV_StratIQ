# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Event repository — persists and queries CanonicalEvents in Postgres.
# Date: 2026-01-13
# ---------------------------------------------------------------------------
"""Event repository — persists and queries CanonicalEvents in Postgres."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import structlog
from sqlalchemy import desc, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from inspector.envelope import CanonicalEvent
from inspector.store.models import CanonicalEventModel, EventReplayModel

logger = structlog.get_logger(__name__)


class EventRepo:
    """Data access object for canonical_events table."""

    # Function: __init__
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # Function: save
    async def save(
        self,
        event: CanonicalEvent,
        stream_name: str | None = None,
        publish_status: str | None = None,
        validation_status: str | None = None,
        validation_errors: list[str] | None = None,
    ) -> CanonicalEventModel:
        """Upsert a CanonicalEvent record."""
        original_event_type = event.payload.get("_original_type")

        record = CanonicalEventModel(
            id=uuid.uuid4(),
            event_id=event.event_id,
            schema_version=event.schema_version,
            correlation_id=event.correlation_id,
            event_type=event.event_type,
            original_event_type=original_event_type,
            severity=event.severity,
            source_system=event.source_system,
            source_event_id=event.source_event_id,
            ingested_at=event.ingested_at,
            source_timestamp=event.source_timestamp,
            root_node_id=event.root_node_id,
            related_node_ids=event.related_node_ids,
            payload=event.payload,
            tags=event.tags,
            stream_name=stream_name,
            publish_status=publish_status,
            validation_status=validation_status,
            validation_errors=validation_errors or [],
        )
        self._session.add(record)
        await self._session.flush()
        return record

    # Function: get_by_event_id
    async def get_by_event_id(self, event_id: str) -> CanonicalEventModel | None:
        """Fetch a single event by its ULID event_id."""
        result = await self._session.execute(
            select(CanonicalEventModel).where(CanonicalEventModel.event_id == event_id)
        )
        return result.scalar_one_or_none()

    # Function: list_events
    async def list_events(
        self,
        event_type: str | None = None,
        source_system: str | None = None,
        severity: str | None = None,
        publish_status: str | None = None,
        validation_status: str | None = None,
        from_dt: datetime | None = None,
        to_dt: datetime | None = None,
        node_id: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> list[CanonicalEventModel]:
        """Paginated event list with optional filters.

        cursor is a ULID event_id — returns records with event_id < cursor
        (chronological descending).
        """
        stmt = select(CanonicalEventModel)

        if event_type:
            stmt = stmt.where(CanonicalEventModel.event_type == event_type)
        if source_system:
            stmt = stmt.where(CanonicalEventModel.source_system == source_system)
        if severity:
            stmt = stmt.where(CanonicalEventModel.severity == severity)
        if publish_status:
            stmt = stmt.where(CanonicalEventModel.publish_status == publish_status)
        if validation_status:
            stmt = stmt.where(CanonicalEventModel.validation_status == validation_status)
        if from_dt:
            stmt = stmt.where(CanonicalEventModel.ingested_at >= from_dt)
        if to_dt:
            stmt = stmt.where(CanonicalEventModel.ingested_at <= to_dt)
        if node_id:
            stmt = stmt.where(CanonicalEventModel.root_node_id == node_id)
        if cursor:
            stmt = stmt.where(CanonicalEventModel.event_id < cursor)

        stmt = stmt.order_by(desc(CanonicalEventModel.event_id)).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # Function: get_recent
    async def get_recent(self, limit: int = 50) -> list[CanonicalEventModel]:
        """Return the most recent events ordered by event_id descending."""
        result = await self._session.execute(
            select(CanonicalEventModel)
            .order_by(desc(CanonicalEventModel.event_id))
            .limit(limit)
        )
        return list(result.scalars().all())

    # Function: increment_replay_count
    async def increment_replay_count(self, event_id: str) -> None:
        """Atomically increment replay_count for an event."""
        await self._session.execute(
            text(
                "UPDATE canonical_events SET replay_count = replay_count + 1, "
                "updated_at = now() WHERE event_id = :eid"
            ),
            {"eid": event_id},
        )

    # Function: record_replay
    async def record_replay(
        self,
        event_id: str,
        target_stream: str,
        result: str,
        error: str | None = None,
        replayed_by: str | None = None,
    ) -> EventReplayModel:
        """Save a replay audit record."""
        replay = EventReplayModel(
            id=uuid.uuid4(),
            event_id=event_id,
            replayed_by=replayed_by,
            target_stream=target_stream,
            result=result,
            error=error,
        )
        self._session.add(replay)
        await self._session.flush()
        return replay
