# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Planning specialist agent.
# Date: 2026-01-22
# ---------------------------------------------------------------------------
"""Planning specialist agent."""
from __future__ import annotations

from agents.specialists.base import BaseSpecialist, SpecialistResponse
from agents.tools.mrp import (
    mrp_production_plan_get,
    mrp_production_plan_revise,
    mrp_stock_query,
    mrp_consumption_forecast,
)

_IN_SCOPE_TYPES = {
    "supplier_delay",
    "logistics_delay",
    "quality_rejection",
    "short_pick",
    "workcenter_stoppage",
    "demand_spike",
    "demand_change",
}


class PlanningSpecialist(BaseSpecialist):
    name = "planning-agent"
    role = "planning"
    domain = "production_planning"
    tools = ["mrp_production_plan_get", "mrp_production_plan_revise", "mrp_stock_query", "mrp_consumption_forecast"]

    # Function: _in_scope
    def _in_scope(self, brief: dict) -> bool:
        return brief.get("disruption_type", "") in _IN_SCOPE_TYPES

    # Function: _mock_run
    async def _mock_run(self, brief: dict) -> SpecialistResponse:
        disruption_type = brief.get("disruption_type", "supplier_delay")
        payload = brief.get("source_event", {}).get("payload", {})
        delay_days = payload.get("delay_days", 7)
        material_id = payload.get("material_id", "MAT-RAW-001")

        actions = []

        plan = await mrp_production_plan_get("PROD-PLAN-2026-Q3")
        actions.append({
            "tool": "mrp_production_plan_get",
            "args": {"plan_id": "PROD-PLAN-2026-Q3"},
            "result": plan,
        })

        stock = await mrp_stock_query(material_id)
        actions.append({"tool": "mrp_stock_query", "args": {"material_id": material_id}, "result": stock})

        forecast = await mrp_consumption_forecast(material_id, days=45)
        actions.append({"tool": "mrp_consumption_forecast", "args": {"material_id": material_id, "days": 45}, "result": forecast})

        if disruption_type in ("supplier_delay", "quality_rejection", "grn_shortage"):
            # Re-sequence production around material availability
            revision = await mrp_production_plan_revise(
                "PROD-PLAN-2026-Q3",
                {
                    "action": "defer_orders_requiring_material",
                    "material_id": material_id,
                    "defer_by_days": delay_days,
                },
            )
            actions.append({
                "tool": "mrp_production_plan_revise",
                "args": {"plan_id": "PROD-PLAN-2026-Q3", "changes": {"defer_by_days": delay_days}},
                "result": revision,
            })

            return SpecialistResponse(
                agent_name=self.name,
                status="completed",
                actions_taken=actions,
                findings=(
                    f"Production plan revised — {revision.get('orders_rescheduled', 3)} orders "
                    f"deferred by {delay_days} days due to {material_id} shortage. "
                    f"Impact: {revision.get('revenue_at_risk_usd', 125000)} USD at risk."
                ),
                blockers=[],
                recommendation=(
                    "Notify sales on affected order dates. "
                    "Run MRP re-plan after supplier confirms new ETA. "
                    "Consider substituting alternate material if available."
                ),
                confidence=0.86,
                requires_human_approval=False,
                irreversible_actions=[],
            )

        elif disruption_type in ("short_pick", "workcenter_stoppage"):
            revision = await mrp_production_plan_revise(
                "PROD-PLAN-2026-Q3",
                {"action": "rebalance_capacity", "affected_workcenter": payload.get("workcenter_id", "WC-001")},
            )
            actions.append({
                "tool": "mrp_production_plan_revise",
                "args": {"plan_id": "PROD-PLAN-2026-Q3", "changes": {"action": "rebalance_capacity"}},
                "result": revision,
            })

            return SpecialistResponse(
                agent_name=self.name,
                status="completed",
                actions_taken=actions,
                findings=(
                    f"Work center rebalancing completed. "
                    f"Orders redirected: {revision.get('orders_rescheduled', 2)}. "
                    "Alternate capacity identified on WC-002."
                ),
                blockers=[],
                recommendation=(
                    "Activate WC-002 overtime allocation. "
                    "Customer communication required for orders with >3 day slip."
                ),
                confidence=0.84,
                requires_human_approval=True,
                irreversible_actions=["Overtime allocation on WC-002"],
            )

        elif disruption_type in ("demand_spike", "demand_change"):
            revision = await mrp_production_plan_revise(
                "PROD-PLAN-2026-Q3",
                {
                    "action": "uplift_production",
                    "uplift_pct": payload.get("uplift_pct", 20),
                },
            )
            actions.append({
                "tool": "mrp_production_plan_revise",
                "args": {"plan_id": "PROD-PLAN-2026-Q3", "changes": {"action": "uplift_production"}},
                "result": revision,
            })

            return SpecialistResponse(
                agent_name=self.name,
                status="completed",
                actions_taken=actions,
                findings=(
                    f"Production uplift of {payload.get('uplift_pct', 20)}% planned. "
                    f"Capacity check: {revision.get('capacity_utilization_pct', 92)}% utilization."
                ),
                blockers=["Raw material availability must be confirmed"] if stock.get("on_hand_qty", 0) < 500 else [],
                recommendation=(
                    "Confirm raw material supply before authorizing capacity uplift. "
                    "Coordinate with buyer on expedite orders."
                ),
                confidence=0.79,
                requires_human_approval=False,
            )

        return SpecialistResponse(
            agent_name=self.name,
            status="completed",
            actions_taken=actions,
            findings=f"Planning review completed for {disruption_type}.",
            recommendation="No planning action required.",
            confidence=0.75,
        )
