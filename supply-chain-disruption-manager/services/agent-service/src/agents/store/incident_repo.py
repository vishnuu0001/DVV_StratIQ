# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Repository for incident CRUD operations with audit trail.
# Date: 2025-08-29
# ---------------------------------------------------------------------------
"""Repository for incident CRUD operations with audit trail."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from agents.store.database import get_session
from agents.store.models import (
    AgentRun,
    HumanDecision,
    Incident,
    IncidentEvent,
    IncidentState,
    OutboxEvent,
    validate_transition,
)

log = structlog.get_logger(__name__)


class InvalidTransitionError(Exception):
    """Raised when a state transition is not allowed."""

    # Function: __init__
    def __init__(self, current: str, target: str) -> None:
        super().__init__(f"Transition {current} -> {target} is not valid")
        self.current = current
        self.target = target


class IncidentRepo:
    """All incident persistence operations."""

    # Function: __init__
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------------ #
    # Create                                                               #
    # ------------------------------------------------------------------ #

    # Function: create
    async def create(
        self,
        source_event_id: str,
        correlation_id: str | None = None,
        root_node_id: str | None = None,
        root_node_kind: str | None = None,
        incident_type: str | None = None,
        severity: str | None = None,
    ) -> Incident:
        incident = Incident(
            id=str(uuid.uuid4()),
            source_event_id=source_event_id,
            correlation_id=correlation_id,
            state=IncidentState.NEW.value,
            root_node_id=root_node_id,
            root_node_kind=root_node_kind,
            type=incident_type,
            severity=severity,
            specialist_runs=[],
            human_decisions=[],
        )
        self._session.add(incident)
        await self._session.flush()
        await self._write_event(incident.id, "incident.created", {"state": incident.state})
        log.info("incident_created", incident_id=incident.id, source_event_id=source_event_id)
        return incident

    # ------------------------------------------------------------------ #
    # Read                                                                 #
    # ------------------------------------------------------------------ #

    # Function: get
    async def get(self, incident_id: str) -> Incident | None:
        result = await self._session.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        return result.scalar_one_or_none()

    # Function: get_by_source_event
    async def get_by_source_event(self, source_event_id: str) -> Incident | None:
        result = await self._session.execute(
            select(Incident).where(Incident.source_event_id == source_event_id)
        )
        return result.scalar_one_or_none()

    # Function: list_incidents
    async def list_incidents(
        self,
        state: str | None = None,
        severity: str | None = None,
        incident_type: str | None = None,
        limit: int = 50,
        cursor: str | None = None,
    ) -> list[Incident]:
        """List incidents with cursor pagination (created_at + id)."""
        stmt = select(Incident).order_by(Incident.created_at.desc(), Incident.id.desc())

        if state:
            stmt = stmt.where(Incident.state == state)
        if severity:
            stmt = stmt.where(Incident.severity == severity)
        if incident_type:
            stmt = stmt.where(Incident.type == incident_type)

        if cursor:
            # cursor is "created_at_iso|id"
            try:
                ts_str, cid = cursor.split("|", 1)
                cursor_dt = datetime.fromisoformat(ts_str)
                from sqlalchemy import or_, and_
                stmt = stmt.where(
                    or_(
                        Incident.created_at < cursor_dt,
                        and_(Incident.created_at == cursor_dt, Incident.id < cid),
                    )
                )
            except (ValueError, AttributeError):
                pass

        stmt = stmt.limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # Function: get_timeline
    async def get_timeline(self, incident_id: str) -> list[IncidentEvent]:
        result = await self._session.execute(
            select(IncidentEvent)
            .where(IncidentEvent.incident_id == incident_id)
            .order_by(IncidentEvent.created_at.asc())
        )
        return list(result.scalars().all())

    # Function: get_agent_runs
    async def get_agent_runs(self, incident_id: str) -> list[AgentRun]:
        result = await self._session.execute(
            select(AgentRun).where(AgentRun.incident_id == incident_id)
        )
        return list(result.scalars().all())

    # ------------------------------------------------------------------ #
    # State machine                                                        #
    # ------------------------------------------------------------------ #

    # Function: transition
    async def transition(
        self,
        incident_id: str,
        target_state: IncidentState,
        payload: dict | None = None,
        updates: dict | None = None,
    ) -> Incident:
        """Transition incident to a new state (validates transition)."""
        incident = await self.get(incident_id)
        if incident is None:
            raise ValueError(f"Incident {incident_id} not found")

        current = IncidentState(incident.state)
        if not validate_transition(current, target_state):
            raise InvalidTransitionError(incident.state, target_state.value)

        incident.state = target_state.value
        incident.updated_at = datetime.now(timezone.utc)

        if target_state == IncidentState.RESOLVED:
            incident.resolved_at = datetime.now(timezone.utc)

        if updates:
            for k, v in updates.items():
                setattr(incident, k, v)

        await self._session.flush()

        event_payload = {"from_state": current.value, "to_state": target_state.value}
        if payload:
            event_payload.update(payload)
        await self._write_event(incident_id, "incident.state_changed", event_payload)

        log.info(
            "incident_transitioned",
            incident_id=incident_id,
            from_state=current.value,
            to_state=target_state.value,
        )
        return incident

    # ------------------------------------------------------------------ #
    # Updates                                                              #
    # ------------------------------------------------------------------ #

    # Function: update_classification
    async def update_classification(
        self,
        incident_id: str,
        incident_type: str,
        severity: str,
        confidence: float,
    ) -> None:
        await self._session.execute(
            update(Incident)
            .where(Incident.id == incident_id)
            .values(
                type=incident_type,
                severity=severity,
                confidence=confidence,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self._session.flush()
        await self._write_event(
            incident_id,
            "incident.classified",
            {"type": incident_type, "severity": severity, "confidence": confidence},
        )

    # Function: update_blast_radius
    async def update_blast_radius(
        self, incident_id: str, blast_radius: dict, owners: list
    ) -> None:
        await self._session.execute(
            update(Incident)
            .where(Incident.id == incident_id)
            .values(
                blast_radius=blast_radius,
                owners=owners,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self._session.flush()

    # Function: update_plan
    async def update_plan(self, incident_id: str, plan: dict) -> None:
        await self._session.execute(
            update(Incident)
            .where(Incident.id == incident_id)
            .values(plan=plan, updated_at=datetime.now(timezone.utc))
        )
        await self._session.flush()
        await self._write_event(incident_id, "incident.plan_composed", {"plan": plan})

    # Function: update_final_summary
    async def update_final_summary(
        self, incident_id: str, summary: str, specialist_runs: list
    ) -> None:
        await self._session.execute(
            update(Incident)
            .where(Incident.id == incident_id)
            .values(
                final_summary=summary,
                specialist_runs=specialist_runs,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self._session.flush()

    # ------------------------------------------------------------------ #
    # Agent runs                                                           #
    # ------------------------------------------------------------------ #

    # Function: create_agent_run
    async def create_agent_run(
        self,
        incident_id: str,
        agent_name: str,
        agent_role: str,
        brief: dict,
    ) -> AgentRun:
        run = AgentRun(
            id=str(uuid.uuid4()),
            incident_id=incident_id,
            agent_name=agent_name,
            agent_role=agent_role,
            status="running",
            brief=brief,
            started_at=datetime.now(timezone.utc),
        )
        self._session.add(run)
        await self._session.flush()
        await self._write_event(
            incident_id,
            "agent.dispatched",
            {"agent_name": agent_name, "role": agent_role, "run_id": run.id},
        )
        return run

    # Function: complete_agent_run
    async def complete_agent_run(
        self,
        run_id: str,
        incident_id: str,
        status: str,
        actions_taken: list,
        findings: str,
        blockers: list,
        recommendation: str,
        confidence: float,
        duration_ms: int,
        token_input: int = 0,
        token_output: int = 0,
        cost_usd: float = 0.0,
    ) -> None:
        await self._session.execute(
            update(AgentRun)
            .where(AgentRun.id == run_id)
            .values(
                status=status,
                actions_taken=actions_taken,
                findings=findings,
                blockers=blockers,
                recommendation=recommendation,
                confidence=confidence,
                duration_ms=duration_ms,
                token_input=token_input,
                token_output=token_output,
                cost_usd=cost_usd,
                completed_at=datetime.now(timezone.utc),
            )
        )
        await self._session.flush()
        await self._write_event(
            incident_id,
            "agent.completed",
            {
                "run_id": run_id,
                "status": status,
                "confidence": confidence,
                "duration_ms": duration_ms,
            },
        )

    # ------------------------------------------------------------------ #
    # Human decisions                                                      #
    # ------------------------------------------------------------------ #

    # Function: record_decision
    async def record_decision(
        self,
        incident_id: str,
        decision: str,
        reason: str | None,
        decided_by: str | None,
        payload: dict | None = None,
    ) -> HumanDecision:
        hd = HumanDecision(
            id=str(uuid.uuid4()),
            incident_id=incident_id,
            decision=decision,
            reason=reason,
            decided_by=decided_by,
            decided_at=datetime.now(timezone.utc),
            payload=payload,
        )
        self._session.add(hd)
        await self._session.flush()

        # Also update the incident's human_decisions JSONB array
        incident = await self.get(incident_id)
        if incident:
            existing = list(incident.human_decisions or [])
            existing.append(
                {
                    "id": hd.id,
                    "decision": decision,
                    "reason": reason,
                    "decided_by": decided_by,
                    "decided_at": hd.decided_at.isoformat(),
                }
            )
            await self._session.execute(
                update(Incident)
                .where(Incident.id == incident_id)
                .values(human_decisions=existing, updated_at=datetime.now(timezone.utc))
            )
            await self._session.flush()

        await self._write_event(
            incident_id,
            f"human.{decision.lower()}",
            {"decision": decision, "reason": reason, "decided_by": decided_by},
        )
        return hd

    # ------------------------------------------------------------------ #
    # Outbox                                                               #
    # ------------------------------------------------------------------ #

    # Function: write_outbox
    async def write_outbox(self, topic: str, payload: dict) -> None:
        evt = OutboxEvent(
            id=str(uuid.uuid4()),
            topic=topic,
            payload=payload,
            status="pending",
        )
        self._session.add(evt)
        await self._session.flush()

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    # Function: _write_event
    async def _write_event(
        self, incident_id: str, event_type: str, payload: dict | None = None
    ) -> None:
        evt = IncidentEvent(
            id=str(uuid.uuid4()),
            incident_id=incident_id,
            event_type=event_type,
            payload=payload or {},
        )
        self._session.add(evt)
        await self._session.flush()


# Function: get_repo
def get_repo(session: AsyncSession) -> IncidentRepo:
    return IncidentRepo(session)
