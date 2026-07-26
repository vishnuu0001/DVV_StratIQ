# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §5.1 Agent 5 — RTM (Excel, openpyxl). Every derived column is a live formula, never
# Date: 2026-04-07
# ---------------------------------------------------------------------------
"""§5.1 Agent 5 — RTM (Excel, openpyxl). Every derived column is a live formula, never
a hardcoded value — spec's own acceptance test: 'opening the RTM and deleting a row
causes all coverage percentages to recalculate correctly.'

One deviation from the spec's literal formula text, documented where it happens: the
Test Count column returns numeric 0 (not the string "GAP") when a requirement has no
test cases, so the downstream Coverage Status formula's `IF(K2=0, ...)` numeric
comparison actually fires — the spec's two example formulas don't compose correctly
taken 100% literally (a text "GAP" would make `K2=0` evaluate to FALSE in Excel,
silently skipping the "NO TESTS" branch). "GAP" as a concept is still surfaced, just
one level down in Coverage Status ("NO TESTS") rather than duplicated in Test Count.
"""
from __future__ import annotations

import uuid

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.db.models import (
    AuditEvent, Chunk, Requirement, SourceCitation, SourceDocument, TestCase, TestScript,
)

_HEADER_FILL = PatternFill(start_color="1F2937", end_color="1F2937", fill_type="solid")
_HEADER_FONT = Font(color="FFFFFF", bold=True)
_MAX_ROW_REF = 5000  # formula ranges are bounded, not whole-column, for perf while still comfortably covering real projects

_BRD_SECTION_BY_LEVEL = {
    "BUSINESS": "4. Business Requirements", "FUNCTIONAL": "5. Functional Requirements",
    "NON_FUNCTIONAL": "6. Non-Functional Requirements", "ASSUMPTION": "7. Assumptions & Dependencies",
    "CONSTRAINT": "7. Assumptions & Dependencies",
}


# Function: _style_header
def _style_header(ws, columns: list[str]) -> None:
    for i, col in enumerate(columns, start=1):
        cell = ws.cell(row=1, column=i, value=col)
        cell.fill = _HEADER_FILL
        cell.font = _HEADER_FONT
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(columns))}1"


# Function: _load_data
async def _load_data(session: AsyncSession, project_id: uuid.UUID):
    requirements = list((await session.execute(
        select(Requirement).where(Requirement.project_id == project_id).order_by(Requirement.req_id)
    )).scalars().all())
    test_cases = list((await session.execute(
        select(TestCase).where(TestCase.project_id == project_id).order_by(TestCase.tc_id)
    )).scalars().all())
    scripts = list((await session.execute(
        select(TestScript).where(TestScript.project_id == project_id).order_by(TestScript.ts_id)
    )).scalars().all())
    audit = list((await session.execute(
        select(AuditEvent).where(AuditEvent.project_id == project_id).order_by(AuditEvent.at)
    )).scalars().all())

    tc_by_id = {tc.id: tc for tc in test_cases}
    citations_by_req: dict[uuid.UUID, list[SourceCitation]] = {}
    for req in requirements:
        result = await session.execute(
            select(SourceCitation, Chunk, SourceDocument)
            .join(Chunk, SourceCitation.chunk_id == Chunk.id)
            .join(SourceDocument, Chunk.source_document_id == SourceDocument.id)
            .where(SourceCitation.requirement_id == req.id)
        )
        citations_by_req[req.id] = list(result.all())

    return requirements, test_cases, scripts, audit, tc_by_id, citations_by_req


