# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Agent workbench endpoints.
# Date: 2025-12-01
# ---------------------------------------------------------------------------
"""Agent workbench endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query

from agents.auth import require_api_key
from agents.store.database import get_session
from agents.store.incident_repo import get_repo

router = APIRouter(tags=["agents"], dependencies=[Depends(require_api_key)])


DEFAULT_AGENTS: list[dict[str, Any]] = [
    {
        "name": "Orchestrator",
        "role": "Master coordinator",
        "domain": "orchestrator",
        "tools": ["classify_incident", "dispatch_specialist", "await_approval", "resolve_incident"],
    },
    {
        "name": "Procurement Specialist",
        "role": "Supplier and PO analysis",
        "domain": "procurement",
        "tools": ["query_kg", "assess_supplier_risk", "find_alternative_suppliers", "evaluate_po_impact"],
    },
    {
        "name": "Logistics Specialist",
        "role": "Shipment and transit analysis",
        "domain": "logistics",
        "tools": ["query_kg", "check_shipment_status", "find_alternate_routes", "assess_customs_risk"],
    },
    {
        "name": "Warehouse Specialist",
        "role": "Inventory and warehouse operations",
        "domain": "warehouse",
        "tools": ["query_kg", "check_inventory_levels", "assess_qc_impact", "find_alternative_stock"],
    },
    {
        "name": "Production Specialist",
        "role": "Production line analysis",
        "domain": "production",
        "tools": ["query_kg", "assess_production_impact", "find_component_alternatives", "evaluate_schedule"],
    },
    {
        "name": "People Specialist",
        "role": "Staffing and HR analysis",
        "domain": "people",
        "tools": ["query_kg", "assess_staffing_needs", "find_coverage", "evaluate_compliance"],
    },
]


# Function: _card
def _card(agent: dict[str, Any]) -> dict[str, Any]:
    return {
        **agent,
        "last_run_at": None,
        "status": "idle",
        "last_confidence": None,
        "last_actions": [],
        "scope_violations": [],
    }


# Function: _serialise_ts
def _serialise_ts(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


# Function: _card_for_run
def _card_for_run(cards: dict[str, dict[str, Any]], run: dict[str, Any]) -> dict[str, Any]:
    name = run.get("agent_name") or run.get("agent") or run.get("domain") or "Unknown Agent"
    return cards.setdefault(
        name,
        {
            "name": name,
            "role": run.get("agent_role") or "Specialist",
            "domain": run.get("domain") or "system",
            "tools": [],
            "last_actions": [],
            "scope_violations": [],
            "last_run_at": None,
            "status": "idle",
            "last_confidence": None,
        },
    )


# Function: _update_card_from_run
def _update_card_from_run(card: dict[str, Any], run: dict[str, Any], incident: Any, incident_ts: Any) -> None:
    completed_at = run.get("completed_at") or run.get("started_at") or incident_ts
    current = card.get("last_run_at")
    if current is not None and not (completed_at and str(completed_at) > str(current)):
        return
    card["last_run_at"] = _serialise_ts(completed_at)
    card["status"] = "running" if run.get("status") == "running" else run.get("status", "idle")
    card["last_confidence"] = run.get("confidence")
    card["last_actions"] = run.get("actions") or run.get("actions_taken") or []
    card["scope_violations"] = run.get("scope_violations") or run.get("blockers") or []
    card["findings"] = run.get("findings") or run.get("recommendation") or ""
    card["last_incident_id"] = str(incident.id)
    card["duration_ms"] = run.get("duration_ms")


# Function: list_agents
@router.get("/agents")
async def list_agents() -> list[dict[str, Any]]:
    cards = {_card(agent)["name"]: _card(agent) for agent in DEFAULT_AGENTS}

    async with get_session() as session:
        repo = get_repo(session)
        incidents = await repo.list_incidents(limit=50)
        for incident in incidents:
            incident_ts = incident.updated_at or incident.created_at
            for run in incident.specialist_runs or []:
                card = _card_for_run(cards, run)
                _update_card_from_run(card, run, incident, incident_ts)

    return list(cards.values())


# Function: _run_record
def _run_record(incident: Any, run: dict[str, Any]) -> dict[str, Any]:
    return {
        "incident_id": str(incident.id),
        "incident_type": incident.type or "unknown",
        "incident_state": incident.state,
        "status": run.get("status", "unknown"),
        "confidence": run.get("confidence"),
        "findings": run.get("findings") or run.get("recommendation") or "",
        "recommendation": run.get("recommendation") or "",
        "actions": run.get("actions") or run.get("actions_taken") or [],
        "scope_violations": run.get("scope_violations") or run.get("blockers") or [],
        "started_at": _serialise_ts(run.get("started_at")),
        "completed_at": _serialise_ts(run.get("completed_at")),
        "duration_ms": run.get("duration_ms"),
        "token_usage": run.get("token_usage"),
    }


# Function: _matching_runs_for_incident
def _matching_runs_for_incident(incident: Any, name: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for run in incident.specialist_runs or []:
        run_name = run.get("agent_name") or run.get("agent") or run.get("domain") or ""
        if run_name.lower() != name.lower():
            continue
        matches.append(_run_record(incident, run))
    return matches


# Function: get_agent_runs
@router.get("/agents/{name}/runs")
async def get_agent_runs(
    name: str,
    limit: int = Query(10, ge=1, le=50),
) -> list[dict[str, Any]]:
    """Return the last N runs for a specific agent across all incidents."""
    results: list[dict[str, Any]] = []
    async with get_session() as session:
        repo = get_repo(session)
        incidents = await repo.list_incidents(limit=200)
        for incident in incidents:
            results.extend(_matching_runs_for_incident(incident, name))
            if len(results) >= limit:
                break
    return results[:limit]
