# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Embedding generation worker that indexes ServiceNow entities into Qdrant.
# Date: 2026-06-11
# ---------------------------------------------------------------------------
"""Embedding generation worker that indexes ServiceNow entities into Qdrant."""
from __future__ import annotations

import hashlib
import logging
import re
import time
import uuid
from typing import Any

import backend.config as cfg
from backend.services.qdrant_store import ensure_collection, qdrant_enabled, upsert_points
from backend.services.postgres_store import ensure_common_schema, get_connection

logger = logging.getLogger(__name__)


# Function: _clean_text
def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"none", "null", "nan"}:
        return ""
    return text


# Function: _get_embeddings
def _get_embeddings(provider: str):
    if provider == "openai" and cfg.OPENAI_API_KEY:
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(api_key=cfg.OPENAI_API_KEY)

    from langchain_ollama import OllamaEmbeddings

    return OllamaEmbeddings(model=cfg.OLLAMA_EMBED_MODEL, base_url=cfg.OLLAMA_BASE_URL)


# Function: _incident_text
def _incident_text(record: dict) -> str:
    return "\n".join(
        [
            f"Incident Number: {_clean_text(record.get('number'))}",
            f"Short Description: {_clean_text(record.get('short_description'))}",
            f"Description: {_clean_text(record.get('description'))}",
            f"Category: {_clean_text(record.get('category'))}",
            f"Subcategory: {_clean_text(record.get('subcategory'))}",
            f"State: {_clean_text(record.get('state'))}",
            f"Priority: {_clean_text(record.get('priority'))}",
            f"Assignment Group: {_clean_text(record.get('assignment_group'))}",
            f"Assigned To: {_clean_text(record.get('assigned_to'))}",
            f"Work Notes: {_clean_text(record.get('work_notes'))}",
            f"Close Notes: {_clean_text(record.get('close_notes'))}",
        ]
    )


# Function: _chunk_text
def _chunk_text(text: str) -> list[str]:
    compact = re.sub(r"\s+", " ", text or "").strip()
    if not compact:
        return []

    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=max(500, int(cfg.CHUNK_SIZE)),
            chunk_overlap=max(50, int(cfg.CHUNK_OVERLAP)),
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        return [c.strip() for c in splitter.split_text(compact) if c.strip()]
    except Exception:
        # Fallback splitter keeps worker operational even if optional splitter fails.
        out: list[str] = []
        max_len = max(500, int(cfg.CHUNK_SIZE))
        i = 0
        while i < len(compact):
            out.append(compact[i : i + max_len])
            i += max_len
        return out


# Function: _stable_point_id
def _stable_point_id(ticket_id: str, chunk_idx: int, source_name: str) -> str:
    key = f"{ticket_id}|{chunk_idx}|{source_name}"
    # Qdrant accepts uint64 or UUID string IDs; use deterministic UUID5 per chunk.
    return str(uuid.uuid5(uuid.NAMESPACE_URL, key))


# Function: index_incidents_to_qdrant
def index_incidents_to_qdrant(records: list[dict], source_name: str, provider: str = "ollama") -> int:
    if not records or not qdrant_enabled():
        return 0

    chunks: list[tuple[str, str, dict[str, Any]]] = []
    for row in records:
        ticket_id = _clean_text(row.get("number")) or _clean_text(row.get("sys_id"))
        if not ticket_id:
            continue

        category = _clean_text(row.get("category"))
        state = _clean_text(row.get("state"))
        group = _clean_text(row.get("assignment_group"))
        short_description = _clean_text(row.get("short_description"))

        text = _incident_text(row)
        text_chunks = _chunk_text(text)
        for idx, chunk in enumerate(text_chunks):
            payload = {
                "ticket_id": ticket_id,
                "source_type": "incident",
                "short_description": short_description,
                "description_chunk": chunk,
                "category": category,
                "state": state,
                "group": group,
                "source_name": source_name,
                "chunk_index": idx,
            }
            chunks.append((ticket_id, chunk, payload))

    if not chunks:
        return 0

    embedding_model = _get_embeddings(provider)
    vectors = embedding_model.embed_documents([c[1] for c in chunks])

    ensure_collection(len(vectors[0]))

    points = []
    for idx, ((ticket_id, _chunk, payload), vector) in enumerate(zip(chunks, vectors)):
        points.append(
            {
                "id": _stable_point_id(ticket_id, idx, source_name),
                "vector": [float(x) for x in vector],
                "payload": payload,
            }
        )

    inserted = 0
    batch = 128
    for i in range(0, len(points), batch):
        inserted += upsert_points(points[i : i + batch])

    logger.info("Indexed %d chunks into Qdrant collection '%s'.", inserted, cfg.QDRANT_COLLECTION)
    return inserted


