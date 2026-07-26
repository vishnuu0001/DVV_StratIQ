# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — csm_backend/app/models (transition.py)
# Date: 2026-05-20
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict


class TransitionCostRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tower: str
    addressable_spend: Decimal
    one_time_transition_cost_pct: Decimal
    transition_cost: Decimal
    duration_months: Decimal
    monthly_transition_cost: Decimal
    notes: str = ""


class TransitionCostResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    records: List[TransitionCostRecord]
    total_transition_cost: Decimal
    total_transition_cost_fmt: str
    duration_months: Decimal
    monthly_avg_cost: Decimal
    calculation_audit: Dict[str, Any] = {}
