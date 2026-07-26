# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/tests (test_testplan_empty_state.py)
# Date: 2026-01-04
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Scope: TraceForge — test-plan empty-state API behavior
# ---------------------------------------------------------------------------
from __future__ import annotations

from traceforge.routers.testcases import get_test_plan


# Function: test_missing_test_plan_is_a_normal_empty_state
async def test_missing_test_plan_is_a_normal_empty_state(session, project):
    result = await get_test_plan(project.id, session=session, user={"username": "tester"})

    assert result is None
