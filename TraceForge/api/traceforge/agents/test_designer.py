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
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from traceforge.agents.base import call_agent_llm
from traceforge.agents.coverage_policy import check_coverage, minimum_scenarios_for_requirement
from traceforge.agents.extractor import _acceptance_criterion_is_grounded, _claim_is_grounded
from traceforge.agents.test_plan_docx_generator import generate_test_plan_docx
from traceforge.config import (
    FAST_PIPELINE,
    TEST_CASE_MAX_TOKENS,
    TEST_CASE_OUTLINE_MAX_TOKENS,
    TEST_DESIGN_CONCURRENCY,
    TEST_PLAN_MAX_TOKENS,
    OLLAMA_ANALYSIS_MODEL,
)
from traceforge.db.ids import allocate_next_id
from traceforge.db.models import Chunk, Project, Requirement, TestCase, TestPlan, TestPlanCitation
from traceforge.db.session import SessionLocal
from traceforge.indexing.retriever import hybrid_search, similarity_search
from traceforge.llm.ollama import OllamaProvider

_TC_SYSTEM_PROMPT = """You are a senior enterprise QA architect, SAP/ERP test architect, integration test specialist, and Playwright automation architect.

SOURCE AUTHORITY — follow strictly:
1. Treat the supplied requirement and source context as the ONLY authoritative source.
2. Preserve exact terminology, identifiers, product codes, quantities, statuses, locations, document names, and process sequence from the source.
3. Never silently resolve contradictions — record them as AMBIGUITY entries in the output.
4. Never replace source terminology with general industry assumptions.
5. Never invent: business rules, boundary values, field names, screens, transaction codes, APIs, selectors, roles, statuses, or master data.
6. When information is missing: write "[EXECUTION DETAIL BLOCKED — <state exactly what the business owner must supply>]" as the step action.
7. All generated test cases start with status DRAFT — never Approved.
8. Preserve the semantic type and unit of every source value. Never convert a quantity, credit, balance, duration, or count into money unless the source explicitly supplies a currency unit.
9. Derived reconciliation formulas may use only source-confirmed operands, units, and rules; otherwise record the missing rule as an ambiguity.
10. Every expected_result must closely reuse the requirement statement or an acceptance criterion. Do not infer a downstream status, timing dependency, arithmetic result, persistence effect, or reconciliation state. If the expected outcome is not stated, use "[PENDING BUSINESS CONFIRMATION â€” expected outcome not supplied]".

REQUIREMENT {req_id} [{ears_pattern}] — {level}:
{statement}

ACCEPTANCE CRITERIA:
{acceptance_criteria}

PROJECT CONTEXT:
{project_context}

SOURCE CONTEXT (verbatim field names, codes, and values — use these exactly; never substitute):
{cited_chunks}

INCIDENT EVIDENCE (real failures — design NEGATIVE/EDGE cases that would have caught these):
{related_incident_clusters}

TEST-LEVEL CLASSIFICATION:
Assign based on what the test exercises, not the tool used to run it:
- INTEGRATION: ERP/SAP transactions, MRP/planning, accounting reconciliation, R2R/BC checks, inter-system flows, authorization/role enforcement, master data validation, external warehouse synchronisation
- API: REST/SOAP endpoints, message queues, interface adapters, webhook callbacks, data validation via API layer
- UAT: Complete business journeys covering full end-to-end value chains verified by business-approved test data
- UI_E2E: UI-navigable workflows where stable screen/URL metadata is available from the source
- UNIT: Isolated calculation, validation, or transformation logic

AUTOMATION CLASSIFICATION — be strictly honest:
- AUTOMATION_BLOCKED: No base URL, no auth method, no stable selectors, no test-data API, OR the test touches shared business records without worker isolation
- READY_FOR_API_AUTOMATION: Endpoint, auth, request/response schemas, test-data factory, and cleanup API all supplied
- READY_FOR_UI_AUTOMATION: Base URL, auth storage state, stable selectors via getByTestId/getByRole, test-data factory, and cleanup all supplied
- MANUAL_ONLY: source-required elapsed-time waits without an approved simulation API; physical sampling; regulatory wet-signature; or approvals requiring human presence
- READY_FOR_HYBRID_AUTOMATION: UI drives workflow, API verifies outcome, all metadata supplied

STEP QUALITY — MANDATORY RULES:
Every step MUST specify ALL of the following that apply:
  • Exact source-named system or application
  • Module / screen / transaction / API endpoint / message queue (use exact source names)
  • Exact source-named user role performing the action
  • Exact action on exact UI field, button, or API field (not vague verbs)
  • Exact input data from the source document (product codes, quantities, grade codes, material numbers)
  • Exact expected state: status code, document number format, stock type, accounting posting, integration result, error message

PROHIBITED generic phrasing — these WILL FAIL the quality gate:
× "Execute the valid business flow"
× "Observe the UI response"
× "Prepare an isolated record and correlation identifier"
× "Reconcile persisted state"
× "Perform the required process"
× "Confirm the system behaves correctly"
× "Verify the expected outcome"
× "The application shall"
× "Execute the documented process"
× "The system responds correctly"

CONSISTENCY RULES — enforced before returning:
- POSITIVE case: every step AND final expected result describes the SUCCESS path. No error states in positive expected results.
- NEGATIVE case: every step describes invalid/unauthorized/missing conditions. Expected results describe REJECTION, BLOCKING, or ERROR.
- EDGE case: explicitly names the retry condition, concurrency state, or interruption point. Expected result names the single idempotent outcome.
- BOUNDARY: uses only documented boundary values from the source. Never invent limits.
- NEGATIVE_SECURITY: names the unauthorized identity and the exact expected access denial message or behaviour.

SHARED-STATE SAFETY:
Tests touching balances, stock, inventory, production records, deliveries, shipments, invoices, or other shared business records MUST be automation_status: AUTOMATION_BLOCKED and parallel_safe: false unless a worker-isolated test-data factory is supplied.

Return JSON ONLY — no markdown, no explanations:
{{"test_cases": [{{
  "title": str,
  "objective": str,
  "process_area": str,
  "test_type": "POSITIVE|NEGATIVE|EDGE|BOUNDARY|NEGATIVE_SECURITY|PERFORMANCE",
  "test_level": "UNIT|API|UI_E2E|INTEGRATION|UAT",
  "priority": "P1|P2|P3",
  "risk_rating": "HIGH|MEDIUM|LOW",
  "automation_status": "READY_FOR_UI_AUTOMATION|READY_FOR_API_AUTOMATION|READY_FOR_HYBRID_AUTOMATION|MANUAL_ONLY|AUTOMATION_BLOCKED",
  "automation_blockers": [str],
  "systems_involved": [str],
  "required_roles": [str],
  "preconditions": [str],
  "steps": [{{"step_no": int, "action": str, "expected_result": str, "test_data": str}}],
  "cleanup_instructions": [str],
  "ambiguities": [str],
  "assumptions": [str],
  "parallel_safe": bool,
  "automation_context": object
}}]}}"""

class ExtractedTestCase(BaseModel):
    title: str = Field(min_length=8)
    objective: str = ""
    process_area: str = ""
    test_type: Literal["POSITIVE", "NEGATIVE", "EDGE", "BOUNDARY", "NEGATIVE_SECURITY", "PERFORMANCE"]
    test_level: str = "INTEGRATION"
    priority: str = "P2"
    risk_rating: Literal["HIGH", "MEDIUM", "LOW"] = "MEDIUM"
    automation_status: Literal[
        "READY_FOR_UI_AUTOMATION", "READY_FOR_API_AUTOMATION",
        "READY_FOR_HYBRID_AUTOMATION", "MANUAL_ONLY", "AUTOMATION_BLOCKED",
    ] = "AUTOMATION_BLOCKED"
    automation_blockers: list[str] = Field(default_factory=list)
    systems_involved: list[str] = Field(default_factory=list)
    required_roles: list[str] = Field(default_factory=list)
    preconditions: list[str] = Field(default_factory=list)
    steps: list[dict] = Field(min_length=4, max_length=8)
    cleanup_instructions: list[str] = Field(default_factory=list)
    ambiguities: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    parallel_safe: bool = False
    automation_context: dict = Field(default_factory=dict)
    coverage_dimension: str = ""
    source_quote: str = ""
    acceptance_criteria_mapped: list[int] = Field(default_factory=list)
    generator_schema_version: int = 2


class ScenarioOutline(BaseModel):
    title: str = Field(min_length=8)
    test_type: Literal["POSITIVE", "NEGATIVE", "EDGE", "BOUNDARY", "NEGATIVE_SECURITY", "PERFORMANCE"]
    objective: str = Field(min_length=8)
    test_data: str = Field(min_length=3)
    acceptance_criteria: list[int] = Field(default_factory=list)
    source_quote: str = Field(min_length=3)
    coverage_dimension: Literal[
        "BUSINESS_RULE", "WORKFLOW", "DATA_VARIANT", "NEGATIVE_CONTROL",
        "BOUNDARY", "EDGE_CONDITION", "SECURITY", "PERFORMANCE",
        "INTEGRATION_HANDOFF", "RECONCILIATION", "END_TO_END",
    ] = "BUSINESS_RULE"
    priority: str = "P2"


class TestDesignSummary(BaseModel):
    test_plan_id: uuid.UUID | None = None
    test_cases_created: int = 0
    warnings: list[str] = Field(default_factory=list)
    quality_gate_failures: list[str] = Field(default_factory=list)


# Patterns that indicate a step contains generic placeholder text rather than executable content
_GENERIC_STEP_PATTERNS: list[re.Pattern] = [
    re.compile(p, re.I) for p in [
        r"execute the valid (primary|alternate|business|documented) flow",
        r"observe the (ui|application|system) response",
        r"prepare an isolated record and correlation identifier",
        r"reconcile persisted state",
        r"perform the required process",
        r"confirm the system behaves correctly",
        r"verify the (expected|documented) outcome",
        r"the application shall",
        r"the system (responds|behaves) correctly",
        r"execute the documented process",
        r"complete the business (flow|process|action)",
    ]
]


def _classify_test_level(requirement: "Requirement", test_type: str) -> str:
    """Return the most appropriate DB-supported test level for a requirement + test_type combination."""
    if test_type == "PERFORMANCE":
        return "INTEGRATION"
    if test_type == "NEGATIVE_SECURITY":
        return "INTEGRATION"

    req_text = f"{requirement.title} {requirement.statement}".lower()
    # API / interface tests
    if any(w in req_text for w in ("api ", " api", "endpoint", "webhook", "rest", "soap", "queue", "message bus", "interface", "adapter")):
        return "API"
    # Integration / accounting / ERP-level
    if any(w in req_text for w in (
        "reconcil", "accounting", "posting", "ledger", "r2r", "bc check", "integration",
        "erp", "sap", "mrp", "tips", "warehouse", "wms", "invoice", "billing", "shipment",
        "master data", "configuration", "authorization", "role", "permission", "approval",
    )):
        return "INTEGRATION"
    # Business-level happy path → UAT
    if requirement.level == "BUSINESS" and test_type == "POSITIVE":
        return "UAT"
    # UI_E2E is evidence-driven. A generic functional requirement without an
    # explicit UI surface must not silently become a browser test.
    if any(w in req_text for w in (
        "user interface", "screen", "page", "form", "button", "browser",
        "portal", "accessible name", "selector",
    )):
        return "UI_E2E"
    return "INTEGRATION"


