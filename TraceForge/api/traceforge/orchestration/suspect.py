# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §6.2 Suspect-link propagation. When an APPROVED Requirement's content_hash changes:
# Date: 2025-11-19
# ---------------------------------------------------------------------------
"""§6.2 Suspect-link propagation. When an APPROVED Requirement's content_hash changes:

1. Previous version -> SUPERSEDED (the edit endpoint already bumps `version` and
   recomputes `content_hash` — see routers/requirements.py — this module reacts to
   that change).
2. TestCases whose upstream_req_hash != requirement.content_hash -> SUSPECT.
3. TestScripts whose parent TestCase is SUSPECT -> SUSPECT.
4. Artifacts (BRD/FSD/SolutionDoc) whose requirement_ids includes this REQ-ID -> stale=True.
5. Nothing is ever deleted — a human may have hand-edited a suspect item.
6. Caller is responsible for the UI banner text; this module returns the affected counts.
"""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.db.models import Artifact, AuditEvent, Requirement, TestCase, TestScript


# Function: propagate_suspect
async def propagate_suspect(session: AsyncSession, requirement: Requirement, actor: str) -> dict:
    """Call this AFTER a Requirement's content_hash has already changed and been
    flushed (not necessarily committed) — reads requirement.content_hash as the new
    value to compare every downstream upstream_*_hash against."""
    result = await session.execute(
        select(TestCase).where(TestCase.requirement_id == requirement.id, TestCase.upstream_req_hash != requirement.content_hash)
    )
    suspect_test_cases = list(result.scalars().all())
    for tc in suspect_test_cases:
        if tc.status != "SUSPECT":
            tc.status = "SUSPECT"

    suspect_scripts: list[TestScript] = []
    if suspect_test_cases:
        tc_ids = [tc.id for tc in suspect_test_cases]
        script_result = await session.execute(select(TestScript).where(TestScript.test_case_id.in_(tc_ids)))
        suspect_scripts = list(script_result.scalars().all())
        for ts in suspect_scripts:
            if ts.status != "SUSPECT":
                ts.status = "SUSPECT"

    artifact_result = await session.execute(select(Artifact).where(Artifact.project_id == requirement.project_id))
    stale_artifacts = []
    for artifact in artifact_result.scalars().all():
        if requirement.req_id in (artifact.requirement_ids or []) and not artifact.stale:
            artifact.stale = True
            stale_artifacts.append(artifact)

    session.add(AuditEvent(
        project_id=requirement.project_id, actor=actor, action="SUSPECT_PROPAGATED",
        entity_type="Requirement", entity_id=requirement.req_id,
        after={
            "suspect_test_cases": [tc.tc_id for tc in suspect_test_cases],
            "suspect_scripts": [ts.ts_id for ts in suspect_scripts],
            "stale_artifacts": [a.filename for a in stale_artifacts],
        },
    ))

    return {
        "requirement_id": requirement.req_id,
        "suspect_test_case_count": len(suspect_test_cases),
        "suspect_script_count": len(suspect_scripts),
        "stale_artifact_count": len(stale_artifacts),
        "suspect_test_case_ids": [tc.tc_id for tc in suspect_test_cases],
        "suspect_script_ids": [ts.ts_id for ts in suspect_scripts],
    }


# Function: get_requirement_impact
async def get_requirement_impact(session: AsyncSession, requirement: Requirement) -> dict:
    """§7 GET /requirements/{req_id}/impact — 'what breaks if I change this', computed
    without actually changing anything (read-only preview)."""
    result = await session.execute(select(TestCase).where(TestCase.requirement_id == requirement.id))
    test_cases = list(result.scalars().all())
    tc_ids = [tc.id for tc in test_cases]
    scripts = []
    if tc_ids:
        script_result = await session.execute(select(TestScript).where(TestScript.test_case_id.in_(tc_ids)))
        scripts = list(script_result.scalars().all())

    artifact_result = await session.execute(select(Artifact).where(Artifact.project_id == requirement.project_id))
    affected_artifacts = [a.filename for a in artifact_result.scalars().all() if requirement.req_id in (a.requirement_ids or [])]

    return {
        "requirement_id": requirement.req_id,
        "test_cases_affected": [tc.tc_id for tc in test_cases],
        "test_scripts_affected": [ts.ts_id for ts in scripts],
        "artifacts_affected": affected_artifacts,
    }
