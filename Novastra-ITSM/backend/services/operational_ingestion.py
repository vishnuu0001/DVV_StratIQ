# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Operational PostgreSQL ingestion layer for ServiceNow entities.
# Date: 2026-04-01
# ---------------------------------------------------------------------------
"""Operational PostgreSQL ingestion layer for ServiceNow entities."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import backend.config as cfg
from backend.services.postgres_store import ensure_common_schema, get_connection

logger = logging.getLogger(__name__)
_LOCAL_SNAPSHOT_CACHE: dict[str, Any] = {"path": None, "mtime": None, "records": []}


# Function: _utc_now
def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


# Function: _clean_text
def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        value = value.get("display_value") or value.get("value") or value.get("name") or ""
    text = str(value).strip()
    if text.lower() in {"none", "null", "nan"}:
        return ""
    return text


# The dashboard's State column/filter is constrained to exactly these five values —
# every raw ServiceNow state (New/In Progress/On Hold/Resolved/Closed/Cancelled/...)
# gets folded into one of them on the way in, so `DISTINCT state` never surfaces a
# raw SN value the UI wasn't built to show. New tickets default to "Open" (SN's own
# default state, "New", also normalizes to "Open").
CANONICAL_STATES = ["Open", "In-Progress", "Pending Clarifications", "Closed", "Re-Opened"]

_STATE_ALIASES: dict[str, str] = {
    "new": "Open",
    "open": "Open",
    "in progress": "In-Progress",
    "in-progress": "In-Progress",
    "assigned": "In-Progress",
    "active": "In-Progress",
    "on hold": "Pending Clarifications",
    "awaiting info": "Pending Clarifications",
    "awaiting caller": "Pending Clarifications",
    "awaiting problem": "Pending Clarifications",
    "awaiting vendor": "Pending Clarifications",
    "awaiting change": "Pending Clarifications",
    "pending": "Pending Clarifications",
    "pending clarifications": "Pending Clarifications",
    "resolved": "Closed",
    "closed": "Closed",
    "canceled": "Closed",
    "cancelled": "Closed",
    "reopened": "Re-Opened",
    "re-opened": "Re-Opened",
    "re opened": "Re-Opened",
}


# Function: normalize_state
def normalize_state(raw: Any) -> str:
    """Maps any raw ServiceNow state (display value or plain text) onto the
    dashboard's fixed 5-value taxonomy. Unrecognized/blank values default to
    "Open" rather than leaking an unmapped raw value into the UI's state filter."""
    text = _clean_text(raw).strip().lower()
    return _STATE_ALIASES.get(text, "Open")


