import asyncio
import json

import pytest
from fastapi import HTTPException

from api import server


def test_persisted_running_requirement_job_becomes_explicit_restart_failure(tmp_path, monkeypatch):
    original = dict(server._REQUIREMENTS_JOBS)
    server._REQUIREMENTS_JOBS.clear()
    monkeypatch.setattr(server, "_REQUIREMENTS_JOBS_DIR", tmp_path)
    try:
        server._REQUIREMENTS_JOBS["req-restart"] = {
            "job_id": "req-restart", "project_id": "APP-003", "document_type": "brd",
            "status": "running", "phase": "drafting", "progress": 65,
        }
        server._persist_requirements_job("req-restart")
        server._REQUIREMENTS_JOBS.clear()

        server._load_persisted_requirements_jobs()

        restored = server._REQUIREMENTS_JOBS["req-restart"]
        assert restored["status"] == "failed"
        assert restored["phase"] == "interrupted"
        assert "backend restarted" in restored["error"]
        assert json.loads((tmp_path / "req-restart.json").read_text(encoding="utf-8"))["status"] == "failed"
    finally:
        server._REQUIREMENTS_JOBS.clear()
        server._REQUIREMENTS_JOBS.update(original)


def test_requirement_job_endpoint_recovers_checkpoint_when_memory_is_empty(tmp_path, monkeypatch):
    original = dict(server._REQUIREMENTS_JOBS)
    server._REQUIREMENTS_JOBS.clear()
    monkeypatch.setattr(server, "_REQUIREMENTS_JOBS_DIR", tmp_path)
    checkpoint = {
        "job_id": "req-checkpoint", "project_id": "APP-003", "document_type": "brd",
        "status": "completed", "progress": 100, "artifact": {"content": "BRD"},
    }
    (tmp_path / "req-checkpoint.json").write_text(json.dumps(checkpoint), encoding="utf-8")
    try:
        result = asyncio.run(server.get_requirement_job("req-checkpoint"))
        assert result == checkpoint
    finally:
        server._REQUIREMENTS_JOBS.clear()
        server._REQUIREMENTS_JOBS.update(original)


def test_requirement_job_endpoint_still_returns_404_when_no_checkpoint_exists(tmp_path, monkeypatch):
    original = dict(server._REQUIREMENTS_JOBS)
    server._REQUIREMENTS_JOBS.clear()
    monkeypatch.setattr(server, "_REQUIREMENTS_JOBS_DIR", tmp_path)
    try:
        with pytest.raises(HTTPException) as exc:
            asyncio.run(server.get_requirement_job("req-missing"))
        assert exc.value.status_code == 404
    finally:
        server._REQUIREMENTS_JOBS.clear()
        server._REQUIREMENTS_JOBS.update(original)
