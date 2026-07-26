# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — csm_backend/app/services (sheet_normalizer_service.py)
# Date: 2026-06-14
# ---------------------------------------------------------------------------
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.models.workbook import SheetInfo


class SheetNormalizerService:
    """Inspect raw sheet data and produce SheetInfo metadata."""

    # Function: get_sheet_infos
    def get_sheet_infos(self, raw_sheets: Dict[str, List[List[Any]]]) -> List[SheetInfo]:
        result: List[SheetInfo] = []
        for name, rows in raw_sheets.items():
            # Filter non-empty rows
            non_empty_rows = [r for r in rows if any(c is not None for c in r)]
            max_cols = max((len(r) for r in non_empty_rows), default=0)
            result.append(
                SheetInfo(
                    name=name,
                    row_count=len(non_empty_rows),
                    column_count=max_cols,
                    has_data=len(non_empty_rows) > 1,
                )
            )
        return result

    # Function: get_sheet_info
    def get_sheet_info(self, name: str, rows: List[List[Any]]) -> SheetInfo:
        non_empty = [r for r in rows if any(c is not None for c in r)]
        max_cols = max((len(r) for r in non_empty), default=0)
        return SheetInfo(
            name=name,
            row_count=len(non_empty),
            column_count=max_cols,
            has_data=len(non_empty) > 1,
        )