def _validate_step_quality(steps: list[dict]) -> list[str]:
    """Return quality issues: generic actions that are not executable by a real tester."""
    issues: list[str] = []
    for step in steps:
        action = step.get("action", "")
        for pattern in _GENERIC_STEP_PATTERNS:
            if pattern.search(action):
                issues.append(
                    f"Step {step.get('step_no', '?')}: prohibited generic text — \"{action[:100]}\""
                )
                break
    return issues


def _touches_shared_state(test_case: ExtractedTestCase) -> bool:
    text = " ".join(
        [test_case.title, test_case.objective, test_case.process_area]
        + [str(value) for step in test_case.steps for value in step.values()]
    ).lower()
    return any(term in text for term in (
        "balance", "stock", "inventory", "production order", "delivery",
        "shipment", "invoice", "accounting document", "warehouse",
    ))


def _enforce_automation_readiness(test_case: ExtractedTestCase) -> None:
    """Derive readiness from supplied contracts instead of trusting an LLM label."""
    context = test_case.automation_context or {}
    required = {
        "READY_FOR_UI_AUTOMATION": ("base_url", "auth", "locators", "assertions", "test_data_factory", "cleanup"),
        "READY_FOR_API_AUTOMATION": ("base_url", "auth", "endpoints", "schemas", "test_data_factory", "cleanup"),
        "READY_FOR_HYBRID_AUTOMATION": ("base_url", "auth", "locators", "assertions", "endpoints", "schemas", "test_data_factory", "cleanup"),
    }.get(test_case.automation_status)
    if not required:
        return
    missing = [name for name in required if not context.get(name)]
    if not test_case.parallel_safe and _touches_shared_state(test_case):
        missing.append("worker_isolation")
    if missing:
        test_case.automation_status = "AUTOMATION_BLOCKED"
        test_case.automation_blockers.append(
            "Missing concrete automation contract: " + ", ".join(dict.fromkeys(missing))
        )


def _tc_metadata_json(tc: "ExtractedTestCase") -> str:
    """Serialise rich metadata into the gherkin column (unused for actual Gherkin syntax here)."""
    return json.dumps({
        "objective": tc.objective,
        "risk_rating": tc.risk_rating,
        "automation_status": tc.automation_status,
        "automation_blockers": tc.automation_blockers,
        "process_area": tc.process_area,
        "systems_involved": tc.systems_involved,
        "required_roles": tc.required_roles,
        "cleanup_instructions": tc.cleanup_instructions,
        "ambiguities": tc.ambiguities,
        "assumptions": tc.assumptions,
        "parallel_safe": tc.parallel_safe,
        "automation_context": tc.automation_context,
        "coverage_dimension": tc.coverage_dimension,
        "source_quote": tc.source_quote,
        "acceptance_criteria_mapped": tc.acceptance_criteria_mapped,
        "generator_schema_version": tc.generator_schema_version,
    }, ensure_ascii=False)


# Function: _content_hash
def _content_hash(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def _authoritative_evidence(requirement: Requirement) -> str:
    """Return source-backed values without synthesising master data or units."""
    values = [requirement.statement, *(requirement.acceptance_criteria or [])]
    values.extend(citation.quoted_span for citation in getattr(requirement, "citations", []) or [])
    return "; ".join(dict.fromkeys(value.strip() for value in values if value and value.strip()))


# Function: _draft_test_plan_content
async def _draft_test_plan_content(
    session: AsyncSession, project: Project, requirements: list[Requirement], pipeline_run_id: uuid.UUID | None,
) -> dict:
    req_count = len(requirements)
    levels = {r.level for r in requirements}
    level_summary = ", ".join(sorted(levels)) if levels else "FUNCTIONAL"
    allowed_test_levels = sorted({
        _classify_test_level(requirement, test_type)
        for requirement in requirements
        for test_type in minimum_scenarios_for_requirement(requirement)
    })

    provider = OllamaProvider(model=OLLAMA_ANALYSIS_MODEL)
    req_summary = "\n".join(
        f"- {r.req_id} [{r.level}] {r.priority}: {r.statement}\n"
        f"  AC: {' | '.join(r.acceptance_criteria or [])}\n"
        f"  Evidence: {' | '.join(c.quoted_span for c in r.citations)}"
        for r in requirements[:60]
    )
    system = (
        "You are a senior test lead writing an enterprise test plan comparable in structure to mature "
        "test-management products. "
        "Classify tests by appropriate level (INTEGRATION, API, UAT, UI_E2E, UNIT). "
        "Never classify everything as UI_E2E. "
        "Identify risks, ambiguities, and shared-state concerns. "
        "Use only facts present in the supplied requirement evidence. Do not invent environments, "
        "roles, systems, interfaces, thresholds, defect severities, schedules, or approval rules. "
        "For any absent plan detail, emit the literal value 'PENDING BUSINESS CONFIRMATION'. "
        f"The only currently evidenced executable test levels are: {', '.join(allowed_test_levels)}. "
        "Do not claim API, UI, unit, interface, or automation coverage unless that level appears in this list. "
        "Build requirement-based coverage, execution waves, data/configuration strategy, risks, "
        "suspension/resumption controls, deliverables, and approval dependencies. Distinguish business/manual "
        "testability from automation readiness. Never claim that a minimum scenario count is comprehensive. "
        "Return JSON only:\n"
        '{"scope": str, "strategy": str, "environments": [str], "test_levels": [str], '
        '"test_types": [str], "objectives": [str], "in_scope": [str], "out_of_scope": [str], '
        '"process_stages": [str], "coverage_model": [str], "test_data_strategy": [str], '
        '"role_strategy": [str], "environment_strategy": [str], "automation_strategy": [str], '
        '"defect_management": [str], "deliverables": [str], "dependencies": [str], '
        '"assumptions": [str], "schedule": {"phases": [str], "execution_waves": [str]}, '
        '"entry_criteria": [str], "exit_criteria": [str], "suspension_criteria": [str], '
        '"resumption_criteria": [str], "risks": [str]}'
    )
    user = (
        f"Project: {project.name}\nClient: {project.client_name or 'N/A'}\n"
        f"Business process: {(project.config or {}).get('description') or 'N/A'}\n\n"
        f"Approved requirements ({req_count} total):\n{req_summary}"
    )
    parsed, _ = await call_agent_llm(
        provider, session, agent_name="test_designer_plan", system=system, user=user,
        pipeline_run_id=pipeline_run_id, max_tokens=TEST_PLAN_MAX_TOKENS,
    )
    if not isinstance(parsed, dict) or not parsed.get("scope") or not parsed.get("strategy"):
        raise ValueError("Ollama did not return a valid source-grounded test plan; generation failed closed")
    mentioned_levels = {
        level for level in ("UNIT", "API", "UI_E2E", "INTEGRATION", "UAT")
        if re.search(rf"\b{re.escape(level)}\b", str(parsed.get("strategy", "")), re.I)
    }
    unsupported_levels = sorted(mentioned_levels - set(allowed_test_levels))
    if unsupported_levels:
        raise ValueError(
            "Ollama test plan claimed unsupported test levels: " + ", ".join(unsupported_levels)
        )
    environments: list[str] = []
    evidence = _normalise_plan_evidence(requirements)
    for value in parsed.get("environments") or []:
        normalised = " ".join(str(value).split())
        if not normalised:
            continue
        if "PENDING BUSINESS CONFIRMATION" in normalised.upper() or normalised.casefold() in evidence:
            if normalised not in environments:
                environments.append(normalised)
    parsed["environments"] = environments or ["PENDING BUSINESS CONFIRMATION"]
    return parsed


def _normalise_plan_evidence(requirements: list[Requirement]) -> str:
    values: list[str] = []
    for requirement in requirements:
        values.extend([requirement.title, requirement.statement, *(requirement.acceptance_criteria or [])])
        values.extend(citation.quoted_span for citation in requirement.citations)
    return " ".join(" ".join(values).split()).casefold()


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
        scope=parsed["scope"],
        strategy=parsed["strategy"],
        environments=parsed.get("environments") or ["PENDING BUSINESS CONFIRMATION"],
        schedule={
            **(parsed.get("schedule") or {}),
            "objectives": parsed.get("objectives", []),
            "in_scope": parsed.get("in_scope", []),
            "out_of_scope": parsed.get("out_of_scope", []),
            "process_stages": parsed.get("process_stages", []),
            "coverage_model": parsed.get("coverage_model", []),
            "test_levels": parsed.get("test_levels", []),
            "test_types": parsed.get("test_types", []),
            "test_data_strategy": parsed.get("test_data_strategy", []),
            "role_strategy": parsed.get("role_strategy", []),
            "environment_strategy": parsed.get("environment_strategy", []),
            "automation_strategy": parsed.get("automation_strategy", []),
            "defect_management": parsed.get("defect_management", []),
            "deliverables": parsed.get("deliverables", []),
            "risks": parsed.get("risks", []),
            "dependencies": parsed.get("dependencies", []),
            "assumptions": parsed.get("assumptions", []),
        },
        entry_exit_criteria={
            "entry": parsed.get("entry_criteria", []),
            "exit": parsed.get("exit_criteria", []),
            "suspension": parsed.get("suspension_criteria", []),
            "resumption": parsed.get("resumption_criteria", []),
        },
        status="DRAFT", version=1,
    )
    session.add(plan)
    await session.flush()

    # P1 for TestPlan too: cite the requirements it was scoped from.
    top_chunks = await similarity_search(session, project.id, project.name, top_k=3)
    for chunk in (top_chunks or []):
        session.add(TestPlanCitation(test_plan_id=plan.id, chunk_id=chunk.id, relevance=1.0, quoted_span=chunk.text[:300]))
    if not top_chunks:
        await _cite_test_plan_from_requirements(session, plan, requirements)

    await session.commit()
    return plan


# Function: _build_test_case_prompt
async def _build_test_case_prompt(
    session: AsyncSession, project_id: uuid.UUID, requirement: Requirement, project: "Project | None" = None,
) -> str:
    cited_text = "\n---\n".join(c.quoted_span for c in requirement.citations[:5])
    if FAST_PIPELINE:
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

    project_context = "(not supplied)"
    if project:
        project_description = (project.config or {}).get("description")
        project_context = (
            f"Project: {project.name} | Client: {project.client_name or 'N/A'} | "
            f"Description: {project_description or 'N/A'}"
        )

    # Build enhanced system prompt with comprehensive scenario guidance
    enhanced_system_prompt = _build_enhanced_system_prompt(requirement)

    prompt_values = {
        "req_id": requirement.req_id,
        "ears_pattern": requirement.ears_pattern,
        "level": requirement.level,
        "statement": requirement.statement,
        "acceptance_criteria": (
            "\n".join(f"- {ac}" for ac in requirement.acceptance_criteria)
            or "(none documented)"
        ),
        "cited_chunks": (
            cited_text.strip()
            or "(no source context available - do NOT invent field names or values)"
        ),
        "related_incident_clusters": incident_text,
        "project_context": project_context,
    }
    for marker, value in prompt_values.items():
        enhanced_system_prompt = enhanced_system_prompt.replace(f"{{{marker}}}", str(value))
    return enhanced_system_prompt


