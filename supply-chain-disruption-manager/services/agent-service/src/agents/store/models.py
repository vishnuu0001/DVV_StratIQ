# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SQLAlchemy ORM models for the Agent Service.
# Date: 2026-01-23
# ---------------------------------------------------------------------------
"""SQLAlchemy ORM models for the Agent Service."""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agents.store.database import Base


class IncidentState(str, enum.Enum):
    NEW = "NEW"
    CLASSIFIED = "CLASSIFIED"
    DISPATCHED = "DISPATCHED"
    IN_PROGRESS = "IN_PROGRESS"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"
    BLOCKED = "BLOCKED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


# Valid state transitions
VALID_TRANSITIONS: dict[IncidentState, set[IncidentState]] = {
    IncidentState.NEW: {IncidentState.CLASSIFIED, IncidentState.FAILED},
    IncidentState.CLASSIFIED: {
        IncidentState.DISPATCHED,
        IncidentState.ESCALATED,
        IncidentState.FAILED,
    },
    IncidentState.DISPATCHED: {IncidentState.IN_PROGRESS, IncidentState.FAILED},
    IncidentState.IN_PROGRESS: {
        IncidentState.AWAITING_APPROVAL,
        IncidentState.RESOLVED,
        IncidentState.BLOCKED,
        IncidentState.FAILED,
    },
    IncidentState.AWAITING_APPROVAL: {
        IncidentState.RESOLVED,
        IncidentState.REJECTED,
        IncidentState.FAILED,
    },
    IncidentState.REJECTED: {IncidentState.CLASSIFIED, IncidentState.FAILED},
    IncidentState.RESOLVED: {IncidentState.FAILED},
    IncidentState.ESCALATED: {IncidentState.FAILED},
    IncidentState.BLOCKED: {IncidentState.FAILED},
    IncidentState.FAILED: set(),
}


# Function: validate_transition
def validate_transition(current: IncidentState, target: IncidentState) -> bool:
    """Return True if the transition is valid."""
    return target in VALID_TRANSITIONS.get(current, set())


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    source_event_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    correlation_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    state: Mapped[str] = mapped_column(String(50), nullable=False, default="NEW")
    type: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    root_node_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_node_kind: Mapped[str | None] = mapped_column(Text, nullable=True)
    blast_radius: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    owners: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    plan: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    specialist_runs: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    human_decisions: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    final_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    events: Mapped[list[IncidentEvent]] = relationship(
        "IncidentEvent", back_populates="incident", cascade="all, delete-orphan"
    )
    agent_runs: Mapped[list[AgentRun]] = relationship(
        "AgentRun", back_populates="incident", cascade="all, delete-orphan"
    )
    decisions: Mapped[list[HumanDecision]] = relationship(
        "HumanDecision", back_populates="incident", cascade="all, delete-orphan"
    )


class IncidentEvent(Base):
    __tablename__ = "incident_events"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    incident_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("incidents.id"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    incident: Mapped[Incident] = relationship("Incident", back_populates="events")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    incident_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("incidents.id"), nullable=False, index=True
    )
    agent_name: Mapped[str] = mapped_column(Text, nullable=False)
    agent_role: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    brief: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    actions_taken: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    findings: Mapped[str | None] = mapped_column(Text, nullable=True)
    blockers: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    token_input: Mapped[int | None] = mapped_column(Integer, nullable=True)
    token_output: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_usd: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    incident: Mapped[Incident] = relationship("Incident", back_populates="agent_runs")


class HumanDecision(Base):
    __tablename__ = "human_decisions"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    incident_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("incidents.id"), nullable=False, index=True
    )
    decision: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    incident: Mapped[Incident] = relationship("Incident", back_populates="decisions")


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    topic: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
