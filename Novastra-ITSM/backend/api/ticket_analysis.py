# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Ticket dump deep analysis API.
# Date: 2026-04-19
# ---------------------------------------------------------------------------
"""
Ticket dump deep analysis API.

Accepts an uploaded Excel ticket dump and returns dashboard-ready metrics:
- Issue type distribution
- Categorization (category / sub-category)
- Total issues
- Average issues per month
- Resolution TAT
- Open tickets and age buckets
- RCA distribution
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import re
import tempfile
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile

from backend.api.auth import get_current_user
from backend.llm.router import get_llm

router = APIRouter(prefix="/api/ticket-analysis", tags=["Ticket Analysis"])
logger = logging.getLogger(__name__)

_AUTOMATION_PREDICTION_CACHE_TTL_SEC = 180
_AUTOMATION_PREDICTION_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
_AUTOMATION_JOBS: dict[str, dict[str, Any]] = {}
_AUTOMATION_JOB_TTL_SEC = 900
_AUTOMATION_MAX_SAMPLE_RECORDS = 12
_AUTOMATION_MAX_TEXT_LEN = 180
_AUTOMATION_INVOKE_TIMEOUT_SEC = 600
_AUTOMATION_MAX_OPPORTUNITIES = 15


# Function: _find_column
def _find_column(columns: list[str], candidates: list[str]) -> Optional[str]:
    by_normalized = {c.lower().strip().replace("_", " "): c for c in columns}
    for cand in candidates:
        key = cand.lower().strip().replace("_", " ")
        if key in by_normalized:
            return by_normalized[key]
    return None


# Function: _safe_text
def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none", "null"}:
        return ""
    return text


# Function: _to_utc_series
def _to_utc_series(values: Any) -> pd.Series:
    """Parse a datetime-like column and normalize it to UTC-aware timestamps."""
    parsed = pd.to_datetime(values, errors="coerce")
    # Coerce to Series for consistent .dt behavior.
    if not isinstance(parsed, pd.Series):
        parsed = pd.Series(parsed)
    try:
        if parsed.dt.tz is None:
            return parsed.dt.tz_localize("UTC")
        return parsed.dt.tz_convert("UTC")
    except Exception:
        # Fallback path for mixed/irregular datetime inputs.
        parsed = pd.to_datetime(values, errors="coerce", utc=True)
        if not isinstance(parsed, pd.Series):
            parsed = pd.Series(parsed)
        return parsed


# Function: _normalize_status
def _normalize_status(value: Any) -> str:
    return _safe_text(value).lower()


# Function: _infer_rca
def _infer_rca(title: str, description: str, issue_type: str, category: str) -> str:
    haystack = f"{title} {description} {issue_type} {category}".lower()
    rules = [
        ("Infrastructure / Network", ["network", "latency", "packet", "dns", "firewall", "proxy", "vpn"]),
        ("Database", ["db", "database", "sql", "oracle", "postgres", "mysql", "query", "deadlock"]),
        ("Application Defect", ["bug", "exception", "nullpointer", "crash", "stack trace", "code defect"]),
        ("Configuration / Deployment", ["config", "configuration", "misconfig", "deployment", "release", "pipeline"]),
        ("Integration / API", ["api", "integration", "endpoint", "http", "timeout", "soap", "rest"]),
        ("Security / Access", ["auth", "authentication", "authorization", "permission", "access", "token", "security"]),
        ("Performance / Capacity", ["cpu", "memory", "capacity", "performance", "slow", "throughput", "resource"]),
        ("Data Quality", ["data", "duplicate", "corrupt", "incomplete", "mismatch", "mapping"]),
        ("Ops Process / Human Error", ["manual", "operator", "human", "runbook", "process gap", "missed step"]),
    ]
    for label, terms in rules:
        if any(term in haystack for term in terms):
            return label
    return "Other / Unknown"


# Function: _to_records
def _to_records(series: pd.Series, top_n: int = 15, key_name: str = "name") -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for key, value in series.head(top_n).items():
        out.append({key_name: str(key), "count": int(value)})
    return out


# Function: _normalize_dataframe_columns
def _normalize_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure dataframe has non-empty, unique string column names."""
    out = df.copy()
    used: dict[str, int] = {}
    normalized: list[str] = []

    for idx, col in enumerate(out.columns):
        base = str(col).strip()
        if not base or base.lower() in {"nan", "none"}:
            base = f"column_{idx + 1}"

        count = used.get(base, 0)
        if count == 0:
            name = base
        else:
            name = f"{base}_{count + 1}"
        used[base] = count + 1
        normalized.append(name)

    out.columns = normalized
    return out


# Function: _extract_json_object
def _extract_json_object(raw: str) -> dict[str, Any] | None:
    text = (raw or "").strip()
    if not text:
        return None

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            data = json.loads(text[start : end + 1])
            return data if isinstance(data, dict) else None
        except Exception:
            return None
    return None


