# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — csm_backend/app/models (inputs.py)
# Date: 2026-04-08
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class InputAssumptions(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # Column B fields
    total_technology_spend: Decimal
    direct_tech_opex: Decimal
    tech_capex: Decimal
    internal_labor_pct: Decimal
    external_talent_labor_spend: Decimal
    total_third_party_spend: Decimal
    vendor_management_overhead_pct: Decimal
    target_vendor_management_overhead_reduction_pct: Decimal
    default_rate_compression_pct: Decimal
    default_productivity_improvement_pct: Decimal
    default_transition_duration_months: Decimal

    # Column E fields
    scenario_name: str
    conservative_rate_compression_pct: Decimal
    base_rate_compression_pct: Decimal
    aggressive_rate_compression_pct: Decimal
    conservative_productivity_pct: Decimal
    base_productivity_pct: Decimal
    aggressive_productivity_pct: Decimal
    one_time_transition_cost_pct: Decimal


class DerivedInputs(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    calculated_internal_labor: Decimal
    external_spend_pct_of_total_tech_spend: Decimal
    talent_spend_pct_of_third_party_spend: Decimal
