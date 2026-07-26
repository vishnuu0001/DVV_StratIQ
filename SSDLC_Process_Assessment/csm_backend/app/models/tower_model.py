# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — csm_backend/app/models (tower_model.py)
# Date: 2026-07-01
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, ConfigDict


class TowerParam(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tower: str
    consolidation_scope_pct: Decimal
    recommended_action: str
    notes: str = ""


class TowerSavingsRow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tower: str
    current_annual_spend: Decimal
    current_vendor_count: int
    consolidation_scope_pct: Decimal
    addressable_spend: Decimal
    productivity_savings: Decimal
    rate_savings: Decimal
    vendor_mgmt_overhead_savings: Decimal
    gross_annual_savings: Decimal
    transition_cost: Decimal
    net_year_1_savings: Decimal
    run_rate_annual_savings: Decimal
    calculation_audit: Dict[str, Any] = {}


class TowerModelResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    rows: List[TowerSavingsRow]
    totals: TowerSavingsRow
    calculation_audit: Dict[str, Any] = {}


DEFAULT_TOWER_PARAMS: List[TowerParam] = [
    TowerParam(tower="Applications",           consolidation_scope_pct=Decimal("0.75"), recommended_action="Consolidate",        notes=""),
    TowerParam(tower="Infrastructure",         consolidation_scope_pct=Decimal("0.75"), recommended_action="Consolidate",        notes=""),
    TowerParam(tower="Data & AI",              consolidation_scope_pct=Decimal("0.75"), recommended_action="Consolidate",        notes=""),
    TowerParam(tower="Workplace/Productivity", consolidation_scope_pct=Decimal("0.60"), recommended_action="Selective",          notes=""),
    TowerParam(tower="Cross-Tower Labor",      consolidation_scope_pct=Decimal("0.70"), recommended_action="Optimize",           notes=""),
    TowerParam(tower="Other",                  consolidation_scope_pct=Decimal("0.30"), recommended_action="Retain / Selective", notes=""),
]
