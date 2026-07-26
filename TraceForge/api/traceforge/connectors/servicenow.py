# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §4.1 ServiceNow connector. Built for real this pass (it was speced in Phase 3 of
# Date: 2026-06-28
# ---------------------------------------------------------------------------
"""§4.1 ServiceNow connector. Built for real this pass (it was speced in Phase 3 of
the original doc but never implemented in the previous build).

The spec is explicit about the one thing that makes or breaks this: incident data is
*tabular*, not prose. Do NOT naively embed thousands of incident rows as chunks — cluster
first, emit one synthesized 'INCIDENT PATTERN' chunk per cluster. Raw rows still land in
the `servicenow_incident` staging table so the UI can drill down to real INC numbers.
"""
from __future__ import annotations

import logging
import re
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

import httpx
import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.db.models import Chunk, Project, ServiceNowIncident, SourceDocument
from traceforge.indexing.embedder import embed_texts

logger = logging.getLogger(__name__)

INCIDENT_FIELDS = (
    "number,short_description,description,category,subcategory,u_application,"
    "cmdb_ci,priority,resolution_notes,opened_at,closed_at"
)

_PROSE_TABLES: dict[str, tuple[str, str]] = {
    # table -> (fields, doc_class)
    "sc_req_item": ("number,short_description,description,cat_item,stage,opened_at", "AS_IS_DOC"),
    "sc_task": ("number,short_description,description,state,opened_at", "AS_IS_DOC"),
    "change_request": ("number,short_description,description,state,risk,type,start_date,end_date", "AS_IS_DOC"),
    "kb_knowledge": ("number,short_description,text,topic,workflow_state", "KB_ARTICLE"),
}


class ServiceNowAuthError(Exception):
    pass


# Function: _get_table
async def _get_table(
    client: httpx.AsyncClient, base_url: str, username: str, password: str,
    table: str, fields: str, limit: int, offset: int, extra_query: str = "",
) -> list[dict]:
    params = {
        "sysparm_fields": fields, "sysparm_limit": limit, "sysparm_offset": offset,
        "sysparm_display_value": "true", "sysparm_exclude_reference_link": "true",
    }
    if extra_query:
        params["sysparm_query"] = extra_query
    response = await client.get(
        f"{base_url}/api/now/table/{table}", params=params,
        auth=(username, password), headers={"Accept": "application/json"},
    )
    if response.status_code == 401:
        raise ServiceNowAuthError(f"ServiceNow rejected credentials for table {table}")
    if response.status_code == 404:
        return []
    response.raise_for_status()
    return response.json().get("result", [])


# Function: _fetch_all
async def _fetch_all(
    client: httpx.AsyncClient, base_url: str, username: str, password: str,
    table: str, fields: str, page_size: int = 500, max_records: int = 10000, extra_query: str = "",
) -> list[dict]:
    records: list[dict] = []
    for offset in range(0, max_records, page_size):
        batch = await _get_table(client, base_url, username, password, table, fields, page_size, offset, extra_query)
        records.extend(batch)
        if len(batch) < page_size:
            break
    return records


# Function: _cluster_label
def _cluster_label(records: list[dict]) -> str:
    words = Counter()
    for r in records:
        text = str(r.get("short_description") or "")
        words.update(w.lower() for w in re.findall(r"[A-Za-z]{4,}", text))
    top = [w for w, _ in words.most_common(4)]
    return " ".join(top) if top else "uncategorised incidents"


# Function: _extract_resolution_verbs
def _extract_resolution_verbs(records: list[dict]) -> list[str]:
    verbs = Counter()
    verb_re = re.compile(r"\b(restarted|reset|patched|rebooted|updated|reconfigured|escalated|replaced|reinstalled|cleared|disabled|enabled|rolled back)\b", re.IGNORECASE)
    for r in records:
        text = str(r.get("resolution_notes") or "")
        verbs.update(m.lower() for m in verb_re.findall(text))
    return [v for v, _ in verbs.most_common(5)]


