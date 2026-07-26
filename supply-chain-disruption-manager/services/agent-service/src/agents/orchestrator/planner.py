# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Response planner — maps disruption type to specialist assignments.
# Date: 2025-08-20
# ---------------------------------------------------------------------------
"""Response planner — maps disruption type to specialist assignments."""
from __future__ import annotations

import structlog

from agents.config import get_settings

log = structlog.get_logger(__name__)

# Maps disruption type -> list of specialist roles to dispatch
AGENT_DISPATCH_MAP: dict[str, list[str]] = {
    "supplier_delay": ["buyer", "logistics", "inventory", "planning"],
    "supplier_shipment": ["logistics", "warehouse"],
    "logistics_delay": ["logistics", "warehouse", "planning"],
    "customs_hold": ["logistics", "buyer"],
    "quality_rejection": ["quality", "buyer", "inventory", "planning"],
    "grn_shortage": ["warehouse", "buyer", "inventory"],
    "short_pick": ["warehouse", "planning", "shopfloor"],
    "workcenter_stoppage": ["shopfloor", "planning", "warehouse"],
    "demand_spike": ["planning", "buyer", "logistics", "inventory"],
    "demand_change": ["planning", "inventory"],
    "warehouse_exception": ["warehouse", "inventory"],
}

# Whether human approval is required (by default) for this type
HUMAN_APPROVAL_REQUIRED: dict[str, bool] = {
    "supplier_delay": True,
    "supplier_shipment": False,
    "logistics_delay": False,
    "customs_hold": False,
    "quality_rejection": True,
    "grn_shortage": False,
    "short_pick": True,
    "workcenter_stoppage": True,
    "demand_spike": False,
    "demand_change": False,
    "warehouse_exception": False,
}

# Approval required if severity reaches threshold
SEVERITY_APPROVAL_THRESHOLD: dict[str, bool] = {
    "critical": True,
    "high": False,
    "medium": False,
    "low": False,
}


class ResponsePlan:
    # Function: __init__
    def __init__(
        self,
        disruption_type: str,
        specialists: list[str],
        requires_human_approval: bool,
        context: dict | None = None,
    ) -> None:
        self.disruption_type = disruption_type
        self.specialists = specialists
        self.requires_human_approval = requires_human_approval
        self.context = context or {}

    # Function: to_dict
    def to_dict(self) -> dict:
        return {
            "disruption_type": self.disruption_type,
            "specialists": self.specialists,
            "requires_human_approval": self.requires_human_approval,
            "context": self.context,
        }


class Planner:
    """Composes the response plan for an incident."""

    # Function: __init__
    def __init__(self) -> None:
        self._settings = get_settings()

    # Function: compose
    def compose(
        self,
        disruption_type: str,
        severity: str,
        blast_radius: dict,
        owners: list[dict],
        rejection_context: str | None = None,
    ) -> ResponsePlan:
        """Determine which specialists to dispatch and if human approval needed."""
        specialists = AGENT_DISPATCH_MAP.get(disruption_type, ["planning"])

        requires_approval = HUMAN_APPROVAL_REQUIRED.get(disruption_type, False)
        if not requires_approval and SEVERITY_APPROVAL_THRESHOLD.get(severity, False):
            requires_approval = True

        affected_nodes = [n.get("id") for n in blast_radius.get("nodes", [])]
        affected_domains = list({n.get("domain") for n in blast_radius.get("nodes", []) if n.get("domain")})

        context: dict = {
            "severity": severity,
            "affected_nodes": affected_nodes[:20],
            "affected_domains": affected_domains,
            "owner_count": len(owners),
        }
        if rejection_context:
            context["rejection_context"] = rejection_context
            context["replanning"] = True

        log.info(
            "plan_composed",
            disruption_type=disruption_type,
            specialists=specialists,
            requires_approval=requires_approval,
            severity=severity,
        )
        return ResponsePlan(disruption_type, specialists, requires_approval, context)
