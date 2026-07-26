# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Logistics specialist agent.
# Date: 2026-05-17
# ---------------------------------------------------------------------------
"""Logistics specialist agent."""
from __future__ import annotations

from agents.specialists.base import BaseSpecialist, SpecialistResponse
from agents.tools.tms import (
    tms_shipment_get,
    tms_shipment_reroute,
    tms_carrier_book,
    tms_customs_status,
    tms_eta_update,
)

_IN_SCOPE_TYPES = {
    "logistics_delay",
    "customs_hold",
    "supplier_delay",
    "supplier_shipment",
    "demand_spike",
}


class LogisticsSpecialist(BaseSpecialist):
    name = "logistics-agent"
    role = "logistics"
    domain = "transportation"
    tools = ["tms_shipment_get", "tms_shipment_reroute", "tms_carrier_book", "tms_customs_status", "tms_eta_update"]

    # Function: _in_scope
    def _in_scope(self, brief: dict) -> bool:
        return brief.get("disruption_type", "") in _IN_SCOPE_TYPES

    # Function: _mock_run
    async def _mock_run(self, brief: dict) -> SpecialistResponse:
        disruption_type = brief.get("disruption_type", "logistics_delay")
        payload = brief.get("source_event", {}).get("payload", {})
        shipment_id = payload.get("shipment_id", "SHIPMENT-001")
        delay_days = payload.get("delay_days", 0)

        actions = []

        shipment = await tms_shipment_get(shipment_id)
        actions.append({"tool": "tms_shipment_get", "args": {"shipment_id": shipment_id}, "result": shipment})

        if disruption_type == "logistics_delay":
            # Update ETA
            new_eta = payload.get("new_eta", "2026-07-22")
            eta_result = await tms_eta_update(shipment_id, new_eta)
            actions.append({"tool": "tms_eta_update", "args": {"shipment_id": shipment_id, "new_eta": new_eta}, "result": eta_result})

            # Try reroute
            reroute = await tms_shipment_reroute(shipment_id, "FASTEST")
            actions.append({"tool": "tms_shipment_reroute", "args": {"shipment_id": shipment_id, "mode": "FASTEST"}, "result": reroute})

            return SpecialistResponse(
                agent_name=self.name,
                status="completed",
                actions_taken=actions,
                findings=(
                    f"Shipment {shipment_id} delayed by {delay_days} days. "
                    f"ETA updated to {new_eta}. Rerouting via fastest available lane attempted."
                ),
                blockers=[],
                recommendation=(
                    "Expedite via air freight if delay > 5 days and material is critical. "
                    "Notify downstream warehouse of new ETA."
                ),
                confidence=0.85,
                requires_human_approval=delay_days >= 7,
                irreversible_actions=["Book air freight upgrade"] if delay_days >= 7 else [],
            )

        elif disruption_type == "customs_hold":
            customs = await tms_customs_status(shipment_id)
            actions.append({"tool": "tms_customs_status", "args": {"shipment_id": shipment_id}, "result": customs})

            return SpecialistResponse(
                agent_name=self.name,
                status="completed",
                actions_taken=actions,
                findings=(
                    f"Shipment {shipment_id} held at customs. "
                    f"Status: {customs.get('status', 'unknown')}. "
                    f"Hold reason: {customs.get('hold_reason', 'Documentation issue')}."
                ),
                blockers=["Awaiting customs clearance"],
                recommendation=(
                    "Engage customs broker immediately. "
                    "Submit missing HS code documentation. "
                    "Expected clearance within 2-3 business days."
                ),
                confidence=0.80,
                requires_human_approval=False,
            )

        elif disruption_type in ("supplier_delay", "supplier_shipment"):
            # Book expedite carrier
            booking = await tms_carrier_book("CARRIER-FAST-001", shipment_id, "EXPRESS")
            actions.append({
                "tool": "tms_carrier_book",
                "args": {"carrier_id": "CARRIER-FAST-001", "shipment_id": shipment_id, "service": "EXPRESS"},
                "result": booking,
            })

            return SpecialistResponse(
                agent_name=self.name,
                status="completed",
                actions_taken=actions,
                findings=f"Express carrier booked for expedited shipment of {shipment_id}.",
                recommendation="Monitor carrier ETA updates. Confirm pickup with supplier.",
                confidence=0.82,
                requires_human_approval=True,
                irreversible_actions=["Book express carrier — incurs premium freight cost"],
            )

        return SpecialistResponse(
            agent_name=self.name,
            status="completed",
            actions_taken=actions,
            findings=f"Logistics review completed for {disruption_type}.",
            recommendation="No immediate logistics intervention required.",
            confidence=0.75,
        )