def _build_enhanced_system_prompt(requirement: Requirement) -> str:
    """Build an enhanced system prompt that guides comprehensive scenario generation.
    
    This prompt extends the base TC system prompt with:
    - Explicit guidance on generating 5-8 scenarios per requirement (not just 2)
    - Business-rule decomposition patterns
    - Process-area identification guidance
    - Priority assignment logic
    - Scenario variant patterns (POSITIVE, NEGATIVE, EDGE, BOUNDARY, SECURITY, INTEGRATION)
    """
    # Build scenario diversity guidance section based on requirement characteristics
    ac_count = len(requirement.acceptance_criteria) if requirement.acceptance_criteria else 1
    diversity_note = (
        f"This requirement has {ac_count} acceptance criteria. Generate at minimum 1 scenario per AC "
        f"(total {ac_count}), plus complementary NEGATIVE, EDGE, BOUNDARY, and SECURITY variants. "
        f"Target 5-8 scenarios total: 3+ POSITIVE (one per AC or business rule), "
        f"2+ NEGATIVE (validation and business rule violations), 1+ EDGE, and conditional BOUNDARY/SECURITY."
    )
    
    # Build process-area guidance
    evidence_text = f"{requirement.title} {requirement.statement} {' '.join(requirement.acceptance_criteria or [])}".lower()
    process_area_hint = _infer_process_area_hint(evidence_text)
    
    enhanced_prompt = f"""You are a senior enterprise QA architect, SAP/ERP test architect, integration test specialist, and Playwright automation architect trained in comprehensive test design comparable to ChatGPT/Codex enterprise test standards.

COMPREHENSIVE SCENARIO GENERATION (NOT MINIMAL COVERAGE):
{diversity_note}

BUSINESS-RULE DECOMPOSITION - CRITICAL INSTRUCTION:
When the requirement or acceptance criteria contain compound conditions (linked by "both", "and", "must", "must also"), decompose EACH condition into its own independent test scenario. Never hide compound conditions under a single scenario title. Generate one POSITIVE and complementary NEGATIVE/EDGE variants for each independently testable condition.

ACCEPTANCE CRITERIA MAPPING:
- Generate one scenario per acceptance criterion (minimum)
- Every scenario must map to one or more AC numbers in "acceptance_criteria" field
- Ensure no AC is left unmapped across the batch

NEGATIVE AND EDGE SCENARIO PATTERNS - Generate These Explicitly:
For every POSITIVE scenario, you MUST also generate:
  1. NEGATIVE_VALIDATION: Invalid/missing required field, wrong data type, out-of-range value
  2. NEGATIVE_BUSINESS_RULE: Violates a stated business rule (insufficient balance, unauthorized role, etc.)
  3. EDGE scenarios: Boundary values, concurrency, retry conditions, interruption points
  4. SECURITY scenarios: Unauthorized identities, role violations, permission denials (when auth keywords present)
  5. INTEGRATION scenarios: Multi-step workflows, inter-system handoffs, reconciliation (when multi-system keywords present)

PROCESS AREA IDENTIFICATION:
This requirement appears to involve: {process_area_hint}
Map the process_area field to the appropriate business domain to enable test organization and coverage reporting.

PRIORITY ASSIGNMENT:
- P1 (Critical): Directly impact business value, customer outcomes, financial accuracy, regulatory compliance, data integrity
- P2 (High): Secondary workflows, error handling, important edge cases
- P3 (Low): Informational, logging, diagnostic scenarios
Default is P2; use P1 only when explicitly justified by requirement criticality.

SOURCE AUTHORITY - follow strictly:
1. Treat requirement and source context as ONLY authoritative source.
2. Preserve exact terminology, identifiers, product codes, quantities, statuses, locations from source.
3. Never silently resolve contradictions - record as AMBIGUITY.
4. Never replace source terminology with industry assumptions.
5. Never invent: business rules, boundary values, field names, screens, APIs, roles, statuses, master data.
6. When missing: write "[EXECUTION DETAIL BLOCKED - <state exactly what business owner must supply>]".
7. All test cases start DRAFT status.
8. Preserve semantic type and unit of every source value.
9. Derived reconciliation formulas may use only source-confirmed operands.
10. Expected_result must closely reuse requirement or AC. If outcome not stated, use "[PENDING BUSINESS CONFIRMATION]".

REQUIREMENT {{req_id}} [{{ears_pattern}}] - {{level}}:
{{statement}}

ACCEPTANCE CRITERIA (generate one or more scenarios per criterion):
{{acceptance_criteria}}

PROJECT CONTEXT:
{{project_context}}

SOURCE CONTEXT (verbatim field names, codes, values - use these exactly):
{{cited_chunks}}

INCIDENT EVIDENCE (real failures - design NEGATIVE/EDGE cases that would have caught these):
{{related_incident_clusters}}

TEST-LEVEL CLASSIFICATION:
- INTEGRATION: ERP/SAP transactions, MRP/planning, accounting reconciliation, R2R/BC, inter-system flows, auth/role enforcement, master data, warehouse sync
- API: REST/SOAP endpoints, message queues, interface adapters, webhook callbacks, data validation via API layer
- UAT: Complete business journeys with business-approved test data
- UI_E2E: UI-navigable workflows where stable screen/URL metadata is available
- UNIT: Isolated calculation, validation, or transformation logic

AUTOMATION CLASSIFICATION - be strictly honest:
- AUTOMATION_BLOCKED: No base URL, no auth method, no stable selectors, no test-data API, OR touches shared business records without worker isolation
- READY_FOR_API_AUTOMATION: Endpoint, auth, schemas, test-data factory, cleanup API all supplied
- READY_FOR_UI_AUTOMATION: Base URL, auth state, stable selectors via getByTestId/getByRole, test-data factory, cleanup all supplied
- MANUAL_ONLY: requires elapsed-time waits without approved simulation; physical sampling; regulatory signatures; human approvals
- READY_FOR_HYBRID_AUTOMATION: UI drives workflow, API verifies outcome, all metadata supplied

STEP QUALITY - MANDATORY RULES:
Every step MUST specify:
  - Exact source-named system or application
  - Module/screen/transaction/API endpoint/message queue (exact source names)
  - Exact source-named user role
  - Exact action on exact UI field/button/API field
  - Exact input data from source (product codes, quantities, material numbers)
  - Exact expected state (status code, document format, stock type, posting, result)

PROHIBITED generic phrasing - WILL FAIL quality gate:
X "Execute the valid business flow"
X "Observe the UI response"
X "Prepare an isolated record and correlation identifier"
X "Reconcile persisted state"
X "Perform the required process"

CONSISTENCY RULES - enforced before returning:
- POSITIVE: every step AND final result describes SUCCESS. No error states in positive expected results.
- NEGATIVE: every step describes invalid/unauthorized/missing conditions. Results describe REJECTION, BLOCKING, ERROR.
- EDGE: explicitly names retry condition, concurrency state, or interruption point. Result names single idempotent outcome.
- BOUNDARY: uses only documented boundary values. Never invent limits.
- NEGATIVE_SECURITY: names unauthorized identity and exact expected access denial message.

SHARED-STATE SAFETY:
Tests touching balances, stock, inventory, production records, deliveries, shipments, invoices MUST be:
  automation_status: AUTOMATION_BLOCKED and parallel_safe: false
Unless a worker-isolated test-data factory is supplied.

Return JSON ONLY - no markdown, no explanations:
{{"test_cases": [{{"title": str, "objective": str, "process_area": str, "test_type": "POSITIVE|NEGATIVE|EDGE|BOUNDARY|NEGATIVE_SECURITY|PERFORMANCE", "test_level": "UNIT|API|UI_E2E|INTEGRATION|UAT", "priority": "P1|P2|P3", "risk_rating": "HIGH|MEDIUM|LOW", "automation_status": "READY_FOR_UI_AUTOMATION|READY_FOR_API_AUTOMATION|READY_FOR_HYBRID_AUTOMATION|MANUAL_ONLY|AUTOMATION_BLOCKED", "automation_blockers": [str], "systems_involved": [str], "required_roles": [str], "preconditions": [str], "steps": [{{"step_no": int, "action": str, "expected_result": str, "test_data": str}}], "cleanup_instructions": [str], "ambiguities": [str], "assumptions": [str], "parallel_safe": bool, "automation_context": object, "acceptance_criteria_mapped": [int]}}]}}"""
    
    return enhanced_prompt


def _infer_process_area_hint(evidence_text: str) -> str:
    """Infer likely process areas from requirement text."""
    areas = []
    
    # Check for each process area keyword
    area_keywords = {
        "Master Data": ["master data", "dimension", "customer", "material", "supplier", "location", "grade", "configuration"],
        "Sales Order": ["order entry", "sales order", "pricing", "validation", "modification", "cancellation"],
        "MRP / TIPS": ["mrp", "tips", "demand planning", "supply planning", "production planning", "raw-material"],
        "Production": ["manufacturing", "production", "shift", "bom", "routing", "twin reel", "single reel"],
        "BIO-Burden Quality": ["bio-burden", "sampling", "testing", "quality release", "certification"],
        "FSC Accounting": ["fsc", "credit", "balance", "reconciliation", "return reversal", "post-dispatch"],
        "Billing": ["billing", "invoice", "line-item", "price", "discount", "posting"],
        "External Warehouse": ["warehouse", "stock receipt", "batch", "availability"],
        "Outbound Logistics": ["outbound", "dispatch", "shipment", "quality-hold"],
        "Customer Return": ["return", "acceptance", "quality assessment", "accounting reversal"],
        "R2R / BC Checks": ["r2r", "bc check", "reconciliation"],
        "Reconciliation": ["reconcil", "inter-system sync", "audit trail", "completeness"],
        "Integration Recovery": ["error handling", "retry", "manual intervention"],
        "Audit and Compliance": ["audit", "compliance", "regulatory"],
    }
    
    for area, keywords in area_keywords.items():
        if any(kw in evidence_text for kw in keywords):
            areas.append(area)
    
    if areas:
        return ", ".join(areas)
    else:
        return "domain-specific process area (identify from business context)"


