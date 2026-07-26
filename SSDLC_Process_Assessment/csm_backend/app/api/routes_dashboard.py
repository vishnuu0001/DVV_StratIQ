# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — csm_backend/app/api (routes_dashboard.py)
# Date: 2026-05-03
# ---------------------------------------------------------------------------
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from app import store
from app.core.exceptions import WorkbookNotFoundError
from app.services.executive_dashboard_service import ExecutiveDashboardService

router = APIRouter()


# Function: _get_or_404
def _get_or_404(workbook_id: str) -> Dict[str, Any]:
    data = store.get(workbook_id)
    if data is None:
        raise WorkbookNotFoundError(workbook_id)
    return data


# Function: get_dashboard
@router.get("/csm/workbooks/{workbook_id}/dashboard")
def get_dashboard(workbook_id: str) -> Dict[str, Any]:
    """Return the full executive dashboard."""
    data = _get_or_404(workbook_id)

    # Rebuild dashboard so workbook_id is correct (was "pending" at upload time)
    svc = ExecutiveDashboardService()
    dashboard = svc.build(
        workbook_id=workbook_id,
        vendor_records=data["vendor_records"],
        tower_result=data["tower_result"],
        inputs=data["inputs"],
        validation=data["validation"],
    )

    # Enrich with extra sections
    result = dashboard.model_dump(mode="json")
    result["savings_summary"] = data["savings_summary"]
    result["vendor_landscape"] = data["landscape"]
    result["techm_growth"] = data["techm"]
    result["transformation_capacity"] = data["capacity"]
    result["vendor_heatmap"] = data["heatmap"]
    result["operating_model"] = data["operating_model"]
    result["roadmap"] = data["roadmap"]
    return result