# Function: _latest_servicenow_snapshot
def _latest_servicenow_snapshot() -> Path | None:
    data_dir = Path(cfg.DATA_DIR)
    if not data_dir.exists():
        return None
    files = sorted(
        data_dir.glob("servicenow_incidents_*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


# Function: _incident_from_snapshot
def _incident_from_snapshot(row: dict, source_name: str, last_synced_at: str | None) -> dict:
    sys_id = _clean_text(row.get("sys_id"))
    number = _clean_text(row.get("number"))
    close_notes = _clean_text(row.get("close_notes") or row.get("resolution_notes"))
    work_notes = _clean_text(row.get("work_notes"))
    return {
        "incident_id": sys_id or number,
        "number": number,
        "short_description": _clean_text(row.get("short_description")),
        "description": _clean_text(row.get("description")),
        "category": _clean_text(row.get("category")),
        "subcategory": _clean_text(row.get("subcategory")),
        "state": normalize_state(row.get("state")),
        "priority": _clean_text(row.get("priority")),
        "assignment_group": _clean_text(row.get("assignment_group")),
        "assigned_to": _clean_text(row.get("assigned_to")),
        "opened_at": _clean_text(row.get("opened_at")),
        "resolved_at": _clean_text(row.get("resolved_at")),
        "closed_at": _clean_text(row.get("closed_at")),
        "close_notes": close_notes,
        "work_notes": work_notes,
        "source_name": source_name,
        "last_synced_at": last_synced_at,
    }


_LOCAL_OVERRIDE_FIELDS = ("assigned_to", "state", "close_notes", "work_notes")


# Function: _local_overrides_path
def _local_overrides_path() -> Path:
    return Path(cfg.DATA_DIR) / "local_incident_overrides.json"


# Function: _load_local_overrides
def _load_local_overrides() -> dict[str, dict]:
    path = _local_overrides_path()
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


# Function: _save_local_overrides
def _save_local_overrides(overrides: dict[str, dict]) -> None:
    path = _local_overrides_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fp:
        json.dump(overrides, fp, indent=2)


# Function: _apply_override_to_incident
def _apply_override_to_incident(inc: dict, override: dict) -> dict:
    inc = dict(inc)
    for field in _LOCAL_OVERRIDE_FIELDS:
        if override.get(field) is not None:
            inc[field] = normalize_state(override[field]) if field == "state" else override[field]
    if override.get("last_synced_at"):
        inc["last_synced_at"] = override["last_synced_at"]
    return inc


# Function: _apply_local_overrides
def _apply_local_overrides(incidents: list[dict]) -> list[dict]:
    overrides = _load_local_overrides()
    if not overrides:
        return incidents

    merged = []
    for inc in incidents:
        override = overrides.get(inc.get("number"))
        merged.append(_apply_override_to_incident(inc, override) if override else inc)
    return merged


# Incidents created outside a bulk ServiceNow sync (e.g. via Omnichannel Ticket
# Intake) — _local_overrides above only ever *edits* a number that already exists
# in the synced snapshot, it can't introduce a brand new one. Without this second
# store, a ticket created through Omnichannel would be real in ServiceNow but
# invisible to the dashboard's search/list/stats until the next full resync pulls
# thousands of tickets just to pick up a handful of new ones.
# Function: _created_incidents_path
def _created_incidents_path() -> Path:
    return Path(cfg.DATA_DIR) / "local_created_incidents.json"


# Function: _load_local_created_incidents_raw
def _load_local_created_incidents_raw() -> dict[str, dict]:
    """Number -> raw stored record, for callers that need to update one entry
    in place (see update_incident_fields). Most callers want the normalized
    list from load_local_created_incidents() instead."""
    path = _created_incidents_path()
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


# Function: load_local_created_incidents
def load_local_created_incidents() -> list[dict]:
    data = _load_local_created_incidents_raw()
    return [normalize_created_incident(number, record) for number, record in data.items()]


# Function: normalize_created_incident
def normalize_created_incident(number: str, record: dict) -> dict:
    return {
        "incident_id": record.get("incident_id") or number,
        "number": number,
        "short_description": _clean_text(record.get("short_description")),
        "description": _clean_text(record.get("description")),
        "category": _clean_text(record.get("category")),
        "subcategory": _clean_text(record.get("subcategory")),
        "state": normalize_state(record.get("state")),
        "priority": _clean_text(record.get("priority")),
        "assignment_group": _clean_text(record.get("assignment_group")),
        "assigned_to": _clean_text(record.get("assigned_to")),
        "opened_at": _clean_text(record.get("opened_at")),
        "resolved_at": _clean_text(record.get("resolved_at")),
        "closed_at": _clean_text(record.get("closed_at")),
        "close_notes": _clean_text(record.get("close_notes")),
        "work_notes": _clean_text(record.get("work_notes")),
        "source_name": record.get("source_name") or "omnichannel_intake",
        "last_synced_at": record.get("last_synced_at"),
        # Passed through unchanged (not part of the standard dashboard-incident
        # shape) — see backend/api/omnichannel.py::_local_record_for_created_ticket.
        "channel": record.get("channel", ""),
        "channel_label": record.get("channel_label", ""),
        "local_ticket_id": record.get("local_ticket_id", ""),
    }


# Function: reembed_incidents
def reembed_incidents(records: list[dict], default_source_name: str = "manual_edit") -> bool:
    """Re-embeds incidents' current field values into the active vector store,
    replacing their old chunks — otherwise chat/RAG keeps answering from stale
    state/close_notes/assigned_to indefinitely after a dashboard edit or a new
    Omnichannel-created ticket. Both LanceDB's upsert_points and Qdrant's
    index_incidents_to_qdrant delete-then-add by incident id internally, so this
    is a real update, not just an additional stale copy. Mirrors the
    VECTOR_BACKEND branch in services/servicenow_sync.py::one_time_sync —
    "hybrid" is treated the same as lancedb-only there, kept consistent here."""
    if not records:
        return False
    # All records share one source_name per call (one batch = one sync/simulate
    # run) — individual records may still override it if they came from elsewhere.
    source_name = records[0].get("source_name") or default_source_name
    if cfg.VECTOR_BACKEND in {"lancedb", "hybrid"}:
        from backend.services.embedding_worker_lancedb import index_incidents_to_lancedb
        index_incidents_to_lancedb(records, source_name)
        return True
    if cfg.VECTOR_BACKEND == "qdrant":
        from backend.services.embedding_worker import index_incidents_to_qdrant
        index_incidents_to_qdrant(records, source_name, cfg.LLM_PROVIDER)
        return True
    return False


# Function: persist_created_incidents
def persist_created_incidents(records: list[dict]) -> None:
    """Adds/updates records in the created-incidents store, keyed by ServiceNow
    number. Safe to call with records that already exist (re-simulating the same
    ticket_id twice, or a later edit) — later calls simply overwrite."""
    if not records:
        return
    path = _created_incidents_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    existing: dict[str, dict] = {}
    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as fp:
                loaded = json.load(fp)
            if isinstance(loaded, dict):
                existing = loaded
        except (json.JSONDecodeError, OSError):
            existing = {}

    for record in records:
        number = _clean_text(record.get("number"))
        if not number:
            continue
        existing[number] = record

    with path.open("w", encoding="utf-8") as fp:
        json.dump(existing, fp, indent=2)


# Function: _parse_snapshot_lines
def _parse_snapshot_lines(fp, snapshot_name: str, last_synced_at: str) -> list[dict]:
    incidents = []
    for line in fp:
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            incidents.append(_incident_from_snapshot(row, snapshot_name, last_synced_at))
    return incidents


# Function: _load_local_snapshot_incidents
def _load_local_snapshot_incidents() -> list[dict]:
    snapshot = _latest_servicenow_snapshot()
    if snapshot is None:
        return []

    stat = snapshot.stat()
    cached_path = _LOCAL_SNAPSHOT_CACHE.get("path")
    cached_mtime = _LOCAL_SNAPSHOT_CACHE.get("mtime")
    if cached_path == str(snapshot) and cached_mtime == stat.st_mtime:
        incidents = list(_LOCAL_SNAPSHOT_CACHE.get("records") or [])
    else:
        last_synced_at = datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()
        with snapshot.open("r", encoding="utf-8") as fp:
            incidents = _parse_snapshot_lines(fp, snapshot.name, last_synced_at)

        _LOCAL_SNAPSHOT_CACHE.update({"path": str(snapshot), "mtime": stat.st_mtime, "records": incidents})
        logger.info("Loaded %d incidents for local dashboard from %s", len(incidents), snapshot)

    return _apply_local_overrides(incidents)


# Function: _filter_local_incidents
def _filter_local_incidents(
    incidents: list[dict],
    search: str | None = None,
    state_filter: str | None = None,
    assigned_to_filter: str | None = None,
) -> list[dict]:
    out = incidents
    if search:
        needle = search.strip().lower()
        searchable_fields = (
            "number",
            "short_description",
            "description",
            "category",
            "subcategory",
            "state",
            "assigned_to",
            "assignment_group",
            "close_notes",
            "work_notes",
        )
        out = [
            inc
            for inc in out
            if any(needle in str(inc.get(field) or "").lower() for field in searchable_fields)
        ]
    if state_filter:
        out = [inc for inc in out if str(inc.get("state") or "") == state_filter]
    if assigned_to_filter:
        out = [inc for inc in out if str(inc.get("assigned_to") or "") == assigned_to_filter]
    return out


# Function: start_sync_log
def start_sync_log(source_name: str, query: str, limit: int) -> int:
    if cfg.DB_BACKEND not in {"postgres", "postgresql"}:
        return 0

    ensure_common_schema()
    now = _utc_now()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sn_sync_logs (
                    source_name,
                    sync_started_at,
                    status,
                    incidents_count,
                    requests_count,
                    kb_count,
                    qdrant_points_indexed,
                    details_json
                )
                VALUES (%s, %s, 'running', 0, 0, 0, 0, %s::jsonb)
                RETURNING id
                """,
                (
                    source_name,
                    now,
                    json.dumps(
                        {
                            "query": query,
                            "limit": int(limit),
                        },
                        ensure_ascii=True,
                    ),
                ),
            )
            sync_log_id = int(cur.fetchone()[0])
        conn.commit()
    return sync_log_id


# Function: finalize_sync_log
def finalize_sync_log(
    sync_log_id: int,
    *,
    status: str,
    incidents_count: int = 0,
    requests_count: int = 0,
    kb_count: int = 0,
    qdrant_points_indexed: int = 0,
    details: dict[str, Any] | None = None,
) -> None:
    if cfg.DB_BACKEND not in {"postgres", "postgresql"}:
        return

    ensure_common_schema()
    now = _utc_now()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE sn_sync_logs
                SET
                    sync_completed_at = %s,
                    status = %s,
                    incidents_count = %s,
                    requests_count = %s,
                    kb_count = %s,
                    qdrant_points_indexed = %s,
                    details_json = %s::jsonb
                WHERE id = %s
                """,
                (
                    now,
                    status,
                    int(incidents_count),
                    int(requests_count),
                    int(kb_count),
                    int(qdrant_points_indexed),
                    json.dumps(details or {}, ensure_ascii=True),
                    int(sync_log_id),
                ),
            )
        conn.commit()


# Function: persist_incidents
def persist_incidents(records: list[dict], source_name: str, sync_log_id: int) -> int:
    if cfg.DB_BACKEND not in {"postgres", "postgresql"}:
        logger.info("Skipping PostgreSQL incident persistence because DB_BACKEND=%s", cfg.DB_BACKEND)
        return 0

    ensure_common_schema()
    if not records:
        return 0

    now = _utc_now()

    with get_connection() as conn:
        with conn.cursor() as cur:
            for row in records:
                sys_id = _clean_text(row.get("sys_id"))
                number = _clean_text(row.get("number"))
                if not sys_id and not number:
                    continue

                incident_id = sys_id or number
                short_description = _clean_text(row.get("short_description"))
                description = _clean_text(row.get("description"))
                category = _clean_text(row.get("category"))
                subcategory = _clean_text(row.get("subcategory"))
                state = normalize_state(row.get("state"))
                priority = _clean_text(row.get("priority"))
                assignment_group = _clean_text(row.get("assignment_group"))
                assigned_to = _clean_text(row.get("assigned_to"))
                close_notes = _clean_text(row.get("close_notes"))
                work_notes = _clean_text(row.get("work_notes"))

                cur.execute(
                    """
                    INSERT INTO sn_incidents (
                        incident_id,
                        number,
                        short_description,
                        description,
                        category,
                        subcategory,
                        state,
                        priority,
                        assignment_group,
                        assigned_to,
                        opened_at,
                        resolved_at,
                        closed_at,
                        close_notes,
                        work_notes,
                        source_name,
                        raw_json,
                        last_synced_at,
                        sync_log_id
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s
                    )
                    ON CONFLICT (incident_id)
                    DO UPDATE SET
                        number = EXCLUDED.number,
                        short_description = EXCLUDED.short_description,
                        description = EXCLUDED.description,
                        category = EXCLUDED.category,
                        subcategory = EXCLUDED.subcategory,
                        state = EXCLUDED.state,
                        priority = EXCLUDED.priority,
                        assignment_group = EXCLUDED.assignment_group,
                        assigned_to = EXCLUDED.assigned_to,
                        opened_at = EXCLUDED.opened_at,
                        resolved_at = EXCLUDED.resolved_at,
                        closed_at = EXCLUDED.closed_at,
                        close_notes = EXCLUDED.close_notes,
                        work_notes = EXCLUDED.work_notes,
                        source_name = EXCLUDED.source_name,
                        raw_json = EXCLUDED.raw_json,
                        last_synced_at = EXCLUDED.last_synced_at,
                        sync_log_id = EXCLUDED.sync_log_id
                    """,
                    (
                        incident_id,
                        number,
                        short_description,
                        description,
                        category,
                        subcategory,
                        state,
                        priority,
                        assignment_group,
                        assigned_to,
                        _clean_text(row.get("opened_at")),
                        _clean_text(row.get("resolved_at")),
                        _clean_text(row.get("closed_at")),
                        close_notes,
                        work_notes,
                        source_name,
                        json.dumps(row, ensure_ascii=True),
                        now,
                        int(sync_log_id),
                    ),
                )

                if category:
                    cur.execute(
                        """
                        INSERT INTO sn_category_metadata(category_name, last_seen_at)
                        VALUES (%s, %s)
                        ON CONFLICT (category_name)
                        DO UPDATE SET last_seen_at = EXCLUDED.last_seen_at
                        """,
                        (category, now),
                    )

                if assignment_group:
                    cur.execute(
                        """
                        INSERT INTO sn_group_metadata(group_name, last_seen_at)
                        VALUES (%s, %s)
                        ON CONFLICT (group_name)
                        DO UPDATE SET last_seen_at = EXCLUDED.last_seen_at
                        """,
                        (assignment_group, now),
                    )

                if assigned_to:
                    cur.execute(
                        """
                        INSERT INTO sn_user_metadata(user_name, last_seen_at)
                        VALUES (%s, %s)
                        ON CONFLICT (user_name)
                        DO UPDATE SET last_seen_at = EXCLUDED.last_seen_at
                        """,
                        (assigned_to, now),
                    )

        conn.commit()

    return len(records)


# Function: count_incidents_by_source
def count_incidents_by_source(source_name: str) -> int:
    if cfg.DB_BACKEND not in {"postgres", "postgresql"}:
        return 0

    ensure_common_schema()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM sn_incidents WHERE source_name = %s",
                (str(source_name or ""),),
            )
            value = int(cur.fetchone()[0] or 0)
        conn.commit()
    return value


