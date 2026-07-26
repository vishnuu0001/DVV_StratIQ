# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Shopfloor / MES specialist agent.
# Date: 2025-11-26
# ---------------------------------------------------------------------------
"""Shopfloor / MES specialist agent."""
from __future__ import annotations

from agents.specialists.base import BaseSpecialist, SpecialistResponse
from agents.tools.mes import (
    mes_workcenter_status,
    mes_production_order_get,
    mes_workcenter_assign,
    mes_downtime_log,
    mes_capacity_check,
)

_IN_SCOPE_TYPES = {"short_pick", "workcenter_stoppage", "demand_spike"}


class ShopfloorSpecialist(BaseSpecialist):
    name = "shopfloor-agent"
    role = "shopfloor"
    domain = "manufacturing"
    tools = ["mes_workcenter_status", "mes_production_order_get", "mes_workcenter_assign", "mes_downtime_log", "mes_capacity_check"]

    # Function: _in_scope
    def _in_scope(self, brief: dict) -> bool:
        return brief.get("disruption_type", "") in _IN_SCOPE_TYPES

    # Function: _mock_run
    async def _mock_run(self, brief: dict) -> SpecialistResponse:
        disruption_type = brief.get("disruption_type", "workcenter_stoppage")
        payload = brief.get("source_event", {}).get("payload", {})
        workcenter_id = payload.get("workcenter_id", "WC-001")
        prod_order_id = payload.get("production_order_id", "PRD-2026-0081")
        stoppage_reason = payload.get("reason", "equipment_failure")

        actions = []

        wc_status = await mes_workcenter_status(workcenter_id)
        actions.append({"tool": "mes_workcenter_status", "args": {"workcenter_id": workcenter_id}, "result": wc_status})

        if disruption_type == "workcenter_stoppage":
            # Log downtime
            downtime = await mes_downtime_log(workcenter_id, stoppage_reason, "ongoing")
            actions.append({
                "tool": "mes_downtime_log",
                "args": {"workcenter_id": workcenter_id, "reason": stoppage_reason},
                "result": downtime,
            })

            # Check alternate capacity
            cap_check = await mes_capacity_check(["WC-002", "WC-003"], prod_order_id)
            actions.append({
                "tool": "mes_capacity_check",
                "args": {"workcenter_ids": ["WC-002", "WC-003"], "prod_order_id": prod_order_id},
                "result": cap_check,
            })

            best_wc = cap_check.get("recommended_workcenter", "WC-002")

            if cap_check.get("capacity_available", True):
                assign = await mes_workcenter_assign(prod_order_id, best_wc)
                actions.append({
                    "tool": "mes_workcenter_assign",
                    "args": {"prod_order_id": prod_order_id, "workcenter_id": best_wc},
                    "result": assign,
                })

            return SpecialistResponse(
                agent_name=self.name,
                status="completed",
                actions_taken=actions,
                findings=(
                    f"Work center {workcenter_id} stopped — {stoppage_reason}. "
                    f"Downtime logged (ref: {downtime.get('downtime_id', 'DT-001')}). "
                    + (
                        f"Production order {prod_order_id} reassigned to {best_wc}."
                        if cap_check.get("capacity_available")
                        else f"No alternate capacity available — production halted."
                    )
                ),
                blockers=[] if cap_check.get("capacity_available") else ["No alternate work center capacity"],
                recommendation=(
                    f"Expedite maintenance on {workcenter_id}. "
                    f"Continue production on {best_wc} in the interim. "
                    "Notify planning of expected capacity recovery time."
                ),
                confidence=0.88,
                requires_human_approval=True,
                irreversible_actions=[f"Reassign production order {prod_order_id} to {best_wc}"],
            )

        elif disruption_type == "short_pick":
            prod_order = await mes_production_order_get(prod_order_id)
            actions.append({
                "tool": "mes_production_order_get",
                "args": {"prod_order_id": prod_order_id},
                "result": prod_order,
            })

            short_qty = payload.get("short_qty", 50)
            required_qty = prod_order.get("required_qty", 200)
            available_pct = (required_qty - short_qty) / required_qty * 100 if required_qty > 0 else 0

            return SpecialistResponse(
                agent_name=self.name,
                status="completed",
                actions_taken=actions,
                findings=(
                    f"Short pick of {short_qty} units. Production order {prod_order_id} "
                    f"can proceed at {available_pct:.0f}% of planned volume."
                ),
                blockers=["Short pick will result in partial production run"] if available_pct < 80 else [],
                recommendation=(
                    f"Proceed with partial production at {available_pct:.0f}% volume. "
                    "Hold open line item for balance when material arrives."
                ),
                confidence=0.85,
                requires_human_approval=available_pct < 50,
                irreversible_actions=[],
            )

        return SpecialistResponse(
            agent_name=self.name,
            status="completed",
            actions_taken=actions,
            findings=f"Shopfloor review completed for {disruption_type}.",
            recommendation="No shopfloor action required.",
            confidence=0.75,
        )
