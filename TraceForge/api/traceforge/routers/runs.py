# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/traceforge/routers (runs.py)
# Date: 2025-10-27
# ---------------------------------------------------------------------------
from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from arq.jobs import Job
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.auth import current_user
from traceforge.db.models import AuditEvent, PipelineRun, Project, SourceDocument
from traceforge.db.session import SessionLocal, get_session
from traceforge.orchestration.gates import assert_stage_unblocked
from traceforge.orchestration.reset import (
    clear_project_data, clear_project_storage, clear_requirements, clear_test_design, reset_pipeline,
)
from traceforge.schemas.project import StartFreshRequest
from traceforge.schemas.run import RunCreate, RunOut
from traceforge.workers.pool import get_arq_pool

router = APIRouter(prefix="/api/v1", tags=["runs"])

_STAGE_JOB = {
    "EXTRACT": "run_extract_stage",
    "BRD": "run_brd_stage",
    "TEST_DESIGN": "run_test_design_stage",
    "SCRIPT_GEN": "run_script_gen_stage",
    "RENDER": "run_render_stage",
}


# Function: create_run
@router.post("/projects/{project_id}/runs", response_model=RunOut, status_code=202)
async def create_run(project_id: uuid.UUID, body: RunCreate, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # P3 / spec §10 Phase 1 acceptance: "attempting to start Agent 2 via the API while
    # Gate 1 is PENDING returns 409" — this is the check that enforces it for every stage.
    await assert_stage_unblocked(session, project_id, body.stage)

    job_name = _STAGE_JOB.get(body.stage)
    if job_name is None:
        raise HTTPException(status_code=501, detail=f"Stage '{body.stage}' is not a recognised pipeline stage.")

    active_run = await session.scalar(
        select(PipelineRun).where(
            PipelineRun.project_id == project_id,
            PipelineRun.stage == body.stage,
            PipelineRun.status.in_(["QUEUED", "RUNNING"]),
        ).limit(1)
    )
    if active_run:
        raise HTTPException(status_code=409, detail=f"A {body.stage} run is already active ({active_run.id}).")

    run = PipelineRun(project_id=project_id, stage=body.stage, status="QUEUED", scope=body.scope, triggered_by=user.get("username"))
    session.add(run)
    await session.flush()
    job_id = f"run-{run.id}"
    run.stats = {"phase": "queued", "job_id": job_id}
    await session.commit()

    pool = await get_arq_pool()
    await pool.enqueue_job(job_name, str(run.id), _job_id=job_id)
    return run


# Function: cancel_run
@router.post("/runs/{run_id}/cancel", status_code=200)
async def cancel_run(
    run_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user),
):
    run = await session.get(PipelineRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    if run.status not in {"QUEUED", "RUNNING"}:
        raise HTTPException(status_code=409, detail=f"Run is already {run.status}.")

    job_id = (run.stats or {}).get("job_id", f"run-{run.id}")
    pool = await get_arq_pool()
    try:
        aborted = await Job(job_id, pool).abort(timeout=8)
    except TimeoutError:
        aborted = False
    run.status = "FAILED"
    run.error = "Stopped by user. Completed batches remain available."
    run.finished_at = datetime.now(timezone.utc)
    session.add(AuditEvent(
        project_id=run.project_id, actor=user.get("username", "unknown"), action="PIPELINE_RUN_STOPPED",
        entity_type="PipelineRun", entity_id=str(run.id), before={"status": "RUNNING"},
        after={"status": "FAILED", "job_id": job_id, "worker_aborted": aborted},
    ))
    await session.commit()
    return {"status": "stopped", "run_id": str(run.id), "worker_aborted": aborted}


# Function: reset_pipeline_route
@router.post("/projects/{project_id}/reset-pipeline", status_code=200)
async def reset_pipeline_route(project_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    active_run = await session.scalar(select(PipelineRun.id).where(
        PipelineRun.project_id == project_id,
        PipelineRun.status.in_(["QUEUED", "RUNNING"]),
    ).limit(1))
    if active_run:
        raise HTTPException(status_code=409, detail="Cannot reset while a pipeline stage is queued or running.")

    runs_deleted = await reset_pipeline(session, project_id, actor=user.get("username", "unknown"))
    await session.commit()
    return {"status": "reset", "runs_deleted": runs_deleted}


@router.post("/projects/{project_id}/reset-test-design", status_code=200)
async def reset_test_design_route(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(current_user),
):
    if await session.get(Project, project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    active_run = await session.scalar(select(PipelineRun.id).where(
        PipelineRun.project_id == project_id,
        PipelineRun.status.in_(["QUEUED", "RUNNING"]),
    ).limit(1))
    if active_run:
        raise HTTPException(status_code=409, detail="Cannot reset Test Design while a pipeline stage is active.")
    removed = await clear_test_design(
        session, project_id, actor=user.get("username", "unknown"),
    )
    await session.commit()
    return {"status": "reset", "removed": removed}


@router.post("/projects/{project_id}/reset-requirements", status_code=200)
async def reset_requirements_route(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(current_user),
):
    if await session.get(Project, project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    active_run = await session.scalar(select(PipelineRun.id).where(
        PipelineRun.project_id == project_id,
        PipelineRun.status.in_(["QUEUED", "RUNNING"]),
    ).limit(1))
    if active_run:
        raise HTTPException(status_code=409, detail="Cannot reset requirements while a pipeline stage is active.")
    try:
        removed = await clear_requirements(
            session, project_id, actor=user.get("username", "unknown"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    runs_deleted = await reset_pipeline(
        session, project_id, actor=user.get("username", "unknown"),
    )
    await session.commit()
    return {"status": "reset", "removed": removed, "runs_deleted": runs_deleted}


# Function: start_fresh_route
@router.post("/projects/{project_id}/start-fresh", status_code=200)
async def start_fresh_route(
    project_id: uuid.UUID,
    body: StartFreshRequest,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(current_user),
):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if body.confirmation != "START OVER":
        raise HTTPException(status_code=422, detail='Type "START OVER" to confirm permanent deletion.')

    active_run = await session.scalar(select(PipelineRun.id).where(
        PipelineRun.project_id == project_id,
        PipelineRun.status.in_(["QUEUED", "RUNNING"]),
    ).limit(1))
    active_ingest = await session.scalar(select(SourceDocument.id).where(
        SourceDocument.project_id == project_id,
        SourceDocument.status.in_(["PENDING", "PARSING"]),
    ).limit(1))
    if active_run or active_ingest:
        raise HTTPException(status_code=409, detail="Cannot start fresh while ingestion or a pipeline stage is active.")

    deleted = await clear_project_data(session, project_id, actor=user.get("username", "unknown"))
    await session.commit()
    storage_deleted = clear_project_storage(project_id)
    return {"status": "fresh", "deleted": deleted, "storage_deleted": storage_deleted}


# Function: list_runs
@router.get("/projects/{project_id}/runs", response_model=list[RunOut])
async def list_runs(project_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    result = await session.execute(select(PipelineRun).where(PipelineRun.project_id == project_id).order_by(PipelineRun.created_at.desc()))
    return list(result.scalars().all())


# Function: get_run
@router.get("/runs/{run_id}", response_model=RunOut)
async def get_run(run_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    run = await session.get(PipelineRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


# Function: run_events
@router.get("/runs/{run_id}/events")
async def run_events(run_id: uuid.UUID, user: dict = Depends(current_user)):
    """SSE progress stream — polls PipelineRun.status/stats every second and pushes a
    delta. Proves live streaming through IIS the same way /health/sse-test does."""
    # Function: event_stream
    async def event_stream():
        last_payload = None
        for _ in range(120):  # ~2 minutes of polling, then the client reconnects
            async with SessionLocal() as session:
                run = await session.get(PipelineRun, run_id)
                if run is None:
                    yield f"data: {json.dumps({'error': 'run not found'})}\n\n"
                    return
                payload = {"status": run.status, "stats": run.stats, "error": run.error}
            if payload != last_payload:
                yield f"data: {json.dumps(payload)}\n\n"
                last_payload = payload
            if payload["status"] in {"AWAITING_APPROVAL", "APPROVED", "REJECTED", "FAILED"}:
                return
            await asyncio.sleep(1)

    return StreamingResponse(
        event_stream(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
