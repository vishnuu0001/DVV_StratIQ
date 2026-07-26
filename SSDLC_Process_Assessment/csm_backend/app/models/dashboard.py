# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — csm_backend/app/models (dashboard.py)
# Date: 2026-03-21
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class ExecutiveDashboardKpis(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_third_party_spend: Decimal
    total_third_party_spend_fmt: str
    external_talent_spend: Decimal
    external_talent_spend_fmt: str
    addressable_spend: Decimal
    addressable_spend_fmt: str
    gross_annual_capacity: Decimal
    gross_annual_capacity_fmt: str
    transition_cost: Decimal
    transition_cost_fmt: str
    net_year_1_savings: Decimal
    net_year_1_savings_fmt: str
    run_rate_annual_savings: Decimal
    run_rate_annual_savings_fmt: str
    roi_pct: Decimal
    roi_pct_fmt: str


class ExecutiveStoryBullet(BaseModel):
    bullet: str
    category: str = "insight"


class DashboardResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    workbook_id: str
    kpis: ExecutiveDashboardKpis
    tower_summary: List[Dict[str, Any]]
    spend_by_category: List[Dict[str, Any]]
    top_vendors: List[Dict[str, Any]]
    executive_story: List[ExecutiveStoryBullet]
    calculation_audit: Dict[str, Any]
    validation: List[str]
