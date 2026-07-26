# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: QMS (Quality Management System) tool mocks.
# Date: 2026-05-30
# ---------------------------------------------------------------------------
"""QMS (Quality Management System) tool mocks."""
from __future__ import annotations

import asyncio
import uuid


# Function: qms_inspection_create
async def qms_inspection_create(
    batch_id: str,
    material_id: str,
    qty: float,
    inspection_type: str,
) -> dict:
    """Create an inspection record in QMS."""
    await asyncio.sleep(0)
    insp_id = f"INS-{str(uuid.uuid4())[:8].upper()}"
    return {
        "inspection_id": insp_id,
        "batch_id": batch_id,
        "material_id": material_id,
        "qty_inspected": qty,
        "inspection_type": inspection_type,
        "status": "OPEN",
        "assigned_to": "QC-TEAM-A",
        "created_at": "2026-06-27T09:00:00Z",
    }


# Function: qms_ncr_raise
async def qms_ncr_raise(
    batch_id: str,
    supplier_id: str,
    rejection_reason: str,
    qty_rejected: float,
) -> dict:
    """Raise a Non-Conformance Report."""
    await asyncio.sleep(0)
    ncr_id = f"NCR-{str(uuid.uuid4())[:8].upper()}"
    return {
        "ncr_id": ncr_id,
        "batch_id": batch_id,
        "supplier_id": supplier_id,
        "rejection_reason": rejection_reason,
        "qty_rejected": qty_rejected,
        "severity": "MAJOR",
        "status": "OPEN",
        "raised_at": "2026-06-27T09:15:00Z",
        "due_date": "2026-07-07T17:00:00Z",
    }


# Function: qms_disposition_set
async def qms_disposition_set(batch_id: str, disposition: str, notes: str = "") -> dict:
    """Set disposition for a batch (RETURN / SCRAP / USE_AS_IS / REWORK)."""
    await asyncio.sleep(0)
    return {
        "batch_id": batch_id,
        "disposition": disposition,
        "notes": notes,
        "set_at": "2026-06-27T09:30:00Z",
        "approved_by": "QC-MANAGER",
        "status": "CONFIRMED",
    }


# Function: qms_capa_create
async def qms_capa_create(
    ncr_id: str,
    supplier_id: str,
    capa_type: str,
    description: str,
) -> dict:
    """Create a CAPA (Corrective and Preventive Action)."""
    await asyncio.sleep(0)
    capa_id = f"CAPA-{str(uuid.uuid4())[:8].upper()}"
    return {
        "capa_id": capa_id,
        "ncr_id": ncr_id,
        "supplier_id": supplier_id,
        "capa_type": capa_type,
        "description": description,
        "status": "OPEN",
        "created_at": "2026-06-27T09:45:00Z",
        "due_date": "2026-07-27T17:00:00Z",
    }


# Function: qms_inspection_result_get
async def qms_inspection_result_get(inspection_id: str) -> dict:
    """Get inspection results."""
    await asyncio.sleep(0)
    return {
        "inspection_id": inspection_id,
        "result": "FAIL",
        "defects_found": [
            {"defect_type": "dimensional", "description": "Width out of spec by 2mm", "severity": "MAJOR"},
            {"defect_type": "surface", "description": "Surface roughness exceeds Ra 1.6", "severity": "MINOR"},
        ],
        "qty_accepted": 0,
        "qty_rejected": 200,
        "completed_at": "2026-06-27T10:30:00Z",
    }


# Function: qms_supplier_scorecard
async def qms_supplier_scorecard(supplier_id: str) -> dict:
    """Get supplier quality scorecard."""
    await asyncio.sleep(0)
    return {
        "supplier_id": supplier_id,
        "overall_score": 72,
        "quality_score": 68,
        "delivery_score": 78,
        "ncr_count_ytd": 3,
        "rejection_rate_pct": 4.2,
        "last_audit": "2025-11-15",
        "risk_level": "MEDIUM",
    }
