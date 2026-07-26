# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/tests (test_workspace_governance.py)
# Date: 2025-09-05
# ---------------------------------------------------------------------------
from __future__ import annotations

import pytest
from pydantic import ValidationError

from traceforge.db.models import Chunk, Requirement, SourceCitation, SourceDocument
from traceforge.routers.workspace import (
    _canonical_hash, create_baseline, requirement_quality,
)
from traceforge.schemas.workspace import BaselineCreate, ConnectorConfigUpsert


# Function: test_connector_configuration_rejects_persisted_secrets
def test_connector_configuration_rejects_persisted_secrets():
    with pytest.raises(ValidationError):
        ConnectorConfigUpsert(
            connector_type="JIRA",
            config={"base_url": "https://example.atlassian.net", "api_token": "secret"},
        )


# Function: test_baseline_hash_is_canonical
def test_baseline_hash_is_canonical():
    assert _canonical_hash({"b": 2, "a": 1}) == _canonical_hash({"a": 1, "b": 2})


# Function: test_quality_and_baseline_capture_real_traceability
async def test_quality_and_baseline_capture_real_traceability(session, project):
    source = SourceDocument(
        project_id=project.id, source_type="UPLOAD", filename="scope.md",
        blob_uri="/tmp/scope.md", sha256="a" * 64, doc_class="SOW",
        status="INDEXED",
    )
    session.add(source)
    await session.flush()
    chunk = Chunk(
        source_document_id=source.id, project_id=project.id, ordinal=0,
        text="The portal shall authenticate users.", token_count=6,
        locator={"section": "Authentication"},
    )
    session.add(chunk)
    await session.flush()
    requirement = Requirement(
        req_id="REQ-0001", project_id=project.id, level="FUNCTIONAL",
        title="Authenticate users",
        statement="The portal shall authenticate users.",
        ears_pattern="UBIQUITOUS", ears_parts={"system_name": "portal"},
        rationale="Required by scope", acceptance_criteria=[],
        priority="MUST", ambiguity_score=0.0, ambiguity_flags=[],
        status="APPROVED", content_hash="b" * 64, version=1,
        created_by_agent=True,
    )
    session.add(requirement)
    await session.flush()
    session.add(SourceCitation(
        requirement_id=requirement.id, chunk_id=chunk.id, relevance=1.0,
        quoted_span="The portal shall authenticate users.",
    ))
    await session.commit()

    quality = await requirement_quality(
        project.id, session=session, user={"username": "tester"},
    )
    assert quality["quality_gate"] == "REVIEW"
    assert quality["findings"][0]["code"] == "MISSING_ACCEPTANCE_CRITERIA"

    baseline = await create_baseline(
        project.id, BaselineCreate(name="Release 1"),
        session=session, user={"username": "tester"},
    )
    assert baseline.snapshot["requirements"][0]["req_id"] == "REQ-0001"
    assert len(baseline.sha256) == 64
