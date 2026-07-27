# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §5 Agent 3 — Test Designer. New this pass: also authors a TestPlan (project-level
# Date: 2025-12-31
# ---------------------------------------------------------------------------
"""§5 Agent 3 — Test Designer. New this pass: also authors a TestPlan (project-level
scope/strategy/environments), not just per-requirement TestCases, per the user's
explicit ask for Test Plan generation alongside Test Cases."""
from __future__ import annotations

import asyncio
import hashlib
import json
import re
import uuid
from collections.abc import Awaitable, Callable
from typing import Literal

from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from traceforge.agents.base import call_agent_llm
from traceforge.agents.coverage_policy import check_coverage
from traceforge.config import (
    FAST_PIPELINE,
    TEST_CASE_MAX_TOKENS,
    TEST_CASE_OUTLINE_MAX_TOKENS,
    TEST_DESIGN_CONCURRENCY,
    TEST_PLAN_MAX_TOKENS,
)
from traceforge.db.ids import allocate_next_id
from traceforge.db.models import Chunk, Project, Requirement, TestCase, TestPlan, TestPlanCitation
from traceforge.db.session import SessionLocal
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
- The orchestrator requests category-specific batches. Generate only the requested test_type
  and count in each batch; do not create near-duplicate titles or steps.
- The completed matrix will contain at least eight distinct scenarios per requirement:
  at least three POSITIVE, three NEGATIVE, and two EDGE cases.
- Add a focused POSITIVE and NEGATIVE case for every acceptance criterion.
- The POSITIVE set must cover the primary end-to-end flow, an alternate valid business flow,
  and persistence/downstream reconciliation after reload.
- The NEGATIVE set must separately cover mandatory-input validation, business-rule rejection,
  and unauthorized or invalid-state access with no partial side effects.
- The EDGE set must separately cover retry/idempotency and concurrency, interruption, expiry,
  or recovery behavior.
- When the requirement contains limits, ranges, dates, lengths, volumes, or timeouts, add
  dedicated BOUNDARY cases for below-minimum, exact-boundary, and above-maximum behavior.
- When authentication, authorization, roles, tenants, sensitive data, or permissions are
  relevant, add a NEGATIVE_SECURITY case covering least privilege and cross-tenant isolation.
- For non-functional requirements, add a PERFORMANCE scenario with measurable workload,
  threshold, recovery, and data-integrity assertions.
- All cases must be executable with Playwright and use test_level UI_E2E. API checks may use
  Playwright's request fixture from the same UI_E2E scenario.
- Each case must contain 4-8 concrete steps and be executable by a person who has never seen the system:
  bad  -> "Verify order is processed correctly"
  good -> "Click [Submit Order]. Expected: order status changes to 'Confirmed' and an
           order number in format ORD-NNNNNNNN is displayed in the confirmation banner."
- Use real field names and codes from the source context. Never use placeholder data
  like 'test123' or 'John Doe' if the source gives you actual formats.
- Derive at least one NEGATIVE case from the EARS 'unwanted behaviour' clause if present,
  or from the incident evidence.
- Set test_level to UI_E2E because the approved automation target is Playwright.

