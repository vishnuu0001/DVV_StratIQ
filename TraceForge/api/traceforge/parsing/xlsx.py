# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §4.2 .xlsx parser: openpyxl, one chunk per logical table region, header-aware.
# Date: 2026-04-27
# ---------------------------------------------------------------------------
"""§4.2 .xlsx parser: openpyxl, one chunk per logical table region, header-aware."""
from __future__ import annotations

import openpyxl

from traceforge.parsing.common import ParsedBlock, ParsedDocument


# Function: _row_text
def _row_text(row: tuple, headers: list[str] | None) -> str:
    values = [str(cell) for cell in row if cell is not None]
    if not values:
        return ""
    if headers and len(headers) == len(row):
        return " | ".join(f"{h}: {cell}" for h, cell in zip(headers, row) if cell is not None)
    return " | ".join(values)


# Function: parse_xlsx
def parse_xlsx(path: str) -> ParsedDocument:
    workbook = openpyxl.load_workbook(path, data_only=True, read_only=True)
    blocks: list[ParsedBlock] = []
    cursor = 0

    for sheet in workbook.worksheets:
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            continue
        headers = [str(c) for c in rows[0]] if any(c is not None for c in rows[0]) else None
        data_rows = rows[1:] if headers else rows
        start_row = 2 if headers else 1

        # One chunk per ~30-row region so a huge sheet doesn't become one giant chunk,
        # never splitting a single row (spec §4.3: "never split a table row").
        region_size = 30
        for i in range(0, len(data_rows), region_size):
            region = data_rows[i:i + region_size]
            lines = [_row_text(row, headers) for row in region]
            lines = [line for line in lines if line]
            if not lines:
                continue
            text = f"Sheet: {sheet.title}\n" + "\n".join(lines)
            start = cursor
            end = start + len(text)
            row_start = start_row + i
            row_end = row_start + len(region) - 1
            blocks.append(ParsedBlock(
                text=text, section_path=sheet.title, char_start=start, char_end=end,
                sheet=sheet.title, row_range=[row_start, row_end],
            ))
            cursor = end + 1

    workbook.close()
    return ParsedDocument(blocks=blocks)
