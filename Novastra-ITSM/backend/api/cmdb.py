# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: CMDB Intelligence: ServiceNow ingestion, validated queries and analysis.
# Date: 2025-08-13
# ---------------------------------------------------------------------------
"""CMDB Intelligence: ServiceNow ingestion, validated queries and analysis."""
from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, Literal

import httpx
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator, model_validator

import backend.config as cfg
from backend.api.auth import get_current_user
from backend.services import cmdb_store

router = APIRouter(prefix="/api/cmdb", tags=["CMDB Intelligence"])
logger = logging.getLogger(__name__)
_LLM_TIMEOUT = 60

Entity = Literal["ci", "relation", "incident", "change", "asset", "license"]
Operator = Literal["equals", "contains", "older_than", "related_to"]

FIELDS: dict[str, set[str]] = {
    "ci": {"sys_id", "name", "sys_class_name", "operational_status", "install_status", "environment", "os", "last_discovered", "sys_updated_on"},
    "relation": {"sys_id", "parent", "child", "type", "sys_updated_on"},
    "incident": {"sys_id", "number", "short_description", "description", "category", "subcategory", "state", "priority", "assignment_group", "assigned_to", "cmdb_ci", "business_service", "opened_at", "resolved_at", "closed_at", "sys_updated_on"},
    "change": {"sys_id", "number", "short_description", "description", "state", "risk", "type", "cmdb_ci", "start_date", "end_date", "sys_updated_on"},
    "asset": {"sys_id", "asset_tag", "display_name", "model", "model_category", "install_status", "assigned_to", "location", "cost", "sys_updated_on"},
    "license": {"sys_id", "name", "display_name", "software_model", "rights", "allocated", "active_rights", "unit_cost", "cost", "sys_updated_on"},
}

TABLES: dict[str, tuple[str, str]] = {
    "ci": ("cmdb_ci", ",".join(sorted(FIELDS["ci"]))),
    "relation": ("cmdb_rel_ci", ",".join(sorted(FIELDS["relation"]))),
    "incident": ("incident", ",".join(sorted(FIELDS["incident"]))),
    "change": ("change_request", ",".join(sorted(FIELDS["change"]))),
    "asset": ("alm_asset", ",".join(sorted(FIELDS["asset"]))),
    "license": ("alm_license", ",".join(sorted(FIELDS["license"]))),
}


class CMDBFilter(BaseModel):
    field: str
    operator: Operator
    value: str | int | float


class CMDBQuery(BaseModel):
    entity: Entity = "ci"
    filters: list[CMDBFilter] = Field(default_factory=list, max_length=10)
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=200)

    # Function: validate_fields
    @model_validator(mode="after")
    def validate_fields(self):
        allowed = FIELDS[self.entity]
        for item in self.filters:
            if item.field not in allowed:
                raise ValueError(f"Field '{item.field}' is not allowed for entity '{self.entity}'")
            if item.operator == "older_than" and not isinstance(item.value, (int, float)):
                try:
                    item.value = int(item.value)
                except ValueError as exc:
                    raise ValueError("older_than requires an integer number of days") from exc
        return self


class IngestRequest(BaseModel):
    base_url: str
    username: str
    password: str
    limit_per_table: int = Field(2000, ge=1, le=10000)
    page_size: int = Field(500, ge=1, le=1000)
    tables: list[Entity] = Field(default_factory=lambda: list(TABLES))
    verify_ssl: bool = True

    # Function: normalize_url
    @field_validator("base_url")
    @classmethod
    def normalize_url(cls, value: str) -> str:
        value = value.strip().rstrip("/")
        if not value.startswith(("https://", "http://")):
            value = "https://" + value
        return value


class StatusResponse(BaseModel):
    ready: bool
    counts: dict[str, int]
    total_records: int
    last_synced_at: str | None = None


class QueryResponse(BaseModel):
    nl_query: str
    structured_query: dict[str, Any]
    explanation: str
    estimated_record_count: int
    sample_results: list[dict[str, Any]]
    result_page: dict[str, Any]
    llm_used: bool


class RelationshipResponse(BaseModel):
    suggested_relationships: list[dict[str, Any]]
    missing_count: int
    authoritative_relationship_count: int
    incident_counts_by_ci: dict[str, int]
    source_counts: dict[str, int]
    llm_used: bool


class LicenseResponse(BaseModel):
    opportunities: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    asset_count: int
    license_count: int
    total_annual_saving_usd: float
    llm_used: bool


# Function: _call_llm
def _call_llm(system_msg: str, user_msg: str) -> str:
    from langchain_ollama import ChatOllama

    llm = ChatOllama(
        model=cfg.OLLAMA_MODEL,
        base_url=cfg.OLLAMA_BASE_URL,
        temperature=0,
        num_predict=384,
        num_ctx=4096,
        format="json",
        timeout=_LLM_TIMEOUT,
        keep_alive=cfg.OLLAMA_KEEP_ALIVE,
    )
    result = llm.invoke([("system", system_msg), ("human", user_msg)])
    return result.content if hasattr(result, "content") else str(result)


