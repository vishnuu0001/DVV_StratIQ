# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/tests (conftest.py)
# Date: 2025-12-26
# ---------------------------------------------------------------------------
from __future__ import annotations

import asyncio
import sys
import uuid

import pytest_asyncio

if sys.platform == "win32":
    # asyncpg + the default Windows ProactorEventLoop have known teardown races
    # ('another operation is in progress' / socket AttributeErrors on connection
    # close). The Selector policy is the standard workaround for asyncpg on Windows.
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from sqlalchemy import text

from traceforge.db.models import Project
from traceforge.db.session import SessionLocal


# Function: session
@pytest_asyncio.fixture
async def session():
    async with SessionLocal() as s:
        yield s


# Function: _try_exec
async def _try_exec(sql: str, project_id: uuid.UUID) -> None:
    """Each statement gets its own transaction — Postgres aborts an entire transaction
    on the first failing statement, and audit_event's immutability trigger (P7: no
    UPDATE/DELETE, ever) makes that DELETE fail by design. Isolating each statement
    means that expected failure doesn't also skip every cleanup step after it."""
    try:
        async with SessionLocal() as s:
            await s.execute(text(sql).bindparams(pid=project_id))
            await s.commit()
    except Exception:  # noqa: BLE001 — cleanup best-effort; audit_event rows are meant to survive
        pass


# Function: project
@pytest_asyncio.fixture
async def project(session):
    """A throwaway project, cleaned up (project + everything FK'd to it) after the test."""
    proj = Project(key=f"TEST-{uuid.uuid4().hex[:8]}", name="Test Project", config={})
    session.add(proj)
    await session.commit()
    await session.refresh(proj)

    yield proj

    # Delete dependents first (no ON DELETE CASCADE by design — deletes are meant to be
    # soft/audited in the real app; tests clean up explicitly instead). audit_event
    # (and therefore the project row itself, once it has any audit history) is
    # deliberately NOT deletable — P7 append-only — so those two are skipped: the test
    # project persists as harmless residue, same as production's audit-bearing rows.
    project_id = proj.id
    # Tests frequently leave a read transaction (or an explicit flush) open on
    # the fixture session. Release its row locks before cleanup uses independent
    # sessions, otherwise PostgreSQL waits for the fixture session to close—which
    # only happens after this teardown completes.
    await session.rollback()
    for sql in [
        "DELETE FROM baseline WHERE project_id = :pid",
        "DELETE FROM gate WHERE pipeline_run_id IN (SELECT id FROM pipeline_run WHERE project_id = :pid)",
        "DELETE FROM pipeline_run WHERE project_id = :pid",
        "DELETE FROM test_script WHERE project_id = :pid",
        "DELETE FROM test_case WHERE project_id = :pid",
        "DELETE FROM test_plan_citation WHERE test_plan_id IN (SELECT id FROM test_plan WHERE project_id = :pid)",
        "DELETE FROM test_plan WHERE project_id = :pid",
        "DELETE FROM artifact WHERE project_id = :pid",
        "DELETE FROM connector_config WHERE project_id = :pid",
        "DELETE FROM source_citation WHERE requirement_id IN (SELECT id FROM requirement WHERE project_id = :pid)",
        "DELETE FROM requirement WHERE project_id = :pid",
        "DELETE FROM chunk WHERE project_id = :pid",
        "DELETE FROM source_document WHERE project_id = :pid",
        "DELETE FROM id_sequence WHERE project_id = :pid",
    ]:
        await _try_exec(sql, project_id)
    await _try_exec("DELETE FROM project WHERE id = :pid", project_id)
