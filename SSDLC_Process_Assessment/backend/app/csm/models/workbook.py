# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — backend/app/csm/models (workbook.py)
# Date: 2025-11-29
# ---------------------------------------------------------------------------
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class SheetInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    row_count: int
    column_count: int
    has_data: bool


class WorkbookMetadata(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    workbook_id: str
    filename: str
    sheet_count: int
    sheets: List[SheetInfo]


class WorkbookUploadResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    workbook_id: str
    filename: str
    status: str
    sheet_count: int
    sheets: List[SheetInfo]
    validation: List[str]
    message: str
