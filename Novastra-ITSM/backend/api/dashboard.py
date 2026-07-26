# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Dashboard API endpoints for viewing and managing synced tickets.
# Date: 2025-08-19
# ---------------------------------------------------------------------------
"""
Dashboard API endpoints for viewing and managing synced tickets.
"""
import asyncio
import logging
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional
from pydantic import BaseModel

import backend.config as cfg
from backend.services.operational_ingestion import CANONICAL_STATES, get_all_incidents, reembed_incidents

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])
logger = logging.getLogger(__name__)


class IncidentUpdateRequest(BaseModel):
    """Request model for updating incident fields"""
    incident_number: str
    assigned_to: Optional[str] = None
    state: Optional[str] = None
    close_notes: Optional[str] = None
    work_notes: Optional[str] = None
    sync_to_servicenow: bool = False


# Function: list_incidents
@router.get("/incidents")
async def list_incidents(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    search: Optional[str] = Query(default=None, max_length=200),
    state: Optional[str] = Query(default=None, max_length=100),
    assigned_to: Optional[str] = Query(default=None, max_length=200),
):
    """
    Get paginated list of all synced ServiceNow incidents with filters.
    
    Query parameters:
    - limit: Number of results per page (1-1000, default: 100)
    - offset: Number of results to skip (default: 0)
    - search: Optional free text search across all fields
    - state: Filter by exact state value
    - assigned_to: Filter by exact assigned_to value
    
    Returns:
    - incidents: List of incident objects
    - total: Total count of incidents matching filters
    - limit: Requested page size
    - offset: Requested offset
    """
    try:
        incidents, total = get_all_incidents(
            limit=limit,
            offset=offset,
            search=search,
            state_filter=state,
            assigned_to_filter=assigned_to
        )
        
        return {
            "incidents": incidents,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as exc:
        logger.exception("Failed to retrieve incidents for dashboard")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve incidents: {exc}"
        )


# Function: get_filter_options
@router.get("/filter-options")
async def get_filter_options():
    """
    Get available filter options for dashboard filters.

    Returns:
    - states: the fixed 5-value state taxonomy (CANONICAL_STATES), always all five
      regardless of which states any ticket currently has — so e.g. "Open" is always
      selectable even before any ticket has been created with that state.
    - assigned_to: List of unique assigned_to values actually present in the data
    """
    try:
        if cfg.DB_BACKEND not in {"postgres", "postgresql"}:
            incidents, _ = get_all_incidents(limit=100000, offset=0)
            assignees = sorted({str(inc.get("assigned_to") or "") for inc in incidents if inc.get("assigned_to")})
            return {"states": CANONICAL_STATES, "assigned_to": assignees[:100]}

        from backend.services.postgres_store import ensure_common_schema, get_connection

        ensure_common_schema()
        options = {"states": CANONICAL_STATES}

        with get_connection() as conn:
            with conn.cursor() as cur:
                # Get unique assigned_to values (top 100 most common)
                cur.execute("""
                    SELECT DISTINCT assigned_to, COUNT(*) as cnt
                    FROM sn_incidents 
                    WHERE assigned_to IS NOT NULL AND assigned_to != ''
                    GROUP BY assigned_to
                    ORDER BY cnt DESC
                    LIMIT 100
                """)
                options["assigned_to"] = [row[0] for row in cur.fetchall()]
            
            conn.commit()
        
        return options
    except Exception as exc:
        logger.exception("Failed to retrieve filter options")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve filter options: {exc}"
        )


# Function: get_incident
@router.get("/incidents/{incident_number}")
async def get_incident(incident_number: str):
    """
    Get details of a specific incident by number (e.g., INC0012345).
    
    Returns the full incident details including description, category, state, etc.
    """
    try:
        incidents, _ = get_all_incidents(limit=1, offset=0, search=incident_number)
        
        if not incidents:
            raise HTTPException(
                status_code=404,
                detail=f"Incident {incident_number} not found"
            )
        
        # Find exact match
        incident = next(
            (inc for inc in incidents if inc.get("number") == incident_number),
            None
        )
        
        if not incident:
            # If no exact match, return the first result (partial match)
            incident = incidents[0]
        
        return incident
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Failed to retrieve incident {incident_number}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve incident: {exc}"
        )


# Function: _top_counts
def _top_counts(incidents: list, field: str, label: str, limit: int = 10):
    counts: dict[str, int] = {}
    for inc in incidents:
        value = str(inc.get(field) or "").strip()
        if value:
            counts[value] = counts.get(value, 0) + 1
    return [
        {label: value, "count": count}
        for value, count in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:limit]
    ]