# Function: get_all_incidents
def get_all_incidents(
    limit: int = 100, 
    offset: int = 0, 
    search: str | None = None,
    state_filter: str | None = None,
    assigned_to_filter: str | None = None
) -> tuple[list[dict], int]:
    """
    Retrieve paginated list of incidents from the database with optional filters.
    Returns tuple of (incidents list, total count).
    
    Args:
        limit: Number of results to return
        offset: Number of results to skip
        search: Free text search across number, description, category, state
        state_filter: Filter by exact state value
        assigned_to_filter: Filter by exact assigned_to value
    """
    if cfg.DB_BACKEND not in {"postgres", "postgresql"}:
        # Created incidents first — they're the most recently-arrived tickets, and this
        # is also what makes a just-simulated Omnichannel ticket show up on page 1 of
        # search/list without needing to know its position among 5,000 synced rows.
        all_incidents = load_local_created_incidents() + _load_local_snapshot_incidents()
        local_incidents = _filter_local_incidents(
            all_incidents,
            search=search,
            state_filter=state_filter,
            assigned_to_filter=assigned_to_filter,
        )
        total = len(local_incidents)
        return local_incidents[int(offset) : int(offset) + int(limit)], total

    ensure_common_schema()
    incidents = []
    total = 0
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Build query with optional filters
            where_conditions = []
            params_count = []
            params_select = []
            
            # Free text search filter
            if search:
                search_pattern = f"%{search}%"
                where_conditions.append("""
                    (number ILIKE %s OR 
                     short_description ILIKE %s OR 
                     description ILIKE %s OR
                     category ILIKE %s OR
                     subcategory ILIKE %s OR
                     state ILIKE %s OR
                     assigned_to ILIKE %s OR
                     assignment_group ILIKE %s OR
                     close_notes ILIKE %s OR
                     work_notes ILIKE %s)
                """)
                params_count.extend([search_pattern] * 10)
                params_select.extend([search_pattern] * 10)
            
            # State filter
            if state_filter:
                where_conditions.append("state = %s")
                params_count.append(state_filter)
                params_select.append(state_filter)
            
            # Assigned to filter
            if assigned_to_filter:
                where_conditions.append("assigned_to = %s")
                params_count.append(assigned_to_filter)
                params_select.append(assigned_to_filter)
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # Add limit and offset to select params
            params_select.extend([int(limit), int(offset)])
            
            # Get total count
            cur.execute(
                f"SELECT COUNT(*) FROM sn_incidents {where_clause}",
                params_count
            )
            total = int(cur.fetchone()[0] or 0)
            
            # Get paginated results
            cur.execute(
                f"""
                SELECT 
                    incident_id,
                    number,
                    short_description,
                    description,
                    category,
                    subcategory,
                    state,
                    priority,
                    assignment_group,
                    assigned_to,
                    opened_at,
                    resolved_at,
                    closed_at,
                    close_notes,
                    work_notes,
                    source_name,
                    last_synced_at
                FROM sn_incidents
                {where_clause}
                ORDER BY last_synced_at DESC, number DESC
                LIMIT %s OFFSET %s
                """,
                params_select
            )
            
            rows = cur.fetchall()
            for row in rows:
                incidents.append({
                    "incident_id": row[0],
                    "number": row[1],
                    "short_description": row[2],
                    "description": row[3],
                    "category": row[4],
                    "subcategory": row[5],
                    "state": row[6],
                    "priority": row[7],
                    "assignment_group": row[8],
                    "assigned_to": row[9],
                    "opened_at": row[10],
                    "resolved_at": row[11],
                    "closed_at": row[12],
                    "close_notes": row[13],
                    "work_notes": row[14],
                    "source_name": row[15],
                    "last_synced_at": str(row[16]) if row[16] else None,
                })
        
        conn.commit()
    
    return incidents, total


