# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Authoritative local CMDB read model backed by SQLite.
# Date: 2026-05-28
# ---------------------------------------------------------------------------
"""Authoritative local CMDB read model backed by SQLite."""
from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import backend.config as cfg

DB_PATH = Path(cfg.BASE_DIR) / "cmdb_intelligence.sqlite3"


# Function: _connect
def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


# Function: ensure_schema
def ensure_schema() -> None:
    with closing(_connect()) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS cmdb_records (
                entity_type TEXT NOT NULL,
                sys_id TEXT NOT NULL,
                display_name TEXT NOT NULL DEFAULT '',
                class_name TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT '',
                data_json TEXT NOT NULL,
                synced_at TEXT NOT NULL,
                PRIMARY KEY(entity_type, sys_id)
            );
            CREATE INDEX IF NOT EXISTS idx_cmdb_records_type_name
                ON cmdb_records(entity_type, display_name);
            CREATE TABLE IF NOT EXISTS cmdb_sync_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                status TEXT NOT NULL,
                counts_json TEXT NOT NULL DEFAULT '{}',
                error TEXT
            );
            """
        )
        conn.commit()


# Function: replace_entity
def replace_entity(entity_type: str, records: list[dict[str, Any]]) -> int:
    ensure_schema()
    now = datetime.now(timezone.utc).isoformat()
    rows = []
    for index, record in enumerate(records):
        sys_id = str(record.get("sys_id") or record.get("number") or record.get("name") or f"row-{index}")
        display = str(
            record.get("name") or record.get("number") or record.get("display_name")
            or record.get("product") or record.get("model") or sys_id
        )
        class_name = str(record.get("sys_class_name") or record.get("class_name") or "")
        updated_at = str(record.get("sys_updated_on") or record.get("updated_at") or "")
        rows.append((entity_type, sys_id, display, class_name, updated_at, json.dumps(record), now))
    with closing(_connect()) as conn:
        conn.execute("DELETE FROM cmdb_records WHERE entity_type = ?", (entity_type,))
        conn.executemany(
            """INSERT INTO cmdb_records
               (entity_type,sys_id,display_name,class_name,updated_at,data_json,synced_at)
               VALUES (?,?,?,?,?,?,?)""",
            rows,
        )
        conn.commit()
    return len(rows)


# Function: status
def status() -> dict[str, Any]:
    ensure_schema()
    with closing(_connect()) as conn:
        rows = conn.execute(
            "SELECT entity_type, COUNT(*) count, MAX(synced_at) synced_at FROM cmdb_records GROUP BY entity_type"
        ).fetchall()
    counts = {row["entity_type"]: int(row["count"]) for row in rows}
    return {
        "ready": sum(counts.values()) > 0,
        "counts": counts,
        "total_records": sum(counts.values()),
        "last_synced_at": max((row["synced_at"] or "" for row in rows), default=None),
    }


# Function: _value
def _value(record: dict[str, Any], field: str) -> Any:
    value: Any = record
    for part in field.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    if isinstance(value, dict):
        return value.get("display_value") or value.get("value") or value.get("name")
    return value


# Function: _number
def _number(value: Any) -> float:
    text = str(value or "0").replace(",", "").replace("$", "").strip()
    try:
        return float(text)
    except ValueError:
        return 0.0


# Function: _op_equals
def _op_equals(actual: Any, expected: Any, record: dict[str, Any]) -> bool:
    return str(actual or "").casefold() == str(expected or "").casefold()


# Function: _op_contains
def _op_contains(actual: Any, expected: Any, record: dict[str, Any]) -> bool:
    return str(expected or "").casefold() in str(actual or "").casefold()


# Function: _op_older_than
def _op_older_than(actual: Any, expected: Any, record: dict[str, Any]) -> bool:
    try:
        actual_dt = datetime.fromisoformat(str(actual).replace("Z", "+00:00"))
        cutoff = datetime.now(timezone.utc).timestamp() - int(expected) * 86400
        return actual_dt.timestamp() < cutoff
    except (TypeError, ValueError):
        return False


# Function: _op_related_to
def _op_related_to(actual: Any, expected: Any, record: dict[str, Any]) -> bool:
    needle = str(expected or "").casefold()
    haystack = " ".join(str(v) for v in record.values()).casefold()
    return needle in haystack


_FILTER_OPERATORS = {
    "equals": _op_equals,
    "contains": _op_contains,
    "older_than": _op_older_than,
    "related_to": _op_related_to,
}


# Function: _filter_item_matches
def _filter_item_matches(record: dict[str, Any], item: dict[str, Any]) -> bool:
    """A filter item with an unrecognized operator never rejects the record."""
    predicate = _FILTER_OPERATORS.get(item["operator"])
    if predicate is None:
        return True
    actual = _value(record, item["field"])
    expected = item.get("value")
    return predicate(actual, expected, record)


# Function: _record_matches_filters
def _record_matches_filters(record: dict[str, Any], filters: list[dict[str, Any]]) -> bool:
    return all(_filter_item_matches(record, item) for item in filters)


# Function: query_records
def query_records(entity: str, filters: list[dict[str, Any]], page: int, page_size: int) -> dict[str, Any]:
    ensure_schema()
    with closing(_connect()) as conn:
        rows = conn.execute(
            "SELECT data_json FROM cmdb_records WHERE entity_type = ?", (entity,)
        ).fetchall()
    records = [json.loads(row["data_json"]) for row in rows]

    filtered = [record for record in records if _record_matches_filters(record, filters)]
    start = (page - 1) * page_size
    return {
        "records": filtered[start:start + page_size],
        "total": len(filtered),
        "page": page,
        "page_size": page_size,
        "pages": (len(filtered) + page_size - 1) // page_size,
    }


# Function: relationship_analysis
def relationship_analysis() -> dict[str, Any]:
    ensure_schema()
    with closing(_connect()) as conn:
        rows = conn.execute(
            "SELECT entity_type,data_json FROM cmdb_records WHERE entity_type IN ('relation','incident','change')"
        ).fetchall()
    grouped: dict[str, list[dict]] = {"relation": [], "incident": [], "change": []}
    for row in rows:
        grouped[row["entity_type"]].append(json.loads(row["data_json"]))
    relations = []
    for rel in grouped["relation"]:
        parent = _value(rel, "parent") or ""
        child = _value(rel, "child") or ""
        if parent and child:
            relations.append({
                "source_ci": parent,
                "target_ci": child,
                "relationship_type": _value(rel, "type") or "depends_on",
                "confidence": 1.0,
                "evidence": ["ServiceNow cmdb_rel_ci"],
            })
    incident_counts: dict[str, int] = {}
    for incident in grouped["incident"]:
        ci = str(_value(incident, "cmdb_ci") or "").strip()
        if ci:
            incident_counts[ci] = incident_counts.get(ci, 0) + 1
    return {
        "suggested_relationships": relations,
        "missing_count": 0,
        "authoritative_relationship_count": len(relations),
        "incident_counts_by_ci": incident_counts,
        "source_counts": {key: len(value) for key, value in grouped.items()},
        "llm_used": False,
    }


# Function: license_analysis
def license_analysis(page: int, page_size: int) -> dict[str, Any]:
    ensure_schema()
    with closing(_connect()) as conn:
        rows = conn.execute(
            "SELECT entity_type,data_json FROM cmdb_records WHERE entity_type IN ('asset','license')"
        ).fetchall()
    assets = [json.loads(row["data_json"]) for row in rows if row["entity_type"] == "asset"]
    licenses = [json.loads(row["data_json"]) for row in rows if row["entity_type"] == "license"]
    opportunities = []
    total = 0.0
    for license_row in licenses:
        product = str(_value(license_row, "display_name") or _value(license_row, "name") or _value(license_row, "software_model") or "Unknown")
        entitled = int(_number(_value(license_row, "rights") or _value(license_row, "licensed_seats")))
        allocated = int(_number(_value(license_row, "allocated") or _value(license_row, "active_rights") or _value(license_row, "active_users")))
        unit_cost = _number(_value(license_row, "unit_cost") or _value(license_row, "cost"))
        reclaim = max(0, entitled - allocated)
        saving = round(reclaim * unit_cost, 2)
        if reclaim:
            total += saving
            opportunities.append({"product": product, "licensed_seats": entitled, "active_users": allocated,
                "utilization_pct": round(allocated / max(entitled, 1) * 100, 1), "reclaim_seats": reclaim,
                "unit_cost": unit_cost, "annual_saving_estimate_usd": saving, "action": "Reclaim unused entitlement"})
    opportunities.sort(key=lambda item: item["annual_saving_estimate_usd"], reverse=True)
    start = (page - 1) * page_size
    return {"opportunities": opportunities[start:start + page_size], "total": len(opportunities),
        "page": page, "page_size": page_size, "asset_count": len(assets),
        "license_count": len(licenses), "total_annual_saving_usd": round(total, 2), "llm_used": False}
