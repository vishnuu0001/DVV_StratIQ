# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Re-index a saved ServiceNow JSONL snapshot into the vector DB.
# Date: 2026-05-10
# ---------------------------------------------------------------------------
"""
Re-index a saved ServiceNow JSONL snapshot into the vector DB.

Usage:
    python reindex_snapshot.py <path_to_snapshot.jsonl>

Example:
    python reindex_snapshot.py data/servicenow_incidents_20260619_094758.jsonl
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure Novastra-ITSM root is on sys.path so backend imports work
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load .env before importing backend modules so config reads the right values
from dotenv import load_dotenv
load_dotenv(dotenv_path=ROOT / ".env")

from langchain_core.documents import Document
from backend.rag.vectorstore import index_documents
import backend.config as cfg


# Function: _safe_text
def _safe_text(value) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"none", "null", "nan"}:
        return ""
    return text


# Function: _clip
def _clip(value, max_chars: int) -> str:
    text = _safe_text(value)
    return text if len(text) <= max_chars else text[:max_chars] + " ...[truncated]"


# Function: _build_incident_doc
def _build_incident_doc(record: dict, source_name: str) -> Document:
    number = _safe_text(record.get("number")) or "UNKNOWN"
    content = (
        f"Incident Number: {number}\n"
        f"Short Description: {_clip(record.get('short_description'), 600)}\n"
        f"Description: {_clip(record.get('description'), 4000)}\n"
        f"Category: {_safe_text(record.get('category'))}\n"
        f"Subcategory: {_safe_text(record.get('subcategory'))}\n"
        f"Priority: {_safe_text(record.get('priority'))}\n"
        f"State: {_safe_text(record.get('state'))}\n"
        f"Assignment Group: {_safe_text(record.get('assignment_group'))}\n"
        f"Assigned To: {_safe_text(record.get('assigned_to'))}\n"
        f"CMDB CI: {_safe_text(record.get('cmdb_ci'))}\n"
        f"Business Service: {_safe_text(record.get('business_service'))}\n"
        f"Opened At: {_safe_text(record.get('opened_at'))}\n"
        f"Resolved At: {_safe_text(record.get('resolved_at'))}\n"
        f"Closed At: {_safe_text(record.get('closed_at'))}\n"
        f"Work Notes: {_clip(record.get('work_notes'), 6000)}\n"
        f"Close Notes: {_clip(record.get('close_notes'), 3000)}\n"
    )
    return Document(
        page_content=content,
        metadata={
            "source": source_name,
            "type": "servicenow_incident",
            "incident_number": number,
            "category": _safe_text(record.get("category")),
            "priority": _safe_text(record.get("priority")),
            "state": _safe_text(record.get("state")),
            "atomic": False,
        },
    )


# Function: main
def main():
    if len(sys.argv) < 2:
        snapshot_path = ROOT / "data" / "servicenow_incidents_20260619_094758.jsonl"
        print(f"No path given; defaulting to: {snapshot_path}")
    else:
        snapshot_path = Path(sys.argv[1])

    if not snapshot_path.exists():
        print(f"ERROR: snapshot not found: {snapshot_path}")
        sys.exit(1)

    print(f"Reading snapshot: {snapshot_path}")
    records = []
    with snapshot_path.open("r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    print(f"Loaded {len(records)} records")

    source_name = snapshot_path.name
    docs = [_build_incident_doc(r, source_name) for r in records]

    provider = cfg.LLM_PROVIDER if hasattr(cfg, "LLM_PROVIDER") else "ollama"
    print(f"Embedding provider: {provider}  |  EMBEDDING_DEVICE: {cfg.EMBEDDING_DEVICE}  |  OLLAMA_EMBED_MODEL: {cfg.OLLAMA_EMBED_MODEL}")

    # LanceDB uses the modern incident ingestion pipeline rather than the legacy
    # PostgreSQL Document indexer. The old helper silently returned zero when
    # DB_BACKEND=sqlite, making a failed re-index look successful.
    if cfg.VECTOR_BACKEND == "lancedb":
        from backend.services.embedding_worker_lancedb import index_incidents_to_lancedb

        total = index_incidents_to_lancedb(records, source_name)
        if total <= 0:
            print("ERROR: LanceDB indexing completed without writing any chunks")
            sys.exit(1)
        print(f"\nDone. Total LanceDB chunks indexed: {total}")
        return

    BATCH = 50
    total = 0
    for i in range(0, len(docs), BATCH):
        batch = docs[i : i + BATCH]
        batch_num = i // BATCH + 1
        for attempt in range(1, 4):
            try:
                from backend.rag.vectorstore import _get_embeddings, reset_vectorstore
                _get_embeddings.cache_clear()  # force fresh Ollama connection each batch
                n = index_documents(batch, provider=provider)
                total += n
                print(f"  Batch {batch_num} ({len(batch)} docs): {n} chunks  [total: {total}]")
                break
            except Exception as exc:
                print(f"  Batch {batch_num} attempt {attempt} failed: {exc}")
                if attempt == 3:
                    print(f"  Skipping batch {batch_num} after 3 failures")
                import time
                time.sleep(3)

    print(f"\nDone. Total chunks indexed: {total}")


if __name__ == "__main__":
    main()