# Function: _synthesize_cluster_chunk
def _synthesize_cluster_chunk(app: str, category: str, subcategory: str, records: list[dict], window_months: int) -> str:
    label = _cluster_label(records)
    p1p2 = sum(1 for r in records if str(r.get("priority", "")).strip().startswith(("1", "2"))) or sum(
        1 for r in records if "critical" in str(r.get("priority", "")).lower() or "high" in str(r.get("priority", "")).lower()
    )
    durations = []
    for r in records:
        opened, closed = r.get("opened_at"), r.get("closed_at")
        if opened and closed:
            try:
                fmt = "%Y-%m-%d %H:%M:%S"
                delta = datetime.strptime(closed, fmt) - datetime.strptime(opened, fmt)
                durations.append(delta.total_seconds() / 3600)
            except ValueError:
                continue
    median_hours = round(sorted(durations)[len(durations) // 2], 1) if durations else None
    examples = "\n".join(f"  - {r.get('number', '?')}: {r.get('short_description', '')}" for r in records[:5])
    verbs = _extract_resolution_verbs(records)

    return (
        f"INCIDENT PATTERN: {label}\n"
        f"Application: {app or 'Unknown'}  |  Category: {category or 'Unknown'}/{subcategory or 'Unknown'}\n"
        f"Volume: {len(records)} incidents over {window_months} months ({round(100 * len(records) / max(1, len(records)), 1)}% of total)\n"
        f"Median resolution: {median_hours if median_hours is not None else 'N/A'}h  |  P1/P2 count: {p1p2}\n"
        f"Representative examples:\n{examples}\n"
        f"Common resolution actions: {', '.join(verbs) if verbs else 'not consistently recorded'}"
    )


# Function: _sub_cluster_bucket
async def _sub_cluster_bucket(bucket_records: list[dict]) -> list[list[dict]]:
    """Semantically sub-clusters a bucket's short_description via HDBSCAN when the
    bucket is large enough for it to be meaningful; otherwise returns it as one group."""
    if len(bucket_records) < 10:
        return [bucket_records]

    import hdbscan

    texts = [str(r.get("short_description") or "") for r in bucket_records]
    embeddings = await embed_texts(texts)
    if not embeddings or len(embeddings) != len(bucket_records):
        return [bucket_records]

    labels = hdbscan.HDBSCAN(min_cluster_size=3, metric="euclidean").fit_predict(np.array(embeddings))
    grouped: dict[int, list[dict]] = defaultdict(list)
    for label, record in zip(labels, bucket_records):
        grouped[int(label)].append(record)
    return list(grouped.values())


# Function: _cluster_incidents
async def _cluster_incidents(records: list[dict], window_months: int) -> list[dict]:
    """Cluster by (category, subcategory, u_application), then semantically sub-cluster
    each bucket's short_description via HDBSCAN when the bucket is large enough for it
    to be meaningful. Returns one dict per cluster: {text, incident_numbers, records}."""
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    for r in records:
        key = (r.get("category") or "", r.get("subcategory") or "", r.get("u_application") or "")
        buckets[key].append(r)

    clusters: list[dict] = []
    for (category, subcategory, app), bucket_records in buckets.items():
        sub_groups = await _sub_cluster_bucket(bucket_records)
        for sub_group in sub_groups:
            if not sub_group:
                continue
            cluster_id = str(uuid.uuid4())
            text = _synthesize_cluster_chunk(app, category, subcategory, sub_group, window_months)
            clusters.append({
                "cluster_id": cluster_id,
                "text": text,
                "incident_numbers": [r.get("number") for r in sub_group],
                "records": sub_group,
            })
    return clusters


# Function: ingest_incidents
async def ingest_incidents(
    session: AsyncSession, project_id: uuid.UUID, client: httpx.AsyncClient,
    base_url: str, username: str, password: str, window_months: int = 12,
) -> int:
    since = (datetime.now(timezone.utc) - timedelta(days=30 * window_months)).strftime("%Y-%m-%d")
    records = await _fetch_all(
        client, base_url, username, password, "incident", INCIDENT_FIELDS,
        extra_query=f"opened_at>={since}",
    )
    if not records:
        return 0

    clusters = await _cluster_incidents(records, window_months)

    doc = SourceDocument(
        project_id=project_id, source_type="SERVICENOW",
        connector_ref={"table": "incident", "base_url": base_url, "window_months": window_months},
        filename=f"ServiceNow incidents ({len(records)} rows, {len(clusters)} clusters)",
        blob_uri=f"servicenow://{base_url}/incident", sha256="0" * 64,
        doc_class="INCIDENT_DATA", status="INDEXED", ingested_at=datetime.now(timezone.utc),
    )
    session.add(doc)
    await session.flush()

    texts = [c["text"] for c in clusters]
    embeddings = await embed_texts(texts)
    for ordinal, (cluster, embedding) in enumerate(zip(clusters, embeddings)):
        session.add(Chunk(
            source_document_id=doc.id, project_id=project_id, ordinal=ordinal,
            text=cluster["text"], token_count=len(cluster["text"].split()),
            locator={"table": "incident", "cluster_id": cluster["cluster_id"], "incident_numbers": cluster["incident_numbers"]},
            embedding=embedding, chunk_metadata={"doc_class": "INCIDENT_DATA"},
        ))
        for record in cluster["records"]:
            number = record.get("number")
            if not number:
                continue
            existing = await session.execute(
                select(ServiceNowIncident).where(ServiceNowIncident.project_id == project_id, ServiceNowIncident.number == number)
            )
            if existing.scalars().first():
                continue
            session.add(ServiceNowIncident(project_id=project_id, number=number, cluster_id=cluster["cluster_id"], fields=record))

    await session.commit()
    return len(clusters)


# Function: ingest_prose_table
async def ingest_prose_table(
    session: AsyncSession, project_id: uuid.UUID, client: httpx.AsyncClient,
    base_url: str, username: str, password: str, table: str,
) -> int:
    fields, doc_class = _PROSE_TABLES[table]
    records = await _fetch_all(client, base_url, username, password, table, fields)
    if not records:
        return 0

    doc = SourceDocument(
        project_id=project_id, source_type="SERVICENOW",
        connector_ref={"table": table, "base_url": base_url},
        filename=f"ServiceNow {table} ({len(records)} rows)",
        blob_uri=f"servicenow://{base_url}/{table}", sha256="0" * 64,
        doc_class=doc_class, status="INDEXED", ingested_at=datetime.now(timezone.utc),
    )
    session.add(doc)
    await session.flush()

    texts = ["\n".join(f"{k}: {v}" for k, v in r.items() if v) for r in records]
    embeddings = await embed_texts(texts)
    for ordinal, (record, text, embedding) in enumerate(zip(records, texts, embeddings)):
        session.add(Chunk(
            source_document_id=doc.id, project_id=project_id, ordinal=ordinal,
            text=text, token_count=len(text.split()),
            locator={"table": table, "number": record.get("number")},
            embedding=embedding, chunk_metadata={"doc_class": doc_class},
        ))
    await session.commit()
    return len(records)


# Function: ingest_cmdb_glossary
async def ingest_cmdb_glossary(
    session: AsyncSession, project_id: uuid.UUID, client: httpx.AsyncClient,
    base_url: str, username: str, password: str,
) -> int:
    """§4.1: cmdb_ci -> glossary + system_name resolution for EARS, not citable prose chunks."""
    records = await _fetch_all(
        client, base_url, username, password, "cmdb_ci",
        "name,sys_class_name,operational_status,environment,os", max_records=2000,
    )
    if not records:
        return 0
    names = sorted({str(r["name"]).strip() for r in records if r.get("name")})

    project = await session.get(Project, project_id)
    if project:
        project.config = {**project.config, "glossary": sorted(set(project.config.get("glossary", [])) | set(names))}
        await session.commit()
    return len(names)


# Function: ingest_servicenow
async def ingest_servicenow(
    session: AsyncSession, project_id: uuid.UUID, *, base_url: str, username: str, password: str,
    tables: list[str], window_months: int = 12, verify_ssl: bool = True, timeout_seconds: int = 60,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    timeout = httpx.Timeout(timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout, verify=verify_ssl) as client:
        for table in tables:
            if table == "incident":
                counts[table] = await ingest_incidents(session, project_id, client, base_url, username, password, window_months)
            elif table == "cmdb_ci":
                counts[table] = await ingest_cmdb_glossary(session, project_id, client, base_url, username, password)
            elif table in _PROSE_TABLES:
                counts[table] = await ingest_prose_table(session, project_id, client, base_url, username, password, table)
            else:
                logger.warning("ServiceNow table %s not supported by this connector", table)
                counts[table] = 0
    return counts
