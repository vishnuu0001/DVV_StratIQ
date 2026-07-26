# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §5 Agent 5 (Doc Renderer) output — real this pass.
# Date: 2026-01-01
# ---------------------------------------------------------------------------
"""§5 Agent 5 (Doc Renderer) output — real this pass."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.auth import current_user
from traceforge.db.models import Artifact
from traceforge.db.session import get_session
from traceforge.schemas.script import ArtifactOut

router = APIRouter(prefix="/api/v1", tags=["artifacts"])


# Function: list_artifacts
@router.get("/projects/{project_id}/artifacts", response_model=list[ArtifactOut])
async def list_artifacts(project_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    result = await session.execute(select(Artifact).where(Artifact.project_id == project_id).order_by(Artifact.generated_at.desc()))
    return list(result.scalars().all())


# Function: download_artifact
@router.get("/artifacts/{artifact_id}/download")
async def download_artifact(artifact_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    artifact = await session.get(Artifact, artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return FileResponse(artifact.blob_uri, filename=artifact.filename, media_type="application/octet-stream")
