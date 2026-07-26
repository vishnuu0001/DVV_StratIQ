# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Orchestrator agent — the main pipeline coordinator.
# Date: 2026-06-28
# ---------------------------------------------------------------------------
"""Orchestrator agent — the main pipeline coordinator."""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import redis.asyncio as aioredis
import structlog

from agents.config import get_settings
from agents.kg.client import get_kg_client
from agents.orchestrator.classifier import Classifier
from agents.orchestrator.planner import Planner
from agents.specialists.buyer import BuyerSpecialist
from agents.specialists.inventory import InventorySpecialist
from agents.specialists.logistics import LogisticsSpecialist
from agents.specialists.planning import PlanningSpecialist
from agents.specialists.quality import QualitySpecialist
from agents.specialists.shopfloor import ShopfloorSpecialist
from agents.specialists.warehouse import WarehouseSpecialist
from agents.store.database import get_session
from agents.store.incident_repo import IncidentRepo, get_repo
from agents.store.models import IncidentState

if TYPE_CHECKING:
    from agents.specialists.base import BaseSpecialist, SpecialistResponse

log = structlog.get_logger(__name__)

SPECIALIST_REGISTRY: dict[str, type] = {
    "buyer": BuyerSpecialist,
    "logistics": LogisticsSpecialist,
    "warehouse": WarehouseSpecialist,
    "quality": QualitySpecialist,
    "inventory": InventorySpecialist,
    "planning": PlanningSpecialist,
    "shopfloor": ShopfloorSpecialist,
}


# Function: _run_specialist
async def _run_specialist(role: str, run_id: str, brief: dict) -> tuple[str, str, "SpecialistResponse"]:
    cls = SPECIALIST_REGISTRY.get(role)
    if cls is None:
        log.warning("unknown_specialist_role", role=role)
        return role, run_id, None  # type: ignore
    specialist = cls()
    resp = await specialist.run(brief)
    return role, run_id, resp


