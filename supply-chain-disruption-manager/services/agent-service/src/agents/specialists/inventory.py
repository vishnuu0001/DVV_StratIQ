# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Inventory specialist agent.
# Date: 2025-12-03
# ---------------------------------------------------------------------------
"""Inventory specialist agent."""
from __future__ import annotations

from agents.specialists.base import BaseSpecialist, SpecialistResponse
from agents.tools.mrp import (
    mrp_stock_query,
    mrp_safety_stock_check,
    mrp_reorder_suggest,
    mrp_consumption_forecast,
)

_IN_SCOPE_TYPES = {
    "supplier_delay",
    "quality_rejection",
    "grn_shortage",
    "demand_spike",
    "demand_change",
    "warehouse_exception",
}


class InventorySpecialist(BaseSpecialist):
    name = "inventory-agent"
    role = "inventory"
    domain = "inventory"
    tools = ["mrp_stock_query", "mrp_safety_stock_check", "mrp_reorder_suggest", "mrp_consumption_forecast"]

    # Function: _in_scope
    def _in_scope(self, brief: dict) -> bool:
        return brief.get("disruption_type", "") in _IN_SCOPE_TYPES

    # Function: _mock_run
    async def _mock_run(self, brief: dict) -> SpecialistResponse:
        disruption_type = brief.get("disruption_type", "supplier_delay")
        payload = brief.get("source_event", {}).get("payload", {})
        material_id = payload.get("material_id", "MAT-RAW-001")
        delay_days = payload.get("delay_days", 7)

        actions = []

        # Check stock levels
        stock = await mrp_stock_query(material_id)
        actions.append({"tool": "mrp_stock_query", "args": {"material_id": material_id}, "result": stock})

        # Check safety stock
        ss_check = await mrp_safety_stock_check(material_id)
        actions.append({"tool": "mrp_safety_stock_check", "args": {"material_id": material_id}, "result": ss_check})

        # Consumption forecast
        forecast = await mrp_consumption_forecast(material_id, days=30)
        actions.append({"tool": "mrp_consumption_forecast", "args": {"material_id": material_id, "days": 30}, "result": forecast})

        on_hand = stock.get("on_hand_qty", 0)
        daily_consumption = forecast.get("daily_avg_consumption", 10)
        days_of_coverage = on_hand / daily_consumption if daily_consumption > 0 else 999
        below_safety = ss_check.get("below_safety_stock", False)
        safety_days = ss_check.get("safety_stock_days", 14)

        actions_taken = list(actions)

        if disruption_type in ("supplier_delay", "grn_shortage", "quality_rejection"):
            if days_of_coverage < delay_days + safety_days:
                # Suggest reorder
                reorder = await mrp_reorder_suggest(material_id, delay_days + safety_days)
                actions_taken.append({
                    "tool": "mrp_reorder_suggest",
                    "args": {"material_id": material_id, "target_days": delay_days + safety_days},
                    "result": reorder,
                })
                shortage_risk = True
            else:
                shortage_risk = False

            return SpecialistResponse(
                agent_name=self.name,
                status="completed",
                actions_taken=actions_taken,
                findings=(
                    f"Material {material_id}: on-hand {on_hand} units, "
                    f"{days_of_coverage:.1f} days of coverage. "
                    f"Delay impact: {delay_days} days. "
                    f"Safety stock: {'BELOW' if below_safety else 'OK'}. "
                    + ("SHORTAGE RISK — reorder recommended." if shortage_risk else "Coverage adequate.")
                ),
                blockers=["Insufficient stock coverage for delay duration"] if shortage_risk else [],
                recommendation=(
                    f"Expedite reorder for {material_id} — shortage projected in {days_of_coverage:.0f} days. "
                    "Consider temporary safety stock uplift."
                    if shortage_risk
                    else f"Stock coverage of {days_of_coverage:.0f} days is sufficient. Monitor daily."
                ),
                confidence=0.89,
                requires_human_approval=shortage_risk and days_of_coverage < 7,
                irreversible_actions=[],
            )

        elif disruption_type in ("demand_spike", "demand_change"):
            reorder = await mrp_reorder_suggest(material_id, 60)
            actions_taken.append({
                "tool": "mrp_reorder_suggest",
                "args": {"material_id": material_id, "target_days": 60},
                "result": reorder,
            })

            return SpecialistResponse(
                agent_name=self.name,
                status="completed",
                actions_taken=actions_taken,
                findings=(
                    f"Demand spike detected. Current coverage: {days_of_coverage:.1f} days. "
                    f"Daily consumption avg: {daily_consumption} units."
                ),
                blockers=[],
                recommendation=(
                    "Increase safety stock target by 20% for next 60 days. "
                    "Coordinate with buyer to expedite supplier orders."
                ),
                confidence=0.82,
                requires_human_approval=False,
            )

        return SpecialistResponse(
            agent_name=self.name,
            status="completed",
            actions_taken=actions_taken,
            findings=f"Inventory review completed for {disruption_type}.",
            recommendation="No inventory action required.",
            confidence=0.75,
        )
