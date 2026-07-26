# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Deterministic parser for the "FY 27 Plan Tracker" sheet of the MFG CTO
# Date: 2026-07-15
# ---------------------------------------------------------------------------
"""Deterministic parser for the "FY 27 Plan Tracker" sheet of the MFG CTO
Oppty Tracker workbook — parse once at upload time, never re-parse the xlsx
later (same philosophy as wave_deterministic.py's scope/categorization
parsers). No LLM involvement; this is pure, auditable data transformation.

Only the "FY 27 Plan Tracker" sheet is in scope — Accounts/Auto/Indus_Process/
EU Account list are explicitly out of scope."""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any

import pandas as pd

SHEET_NAME = "FY 27 Plan Tracker"
HEADER_ROW = 2  # 0-indexed — row 0 is a title banner, row 1 a pre-computed projection summary

# Canonical field -> normalized source column name (whitespace/newlines collapsed
# to single spaces before matching, since the real header has a trailing space on
# "Solution / Offering " and embedded newlines on the date/FY-total columns).
_COLUMN_MAP = {
    "region": "Region",
    "customer_group": "Customer Group",
    "sub_vertical": "Sub Vertical",
    "solution_offering": "Solution / Offering",
    "so_coe_leader": "SO/COE Leader",
    "crm_ref": "CRM Ref #",
    "opportunity_name": "Opportunity Name",
    "oppty_stage": "Oppty Stage",
    "start_date": "Start Date DD-MMM-YY",
    "oppty_owner": "Oppty Owner",
    "tcv_mn": "TCV $ Mn",
    "q1_mn": "Q1'27",
    "q2_mn": "Q2'27",
    "q3_mn": "Q3'27",
    "q4_mn": "Q4'27",
    "_fy27_check": "FY '27 $ Mn",  # cross-validation only, never stored
    "remarks": "Remarks",
    "hyperscaler": "Hyperscaler",
    "delivery_ibu": "Delivery IBU",
    "delivery_ibu_leader": "Delivery IBU Leader",
    "delivery_validation": "Delivery Validation Yes/No",
}
_REQUIRED_FIELDS = {"opportunity_name"}

# A CRM Ref # is only trustworthy as an upsert key if it looks like a real
# reference (has both letters and digits, or is reasonably long) — the one
# populated value observed in the real workbook ("1xxx") is an obvious
# placeholder, not a genuine CRM identifier.
_PLACEHOLDER_CRM_REF_PATTERN = re.compile(r"^1?x+$", re.IGNORECASE)


# Function: _normalize_column_name
def _normalize_column_name(col: Any) -> str:
    return re.sub(r"\s+", " ", str(col)).strip()


# Function: _clean_str
def _clean_str(value) -> str:
    """Some entirely-blank rows in the source sheet get every cell inferred as
    NaT (not NaN) by pandas, even for text columns — checked via pd.isna()
    first, not just a "nan" string filter, or a blank row's Opportunity Name
    silently becomes the literal string "NaT" instead of being skipped."""
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass  # some values (e.g. arrays) raise on isna() — fall through to str handling
    text = str(value).strip()
    return "" if text.lower() in ("nan", "nat") else text


# Function: _clean_float
def _clean_float(value) -> float:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


# Function: _clean_date
def _clean_date(value) -> str:
    """Normalize pandas Timestamp/NaT/string to an ISO YYYY-MM-DD string, matching
    the frontend's <input type="date"> — imported dates must round-trip through
    the same form as manually-created opportunities. NaT is checked via pd.isna()
    first, not isinstance(), since NaT can satisfy isinstance(value, datetime) in
    some pandas versions while still being a null value that can't strftime()."""
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass  # some values (e.g. arrays) raise on isna() — fall through to str handling
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.strftime("%Y-%m-%d")
    text = str(value).strip()
    return "" if text.lower() in ("nan", "nat") else text


# Function: is_placeholder_crm_ref
def is_placeholder_crm_ref(crm_ref: str) -> bool:
    crm_ref = (crm_ref or "").strip()
    if not crm_ref:
        return True
    return bool(_PLACEHOLDER_CRM_REF_PATTERN.match(crm_ref))


# Function: _resolve_field_columns
def _resolve_field_columns(df: pd.DataFrame) -> dict[str, str]:
    normalized_to_raw = {_normalize_column_name(c): c for c in df.columns}

    missing_required = []
    field_to_raw_col: dict[str, str] = {}
    for field, normalized_name in _COLUMN_MAP.items():
        raw_col = normalized_to_raw.get(normalized_name)
        if raw_col is None:
            if field in _REQUIRED_FIELDS:
                missing_required.append(normalized_name)
            continue
        field_to_raw_col[field] = raw_col

    if missing_required:
        raise ValueError(
            f"Sheet '{SHEET_NAME}' is missing required column(s): {', '.join(missing_required)}"
        )
    return field_to_raw_col


