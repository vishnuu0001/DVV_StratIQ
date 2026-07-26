# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Buyer/Procurement specialist agent.
# Date: 2026-05-17
# ---------------------------------------------------------------------------
"""Buyer/Procurement specialist agent."""
from __future__ import annotations

from agents.specialists.base import BaseSpecialist, SpecialistResponse
from agents.tools.erp import (
    erp_po_get,
    erp_po_update_status,
    sourcing_alternates,
    supplier_contact,
)

_IN_SCOPE_TYPES = {
    "supplier_delay",
    "customs_hold",
    "quality_rejection",
    "grn_shortage",
    "demand_spike",
}


class BuyerSpecialist(BaseSpecialist):
    name = "buyer-agent"
    role = "buyer"
    domain = "procurement"
    tools = ["erp_po_get", "erp_po_update_status", "sourcing_alternates", "supplier_contact"]

    # Function: _in_scope
    def _in_scope(self, brief: dict) -> bool:
        return brief.get("disruption_type", "") in _IN_SCOPE_TYPES

    # Function: _mock_run
    async def _mock_run(self, brief: dict) -> SpecialistResponse:
        disruption_type = brief.get("disruption_type", "supplier_delay")
        payload = brief.get("source_event", {}).get("payload", {})
        po_id = payload.get("po_id") or payload.get("po_ids_affected", ["PO-10001"])[0]
        supplier_id = payload.get("supplier_id", "SUP-001")
        delay_days = payload.get("delay_days", 7)

        actions = []

        # Fetch PO details
        po_data = await erp_po_get(po_id)
        actions.append({"tool": "erp_po_get", "args": {"po_id": po_id}, "result": po_data})

        if disruption_type == "supplier_delay":
            # Contact supplier
            contact_result = await supplier_contact(
                supplier_id,
                "email",
                f"Urgent: PO {po_id} delayed {delay_days} days. Please confirm new ETA.",
            )
            actions.append({
                "tool": "supplier_contact",
                "args": {"supplier_id": supplier_id, "channel": "email"},
                "result": contact_result,
            })

            # Find alternates for the material
            material_id = po_data["lines"][0]["material_id"] if po_data.get("lines") else "MAT-RAW-001"
            alts = await sourcing_alternates(material_id)
            actions.append({
                "tool": "sourcing_alternates",
                "args": {"material_id": material_id},
                "result": alts,
            })

            has_alternate = bool(alts.get("alternates"))
            best_alt = alts["alternates"][0] if has_alternate else None

            return SpecialistResponse(
                agent_name=self.name,
                status="completed",
                actions_taken=actions,
                findings=(
                    f"PO {po_id} delayed by {delay_days} days from supplier {supplier_id}. "
                    f"Supplier contacted via email. "
                    + (
                        f"Alternate supplier {best_alt['supplier_id']} available "
                        f"with {best_alt['lead_time_days']} day lead time."
                        if best_alt
                        else "No alternate suppliers found — escalation required."
                    )
                ),
                blockers=[] if has_alternate else ["No alternate supplier with sufficient lead time"],
                recommendation=(
                    f"Place emergency PO with {best_alt['supplier_id']} for critical quantity. "
                    f"Update original PO {po_id} status to DELAYED. "
                    "Requires approval to commit additional spend."
                    if best_alt
                    else "Escalate to procurement director — no alternates available."
                ),
                confidence=0.88,
                requires_human_approval=True,
                irreversible_actions=[f"Issue alternate PO to {best_alt['supplier_id']}"] if best_alt else [],
            )

        elif disruption_type in ("customs_hold", "grn_shortage"):
            # Flag PO on hold
            update = await erp_po_update_status(po_id, "ON_HOLD", "Customs hold / GRN shortage")
            actions.append({
                "tool": "erp_po_update_status",
                "args": {"po_id": po_id, "new_status": "ON_HOLD"},
                "result": update,
            })

            alts = await sourcing_alternates("MAT-RAW-001")
            actions.append({
                "tool": "sourcing_alternates",
                "args": {"material_id": "MAT-RAW-001"},
                "result": alts,
            })

            return SpecialistResponse(
                agent_name=self.name,
                status="completed",
                actions_taken=actions,
                findings=f"PO {po_id} placed on hold. Alternate sourcing options identified.",
                blockers=[],
                recommendation="Expedite customs clearance OR activate alternate supplier.",
                confidence=0.85,
                requires_human_approval=False,
                irreversible_actions=[],
            )

        elif disruption_type == "quality_rejection":
            update = await erp_po_update_status(po_id, "QUALITY_HOLD", "QC rejection")
            actions.append({
                "tool": "erp_po_update_status",
                "args": {"po_id": po_id, "new_status": "QUALITY_HOLD"},
                "result": update,
            })
            contact = await supplier_contact(
                supplier_id,
                "portal",
                f"Quality rejection on PO {po_id} — corrective action report required within 24h.",
            )
            actions.append({
                "tool": "supplier_contact",
                "args": {"supplier_id": supplier_id, "channel": "portal"},
                "result": contact,
            })

            return SpecialistResponse(
                agent_name=self.name,
                status="completed",
                actions_taken=actions,
                findings=f"PO {po_id} placed on QUALITY_HOLD. Supplier notified via portal.",
                blockers=[],
                recommendation="Await corrective action report from supplier. Consider return shipment.",
                confidence=0.90,
                requires_human_approval=True,
                irreversible_actions=["Return shipment to supplier"],
            )

        # Generic path
        return SpecialistResponse(
            agent_name=self.name,
            status="completed",
            actions_taken=actions,
            findings=f"Buyer review completed for {disruption_type}.",
            recommendation="No immediate buyer action required.",
            confidence=0.75,
        )