# Function: _get_dashboard_stats_local
def _get_dashboard_stats_local():
    incidents, total = get_all_incidents(limit=100000, offset=0)

    by_source: dict[str, int] = {}
    for inc in incidents:
        source = str(inc.get("source_name") or "").strip()
        if source:
            by_source[source] = by_source.get(source, 0) + 1

    return {
        "total_incidents": total,
        "by_state": _top_counts(incidents, "state", "state"),
        "by_category": _top_counts(incidents, "category", "category"),
        "by_priority": _top_counts(incidents, "priority", "priority"),
        "by_source": [
            {"source": source, "count": count}
            for source, count in sorted(by_source.items(), key=lambda item: item[0], reverse=True)[:5]
        ],
    }


# Function: _get_dashboard_stats_postgres
def _get_dashboard_stats_postgres():
    from backend.services.postgres_store import ensure_common_schema, get_connection

    ensure_common_schema()
    stats = {}

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Total incidents
            cur.execute("SELECT COUNT(*) FROM sn_incidents")
            stats["total_incidents"] = int(cur.fetchone()[0] or 0)

            # By state
            cur.execute("""
                SELECT state, COUNT(*)
                FROM sn_incidents
                WHERE state IS NOT NULL AND state != ''
                GROUP BY state
                ORDER BY COUNT(*) DESC
                LIMIT 10
            """)
            stats["by_state"] = [
                {"state": row[0], "count": int(row[1])}
                for row in cur.fetchall()
            ]

            # By category
            cur.execute("""
                SELECT category, COUNT(*)
                FROM sn_incidents
                WHERE category IS NOT NULL AND category != ''
                GROUP BY category
                ORDER BY COUNT(*) DESC
                LIMIT 10
            """)
            stats["by_category"] = [
                {"category": row[0], "count": int(row[1])}
                for row in cur.fetchall()
            ]

            # By priority
            cur.execute("""
                SELECT priority, COUNT(*)
                FROM sn_incidents
                WHERE priority IS NOT NULL AND priority != ''
                GROUP BY priority
                ORDER BY priority
            """)
            stats["by_priority"] = [
                {"priority": row[0], "count": int(row[1])}
                for row in cur.fetchall()
            ]

            # Recent syncs
            cur.execute("""
                SELECT source_name, COUNT(*)
                FROM sn_incidents
                GROUP BY source_name
                ORDER BY source_name DESC
                LIMIT 5
            """)
            stats["by_source"] = [
                {"source": row[0], "count": int(row[1])}
                for row in cur.fetchall()
            ]

        conn.commit()

    return stats


# Function: get_dashboard_stats
@router.get("/stats")
async def get_dashboard_stats():
    """
    Get summary statistics for the dashboard.

    Returns counts by category, state, priority, etc.
    """
    try:
        if cfg.DB_BACKEND not in {"postgres", "postgresql"}:
            return _get_dashboard_stats_local()

        return _get_dashboard_stats_postgres()
    except Exception as exc:
        logger.exception("Failed to retrieve dashboard statistics")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve statistics: {exc}"
        )


# Function: _build_updated_fields
def _build_updated_fields(update_data: IncidentUpdateRequest) -> dict:
    updated_fields = {}
    if update_data.assigned_to is not None:
        updated_fields["assigned_to"] = update_data.assigned_to
    if update_data.state is not None:
        updated_fields["state"] = update_data.state
    if update_data.close_notes is not None:
        updated_fields["close_notes"] = update_data.close_notes
    if update_data.work_notes is not None:
        updated_fields["work_notes"] = update_data.work_notes
    return updated_fields


# Function: _build_servicenow_update_payload
def _build_servicenow_update_payload(update_data: IncidentUpdateRequest) -> dict:
    update_payload = {}
    if update_data.assigned_to is not None:
        update_payload["assigned_to"] = update_data.assigned_to
    if update_data.state is not None:
        # Dashboard state (backend/services/operational_ingestion.py's
        # CANONICAL_STATES) -> ServiceNow's own state codes. "Re-Opened"
        # has no distinct SN state; a reopened ticket is active again,
        # so it maps to the same code as "In-Progress".
        state_map = {
            "Open": "1", "In-Progress": "2", "Pending Clarifications": "3",
            "Closed": "7", "Re-Opened": "2",
        }
        update_payload["state"] = state_map.get(update_data.state, "1")
    if update_data.close_notes is not None:
        update_payload["close_notes"] = update_data.close_notes
    if update_data.work_notes is not None:
        update_payload["work_notes"] = update_data.work_notes

    # This instance's Data Policy rejects state=7 (Closed) with a 403
    # unless close_code + a non-empty close_notes are present in the
    # SAME request — confirmed live against dev394189. Without this, any
    # edit that sets state to "Closed" without also typing close_notes
    # would fail ServiceNow sync (result["servicenow_error"]) while local
    # storage and the vector store below still updated, leaving them
    # silently out of sync with the real ServiceNow record.
    if update_payload.get("state") == "7":
        update_payload.setdefault("close_code", "Solution provided")
        if not update_payload.get("close_notes"):
            update_payload["close_notes"] = "Closed via Novastra-ITSM Dashboard."

    return update_payload