# Function: _extract_json
def _extract_json(raw: str) -> dict[str, Any]:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I)
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            try:
                value = json.loads(text[start:end + 1])
                return value if isinstance(value, dict) else {}
            except json.JSONDecodeError:
                pass
    return {}


# Function: _heuristic_query
def _heuristic_query(text: str, page: int, page_size: int) -> CMDBQuery:
    lower = text.casefold()
    entity: Entity = "incident" if any(word in lower for word in ("ticket", "incident")) else "change" if "change" in lower else "asset" if "asset" in lower else "license" if "licen" in lower else "ci"
    filters: list[CMDBFilter] = []
    related = re.search(r"(?:related to|containing|about)\s+['\"]?([\w ._-]+)", text, re.I)
    if related:
        filters.append(CMDBFilter(field="short_description" if entity == "incident" else "name", operator="related_to", value=related.group(1).strip()))
    if "windows" in lower and entity == "ci":
        filters.append(CMDBFilter(field="os", operator="contains", value="Windows"))
    if "production" in lower and entity == "ci":
        filters.append(CMDBFilter(field="environment", operator="equals", value="Production"))
    older = re.search(r"older than\s+(\d+)\s+days", lower)
    if older:
        date_field = "last_discovered" if entity == "ci" else "sys_updated_on"
        filters.append(CMDBFilter(field=date_field, operator="older_than", value=int(older.group(1))))
    return CMDBQuery(entity=entity, filters=filters, page=page, page_size=page_size)


# Function: _translate_query
async def _translate_query(text: str, page: int, page_size: int) -> tuple[CMDBQuery, str, bool]:
    schema = {entity: sorted(fields) for entity, fields in FIELDS.items()}
    system = (
        "Translate the request into strict JSON with keys entity and filters. "
        "entity must be ci, relation, incident, change, asset, or license. Each filter has "
        "field, operator (equals|contains|older_than|related_to), and value. Use only these fields: "
        + json.dumps(schema)
    )
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system, text), timeout=_LLM_TIMEOUT + 5)
        parsed = _extract_json(raw)
        parsed.update({"page": page, "page_size": page_size})
        query = CMDBQuery.model_validate(parsed)
        return query, "Translated by Qwen and executed against synchronized CMDB data.", True
    except Exception as exc:
        logger.warning("CMDB query translation fallback: %s", exc)
        return _heuristic_query(text, page, page_size), "Parsed deterministically and executed against synchronized CMDB data.", False


_TRANSIENT_RETRY_ATTEMPTS = 3
_TRANSIENT_RETRY_BACKOFF_SECONDS = 2


# Function: _get_page_with_retry
async def _get_page_with_retry(client: httpx.AsyncClient, request: IngestRequest, table: str, fields: str,
                                limit: int, offset: int) -> httpx.Response:
    # ServiceNow personal developer instances intermittently reject or time out
    # the first request after being idle (waking from hibernation) or under a
    # brief rate limit, then succeed immediately on retry with the same
    # credentials. Treat 401/5xx/timeouts as possibly transient and retry a
    # few times with backoff before treating it as a real credential/ACL
    # failure, instead of surfacing a one-off blip to the user every time.
    params = {"sysparm_fields": fields, "sysparm_limit": limit, "sysparm_offset": offset,
              "sysparm_display_value": "true", "sysparm_exclude_reference_link": "true"}
    for attempt in range(_TRANSIENT_RETRY_ATTEMPTS):
        is_last_attempt = attempt == _TRANSIENT_RETRY_ATTEMPTS - 1
        try:
            response = await client.get(
                f"{request.base_url}/api/now/table/{table}",
                params=params,
                auth=(request.username, request.password),
                headers={"Accept": "application/json"},
            )
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            if is_last_attempt:
                raise
            logger.warning("ServiceNow request for %s timed out (attempt %d/%d): %s",
                            table, attempt + 1, _TRANSIENT_RETRY_ATTEMPTS, exc)
            await asyncio.sleep(_TRANSIENT_RETRY_BACKOFF_SECONDS * (attempt + 1))
            continue
        if not is_last_attempt and (response.status_code == 401 or response.status_code >= 500):
            logger.warning("ServiceNow request for %s returned %d (attempt %d/%d), retrying",
                            table, response.status_code, attempt + 1, _TRANSIENT_RETRY_ATTEMPTS)
            await asyncio.sleep(_TRANSIENT_RETRY_BACKOFF_SECONDS * (attempt + 1))
            continue
        return response
    return response