# Function: _format_ticket_row
def _format_ticket_row(
    row: "pd.Series",
    ticket_id_col: str,
    title_col: str,
    status_col: str,
    category_col: str,
    age_col: str,
    number_col: Optional[str],
    short_description_col: Optional[str],
    configuration_item_col: Optional[str],
    state_col: Optional[str],
    urgency_col: Optional[str],
    impact_col: Optional[str],
    priority_col: Optional[str],
    updated_val: Any,
    created_val: Any,
    callback_val: Any,
    parent_incident_col: Optional[str],
    problem_col: Optional[str],
) -> dict:
    """Build a single ticket row dict for dashboard/oldest_open lists."""
    import pandas as _pd
    age_raw = row[age_col]
    return {
        "ticket_id": _safe_text(row[ticket_id_col]),
        "title": _safe_text(row[title_col]),
        "status": _safe_text(row[status_col]) or "open",
        "category": _safe_text(row[category_col]) or "Uncategorized",
        "age_days": int(round(float(age_raw))) if age_raw is not None and _pd.notna(age_raw) else None,
        "number": _safe_text(row[number_col]) if number_col else _safe_text(row[ticket_id_col]),
        "short_description": _safe_text(row[short_description_col]) if short_description_col else _safe_text(row[title_col]),
        "configuration_item": _safe_text(row[configuration_item_col]) if configuration_item_col else "",
        "state": _safe_text(row[state_col]) if state_col else (_safe_text(row[status_col]) or "open"),
        "urgency": _safe_text(row[urgency_col]) if urgency_col else "",
        "impact": _safe_text(row[impact_col]) if impact_col else "",
        "priority": _safe_text(row[priority_col]) if priority_col else "",
        "updated": updated_val.isoformat() if _pd.notna(updated_val) else "",
        "created": created_val.isoformat() if _pd.notna(created_val) else "",
        "callback_action_date": callback_val.isoformat() if _pd.notna(callback_val) else "",
        "parent_incident": _safe_text(row[parent_incident_col]) if parent_incident_col else "",
        "problem": _safe_text(row[problem_col]) if problem_col else "",
    }


# Function: _map_ticket_columns
def _map_ticket_columns(df: "pd.DataFrame", columns: list) -> dict:
    """Detect and return ITSM column name mapping with synthetic fallbacks applied to df."""
    find = lambda cands: _find_column(columns, cands)
    m = {
        "ticket_id": find(["ticket id", "ticket", "incident id", "incident number", "id", "number"]),
        "title": find(["title", "summary", "short description", "issue summary", "subject"]),
        "description": find(["description", "details", "issue description", "problem description"]),
        "status": find(["status", "state", "ticket status"]),
        "created": find(["created", "created date", "opened", "opened at", "open date", "reported date"]),
        "resolved": find(["resolved", "resolved at", "resolved on", "resolved date", "closed", "closed at",
                          "closed on", "closed date", "close date", "resolution date", "resolution datetime",
                          "completed", "completed date", "completion date", "solved", "solved at",
                          "solved date", "fixed date"]),
        "updated": find(["updated", "updated at", "updated on", "last updated", "last modified",
                         "modified", "modified at", "modified date"]),
        "issue_type": find(["issue type", "type", "incident type", "ticket type"]),
        "category": find(["category", "issue category", "classification"]),
        "subcategory": find(["sub category", "subcategory", "sub-category", "sub classification"]),
        "rca": find(["rca", "root cause", "root cause analysis", "reason", "cause"]),
        "number": find(["number", "ticket number", "incident number"]),
        "short_description": find(["short description", "title", "summary", "subject"]),
        "configuration_item": find(["configuration item", "ci", "cmdb ci", "configuration"]),
        "state": find(["state", "status", "ticket status"]),
        "urgency": find(["urgency"]),
        "impact": find(["impact"]),
        "priority": find(["priority"]),
        "callback_action_date": find(["call back/action date", "call back date", "callback date",
                                      "action date", "callback/action date"]),
        "parent_incident": find(["parent incident", "parent"]),
        "problem": find(["problem", "problem id", "problem number"]),
    }
    # Apply synthetic fallback columns directly to df
    if m["ticket_id"] is None:
        df["__ticket_id"] = [f"TICKET-{i+1}" for i in range(len(df))]
        m["ticket_id"] = "__ticket_id"
    if m["title"] is None:
        df["__title"] = "(No Title)"
        m["title"] = "__title"
    if m["description"] is None:
        df["__description"] = ""
        m["description"] = "__description"
    if m["issue_type"] is None:
        df["__issue_type"] = "Unspecified"
        m["issue_type"] = "__issue_type"
    if m["category"] is None:
        df["__category"] = "Uncategorized"
        m["category"] = "__category"
    if m["subcategory"] is None:
        df["__subcategory"] = "Unspecified"
        m["subcategory"] = "__subcategory"
    if m["status"] is None:
        df["__status"] = "open"
        m["status"] = "__status"
    return m


