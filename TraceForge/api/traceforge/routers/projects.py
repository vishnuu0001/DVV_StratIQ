# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/traceforge/routers (projects.py)
# Date: 2026-01-13
# ---------------------------------------------------------------------------
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.auth import current_user
from traceforge.db.models import AuditEvent, Project
from traceforge.db.session import get_session
from traceforge.schemas.project import ProjectConfigPatch, ProjectCreate, ProjectOut

router = APIRouter(prefix="/api/v1", tags=["projects"])


# Function: _database_unavailable
def _database_unavailable() -> HTTPException:
    return HTTPException(
        status_code=503,
        detail="TraceForge database is unavailable. Verify DATABASE_URL credentials and PostgreSQL connectivity.",
    )


# Function: create_project
@router.post("/projects", response_model=ProjectOut, status_code=201)
async def create_project(body: ProjectCreate, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    try:
        existing = await session.execute(select(Project).where(Project.key == body.key))
        if existing.scalars().first():
            raise HTTPException(status_code=409, detail=f"Project key '{body.key}' already exists.")

        project = Project(key=body.key, name=body.name, client_name=body.client_name, config=body.config, created_by=user.get("username"))
        session.add(project)
        await session.flush()
        session.add(AuditEvent(project_id=project.id, actor=user.get("username", "unknown"), action="PROJECT_CREATED",
                                entity_type="Project", entity_id=str(project.id), after={"key": project.key, "name": project.name}))
        await session.commit()
        await session.refresh(project)
        return project
    except HTTPException:
        raise
    except (SQLAlchemyError, Exception) as exc:
        raise _database_unavailable() from exc


# Function: get_project
@router.get("/projects/{project_id}", response_model=ProjectOut)
async def get_project(project_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    try:
        project = await session.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except HTTPException:
        raise
    except (SQLAlchemyError, Exception) as exc:
        raise _database_unavailable() from exc


# Function: list_projects
@router.get("/projects", response_model=list[ProjectOut])
async def list_projects(session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    try:
        result = await session.execute(select(Project).order_by(Project.created_at.desc()))
        return list(result.scalars().all())
    except (SQLAlchemyError, Exception) as exc:
        raise _database_unavailable() from exc


# Function: patch_project_config
@router.patch("/projects/{project_id}/config", response_model=ProjectOut)
async def patch_project_config(project_id: uuid.UUID, body: ProjectConfigPatch, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    try:
        project = await session.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        before = dict(project.config)
        project.config = {**project.config, **body.config}
        session.add(AuditEvent(project_id=project.id, actor=user.get("username", "unknown"), action="PROJECT_CONFIG_UPDATED",
                                entity_type="Project", entity_id=str(project.id), before={"config": before}, after={"config": project.config}))
        await session.commit()
        await session.refresh(project)
        return project
    except HTTPException:
        raise
    except (SQLAlchemyError, Exception) as exc:
        raise _database_unavailable() from exc
