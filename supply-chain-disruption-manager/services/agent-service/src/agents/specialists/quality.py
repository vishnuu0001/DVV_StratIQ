# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Quality specialist agent.
# Date: 2025-07-13
# ---------------------------------------------------------------------------
"""Quality specialist agent."""
from __future__ import annotations

from agents.specialists.base import BaseSpecialist, SpecialistResponse
from agents.tools.qms import (
    qms_inspection_create,
    qms_ncr_raise,
    qms_disposition_set,
    qms_capa_create,
)

_IN_SCOPE_TYPES = {"quality_rejection", "grn_shortage", "warehouse_exception"}


class QualitySpecialist(BaseSpecialist):
    name = "quality-agent"
    role = "quality"
    domain = "quality"
    tools = ["qms_inspection_create", "qms_ncr_raise", "qms_disposition_set", "qms_capa_create"]

    # Function: _in_scope
    def _in_scope(self, brief: dict) -> bool:
        return brief.get("disruption_type", "") in _IN_SCOPE_TYPES

    # Function: _mock_run
    async def _mock_run(self, brief: dict) -> SpecialistResponse:
        disruption_type = brief.get("disruption_type", "quality_rejection")
        payload = brief.get("source_event", {}).get("payload", {})
        batch_id = payload.get("batch_id", "BATCH-2026-001")
        material_id = payload.get("material_id", "MAT-RAW-001")
        rejection_reason = payload.get("rejection_reason", "dimensional out of spec")
        qty_rejected = payload.get("qty_rejected", 200)
        supplier_id = payload.get("supplier_id", "SUP-001")

        actions = []

        if disruption_type == "quality_rejection":
            # Create inspection record
            insp = await qms_inspection_create(batch_id, material_id, qty_rejected, "incoming")
            actions.append({
                "tool": "qms_inspection_create",
                "args": {"batch_id": batch_id, "material_id": material_id, "qty": qty_rejected, "type": "incoming"},
                "result": insp,
            })

            # Raise NCR
            ncr = await qms_ncr_raise(batch_id, supplier_id, rejection_reason, qty_rejected)
            actions.append({
                "tool": "qms_ncr_raise",
                "args": {"batch_id": batch_id, "supplier_id": supplier_id, "reason": rejection_reason, "qty": qty_rejected},
                "result": ncr,
            })

            # Set disposition to RETURN
            disp = await qms_disposition_set(batch_id, "RETURN", f"Batch failed QC: {rejection_reason}")
            actions.append({
                "tool": "qms_disposition_set",
                "args": {"batch_id": batch_id, "disposition": "RETURN", "notes": rejection_reason},
                "result": disp,
            })

            # Open CAPA
            capa = await qms_capa_create(ncr["ncr_id"], supplier_id, "CORRECTIVE", "Supplier corrective action required")
            actions.append({
                "tool": "qms_capa_create",
                "args": {"ncr_id": ncr["ncr_id"], "supplier_id": supplier_id, "type": "CORRECTIVE"},
                "result": capa,
            })

            return SpecialistResponse(
                agent_name=self.name,
                status="completed",
                actions_taken=actions,
                findings=(
                    f"Batch {batch_id} ({qty_rejected} units of {material_id}) rejected — {rejection_reason}. "
                    f"NCR {ncr['ncr_id']} raised. Disposition: RETURN to supplier {supplier_id}. "
                    f"CAPA {capa['capa_id']} opened."
                ),
                blockers=[],
                recommendation=(
                    f"Return batch to {supplier_id}. "
                    "Request replacement shipment with corrected spec. "
                    "CAPA closure required within 30 days."
                ),
                confidence=0.94,
                requires_human_approval=True,
                irreversible_actions=[f"Return shipment to {supplier_id}", f"Raise NCR {ncr['ncr_id']}"],
            )

        return SpecialistResponse(
            agent_name=self.name,
            status="completed",
            actions_taken=actions,
            findings=f"Quality review completed for {disruption_type}.",
            recommendation="No quality action required.",
            confidence=0.80,
        )
