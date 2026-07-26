# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — backend/app/csm/services (transition_cost_service.py)
# Date: 2025-10-08
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List

from app.csm.models.inputs import InputAssumptions
from app.csm.models.tower_model import TowerSavingsRow
from app.csm.models.transition import TransitionCostRecord, TransitionCostResult


# Function: _fmt_currency
def _fmt_currency(value: Decimal) -> str:
    millions = value / Decimal("1000000")
    return f"${millions.quantize(Decimal('0.001')).normalize()}M"


class TransitionCostService:
    """Break down transition costs per tower."""

    # Function: calculate
    def calculate(
        self,
        tower_rows: List[TowerSavingsRow],
        inputs: InputAssumptions,
    ) -> TransitionCostResult:
        records: List[TransitionCostRecord] = []
        duration = inputs.default_transition_duration_months

        for row in tower_rows:
            if row.tower == "TOTAL":
                continue
            monthly = (
                row.transition_cost / duration
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if duration else Decimal("0")

            records.append(
                TransitionCostRecord(
                    tower=row.tower,
                    addressable_spend=row.addressable_spend,
                    one_time_transition_cost_pct=inputs.one_time_transition_cost_pct,
                    transition_cost=row.transition_cost,
                    duration_months=duration,
                    monthly_transition_cost=monthly,
                    notes=f"Addressable × {inputs.one_time_transition_cost_pct * 100:.0f}%",
                )
            )

        total = sum((r.transition_cost for r in records), Decimal("0"))
        monthly_avg = (total / duration).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if duration else Decimal("0")

        audit: Dict[str, Any] = {
            "service": "TransitionCostService",
            "formula": "addressable_spend × one_time_transition_cost_pct",
            "one_time_transition_cost_pct": str(inputs.one_time_transition_cost_pct),
            "duration_months": str(duration),
            "total_transition_cost": str(total),
        }

        return TransitionCostResult(
            records=records,
            total_transition_cost=total,
            total_transition_cost_fmt=_fmt_currency(total),
            duration_months=duration,
            monthly_avg_cost=monthly_avg,
            calculation_audit=audit,
        )
