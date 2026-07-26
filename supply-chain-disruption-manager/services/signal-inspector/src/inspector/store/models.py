# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SQLAlchemy ORM models for the signal-inspector service.
# Date: 2026-04-15
# ---------------------------------------------------------------------------
"""SQLAlchemy ORM models for the signal-inspector service."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


# Function: _utcnow
def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CanonicalEventModel(Base):
    """Persisted CanonicalEvent record."""

    __tablename__ = "canonical_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    event_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    schema_version: Mapped[int] = mapped_column(Integer, default=1)
    correlation_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_type: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    original_event_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    source_system: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    source_event_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    source_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    root_node_id: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)
    related_node_ids: Mapped[dict] = mapped_column(JSONB, default=list, server_default="[]")
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    tags: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    stream_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    publish_status: Mapped[str | None] = mapped_column(Text, nullable=True)
    validation_status: Mapped[str | None] = mapped_column(Text, nullable=True)
    validation_errors: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    replay_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
        server_default=func.now(),
    )


class EventReplayModel(Base):
    """Audit record for event replay actions."""

    __tablename__ = "event_replays"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    event_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    replayed_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    replayed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        server_default=func.now(),
    )
    target_stream: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)


class AdapterHealthSnapshotModel(Base):
    """Point-in-time health snapshot for an adapter."""

    __tablename__ = "adapter_health_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    adapter_name: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    last_event_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    events_last_5m: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_rate_5m: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        server_default=func.now(),
    )