def _detect_and_assign_process_area(evidence_text: str, test_type: str = "") -> str:
    """Detect and assign process area to test case based on requirement and test type.
    
    Maps requirement content to one of 14 business process areas to enable
    coverage organization and reporting by domain.
    """
    keywords_by_area = {
        "Master Data": ["master data", "dimension", "customer", "material", "supplier", "location", "grade", "configuration", "setup", "reference data"],
        "Sales Order": ["order entry", "sales order", "order creation", "pricing", "validation", "modification", "cancellation", "so", "order"],
        "MRP / TIPS": ["mrp", "tips", "demand planning", "supply planning", "production planning", "raw-material", "requirements"],
        "Production": ["manufacturing", "production", "shift", "bom", "routing", "twin reel", "single reel", "mo", "production order"],
        "BIO-Burden Quality": ["bio-burden", "bioburden", "sampling", "testing", "quality release", "certification", "qc check"],
        "FSC Accounting": ["fsc", "credit", "balance", "reconciliation", "return reversal", "post-dispatch", "fsc account"],
        "Billing": ["billing", "invoice", "line-item", "price", "discount", "posting", "accounting", "receivable"],
        "External Warehouse": ["warehouse", "stock receipt", "batch", "availability", "external wh"],
        "Outbound Logistics": ["outbound", "dispatch", "shipment", "quality-hold", "shipping", "delivery"],
        "Customer Return": ["return", "acceptance", "quality assessment", "accounting reversal", "return reversal"],
        "R2R / BC Checks": ["r2r", "bc check", "book-to-cash", "reconciliation"],
        "Reconciliation": ["reconcil", "inter-system sync", "audit trail", "completeness", "balance validation"],
        "Integration Recovery": ["error handling", "retry", "manual intervention", "error recovery", "reprocessing"],
        "Audit and Compliance": ["audit", "compliance", "regulatory", "audit trail", "sarbanes-oxley"],
    }
    
    evidence_lower = evidence_text.lower()
    
    # Find all matching areas
    matched_areas = []
    for area, keywords in keywords_by_area.items():
        for keyword in keywords:
            if keyword in evidence_lower:
                matched_areas.append(area)
                break  # Found this area, move to next area
    
    # Return the first matched area, or fallback
    if matched_areas:
        return matched_areas[0]
    
    # If no keywords matched, try pattern matching
    if "authorization" in evidence_lower or "role" in evidence_lower or "permission" in evidence_lower:
        return "Audit and Compliance"
    
    return "domain-specific process area"


