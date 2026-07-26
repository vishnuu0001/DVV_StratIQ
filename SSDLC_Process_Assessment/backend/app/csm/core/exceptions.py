# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — backend/app/csm/core (exceptions.py)
# Date: 2025-07-12
# ---------------------------------------------------------------------------
from __future__ import annotations

from fastapi import HTTPException, status


class WorkbookNotFoundError(HTTPException):
    # Function: __init__
    def __init__(self, workbook_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workbook '{workbook_id}' not found. Please upload a workbook first.",
        )


class InvalidFileTypeError(HTTPException):
    # Function: __init__
    def __init__(self, filename: str) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid file type for '{filename}'. Only .xlsx files are accepted.",
        )


class WorkbookParseError(HTTPException):
    # Function: __init__
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Workbook parse error: {detail}",
        )


class CalculationError(Exception):
    # Function: __init__
    def __init__(self, service: str, detail: str) -> None:
        self.service = service
        super().__init__(f"[{service}] {detail}")
