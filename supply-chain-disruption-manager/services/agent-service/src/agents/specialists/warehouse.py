# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Warehouse specialist agent.
# Date: 2025-07-31
# ---------------------------------------------------------------------------
"""Warehouse specialist agent."""
from __future__ import annotations

from agents.specialists.base import BaseSpecialist, SpecialistResponse
from agents.tools.wms import (
    wms_bin_query,
    wms_grn_create,
    wms_inventory_reserve,
    wms_putaway_suggest,
    wms_transfer_order_create,
)

_IN_SCOPE_TYPES = {
    "grn_shortage",
    "short_pick",
    "warehouse_exception",
    "logistics_delay",
    "workcenter_stoppage",
    "supplier_shipment",
}


class WarehouseSpecialist(BaseSpecialist):
    name = "warehouse-agent"
    role = "warehouse"
    domain = "warehouse"
    tools = ["wms_bin_query", "wms_grn_create", "wms_inventory_reserve", "wms_putaway_suggest", "wms_transfer_order_create"]

    # Function: _in_scope
    def _in_scope(self, brief: dict) -> bool:
        return brief.get("disruption_type", "") in _IN_SCOPE_TYPES

    # Function: _mock_run
    async def _mock_run(self, brief: dict) -> SpecialistResponse:
        disruption_type = brief.get("disruption_type", "grn_shortage")
        payload = brief.get("source_event", {}).get("payload", {})
        material_id = payload.get("material_id", "MAT-RAW-001")
        sku_id = payload.get("sku_id", "SKU-PROD-001")
        short_qty = payload.get("short_qty", 50)

        actions = []

        if disruption_type == "grn_shortage":
            # Check bin levels
            bin_data = await wms_bin_query(material_id)
            actions.append({"tool": "wms_bin_query", "args": {"material_id": material_id}, "result": bin_data})

            on_hand_qty = sum(b.get("qty", 0) for b in bin_data.get("bins", []))
            shortage_covered = on_hand_qty >= short_qty

            if not shortage_covered:
                # Try transfer from another DC
                transfer = await wms_transfer_order_create(
                    from_location="WH-002", to_location="WH-001", material_id=material_id, qty=short_qty
                )
                actions.append({
                    "tool": "wms_transfer_order_create",
                    "args": {"from": "WH-002", "to": "WH-001", "material_id": material_id, "qty": short_qty},
                    "result": transfer,
                })

            return SpecialistResponse(
                agent_name=self.name,
                status="completed",
                actions_taken=actions,
                findings=(
                    f"GRN short by {short_qty} units of {material_id}. "
                    f"On-hand: {on_hand_qty} units across {len(bin_data.get('bins', []))} bins. "
                    + ("Transfer order created from WH-002." if not shortage_covered else "Existing stock sufficient to cover shortage.")
                ),
                blockers=[] if shortage_covered else [],
                recommendation=(
                    "Transfer order from secondary DC will cover shortage. "
                    "Expected arrival: 1 business day."
                    if not shortage_covered
                    else "No warehouse action required — stock on hand."
                ),
                confidence=0.91,
                requires_human_approval=False,
                irreversible_actions=[],
            )

        elif disruption_type == "short_pick":
            bin_data = await wms_bin_query(sku_id)
            actions.append({"tool": "wms_bin_query", "args": {"material_id": sku_id}, "result": bin_data})

            available = sum(b.get("qty", 0) for b in bin_data.get("bins", []))
            reserve = await wms_inventory_reserve(sku_id, min(available, short_qty), "PROD-ORDER-001")
            actions.append({
                "tool": "wms_inventory_reserve",
                "args": {"sku_id": sku_id, "qty": min(available, short_qty), "order_id": "PROD-ORDER-001"},
                "result": reserve,
            })

            return SpecialistResponse(
                agent_name=self.name,
                status="completed",
                actions_taken=actions,
                findings=(
                    f"Short pick of {short_qty} units for {sku_id}. "
                    f"Available: {available} units. Reserved {reserve.get('reserved_qty', 0)} units."
                ),
                blockers=["Insufficient stock for full production order"] if available < short_qty else [],
                recommendation=(
                    "Partial pick approved. Notify production planner of shortfall. "
                    "Request replenishment from supplier."
                ),
                confidence=0.87,
                requires_human_approval=True,
                irreversible_actions=["Partial pick dispatch to production floor"],
            )

        elif disruption_type == "warehouse_exception":
            bin_data = await wms_bin_query(material_id)
            actions.append({"tool": "wms_bin_query", "args": {"material_id": material_id}, "result": bin_data})
            putaway = await wms_putaway_suggest(material_id, 100)
            actions.append({"tool": "wms_putaway_suggest", "args": {"material_id": material_id, "qty": 100}, "result": putaway})

            return SpecialistResponse(
                agent_name=self.name,
                status="completed",
                actions_taken=actions,
                findings=f"Bin exception for {material_id}. Putaway suggestion: {putaway.get('suggested_bin', 'BIN-A01')}.",
                recommendation="Re-slot material to suggested bin. Update WMS records.",
                confidence=0.83,
                requires_human_approval=False,
            )

        return SpecialistResponse(
            agent_name=self.name,
            status="completed",
            actions_taken=actions,
            findings=f"Warehouse review completed for {disruption_type}.",
            recommendation="No immediate warehouse action required.",
            confidence=0.78,
        )
