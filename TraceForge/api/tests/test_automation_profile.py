from __future__ import annotations

import json
import uuid

from types import SimpleNamespace

from traceforge.agents.script_gen.playwright import PlaywrightEmitter, _parse_tc_metadata, _verified_automation_status, runtime_with_context
from traceforge.agents.script_gen.semantic_runtime import PLAYWRIGHT_RUNTIME_MODULE
from traceforge.db.models import Chunk, Requirement, SourceCitation, SourceDocument, TestCase
from traceforge.routers.testcases import apply_automation_profile
from traceforge.schemas.testcase import AutomationProfileApply


def test_verified_status_classifies_integration_case_as_manual_only():
    test_case = SimpleNamespace(test_level="INTEGRATION", steps=[])

    status, blockers = _verified_automation_status(
        test_case,
        {"automation_status": "AUTOMATION_BLOCKED", "automation_blockers": ["Missing UI locators"]},
    )

    assert status == "MANUAL_ONLY"
    assert blockers == []


async def test_automation_profile_unblocks_only_reviewed_ui_cases(session, project):
    document = SourceDocument(
        project_id=project.id, source_type="UPLOAD", filename="automation.txt", blob_uri="/tmp/automation.txt",
        sha256=uuid.uuid4().hex.ljust(64, "0"), doc_class="AS_IS_DOC", status="INDEXED",
    )
    session.add(document)
    await session.flush()
    chunk = Chunk(
        source_document_id=document.id, project_id=project.id, ordinal=0,
        text="The application shall submit the reviewed transaction.", token_count=7, locator={},
    )
    session.add(chunk)
    await session.flush()
    requirement = Requirement(
        req_id="REQ-AUTO", project_id=project.id, level="FUNCTIONAL", title="Reviewed transaction",
        statement="The application shall submit the reviewed transaction.", ears_pattern="UBIQUITOUS",
        ears_parts={}, acceptance_criteria=["The transaction is accepted."], priority="MUST",
        ambiguity_score=0, ambiguity_flags=[], conflict_flags=[], status="APPROVED", content_hash="a" * 64,
    )
    session.add(requirement)
    await session.flush()
    session.add(SourceCitation(
        requirement_id=requirement.id, chunk_id=chunk.id, relevance=1.0,
        quoted_span="The application shall submit the reviewed transaction.",
    ))
    reviewed = TestCase(
        tc_id="TC-AUTO-1", project_id=project.id, requirement_id=requirement.id,
        title="Submit reviewed transaction", test_type="POSITIVE", test_level="UI_E2E",
        preconditions=[], steps=[{
            "step_no": 1, "action": "Select Submit transaction",
            "expected_result": "The transaction is accepted.", "test_data": "Approved transaction",
        }],
        gherkin=json.dumps({"automation_status": "MANUAL_ONLY"}), priority="P1",
        status="APPROVED", upstream_req_hash=requirement.content_hash, content_hash="b" * 64,
    )
    unresolved = TestCase(
        tc_id="TC-AUTO-2", project_id=project.id, requirement_id=requirement.id,
        title="Unresolved transaction", test_type="NEGATIVE", test_level="UI_E2E",
        preconditions=[], steps=[{
            "step_no": 1, "action": "[EXECUTION DETAIL BLOCKED — field is unknown]",
            "expected_result": "[PENDING BUSINESS CONFIRMATION — result is unknown]",
        }],
        gherkin=json.dumps({"automation_status": "AUTOMATION_BLOCKED"}), priority="P1",
        status="APPROVED", upstream_req_hash=requirement.content_hash, content_hash="c" * 64,
    )
    session.add_all([reviewed, unresolved])
    await session.flush()

    result = await apply_automation_profile(
        project.id,
        AutomationProfileApply(
            test_case_ids=[reviewed.id, unresolved.id], base_url="https://test.example.com",
            auth_method="Playwright storage state", locators={"Select Submit transaction": "[data-testid=submit]"},
            assertions={"The transaction is accepted.": "[data-testid=accepted]"},
            test_data_factory="Worker-scoped transaction factory", cleanup="Delete transaction through test API",
            worker_isolation=True,
        ),
        session,
        {"username": "test-lead"},
    )

    assert result["ready"] == ["TC-AUTO-1"]
    assert result["blocked"][0]["tc_id"] == "TC-AUTO-2"
    assert "blocked and pending execution steps" in result["blocked"][0]["reasons"][-1]
    metadata = _parse_tc_metadata(reviewed)
    assert _verified_automation_status(reviewed, metadata)[0] == "READY_FOR_UI_AUTOMATION"
    assert metadata["automation_context"]["auth"] == {"method": "Playwright storage state"}
    assert "secret" not in json.dumps(metadata).lower()

    code, _, _ = await PlaywrightEmitter().generate(
        session, None, reviewed, requirement,
        {"batch_scenario": reviewed.title, "sources_label": "automation.txt"}, None,
    )
    assert "https://test.example.com/" in code
    assert '"Select Submit transaction": "[data-testid=submit]"' in code
    assert '"The transaction is accepted.": "[data-testid=accepted]"' in code
    assert "Playwright storage state" in code
    shared_runtime = runtime_with_context(metadata, PLAYWRIGHT_RUNTIME_MODULE)
    assert "https://test.example.com/" in shared_runtime
    assert '"Select Submit transaction": "[data-testid=submit]"' in shared_runtime