# Function: _sync_incident_to_servicenow
async def _sync_incident_to_servicenow(incident_number: str, update_data: IncidentUpdateRequest) -> dict:
    """Look up the incident in ServiceNow and PATCH it. Returns servicenow_* result fields."""
    import backend.config as cfg
    import httpx

    sync_result: dict = {"servicenow_synced": False}
    try:
        lookup_url = f"{cfg.SERVICENOW_BASE_URL}/api/now/table/incident"
        async with httpx.AsyncClient() as client:
            lookup_response = await client.get(
                lookup_url,
                params={
                    "sysparm_query": f"number={incident_number}",
                    "sysparm_limit": "1",
                    "sysparm_fields": "sys_id,number"
                },
                auth=(cfg.SERVICENOW_USERNAME, cfg.SERVICENOW_PASSWORD),
                timeout=15.0
            )
            lookup_response.raise_for_status()
            lookup_data = lookup_response.json()

            if not lookup_data.get("result"):
                logger.warning(f"Incident {incident_number} not found in ServiceNow")
                return sync_result

            sys_id = lookup_data["result"][0]["sys_id"]
            update_payload = _build_servicenow_update_payload(update_data)

            if update_payload:
                update_url = f"{lookup_url}/{sys_id}"
                update_response = await client.patch(
                    update_url,
                    json=update_payload,
                    auth=(cfg.SERVICENOW_USERNAME, cfg.SERVICENOW_PASSWORD),
                    timeout=15.0
                )
                update_response.raise_for_status()
                sync_result["servicenow_synced"] = True
                logger.info(f"Successfully synced {incident_number} to ServiceNow")

    except Exception as exc:
        logger.error(f"Failed to sync to ServiceNow: {exc}")
        sync_result["servicenow_error"] = str(exc)

    return sync_result


# Function: _reembed_updated_incident
async def _reembed_updated_incident(incident_number: str) -> dict:
    """Re-embed the edited incident so chat/RAG stops answering from the pre-edit state."""
    reembed_result: dict = {"vector_db_updated": False}
    try:
        updated_incidents, _ = get_all_incidents(limit=1, offset=0, search=incident_number)
        updated_record = next(
            (inc for inc in updated_incidents if inc.get("number") == incident_number), None
        )
        if updated_record is not None:
            reembed_result["vector_db_updated"] = await asyncio.to_thread(
                reembed_incidents, [updated_record], "manual_edit"
            )
    except Exception as exc:
        logger.error(f"Failed to re-embed {incident_number} into the vector store: {exc}")
        reembed_result["vector_db_error"] = str(exc)
    return reembed_result


# Function: update_incident
@router.put("/incidents/{incident_number}")
async def update_incident(incident_number: str, update_data: IncidentUpdateRequest):
    """
    Update incident fields in the local database and optionally sync to ServiceNow.

    Updates one or more fields:
    - assigned_to: User assigned to the incident
    - state: One of Open, In-Progress, Pending Clarifications, Closed, Re-Opened
      (see operational_ingestion.CANONICAL_STATES) — any other value normalizes to "Open".
    - close_notes: Resolution notes
    - work_notes: Work notes

    If sync_to_servicenow is True, will attempt to update ServiceNow via API.
    """
    try:
        from backend.services.operational_ingestion import update_incident_fields
        import backend.config as cfg

        # Update local database
        success = update_incident_fields(
            incident_number=incident_number,
            assigned_to=update_data.assigned_to,
            state=update_data.state,
            close_notes=update_data.close_notes,
            work_notes=update_data.work_notes
        )

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Incident {incident_number} not found"
            )

        result = {
            "success": True,
            "incident_number": incident_number,
            "updated_fields": _build_updated_fields(update_data),
            "servicenow_synced": False
        }

        # Sync to ServiceNow if requested and credentials available
        if update_data.sync_to_servicenow and all([
            cfg.SERVICENOW_BASE_URL,
            cfg.SERVICENOW_USERNAME,
            cfg.SERVICENOW_PASSWORD
        ]):
            result.update(await _sync_incident_to_servicenow(incident_number, update_data))

        result.update(await _reembed_updated_incident(incident_number))

        return result

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Failed to update incident {incident_number}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update incident: {exc}"
        )
