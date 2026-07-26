# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — backend/app/csm/services (input_assumption_service.py)
# Date: 2025-10-30
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict

from app.csm.models.inputs import InputAssumptions, DerivedInputs


class InputAssumptionService:
    """Compute derived inputs from parsed InputAssumptions."""

    # Function: calculate_derived_inputs
    def calculate_derived_inputs(self, inputs: InputAssumptions) -> DerivedInputs:
        total_tech = inputs.total_technology_spend
        third_party = inputs.total_third_party_spend
        talent_spend = inputs.external_talent_labor_spend
        internal_pct = inputs.internal_labor_pct

        calculated_internal_labor = (total_tech * internal_pct).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if total_tech != Decimal("0"):
            external_spend_pct = (third_party / total_tech).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
        else:
            external_spend_pct = Decimal("0")

        if third_party != Decimal("0"):
            talent_spend_pct = (talent_spend / third_party).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
        else:
            talent_spend_pct = Decimal("0")

        return DerivedInputs(
            calculated_internal_labor=calculated_internal_labor,
            external_spend_pct_of_total_tech_spend=external_spend_pct,
            talent_spend_pct_of_third_party_spend=talent_spend_pct,
        )

    # Function: audit
    def audit(self, inputs: InputAssumptions, derived: DerivedInputs) -> Dict[str, Any]:
        return {
            "service": "InputAssumptionService",
            "formulas": [
                {
                    "name": "calculated_internal_labor",
                    "expression": "total_technology_spend × internal_labor_pct",
                    "inputs": {
                        "total_technology_spend": str(inputs.total_technology_spend),
                        "internal_labor_pct": str(inputs.internal_labor_pct),
                    },
                    "result": str(derived.calculated_internal_labor),
                },
                {
                    "name": "external_spend_pct_of_total_tech_spend",
                    "expression": "total_third_party_spend / total_technology_spend",
                    "inputs": {
                        "total_third_party_spend": str(inputs.total_third_party_spend),
                        "total_technology_spend": str(inputs.total_technology_spend),
                    },
                    "result": str(derived.external_spend_pct_of_total_tech_spend),
                },
                {
                    "name": "talent_spend_pct_of_third_party_spend",
                    "expression": "external_talent_labor_spend / total_third_party_spend",
                    "inputs": {
                        "external_talent_labor_spend": str(inputs.external_talent_labor_spend),
                        "total_third_party_spend": str(inputs.total_third_party_spend),
                    },
                    "result": str(derived.talent_spend_pct_of_third_party_spend),
                },
            ],
        }
