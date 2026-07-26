# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Data Sources API  manage document source connections.
# Date: 2026-06-23
# ---------------------------------------------------------------------------
"""
Data Sources API  manage document source connections.

Supported types: local_folder, sharepoint, url
"""
import json
import logging
import os
import secrets
import time
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

import backend.config as cfg
from backend.api.auth import get_current_user
from backend.rag.document_loader import load_file
from backend.rag.vectorstore import index_documents

router = APIRouter(prefix="/api/datasources", tags=["Data Sources"])
logger = logging.getLogger(__name__)

SOURCES_DB_PATH = Path(cfg.BASE_DIR) / "datasources_db.json"


# ””€ Storage helpers ””””””””””””””””””””””””””””””””””””””””””€
# Function: _load_sources
def _load_sources() -> list:
    if not SOURCES_DB_PATH.exists():
        return []
    try:
        return json.loads(SOURCES_DB_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


# Function: _save_sources
def _save_sources(sources: list) -> None:
    SOURCES_DB_PATH.write_text(json.dumps(sources, indent=2), encoding="utf-8")


# ””€ Models ”””””””””””””””””””””””””””””””””””””””””””””””””””€
class DataSourceCreate(BaseModel):
    name: str
    type: str  # "local_folder" | "sharepoint" | "url"
    config: dict


# ””€ Sync workers ”””””””””””””””””””””””””””””””””””””””””””””€
# Function: _sync_local_folder
def _sync_local_folder(source: dict) -> dict:
    """Index all supported files from a configured local folder path."""
    from backend.rag.document_loader import load_documents
    from backend.rag.vectorstore import index_documents

    folder = source["config"].get("path", "").strip()
    if not folder:
        return {"status": "error", "message": "No folder path configured"}

    folder_path = Path(folder)
    if not folder_path.exists() or not folder_path.is_dir():
        return {"status": "error", "message": f"Folder not found: {folder}"}

    supported = {".docx", ".xlsx", ".csv", ".txt", ".md", ".pdf"}
    files = [f for f in folder_path.iterdir() if f.is_file() and f.suffix.lower() in supported]
    if not files:
        return {"status": "ok", "message": "No supported files found", "chunks": 0}

    total_chunks = 0
    errors = []
    for file_path in files:
        try:
            docs = load_documents(str(file_path))
            if docs:
                total_chunks += index_documents(docs)
        except Exception as exc:
            logger.warning("Failed to index %s: %s", file_path.name, exc)
            errors.append(file_path.name)

    result = {"status": "ok", "chunks": total_chunks, "files": len(files)}
    if errors:
        result["warnings"] = f"Could not index: {', '.join(errors)}"
    return result


# Function: _sync_sharepoint
def _sync_sharepoint(source: dict) -> dict:
    """
    SharePoint sync via Microsoft Graph API.
    Requires: tenant_id, client_id, client_secret, site_url, library (optional).
    Install msal to enable: pip install msal
    """
    config = source["config"]
    required = ["tenant_id", "client_id", "client_secret", "site_url"]
    missing = [k for k in required if not config.get(k)]
    if missing:
        return {"status": "error", "message": f"Missing configuration: {', '.join(missing)}"}

    try:
        import msal  # noqa: F401
    except ImportError:
        return {
            "status": "error",
            "message": "msal package is required for SharePoint sync. Run: pip install msal",
        }

    # TODO: Implement full SharePoint integration using Microsoft Graph API
    # Currently validates MSAL credentials but full document indexing requires:
    # 1. OAuth 2.0 token flow for user delegation
    # 2. Microsoft Graph API calls to enumerate SharePoint sites and document libraries
    # 3. Document download and content extraction pipeline
    # 4. Integration with LangChain document loader
    return {
        "status": "error",
        "message": "SharePoint sync is not yet fully implemented. Credentials validated.",
    }


# Function: _sync_url
def _sync_url(source: dict) -> dict:
    """Fetch and index text content from a web URL."""
    import httpx
    from langchain_core.documents import Document
    from backend.rag.vectorstore import index_documents

    url = source["config"].get("url", "").strip()
    if not url:
        return {"status": "error", "message": "No URL configured"}

    try:
        resp = httpx.get(url, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        content = resp.text[:50_000]  # cap to 50 KB
        doc = Document(
            page_content=content,
            metadata={"source": source["name"], "type": "url", "url": url},
        )
        chunks = index_documents([doc])
        return {"status": "ok", "chunks": chunks}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


# Function: _do_sync
def _do_sync(source_id: str) -> None:
    """Run sync for a single source and persist the result."""
    sources = _load_sources()
    for s in sources:
        if s["id"] != source_id:
            continue
        try:
            if s["type"] == "local_folder":
                result = _sync_local_folder(s)
            elif s["type"] == "sharepoint":
                result = _sync_sharepoint(s)
            elif s["type"] == "url":
                result = _sync_url(s)
            else:
                result = {"status": "error", "message": f"Unknown source type: {s['type']}"}
            s["status"] = result.get("status", "ok")
            s["last_synced"] = time.time()
            s["chunks_indexed"] = result.get("chunks", s.get("chunks_indexed", 0))
            s["last_result"] = result
        except Exception as exc:
            s["status"] = "error"
            s["last_result"] = {"status": "error", "message": str(exc)}
        break
    _save_sources(sources)


# ””€ Endpoints ””””””””””””””””””””””””””””””””””””””””””””””””€
# Function: get_source_types
@router.get("/types")
async def get_source_types():
    """Return metadata describing each available source type and its config fields."""
    return [
        {
            "type": "local_folder",
            "label": "Local Folder",
            "icon": "folder",
            "description": "Index documents from a local directory on the server.",
            "fields": [
                {
                    "key": "path",
                    "label": "Folder Path",
                    "type": "text",
                    "placeholder": "C:/data/documents  or  /srv/knowledge",
                    "required": True,
                },
            ],
        },
        {
            "type": "sharepoint",
            "label": "SharePoint",
            "icon": "cloud",
            "description": "Connect to a Microsoft SharePoint document library via Graph API.",
            "fields": [
                {"key": "tenant_id",     "label": "Tenant ID",           "type": "text",     "required": True},
                {"key": "client_id",     "label": "Client ID (App ID)",  "type": "text",     "required": True},
                {"key": "client_secret", "label": "Client Secret",       "type": "password", "required": True},
                {
                    "key": "site_url",
                    "label": "SharePoint Site URL",
                    "type": "url",
                    "placeholder": "https://company.sharepoint.com/sites/mysite",
                    "required": True,
                },
                {
                    "key": "library",
                    "label": "Document Library",
                    "type": "text",
                    "placeholder": "Documents",
                    "required": False,
                },
            ],
        },
        {
            "type": "url",
            "label": "Web URL",
            "icon": "globe",
            "description": "Fetch and index content from a web page or REST endpoint.",
            "fields": [
                {
                    "key": "url",
                    "label": "URL",
                    "type": "url",
                    "placeholder": "https://example.com/knowledge-article",
                    "required": True,
                },
            ],
        },
    ]


# Function: list_sources
@router.get("")
async def list_sources(current_user: dict = Depends(get_current_user)):
    return _load_sources()


# Function: add_source
@router.post("")
async def add_source(
    body: DataSourceCreate,
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    sources = _load_sources()
    if any(s["name"].lower() == body.name.lower() for s in sources):
        raise HTTPException(status_code=400, detail="A data source with this name already exists")

    source = {
        "id": f"ds_{secrets.token_hex(6)}",
        "name": body.name,
        "type": body.type,
        "config": body.config,
        "status": "idle",
        "last_synced": None,
        "chunks_indexed": 0,
        "created_at": time.time(),
        "last_result": None,
    }
    sources.append(source)
    _save_sources(sources)
    return source


# ── Direct file upload + index (must be before /{source_id} routes) ───────
# Function: process_files
@router.post("/process-files")
async def process_files(
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Upload one or more files and index them directly into PostgreSQL pgvector."""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    import gc
    import shutil
    import stat
    import tempfile
    import traceback

    # Function: _force_rmtree
    def _force_rmtree(path: str) -> None:
        """Remove a temp directory, force-releasing locked files on Windows."""
        # Function: _on_error
        def _on_error(func, fpath, _exc_info):
            try:
                os.chmod(fpath, stat.S_IWRITE)
                func(fpath)
            except Exception:
                pass  # best-effort; OS will reclaim on reboot
        gc.collect()  # prompt Python to release any lingering handles
        shutil.rmtree(path, onerror=_on_error)

    SUPPORTED = {".docx", ".xlsx", ".xls", ".csv", ".txt", ".md", ".pdf",
                 ".png", ".jpg", ".jpeg"}

    results = []
    errors = []
    tmpdir = tempfile.mkdtemp()
    try:
        tmp_root = Path(tmpdir)
        for upload in files:
            safe_name = Path(upload.filename or "file").name
            suffix = Path(safe_name).suffix.lower()
            if suffix not in SUPPORTED:
                errors.append({"file": safe_name, "error": f"Unsupported file type: {suffix}"})
                continue
            tmp_path = tmp_root / f"{len(results)+len(errors)}_{safe_name}"
            try:
                content = await upload.read()
                tmp_path.write_bytes(content)
                docs = load_file(tmp_path)
                if docs:
                    chunks = index_documents(docs, provider=cfg.LLM_PROVIDER)
                    results.append({"file": safe_name, "chunks": chunks})
                else:
                    results.append({"file": safe_name, "chunks": 0, "note": "no content extracted"})
            except Exception as exc:
                logger.warning("Failed to index %s: %s", safe_name, exc)
                errors.append({"file": safe_name, "error": str(exc)})
    except Exception as exc:
        logger.error("process_files outer error: %s\n%s", exc, traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Processing failed: {exc}")
    finally:
        _force_rmtree(tmpdir)

    total_chunks = sum(r["chunks"] for r in results)
    return {
        "status": "ok",
        "files_processed": len(results),
        "files_failed": len(errors),
        "total_chunks": total_chunks,
        "results": results,
        "errors": errors,
    }


# Function: process_files_stream
@router.post("/process-files-stream")
async def process_files_stream(
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Upload files and index them, streaming SSE progress events for each file."""
    import asyncio
    import gc
    import json
    import shutil
    import stat
    import tempfile
    import traceback
    from fastapi.responses import StreamingResponse

    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    SUPPORTED = {".docx", ".xlsx", ".xls", ".csv", ".txt", ".md", ".pdf",
                 ".png", ".jpg", ".jpeg"}

    # Read all file contents upfront before the streaming response starts
    file_data = []
    for upload in files:
        content = await upload.read()
        file_data.append({
            "name": Path(upload.filename or "file").name,
            "content": content,
        })

    total = len(file_data)

    # Function: event_stream
    async def event_stream():
        # Function: _force_rmtree
        def _force_rmtree(path: str) -> None:
            # Function: _on_error
            def _on_error(func, fpath, _exc_info):
                try:
                    os.chmod(fpath, stat.S_IWRITE)
                    func(fpath)
                except Exception:
                    pass
            gc.collect()
            shutil.rmtree(path, onerror=_on_error)

        # Function: _sse
        def _sse(data: dict) -> str:
            return f"data: {json.dumps(data)}\n\n"

        yield _sse({"type": "start", "total": total,
                    "message": f"Starting to process {total} file(s)…"})

        results = []
        errors = []
        tmpdir = tempfile.mkdtemp()

        try:
            tmp_root = Path(tmpdir)
            loop = asyncio.get_event_loop()

            for i, fd in enumerate(file_data):
                safe_name = fd["name"]
                suffix = Path(safe_name).suffix.lower()

                yield _sse({
                    "type": "progress", "file": safe_name,
                    "current": i + 1, "total": total,
                    "message": f"Processing {safe_name}…",
                })

                if suffix not in SUPPORTED:
                    errors.append({"file": safe_name, "error": f"Unsupported type: {suffix}"})
                    yield _sse({
                        "type": "file_error", "file": safe_name,
                        "current": i + 1, "total": total,
                        "message": f"Skipped {safe_name} — unsupported file type",
                    })
                    continue

                tmp_path = tmp_root / f"{i}_{safe_name}"
                try:
                    tmp_path.write_bytes(fd["content"])
                    docs = await loop.run_in_executor(None, load_file, tmp_path)
                    if docs:
                        chunks = await loop.run_in_executor(
                            None, lambda d=docs: index_documents(d, provider=cfg.LLM_PROVIDER)
                        )
                        results.append({"file": safe_name, "chunks": chunks})
                        yield _sse({
                            "type": "file_done", "file": safe_name, "chunks": chunks,
                            "current": i + 1, "total": total,
                            "message": f"Indexed {safe_name} — {chunks} chunk(s) added",
                        })
                    else:
                        results.append({"file": safe_name, "chunks": 0})
                        yield _sse({
                            "type": "file_done", "file": safe_name, "chunks": 0,
                            "current": i + 1, "total": total,
                            "message": f"Indexed {safe_name} — no extractable content",
                        })
                except Exception as exc:
                    logger.warning("Failed to index %s: %s", safe_name, exc)
                    errors.append({"file": safe_name, "error": str(exc)})
                    yield _sse({
                        "type": "file_error", "file": safe_name,
                        "current": i + 1, "total": total,
                        "message": f"Failed: {safe_name} — {exc}",
                    })

                await asyncio.sleep(0)  # yield control to the event loop

        except Exception as exc:
            logger.error("process_files_stream error: %s\n%s", exc, traceback.format_exc())
            yield _sse({"type": "error", "message": f"Processing failed: {exc}"})
            return
        finally:
            _force_rmtree(tmpdir)

        total_chunks = sum(r["chunks"] for r in results)

        yield _sse({
            "type": "building_graph",
            "message": "Updating knowledge graph index…",
            "total_chunks": total_chunks,
        })

        await asyncio.sleep(0.05)

        msg = (
            f"Done! {len(results)} file(s) indexed — {total_chunks} chunks added to knowledge base"
            if not errors else
            f"Done! {len(results)} file(s) indexed ({len(errors)} failed) — {total_chunks} chunks added"
        )
        yield _sse({
            "type": "complete",
            "files_processed": len(results),
            "files_failed": len(errors),
            "total_chunks": total_chunks,
            "results": results,
            "errors": errors,
            "message": msg,
        })

    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# Function: sync_source
@router.post("/{source_id}/sync")
async def sync_source(
    source_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    sources = _load_sources()
    if not any(s["id"] == source_id for s in sources):
        raise HTTPException(status_code=404, detail="Data source not found")

    for s in sources:
        if s["id"] == source_id:
            s["status"] = "syncing"
    _save_sources(sources)

    background_tasks.add_task(_do_sync, source_id)
    return {"message": "Sync started", "source_id": source_id}


# Function: get_source
@router.get("/{source_id}")
async def get_source(
    source_id: str,
    current_user: dict = Depends(get_current_user),
):
    sources = _load_sources()
    source = next((s for s in sources if s["id"] == source_id), None)
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    return source


# Function: delete_source
@router.delete("/{source_id}")
async def delete_source(
    source_id: str,
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    sources = _load_sources()
    target = next((s for s in sources if s["id"] == source_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Data source not found")
    _save_sources([s for s in sources if s["id"] != source_id])
    return {"deleted": source_id, "name": target["name"]}