# Function: _build_tracker_row
def _build_tracker_row(raw_row, field_to_raw_col: dict[str, str], opportunity_name: str) -> dict[str, Any]:
    return {
        "opportunity_name": opportunity_name,
        "region": _clean_str(raw_row.get(field_to_raw_col.get("region"))),
        "customer_group": _clean_str(raw_row.get(field_to_raw_col.get("customer_group"))),
        "sub_vertical": _clean_str(raw_row.get(field_to_raw_col.get("sub_vertical"))),
        "solution_offering": _clean_str(raw_row.get(field_to_raw_col.get("solution_offering"))),
        "so_coe_leader": _clean_str(raw_row.get(field_to_raw_col.get("so_coe_leader"))),
        "crm_ref": _clean_str(raw_row.get(field_to_raw_col.get("crm_ref"))),
        # Blank stage is preserved as "" (a genuine data-quality gap in the
        # source), never fabricated to a default like "Prospecting".
        "oppty_stage": _clean_str(raw_row.get(field_to_raw_col.get("oppty_stage"))),
        "start_date": _clean_date(raw_row.get(field_to_raw_col.get("start_date"))),
        "oppty_owner": _clean_str(raw_row.get(field_to_raw_col.get("oppty_owner"))),
        "tcv_mn": _clean_float(raw_row.get(field_to_raw_col.get("tcv_mn"))),
        "q1_mn": _clean_float(raw_row.get(field_to_raw_col.get("q1_mn"))),
        "q2_mn": _clean_float(raw_row.get(field_to_raw_col.get("q2_mn"))),
        "q3_mn": _clean_float(raw_row.get(field_to_raw_col.get("q3_mn"))),
        "q4_mn": _clean_float(raw_row.get(field_to_raw_col.get("q4_mn"))),
        "remarks": _clean_str(raw_row.get(field_to_raw_col.get("remarks"))),
        "hyperscaler": _clean_str(raw_row.get(field_to_raw_col.get("hyperscaler"))),
        "delivery_ibu": _clean_str(raw_row.get(field_to_raw_col.get("delivery_ibu"))),
        "delivery_ibu_leader": _clean_str(raw_row.get(field_to_raw_col.get("delivery_ibu_leader"))),
        "delivery_validation": _clean_str(raw_row.get(field_to_raw_col.get("delivery_validation"))) or "No",
    }


# Function: _fy27_mismatch_warning
def _fy27_mismatch_warning(
    raw_row, row: dict[str, Any], field_to_raw_col: dict[str, str], idx: int, opportunity_name: str,
) -> str | None:
    # Cross-validate against the sheet's own FY total column — never stored,
    # fy27_mn stays a computed property (models.py) — only used to flag
    # rows where the source workbook's own arithmetic looks inconsistent.
    fy27_check_col = field_to_raw_col.get("_fy27_check")
    if fy27_check_col is None:
        return None
    sheet_fy27 = _clean_float(raw_row.get(fy27_check_col))
    computed_fy27 = row["q1_mn"] + row["q2_mn"] + row["q3_mn"] + row["q4_mn"]
    if abs(sheet_fy27 - computed_fy27) <= 0.01:
        return None
    return (
        f"Row {idx + HEADER_ROW + 2} ('{opportunity_name}'): sheet FY'27 total "
        f"({sheet_fy27:.4f}) does not match Q1-Q4 sum ({computed_fy27:.4f})."
    )


# Function: parse_fy27_plan_tracker
def parse_fy27_plan_tracker(path: str) -> tuple[list[dict], list[str]]:
    """Returns (rows, warnings). Each row is a dict of Opportunity model field
    names -> cleaned values, ready for upsert. Rows with a blank Opportunity
    Name are skipped (this is the model's own nullable=False constraint, and
    precisely separates real deals from the workbook's filler/banner rows)."""
    try:
        df = pd.read_excel(path, sheet_name=SHEET_NAME, header=HEADER_ROW)
    except ValueError as exc:
        raise ValueError(f"Could not read sheet '{SHEET_NAME}': {exc}") from exc

    field_to_raw_col = _resolve_field_columns(df)

    rows: list[dict] = []
    warnings: list[str] = []

    for idx, raw_row in df.iterrows():
        opportunity_name = _clean_str(raw_row.get(field_to_raw_col.get("opportunity_name")))
        if not opportunity_name:
            continue  # filler/banner row — not a real opportunity

        row = _build_tracker_row(raw_row, field_to_raw_col, opportunity_name)
        warning = _fy27_mismatch_warning(raw_row, row, field_to_raw_col, idx, opportunity_name)
        if warning:
            warnings.append(warning)
        rows.append(row)

    return rows, warnings


# Function: resolve_upsert_key
def resolve_upsert_key(row: dict) -> tuple[str, str]:
    """('crm_ref', value) if the row has a real-looking CRM Ref #, else
    ('name_customer', "name||customer" case-insensitive-trimmed) — only 1 of
    21 real rows in the source workbook has any CRM Ref # at all, so it can
    never be the sole key."""
    crm_ref = (row.get("crm_ref") or "").strip()
    if crm_ref and not is_placeholder_crm_ref(crm_ref):
        return ("crm_ref", crm_ref.lower())
    name = (row.get("opportunity_name") or "").strip().lower()
    customer = (row.get("customer_group") or "").strip().lower()
    return ("name_customer", f"{name}||{customer}")