# Function: _build_rtm_sheet
def _build_rtm_sheet(wb: Workbook, requirements: list[Requirement], citations_by_req: dict) -> None:
    ws = wb.active
    ws.title = "RTM"
    columns = ["REQ-ID", "Level", "Statement", "Priority", "EARS Pattern", "Ambiguity Score",
               "Source Document(s)", "Source Locator(s)", "BRD Section", "Test Case IDs", "Test Count",
               "Positive Count", "Negative Count", "Script IDs", "Script Count", "Coverage Status", "Approval Status"]
    _style_header(ws, columns)

    for row_i, req in enumerate(requirements, start=2):
        rows = citations_by_req.get(req.id, [])
        source_docs = ", ".join(sorted({sd.filename for _, _, sd in rows})) or "(none)"
        locators = "; ".join(f"{sd.filename}: {c.quoted_span[:40]}..." for c, _, sd in rows[:3]) or "(none)"

        ws.cell(row=row_i, column=1, value=req.req_id).hyperlink = "#Requirements!A1"
        ws.cell(row=row_i, column=2, value=req.level)
        ws.cell(row=row_i, column=3, value=req.statement)
        ws.cell(row=row_i, column=4, value=req.priority)
        ws.cell(row=row_i, column=5, value=req.ears_pattern)
        ws.cell(row=row_i, column=6, value=round(req.ambiguity_score, 2))
        ws.cell(row=row_i, column=7, value=source_docs)
        ws.cell(row=row_i, column=8, value=locators)
        ws.cell(row=row_i, column=9, value=_BRD_SECTION_BY_LEVEL.get(req.level, ""))
        ws.cell(row=row_i, column=10,
                value=f'=TEXTJOIN(", ",TRUE,IF(TestCases!$B$2:$B${_MAX_ROW_REF}=A{row_i},TestCases!$A$2:$A${_MAX_ROW_REF},""))')
        ws.cell(row=row_i, column=11, value=f'=IF(J{row_i}="",0,COUNTIF(TestCases!$B$2:$B${_MAX_ROW_REF},A{row_i}))')
        ws.cell(row=row_i, column=12, value=f'=COUNTIFS(TestCases!$B$2:$B${_MAX_ROW_REF},A{row_i},TestCases!$C$2:$C${_MAX_ROW_REF},"POSITIVE")')
        ws.cell(row=row_i, column=13, value=f'=COUNTIFS(TestCases!$B$2:$B${_MAX_ROW_REF},A{row_i},TestCases!$C$2:$C${_MAX_ROW_REF},"NEGATIVE")')
        ws.cell(row=row_i, column=14,
                value=f'=TEXTJOIN(", ",TRUE,IF(Scripts!$C$2:$C${_MAX_ROW_REF}=A{row_i},Scripts!$A$2:$A${_MAX_ROW_REF},""))')
        ws.cell(row=row_i, column=15, value=f'=IF(N{row_i}="",0,COUNTIF(Scripts!$C$2:$C${_MAX_ROW_REF},A{row_i}))')
        ws.cell(row=row_i, column=16,
                value=f'=IF(K{row_i}=0,"NO TESTS",IF(M{row_i}=0,"NO NEGATIVE",IF(O{row_i}=0,"NOT AUTOMATED","COVERED")))')
        ws.cell(row=row_i, column=17, value=req.status)

    last_row = max(2, len(requirements) + 1)
    ws.conditional_formatting.add(
        f"F2:F{last_row}", CellIsRule(operator="lessThan", formula=["0.2"], fill=PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid"))
    )
    ws.conditional_formatting.add(
        f"F2:F{last_row}", CellIsRule(operator="between", formula=["0.2", "0.4"], fill=PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid"))
    )
    ws.conditional_formatting.add(
        f"F2:F{last_row}", CellIsRule(operator="greaterThan", formula=["0.4"], fill=PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"))
    )
    for i, width in enumerate([12, 14, 60, 8, 16, 10, 30, 40, 28, 20, 10, 10, 10, 20, 10, 16, 24], start=1):
        ws.column_dimensions[get_column_letter(i)].width = width


# Function: _build_testcases_sheet
def _build_testcases_sheet(wb: Workbook, test_cases: list[TestCase], req_id_by_uuid: dict) -> None:
    ws = wb.create_sheet("TestCases")
    columns = ["TC-ID", "REQ-ID", "Test Type", "Test Level", "Priority", "Title", "Status", "Steps (count)"]
    _style_header(ws, columns)
    for row_i, tc in enumerate(test_cases, start=2):
        ws.cell(row=row_i, column=1, value=tc.tc_id)
        ws.cell(row=row_i, column=2, value=req_id_by_uuid.get(tc.requirement_id, ""))
        ws.cell(row=row_i, column=3, value=tc.test_type)
        ws.cell(row=row_i, column=4, value=tc.test_level)
        ws.cell(row=row_i, column=5, value=tc.priority)
        ws.cell(row=row_i, column=6, value=tc.title)
        ws.cell(row=row_i, column=7, value=tc.status)
        ws.cell(row=row_i, column=8, value=len(tc.steps or []))
    for i, width in enumerate([12, 12, 14, 12, 8, 50, 12, 14], start=1):
        ws.column_dimensions[get_column_letter(i)].width = width


# Function: _build_scripts_sheet
def _build_scripts_sheet(wb: Workbook, scripts: list[TestScript], tc_by_id: dict, req_id_by_uuid: dict) -> None:
    ws = wb.create_sheet("Scripts")
    columns = ["TS-ID", "TC-ID", "REQ-ID", "Target", "File Path", "Compiles", "Status"]
    _style_header(ws, columns)
    for row_i, ts in enumerate(scripts, start=2):
        tc = tc_by_id.get(ts.test_case_id)
        ws.cell(row=row_i, column=1, value=ts.ts_id)
        ws.cell(row=row_i, column=2, value=tc.tc_id if tc else "")
        ws.cell(row=row_i, column=3, value=req_id_by_uuid.get(tc.requirement_id, "") if tc else "")
        ws.cell(row=row_i, column=4, value=ts.target)
        ws.cell(row=row_i, column=5, value=ts.file_path)
        ws.cell(row=row_i, column=6, value="Yes" if ts.compiles else ("No" if ts.compiles is False else "Not validated"))
        ws.cell(row=row_i, column=7, value=ts.status)
    for i, width in enumerate([12, 12, 12, 16, 40, 12, 12], start=1):
        ws.column_dimensions[get_column_letter(i)].width = width


# Function: _build_coverage_summary_sheet
def _build_coverage_summary_sheet(wb: Workbook, requirements: list[Requirement]) -> None:
    ws = wb.create_sheet("Coverage Summary")
    ws.cell(row=1, column=1, value="Coverage by Level").font = Font(bold=True, size=13)
    columns = ["Level", "Total", "Covered", "Coverage %"]
    for i, col in enumerate(columns, start=1):
        ws.cell(row=3, column=i, value=col).font = Font(bold=True)

    levels = ["BUSINESS", "FUNCTIONAL", "NON_FUNCTIONAL", "ASSUMPTION", "CONSTRAINT"]
    last_rtm_row = max(2, len(requirements) + 1)
    for row_i, level in enumerate(levels, start=4):
        ws.cell(row=row_i, column=1, value=level)
        ws.cell(row=row_i, column=2, value=f'=COUNTIF(RTM!$B$2:$B${last_rtm_row},A{row_i})')
        ws.cell(row=row_i, column=3, value=f'=COUNTIFS(RTM!$B$2:$B${last_rtm_row},A{row_i},RTM!$P$2:$P${last_rtm_row},"COVERED")')
        ws.cell(row=row_i, column=4, value=f'=IF(B{row_i}=0,"N/A",C{row_i}/B{row_i})')
        ws.cell(row=row_i, column=4).number_format = "0%"

    summary_row = 4 + len(levels) + 1
    ws.cell(row=summary_row, column=1, value="TOTAL").font = Font(bold=True)
    ws.cell(row=summary_row, column=2, value=f'=SUM(B4:B{3 + len(levels)})')
    ws.cell(row=summary_row, column=3, value=f'=SUM(C4:C{3 + len(levels)})')
    ws.cell(row=summary_row, column=4, value=f'=IF(B{summary_row}=0,"N/A",C{summary_row}/B{summary_row})')
    ws.cell(row=summary_row, column=4).number_format = "0%"

    ambiguity_row = summary_row + 2
    ws.cell(row=ambiguity_row, column=1, value="Ambiguity distribution (score > 0.4)").font = Font(bold=True)
    ws.cell(row=ambiguity_row + 1, column=1, value="Blocked requirements")
    ws.cell(row=ambiguity_row + 1, column=2, value=f'=COUNTIF(RTM!$F$2:$F${last_rtm_row},">0.4")')

    for i, width in enumerate([16, 10, 10, 12], start=1):
        ws.column_dimensions[get_column_letter(i)].width = width


# Function: _build_gaps_sheet
def _build_gaps_sheet(wb: Workbook, requirements: list[Requirement]) -> None:
    ws = wb.create_sheet("Gaps")
    ws.cell(row=1, column=1, value="Requirements with Coverage Status <> COVERED — live view (Excel 365 FILTER)").font = Font(bold=True)
    last_rtm_row = max(2, len(requirements) + 1)
    ws.cell(row=2, column=1, value=f'=IFERROR(FILTER(RTM!A2:Q{last_rtm_row},RTM!P2:P{last_rtm_row}<>"COVERED"),"No gaps.")')
    ws.column_dimensions["A"].width = 100


# Function: _build_audit_sheet
def _build_audit_sheet(wb: Workbook, audit_events: list[AuditEvent]) -> None:
    ws = wb.create_sheet("Audit")
    columns = ["At", "Actor", "Action", "Entity Type", "Entity ID", "Rationale/Detail"]
    _style_header(ws, columns)
    for row_i, event in enumerate(audit_events, start=2):
        detail = ""
        if event.after and isinstance(event.after, dict):
            detail = str(event.after.get("rationale") or event.after)[:200]
        ws.cell(row=row_i, column=1, value=event.at.strftime("%Y-%m-%d %H:%M:%S") if event.at else "")
        ws.cell(row=row_i, column=2, value=event.actor)
        ws.cell(row=row_i, column=3, value=event.action)
        ws.cell(row=row_i, column=4, value=event.entity_type)
        ws.cell(row=row_i, column=5, value=event.entity_id)
        ws.cell(row=row_i, column=6, value=detail)
    for i, width in enumerate([20, 20, 24, 16, 14, 60], start=1):
        ws.column_dimensions[get_column_letter(i)].width = width


# Function: render_rtm_xlsx
async def render_rtm_xlsx(session: AsyncSession, project_id: uuid.UUID, output_path: str) -> None:
    requirements, test_cases, scripts, audit, tc_by_id, citations_by_req = await _load_data(session, project_id)
    req_id_by_uuid = {r.id: r.req_id for r in requirements}

    wb = Workbook()
    _build_rtm_sheet(wb, requirements, citations_by_req)
    _build_testcases_sheet(wb, test_cases, req_id_by_uuid)
    _build_scripts_sheet(wb, scripts, tc_by_id, req_id_by_uuid)
    _build_coverage_summary_sheet(wb, requirements)
    _build_gaps_sheet(wb, requirements)
    _build_audit_sheet(wb, audit)
    wb.save(output_path)