class Orchestrator:
    """Processes disruption events end-to-end."""

    # Function: __init__
    def __init__(self, redis_client: aioredis.Redis | None = None) -> None:
        self._redis = redis_client
        self._settings = get_settings()
        self._classifier = Classifier()
        self._planner = Planner()
        self._kg = get_kg_client()

    # Function: handle_event
    async def handle_event(self, event: dict) -> str:
        """
        Process a disruption event, create incident, run full pipeline.
        Returns incident_id.
        """
        source_event_id = event.get("source_event_id", "")
        correlation_id = event.get("correlation_id")
        root_node_id = event.get("root_node_id") or event.get("payload", {}).get(
            "supplier_id"
        ) or event.get("payload", {}).get("shipment_id")
        root_node_kind = event.get("root_node_kind")

        async with get_session() as session:
            repo = get_repo(session)

            # 1. Create incident in NEW state
            incident = await repo.create(
                source_event_id=source_event_id,
                correlation_id=correlation_id,
                root_node_id=root_node_id,
                root_node_kind=root_node_kind,
            )
            incident_id = incident.id
            log.info("incident_created", incident_id=incident_id)

            try:
                # 2-7. Classify, traverse KG, compose plan, dispatch
                classification = await self._classify_and_dispatch(event, incident_id, root_node_id, repo)
            except Exception as exc:
                await self._handle_dispatch_failure(repo, incident_id, exc)
                raise

            # Emit created event
            await self._emit_redis(
                "incident.created",
                {
                    "incident_id": incident_id,
                    "state": "DISPATCHED",
                    "type": classification.disruption_type,
                    "severity": classification.severity,
                },
            )

        # 8. Dispatch specialists in parallel (outside the first session)
        async with get_session() as session:
            repo = get_repo(session)

            # Reload incident
            incident = await repo.get(incident_id)
            plan_data = incident.plan or {}
            specialists_to_run = plan_data.get("specialists", [])

            # 9. Transition to IN_PROGRESS
            await repo.transition(incident_id, IncidentState.IN_PROGRESS)
            await self._emit_redis(
                "incident.updated",
                {"incident_id": incident_id, "state": "IN_PROGRESS"},
            )

            brief = self._build_brief(incident_id, incident, event, plan_data)

            # Create agent run records upfront
            run_ids = await self._create_agent_runs(repo, incident_id, specialists_to_run, brief)
            # flush to DB before parallel dispatch
            await session.flush()

        # Dispatch in parallel outside the session
        tasks = [_run_specialist(role, run_ids[role], brief) for role in run_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        async with get_session() as session:
            repo = get_repo(session)

            # 10. Aggregate results
            all_runs_summary, any_blocked, any_approval = await self._aggregate_specialist_results(
                repo, incident_id, results
            )

            final_summary = self._build_summary(
                incident.type or "unknown",
                all_runs_summary,
                any_approval,
                any_blocked,
            )

            await repo.update_final_summary(incident_id, final_summary, all_runs_summary)

            # 11/12. Determine final state
            target, emit_topic = self._determine_final_state(any_blocked, any_approval)

            await self._finalize_incident(
                repo, incident, incident_id, final_summary, all_runs_summary, target, emit_topic, any_approval
            )

        return incident_id

    # Function: _classify_and_dispatch
    async def _classify_and_dispatch(self, event: dict, incident_id: str, root_node_id: str | None, repo: IncidentRepo):
        # 2. Classify the event
        classification = await self._classifier.classify(event)

        # Update classification fields
        await repo.update_classification(
            incident_id,
            classification.disruption_type,
            classification.severity,
            classification.confidence,
        )

        # 3. Transition to CLASSIFIED
        await repo.transition(
            incident_id,
            IncidentState.CLASSIFIED,
            payload=classification.to_dict(),
        )

        # 4. Traverse KG for blast radius
        blast_radius = await self._kg.traverse(
            root_node_id or "unknown",
            max_depth=6,
        )

        # 5. Get owners
        owners = await self._kg.get_owners(root_node_id or "unknown")

        await repo.update_blast_radius(incident_id, blast_radius, owners)

        # 6. Compose plan
        plan = self._planner.compose(
            disruption_type=classification.disruption_type,
            severity=classification.severity,
            blast_radius=blast_radius,
            owners=owners,
        )
        await repo.update_plan(incident_id, plan.to_dict())

        # 7. Transition to DISPATCHED
        await repo.transition(incident_id, IncidentState.DISPATCHED)

        return classification

    # Function: _handle_dispatch_failure
    async def _handle_dispatch_failure(self, repo: IncidentRepo, incident_id: str, exc: Exception) -> None:
        log.error("orchestrator_pre_dispatch_failed", incident_id=incident_id, error=str(exc))
        await repo.transition(
            incident_id,
            IncidentState.FAILED,
            payload={"error": str(exc)},
        )
        await self._emit_redis(
            "incident.updated",
            {"incident_id": incident_id, "state": "FAILED", "error": str(exc)},
        )

    # Function: _build_brief
    def _build_brief(self, incident_id: str, incident, event: dict, plan_data: dict) -> dict:
        return {
            "incident_id": incident_id,
            "disruption_type": incident.type,
            "severity": incident.severity,
            "root_node_id": incident.root_node_id,
            "blast_radius": incident.blast_radius or {},
            "owners": incident.owners or [],
            "plan": plan_data,
            "source_event": event,
        }

    # Function: _create_agent_runs
    async def _create_agent_runs(
        self, repo: IncidentRepo, incident_id: str, specialists_to_run: list[str], brief: dict
    ) -> dict[str, str]:
        run_ids: dict[str, str] = {}
        for role in specialists_to_run:
            cls = SPECIALIST_REGISTRY.get(role)
            if cls is None:
                continue
            specialist = cls()
            run = await repo.create_agent_run(
                incident_id=incident_id,
                agent_name=specialist.name,
                agent_role=specialist.role,
                brief=brief,
            )
            run_ids[role] = run.id
        return run_ids

    # Function: _aggregate_specialist_results
    async def _aggregate_specialist_results(
        self, repo: IncidentRepo, incident_id: str, results: list
    ) -> tuple[list[dict], bool, bool]:
        all_runs_summary: list[dict] = []
        any_blocked = False
        any_approval = False

        for item in results:
            if isinstance(item, Exception):
                log.error("specialist_exception", error=str(item))
                any_blocked = True
                continue

            role, run_id, resp = item
            if resp is None:
                continue

            # Persist agent run
            await repo.complete_agent_run(
                run_id=run_id,
                incident_id=incident_id,
                status=resp.status,
                actions_taken=resp.actions_taken,
                findings=resp.findings,
                blockers=resp.blockers,
                recommendation=resp.recommendation,
                confidence=resp.confidence,
                duration_ms=resp.duration_ms,
                token_input=resp.token_input,
                token_output=resp.token_output,
                cost_usd=resp.cost_usd,
            )

            summary = {
                "role": role,
                "agent_name": resp.agent_name,
                "status": resp.status,
                "confidence": resp.confidence,
                "requires_human_approval": resp.requires_human_approval,
                "irreversible_actions": resp.irreversible_actions,
                "recommendation": resp.recommendation,
                "findings": resp.findings,
                "blockers": resp.blockers,
            }
            all_runs_summary.append(summary)

            if resp.status == "blocked":
                any_blocked = True
            if resp.requires_human_approval or resp.irreversible_actions:
                any_approval = True

        return all_runs_summary, any_blocked, any_approval

    # Function: _determine_final_state
    def _determine_final_state(self, any_blocked: bool, any_approval: bool) -> tuple[IncidentState, str]:
        if any_blocked:
            return IncidentState.BLOCKED, "incident.updated"
        if any_approval:
            return IncidentState.AWAITING_APPROVAL, "incident.updated"
        return IncidentState.RESOLVED, "incident.resolved"

    # Function: _finalize_incident
    async def _finalize_incident(
        self,
        repo: IncidentRepo,
        incident,
        incident_id: str,
        final_summary: str,
        all_runs_summary: list[dict],
        target: IncidentState,
        emit_topic: str,
        any_approval: bool,
    ) -> None:
        await repo.transition(
            incident_id,
            target,
            payload={"reason": "specialists_completed"},
        )

        # 13. Outbox
        await repo.write_outbox(
            emit_topic,
            {
                "incident_id": incident_id,
                "state": target.value,
                "type": incident.type,
                "severity": incident.severity,
                "final_summary": final_summary,
            },
        )

        # 14. Emit to Redis streams
        await self._emit_redis(
            emit_topic,
            {
                "incident_id": incident_id,
                "state": target.value,
                "type": incident.type,
                "severity": incident.severity,
                "final_summary": final_summary,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        log.info(
            "orchestration_complete",
            incident_id=incident_id,
            final_state=target.value,
            specialists_run=len(all_runs_summary),
            requires_approval=any_approval,
        )

    # Function: replan_after_rejection
    async def replan_after_rejection(
        self, incident_id: str, rejection_reason: str
    ) -> None:
        """Re-trigger planning after human rejection."""
        async with get_session() as session:
            repo = get_repo(session)
            incident = await repo.get(incident_id)
            if not incident:
                return

            # Transition back to CLASSIFIED
            await repo.transition(
                incident_id,
                IncidentState.CLASSIFIED,
                payload={"rejection_reason": rejection_reason},
            )

            # Rebuild plan with rejection context
            blast_radius = incident.blast_radius or {}
            owners = incident.owners or []
            plan = self._planner.compose(
                disruption_type=incident.type or "unknown",
                severity=incident.severity or "medium",
                blast_radius=blast_radius,
                owners=owners,
                rejection_context=rejection_reason,
            )
            await repo.update_plan(incident_id, plan.to_dict())
            await self._emit_redis(
                "incident.updated",
                {
                    "incident_id": incident_id,
                    "state": "CLASSIFIED",
                    "replanning": True,
                    "rejection_reason": rejection_reason,
                },
            )

    # Function: _build_summary
    def _build_summary(
        self,
        disruption_type: str,
        runs: list[dict],
        requires_approval: bool,
        has_blockers: bool,
    ) -> str:
        completed = [r for r in runs if r.get("status") == "completed"]
        blocked = [r for r in runs if r.get("status") == "blocked"]
        total = len(runs)
        avg_conf = (
            sum(r.get("confidence", 0.0) for r in completed) / len(completed)
            if completed
            else 0.0
        )
        lines = [
            f"Disruption type: {disruption_type}",
            f"Specialists dispatched: {total} | Completed: {len(completed)} | Blocked: {len(blocked)}",
            f"Average confidence: {avg_conf:.2f}",
        ]
        if requires_approval:
            lines.append("Status: AWAITING_HUMAN_APPROVAL — irreversible actions detected.")
        elif has_blockers:
            lines.append("Status: BLOCKED — one or more specialists could not complete.")
        else:
            lines.append("Status: RESOLVED — all specialist actions completed.")

        for r in runs:
            lines.append(f"\n[{r['role'].upper()}] {r['recommendation']}")
            if r.get("blockers"):
                lines.append(f"  Blockers: {', '.join(r['blockers'])}")

        return "\n".join(lines)

    # Function: _emit_redis
    async def _emit_redis(self, stream: str, payload: dict) -> None:
        if self._redis is None:
            return
        try:
            fields = {k: json.dumps(v) if not isinstance(v, str) else v for k, v in payload.items()}
            await self._redis.xadd(stream, fields)
        except Exception as exc:
            log.warning("redis_emit_failed", stream=stream, error=str(exc))
