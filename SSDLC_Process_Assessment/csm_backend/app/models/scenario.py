# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — csm_backend/app/models (scenario.py)
# Date: 2025-11-02
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class ScenarioRequest(BaseModel):
    scenario_name: str
    rate_compression_pct: float
    productivity_improvement_pct: float
    transition_cost_pct: float
    tower_scope_overrides: Dict[str, float] = {}


class ScenarioResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_name: str
    tower_rows: List[Dict[str, Any]]
    totals: Dict[str, Any]
    kpis: Dict[str, Any]
    vs_base_case: Dict[str, Any]
    calculation_audit: Dict[str, Any]
