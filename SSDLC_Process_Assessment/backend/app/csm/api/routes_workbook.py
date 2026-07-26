# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — backend/app/csm/api (routes_workbook.py)
# Date: 2026-02-26
# ---------------------------------------------------------------------------
from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.csm import store
from app.csm.core.exceptions import WorkbookNotFoundError

router = APIRouter()


# Function: _get_or_404
def _get_or_404(workbook_id: str) -> Dict[str, Any]:
    data = store.get(workbook_id)
    if data is None:
        raise WorkbookNotFoundError(workbook_id)
    return data


# Function: list_workbooks
@router.get("/csm/workbooks")
def list_workbooks() -> Dict[str, Any]:
    """List all workbook IDs currently in the store."""
    ids = store.list_ids()
    return {"workbook_ids": ids, "count": len(ids)}


# Function: get_workbook_metadata
@router.get("/csm/workbooks/{workbook_id}/metadata")
def get_workbook_metadata(workbook_id: str) -> Dict[str, Any]:
    """Return metadata for a stored workbook."""
    data = _get_or_404(workbook_id)
    return {
        "workbook_id": workbook_id,
        "filename": data.get("filename", ""),
        "sheet_count": len(data.get("sheet_infos", [])),
        "sheets": [s.model_dump() for s in data.get("sheet_infos", [])],
        "vendor_record_count": len(data.get("vendor_records", [])),
        "validation": data.get("validation", []),
    }


# Function: delete_workbook
@router.delete("/csm/workbooks/{workbook_id}")
def delete_workbook(workbook_id: str) -> Dict[str, Any]:
    """Remove a workbook from the store."""
    _get_or_404(workbook_id)
    store.delete(workbook_id)
    return {"workbook_id": workbook_id, "status": "deleted"}
