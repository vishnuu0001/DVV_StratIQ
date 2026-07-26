# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Admin API — knowledge document upload, indexing, and management.
# Date: 2026-03-04
# ---------------------------------------------------------------------------
"""
Admin API — knowledge document upload, indexing, and management.
Protected by a simple secret header (replace with JWT in production).
"""
import asyncio
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse

import backend.config as cfg
from backend.models.schemas import (
    DeleteDocRequest,
    IndexRequest,
    IndexResponse,
    KnowledgeDocument,
)
from backend.rag.document_loader import load_directory, load_file, load_image_bytes
from backend.rag.vectorstore import (
    delete_by_source,
    get_collection_stats,
    index_documents,
    reset_vectorstore,
    wipe_collection,
)
from backend.services.embedding_worker import backfill_qdrant_from_pgvector

router = APIRouter(prefix="/api/admin", tags=["Admin"])
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".docx", ".xlsx", ".xls", ".csv", ".txt", ".pdf", ".md", ".png", ".jpg", ".jpeg"}


# ── Auth guard ────────────────────────────────────────────────

# Function: verify_admin
def verify_admin(x_admin_secret: str = Header(...)):
    if x_admin_secret != cfg.ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin secret.")


# ── Index data directory ──────────────────────────────────────

# Function: index_knowledge_base
@router.post("/index", response_model=IndexResponse, dependencies=[Depends(verify_admin)])
async def index_knowledge_base(request: IndexRequest, background_tasks: BackgroundTasks):
    """
    Index (or re-index) all documents in the data directory.
    Pass reindex=true to wipe existing vectors first.
    """
    provider = cfg.LLM_PROVIDER

    if request.reindex:
        deleted = wipe_collection(provider=provider)
        logger.info("Wiped existing pgvector collection '%s' (%d chunks).", cfg.VECTOR_COLLECTION, deleted)
        reset_vectorstore()

    docs = load_directory(cfg.DATA_DIR)
    if not docs:
        return IndexResponse(status="no_documents", chunks_indexed=0, files_processed=0)

    unique_files = len({d.metadata.get("source", "") for d in docs})
    chunks = index_documents(docs, provider=provider)

    return IndexResponse(
        status="success",
        chunks_indexed=chunks,
        files_processed=unique_files,
    )


# Function: knowledge_base_stats
@router.get("/stats", dependencies=[Depends(verify_admin)])
async def knowledge_base_stats():
    try:
        stats = get_collection_stats(cfg.LLM_PROVIDER)
        return stats
    except Exception as exc:
        return {"collection": cfg.VECTOR_COLLECTION, "total_chunks": 0, "error": str(exc)}


# Function: backfill_qdrant
@router.post("/backfill-qdrant", dependencies=[Depends(verify_admin)])
async def backfill_qdrant(batch_size: int = 1200, max_rows: int = 0):
    """Backfill Qdrant points from existing pgvector rows for modern retrieval path."""
    if batch_size < 100 or batch_size > 5000:
        raise HTTPException(status_code=400, detail="batch_size must be between 100 and 5000")
    if max_rows < 0:
        raise HTTPException(status_code=400, detail="max_rows must be >= 0")

    result = await asyncio.to_thread(
        backfill_qdrant_from_pgvector,
        int(batch_size),
        int(max_rows),
    )
    return {
        "status": "ok",
        "vector_backend": cfg.VECTOR_BACKEND,
        "qdrant_collection": cfg.QDRANT_COLLECTION,
        **result,
    }


# Function: wipe_vectorstore
@router.post("/wipe-vectorstore", dependencies=[Depends(verify_admin)])
async def wipe_vectorstore():
    """Delete the active PostgreSQL vector collection so ServiceNow data can be reloaded cleanly."""
    before = get_collection_stats(cfg.LLM_PROVIDER)
    wipe_collection(cfg.LLM_PROVIDER)

    reset_vectorstore()

    return {
        "status": "success",
        "collection": cfg.VECTOR_COLLECTION,
        "deleted_chunks": before.get("total_chunks", 0),
        "message": "Vector store cleared. It is ready for a fresh ServiceNow sync.",
    }


# ── Upload a new document ─────────────────────────────────────

# Function: upload_document
@router.post("/upload", dependencies=[Depends(verify_admin)])
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a knowledge document. It is saved to DATA_DIR and immediately indexed.
    """
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{suffix}' is not supported. Allowed: {ALLOWED_EXTENSIONS}",
        )

    save_path = Path(cfg.DATA_DIR) / file.filename
    raw = await file.read()

    # Save file
    save_path.write_bytes(raw)

    # Index immediately
    provider = cfg.LLM_PROVIDER
    if suffix in {".png", ".jpg", ".jpeg"}:
        docs = load_image_bytes(raw, file.filename)
    else:
        docs = load_file(save_path)

    chunks = index_documents(docs, provider=provider)

    return {
        "filename": file.filename,
        "chunks_indexed": chunks,
        "status": "indexed" if chunks > 0 else "no_content_extracted",
    }


# ── Delete a document ─────────────────────────────────────────

# Function: delete_document
@router.delete("/document", dependencies=[Depends(verify_admin)])
async def delete_document(request: DeleteDocRequest):
    """Remove a document from the vector store by source name."""
    deleted = delete_by_source(request.source_name, cfg.LLM_PROVIDER)
    # Also remove file from disk if it exists
    file_path = Path(cfg.DATA_DIR) / request.source_name
    if file_path.exists():
        os.remove(file_path)
    return {"source": request.source_name, "chunks_deleted": deleted}


# ── List indexed documents ────────────────────────────────────

# Function: list_documents
@router.get("/documents", dependencies=[Depends(verify_admin)])
async def list_documents():
    """List all files in the data directory with basic metadata."""
    data_dir = Path(cfg.DATA_DIR)
    if not data_dir.exists():
        return {"documents": []}

    docs = []
    for fp in sorted(data_dir.iterdir()):
        if fp.is_file() and fp.suffix.lower() in ALLOWED_EXTENSIONS:
            stat = fp.stat()
            docs.append({
                "source": fp.name,
                "type": fp.suffix.lstrip("."),
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            })
    return {"documents": docs}