# Function: _detect_generic_columns
def _detect_generic_columns(df: pd.DataFrame, columns: list) -> dict:
    total_rows = len(df)
    find = lambda cands: _find_column(columns, cands)
    number_col = find(["number", "id", "record id", "incident number", "ticket number", "case id"])
    short_description_col = find(["short description", "description", "title", "summary", "subject", "name"])
    category_col = find(["category", "type", "classification", "group", "module", "domain"])
    subcategory_col = find(["subcategory", "sub category", "sub-category", "sub type", "subtype"])
    state_col = find(["state", "status", "stage"])
    priority_col = find(["priority", "severity"])
    urgency_col = find(["urgency"])
    impact_col = find(["impact"])
    configuration_item_col = find(["configuration item", "asset", "application", "system", "component", "service"])
    created_col = find(["created", "created date", "opened", "open date", "date", "timestamp", "month"])
    updated_col = find(["updated", "updated date", "modified", "last updated", "closed", "resolved"])
    callback_action_date_col = find(["call back/action date", "callback date", "action date", "due date", "target date"])
    parent_incident_col = find(["parent", "parent incident", "parent id"])
    problem_col = find(["problem", "root cause", "issue", "error"])
    if number_col is None:
        df["__number"] = [f"ROW-{i+1}" for i in range(total_rows)]
        number_col = "__number"
    if short_description_col is None:
        best_col = None
        best_non_empty = -1
        for c in columns:
            non_empty = int(df[c].astype(str).str.strip().replace({"nan": ""}).ne("").sum())
            if non_empty > best_non_empty:
                best_non_empty = non_empty
                best_col = c
        short_description_col = best_col or number_col
    if category_col is None:
        for c in columns:
            unique_count = int(df[c].astype(str).nunique(dropna=True))
            if 2 <= unique_count <= max(8, min(40, total_rows // 2)):
                category_col = c
                break
    if category_col is None:
        category_col = short_description_col
    if subcategory_col is None:
        subcategory_col = category_col
    if state_col is None:
        df["__state"] = "Unknown"
        state_col = "__state"
    return {
        "number_col": number_col,
        "short_description_col": short_description_col,
        "category_col": category_col,
        "subcategory_col": subcategory_col,
        "state_col": state_col,
        "priority_col": priority_col,
        "urgency_col": urgency_col,
        "impact_col": impact_col,
        "configuration_item_col": configuration_item_col,
        "created_col": created_col,
        "updated_col": updated_col,
        "callback_action_date_col": callback_action_date_col,
        "parent_incident_col": parent_incident_col,
        "problem_col": problem_col,
    }


# Function: _build_generic_row
def _build_generic_row(
    idx,
    row,
    col_map: dict,
    created: "pd.Series",
    updated: "pd.Series",
    callback_action_date: "pd.Series",
    ticket_age_days: "pd.Series",
) -> dict:
    created_value = created.loc[idx] if idx in created.index else pd.NaT
    updated_value = updated.loc[idx] if idx in updated.index else pd.NaT
    callback_value = callback_action_date.loc[idx] if idx in callback_action_date.index else pd.NaT
    age_value = ticket_age_days.loc[idx] if idx in ticket_age_days.index else None
    return {
        "ticket_id": _safe_text(row[col_map["number_col"]]),
        "title": _safe_text(row[col_map["short_description_col"]]),
        "status": _safe_text(row[col_map["state_col"]]) or "Unknown",
        "category": _safe_text(row[col_map["category_col"]]) or "Unspecified",
        "age_days": int(round(float(age_value))) if age_value is not None and pd.notna(age_value) else None,
        "number": _safe_text(row[col_map["number_col"]]),
        "short_description": _safe_text(row[col_map["short_description_col"]]),
        "configuration_item": _safe_text(row[col_map["configuration_item_col"]]) if col_map["configuration_item_col"] else "",
        "state": _safe_text(row[col_map["state_col"]]) or "Unknown",
        "urgency": _safe_text(row[col_map["urgency_col"]]) if col_map["urgency_col"] else "",
        "impact": _safe_text(row[col_map["impact_col"]]) if col_map["impact_col"] else "",
        "priority": _safe_text(row[col_map["priority_col"]]) if col_map["priority_col"] else "",
        "updated": updated_value.isoformat() if pd.notna(updated_value) else "",
        "created": created_value.isoformat() if pd.notna(created_value) else "",
        "callback_action_date": callback_value.isoformat() if pd.notna(callback_value) else "",
        "parent_incident": _safe_text(row[col_map["parent_incident_col"]]) if col_map["parent_incident_col"] else "",
        "problem": _safe_text(row[col_map["problem_col"]]) if col_map["problem_col"] else "",
    }


# Function: _build_generic_dataset_analysis
def _build_generic_dataset_analysis(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded Excel has no rows.")

    df = _normalize_dataframe_columns(df)
    columns = list(df.columns)
    total_rows = len(df)

    cm = _detect_generic_columns(df, columns)
    number_col = cm["number_col"]
    short_description_col = cm["short_description_col"]
    category_col = cm["category_col"]
    subcategory_col = cm["subcategory_col"]
    state_col = cm["state_col"]
    priority_col = cm["priority_col"]
    urgency_col = cm["urgency_col"]
    impact_col = cm["impact_col"]
    configuration_item_col = cm["configuration_item_col"]
    created_col = cm["created_col"]
    updated_col = cm["updated_col"]
    callback_action_date_col = cm["callback_action_date_col"]
    parent_incident_col = cm["parent_incident_col"]
    problem_col = cm["problem_col"]

    created = _to_utc_series(df[created_col]) if created_col else pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns, UTC]")
    updated = _to_utc_series(df[updated_col]) if updated_col else pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns, UTC]")
    callback_action_date = (
        _to_utc_series(df[callback_action_date_col])
        if callback_action_date_col
        else pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns, UTC]")
    )

    # Build month trend from first parseable datetime column.
    month_counts = pd.Series(dtype="int64")
    if not created.isna().all():
        month_counts = created.dropna().dt.to_period("M").value_counts().sort_index()
    else:
        for c in columns:
            parsed = _to_utc_series(df[c])
            if parsed.notna().sum() >= max(3, int(total_rows * 0.2)):
                month_counts = parsed.dropna().dt.to_period("M").value_counts().sort_index()
                created = parsed
                created_col = c
                break

    by_type = df[category_col].map(_safe_text).replace("", "Unspecified").value_counts()
    by_category = by_type
    cat_sub_counts = (
        df.assign(
            __cat=df[category_col].map(_safe_text).replace("", "Unspecified"),
            __sub=df[subcategory_col].map(_safe_text).replace("", "Unspecified"),
        )
        .groupby(["__cat", "__sub"])
        .size()
        .sort_values(ascending=False)
    )

    rca_source_col = problem_col if problem_col else category_col
    rca_counts = df[rca_source_col].map(_safe_text).replace("", "Unknown").value_counts()

    average_issues_per_month = round(float(month_counts.mean()), 2) if len(month_counts) else 0.0

    ticket_age_days = pd.Series([None] * total_rows, index=df.index, dtype="object")
    if not created.isna().all():
        reference = updated.where(updated.notna(), pd.Timestamp.now(tz="UTC"))
        age = (reference - created).dt.total_seconds() / 86400.0
        age = age.where(age >= 0)
        ticket_age_days = age

    _col_map = {
        "number_col": number_col,
        "short_description_col": short_description_col,
        "state_col": state_col,
        "category_col": category_col,
        "configuration_item_col": configuration_item_col,
        "urgency_col": urgency_col,
        "impact_col": impact_col,
        "priority_col": priority_col,
        "parent_incident_col": parent_incident_col,
        "problem_col": problem_col,
    }
    ticket_dashboard_rows = [
        _build_generic_row(idx, row, _col_map, created, updated, callback_action_date, ticket_age_days)
        for idx, row in df.iterrows()
    ]

    top_dimensions = []
    for c in columns:
        vals = df[c].map(_safe_text)
        unique_count = int(vals.replace("", pd.NA).dropna().nunique())
        if 2 <= unique_count <= max(8, min(60, total_rows // 2)):
            top_values = vals.replace("", pd.NA).dropna().value_counts().head(5)
            top_dimensions.append(
                {
                    "column": c,
                    "unique_values": unique_count,
                    "top_values": [{"value": str(k), "count": int(v)} for k, v in top_values.items()],
                }
            )

    top_dimensions = sorted(top_dimensions, key=lambda x: x["unique_values"])[:6]

    by_month_records = [{"month": str(month), "count": int(count)} for month, count in month_counts.items()]
    categorization_records = [
        {"category": str(cat), "subcategory": str(sub), "count": int(count)}
        for (cat, sub), count in cat_sub_counts.head(25).items()
    ]

    return {
        "analysis_mode": "generic",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "detected_columns": {
            "ticket_id": number_col,
            "title": short_description_col,
            "description": short_description_col,
            "status": state_col,
            "created": created_col,
            "resolved": updated_col,
            "updated": updated_col,
            "issue_type": category_col,
            "category": category_col,
            "subcategory": subcategory_col,
            "rca": problem_col,
            "number": number_col,
            "short_description": short_description_col,
            "configuration_item": configuration_item_col,
            "state": state_col,
            "urgency": urgency_col,
            "impact": impact_col,
            "priority": priority_col,
            "callback_action_date": callback_action_date_col,
            "parent_incident": parent_incident_col,
            "problem": problem_col,
        },
        "summary": {
            "total_issues": int(total_rows),
            "average_issues_per_month": average_issues_per_month,
            "resolved_count": 0,
            "open_count": 0,
            "average_tat_days": None,
            "median_tat_days": None,
            "average_open_age_days": None,
        },
        "issues_by_type": _to_records(by_type, top_n=500, key_name="issue_type"),
        "issues_by_category": _to_records(by_category, top_n=500, key_name="category"),
        "categorization": categorization_records,
        "issues_per_month": by_month_records,
        "open_age_buckets": {"0-7": 0, "8-30": 0, "31-90": 0, "90+": 0},
        "rca_distribution": _to_records(rca_counts, top_n=500, key_name="rca"),
        "ticket_dashboard_rows": ticket_dashboard_rows,
        "oldest_open_tickets": ticket_dashboard_rows,
        "generic_profile": {
            "row_count": int(total_rows),
            "column_count": int(len(columns)),
            "columns": columns,
            "top_dimensions": top_dimensions,
        },
    }


# Function: _collect_automation_sample_records
def _collect_automation_sample_records(
    analysis_payload: dict[str, Any],
    df: Optional[pd.DataFrame],
) -> list[dict[str, Any]]:
    sample_records: list[dict[str, Any]] = []
    if df is not None and not df.empty:
        sample_cols = [c for c in ["number", "short_description", "category", "state", "priority", "issue_type"] if c in df.columns]
        if sample_cols:
            sample_df = df[sample_cols].head(_AUTOMATION_MAX_SAMPLE_RECORDS).fillna("")
            sample_records = sample_df.to_dict(orient="records")
    if not sample_records:
        row_cols = ["number", "short_description", "category", "state", "priority", "issue_type"]
        for row in (analysis_payload.get("ticket_dashboard_rows") or [])[:_AUTOMATION_MAX_SAMPLE_RECORDS]:
            if isinstance(row, dict):
                sample_records.append({k: row.get(k, "") for k in row_cols})

    # Bound value lengths to keep prompts predictable under large uploaded datasets.
    bounded: list[dict[str, Any]] = []
    for row in sample_records:
        clean_row: dict[str, Any] = {}
        for key, value in row.items():
            text = str(value or "").strip()
            clean_row[str(key)] = text[:_AUTOMATION_MAX_TEXT_LEN]
        bounded.append(clean_row)
    return bounded


# Function: _flatten_to_strings
def _flatten_to_strings(value: Any, _depth: int = 0) -> list[str]:
    """Recursively extract all text from a value that may be a string, dict, or list.

    The LLM sometimes returns recommended_steps as nested dicts instead of plain strings.
    This function walks the structure and collects every meaningful string it finds,
    so the frontend always receives a clean list of sentences.
    """
    if _depth > 6:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, dict):
        sentences: list[str] = []
        for k, v in value.items():
            key_text = str(k).strip()
            if key_text:
                sentences.append(key_text)
            sentences.extend(_flatten_to_strings(v, _depth + 1))
        return sentences
    if isinstance(value, list):
        sentences = []
        for item in value:
            sentences.extend(_flatten_to_strings(item, _depth + 1))
        return sentences
    text = str(value).strip()
    return [text] if text else []


# Function: _clean_llm_opportunity
def _clean_llm_opportunity(row: dict, idx: int) -> dict[str, Any]:
    # Function: _enum
    def _enum(value: Any, allowed: set[str], default: str) -> str:
        normalized = str(value or default).strip().lower()
        return normalized if normalized in allowed else default

    raw_steps = row.get("recommended_steps") or []
    if isinstance(raw_steps, list):
        flat_steps: list[str] = []
        for item in raw_steps:
            flat_steps.extend(_flatten_to_strings(item))
    else:
        flat_steps = _flatten_to_strings(raw_steps)

    raw_evidence = row.get("evidence") or []
    if isinstance(raw_evidence, list):
        flat_evidence: list[str] = []
        for item in raw_evidence:
            flat_evidence.extend(_flatten_to_strings(item))
    else:
        flat_evidence = _flatten_to_strings(raw_evidence)

    return {
        "id": str(row.get("id") or f"AUTO-{idx}"),
        "title": str(row.get("title") or "Automation Opportunity"),
        "opportunity_type": str(row.get("opportunity_type") or "Automation"),
        "confidence": _enum(row.get("confidence"), {"high", "medium", "low"}, "medium"),
        "impact": _enum(row.get("impact"), {"high", "medium", "low"}, "medium"),
        "effort": _enum(row.get("effort"), {"high", "medium", "low"}, "medium"),
        "estimated_monthly_hours_saved": float(row.get("estimated_monthly_hours_saved") or 0),
        "description": str(row.get("description") or ""),
        "evidence": flat_evidence[:8],
        "recommended_steps": flat_steps[:8],
    }


# Function: _automation_cache_key
def _automation_cache_key(payload: dict[str, Any]) -> str:
    compact = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(compact.encode("utf-8", errors="ignore")).hexdigest()


# Function: _automation_cache_get
def _automation_cache_get(key: str) -> Optional[dict[str, Any]]:
    item = _AUTOMATION_PREDICTION_CACHE.get(key)
    if not item:
        return None
    expires_at, data = item
    if expires_at < time.time():
        _AUTOMATION_PREDICTION_CACHE.pop(key, None)
        return None
    return data


# Function: _automation_cache_put
def _automation_cache_put(key: str, value: dict[str, Any]) -> None:
    _AUTOMATION_PREDICTION_CACHE[key] = (time.time() + _AUTOMATION_PREDICTION_CACHE_TTL_SEC, value)


# Function: _cleanup_automation_jobs
def _cleanup_automation_jobs() -> None:
    now = time.time()
    stale = [job_id for job_id, meta in _AUTOMATION_JOBS.items() if float(meta.get("expires_at", 0)) < now]
    for job_id in stale:
        _AUTOMATION_JOBS.pop(job_id, None)


# Function: _run_automation_job
async def _run_automation_job(job_id: str, analysis_payload: dict[str, Any]) -> None:
    started_at = time.perf_counter()
    try:
        result = await asyncio.to_thread(_predict_automation_opportunities, analysis_payload, None)
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "automation_opportunities": result,
        }
        _AUTOMATION_JOBS[job_id].update({"status": "done", "result": payload})
        logger.info(
            "automation_job done job_id=%s elapsed_ms=%.1f opportunities=%d",
            job_id,
            (time.perf_counter() - started_at) * 1000,
            len(result.get("opportunities", [])),
        )
    except Exception as exc:
        _AUTOMATION_JOBS[job_id].update({"status": "error", "detail": str(exc)})
        logger.exception("automation_job failed job_id=%s elapsed_ms=%.1f", job_id, (time.perf_counter() - started_at) * 1000)


