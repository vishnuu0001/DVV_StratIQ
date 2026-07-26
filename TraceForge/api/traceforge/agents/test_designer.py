# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §5 Agent 3 — Test Designer. New this pass: also authors a TestPlan (project-level
# Date: 2025-12-31
# ---------------------------------------------------------------------------
"""§5 Agent 3 — Test Designer. New this pass: also authors a TestPlan (project-level
scope/strategy/environments), not just per-requirement TestCases, per the user's
explicit ask for Test Plan generation alongside Test Cases."""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from collections.abc import Awaitable, Callable

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from traceforge.agents.base import batched, call_agent_llm
from traceforge.agents.coverage_policy import check_coverage
from traceforge.config import AGENT_BATCH_SIZE_CHUNKS, FAST_PIPELINE, TEST_CASE_MAX_TOKENS, TEST_PLAN_MAX_TOKENS
from traceforge.db.ids import allocate_next_id
from traceforge.db.models import Project, Requirement, TestCase, TestPlan, TestPlanCitation
from traceforge.indexing.retriever import hybrid_search, similarity_search
from traceforge.llm.ollama import OllamaProvider

_TC_SYSTEM_PROMPT = """You are a senior test architect. For the requirement below, design test cases.

REQUIREMENT {req_id} [{ears_pattern}]:
{statement}

ACCEPTANCE CRITERIA:
{acceptance_criteria}

SOURCE CONTEXT (for realistic test data — use actual field names, codes, and values found here):
{cited_chunks}

INCIDENT EVIDENCE (real failures observed in production for this application — design NEGATIVE
and EDGE cases that would have caught these):
{related_incident_clusters}

Rules:
- Every test case maps to exactly one requirement and cites which acceptance criteria it verifies.
- Steps must be concrete and executable by a person who has never seen the system:
  bad  -> "Verify order is processed correctly"
  good -> "Click [Submit Order]. Expected: order status changes to 'Confirmed' and an
           order number in format ORD-NNNNNNNN is displayed in the confirmation banner."
- Use real field names and codes from the source context. Never use placeholder data
  like 'test123' or 'John Doe' if the source gives you actual formats.
- Derive at least one NEGATIVE case from the EARS 'unwanted behaviour' clause if present,
  or from the incident evidence.
- Assign test_level based on where the requirement is verifiable, not by default.

Return JSON matching this schema, and nothing else:
{{"test_cases": [{{
  "title": str, "test_type": "POSITIVE|NEGATIVE|EDGE|BOUNDARY|NEGATIVE_SECURITY|PERFORMANCE",
  "test_level": "UNIT|API|UI_E2E|INTEGRATION|UAT", "priority": "P1|P2|P3",
  "preconditions": [str, ...],
  "steps": [{{"step_no": int, "action": str, "expected_result": str, "test_data": str}}]
}}]}}"""

_GAP_REPROMPT = "\n\nThe previous attempt had these coverage gaps — fix them specifically:\n{gaps}"


class ExtractedTestCase(BaseModel):
    title: str
    test_type: str
    test_level: str
    priority: str = "P2"
    preconditions: list[str] = Field(default_factory=list)
    steps: list[dict] = Field(default_factory=list)


class TestDesignSummary(BaseModel):
    test_plan_id: uuid.UUID | None = None
    test_cases_created: int = 0
    warnings: list[str] = Field(default_factory=list)


