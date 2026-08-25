import asyncio

import pytest
from fastapi import HTTPException

from api import server


def _job(job_id: str, status: str) -> dict:
    return {
        "job_id": job_id,
        "status": status,
        "phase": status,
        "progress": 50,
        "events": [],
    }


@pytest.mark.parametrize("status", ["queued", "pending", "running"])
def test_active_generation_job_cannot_be_removed(status):
    job_id = f"active-removal-{status}"
    server._JOBS[job_id] = _job(job_id, status)
    try:
        with pytest.raises(HTTPException) as caught:
            asyncio.run(server.delete_job(job_id))

        assert caught.value.status_code == 409
        assert server._JOBS[job_id]["status"] == status
    finally:
        server._JOBS.pop(job_id, None)
        server._JOB_QUEUES.pop(job_id, None)
        server._job_file(job_id).unlink(missing_ok=True)


@pytest.mark.parametrize("status", ["completed", "validation_failed", "failed"])
def test_terminal_generation_job_remains_removable(status):
    job_id = f"terminal-removal-{status}"
    server._JOBS[job_id] = _job(job_id, status)
    try:
        result = asyncio.run(server.delete_job(job_id))

        assert result == {"deleted": job_id}
        assert job_id not in server._JOBS
    finally:
        server._JOBS.pop(job_id, None)
        server._JOB_QUEUES.pop(job_id, None)
        server._job_file(job_id).unlink(missing_ok=True)


def test_progress_callback_registry_race_does_not_abort_generation(monkeypatch):
    from services import analyzer, modernizer

    job_id = "progress-registry-race"
    job = _job(job_id, "queued")
    server._JOBS[job_id] = job

    def analyze_project(_folder, on_progress, _target):
        on_progress("scanning", 25, "Scanning")
        server._JOBS.pop(job_id, None)
        on_progress("architecture", 50, "Analysis complete")
        return {"architecture": {}}

    def modernize_project(_folder, _analysis, _target, on_progress, *_args, **_kwargs):
        on_progress("llm", 75, "Generating")
        return {"ModernizedApp/README.md": "complete"}, {
            "production_ready": True,
            "failed": 0,
            "strict_checked": 1,
            "build": {"passed": True},
        }

    monkeypatch.setattr(analyzer, "analyze_project", analyze_project)
    monkeypatch.setattr(modernizer, "modernize_project", modernize_project)
    try:
        server._analysis_worker(job_id, "source", "spring_boot", output_mode="project")

        assert job["status"] == "completed"
        assert job["progress"] == 100
        assert job["output"] == {"ModernizedApp/README.md": "complete"}
    finally:
        server._JOBS.pop(job_id, None)
        server._JOB_QUEUES.pop(job_id, None)
        server._job_file(job_id).unlink(missing_ok=True)