# Function: _predict_automation_opportunities
def _predict_automation_opportunities(
    analysis_payload: dict[str, Any],
    df: Optional[pd.DataFrame] = None,
) -> dict[str, Any]:
    analysis_mode = analysis_payload.get("analysis_mode") or "ticket"
    summary = analysis_payload.get("summary", {})
    sample_records = _collect_automation_sample_records(analysis_payload, df)

    prompt_payload = {
        "analysis_mode": analysis_mode,
        "summary": summary,
        "issues_by_type": analysis_payload.get("issues_by_type", []),
        "issues_by_category": analysis_payload.get("issues_by_category", []),
        "categorization": analysis_payload.get("categorization", [])[:20],
        "rca_distribution": analysis_payload.get("rca_distribution", []),
        "open_age_buckets": analysis_payload.get("open_age_buckets", {}),
        "issues_per_month": analysis_payload.get("issues_per_month", [])[-12:],
        "sample_tickets": sample_records,
        "generic_profile": {
            "row_count": (analysis_payload.get("generic_profile") or {}).get("row_count"),
            "column_count": (analysis_payload.get("generic_profile") or {}).get("column_count"),
            "top_dimensions": ((analysis_payload.get("generic_profile") or {}).get("top_dimensions") or [])[:8],
        },
    }
    cache_key = _automation_cache_key(prompt_payload)
    cached = _automation_cache_get(cache_key)
    if cached is not None:
        return cached

    domain_line = (
        "You are a senior enterprise ITSM and AI automation strategist with deep expertise in ServiceNow, ITIL, LLM-powered AI agents, RAG pipelines, RPA, AIOps, and open-source AI tooling. "
        if analysis_mode == "ticket"
        else "You are a senior enterprise data operations automation strategist with expertise in LLM-powered AI agents, ML pipelines, RAG architectures, data quality automation, RPA, and open-source AI tooling. "
    )

    automation_categories = (
        "1) Auto-Triage & Classification (NLP/ML-based AI agent), "
        "2) Runbook & Self-Healing Automation (AI agent-driven auto-remediation), "
        "3) Knowledge Base & Virtual Agent Deflection (RAG + LLM chatbot agent), "
        "4) Predictive Prevention (ML forecasting agent for anomaly detection), "
        "5) SLA Management Automation (AI watchdog agent for early-warning and escalation), "
        "6) Root-Cause Automation (LLM-powered RCA agent with auto-fix playbooks), "
        "7) Workflow & Process Automation (AI orchestration agent for ticket lifecycle), "
        "8) Duplicate & Related Ticket Detection (embedding-based similarity agent), "
        "9) Reporting & Analytics Automation (AI-driven KPI pipeline and insight agent), "
        "10) Integration & API Health Monitoring (synthetic monitoring + self-recovery agent), "
        "11) Change & Problem Management Automation (AI linkage and impact analysis agent), "
        "12) Notification & Communication Automation (LLM-driven intelligent stakeholder update agent), "
        "13) Capacity & Resource Optimization (AI demand forecasting agent for staffing/infra), "
        "14) Conversational ITSM Agent (end-user self-service LLM chatbot), "
        "15) AI-Assisted Root Cause Analysis (multi-step LLM RCA generation agent)."
    )

    recommended_steps_instruction = (
        "recommended_steps must be a JSON array of plain text strings only — no objects, no dicts, no nested JSON. "
        "Each string is one actionable sentence a developer can execute. "
        "Write steps that describe building custom AI agents or open-source solutions: name the agent type (ReAct, RAG, classifier), "
        "the framework (LangChain, LlamaIndex, Hugging Face, spaCy, sentence-transformers, FAISS, Chroma, Airflow, FastAPI), "
        "the data it uses, and the action it takes. Only mention commercial platforms as a last resort."
    )

    prompt = (
        domain_line
        + "Analyze the provided ITSM ticket data and identify the top 15 most viable automation and AI optimization opportunities. "
        + "If fewer than 15 distinct high-impact opportunities exist in the data, return only those that are genuinely viable. "
        + "Cover as many of the following automation categories as the data supports: " + automation_categories + " "
        + "Return ONLY a JSON object with this exact schema — no markdown, no prose, no extra keys: "
        + '{"opportunities":[{"id":string,"title":string,"opportunity_type":string,"confidence":"high"|"medium"|"low",'
        + '"impact":"high"|"medium"|"low","effort":"high"|"medium"|"low","estimated_monthly_hours_saved":number,'
        + '"description":string,"evidence":[string,string,...],"recommended_steps":[string,string,...]}],'
        + '"overall_recommendation":string}. '
        + "Rules: (1) Return up to 15 distinct automation opportunities, ranked by viability — prioritize high-confidence, high-impact items first. "
        + "(2) Each opportunity MUST cite specific numbers, category names, or patterns from the input data as evidence. "
        + "(3) estimated_monthly_hours_saved must be a realistic positive number based on ticket volume and opportunity type. "
        + "(4) " + recommended_steps_instruction + " "
        + "(5) Cover both quick-wins (low effort, immediate value) and strategic automation (high effort, high impact). "
        + "(6) Do not invent opportunities unsupported by the data — every item must have real evidence from the input. "
        + "Input data JSON: "
        + json.dumps(prompt_payload, ensure_ascii=True)
    )

    try:
        from backend.config import OLLAMA_BASE_URL, OLLAMA_MODEL
        from backend.llm.router import assert_ollama_gpu_available
        from langchain_ollama import ChatOllama
        assert_ollama_gpu_available(OLLAMA_MODEL)
        llm = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.1,
            num_predict=8192,
            num_ctx=16384,
            repeat_penalty=1.1,
            top_k=20,
            top_p=0.9,
            format="json",
            timeout=_AUTOMATION_INVOKE_TIMEOUT_SEC,
            keep_alive="15m",
        )
        system_msg = (
            "You are a strict enterprise ITSM automation advisor and AI agent architect. "
            "Your recommended_steps must always prioritize building custom AI agents or custom solutions using open-source frameworks "
            "(LangChain, LlamaIndex, Haystack, Hugging Face, spaCy, scikit-learn, sentence-transformers, FAISS, Chroma, FastAPI, Airflow, Prefect) "
            "over generic platform recommendations. Each step must be specific enough for a developer to implement immediately. "
            "Return valid JSON only. Do not include any markdown, code fences, or explanation text — output only raw JSON."
        )
        with ThreadPoolExecutor(max_workers=1) as pool:
            llm_result = pool.submit(
                llm.invoke,
                [
                    ("system", system_msg),
                    ("human", prompt),
                ],
            ).result(timeout=_AUTOMATION_INVOKE_TIMEOUT_SEC)
        llm_text = llm_result.content if hasattr(llm_result, "content") else str(llm_result)
        parsed = _extract_json_object(llm_text)
        if not parsed:
            raise ValueError("Ollama returned non-JSON response.")

        opportunities = parsed.get("opportunities") or []
        if not isinstance(opportunities, list):
            opportunities = []

        cleaned = [
            _clean_llm_opportunity(row, idx)
            for idx, row in enumerate(opportunities, start=1)
            if isinstance(row, dict)
        ]

        if not cleaned:
            raise ValueError("No opportunities parsed from Ollama response.")

        result = {
            "provider": "ollama",
            "model": "configured",
            "overall_recommendation": str(parsed.get("overall_recommendation") or "Adopt a phased automation strategy targeting high-volume categories, runbook automation, and virtual agent deflection for maximum ROI."),
            "opportunities": cleaned[:_AUTOMATION_MAX_OPPORTUNITIES],
            "generated_with_llm": True,
        }
        _automation_cache_put(cache_key, result)
        return result
    except FutureTimeout:
        logger.error(
            "Ollama automation prediction timed out after %ss — consider increasing _AUTOMATION_INVOKE_TIMEOUT_SEC or the Ollama server timeout",
            _AUTOMATION_INVOKE_TIMEOUT_SEC,
        )
        raise HTTPException(
            status_code=503,
            detail=f"Ollama LLM timed out after {_AUTOMATION_INVOKE_TIMEOUT_SEC}s. The model may still be loading. Please retry in a moment.",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Ollama automation prediction failed: %s", exc)
        raise HTTPException(
            status_code=503,
            detail=f"Ollama LLM prediction failed: {exc}. Ensure Ollama is running with the configured model and retry.",
        )


# Function: _build_ticket_analysis
def _build_ticket_analysis(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded Excel has no rows.")

    df = _normalize_dataframe_columns(df)
    columns = list(df.columns)

    m = _map_ticket_columns(df, columns)

    if m["created"] is None:
        return _build_generic_dataset_analysis(df)

    created = _to_utc_series(df[m["created"]])
    resolved = _to_utc_series(df[m["resolved"]]) if m["resolved"] else pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns, UTC]")
    updated = _to_utc_series(df[m["updated"]]) if m["updated"] else pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns, UTC]")
    callback_action_date = _to_utc_series(df[m["callback_action_date"]]) if m["callback_action_date"] else pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns, UTC]")

    normalized_status = df[m["status"]].map(_normalize_status)
    open_statuses = {"open", "new", "pending", "in progress", "assigned", "reopened", "wip", "work in progress"}
    closed_statuses = {"closed", "resolved", "done", "completed", "cancelled", "canceled"}

    resolved_effective = resolved.copy()
    missing_resolved_for_closed = normalized_status.isin(closed_statuses) & resolved_effective.isna()
    if missing_resolved_for_closed.any() and not updated.isna().all():
        resolved_effective.loc[missing_resolved_for_closed] = updated.loc[missing_resolved_for_closed]

    is_closed = normalized_status.isin(closed_statuses) | resolved_effective.notna()
    is_open = normalized_status.isin(open_statuses) | (~is_closed & resolved_effective.isna())

    total_issues = int(len(df))
    valid_created = created.dropna()
    if valid_created.empty:
        raise HTTPException(status_code=400, detail="Could not parse any valid Created/Open dates.")

    month_counts = valid_created.dt.to_period("M").value_counts().sort_index()
    average_issues_per_month = round(float(month_counts.mean()), 2) if len(month_counts) else 0.0

    tat_days = (resolved_effective - created).dt.total_seconds() / 86400.0
    tat_days = tat_days[(tat_days.notna()) & (tat_days >= 0)]

    now_utc = pd.Timestamp.now(tz="UTC")
    open_age_days = (now_utc - created).dt.total_seconds() / 86400.0
    open_age_days = open_age_days[is_open & open_age_days.notna()]

    age_buckets = {
        "0-7": int(((open_age_days >= 0) & (open_age_days <= 7)).sum()),
        "8-30": int(((open_age_days > 7) & (open_age_days <= 30)).sum()),
        "31-90": int(((open_age_days > 30) & (open_age_days <= 90)).sum()),
        "90+": int((open_age_days > 90).sum()),
    }

    by_type = df[m["issue_type"]].map(_safe_text).replace("", "Unspecified").value_counts()
    by_category = df[m["category"]].map(_safe_text).replace("", "Uncategorized").value_counts()
    cat_sub_counts = (
        df.assign(
            __cat=df[m["category"]].map(_safe_text).replace("", "Uncategorized"),
            __sub=df[m["subcategory"]].map(_safe_text).replace("", "Unspecified"),
        )
        .groupby(["__cat", "__sub"]).size().sort_values(ascending=False)
    )

    rca_series = df[m["rca"]].map(_safe_text) if m["rca"] else pd.Series([""] * len(df))
    inferred_rca = []
    for i in range(len(df)):
        explicit = _safe_text(rca_series.iloc[i])
        if explicit:
            inferred_rca.append(explicit)
            continue
        inferred_rca.append(_infer_rca(
            _safe_text(df[m["title"]].iloc[i]), _safe_text(df[m["description"]].iloc[i]),
            _safe_text(df[m["issue_type"]].iloc[i]), _safe_text(df[m["category"]].iloc[i]),
        ))
    rca_counts = pd.Series(inferred_rca).value_counts()

    open_df = df[is_open].copy()
    open_df["__open_age_days"] = open_age_days.reindex(open_df.index)

    ticket_age_days = (now_utc - created).dt.total_seconds() / 86400.0
    resolved_age_days = (resolved_effective - created).dt.total_seconds() / 86400.0
    ticket_age_days = ticket_age_days.where(resolved_effective.isna(), resolved_age_days)

    all_tickets_df = df.copy()
    all_tickets_df["__ticket_age_days"] = ticket_age_days.reindex(all_tickets_df.index)

    # Function: _row_kwargs
    def _row_kwargs(row, age_col):
        idx = row.name
        return dict(
            row=row, ticket_id_col=m["ticket_id"], title_col=m["title"], status_col=m["status"],
            category_col=m["category"], age_col=age_col, number_col=m["number"],
            short_description_col=m["short_description"], configuration_item_col=m["configuration_item"],
            state_col=m["state"], urgency_col=m["urgency"], impact_col=m["impact"],
            priority_col=m["priority"],
            updated_val=updated.loc[idx] if idx in updated.index else pd.NaT,
            created_val=created.loc[idx] if idx in created.index else pd.NaT,
            callback_val=callback_action_date.loc[idx] if idx in callback_action_date.index else pd.NaT,
            parent_incident_col=m["parent_incident"], problem_col=m["problem"],
        )

    ticket_dashboard_rows = [
        _format_ticket_row(**_row_kwargs(row, "__ticket_age_days"))
        for _, row in all_tickets_df.sort_values("__ticket_age_days", ascending=False).iterrows()
    ]
    oldest_open = [
        _format_ticket_row(**_row_kwargs(row, "__open_age_days"))
        for _, row in open_df.sort_values("__open_age_days", ascending=False).iterrows()
    ]

    by_month_records = [{"month": str(month), "count": int(count)} for month, count in month_counts.items()]
    categorization_records = [
        {"category": str(cat), "subcategory": str(sub), "count": int(count)}
        for (cat, sub), count in cat_sub_counts.head(25).items()
    ]

    return {
        "analysis_mode": "ticket",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "detected_columns": {k: m[k] for k in m},
        "summary": {
            "total_issues": total_issues,
            "average_issues_per_month": average_issues_per_month,
            "resolved_count": int(is_closed.sum()),
            "open_count": int(is_open.sum()),
            "average_tat_days": round(float(tat_days.mean()), 2) if len(tat_days) else None,
            "median_tat_days": round(float(tat_days.median()), 2) if len(tat_days) else None,
            "average_open_age_days": round(float(open_age_days.mean()), 2) if len(open_age_days) else None,
        },
        "issues_by_type": _to_records(by_type, top_n=500, key_name="issue_type"),
        "issues_by_category": _to_records(by_category, top_n=500, key_name="category"),
        "categorization": categorization_records,
        "issues_per_month": by_month_records,
        "open_age_buckets": age_buckets,
        "rca_distribution": _to_records(rca_counts, top_n=500, key_name="rca"),
        "ticket_dashboard_rows": ticket_dashboard_rows,
        "oldest_open_tickets": oldest_open,
    }