# Function: _apply_field_updates
def _apply_field_updates(
    target: dict,
    assigned_to: str | None,
    state: str | None,
    close_notes: str | None,
    work_notes: str | None,
) -> dict:
    if assigned_to is not None:
        target["assigned_to"] = assigned_to
    if state is not None:
        target["state"] = normalize_state(state)
    if close_notes is not None:
        target["close_notes"] = close_notes
    if work_notes is not None:
        target["work_notes"] = work_notes
    return target


# Function: _update_local_created_incident
def _update_local_created_incident(
    incident_number: str,
    assigned_to: str | None,
    state: str | None,
    close_notes: str | None,
    work_notes: str | None,
) -> bool:
    existing = _load_local_created_incidents_raw()
    record = _apply_field_updates(existing.get(incident_number, {}), assigned_to, state, close_notes, work_notes)
    record["last_synced_at"] = _utc_now().isoformat()
    existing[incident_number] = record
    path = _created_incidents_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fp:
        json.dump(existing, fp, indent=2)
    return True


# Function: _update_local_override_incident
def _update_local_override_incident(
    incident_number: str,
    assigned_to: str | None,
    state: str | None,
    close_notes: str | None,
    work_notes: str | None,
) -> bool:
    incidents = _load_local_snapshot_incidents()
    if not any(inc.get("number") == incident_number for inc in incidents):
        return False

    overrides = _load_local_overrides()
    entry = _apply_field_updates(overrides.get(incident_number, {}), assigned_to, state, close_notes, work_notes)
    entry["last_synced_at"] = _utc_now().isoformat()
    overrides[incident_number] = entry
    _save_local_overrides(overrides)
    return True