# Function: _content_hash
def _content_hash(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


# Function: _draft_test_plan_content
async def _draft_test_plan_content(
    session: AsyncSession, project: Project, requirements: list[Requirement], pipeline_run_id: uuid.UUID | None,
) -> dict:
    if FAST_PIPELINE:
        return {
            "scope": f"Validate all {len(requirements)} approved requirements for {project.name}.",
            "strategy": "Risk-based positive, negative, integration, regression, and acceptance testing with requirement-level traceability.",
            "environments": ["QA", "UAT"],
            "schedule": {"phases": ["Test design", "Execution", "Defect retest", "Regression", "UAT sign-off"]},
            "entry_criteria": ["Requirements approved", "QA environment available", "Test data prepared"],
            "exit_criteria": ["All P1/P2 tests executed", "No open critical defects", "Traceability reviewed"],
        }

    provider = OllamaProvider()
    req_summary = "\n".join(f"- {r.req_id} [{r.level}]: {r.title}" for r in requirements[:60])
    system = (
        "You are a senior test lead writing a Test Plan for a project. Return JSON only: "
        '{"scope": str, "strategy": str, "environments": [str, ...], '
        '"schedule": {"phases": [str, ...]}, "entry_criteria": [str, ...], "exit_criteria": [str, ...]}'
    )
    user = f"Project: {project.name}\nClient: {project.client_name or 'N/A'}\n\nApproved requirements:\n{req_summary}"
    parsed, _ = await call_agent_llm(
        provider, session, agent_name="test_designer_plan", system=system, user=user,
        pipeline_run_id=pipeline_run_id, max_tokens=TEST_PLAN_MAX_TOKENS,
    )
    return parsed or {}


# Function: _cite_test_plan_from_requirements
async def _cite_test_plan_from_requirements(session: AsyncSession, plan: TestPlan, requirements: list[Requirement]) -> None:
    """No indexed chunks at all (pure-JIRA/manual project) — cite the requirement
    statements themselves via their own citations so P1 still holds."""
    cited_chunk_ids: set[uuid.UUID] = set()
    for req in requirements[:3]:
        for citation in req.citations:
            if citation.chunk_id in cited_chunk_ids:
                continue
            session.add(TestPlanCitation(test_plan_id=plan.id, chunk_id=citation.chunk_id, relevance=0.5, quoted_span=citation.quoted_span))
            cited_chunk_ids.add(citation.chunk_id)


# Function: _author_test_plan
async def _author_test_plan(session: AsyncSession, project: Project, requirements: list[Requirement], pipeline_run_id: uuid.UUID | None) -> TestPlan:
    parsed = await _draft_test_plan_content(session, project, requirements, pipeline_run_id)

    plan = TestPlan(
        project_id=project.id, pipeline_run_id=pipeline_run_id, title=f"{project.name} Test Plan",
        scope=parsed.get("scope", "Covers all APPROVED requirements for this project."),
        strategy=parsed.get("strategy", "Risk-based test design per requirement, with automated regression via generated scripts."),
        environments=parsed.get("environments", ["QA", "UAT"]),
        schedule=parsed.get("schedule", {}),
        entry_exit_criteria={"entry": parsed.get("entry_criteria", []), "exit": parsed.get("exit_criteria", [])},
        status="DRAFT", version=1,
    )
    session.add(plan)
    await session.flush()

    # P1 for TestPlan too: cite the requirements it was scoped from.
    top_chunks = [] if FAST_PIPELINE else await similarity_search(session, project.id, project.name, top_k=3)
    for chunk in (top_chunks or []):
        session.add(TestPlanCitation(test_plan_id=plan.id, chunk_id=chunk.id, relevance=1.0, quoted_span=chunk.text[:300]))
    if not top_chunks:
        await _cite_test_plan_from_requirements(session, plan, requirements)

    await session.commit()
    return plan


# Function: _build_test_case_prompt
async def _build_test_case_prompt(session: AsyncSession, project_id: uuid.UUID, requirement: Requirement) -> str:
    cited_text = "\n---\n".join(c.quoted_span for c in requirement.citations[:5])
    incident_chunks = await hybrid_search(session, project_id, f"{requirement.title} {requirement.statement}", top_k=5)
    incident_text = "\n---\n".join(c.text for c in incident_chunks if "INCIDENT PATTERN" in c.text) or "(none found)"

    return _TC_SYSTEM_PROMPT.format(
        req_id=requirement.req_id, ears_pattern=requirement.ears_pattern, statement=requirement.statement,
        acceptance_criteria="\n".join(f"- {ac}" for ac in requirement.acceptance_criteria),
        cited_chunks=cited_text or "(no additional context)", related_incident_clusters=incident_text,
    )


# Function: _build_test_cases_from_items
async def _build_test_cases_from_items(
    session: AsyncSession, project_id: uuid.UUID, requirement: Requirement, raw_items: list[dict],
) -> list[TestCase]:
    test_cases: list[TestCase] = []
    for raw in raw_items:
        try:
            extracted = ExtractedTestCase.model_validate(raw)
        except Exception:  # noqa: BLE001
            continue
        tc_id = await allocate_next_id(session, project_id, "TC")
        content_hash = _content_hash({"title": extracted.title, "steps": extracted.steps})
        tc = TestCase(
            tc_id=tc_id, project_id=project_id, requirement_id=requirement.id, title=extracted.title,
            test_type=extracted.test_type, test_level=extracted.test_level, preconditions=extracted.preconditions,
            steps=extracted.steps, priority=extracted.priority if extracted.priority in ("P1", "P2", "P3") else "P2",
            status="DRAFT", upstream_req_hash=requirement.content_hash, content_hash=content_hash, version=1, created_by_agent=True,
        )
        session.add(tc)
        test_cases.append(tc)
    return test_cases


# Function: _generate_test_cases_for_requirement
async def _generate_test_cases_for_requirement(
    session: AsyncSession, provider: OllamaProvider, project_id: uuid.UUID, requirement: Requirement, pipeline_run_id: uuid.UUID | None,
) -> list[TestCase]:
    system = await _build_test_case_prompt(session, project_id, requirement)

    test_cases: list[TestCase] = []
    gap_note = ""
    max_attempts = 2
    for attempt in range(max_attempts):  # spec: auto-reprompt once with the specific gap, then accept
        parsed, warnings = await call_agent_llm(
            provider, session, agent_name="test_designer_tc", system=system + gap_note, user="Generate the test cases now.",
            pipeline_run_id=pipeline_run_id, max_tokens=TEST_CASE_MAX_TOKENS,
        )
        raw_items = (parsed or {}).get("test_cases", []) if isinstance(parsed, dict) else []
        test_cases = await _build_test_cases_from_items(session, project_id, requirement, raw_items)
        await session.flush()

        gaps = check_coverage(requirement, test_cases)
        if not gaps or attempt == max_attempts - 1:
            # No gaps, or this was the last allowed attempt — spec says accept what we
            # have rather than deleting it. A prior version of this loop deleted the
            # final attempt's rows too whenever gaps were still present, silently
            # leaving the requirement with zero test cases despite the LLM having
            # produced some and the run reporting a nonzero created-count for it.
            break
        gap_note = _GAP_REPROMPT.format(gaps="\n".join(f"- {g.description}" for g in gaps))
        for tc in test_cases:
            await session.delete(tc)
        await session.flush()

    return test_cases


# Function: _fast_test_level
def _fast_test_level(requirement: Requirement) -> str:
    text = f"{requirement.title} {requirement.statement}".lower()
    if requirement.level == "NON_FUNCTIONAL":
        return "API" if any(word in text for word in ("latency", "throughput", "performance")) else "UAT"
    if any(word in text for word in ("api", "interface", "integration", "service")):
        return "INTEGRATION"
    return "UAT" if requirement.level == "BUSINESS" else "UI_E2E"


# Function: _build_positive_steps
def _build_positive_steps(requirement: Requirement, criteria: list[str], trigger: str) -> list[dict]:
    positive_steps = [
        {"step_no": 1, "action": f"Prepare a valid end-to-end record for {requirement.title} and satisfy every documented prerequisite.",
         "expected_result": "The record is accepted for processing and all prerequisite states are confirmed.",
         "test_data": "Use representative production-like data matching the documented formats and business rules."},
        {"step_no": 2, "action": f"Initiate the documented trigger: {trigger or requirement.statement}",
         "expected_result": "The workflow starts once, retains the submitted data, and enters the expected initial state.",
         "test_data": "Use the valid record prepared in step 1."},
    ]
    for index, criterion in enumerate(criteria, start=1):
        positive_steps.append({
            "step_no": len(positive_steps) + 1,
            "action": f"Complete functional checkpoint {index} and observe the resulting system state.",
            "expected_result": criterion,
            "test_data": f"Use the same correlated record; verify acceptance criterion {index} without resetting the workflow.",
        })
    positive_steps.append({
        "step_no": len(positive_steps) + 1,
        "action": "Retrieve the completed record through the downstream interface or persisted view and reconcile its audit history.",
        "expected_result": "The final state, downstream data, and audit trail are consistent with every preceding checkpoint.",
        "test_data": "Use the identifier created by the end-to-end workflow.",
    })
    return positive_steps


# Function: _build_negative_steps
def _build_negative_steps(requirement: Requirement, criteria: list[str]) -> list[dict]:
    return [
        {"step_no": 1, "action": "Create a valid baseline record, then remove or invalidate one mandatory value, state, permission, or dependency.",
         "expected_result": "The invalid condition is isolated while the baseline record remains unchanged.",
         "test_data": f"Violate the first applicable rule: {criteria[0]}"},
        {"step_no": 2, "action": f"Attempt the complete behavior with the invalid condition: {requirement.statement}",
         "expected_result": "Processing is rejected or safely stopped at the responsible checkpoint with actionable feedback.",
         "test_data": "Use the invalid variant from step 1."},
        {"step_no": 3, "action": "Correct the invalid value and resubmit the same business transaction.",
         "expected_result": "The corrected transaction succeeds without duplicate records or residual partial state from the failed attempt.",
         "test_data": "Reuse the same business key and restore a documented valid value."},
        {"step_no": 4, "action": "Review persisted data, downstream messages, notifications, and audit events for both attempts.",
         "expected_result": "The failed attempt has no unintended side effects; rejection and successful recovery are both traceable.",
         "test_data": "Correlate events using the transaction identifier."},
    ]


# Function: _build_edge_steps
def _build_edge_steps(requirement: Requirement, criteria: list[str], trigger: str) -> list[dict]:
    edge_steps = [
        {"step_no": 1, "action": "Prepare minimum valid data and identify every upstream and downstream checkpoint in the documented flow.",
         "expected_result": "All dependencies are reachable and the smallest supported record is ready.",
         "test_data": "Use minimum-length optional data while retaining every mandatory value."},
        {"step_no": 2, "action": f"Execute the end-to-end scenario and interrupt or repeat the trigger once during processing: {trigger or requirement.statement}",
         "expected_result": "The system handles retry, duplicate submission, or interruption without corrupting state or executing the transaction twice.",
         "test_data": "Submit the same correlation/business key twice or resume after a controlled interruption."},
    ]
    for index, criterion in enumerate(criteria, start=1):
        edge_steps.append({
            "step_no": len(edge_steps) + 1,
            "action": f"Trace alternate-path checkpoint {index} across the UI/API, persistence layer, and dependent service where applicable.",
            "expected_result": criterion,
            "test_data": f"Retain the same correlation identifier through acceptance criterion {index}.",
        })
    edge_steps.append({
        "step_no": len(edge_steps) + 1,
        "action": "Complete reconciliation after the retry/interruption and compare the final result with a normal successful transaction.",
        "expected_result": "Exactly one consistent business outcome exists and all recovery activity is auditable.",
        "test_data": "Compare identifiers, state history, downstream events, and notification counts.",
    })
    return edge_steps


# Function: _boundary_definition
def _boundary_definition(requirement: Requirement, criteria: list[str]) -> tuple[str, str, list[dict]]:
    return ("BOUNDARY", f"Boundary values — {requirement.title}", [
        {"step_no": 1, "action": "Identify each documented numeric, length, date, volume, or timeout boundary.", "expected_result": "The exact lower and upper limits and units are recorded before execution.", "test_data": requirement.statement},
        {"step_no": 2, "action": "Execute with a value immediately below the lower boundary.", "expected_result": "The value is rejected with no partial processing.", "test_data": "lower-boundary minus one valid unit"},
        {"step_no": 3, "action": "Execute at the lower and upper boundaries.", "expected_result": "; ".join(criteria), "test_data": "exact lower boundary; exact upper boundary"},
        {"step_no": 4, "action": "Execute immediately above the upper boundary and reconcile persisted state.", "expected_result": "The value is rejected and prior valid boundary transactions remain unchanged.", "test_data": "upper-boundary plus one valid unit"},
    ])


# Function: _security_definition
def _security_definition(requirement: Requirement, criteria: list[str]) -> tuple[str, str, list[dict]]:
    return ("NEGATIVE_SECURITY", f"Authorization enforcement — {requirement.title}", [
        {"step_no": 1, "action": "Prepare authorized, unauthorized, expired-session, and cross-tenant identities.", "expected_result": "Each identity has a verified and distinct access scope.", "test_data": "Approved role matrix and isolated tenant records."},
        {"step_no": 2, "action": f"Execute the protected workflow as the authorized identity: {requirement.statement}", "expected_result": "; ".join(criteria), "test_data": "Authorized identity and valid record."},
        {"step_no": 3, "action": "Repeat with an unauthorized role and an expired or tampered session.", "expected_result": "Access is denied without revealing protected data or changing persisted state.", "test_data": "Unauthorized role; expired token; invalid signature."},
        {"step_no": 4, "action": "Review security and audit events for all attempts.", "expected_result": "Allowed and denied actions are attributable, timestamped, and contain no secret values.", "test_data": "Correlation IDs from each attempt."},
    ])


# Function: _performance_definition
def _performance_definition(requirement: Requirement, criteria: list[str]) -> tuple[str, str, list[dict]]:
    return ("PERFORMANCE", f"Capacity and response — {requirement.title}", [
        {"step_no": 1, "action": "Extract the documented service level, workload profile, measurement window, and success threshold.", "expected_result": "A measurable baseline and pass/fail threshold are defined from the requirement.", "test_data": requirement.statement},
        {"step_no": 2, "action": "Warm the environment and execute the baseline workload.", "expected_result": "Baseline metrics are stable and free from startup/cache distortion.", "test_data": "Production-representative payload and concurrency."},
        {"step_no": 3, "action": "Run sustained expected load and a controlled peak above expected load.", "expected_result": "; ".join(criteria), "test_data": "Expected and peak workload profiles."},
        {"step_no": 4, "action": "Return to normal load and verify recovery, resource release, errors, and data integrity.", "expected_result": "The service recovers within the documented target with no lost, duplicated, or corrupted transactions.", "test_data": "Metrics, logs, traces, and transaction reconciliation report."},
    ])


# Function: _build_test_case_definitions
def _build_test_case_definitions(requirement: Requirement, criteria: list[str], trigger: str) -> list[tuple[str, str, list[dict]]]:
    definitions = [
        ("POSITIVE", f"End-to-end success — {requirement.title}", _build_positive_steps(requirement, criteria, trigger)),
        ("NEGATIVE", f"Validation and recovery — {requirement.title}", _build_negative_steps(requirement, criteria)),
        ("EDGE", f"Retry, interruption, and alternate flow — {requirement.title}", _build_edge_steps(requirement, criteria, trigger)),
    ]

    requirement_text = f"{requirement.title} {requirement.statement} {' '.join(criteria)}".lower()
    if re.search(r"\b\d+(?:\.\d+)?\b|minimum|maximum|limit|range|threshold", requirement_text):
        definitions.append(_boundary_definition(requirement, criteria))
    if any(word in requirement_text for word in ("auth", "permission", "role", "access", "security", "credential")):
        definitions.append(_security_definition(requirement, criteria))
    if requirement.level == "NON_FUNCTIONAL" or any(word in requirement_text for word in ("latency", "throughput", "performance", "concurrent", "response time")):
        definitions.append(_performance_definition(requirement, criteria))

    return definitions


# Function: _build_gherkin
def _build_gherkin(requirement: Requirement, title: str, steps: list[dict]) -> str:
    return (
        f"Feature: {requirement.title}\n\nScenario: {title}\n"
        + "\n".join(
            f"  {'Given' if index == 0 else 'When' if index == 1 else 'Then'} {step['action']}\n"
            f"  And expect {step['expected_result']}"
            for index, step in enumerate(steps)
        )
    )


# Function: _build_fast_test_case
async def _build_fast_test_case(
    session: AsyncSession, project_id: uuid.UUID, requirement: Requirement, level: str, preconditions: list[str],
    test_type: str, title: str, steps: list[dict],
) -> TestCase:
    tc_id = await allocate_next_id(session, project_id, "TC")
    tc = TestCase(
        tc_id=tc_id, project_id=project_id, requirement_id=requirement.id, title=title,
        test_type=test_type, test_level=level,
        preconditions=preconditions,
        steps=steps, priority="P1" if requirement.priority == "MUST" else "P2",
        gherkin=_build_gherkin(requirement, title, steps),
        status="DRAFT", upstream_req_hash=requirement.content_hash,
        content_hash=_content_hash({"title": title, "steps": steps}), version=1, created_by_agent=True,
    )
    session.add(tc)
    return tc


# Function: _generate_fast_test_cases_for_requirement
async def _generate_fast_test_cases_for_requirement(
    session: AsyncSession, project_id: uuid.UUID, requirement: Requirement,
) -> list[TestCase]:
    """Build a detailed scenario matrix from the qwen-extracted requirement and
    acceptance criteria without making one additional GPU call per requirement."""
    level = _fast_test_level(requirement)
    criteria = requirement.acceptance_criteria or [requirement.statement]
    precondition = str((requirement.ears_parts or {}).get("precondition") or "").strip()
    trigger = str((requirement.ears_parts or {}).get("trigger") or "").strip()
    preconditions = [
        value for value in (
            "The approved requirement, integrated dependencies, and test environment are available.",
            precondition or None,
        ) if value
    ]

    definitions = _build_test_case_definitions(requirement, criteria, trigger)

    generated: list[TestCase] = []
    for test_type, title, steps in definitions:
        tc = await _build_fast_test_case(session, project_id, requirement, level, preconditions, test_type, title, steps)
        generated.append(tc)
    return generated


# Function: run_test_designer
async def run_test_designer(
    session: AsyncSession, *, project_id: uuid.UUID, pipeline_run_id: uuid.UUID | None,
    progress: Callable[[int, int, int], Awaitable[None]] | None = None,
) -> TestDesignSummary:
    project = await session.get(Project, project_id)
    if project is None:
        raise ValueError(f"project {project_id} not found")

    result = await session.execute(
        select(Requirement)
        .options(selectinload(Requirement.citations))
        .where(Requirement.project_id == project_id, Requirement.status == "APPROVED")
        .order_by(Requirement.req_id)
    )
    requirements = list(result.scalars().all())
    if not requirements:
        raise ValueError("No APPROVED requirements — cannot design tests for an empty requirement set.")

    plan = await _author_test_plan(session, project, requirements, pipeline_run_id)

    provider = OllamaProvider()
    summary = TestDesignSummary(test_plan_id=plan.id)
    batch_size = 20 if FAST_PIPELINE else max(1, AGENT_BATCH_SIZE_CHUNKS // 2)
    completed = 0
    for batch in batched(requirements, batch_size):
        for requirement in batch:
            test_cases = (
                await _generate_fast_test_cases_for_requirement(session, project_id, requirement)
                if FAST_PIPELINE
                else await _generate_test_cases_for_requirement(session, provider, project_id, requirement, pipeline_run_id)
            )
            summary.test_cases_created += len(test_cases)
            completed += 1
            if not test_cases:
                summary.warnings.append(f"{requirement.req_id}: no test cases could be generated that satisfy the coverage policy.")
        await session.commit()
        if progress:
            await progress(completed, len(requirements), summary.test_cases_created)

    return summary