# Function: _validate_test_case_items
def _validate_test_case_items(
    raw_items: list[dict],
    *,
    requirement: Requirement,
    project_source_evidence: str = "",
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
        for list_field in (
            "automation_blockers", "systems_involved", "required_roles", "preconditions",
            "cleanup_instructions", "ambiguities", "assumptions",
        ):
            value = normalized.get(list_field)
            if value is None or value == "":
                normalized[list_field] = []
            elif isinstance(value, str):
                normalized[list_field] = [value]
        if normalized.get("automation_context") is None:
            normalized["automation_context"] = {}
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
        _sanitise_optional_metadata(requirement, extracted)
        
        # Assign process area if not already set by Ollama
        if not extracted.process_area or not extracted.process_area.strip():
            evidence_text = f"{requirement.title} {requirement.statement} {' '.join(requirement.acceptance_criteria or [])}".lower()
            extracted.process_area = _detect_and_assign_process_area(evidence_text, extracted.test_type)
        
        if expected_type == "NEGATIVE" and extracted.test_type == "NEGATIVE_SECURITY":
            extracted.test_type = "NEGATIVE"
        if expected_type and extracted.test_type != expected_type:
            rejected.append(
                f"item {item_number} returned {extracted.test_type}, expected {expected_type}",
            )
            continue
        semantic_issues = _scenario_semantic_issues(extracted)
        if semantic_issues:
            rejected.append(f"item {item_number} failed scenario semantics: {'; '.join(semantic_issues)}")
            continue
        source_issues = _test_case_source_issues(
            requirement, extracted, project_source_evidence=project_source_evidence,
        )
        has_blocked_action = any(
            "execution detail blocked" in str(step.get("action", "")).casefold()
            for step in extracted.steps
        )
        if (source_issues and not any("unsupported fact token" in issue for issue in source_issues)) or has_blocked_action:
            _normalise_unsupported_execution_details(requirement, extracted)
            source_issues = _test_case_source_issues(
                requirement, extracted, project_source_evidence=project_source_evidence,
            )
        if source_issues:
            rejected.append(f"item {item_number} failed source grounding: {'; '.join(source_issues[:5])}")
            continue
        semantic_issues = _scenario_semantic_issues(extracted)
        if semantic_issues:
            rejected.append(f"item {item_number} failed scenario semantics after grounding: {'; '.join(semantic_issues)}")
            continue
        # Enforce correct test level based on requirement (override LLM classification if needed)
        valid_levels = {"UNIT", "API", "UI_E2E", "INTEGRATION", "UAT"}
        if extracted.test_level not in valid_levels:
            extracted.test_level = "INTEGRATION"
        scenario_key = re.sub(r"[^a-z0-9]+", " ", extracted.title.lower()).strip()
        if scenario_key in seen_scenarios:
            rejected.append(f"item {item_number} duplicated scenario title '{extracted.title}'")
            continue
        # Quality gate: reject cases with generic step text
        step_issues = _validate_step_quality(extracted.steps)
        if step_issues:
            extracted.automation_status = "AUTOMATION_BLOCKED"
            extracted.automation_blockers.extend(step_issues)
        _enforce_automation_readiness(extracted)
        # Positive cases with negative expected results are marked inconsistent
        if extracted.test_type == "POSITIVE":
            final_expected = " ".join(s.get("expected_result", "") for s in extracted.steps).lower()
            if re.search(r"\b(error|fail|reject|block|invalid|denied|exception)\b", final_expected):
                extracted.assumptions.append(
                    "QA REVIEW NEEDED: Positive scenario contains negative-outcome language in expected results. "
                    "Verify scenario data, action, and expected result all describe the same business state."
                )
        seen_scenarios.add(scenario_key)
        test_cases.append(extracted)
    return test_cases, rejected


_TEST_FACT_RE = re.compile(
    r"(?<![\w])(?:\d+(?:[.,]\d+)?(?:\s*[x×]\s*\d+(?:[.,]\d+)?)?|[A-Z]{2,}\d[A-Z0-9-]*|\d{5,})(?![\w])"
)
_IMPLEMENTATION_CLAIM_RE = re.compile(
    r"\b(automatically?|api|endpoint|button|field|screen|notification|alert|dashboard|"
    r"timeout|expiry|expiration|audit entry|error message|status code)\b",
    re.IGNORECASE,
)
_UNSUPPORTED_ASSERTION_TERMS = {
    "alert", "api", "audit", "automatically", "available", "button", "code", "dashboard", "draft",
    "endpoint", "error", "field", "header", "message", "notification", "posting", "saved",
    "screen", "status", "transition",
}
_NEGATIVE_OUTCOME_RE = re.compile(
    r"\b(block(?:ed|s)?|prevent(?:ed|s)?|reject(?:ed|s)?|cannot|does not|must not|"
    r"denied|invalid|failed?|pending|without|imbalance|not generated|not approved)\b",
    re.IGNORECASE,
)
_SUCCESS_INTENT_RE = re.compile(
    r"\b(success(?:ful|fully)?|permitted|allowed|authori[sz]ed|after approval|"
    r"approved result|completed result|generated and approved)\b",
    re.IGNORECASE,
)


def _sanitise_optional_metadata(requirement: Requirement, test_case: ExtractedTestCase) -> None:
    """Remove optional LLM metadata that is not stated in requirement evidence."""
    evidence = _authoritative_evidence(requirement).casefold()

    def supported(values: list[str]) -> list[str]:
        kept: list[str] = []
        for value in values or []:
            normalised = " ".join(str(value).split()).casefold()
            if normalised and (
                normalised in evidence
                or "pending business" in normalised
                or "execution detail blocked" in normalised
            ):
                kept.append(value)
        return kept

    test_case.systems_involved = supported(test_case.systems_involved)
    test_case.required_roles = supported(test_case.required_roles)
    test_case.assumptions = supported(test_case.assumptions)
    test_case.ambiguities = supported(test_case.ambiguities)
    test_case.cleanup_instructions = supported(test_case.cleanup_instructions)
    if test_case.process_area and " ".join(test_case.process_area.split()).casefold() not in evidence:
        test_case.process_area = ""
    test_case.automation_context = {}


def _scenario_semantic_issues(test_case: ExtractedTestCase) -> list[str]:
    """Reject category labels that contradict the scenario intent/outcome."""
    intent = f"{test_case.title} {test_case.objective}"
    expected_results = [str(step.get("expected_result", "")) for step in test_case.steps]
    scenario_context = " ".join([
        intent,
        *expected_results,
        *[str(step.get("action", "")) for step in test_case.steps],
        *[str(step.get("test_data", "")) for step in test_case.steps],
    ])
    if test_case.test_type == "POSITIVE":
        if (
            _SUCCESS_INTENT_RE.search(intent)
            and expected_results
            and all(_NEGATIVE_OUTCOME_RE.search(value) for value in expected_results)
        ):
            return ["POSITIVE scenario has no source-supported success outcome"]
    if test_case.test_type in {"NEGATIVE", "NEGATIVE_SECURITY"}:
        if not _NEGATIVE_OUTCOME_RE.search(scenario_context):
            return ["NEGATIVE scenario does not identify the invalid, missing, or prohibited condition"]
    return []


def _normalise_unsupported_execution_details(
    requirement: Requirement,
    test_case: ExtractedTestCase,
) -> None:
    """Retain the business procedure while separating missing app bindings.

    A missing screen, role, endpoint, or selector is an implementation-binding
    gap.  It must not erase the distinct, source-backed actions authored for the
    scenario, which was the cause of the repeated four-step placeholders.
    """
    criteria = list(requirement.acceptance_criteria or [requirement.statement])
    negative_criteria = [
        criterion for criterion in criteria
        if re.search(r"\b(block|prevent|reject|den(?:y|ied)|invalid|imbalance|not allowed|fail)\b", criterion, re.I)
    ]
    positive_criteria = [criterion for criterion in criteria if criterion not in negative_criteria]
    if test_case.test_type in {"NEGATIVE", "NEGATIVE_SECURITY"} and negative_criteria:
        assertion_pool = negative_criteria
    elif test_case.test_type == "POSITIVE" and positive_criteria:
        assertion_pool = positive_criteria
    else:
        assertion_pool = criteria
    source_quote = test_case.source_quote or assertion_pool[0]
    criteria_text = "; ".join(assertion_pool)
    test_case.preconditions = [
        "[PENDING BUSINESS CONFIRMATION — executable environment, role, and prerequisite state are not supplied]",
    ]
    test_case.steps = [
        {
            "step_no": 1,
            "action": (
                f"Review the source-defined condition for {requirement.req_id}: {source_quote} "
                "[IMPLEMENTATION BINDING PENDING — confirm the execution system, entry point, and user role.]"
            ),
            "expected_result": "[PENDING BUSINESS CONFIRMATION — executable prerequisite outcome is not supplied]",
            "test_data": f"Source condition: {source_quote}",
            "binding_status": "PENDING",
        },
        {
            "step_no": 2,
            "action": (
                f"Prepare only the source-confirmed business data for this scenario: {source_quote} "
                "[IMPLEMENTATION BINDING PENDING — map source values to exact fields or payload attributes.]"
            ),
            "expected_result": "[PENDING BUSINESS CONFIRMATION — field-level validation behavior is not supplied]",
            "test_data": source_quote,
            "binding_status": "PENDING",
        },
        {
            "step_no": 3,
            "action": (
                f"Perform the source-defined business behavior for {requirement.req_id}: {requirement.statement} "
                "[IMPLEMENTATION BINDING PENDING — confirm the exact transaction, action, or interface trigger.]"
            ),
            "expected_result": criteria_text,
            "test_data": f"Scenario evidence: {source_quote}",
            "binding_status": "PENDING",
        },
        {
            "step_no": 4,
            "action": (
                f"Verify the source-stated outcome for {requirement.req_id}: {criteria_text} "
                "[IMPLEMENTATION BINDING PENDING — identify the authoritative result field, document, or system.]"
            ),
            "expected_result": criteria_text,
            "test_data": f"Acceptance evidence: {criteria_text}",
            "binding_status": "PENDING",
        },
    ]
    test_case.automation_status = "AUTOMATION_BLOCKED"
    blocker = "Application entry point, role, fields, actions, and assertion targets are not supplied by the source"
    if blocker not in test_case.automation_blockers:
        test_case.automation_blockers.append(blocker)
    ambiguity = f"{requirement.req_id}: executable application metadata requires business confirmation."
    if ambiguity not in test_case.ambiguities:
        test_case.ambiguities.append(ambiguity)


def _test_case_source_issues(
    requirement: Requirement,
    test_case: ExtractedTestCase,
    *,
    project_source_evidence: str = "",
) -> list[str]:
    """Reject damaging factual additions that cannot be found in cited evidence."""
    requirement_evidence = " ".join(
        f"{getattr(requirement, 'req_id', '')} {_authoritative_evidence(requirement)}".replace("×", "x").split()
    ).casefold()
    project_evidence = " ".join(project_source_evidence.replace("×", "x").split()).casefold()
    evidence = requirement_evidence
    values = [
        test_case.title, test_case.objective, test_case.process_area,
        *test_case.preconditions, *test_case.systems_involved,
        *test_case.required_roles, *test_case.cleanup_instructions,
        *test_case.assumptions, *test_case.ambiguities,
        json.dumps(test_case.automation_context or {}, ensure_ascii=False),
    ]
    for step in test_case.steps:
        values.extend(str(step.get(key, "")) for key in ("action", "expected_result", "test_data"))
    failures: list[str] = []
    for value in values:
        normalised = " ".join((value or "").replace("×", "x").split()).casefold()
        # Text from our own BLOCKED/PENDING sentinels is authoritative — do not re-validate it.
        declared_unknown = (
            "execution detail blocked" in normalised
            or "implementation binding pending" in normalised
            or "pending business confirmation" in normalised
        )
        if not declared_unknown:
            for token in _TEST_FACT_RE.findall(value or ""):
                token_norm = " ".join(token.replace("×", "x").split()).casefold()
                # Skip trivial standalone numbers (0-99) — they are too common to be meaningful facts.
                if re.fullmatch(r"\d{1,2}", token_norm):
                    continue
                if token_norm not in evidence:
                    failures.append(f"unsupported fact token '{token}'")
            for match in _IMPLEMENTATION_CLAIM_RE.finditer(normalised):
                claim = match.group(1).casefold()
                if claim not in evidence:
                    failures.append(f"unsupported implementation claim '{claim}'")
    # Only check expected-result terms for non-blocked steps.
    requirement_words = set(re.findall(r"[a-z][a-z0-9-]+", requirement_evidence))
    for step in test_case.steps:
        expected = " ".join(str(step.get("expected_result", "")).split()).casefold()
        if "pending business confirmation" in expected or "execution detail blocked" in expected:
            continue
        unsupported_terms = sorted(
            term for term in _UNSUPPORTED_ASSERTION_TERMS
            if re.search(rf"\b{re.escape(term)}\b", expected) and term not in requirement_words
        )
        if unsupported_terms:
            failures.append(
                "expected result adds unsupported implementation terms: " + ", ".join(unsupported_terms)
            )
    return list(dict.fromkeys(failures))


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
        # Requirement evidence is authoritative. The LLM's label cannot turn an
        # unspecified interaction into UI_E2E merely because Playwright exists.
        test_level = _classify_test_level(requirement, extracted.test_type)
        if extracted.test_level == "UNIT" and requirement.level != "BUSINESS":
            test_level = "UNIT"
        tc = TestCase(
            tc_id=tc_id, project_id=project_id, requirement_id=requirement.id,
            title=f"{requirement.req_id} — {extracted.title}",
            test_type=extracted.test_type, test_level=test_level, preconditions=extracted.preconditions,
            steps=extracted.steps, priority=extracted.priority if extracted.priority in ("P1", "P2", "P3") else "P2",
            status="DRAFT",  # Never Approved for agent-generated cases
            gherkin=_tc_metadata_json(extracted),
            upstream_req_hash=requirement.content_hash, content_hash=content_hash, version=1, created_by_agent=True,
        )
        session.add(tc)
        test_cases.append(tc)
    return test_cases


_BOUNDARY_TRIGGER_RE = re.compile(
    r"\b(\d+(?:\.\d+)?\s*(?:-|to|and)\s*\d+(?:\.\d+)?|maximum|minimum|limit|range|threshold|timeout)\b",
    re.IGNORECASE,
)
_SECURITY_TRIGGER_RE = re.compile(
    r"\b(auth(?:entication|orization)?|permission|role|tenant|access|credential|sensitive|security)\b",
    re.IGNORECASE,
)
_EDGE_TRIGGER_RE = re.compile(
    r"\b(retry|duplicate|partial|interrupt|concurrent|simultaneous|idempot|recovery|timeout)\b",
    re.IGNORECASE,
)


def _outline_source_issues(requirement: Requirement, outline: ScenarioOutline) -> list[str]:
    authoritative = _authoritative_evidence(requirement).lower()
    proposed = f"{outline.title} {outline.objective} {outline.test_data}".lower()
    issues: list[str] = []
    if " ".join(outline.source_quote.split()).casefold() not in " ".join(authoritative.split()).casefold():
        issues.append("source_quote is not a verbatim span from the requirement evidence")
    if not _claim_is_grounded(outline.objective, authoritative, minimum_ratio=0.60):
        issues.append("scenario objective is not entailed by the requirement evidence")
    if outline.test_type in {"NEGATIVE", "NEGATIVE_SECURITY"} and not _NEGATIVE_OUTCOME_RE.search(outline.source_quote):
        issues.append("negative scenario is not supported by an explicit prohibited or failure condition")
    if outline.test_type == "EDGE" and not _EDGE_TRIGGER_RE.search(outline.source_quote):
        issues.append("edge scenario is not supported by an explicit edge condition")
    if outline.test_type == "NEGATIVE_SECURITY" and not _SECURITY_TRIGGER_RE.search(outline.source_quote):
        issues.append("security scenario is not supported by explicit access-control evidence")
    if outline.test_type == "PERFORMANCE" and requirement.level != "NON_FUNCTIONAL":
        issues.append("performance scenario is not backed by a non-functional requirement")
    if re.search(r"\b(max(?:imum)?|min(?:imum)?|boundary|upper limit|lower limit)\b", proposed) and not _BOUNDARY_TRIGGER_RE.search(authoritative):
        issues.append("scenario reinterprets a documented quantity as an unsupported boundary")
    source_numbers = set(re.findall(r"(?<![\w])\d+(?:\.\d+)?(?![\w])", authoritative))
    proposed_numbers = set(re.findall(r"(?<![\w])\d+(?:\.\d+)?(?![\w])", proposed))
    unsupported_numbers = sorted(proposed_numbers - source_numbers)
    unsupported_numbers = [number for number in unsupported_numbers if not re.fullmatch(r"\d{1,2}", number)]
    if unsupported_numbers:
        issues.append("scenario invents numeric values absent from source: " + ", ".join(unsupported_numbers))
    if re.search(r"[$€£]|\b(?:usd|eur|dollars?|euros?)\b", proposed) and not re.search(r"[$€£]|\b(?:usd|eur|dollars?|euros?)\b", authoritative):
        issues.append("scenario invents a monetary unit absent from source")
    return issues


def _category_targets_for_requirement(requirement: Requirement) -> list[tuple[str, int]]:
    targets = dict(minimum_scenarios_for_requirement(requirement))
    requirement_text = (
        f"{requirement.title} {requirement.statement} {' '.join(requirement.acceptance_criteria or [])}"
    )
    if _BOUNDARY_TRIGGER_RE.search(requirement_text):
        targets["BOUNDARY"] = max(targets.get("BOUNDARY", 0), 1)
    if _SECURITY_TRIGGER_RE.search(requirement_text):
        targets["NEGATIVE_SECURITY"] = max(targets.get("NEGATIVE_SECURITY", 0), 1)
    if _EDGE_TRIGGER_RE.search(requirement_text):
        targets["EDGE"] = max(targets.get("EDGE", 0), 1)
    if requirement.level == "NON_FUNCTIONAL":
        targets["PERFORMANCE"] = max(targets.get("PERFORMANCE", 0), 1)
    return list(targets.items())


def _expand_outline(requirement: Requirement, outline: ScenarioOutline) -> ExtractedTestCase:
    """Expand an Ollama-authored coverage dimension without inventing app metadata."""
    selected_criteria = [
        requirement.acceptance_criteria[index - 1]
        for index in outline.acceptance_criteria
        if 1 <= index <= len(requirement.acceptance_criteria)
    ] or requirement.acceptance_criteria or [requirement.statement]
    criteria_text = "; ".join(selected_criteria)
    test_level = _classify_test_level(requirement, outline.test_type)
    process_evidence = (
        f"{requirement.title} {requirement.statement} "
        f"{' '.join(requirement.acceptance_criteria or [])}"
    )
    test_case = ExtractedTestCase(
        title=outline.title,
        objective=outline.objective,
        process_area=_detect_and_assign_process_area(process_evidence, outline.test_type),
        test_type=outline.test_type,
        test_level=test_level,
        priority=outline.priority if outline.priority in ("P1", "P2", "P3") else "P2",
        risk_rating="HIGH" if requirement.priority == "MUST" else "MEDIUM",
        automation_status="AUTOMATION_BLOCKED",
        automation_blockers=[
            "Application screen, transaction code, URL, and stable selectors not supplied",
            "Test-data factory and cleanup API not supplied",
            "Shared business state requires worker isolation before automation",
        ],
        systems_involved=[],
        required_roles=[],
        preconditions=[],
        steps=[
            {"step_no": number, "action": outline.source_quote,
             "expected_result": criteria_text, "test_data": outline.test_data}
            for number in range(1, 5)
        ],
        cleanup_instructions=[
            "[PENDING BUSINESS REVIEW — cleanup/reversal process not confirmed for this scenario]"
        ],
        ambiguities=[
            f"[PENDING BUSINESS CONFIRMATION — {requirement.req_id} application entry point, "
            "screen/transaction, and field metadata are not supplied.]"
        ],
        assumptions=[
            "DRAFT status: test case requires business owner review and confirmation of test data before execution."
        ],
        parallel_safe=False,
        coverage_dimension=outline.coverage_dimension,
        source_quote=outline.source_quote,
        acceptance_criteria_mapped=outline.acceptance_criteria,
    )
    _normalise_unsupported_execution_details(requirement, test_case)
    return test_case


async def _generate_outline_matrix(
    session: AsyncSession,
    provider: OllamaProvider,
    requirement: Requirement,
    pipeline_run_id: uuid.UUID | None,
    *,
    detailed_system: str,
    targets: list[tuple[str, int]],
) -> tuple[list[ExtractedTestCase], list[str]]:
    """Ask Ollama for an exhaustive evidence matrix, then expand it safely."""
    target_text = ", ".join(f"at least {minimum} {test_type}" for test_type, minimum in targets)
    system = (
        "You are an evidence-first test analyst. Decompose only the supplied requirement into a compact, "
        "exhaustive coverage matrix. Do not design execution steps and do not use general industry knowledge.\n\n"
        f"REQUIREMENT {requirement.req_id}:\n{requirement.statement}\n\n"
        "ACCEPTANCE CRITERIA:\n"
        + "\n".join(f"{index}. {criterion}" for index, criterion in enumerate(requirement.acceptance_criteria, 1))
        + "\n\nVERBATIM SOURCE EVIDENCE:\n"
        + "\n---\n".join(citation.quoted_span for citation in requirement.citations)
        + "\n\nRules:\n"
        "- Return compact coverage dimensions only; the orchestrator expands them into reviewed steps.\n"
        "- The minimum category floor is not the desired total. Add one distinct scenario for EVERY independent "
        "source-stated business rule, workflow outcome, data/configuration variant, negative control, handoff, "
        "reconciliation, boundary, edge condition, security rule, and measurable NFR.\n"
        "- Add a combined END_TO_END scenario when the evidence explicitly links multiple conditions in one journey.\n"
        "- When one sentence links conditions with 'both', 'and', or separate lifecycle checkpoints, create one "
        "scenario for each independently observable condition plus one combined scenario only when the combined "
        "relationship is itself required.\n"
        "  Domain-neutral example: 'A record requires approval and checksum validation' produces three rows: "
        "approval, checksum validation, and the explicitly linked combined condition. Never return only the combined row.\n"
        "- Do not create a negative, boundary, edge, security, or performance scenario unless its condition is explicit.\n"
        "- source_quote must be one exact verbatim span from the supplied requirement, acceptance criteria, or "
        "source evidence that proves the scenario.\n"
        "- Independent rows from the same compound sentence may and should reuse that entire sentence as source_quote; "
        "never leave source_quote empty.\n"
        "- Cover every acceptance criterion across the outlines using its 1-based number; do not hide multiple "
        "independent conditions in one broad scenario.\n"
        "- Keep every title, objective, and test_data value under 24 words.\n"
        "- Do not repeat titles or objectives.\n"
        "- Return JSON only with this schema:\n"
        '{"scenarios":[{"title":str,"test_type":"POSITIVE|NEGATIVE|EDGE|BOUNDARY|'
        'NEGATIVE_SECURITY|PERFORMANCE","objective":str,"test_data":str,'
        '"acceptance_criteria":[int],"source_quote":str,'
        '"coverage_dimension":"BUSINESS_RULE|WORKFLOW|DATA_VARIANT|NEGATIVE_CONTROL|BOUNDARY|'
        'EDGE_CONDITION|SECURITY|PERFORMANCE|INTEGRATION_HANDOFF|RECONCILIATION|END_TO_END",'
        '"priority":"P1|P2|P3"}]}'
    )
    parsed, warnings = await call_agent_llm(
        provider,
        session,
        agent_name="test_designer_outline_matrix",
        system=system,
        user=(
            f"Generate the complete scenario matrix. Required minimum floors: {target_text}. "
            "Continue beyond those floors until every independently testable source condition is represented."
        ),
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
        if not str(normalized.get("source_quote") or "").strip():
            mapped = normalized.get("acceptance_criteria") or []
            mapped_criteria = [
                requirement.acceptance_criteria[number - 1]
                for number in mapped if isinstance(number, int) and 1 <= number <= len(requirement.acceptance_criteria)
            ]
            normalized["source_quote"] = mapped_criteria[0] if mapped_criteria else requirement.statement
        if not isinstance(normalized.get("test_data"), str):
            normalized["test_data"] = json.dumps(
                normalized.get("test_data"), ensure_ascii=False, sort_keys=True,
            )
        normalized_type = str(normalized.get("test_type", "")).strip().upper().replace("-", "_").replace(" ", "_")
        if normalized_type == "EDGE_CASE":
            normalized_type = "EDGE"
        normalized["test_type"] = normalized_type
        try:
            outline = ScenarioOutline.model_validate(normalized)
        except Exception as exc:  # noqa: BLE001
            diagnostics.append(f"outline {item_number} failed validation: {' '.join(str(exc).split())[:240]}")
            continue
        source_issues = _outline_source_issues(requirement, outline)
        if source_issues:
            diagnostics.append(f"outline {item_number} rejected: {'; '.join(source_issues)}")
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
    project_source_evidence: str,
    focus: str = "",
) -> tuple[list[ExtractedTestCase], list[str]]:
    """Generate one small scenario category at a time to avoid large truncated JSON."""
    generated: list[ExtractedTestCase] = []
    diagnostics: list[str] = []
    rejection_feedback = ""
    for batch_attempt in range(2):
        needed = minimum - len(generated)
        if needed <= 0:
            break
        existing_titles = "; ".join(tc.title for tc in generated) or "(none)"
        user = (
            f"Generate exactly {needed} additional {test_type} test cases now. "
            f"Every returned test_case must have test_type {test_type}, 4-8 detailed steps, "
            "and a distinct business purpose. Set acceptance_criteria_mapped to the exact 1-based "
            "criterion numbers covered by each case. Across this category, map every acceptance "
            "criterion in the expected_result text where relevant.\n"
            f"Return exactly {needed} item(s), never more. Copy expected outcomes closely from the supplied "
            "requirement or acceptance criteria; use PENDING BUSINESS CONFIRMATION when an outcome is absent.\n"
            "Keep JSON compact. Omit optional metadata keys when unknown instead of filling them with prose. "
            "The only required keys are title, test_type, and four steps with step_no, action, expected_result, and test_data.\n"
            + (f"Mandatory coverage gaps to address explicitly:\n{focus}\n" if focus else "")
            + (f"The previous attempt was rejected for these reasons; correct every one and do not repeat them:\n"
               f"{rejection_feedback}\n" if rejection_feedback else "")
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
            max_tokens=min(TEST_CASE_MAX_TOKENS, 1800 * needed),
        )
        diagnostics.extend(warnings)
        raw_items = (parsed or {}).get("test_cases", []) if isinstance(parsed, dict) else []
        if len(raw_items) > needed:
            diagnostics.append(
                f"{test_type} batch {batch_attempt + 1}: Ollama returned {len(raw_items)} items; "
                f"only the first {needed} grounded items will be retained",
            )
        candidate_seen = set(seen_scenarios)
        accepted, rejected = _validate_test_case_items(
            raw_items,
            requirement=requirement,
            project_source_evidence=project_source_evidence,
            expected_type=test_type,
            seen_scenarios=candidate_seen,
        )
        accepted = accepted[:needed]
        generated.extend(accepted)
        for test_case in accepted:
            seen_scenarios.add(re.sub(r"[^a-z0-9]+", " ", test_case.title.lower()).strip())
        diagnostics.extend(
            f"{test_type} batch {batch_attempt + 1}: {reason}" for reason in rejected[:5]
        )
        rejection_feedback = "\n".join(rejected[:5])
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
        target.acceptance_criteria_mapped = [criterion_number]
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
    source_evidence = _authoritative_evidence(requirement)
    expected_by_type = {
        "POSITIVE": criteria_result,
        "NEGATIVE": "[PENDING BUSINESS CONFIRMATION — exact rejection message/status and complete no-side-effect assertions are not supplied]",
        "NEGATIVE_SECURITY": "[PENDING BUSINESS CONFIRMATION — exact access denial, audit event, and no-side-effect assertions are not supplied]",
        "EDGE": "[PENDING BUSINESS CONFIRMATION — exact retry/interruption outcome and idempotency assertions are not supplied]",
        "BOUNDARY": criteria_result,
        "PERFORMANCE": "[PENDING BUSINESS CONFIRMATION — workload, measurement window, threshold, and recovery criteria are not supplied]",
    }
    for test_type, minimum in targets:
        existing = sum(
            case.test_type == test_type
            or (test_type == "NEGATIVE" and case.test_type == "NEGATIVE_SECURITY")
            for case in test_cases
        )
        while existing < minimum:
            sequence = existing + 1
            criterion_label = (criteria[(sequence - 1) % len(criteria)] if criteria else requirement.statement)[:80]
            test_cases.append(ExtractedTestCase(
                title=f"{requirement.title} — {test_type.lower().replace('_', ' ')}: {criterion_label}",
                test_type=test_type,
                test_level=_classify_test_level(requirement, test_type),
                priority="P1" if requirement.priority == "MUST" else "P2",
                automation_status="AUTOMATION_BLOCKED",
                automation_blockers=["Source-grounded coverage fallback — application metadata not supplied"],
                parallel_safe=False,
                preconditions=[
                    f"Requirement {requirement.req_id} is APPROVED and test environment is available.",
                ],
                steps=[
                    {
                        "step_no": 1,
                        "action": (
                            f"[EXECUTION DETAIL BLOCKED — application screen, transaction, and field metadata not supplied. "
                            f"Business owner must provide the entry point and user role for: {requirement.title}]"
                        ),
                        "expected_result": "The entry point for the requirement is accessible to the authorised user.",
                        "test_data": "Use requirement-approved data formats; do not invent values.",
                    },
                    {
                        "step_no": 2,
                        "action": (
                            f"[EXECUTION DETAIL BLOCKED — exact {test_type.lower()} action, input, and expected status "
                            "are not supplied. Business owner must map the cited evidence to executable fields.]"
                        ),
                        "expected_result": expected_by_type[test_type],
                        "test_data": source_evidence,
                    },
                    {
                        "step_no": 3,
                        "action": (
                            "[EXECUTION DETAIL BLOCKED — result fields, document identifiers, and verification "
                            "system are not supplied. Business owner must provide each assertion target.]"
                        ),
                        "expected_result": expected_by_type[test_type],
                        "test_data": source_evidence,
                    },
                    {
                        "step_no": 4,
                        "action": (
                            "[EXECUTION DETAIL BLOCKED — persistence, downstream reconciliation, reload method, "
                            "and audit location are not supplied. Business owner must provide them.]"
                        ),
                        "expected_result": expected_by_type[test_type],
                        "test_data": source_evidence,
                    },
                ],
            ))
            existing += 1
            repaired += 1
    return repaired


# Function: _generate_test_cases_for_requirement
async def _generate_test_cases_for_requirement(
    session: AsyncSession,
    provider: OllamaProvider,
    project_id: uuid.UUID,
    requirement: Requirement,
    pipeline_run_id: uuid.UUID | None,
    project: "Project | None" = None,
) -> list[TestCase]:
    system = await _build_test_case_prompt(session, project_id, requirement, project=project)
    # Include all cited-chunk text so tokens the LLM saw are guaranteed in evidence.
    cited_evidence = " ".join(c.quoted_span for c in (requirement.citations or []))
    chunk_evidence = "\n".join((await session.scalars(
        select(Chunk.text).where(Chunk.project_id == project_id).order_by(Chunk.ordinal).limit(120)
    )).all())
    project_source_evidence = f"{chunk_evidence}\n{cited_evidence}"
    targets = _category_targets_for_requirement(requirement)
    # Ollama decomposes the evidence into independently testable dimensions.
    # The orchestrator expands those dimensions into steps while keeping missing
    # application bindings separate from the source-backed business actions.
    test_cases, diagnostics = await _generate_outline_matrix(
        session,
        provider,
        requirement,
        pipeline_run_id,
        detailed_system=system,
        targets=targets,
    )
    valid_cases: list[ExtractedTestCase] = []
    seen_scenarios: set[str] = set()
    for index, test_case in enumerate(test_cases, start=1):
        key = re.sub(r"[^a-z0-9]+", " ", test_case.title.lower()).strip()
        if key in seen_scenarios:
            diagnostics.append(f"expanded scenario {index} duplicated title '{test_case.title}'")
            continue
        source_issues = _test_case_source_issues(
            requirement, test_case, project_source_evidence=project_source_evidence,
        )
        if source_issues:
            diagnostics.append(
                f"expanded scenario {index} failed grounding: {'; '.join(source_issues[:5])}"
            )
            continue
        seen_scenarios.add(key)
        _enforce_automation_readiness(test_case)
        valid_cases.append(test_case)
    test_cases = valid_cases
    gaps = check_coverage(requirement, test_cases)

    # Retry only missing category floors, preserving valid outline scenarios.
    for test_type, minimum in targets:
        existing = sum(
            test_case.test_type == test_type
            or (test_type == "NEGATIVE" and test_case.test_type == "NEGATIVE_SECURITY")
            for test_case in test_cases
        )
        deficit = minimum - existing
        if deficit <= 0:
            continue
        generated, retry_diagnostics = await _generate_category_batch(
            session,
            provider,
            project_id,
            requirement,
            pipeline_run_id,
            system=system,
            test_type=test_type,
            minimum=deficit,
            seen_scenarios=seen_scenarios,
            project_source_evidence=project_source_evidence,
            focus=f"Supply the missing {test_type} coverage floor without duplicating an existing scenario.",
        )
        test_cases.extend(generated)
        diagnostics.extend(retry_diagnostics)

    # A dedicated AC retry is separate from category floors: one case may not
    # hide several independently observable criteria behind a broad title.
    gaps = check_coverage(requirement, test_cases)
    for gap in [gap for gap in gaps if " AC #" in gap.description]:
        match = re.search(r"AC #(\d+)", gap.description)
        if not match:
            continue
        criterion_number = int(match.group(1))
        criterion = requirement.acceptance_criteria[criterion_number - 1]
        test_type = "NEGATIVE" if _NEGATIVE_OUTCOME_RE.search(criterion) else "POSITIVE"
        generated, retry_diagnostics = await _generate_category_batch(
            session,
            provider,
            project_id,
            requirement,
            pipeline_run_id,
            system=system,
            test_type=test_type,
            minimum=1,
            seen_scenarios=seen_scenarios,
            project_source_evidence=project_source_evidence,
            focus=(
                f"Create one dedicated scenario for AC #{criterion_number}: {criterion}. "
                f"Set acceptance_criteria_mapped to exactly [{criterion_number}]."
            ),
        )
        test_cases.extend(generated)
        diagnostics.extend(retry_diagnostics)

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
    blocker_prefix = (
        f"[EXECUTION DETAIL BLOCKED — application system, screen/transaction/URL, user role, "
        f"and field names not supplied. Business owner must provide these for: "
    )
    positive_steps = [
        {
            "step_no": 1,
            "action": (
                f"{blocker_prefix}{requirement.title} — step 1: entry point, user role, "
                f"prerequisite state, and upstream dependencies]"
            ),
            "expected_result": f"The entry point for '{requirement.title}' is accessible to the authorised user and all prerequisites are satisfied.",
            "test_data": "Use requirement-approved data formats and values. Do NOT invent field values not present in the source document.",
        },
        {
            "step_no": 2,
            "action": (
                f"{blocker_prefix}{requirement.title} — step 2: exact trigger action, "
                f"field names, and input values for: {trigger or requirement.statement[:120]}]"
            ),
            "expected_result": "The workflow starts once, retains the submitted data, and enters the expected initial business state without errors.",
            "test_data": "Use the same correlation identifier from step 1. Confirm input format with business owner.",
        },
    ]
    for index, criterion in enumerate(criteria, start=1):
        positive_steps.append({
            "step_no": len(positive_steps) + 1,
            "action": (
                f"{blocker_prefix}{requirement.title} — step {len(positive_steps) + 1}: "
                f"verification action for acceptance criterion {index}: {criterion[:100]}]"
            ),
            "expected_result": criterion,
            "test_data": f"Retain the same correlation identifier. Verify acceptance criterion {index} verbatim from the requirement.",
        })
    positive_steps.append({
        "step_no": len(positive_steps) + 1,
        "action": (
            f"{blocker_prefix}{requirement.title} — final step: downstream verification screen/API, "
            f"document number format, stock type, accounting document, or audit trail location]"
        ),
        "expected_result": "The final persisted state, downstream records, and audit trail are consistent with all preceding checkpoints and business outcomes.",
        "test_data": "Use the document/record identifier created during execution. Reconcile against all acceptance criteria.",
    })
    return positive_steps


# Function: _build_negative_steps
def _build_negative_steps(requirement: Requirement, criteria: list[str]) -> list[dict]:
    return [
        {"step_no": 1, "action": "Create a valid baseline record, then remove or invalidate one mandatory value, state, permission, dependency, or business rule input.",
         "expected_result": "The invalid condition is isolated while the baseline record remains unchanged.",
         "test_data": f"Violate the first applicable rule: {criteria[0]}"},
        {"step_no": 2, "action": f"Attempt the complete business behavior with the invalid condition: {requirement.statement}",
         "expected_result": "Processing is rejected or safely stopped at the responsible checkpoint with actionable feedback and no partial commit.",
         "test_data": "Use the invalid variant from step 1 and keep the same business key."},
        {"step_no": 3, "action": "Correct the invalid value and resubmit the same business transaction through the same workflow entry point.",
         "expected_result": "The corrected transaction succeeds without duplicate records or residual partial state from the failed attempt.",
         "test_data": "Reuse the same business key and restore a documented valid value."},
        {"step_no": 4, "action": "Review persisted data, downstream messages, notifications, validation errors, and audit events for both attempts.",
         "expected_result": "The failed attempt has no unintended side effects; rejection and successful recovery are both traceable.",
         "test_data": "Correlate events using the transaction identifier and the rejected input value."},
        {"step_no": 5,
         "action": (
             f"[EXECUTION DETAIL BLOCKED — audit trail, history screen, or downstream reconciliation "
             f"screen/API not supplied for: {requirement.title}. Business owner must confirm where "
             f"rejected attempts are auditable and what persisted state confirms no side-effects.]"
         ),
         "expected_result": "Only the corrected attempt appears in persisted data; the rejected attempt is auditable with no residual state change.",
         "test_data": "Correlate using the transaction identifier from both attempts."},
    ]


# Function: _build_edge_steps
def _build_edge_steps(requirement: Requirement, criteria: list[str], trigger: str) -> list[dict]:
    blocker_prefix = (
        f"[EXECUTION DETAIL BLOCKED — application system, screen/transaction, and user role not supplied. "
        f"Business owner must provide for: "
    )
    edge_steps = [
        {
            "step_no": 1,
            "action": (
                f"{blocker_prefix}{requirement.title} — step 1: entry point, minimum valid data, "
                f"retry/interrupt mechanism, and all upstream/downstream checkpoints]"
            ),
            "expected_result": "All dependencies are reachable, the minimum supported record is ready, and the retry/interrupt mechanism is identified.",
            "test_data": "Use minimum-length optional data while retaining every mandatory value. Do NOT invent boundary values.",
        },
        {
            "step_no": 2,
            "action": (
                f"{blocker_prefix}{requirement.title} — step 2: exact retry, interrupt, or concurrent "
                f"execution mechanism for: {(trigger or requirement.statement)[:120]}]"
            ),
            "expected_result": "The system handles retry, duplicate submission, interruption, or recovery without corrupting state or executing the transaction twice.",
            "test_data": "Submit the same correlation/business key twice or resume after a controlled interruption. Confirm idempotency with business owner.",
        },
    ]
    for index, criterion in enumerate(criteria, start=1):
        edge_steps.append({
            "step_no": len(edge_steps) + 1,
            "action": (
                f"{blocker_prefix}{requirement.title} — step {len(edge_steps) + 1}: "
                f"verification of alternate-path checkpoint {index}: {criterion[:100]}]"
            ),
            "expected_result": criterion,
            "test_data": f"Retain the same correlation identifier through acceptance criterion {index} and compare recovered state with the baseline.",
        })
    edge_steps.append({
        "step_no": len(edge_steps) + 1,
        "action": (
            f"{blocker_prefix}{requirement.title} — final step: reconciliation screen/API after retry/interruption; "
            f"document/record identifier and comparison point not supplied]"
        ),
        "expected_result": "Exactly one consistent business outcome exists and all recovery activity is auditable.",
        "test_data": "Compare identifiers, state history, downstream events, notification counts, and record versions.",
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
        "no partial record is committed, the rejected state is preserved, and the failed attempt is auditable."
        if negative else criterion
    )
    return [
        {
            "step_no": 1,
            "action": f"Open the application at the configured Playwright base URL and authenticate with the {'least-privileged' if negative else 'authorized'} test identity for the business flow under test.",
            "expected_result": "The application shell loads, the authenticated identity is visible, and the target workflow is accessible.",
            "test_data": "Use PLAYWRIGHT_BASE_URL and a dedicated non-production test account from environment variables.",
        },
        {
            "step_no": 2,
            "action": f"Navigate to the workflow for {requirement.title} and create a uniquely identifiable baseline business record.",
            "expected_result": "The workflow entry point is visible and the correlation key is unique for this test run.",
            "test_data": f"Use a worker-scoped correlation key for acceptance criterion {criterion_number}.",
        },
        {
            "step_no": 3,
            "action": f"Populate all fields required by acceptance criterion {criterion_number} with {variant} values and verify the form or API payload matches the documented business data.",
            "expected_result": "Every entered value remains visible and validation reflects the supplied data without unrelated errors.",
            "test_data": f"Criterion {criterion_number}: {criterion}",
        },
        {
            "step_no": 4,
            "action": f"Submit the workflow and wait for the response associated with acceptance criterion {criterion_number}, including the visible status or message that confirms the business rule result.",
            "expected_result": expected,
            "test_data": "Capture the correlation key, response status, visible notification, and resulting record identifier or rejection code.",
        },
        {
            "step_no": 5,
            "action": "Reload or reopen the record, then reconcile the visible state with the response, downstream effects, and audit history.",
            "expected_result": (
                "No prohibited state change, missing verification, or duplicate side effect exists after reload."
                if negative else f"The persisted state remains consistent with: {criterion}"
            ),
            "test_data": "Reuse the correlation key created in step 2; do not rely on shared test data.",
        },
    ]


# Function: _boundary_definition
def _boundary_definition(requirement: Requirement, criteria: list[str]) -> tuple[str, str, list[dict]]:
    return ("BOUNDARY", f"Boundary values — {requirement.title}", [
        {"step_no": 1, "action": "Identify each documented numeric, length, date, volume, or timeout boundary and record the exact units and business meaning.", "expected_result": "The exact lower and upper limits and units are recorded before execution.", "test_data": requirement.statement},
        {"step_no": 2, "action": "Execute with a value immediately below the lower boundary and observe the validation response.", "expected_result": "The value is rejected with no partial processing.", "test_data": "lower-boundary minus one valid unit"},
        {"step_no": 3, "action": "Execute at the lower and upper boundaries and confirm the documented business outcome at both edges.", "expected_result": "; ".join(criteria), "test_data": "exact lower boundary; exact upper boundary"},
        {"step_no": 4, "action": "Execute immediately above the upper boundary and reconcile persisted state, messages, and audit history.", "expected_result": "The value is rejected and prior valid boundary transactions remain unchanged.", "test_data": "upper-boundary plus one valid unit"},
    ])


# Function: _security_definition
def _security_definition(requirement: Requirement, criteria: list[str]) -> tuple[str, str, list[dict]]:
    return ("NEGATIVE_SECURITY", f"Authorization enforcement — {requirement.title}", [
        {"step_no": 1, "action": "Prepare authorized, unauthorized, expired-session, and cross-tenant identities and document the expected access scope for each.", "expected_result": "Each identity has a verified and distinct access scope.", "test_data": "Approved role matrix and isolated tenant records."},
        {"step_no": 2, "action": f"Execute the protected workflow as the authorized identity: {requirement.statement}", "expected_result": "; ".join(criteria), "test_data": "Authorized identity and valid record."},
        {"step_no": 3, "action": "Repeat with an unauthorized role and an expired or tampered session.", "expected_result": "Access is denied without revealing protected data or changing persisted state.", "test_data": "Unauthorized role; expired token; invalid signature."},
        {"step_no": 4, "action": "Attempt a cross-tenant read or update and confirm the tenant boundary is enforced.", "expected_result": "The other tenant's data remains inaccessible and unchanged.", "test_data": "Cross-tenant target record identifier."},
        {"step_no": 5, "action": "Review security and audit events for all attempts.", "expected_result": "Allowed and denied actions are attributable, timestamped, and contain no secret values.", "test_data": "Correlation IDs from each attempt."},
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
    if _BOUNDARY_TRIGGER_RE.search(requirement_text):
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
    # Build metadata for the gherkin column
    metadata = ExtractedTestCase(
        title=title,
        objective=f"{test_type} coverage of: {requirement.title}",
        process_area=requirement.level,
        test_type=test_type,
        test_level=level,
        priority="P1" if requirement.priority == "MUST" else "P2",
        risk_rating="HIGH" if requirement.priority == "MUST" else "MEDIUM",
        automation_status="AUTOMATION_BLOCKED",
        automation_blockers=[
            "Application screen, transaction code, URL, and stable selectors not yet supplied",
            "Test-data factory and cleanup process not confirmed",
        ],
        preconditions=preconditions,
        steps=steps,
        assumptions=["DRAFT: requires business owner review before execution"],
        parallel_safe=False,
    )
    tc = TestCase(
        tc_id=tc_id, project_id=project_id, requirement_id=requirement.id, title=title,
        test_type=test_type, test_level=level,
        preconditions=preconditions,
        steps=steps, priority="P1" if requirement.priority == "MUST" else "P2",
        gherkin=_tc_metadata_json(metadata),
        status="DRAFT", upstream_req_hash=requirement.content_hash,
        content_hash=content_hash, version=1, created_by_agent=True,
    )
    session.add(tc)
    return tc


# Function: _generate_fast_test_cases_for_requirement
async def _generate_fast_test_cases_for_requirement(
    session: AsyncSession, project_id: uuid.UUID, requirement: Requirement,
) -> list[TestCase]:
    """Build a scenario matrix from extracted requirement and acceptance criteria.

    Uses _classify_test_level to assign appropriate test levels rather than defaulting
    everything to UI_E2E.
    """
    criteria = requirement.acceptance_criteria or [requirement.statement]
    precondition = str((requirement.ears_parts or {}).get("precondition") or "").strip()
    trigger = str((requirement.ears_parts or {}).get("trigger") or "").strip()
    preconditions = [
        v for v in (
            f"Requirement {requirement.req_id} is APPROVED and test environment is available.",
            precondition or None,
        ) if v
    ]

    definitions = _build_test_case_definitions(requirement, criteria, trigger)

    generated: list[TestCase] = []
    for test_type, title, steps in definitions:
        # Classify each test to the appropriate level based on its type and requirement characteristics
        level = _classify_test_level(requirement, test_type)
        tc = await _build_fast_test_case(session, project_id, requirement, level, preconditions, test_type, title, steps)
        if tc is not None:
            generated.append(tc)
    return generated


async def _create_project_journey_case(
    session: AsyncSession, project: Project, requirements: list[Requirement],
) -> TestCase | None:
    """Create one source-ordered UAT reconciliation spanning all extracted stages."""
    if len(requirements) < 2:
        return None
    steps = []
    for step_no, requirement in enumerate(requirements, 1):
        steps.append({
            "step_no": step_no,
            "action": (
                f"Perform the source-defined journey stage for {requirement.req_id}: {requirement.statement} "
                "[IMPLEMENTATION BINDING PENDING — map this business action to the confirmed system, role, "
                "transaction or interface, and fields before execution.]"
            ),
            "expected_result": "; ".join(requirement.acceptance_criteria or [requirement.statement]),
            "test_data": _authoritative_evidence(requirement),
            "binding_status": "PENDING",
        })
    title = f"{project.name} — end-to-end requirement sequence reconciliation"
    content_hash = _content_hash({"title": title, "steps": steps, "generator_schema_version": 2})
    test_case = TestCase(
        tc_id=await allocate_next_id(session, project.id, "TC"),
        project_id=project.id,
        requirement_id=requirements[0].id,
        title=title,
        test_type="POSITIVE",
        test_level="UAT",
        preconditions=[
            "Every linked requirement is approved.",
            "All recorded ambiguities, roles, systems, units, statuses, and automation contracts are resolved.",
        ],
        steps=steps,
        priority="P1",
        status="DRAFT",
        gherkin=json.dumps({
            "objective": "Reconcile the complete source-ordered business journey across all approved requirements.",
            "process_area": "END_TO_END",
            "risk_rating": "HIGH",
            "automation_status": "AUTOMATION_BLOCKED",
            "automation_blockers": ["Cross-system execution and reconciliation contract not supplied"],
            "systems_involved": [],
            "required_roles": [],
            "cleanup_instructions": ["[PENDING BUSINESS REVIEW — end-to-end reversal sequence not supplied]"],
            "ambiguities": ["Cross-system document-flow and reconciliation checkpoints require business confirmation."],
            "assumptions": [],
            "parallel_safe": False,
            "automation_context": {},
            "generator_schema_version": 2,
            "linked_requirement_ids": [requirement.req_id for requirement in requirements],
        }, ensure_ascii=False),
        upstream_req_hash=requirements[0].content_hash,
        content_hash=content_hash,
        version=1,
        created_by_agent=True,
    )
    session.add(test_case)
    await session.flush()
    return test_case


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
    approved_requirements = list(result.scalars().all())
    if not approved_requirements:
        raise ValueError("No APPROVED requirements — cannot design tests for an empty requirement set.")

    grounding_gaps: list[str] = []
    non_testable: list[Requirement] = []
    for requirement in approved_requirements:
        if not requirement.acceptance_criteria:
            if requirement.level == "ASSUMPTION":
                non_testable.append(requirement)
                continue
            grounding_gaps.append(
                f"{requirement.req_id} has no source-stated, testable expected outcome"
            )
            continue
        chunk_ids = [citation.chunk_id for citation in requirement.citations]
        evidence = "\n".join((await session.scalars(
            select(Chunk.text).where(Chunk.id.in_(chunk_ids))
        )).all()) if chunk_ids else ""
        for criterion_number, criterion in enumerate(requirement.acceptance_criteria or [], start=1):
            if not _acceptance_criterion_is_grounded(criterion, evidence):
                grounding_gaps.append(
                    f"{requirement.req_id} AC #{criterion_number} is not entailed by its cited source"
                )
    if grounding_gaps:
        raise ValueError(
            "Test Design blocked because the approved requirement baseline contains unsupported "
            "acceptance criteria: " + "; ".join(grounding_gaps)
        )
    requirements = [
        requirement for requirement in approved_requirements
        if requirement.acceptance_criteria and requirement.level != "ASSUMPTION"
    ]
    if not requirements:
        raise ValueError(
            "Test Design blocked: the approved baseline contains no testable requirements with source-stated outcomes."
        )

    existing_count = await session.scalar(
        select(func.count(TestCase.id)).where(TestCase.project_id == project_id)
    )
    if existing_count:
        raise ValueError(
            f"Project already contains {existing_count} test case(s). Test Design is replacement-based; "
            "archive/reset existing Test Design artifacts before regenerating to prevent duplicate inventory growth."
        )

    summary = TestDesignSummary()
    plan = await _author_test_plan(session, project, approved_requirements, pipeline_run_id)
    summary.test_plan_id = plan.id
    if non_testable:
        summary.warnings.append(
            "Excluded information-gap assumptions from executable coverage: "
            + ", ".join(requirement.req_id for requirement in non_testable)
        )
    
    # Generate comprehensive test plan DOCX document
    try:
        await generate_test_plan_docx(session, project_id=project_id, test_plan=plan, pipeline_run_id=pipeline_run_id)
    except Exception as exc:
        # Log warning but don't fail the entire test design if DOCX generation fails
        summary.warnings.append(f"Test plan DOCX generation failed: {str(exc)[:200]}")

    completed = 0
    semaphore = asyncio.Semaphore(TEST_DESIGN_CONCURRENCY)
    design_provider = OllamaProvider(model=OLLAMA_ANALYSIS_MODEL, keep_alive="5m")
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
                    design_provider,
                    project_id,
                    requirement,
                    pipeline_run_id,
                    project=project,
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
        await design_provider.unload()

    journey = await _create_project_journey_case(session, project, requirements)
    if journey is not None:
        await session.commit()
        summary.test_cases_created += 1
    return summary
