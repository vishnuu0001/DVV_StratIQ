# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/tests (test_run_cancel.py)
# Date: 2026-06-24
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Scope: TraceForge — user-initiated pipeline cancellation
# ---------------------------------------------------------------------------
from __future__ import annotations

from traceforge.db.models import PipelineRun
from traceforge.routers.runs import cancel_run


class _FakePool:
    pass


class _FakeJob:
    # Function: __init__
    def __init__(self, job_id: str, pool):
        self.job_id = job_id

    # Function: abort
    async def abort(self, *, timeout: float):
        return True


# Function: test_cancel_run_stops_active_job_and_preserves_completed_work
async def test_cancel_run_stops_active_job_and_preserves_completed_work(session, project, monkeypatch):
    run = PipelineRun(
        project_id=project.id, stage="EXTRACT", status="RUNNING",
        stats={"job_id": "run-test", "items_generated": 12},
    )
    session.add(run)
    await session.commit()
    await session.refresh(run)
    monkeypatch.setattr("traceforge.routers.runs.Job", _FakeJob)
    # Function: fake_pool
    async def fake_pool():
        return _FakePool()
    monkeypatch.setattr("traceforge.routers.runs.get_arq_pool", fake_pool)

    result = await cancel_run(run.id, session=session, user={"username": "tester"})

    assert result["status"] == "stopped"
    assert result["worker_aborted"] is True
    assert run.status == "FAILED"
    assert run.stats["items_generated"] == 12
