# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Entrypoint: `arq traceforge.workers.arq_worker.WorkerSettings`. Registered with
# Date: 2025-11-23
# ---------------------------------------------------------------------------
"""Entrypoint: `arq traceforge.workers.arq_worker.WorkerSettings`. Registered with
watchdog_all_backends.ps1 as its own process (TraceForge-Worker) — independent of the
TraceForge-API uvicorn process, so an IIS/app-pool recycle never kills a running job."""
from __future__ import annotations

from arq.connections import RedisSettings

from traceforge.config import AGENT_JOB_TIMEOUT_SECONDS, AGENT_WORKER_CONCURRENCY, REDIS_URL
from traceforge.workers.tasks import (
    ingest_github_task,
    ingest_jira_task,
    ingest_servicenow_task,
    ingest_source,
    run_brd_stage,
    run_extract_stage,
    run_render_stage,
    run_script_gen_stage,
    run_test_design_stage,
)


class WorkerSettings:
    functions = [
        ingest_source, run_extract_stage, ingest_servicenow_task, ingest_jira_task, ingest_github_task,
        run_brd_stage, run_test_design_stage, run_script_gen_stage, run_render_stage,
    ]
    redis_settings = RedisSettings.from_dsn(REDIS_URL)
    # Ollama is backed by one 8 GB GPU, so serialize agent work instead of making
    # concurrent jobs contend for the same VRAM.
    max_jobs = AGENT_WORKER_CONCURRENCY
    allow_abort_jobs = True
    job_timeout = AGENT_JOB_TIMEOUT_SECONDS
    max_tries = 1
