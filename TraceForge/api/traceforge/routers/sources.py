# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/traceforge/routers (sources.py)
# Date: 2025-07-13
# ---------------------------------------------------------------------------
from __future__ import annotations

import asyncio
import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.auth import current_user
from traceforge.config import STORAGE_DIR
from traceforge.db.models import AuditEvent, Chunk, Project, SourceDocument
from traceforge.db.session import get_session
from traceforge.schemas.source import ChunkOut, SourceOut
from traceforge.workers.pool import get_arq_pool

router = APIRouter(prefix="/api/v1", tags=["sources"])


class ServiceNowIngestRequest(BaseModel):
    base_url: str
    username: str
    password: str
    tables: list[str] = Field(default_factory=lambda: ["incident", "sc_req_item", "change_request", "kb_knowledge", "cmdb_ci"])
    window_months: int = 12
    verify_ssl: bool = True


class JiraIngestRequest(BaseModel):
    base_url: str
    email: str
    api_token: str
    jql: str
    max_results: int = Field(200, le=1000)


class GitHubIngestRequest(BaseModel):
    repo_url: str
    token: str | None = None
    ref: str | None = None

_DOC_CLASS_BY_EXTENSION = {
    ".docx": "AS_IS_DOC", ".pdf": "AS_IS_DOC", ".xlsx": "OTHER",
    ".md": "AS_IS_DOC", ".txt": "AS_IS_DOC",
}
_CODE_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".cs", ".go", ".rb", ".php", ".cpp", ".cc", ".c", ".h", ".rs", ".kt"}
_SUPPORTED_EXTENSIONS = set(_DOC_CLASS_BY_EXTENSION) | _CODE_EXTENSIONS
_ARTIFACT_ROLES = {
    "FUNCTIONAL_DETAILS": "AS_IS_DOC",
    "SUPPORTING_ARTIFACT": "OTHER",
    "PROCESS_FLOW": "PROCESS_MAP",
    "BUSINESS_RULES": "SOW",
    "TEST_EVIDENCE": "OTHER",
    "SOURCE_CODE": "LEGACY_CODE",
}


# Function: upload_sources
@router.post("/projects/{project_id}/sources/upload", response_model=list[SourceOut], status_code=202)
async def upload_sources(
    project_id: uuid.UUID,
    files: list[UploadFile],
    artifact_role: str = Form("FUNCTIONAL_DETAILS"),
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(current_user),
):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    artifact_role = artifact_role.strip().upper()
    if artifact_role not in _ARTIFACT_ROLES:
        raise HTTPException(status_code=422, detail=f"Unsupported artifact role '{artifact_role}'")

    project_dir = STORAGE_DIR / str(project_id)
    project_dir.mkdir(parents=True, exist_ok=True)

    uploads: list[tuple[UploadFile, str, str]] = []
    for upload in files:
        filename = Path(upload.filename or "").name
        suffix = Path(filename).suffix.lower()
        if not filename or suffix not in _SUPPORTED_EXTENSIONS:
            supported = ", ".join(sorted(_SUPPORTED_EXTENSIONS))
            raise HTTPException(status_code=422, detail=f"Unsupported file '{filename or 'unnamed'}'. Supported types: {supported}")
        uploads.append((upload, filename, suffix))

    created: list[SourceDocument] = []
    pool = await get_arq_pool()
    for upload, filename, suffix in uploads:
        content = await upload.read()
        if not content:
            raise HTTPException(status_code=422, detail=f"File '{filename}' is empty")
        sha256 = hashlib.sha256(content).hexdigest()
        dest = project_dir / f"{sha256}{suffix}"
        await asyncio.to_thread(dest.write_bytes, content)

        doc = SourceDocument(
            project_id=project_id,
            source_type="UPLOAD",
            connector_ref={"artifact_role": artifact_role},
            filename=filename,
            mime_type=upload.content_type,
            blob_uri=str(dest),
            sha256=sha256,
            doc_class="LEGACY_CODE" if suffix in _CODE_EXTENSIONS else _ARTIFACT_ROLES[artifact_role],
            status="PENDING",
        )
        session.add(doc)
        await session.flush()
        session.add(AuditEvent(project_id=project_id, actor=user.get("username", "unknown"), action="SOURCE_UPLOADED",
                                entity_type="SourceDocument", entity_id=str(doc.id), after={"filename": doc.filename}))
        created.append(doc)

    await session.commit()
    for doc in created:
        await session.refresh(doc)
        await pool.enqueue_job("ingest_source", str(doc.id))

    return created


# Function: list_sources
@router.get("/projects/{project_id}/sources", response_model=list[SourceOut])
async def list_sources(project_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    result = await session.execute(
        select(SourceDocument).where(SourceDocument.project_id == project_id, SourceDocument.deleted_at.is_(None))
        .order_by(SourceDocument.filename)
    )
    return list(result.scalars().all())


# Function: get_source_chunks
@router.get("/sources/{source_id}/chunks", response_model=list[ChunkOut])
async def get_source_chunks(source_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    result = await session.execute(select(Chunk).where(Chunk.source_document_id == source_id).order_by(Chunk.ordinal))
    return list(result.scalars().all())


# Function: delete_source
@router.delete("/sources/{source_id}", status_code=204)
async def delete_source(source_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    doc = await session.get(SourceDocument, source_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Source not found")
    doc.deleted_at = datetime.now(timezone.utc)
    # NOTE: cascading dependent Requirements to SUSPECT (spec §7) lands with suspect-link
    # propagation in Phase 3 — see PROGRESS.md. This soft-deletes the source only.
    await session.commit()


# Function: ingest_servicenow_source
@router.post("/projects/{project_id}/sources/servicenow", status_code=202)
async def ingest_servicenow_source(
    project_id: uuid.UUID, body: ServiceNowIngestRequest,
    session: AsyncSession = Depends(get_session), user: dict = Depends(current_user),
):
    """Credentials are used for this request only and are not stored (same convention
    as every other credential-bearing endpoint in this codebase)."""
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    pool = await get_arq_pool()
    await pool.enqueue_job(
        "ingest_servicenow_task", str(project_id), body.base_url, body.username, body.password,
        body.tables, body.window_months, body.verify_ssl,
    )
    return {"status": "queued"}


# Function: ingest_jira_source
@router.post("/projects/{project_id}/sources/jira", status_code=202)
async def ingest_jira_source(
    project_id: uuid.UUID, body: JiraIngestRequest,
    session: AsyncSession = Depends(get_session), user: dict = Depends(current_user),
):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    pool = await get_arq_pool()
    await pool.enqueue_job("ingest_jira_task", str(project_id), body.base_url, body.email, body.api_token, body.jql, body.max_results)
    return {"status": "queued"}


# Function: ingest_github_source
@router.post("/projects/{project_id}/sources/github", status_code=202)
async def ingest_github_source(
    project_id: uuid.UUID, body: GitHubIngestRequest,
    session: AsyncSession = Depends(get_session), user: dict = Depends(current_user),
):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    pool = await get_arq_pool()
    await pool.enqueue_job("ingest_github_task", str(project_id), body.repo_url, body.token, body.ref)
    return {"status": "queued"}


# Function: rebuild_index
@router.post("/projects/{project_id}/index/rebuild", status_code=202)
async def rebuild_index(project_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    result = await session.execute(
        select(SourceDocument).where(SourceDocument.project_id == project_id, SourceDocument.deleted_at.is_(None))
    )
    pool = await get_arq_pool()
    count = 0
    for doc in result.scalars().all():
        await pool.enqueue_job("ingest_source", str(doc.id))
        count += 1
    return {"queued": count}
