# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — csm_backend/app/api (routes_scenarios.py)
# Date: 2026-01-14
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict

from fastapi import APIRouter

from app import store
from app.core.exceptions import WorkbookNotFoundError
from app.models.scenario import ScenarioRequest, ScenarioResult
from app.models.tower_model import TowerParam
from app.services.tower_consolidation_service import TowerConsolidationService
from app.services.savings_summary_service import SavingsSummaryService
from app.services.executive_dashboard_service import ExecutiveDashboardService

router = APIRouter()


# Function: _get_or_404
def _get_or_404(workbook_id: str) -> Dict[str, Any]:
    data = store.get(workbook_id)
    if data is None:
        raise WorkbookNotFoundError(workbook_id)
    return data


# Function: run_scenario
@router.post("/csm/workbooks/{workbook_id}/scenarios/run", response_model=ScenarioResult)
def run_scenario(workbook_id: str, req: ScenarioRequest) -> ScenarioResult:
    """Run a what-if scenario without modifying stored workbook data."""
    data = _get_or_404(workbook_id)

    inputs = data["inputs"]
    vendor_records = data["vendor_records"]
    tower_params: list[TowerParam] = data["tower_params"]

    # Convert overrides to Decimal
    scope_overrides: Dict[str, Decimal] = {
        k: Decimal(str(v)) for k, v in req.tower_scope_overrides.items()
    }

    tower_svc = TowerConsolidationService()
    scenario_result = tower_svc.calculate_with_overrides(
        vendor_records=vendor_records,
        inputs=inputs,
        tower_params=tower_params,
        rate_compression_pct=Decimal(str(req.rate_compression_pct)),
        productivity_improvement_pct=Decimal(str(req.productivity_improvement_pct)),
        transition_cost_pct=Decimal(str(req.transition_cost_pct)),
        tower_scope_overrides=scope_overrides,
    )

    savings_svc = SavingsSummaryService()
    summary = savings_svc.summarise(scenario_result)

    # Compare vs base case
    base_totals = data["tower_result"].totals
    scenario_totals = scenario_result.totals

    # Function: _diff
    def _diff(scenario_val: Decimal, base_val: Decimal) -> str:
        return str((scenario_val - base_val).quantize(Decimal("0.01")))

    vs_base = {
        "gross_savings_delta": _diff(scenario_totals.gross_annual_savings, base_totals.gross_annual_savings),
        "transition_cost_delta": _diff(scenario_totals.transition_cost, base_totals.transition_cost),
        "net_year_1_delta": _diff(scenario_totals.net_year_1_savings, base_totals.net_year_1_savings),
        "run_rate_delta": _diff(scenario_totals.run_rate_annual_savings, base_totals.run_rate_annual_savings),
    }

    tower_rows_list = [r.model_dump(mode="json") for r in scenario_result.rows]
    totals_dict = scenario_result.totals.model_dump(mode="json")

    kpis_dict = {
        "gross_annual_savings": str(scenario_totals.gross_annual_savings),
        "transition_cost": str(scenario_totals.transition_cost),
        "net_year_1_savings": str(scenario_totals.net_year_1_savings),
        "run_rate_annual_savings": str(scenario_totals.run_rate_annual_savings),
    }

    return ScenarioResult(
        scenario_name=req.scenario_name,
        tower_rows=tower_rows_list,
        totals=totals_dict,
        kpis=kpis_dict,
        vs_base_case=vs_base,
        calculation_audit=scenario_result.calculation_audit,
    )