# Function: _parse_vector_text
def _parse_vector_text(raw: Any) -> list[float]:
    text = str(raw or "").strip()
    if not text:
        return []
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]
    if not text:
        return []
    values: list[float] = []
    for part in text.split(","):
        item = part.strip()
        if not item:
            continue
        values.append(float(item))
    return values


# Function: _convert_rows_to_qdrant_points
def _convert_rows_to_qdrant_points(rows, vector_size: int) -> tuple[list, int, int, int]:
    """Convert a batch of pgvector rows into Qdrant points.

    Returns (points, processed_count, skipped_count, updated_vector_size).
    """
    points = []
    processed = 0
    skipped = 0
    for row in rows:
        row_id = str(row[0])
        document = str(row[1] or "")
        metadata = row[2] or {}
        vector = _parse_vector_text(row[3])
        processed += 1

        if not vector:
            skipped += 1
            continue

        if vector_size <= 0:
            vector_size = len(vector)
            ensure_collection(vector_size)

        payload = {
            "ticket_id": metadata.get("incident_number") or row_id,
            "source_type": metadata.get("type") or "servicenow_incident",
            "short_description": metadata.get("short_description") or "",
            "description_chunk": document,
            "category": metadata.get("category") or "",
            "state": metadata.get("state") or "",
            "group": metadata.get("assignment_group") or "",
            "source_name": metadata.get("source") or "pgvector_backfill",
            "chunk_index": metadata.get("chunk_index") or 0,
        }
        points.append({"id": row_id, "vector": vector, "payload": payload})

    return points, processed, skipped, vector_size


# Function: backfill_qdrant_from_pgvector
def backfill_qdrant_from_pgvector(batch_size: int = 1000, max_rows: int = 0) -> dict[str, int | float]:
    """Backfill Qdrant points from existing pgvector chunks without re-embedding."""
    if not qdrant_enabled():
        return {"processed": 0, "inserted": 0, "skipped": 0, "elapsed_ms": 0.0}

    ensure_common_schema()
    started = time.perf_counter()
    processed = 0
    inserted = 0
    skipped = 0
    offset = 0
    vector_size = 0

    with get_connection() as conn:
        with conn.cursor() as cur:
            while True:
                if max_rows and processed >= max_rows:
                    break

                limit = int(max(100, batch_size))
                if max_rows:
                    limit = min(limit, int(max_rows - processed))

                cur.execute(
                    """
                    SELECT id, document, metadata_json, embedding::text
                    FROM vector_chunks
                    WHERE collection_name = %s
                    ORDER BY created_at ASC
                    LIMIT %s OFFSET %s
                    """,
                    (cfg.VECTOR_COLLECTION, int(limit), int(offset)),
                )
                rows = cur.fetchall()
                if not rows:
                    break

                points, batch_processed, batch_skipped, vector_size = _convert_rows_to_qdrant_points(rows, vector_size)
                processed += batch_processed
                skipped += batch_skipped

                if points:
                    inserted += upsert_points(points)

                offset += len(rows)
        conn.commit()

    elapsed_ms = (time.perf_counter() - started) * 1000.0
    logger.info(
        "Qdrant backfill complete: processed=%d inserted=%d skipped=%d elapsed_ms=%.1f",
        processed,
        inserted,
        skipped,
        elapsed_ms,
    )
    return {
        "processed": int(processed),
        "inserted": int(inserted),
        "skipped": int(skipped),
        "elapsed_ms": float(round(elapsed_ms, 1)),
    }