# Function: _build_postgres_update_fields
def _build_postgres_update_fields(
    assigned_to: str | None,
    state: str | None,
    close_notes: str | None,
    work_notes: str | None,
) -> tuple[list, list]:
    update_fields = []
    params = []

    if assigned_to is not None:
        update_fields.append("assigned_to = %s")
        params.append(assigned_to)

    if state is not None:
        update_fields.append("state = %s")
        params.append(normalize_state(state))

    if close_notes is not None:
        update_fields.append("close_notes = %s")
        params.append(close_notes)

    if work_notes is not None:
        update_fields.append("work_notes = %s")
        params.append(work_notes)

    return update_fields, params


# Function: _update_postgres_incident_fields
def _update_postgres_incident_fields(
    incident_number: str,
    assigned_to: str | None,
    state: str | None,
    close_notes: str | None,
    work_notes: str | None,
) -> bool:
    ensure_common_schema()

    # Build update query dynamically based on provided fields
    update_fields, params = _build_postgres_update_fields(assigned_to, state, close_notes, work_notes)

    if not update_fields:
        # No fields to update
        return True

    # Add last_synced_at update
    update_fields.append("last_synced_at = %s")
    params.append(_utc_now())

    # Add incident_number for WHERE clause
    params.append(incident_number)

    with get_connection() as conn:
        with conn.cursor() as cur:
            query = f"""
                UPDATE sn_incidents
                SET {', '.join(update_fields)}
                WHERE number = %s
            """
            cur.execute(query, params)
            rows_updated = cur.rowcount
        conn.commit()

    return rows_updated > 0