# Function: _fetch_table
async def _fetch_table(client: httpx.AsyncClient, request: IngestRequest, table: str, fields: str) -> list[dict]:
    records: list[dict] = []
    for offset in range(0, request.limit_per_table, request.page_size):
        limit = min(request.page_size, request.limit_per_table - offset)
        response = await _get_page_with_retry(client, request, table, fields, limit, offset)
        if response.status_code == 401:
            # This is an upstream ServiceNow authentication failure, not an
            # expired StratIQ portal session.  Never propagate it as 401: the
            # workspace's global auth handler correctly treats 401 responses
            # as a reason to clear the portal token and redirect to login.
            raise HTTPException(
                status_code=502,
                detail=(
                    f"ServiceNow rejected the credentials or denied access to {table}. "
                    "Verify the instance URL, username/password or token, and table ACL permissions."
                ),
            )
        if response.status_code == 404:
            logger.warning("ServiceNow table %s is unavailable", table)
            return []
        response.raise_for_status()
        batch = response.json().get("result", [])
        records.extend(batch)
        if len(batch) < limit:
            break
    return records


# Function: ingest
@router.post("/ingest")
async def ingest(request: IngestRequest, current_user: dict = Depends(get_current_user)):
    counts: dict[str, int] = {}
    errors: dict[str, str] = {}
    timeout = httpx.Timeout(max(20, cfg.SERVICENOW_TIMEOUT_SECONDS))
    async with httpx.AsyncClient(timeout=timeout, verify=request.verify_ssl) as client:
        for entity in request.tables:
            table, fields = TABLES[entity]
            try:
                records = await _fetch_table(client, request, table, fields)
                counts[entity] = await asyncio.to_thread(cmdb_store.replace_entity, entity, records)
            except HTTPException as exc:
                # Upstream ServiceNow authentication/ACL failures are a sync
                # result, not a StratIQ gateway failure. Return a structured
                # response so the browser keeps the page and console clean.
                errors[entity] = str(exc.detail)
                return {
                    "status": "failed",
                    "failed_entity": entity,
                    "failed_table": table,
                    "counts": counts,
                    "errors": errors,
                    **cmdb_store.status(),
                }
            except Exception as exc:
                logger.exception("CMDB ingestion failed for %s", table)
                errors[entity] = str(exc)
    return {"status": "completed" if not errors else "partial", "counts": counts, "errors": errors, **cmdb_store.status()}


# Function: get_status
@router.get("/status", response_model=StatusResponse)
async def get_status(current_user: dict = Depends(get_current_user)):
    return cmdb_store.status()


# Function: get_default_connection
@router.get("/default-connection")
async def get_default_connection(current_user: dict = Depends(get_current_user)):
    if not cfg.SERVICENOW_BASE_URL:
        return {"configured": False}
    return {
        "configured": True,
        "base_url": cfg.SERVICENOW_BASE_URL,
        "username": cfg.SERVICENOW_USERNAME,
        "password": cfg.SERVICENOW_PASSWORD,
        "verify_ssl": cfg.SERVICENOW_VERIFY_SSL,
    }


# Function: nl_query
@router.post("/nl-query", response_model=QueryResponse)
async def nl_query(payload: dict = Body(...), current_user: dict = Depends(get_current_user)):
    text = str(payload.get("query") or "").strip()
    if not text:
        raise HTTPException(status_code=422, detail="query is required")
    page = max(1, int(payload.get("page") or 1))
    page_size = min(200, max(1, int(payload.get("page_size") or 50)))
    if payload.get("structured_query"):
        query = CMDBQuery.model_validate({**payload["structured_query"], "page": page, "page_size": page_size})
        explanation, llm_used = "Validated client query executed against synchronized CMDB data.", False
    else:
        query, explanation, llm_used = await _translate_query(text, page, page_size)
    result = await asyncio.to_thread(cmdb_store.query_records, query.entity, [f.model_dump() for f in query.filters], query.page, query.page_size)
    return {"nl_query": text, "structured_query": query.model_dump(), "explanation": explanation,
            "estimated_record_count": result["total"], "sample_results": result.pop("records"),
            "result_page": result, "llm_used": llm_used}


# Function: discover_relationships
@router.post("/discover-relationships", response_model=RelationshipResponse)
async def discover_relationships(payload: dict = Body(default={}), current_user: dict = Depends(get_current_user)):
    return await asyncio.to_thread(cmdb_store.relationship_analysis)


# Function: analyze_licenses
@router.post("/license-analysis", response_model=LicenseResponse)
async def analyze_licenses(payload: dict = Body(default={}), current_user: dict = Depends(get_current_user)):
    page = max(1, int(payload.get("page") or 1))
    page_size = min(200, max(1, int(payload.get("page_size") or 50)))
    return await asyncio.to_thread(cmdb_store.license_analysis, page, page_size)