Return JSON matching this schema, and nothing else:
{{"test_cases": [{{
  "title": str, "test_type": "POSITIVE|NEGATIVE|EDGE|BOUNDARY|NEGATIVE_SECURITY|PERFORMANCE",
  "test_level": "UNIT|API|UI_E2E|INTEGRATION|UAT", "priority": "P1|P2|P3",
  "preconditions": [str, ...],
  "steps": [{{"step_no": int, "action": str, "expected_result": str, "test_data": str}}]
}}]}}"""

class ExtractedTestCase(BaseModel):
    title: str = Field(min_length=8)
    test_type: Literal["POSITIVE", "NEGATIVE", "EDGE", "BOUNDARY", "NEGATIVE_SECURITY", "PERFORMANCE"]
    test_level: str
    priority: str = "P2"
    preconditions: list[str] = Field(default_factory=list)
    steps: list[dict] = Field(min_length=4, max_length=8)


class ScenarioOutline(BaseModel):
    title: str = Field(min_length=8)
    test_type: Literal["POSITIVE", "NEGATIVE", "EDGE", "BOUNDARY", "NEGATIVE_SECURITY", "PERFORMANCE"]
    objective: str = Field(min_length=8)
    test_data: str = Field(min_length=3)
    acceptance_criteria: list[int] = Field(default_factory=list)
    priority: str = "P2"


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
    if FAST_PIPELINE:
        # Avoid swapping the embedding model into limited VRAM once per requirement.
        # Incident-pattern chunks are already explicitly labelled during ingestion.
        incident_chunks = list((await session.scalars(
            select(Chunk)
            .where(Chunk.project_id == project_id, Chunk.text.ilike("%INCIDENT PATTERN%"))
            .order_by(Chunk.ordinal)
            .limit(5)
        )).all())
    else:
        incident_chunks = await hybrid_search(
            session, project_id, f"{requirement.title} {requirement.statement}", top_k=5,
        )
    incident_text = "\n---\n".join(c.text for c in incident_chunks if "INCIDENT PATTERN" in c.text) or "(none found)"

    return _TC_SYSTEM_PROMPT.format(
        req_id=requirement.req_id, ears_pattern=requirement.ears_pattern, statement=requirement.statement,
        acceptance_criteria="\n".join(f"- {ac}" for ac in requirement.acceptance_criteria),
        cited_chunks=cited_text or "(no additional context)", related_incident_clusters=incident_text,
    )


# Function: _validate_test_case_items
def _validate_test_case_items(
    raw_items: list[dict],
    *,
    expected_type: str | None,
    seen_scenarios: set[str],
) -> tuple[list[ExtractedTestCase], list[str]]:
    test_cases: list[ExtractedTestCase] = []
    rejected: list[str] = []
    for item_number, raw in enumerate(raw_items, start=1):
        if not isinstance(raw, dict):
            rejected.append(f"item {item_number} was not a JSON object")
            continue
        normalized = dict(raw)
        normalized_type = str(normalized.get("test_type", "")).strip().upper().replace("-", "_").replace(" ", "_")
        if normalized_type == "EDGE_CASE":
            normalized_type = "EDGE"
        normalized["test_type"] = normalized_type
        try:
            extracted = ExtractedTestCase.model_validate(normalized)
        except Exception as exc:  # noqa: BLE001
            error_text = " ".join(str(exc).split())[:300]
            rejected.append(f"item {item_number} failed validation: {error_text}")
            continue
        if expected_type == "NEGATIVE" and extracted.test_type == "NEGATIVE_SECURITY":
            extracted.test_type = "NEGATIVE"
        if expected_type and extracted.test_type != expected_type:
            rejected.append(
                f"item {item_number} returned {extracted.test_type}, expected {expected_type}",
            )
            continue
        scenario_key = re.sub(r"[^a-z0-9]+", " ", extracted.title.lower()).strip()
        if scenario_key in seen_scenarios:
            rejected.append(f"item {item_number} duplicated scenario title '{extracted.title}'")
            continue
        seen_scenarios.add(scenario_key)
        test_cases.append(extracted)
    return test_cases, rejected


async def _persist_test_cases(
    session: AsyncSession,
    project_id: uuid.UUID,
    requirement: Requirement,
    drafts: list[ExtractedTestCase],
) -> list[TestCase]:
    test_cases: list[TestCase] = []
    for extracted in drafts:
        tc_id = await allocate_next_id(session, project_id, "TC")
        content_hash = _content_hash({"title": extracted.title, "steps": extracted.steps})
        tc = TestCase(
            tc_id=tc_id, project_id=project_id, requirement_id=requirement.id, title=extracted.title,
            test_type=extracted.test_type, test_level="UI_E2E", preconditions=extracted.preconditions,
            steps=extracted.steps, priority=extracted.priority if extracted.priority in ("P1", "P2", "P3") else "P2",
            status="DRAFT", upstream_req_hash=requirement.content_hash, content_hash=content_hash, version=1, created_by_agent=True,
        )
        session.add(tc)
        test_cases.append(tc)
    return test_cases


_CATEGORY_TARGETS = (("POSITIVE", 3), ("NEGATIVE", 3), ("EDGE", 2))
_BOUNDARY_TRIGGER_RE = re.compile(
    r"\b(\d+(?:\.\d+)?\s*(?:-|to|and)\s*\d+(?:\.\d+)?|maximum|minimum|limit|range|threshold|timeout)\b",
    re.IGNORECASE,
)
_SECURITY_TRIGGER_RE = re.compile(
    r"\b(auth(?:entication|orization)?|permission|role|tenant|access|credential|sensitive|security)\b",
    re.IGNORECASE,
)


def _category_targets_for_requirement(requirement: Requirement) -> list[tuple[str, int]]:
    targets = list(_CATEGORY_TARGETS)
    requirement_text = (
        f"{requirement.title} {requirement.statement} {' '.join(requirement.acceptance_criteria or [])}"
    )
    if _BOUNDARY_TRIGGER_RE.search(requirement_text):
        targets.append(("BOUNDARY", 1))
    if _SECURITY_TRIGGER_RE.search(requirement_text):
        targets.append(("NEGATIVE_SECURITY", 1))
    if requirement.level == "NON_FUNCTIONAL":
        targets.append(("PERFORMANCE", 1))
    return targets


def _expand_outline(requirement: Requirement, outline: ScenarioOutline) -> ExtractedTestCase:
    selected_criteria = [
        requirement.acceptance_criteria[index - 1]
        for index in outline.acceptance_criteria
        if 1 <= index <= len(requirement.acceptance_criteria)
    ] or requirement.acceptance_criteria or [requirement.statement]
    expected = "; ".join(selected_criteria)
    execution_action = {
        "POSITIVE": "Execute the valid primary or alternate business flow described by the scenario objective.",
        "NEGATIVE": "Execute the scenario with the identified invalid value, state, or missing prerequisite.",
        "EDGE": "Repeat, interrupt, expire, or concurrently execute the scenario using the same correlation key.",
        "BOUNDARY": "Execute below, at, and above the documented boundary using isolated records.",
        "NEGATIVE_SECURITY": "Execute with the least-privileged or unauthorized identity described by the scenario.",
        "PERFORMANCE": "Execute the documented workload and measurement window for the scenario.",
    }[outline.test_type]
    return ExtractedTestCase(
        title=outline.title,
        test_type=outline.test_type,
        test_level="UI_E2E",
        priority=outline.priority if outline.priority in ("P1", "P2", "P3") else "P2",
        preconditions=[
            "The approved requirement, Playwright environment, and isolated test identity are available.",
        ],
        steps=[
            {
                "step_no": 1,
                "action": f"Prepare an isolated record and correlation identifier for: {outline.objective}",
                "expected_result": "All documented prerequisites are satisfied and the test record is uniquely traceable.",
                "test_data": outline.test_data,
            },
            {
                "step_no": 2,
                "action": execution_action,
                "expected_result": "The application accepts or safely rejects the action exactly once without an unrelated error.",
                "test_data": outline.test_data,
            },
            {
                "step_no": 3,
                "action": "Observe the UI response and reconcile it with the mapped acceptance criteria.",
                "expected_result": expected,
                "test_data": "Capture visible messages, state, identifiers, response status, and relevant audit evidence.",
            },
            {
                "step_no": 4,
                "action": "Reload the record and reconcile persisted state, downstream effects, and audit history.",
                "expected_result": "The final state is consistent, traceable, and has no duplicate or partial side effects.",
                "test_data": "Reuse the worker-scoped correlation identifier created in step 1.",
            },
        ],
    )


async def _generate_outline_matrix(
    session: AsyncSession,
    provider: OllamaProvider,
    requirement: Requirement,
    pipeline_run_id: uuid.UUID | None,
    *,
    detailed_system: str,
    targets: list[tuple[str, int]],
) -> tuple[list[ExtractedTestCase], list[str]]:
    """Ask Ollama for compact predictions, then expand them into detailed cases locally."""
    context = detailed_system.split("Rules:", 1)[0]
    target_text = ", ".join(f"{minimum} {test_type}" for test_type, minimum in targets)
    system = (
        context
        + "\nRules:\n"
        "- Return compact scenario outlines only; the orchestrator expands them into reviewed steps.\n"
        "- Cover every acceptance criterion across the outlines using its 1-based number.\n"
        "- Keep every title, objective, and test_data value under 24 words.\n"
        "- Do not repeat titles or objectives.\n"
        "- Return JSON only with this schema:\n"
        '{"scenarios":[{"title":str,"test_type":"POSITIVE|NEGATIVE|EDGE|BOUNDARY|'
        'NEGATIVE_SECURITY|PERFORMANCE","objective":str,"test_data":str,'
        '"acceptance_criteria":[int],"priority":"P1|P2|P3"}]}'
    )
    parsed, warnings = await call_agent_llm(
        provider,
        session,
        agent_name="test_designer_outline_matrix",
        system=system,
        user=f"Generate exactly this scenario matrix: {target_text}.",
        pipeline_run_id=pipeline_run_id,
        max_tokens=TEST_CASE_OUTLINE_MAX_TOKENS,
    )
    raw_items = (parsed or {}).get("scenarios", []) if isinstance(parsed, dict) else []
    outlines: list[ScenarioOutline] = []
    diagnostics = list(warnings)
    seen: set[str] = set()
    for item_number, raw in enumerate(raw_items, start=1):
        if not isinstance(raw, dict):
            diagnostics.append(f"outline {item_number} was not a JSON object")
            continue
        normalized = dict(raw)
        normalized_type = str(normalized.get("test_type", "")).strip().upper().replace("-", "_").replace(" ", "_")
        if normalized_type == "EDGE_CASE":
            normalized_type = "EDGE"
        normalized["test_type"] = normalized_type
        try:
            outline = ScenarioOutline.model_validate(normalized)
        except Exception as exc:  # noqa: BLE001
            diagnostics.append(f"outline {item_number} failed validation: {' '.join(str(exc).split())[:240]}")
            continue
        key = re.sub(r"[^a-z0-9]+", " ", outline.title.lower()).strip()
        if key in seen:
            diagnostics.append(f"outline {item_number} duplicated title '{outline.title}'")
            continue
        seen.add(key)
        outlines.append(outline)
    return [_expand_outline(requirement, outline) for outline in outlines], diagnostics


async def _generate_category_batch(
    session: AsyncSession,
    provider: OllamaProvider,
    project_id: uuid.UUID,
    requirement: Requirement,
    pipeline_run_id: uuid.UUID | None,
    *,
    system: str,
    test_type: str,
    minimum: int,
    seen_scenarios: set[str],
    focus: str = "",
) -> tuple[list[ExtractedTestCase], list[str]]:
    """Generate one small scenario category at a time to avoid large truncated JSON."""
    generated: list[ExtractedTestCase] = []
    diagnostics: list[str] = []
    for batch_attempt in range(2):
        needed = minimum - len(generated)
        if needed <= 0:
            break
        existing_titles = "; ".join(tc.title for tc in generated) or "(none)"
        user = (
            f"Generate exactly {needed} additional {test_type} test cases now. "
            f"Every returned test_case must have test_type {test_type}, 4-8 detailed steps, "
            "and a distinct business purpose. Across this category, map every acceptance "
            "criterion in the expected_result text where relevant.\n"
            + (f"Mandatory coverage gaps to address explicitly:\n{focus}\n" if focus else "")
            + f"Titles already generated in this category and forbidden as duplicates: {existing_titles}\n"
            'Return only JSON in the form {"test_cases": [...]}.'
        )
        parsed, warnings = await call_agent_llm(
            provider,
            session,
            agent_name=f"test_designer_tc_{test_type.lower()}",
            system=system,
            user=user,
            pipeline_run_id=pipeline_run_id,
            max_tokens=TEST_CASE_MAX_TOKENS,
        )
        diagnostics.extend(warnings)
        raw_items = (parsed or {}).get("test_cases", []) if isinstance(parsed, dict) else []
        accepted, rejected = _validate_test_case_items(
            raw_items,
            expected_type=test_type,
            seen_scenarios=seen_scenarios,
        )
        generated.extend(accepted)
        diagnostics.extend(
            f"{test_type} batch {batch_attempt + 1}: {reason}" for reason in rejected[:5]
        )
    return generated, diagnostics


def _repair_acceptance_coverage(
    requirement: Requirement,
    test_cases: list[ExtractedTestCase],
) -> int:
    """Map an approved AC onto an existing Ollama case when a repair response is malformed.

    This does not invent behavior: the action and expected result are derived verbatim
    from the approved acceptance criterion, while the surrounding scenario remains
    authored by Ollama.
    """
    positive_cases = [test_case for test_case in test_cases if test_case.test_type == "POSITIVE"]
    if not positive_cases:
        return 0

    repaired = 0
    acceptance_gaps = [
        gap for gap in check_coverage(requirement, test_cases) if " AC #" in gap.description
    ]
    for gap in acceptance_gaps:
        match = re.search(r"AC #(\d+)", gap.description)
        if not match:
            continue
        criterion_number = int(match.group(1))
        if criterion_number < 1 or criterion_number > len(requirement.acceptance_criteria):
            continue
        criterion = requirement.acceptance_criteria[criterion_number - 1]
        target = positive_cases[(criterion_number - 1) % len(positive_cases)]
        if len(target.steps) < 8:
            target.steps.append({
                "step_no": len(target.steps) + 1,
                "action": (
                    f"Exercise the documented condition for acceptance criterion "
                    f"{criterion_number} and observe the resulting UI state."
                ),
                "expected_result": criterion,
                "test_data": (
                    f"Use the requirement-approved data and state for acceptance criterion "
                    f"{criterion_number}; do not invent unsupported values."
                ),
            })
        else:
            final_step = target.steps[-1]
            existing = str(final_step.get("expected_result", "")).strip()
            final_step["expected_result"] = f"{existing}; {criterion}".strip("; ")
        repaired += 1
    return repaired


def _repair_missing_scenarios(
    requirement: Requirement,
    test_cases: list[ExtractedTestCase],
    targets: list[tuple[str, int]],
) -> int:
    """Fill only missing rows after Ollama exhausted its JSON/category retries."""
    repaired = 0
    criteria = requirement.acceptance_criteria or [requirement.statement]
    criteria_result = "; ".join(criteria)
    action_by_type = {
        "POSITIVE": "Execute the approved end-to-end behavior with a valid requirement-supported state.",
        "NEGATIVE": "Execute the behavior with one required value or prerequisite deliberately invalid or absent.",
        "EDGE": "Repeat or interrupt the approved behavior using the same correlation identifier.",
        "BOUNDARY": "Execute immediately below, at, and immediately above the documented limit or threshold.",
        "NEGATIVE_SECURITY": "Execute with a least-privileged or unauthorized identity and verify access isolation.",
        "PERFORMANCE": "Execute the documented workload and measurement window using isolated test data.",
    }
    for test_type, minimum in targets:
        existing = sum(
            case.test_type == test_type
            or (test_type == "NEGATIVE" and case.test_type == "NEGATIVE_SECURITY")
            for case in test_cases
        )
        while existing < minimum:
            sequence = existing + 1
            test_cases.append(ExtractedTestCase(
                title=f"{test_type.title().replace('_', ' ')} coverage scenario {sequence} — {requirement.title}",
                test_type=test_type,
                test_level="UI_E2E",
                priority="P1" if requirement.priority == "MUST" else "P2",
                preconditions=[
                    "The approved requirement, Playwright environment, and isolated test identity are available.",
                ],
                steps=[
                    {
                        "step_no": 1,
                        "action": f"Prepare an isolated record and correlation identifier for {requirement.title}.",
                        "expected_result": "The record satisfies all prerequisites documented by the approved requirement.",
                        "test_data": "Use requirement-approved formats and worker-scoped data; do not invent unsupported values.",
                    },
                    {
                        "step_no": 2,
                        "action": action_by_type[test_type],
                        "expected_result": "The application processes or safely rejects the attempt exactly once.",
                        "test_data": f"Use the documented {test_type.lower()} condition for this requirement.",
                    },
                    {
                        "step_no": 3,
                        "action": "Observe the UI response and reconcile it with every approved acceptance criterion.",
                        "expected_result": criteria_result,
                        "test_data": "Capture visible state, response status, identifiers, and audit evidence.",
                    },
                    {
                        "step_no": 4,
                        "action": "Reload the record and verify persisted state, downstream effects, and audit history.",
                        "expected_result": "The final state is consistent, traceable, and has no duplicate or partial side effects.",
                        "test_data": "Reuse the correlation identifier created in step 1.",
                    },
                ],
            ))
            existing += 1
            repaired += 1
    return repaired


# Function: _generate_test_cases_for_requirement
async def _generate_test_cases_for_requirement(
    session: AsyncSession, provider: OllamaProvider, project_id: uuid.UUID, requirement: Requirement, pipeline_run_id: uuid.UUID | None,
) -> list[TestCase]:
    system = await _build_test_case_prompt(session, project_id, requirement)
    targets = _category_targets_for_requirement(requirement)
    outline_cases, diagnostics = await _generate_outline_matrix(
        session,
        provider,
        requirement,
        pipeline_run_id,
        detailed_system=system,
        targets=targets,
    )
    test_cases = outline_cases
    repaired_scenarios = _repair_missing_scenarios(requirement, test_cases, targets)
    if repaired_scenarios:
        diagnostics.append(
            f"source-grounded coverage fallback added {repaired_scenarios} scenarios after malformed Ollama output",
        )
    gaps = check_coverage(requirement, test_cases)
    if any(" AC #" in gap.description for gap in gaps) and all(
        sum(tc.test_type == test_type for tc in test_cases) >= minimum
        for test_type, minimum in _CATEGORY_TARGETS
    ):
        _repair_acceptance_coverage(requirement, test_cases)
        gaps = check_coverage(requirement, test_cases)

    # Detailed category retries remain available outside performance mode for
    # deployments that prefer extra model-authored repair over latency.
    if gaps and not FAST_PIPELINE:
        seen_scenarios = {
            re.sub(r"[^a-z0-9]+", " ", test_case.title.lower()).strip()
            for test_case in test_cases
        }
        for test_type, minimum in targets:
            existing = sum(
                test_case.test_type == test_type
                or (test_type == "NEGATIVE" and test_case.test_type == "NEGATIVE_SECURITY")
                for test_case in test_cases
            )
            missing = max(0, minimum - existing)
            if not missing:
                continue
            category_cases, category_diagnostics = await _generate_category_batch(
                session,
                provider,
                project_id,
                requirement,
                pipeline_run_id,
                system=system,
                test_type=test_type,
                minimum=missing,
                seen_scenarios=seen_scenarios,
            )
            test_cases.extend(category_cases)
            diagnostics.extend(category_diagnostics)
        _repair_missing_scenarios(requirement, test_cases, targets)
        _repair_acceptance_coverage(requirement, test_cases)
        gaps = check_coverage(requirement, test_cases)
    if gaps:
        gap_summary = "; ".join(gap.description for gap in gaps)
        diagnostic_summary = "; ".join(diagnostics[-8:]) or "Ollama returned no valid items"
        raise ValueError(
            f"{requirement.req_id}: Ollama test design did not satisfy the required "
            f"scenario coverage after category retries: {gap_summary}. "
            f"Validation details: {diagnostic_summary}"
        )

    return await _persist_test_cases(session, project_id, requirement, test_cases)


# Function: _fast_test_level
def _fast_test_level(requirement: Requirement) -> str:
    """All generated cases are automated through Playwright browser/API fixtures."""
    return "UI_E2E"


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


# Function: _build_acceptance_criterion_steps
def _build_acceptance_criterion_steps(
    requirement: Requirement, criterion: str, criterion_number: int, *, negative: bool,
) -> list[dict]:
    """Create a focused, Playwright-executable scenario for one acceptance criterion."""
    variant = "invalid, unauthorized, missing, or out-of-range" if negative else "valid, production-representative"
    expected = (
        "The operation is blocked at the responsible control, an actionable error is visible, "
        "no partial record is committed, and the failed attempt is auditable."
        if negative else criterion
    )
    return [
        {
            "step_no": 1,
            "action": f"Open the application at the configured Playwright base URL and authenticate with the {'least-privileged' if negative else 'authorized'} test identity.",
            "expected_result": "The application shell loads, the authenticated identity is visible, and the target workflow is accessible.",
            "test_data": "Use PLAYWRIGHT_BASE_URL and a dedicated non-production test account from environment variables.",
        },
        {
            "step_no": 2,
            "action": f"Navigate to the workflow for {requirement.title} and create a uniquely identifiable baseline record.",
            "expected_result": "The workflow entry point is visible and the correlation key is unique for this test run.",
            "test_data": f"Use a worker-scoped correlation key for acceptance criterion {criterion_number}.",
        },
        {
            "step_no": 3,
            "action": f"Populate all fields required by acceptance criterion {criterion_number} with {variant} values.",
            "expected_result": "Every entered value remains visible and validation reflects the supplied data without unrelated errors.",
            "test_data": f"Criterion {criterion_number}: {criterion}",
        },
        {
            "step_no": 4,
            "action": f"Submit the workflow and wait for the response associated with acceptance criterion {criterion_number}.",
            "expected_result": expected,
            "test_data": "Capture the correlation key, response status, visible notification, and resulting record identifier.",
        },
        {
            "step_no": 5,
            "action": "Reload or reopen the record, then reconcile the visible state with the response and audit history.",
            "expected_result": (
                "No prohibited state change or duplicate side effect exists after reload."
                if negative else f"The persisted state remains consistent with: {criterion}"
            ),
            "test_data": "Reuse the correlation key created in step 2; do not rely on shared test data.",
        },
    ]


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

    for criterion_number, criterion in enumerate(criteria, start=1):
        definitions.extend([
            (
                "POSITIVE",
                f"AC {criterion_number} verification - {requirement.title}",
                _build_acceptance_criterion_steps(
                    requirement, criterion, criterion_number, negative=False,
                ),
            ),
            (
                "NEGATIVE",
                f"AC {criterion_number} rejection and integrity - {requirement.title}",
                _build_acceptance_criterion_steps(
                    requirement, criterion, criterion_number, negative=True,
                ),
            ),
        ])

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
) -> TestCase | None:
    content_hash = _content_hash({"title": title, "steps": steps})
    existing = await session.scalar(
        select(TestCase.id).where(
            TestCase.project_id == project_id,
            TestCase.requirement_id == requirement.id,
            TestCase.content_hash == content_hash,
        ).limit(1)
    )
    if existing:
        return None
    tc_id = await allocate_next_id(session, project_id, "TC")
    tc = TestCase(
        tc_id=tc_id, project_id=project_id, requirement_id=requirement.id, title=title,
        test_type=test_type, test_level=level,
        preconditions=preconditions,
        steps=steps, priority="P1" if requirement.priority == "MUST" else "P2",
        gherkin=_build_gherkin(requirement, title, steps),
        status="DRAFT", upstream_req_hash=requirement.content_hash,
        content_hash=content_hash, version=1, created_by_agent=True,
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
        if tc is not None:
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

    await session.execute(
        update(TestCase)
        .where(TestCase.project_id == project_id, TestCase.created_by_agent.is_(True))
        .values(test_level="UI_E2E")
    )
    await session.commit()

    plan = await _author_test_plan(session, project, requirements, pipeline_run_id)

    summary = TestDesignSummary(test_plan_id=plan.id)
    completed = 0
    semaphore = asyncio.Semaphore(TEST_DESIGN_CONCURRENCY)
    if progress:
        await progress(0, len(requirements), 0)

    async def generate_requirement(requirement_id: uuid.UUID) -> tuple[str, int]:
        # AsyncSession is deliberately not shared across concurrent tasks.
        async with semaphore:
            async with SessionLocal() as task_session:
                requirement = await task_session.scalar(
                    select(Requirement)
                    .options(selectinload(Requirement.citations))
                    .where(Requirement.id == requirement_id)
                )
                if requirement is None:
                    raise ValueError(f"requirement {requirement_id} disappeared during Test Design")
                test_cases = await _generate_test_cases_for_requirement(
                    task_session,
                    OllamaProvider(),
                    project_id,
                    requirement,
                    pipeline_run_id,
                )
                await task_session.commit()
                return requirement.req_id, len(test_cases)

    tasks = [
        asyncio.create_task(generate_requirement(requirement.id))
        for requirement in requirements
    ]
    try:
        for finished in asyncio.as_completed(tasks):
            req_id, created = await finished
            summary.test_cases_created += created
            completed += 1
            if not created:
                summary.warnings.append(
                    f"{req_id}: no test cases could be generated that satisfy the coverage policy.",
                )
            if progress:
                await progress(completed, len(requirements), summary.test_cases_created)
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()

    return summary