# Function: update_incident_fields
def update_incident_fields(
    incident_number: str,
    assigned_to: str | None = None,
    state: str | None = None,
    close_notes: str | None = None,
    work_notes: str | None = None
) -> bool:
    """
    Update specific fields of an incident in the database.

    Args:
        incident_number: Incident number (e.g., INC0012345)
        assigned_to: New assigned_to value
        state: New state value
        close_notes: New close_notes value
        work_notes: New work_notes value

    Returns:
        bool: True if update succeeded, False if incident not found
    """
    if cfg.DB_BACKEND not in {"postgres", "postgresql"}:
        # Local/sqlite mode: incidents bulk-synced from ServiceNow are a read-only
        # JSONL snapshot, so edits to THOSE are persisted in a side-car overrides file
        # and layered back on top by _apply_local_overrides(). Incidents created via
        # Omnichannel Ticket Intake live in a separate created-incidents store (they
        # were never part of any snapshot) — edit that store directly instead.
        created_numbers = {inc["number"] for inc in load_local_created_incidents()}
        if incident_number in created_numbers:
            return _update_local_created_incident(incident_number, assigned_to, state, close_notes, work_notes)
        return _update_local_override_incident(incident_number, assigned_to, state, close_notes, work_notes)

    return _update_postgres_incident_fields(incident_number, assigned_to, state, close_notes, work_notes)
