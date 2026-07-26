# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — backend/app/csm/api (routes_calculations.py)
# Date: 2025-12-03
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict

from fastapi import APIRouter

from app.csm import store
from app.csm.core.exceptions import WorkbookNotFoundError
from app.csm.services.input_assumption_service import InputAssumptionService
from app.csm.services.savings_summary_service import SavingsSummaryService
from app.csm.services.transition_cost_service import TransitionCostService
from app.csm.services.vendor_landscape_service import VendorLandscapeService
from app.csm.services.techm_growth_service import TechMGrowthService
from app.csm.services.transformation_capacity_service import TransformationCapacityService
from app.csm.services.vendor_heatmap_service import VendorHeatmapService

router = APIRouter()


# Function: _get_or_404
def _get_or_404(workbook_id: str) -> Dict[str, Any]:
    data = store.get(workbook_id)
    if data is None:
        raise WorkbookNotFoundError(workbook_id)
    return data


# Function: get_full_audit
@router.get("/csm/workbooks/{workbook_id}/calculations")
def get_full_audit(workbook_id: str) -> Dict[str, Any]:
    """Return the full calculation audit for this workbook."""
    data = _get_or_404(workbook_id)
    return data["full_audit"]


# Function: get_inputs
@router.get("/csm/workbooks/{workbook_id}/calculations/inputs")
def get_inputs(workbook_id: str) -> Dict[str, Any]:
    """Return parsed inputs and derived inputs with audit trail."""
    data = _get_or_404(workbook_id)
    inputs = data["inputs"]
    derived = data["derived_inputs"]
    svc = InputAssumptionService()
    audit = svc.audit(inputs, derived)
    return {
        "inputs": inputs.model_dump(mode="json"),
        "derived_inputs": derived.model_dump(mode="json"),
        "calculation_audit": audit,
    }


# Function: get_tower_model
@router.get("/csm/workbooks/{workbook_id}/calculations/tower-model")
def get_tower_model(workbook_id: str) -> Dict[str, Any]:
    """Return tower model rows with per-row calculation audit."""
    data = _get_or_404(workbook_id)
    tower_result = data["tower_result"]
    rows = [r.model_dump(mode="json") for r in tower_result.rows]
    totals = tower_result.totals.model_dump(mode="json")
    return {
        "rows": rows,
        "totals": totals,
        "calculation_audit": tower_result.calculation_audit,
    }


# Function: get_savings_summary
@router.get("/csm/workbooks/{workbook_id}/calculations/savings-summary")
def get_savings_summary(workbook_id: str) -> Dict[str, Any]:
    """Return savings summary totals."""
    data = _get_or_404(workbook_id)
    return data["savings_summary"]


# Function: get_vendor_landscape
@router.get("/csm/workbooks/{workbook_id}/calculations/vendor-landscape")
def get_vendor_landscape(workbook_id: str) -> Dict[str, Any]:
    """Return vendor landscape analysis."""
    data = _get_or_404(workbook_id)
    return {
        "vendors": data["landscape"],
        "calculation_audit": data["landscape_audit"],
    }


# Function: get_techm_growth
@router.get("/csm/workbooks/{workbook_id}/calculations/techm-growth")
def get_techm_growth(workbook_id: str) -> Dict[str, Any]:
    """Return Tech Mahindra growth scenarios."""
    data = _get_or_404(workbook_id)
    return data["techm"]


# Function: get_transformation_capacity
@router.get("/csm/workbooks/{workbook_id}/calculations/transformation-capacity")
def get_transformation_capacity(workbook_id: str) -> Dict[str, Any]:
    """Return transformation capacity scenarios and reinvestment allocations."""
    data = _get_or_404(workbook_id)
    return data["capacity"]


# Function: get_vendor_heatmap
@router.get("/csm/workbooks/{workbook_id}/calculations/vendor-heatmap")
def get_vendor_heatmap(workbook_id: str) -> Dict[str, Any]:
    """Return vendor heatmap with scores and RAG status."""
    data = _get_or_404(workbook_id)
    return data["heatmap"]


# Function: get_transition_costs
@router.get("/csm/workbooks/{workbook_id}/calculations/transition-costs")
def get_transition_costs(workbook_id: str) -> Dict[str, Any]:
    """Return transition cost analysis per tower."""
    data = _get_or_404(workbook_id)
    transition_result = data["transition_result"]
    return transition_result.model_dump(mode="json")


# Function: get_operating_model
@router.get("/csm/workbooks/{workbook_id}/calculations/operating-model")
def get_operating_model(workbook_id: str) -> Dict[str, Any]:
    """Return operating model analysis."""
    data = _get_or_404(workbook_id)
    return data["operating_model"]


# Function: get_roadmap
@router.get("/csm/workbooks/{workbook_id}/calculations/roadmap")
def get_roadmap(workbook_id: str) -> Dict[str, Any]:
    """Return phased consolidation roadmap."""
    data = _get_or_404(workbook_id)
    return data["roadmap"]