# Function: predict_automation_opportunities
@router.post("/predict-automation")
async def predict_automation_opportunities(
    analysis_payload: dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not isinstance(analysis_payload, dict) or not analysis_payload.get("summary"):
        raise HTTPException(status_code=400, detail="Valid ticket analysis payload is required.")

    automation = await asyncio.to_thread(_predict_automation_opportunities, analysis_payload, None)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "automation_opportunities": automation,
    }


# Function: predict_automation_opportunities_async
@router.post("/predict-automation-async")
async def predict_automation_opportunities_async(
    analysis_payload: dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not isinstance(analysis_payload, dict) or not analysis_payload.get("summary"):
        raise HTTPException(status_code=400, detail="Valid ticket analysis payload is required.")

    _cleanup_automation_jobs()
    job_id = hashlib.sha256(json.dumps(analysis_payload, sort_keys=True, ensure_ascii=True).encode("utf-8", errors="ignore")).hexdigest()[:16]
    _AUTOMATION_JOBS[job_id] = {
        "status": "pending",
        "result": None,
        "detail": None,
        "created_at": time.time(),
        "expires_at": time.time() + _AUTOMATION_JOB_TTL_SEC,
    }
    asyncio.create_task(_run_automation_job(job_id, analysis_payload))
    return {"status": "pending", "job_id": job_id}


# Function: predict_automation_job_status
@router.get("/predict-automation-job/{job_id}")
async def predict_automation_job_status(job_id: str, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    _cleanup_automation_jobs()
    job = _AUTOMATION_JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Prediction job not found or expired")

    elapsed = max(0.0, time.time() - float(job.get("created_at", time.time())))
    retry_after_ms = 0
    if job.get("status", "pending") == "pending":
        if elapsed < 3:
            retry_after_ms = 250
        elif elapsed < 15:
            retry_after_ms = 500
        elif elapsed < 45:
            retry_after_ms = 900
        else:
            retry_after_ms = 1400

    return {
        "status": job.get("status", "pending"),
        "result": job.get("result"),
        "detail": job.get("detail"),
        "retry_after_ms": retry_after_ms,
    }


# Function: _read_excel_to_dataframe
def _read_excel_to_dataframe(tmp_path: Path, suffix: str, sheet_name: Optional[str]) -> pd.DataFrame:
    read_kwargs: dict[str, Any] = {"dtype": str}
    if suffix in {".xlsx", ".xlsm"}:
        read_kwargs["engine"] = "openpyxl"
    elif suffix == ".xls":
        read_kwargs["engine"] = "xlrd"
    if sheet_name:
        read_kwargs["sheet_name"] = sheet_name
    try:
        data = pd.read_excel(tmp_path, **read_kwargs)
    except ImportError as exc:
        msg = str(exc).lower()
        if "xlrd" in msg or suffix == ".xls":
            raise HTTPException(
                status_code=400,
                detail="Legacy .xls parsing requires xlrd. Please upload .xlsx/.xlsm or install xlrd.",
            )
        if "openpyxl" in msg:
            raise HTTPException(
                status_code=400,
                detail="Excel parser dependency openpyxl is missing on server. Install openpyxl and retry.",
            )
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse Excel file: {exc}")
    if isinstance(data, dict):
        return next((v for v in data.values() if isinstance(v, pd.DataFrame) and not v.empty), pd.DataFrame())
    return data


# Function: analyze_ticket_dump_excel
@router.post("/analyze-excel")
async def analyze_ticket_dump_excel(
    file: UploadFile = File(...),
    sheet_name: Optional[str] = Form(default=None),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    file_name = (file.filename or "").lower()
    suffix = Path(file_name).suffix
    if suffix not in {".xlsx", ".xls", ".xlsm"}:
        raise HTTPException(status_code=400, detail="Please upload a valid Excel file (.xlsx/.xls/.xlsm).")

    tmp_path: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename or "ticket_dump.xlsx").suffix) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(await file.read())

        df = _read_excel_to_dataframe(tmp_path, suffix, sheet_name)

        try:
            payload = _build_ticket_analysis(df)
        except HTTPException:
            raise
        except Exception as exc:
            # Last-resort fallback for heterogeneous Excel schemas where ticket-specific inference fails.
            logger.warning("Ticket analyzer failed, using generic dataset analyzer fallback: %s", exc)
            payload = _build_generic_dataset_analysis(df)
            payload["analysis_mode"] = "generic"
            payload["analysis_fallback_reason"] = str(exc)

        payload["file_name"] = file.filename
        payload["sheet_name"] = sheet_name
        return payload

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Ticket dump analysis failed: %s\n%s", exc, traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Ticket dump analysis failed: {exc}")
    finally:
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                pass
