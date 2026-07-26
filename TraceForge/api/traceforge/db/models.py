# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Full TraceForge domain model (spec §3). Every entity is defined even though only a
# Date: 2026-02-16
# ---------------------------------------------------------------------------
"""Full TraceForge domain model (spec §3). Every entity is defined even though only a
subset is exercised by working routes in this pass — see PROGRESS.md for what's wired up."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean, CheckConstraint, Computed, DateTime, Float, ForeignKey, Integer,
    String, Text, UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from traceforge.config import OLLAMA_EMBED_DIM

# FK target constants — referenced by every table below (project.id alone appears
# on nearly every entity per §3), so a typo in one literal would silently create
# an orphaned/broken relationship instead of a name error.
_PROJECT_FK = "project.id"
_REQUIREMENT_FK = "requirement.id"
_PIPELINE_RUN_FK = "pipeline_run.id"


class Base(DeclarativeBase):
    pass


# Function: _uuid_pk
def _uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


# Function: _now
def _now() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), server_default=func.now())


# ── Enums (stored as VARCHAR + CHECK, not native PG enum — avoids ALTER TYPE churn) ──

class ProjectStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class SourceType(str, enum.Enum):
    SERVICENOW = "SERVICENOW"
    JIRA = "JIRA"
    UPLOAD = "UPLOAD"
    GIT_REPO = "GIT_REPO"
    URL = "URL"


class DocClass(str, enum.Enum):
    AS_IS_DOC = "AS_IS_DOC"
    SOW = "SOW"
    PROCESS_MAP = "PROCESS_MAP"
    INCIDENT_DATA = "INCIDENT_DATA"
    LEGACY_CODE = "LEGACY_CODE"
    KB_ARTICLE = "KB_ARTICLE"
    OTHER = "OTHER"


class SourceStatus(str, enum.Enum):
    PENDING = "PENDING"
    PARSING = "PARSING"
    INDEXED = "INDEXED"
    FAILED = "FAILED"


class ReqLevel(str, enum.Enum):
    BUSINESS = "BUSINESS"
    FUNCTIONAL = "FUNCTIONAL"
    NON_FUNCTIONAL = "NON_FUNCTIONAL"
    CONSTRAINT = "CONSTRAINT"
    ASSUMPTION = "ASSUMPTION"


class EarsPattern(str, enum.Enum):
    UBIQUITOUS = "UBIQUITOUS"
    EVENT_DRIVEN = "EVENT_DRIVEN"
    STATE_DRIVEN = "STATE_DRIVEN"
    OPTIONAL_FEATURE = "OPTIONAL_FEATURE"
    UNWANTED_BEHAVIOUR = "UNWANTED_BEHAVIOUR"
    COMPLEX = "COMPLEX"
    NON_CONFORMANT = "NON_CONFORMANT"


class Priority(str, enum.Enum):
    MUST = "MUST"
    SHOULD = "SHOULD"
    COULD = "COULD"
    WONT = "WONT"


class ReqStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"
    SUSPECT = "SUSPECT"


class TestType(str, enum.Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    EDGE = "EDGE"
    BOUNDARY = "BOUNDARY"
    NEGATIVE_SECURITY = "NEGATIVE_SECURITY"
    PERFORMANCE = "PERFORMANCE"


class TestLevel(str, enum.Enum):
    UNIT = "UNIT"
    API = "API"
    UI_E2E = "UI_E2E"
    INTEGRATION = "INTEGRATION"
    UAT = "UAT"


class ArtifactStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUSPECT = "SUSPECT"


class ScriptTarget(str, enum.Enum):
    PLAYWRIGHT_TS = "PLAYWRIGHT_TS"
    SELENIUM_TS = "SELENIUM_TS"
    PYTEST = "PYTEST"
    KARATE = "KARATE"
    TOSCA_XML = "TOSCA_XML"
    ROBOT = "ROBOT"


class PipelineStage(str, enum.Enum):
    INGEST = "INGEST"
    EXTRACT = "EXTRACT"
    BRD = "BRD"
    TEST_DESIGN = "TEST_DESIGN"
    SCRIPT_GEN = "SCRIPT_GEN"
    RENDER = "RENDER"


class RunStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class GateRole(str, enum.Enum):
    BUSINESS_ANALYST = "BUSINESS_ANALYST"
    TEST_LEAD = "TEST_LEAD"
    ARCHITECT = "ARCHITECT"
    CLIENT_REVIEWER = "CLIENT_REVIEWER"


class GateDecision(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPROVED_WITH_COMMENTS = "APPROVED_WITH_COMMENTS"


class ArtifactKind(str, enum.Enum):
    BRD_DOCX = "BRD_DOCX"
    FRD_DOCX = "FRD_DOCX"
    FSD_DOCX = "FSD_DOCX"
    SOLUTION_DOC_DOCX = "SOLUTION_DOC_DOCX"
    TEST_PLAN_DOCX = "TEST_PLAN_DOCX"
    RTM_XLSX = "RTM_XLSX"
    TEST_PACK_ZIP = "TEST_PACK_ZIP"
    SCRIPT_BUNDLE_ZIP = "SCRIPT_BUNDLE_ZIP"


class TemplateKind(str, enum.Enum):
    BRD = "BRD"
    FRD = "FRD"
    FSD = "FSD"
    SOLUTION_DOC = "SOLUTION_DOC"
    RTM = "RTM"
    TEST_PLAN = "TEST_PLAN"
    TEST_CASE = "TEST_CASE"


class ConnectorType(str, enum.Enum):
    SERVICENOW = "SERVICENOW"
    JIRA = "JIRA"
    GITHUB = "GITHUB"


# Function: _str_enum
def _str_enum(values: type[enum.Enum]) -> String:
    """VARCHAR sized to fit the longest member of `values` (floor of 64 so
    existing columns never shrink for any enum defined today)."""
    longest = max((len(v.value) for v in values), default=0)
    return String(max(64, longest))


# Function: _check
def _check(column: str, values: type[enum.Enum]) -> CheckConstraint:
    allowed = ", ".join(f"'{v.value}'" for v in values)
    return CheckConstraint(f"{column} IN ({allowed})", name=f"ck_{column}")


# ── 3.1 Core ──────────────────────────────────────────────────

class Project(Base):
    __tablename__ = "project"

    id: Mapped[uuid.UUID] = _uuid_pk()
    key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    client_name: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(_str_enum(ProjectStatus), default=ProjectStatus.DRAFT.value, nullable=False)
    brd_template_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("template.id"))
    config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = _now()
    created_by: Mapped[str | None] = mapped_column(String(255))

    __table_args__ = (_check("status", ProjectStatus),)


class SourceDocument(Base):
    __tablename__ = "source_document"

    id: Mapped[uuid.UUID] = _uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(_PROJECT_FK), nullable=False)
    source_type: Mapped[str] = mapped_column(_str_enum(SourceType), nullable=False)
    connector_ref: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(128))
    blob_uri: Mapped[str] = mapped_column(String(1024), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    doc_class: Mapped[str] = mapped_column(_str_enum(DocClass), nullable=False)
    page_count: Mapped[int | None] = mapped_column(Integer)
    ingested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(_str_enum(SourceStatus), default=SourceStatus.PENDING.value, nullable=False)
    parse_error: Mapped[str | None] = mapped_column(Text)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))  # soft delete per §7

    __table_args__ = (_check("source_type", SourceType), _check("doc_class", DocClass), _check("status", SourceStatus))


class Chunk(Base):
    __tablename__ = "chunk"

    id: Mapped[uuid.UUID] = _uuid_pk()
    source_document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("source_document.id"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(_PROJECT_FK), nullable=False)  # denormalised for filter perf
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    locator: Mapped[dict] = mapped_column(JSONB, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(OLLAMA_EMBED_DIM))
    # DB-generated (see migration: GENERATED ALWAYS AS (to_tsvector(...)) STORED). The
    # Computed() marker here tells the ORM to never include this column in INSERT/UPDATE
    # — Postgres rejects any explicit value, even NULL, for a generated column.
    bm25_tsv: Mapped[str | None] = mapped_column(TSVECTOR, Computed("to_tsvector('english', text)", persisted=True))
    chunk_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, nullable=False)

    __table_args__ = (UniqueConstraint("source_document_id", "ordinal", name="uq_chunk_source_ordinal"),)


# ── 3.2 The Traceability Spine ───────────────────────────────

class Requirement(Base):
    __tablename__ = "requirement"

    id: Mapped[uuid.UUID] = _uuid_pk()
    req_id: Mapped[str] = mapped_column(String(32), nullable=False)  # "REQ-0001" — immutable, allocated via IdSequence
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(_PROJECT_FK), nullable=False)
    parent_req_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey(_REQUIREMENT_FK))
    level: Mapped[str] = mapped_column(_str_enum(ReqLevel), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    ears_pattern: Mapped[str] = mapped_column(_str_enum(EarsPattern), nullable=False)
    ears_parts: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    rationale: Mapped[str | None] = mapped_column(Text)
    acceptance_criteria: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    priority: Mapped[str] = mapped_column(_str_enum(Priority), default=Priority.SHOULD.value, nullable=False)
    ambiguity_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    ambiguity_flags: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    status: Mapped[str] = mapped_column(_str_enum(ReqStatus), default=ReqStatus.DRAFT.value, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_by_agent: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = _now()
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    # §5 Agent 1 'Additional passes' — dedup: set when this requirement was merged into
    # a canonical duplicate (status becomes SUPERSEDED, row is kept, never deleted, P5).
    merged_into_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey(_REQUIREMENT_FK))
    # §5 Agent 1 'Additional passes' — conflict detection: [{conflicting_req_id, explanation}].
    conflict_flags: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    citations: Mapped[list["SourceCitation"]] = relationship(back_populates="requirement", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("project_id", "req_id", name="uq_requirement_project_req_id"),
        _check("level", ReqLevel), _check("ears_pattern", EarsPattern),
        _check("priority", Priority), _check("status", ReqStatus),
    )


class SourceCitation(Base):
    """The P1 enforcement table. See migration for the DEFERRABLE constraint trigger
    that rejects a transaction committing a Requirement with zero citations."""
    __tablename__ = "source_citation"

    id: Mapped[uuid.UUID] = _uuid_pk()
    requirement_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(_REQUIREMENT_FK), nullable=False)
    chunk_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chunk.id"), nullable=False)
    relevance: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    quoted_span: Mapped[str] = mapped_column(Text, nullable=False)

    requirement: Mapped["Requirement"] = relationship(back_populates="citations")

    __table_args__ = (UniqueConstraint("requirement_id", "chunk_id", name="uq_citation_req_chunk"),)


class TestCase(Base):
    __test__ = False
    __tablename__ = "test_case"

    id: Mapped[uuid.UUID] = _uuid_pk()
    tc_id: Mapped[str] = mapped_column(String(32), nullable=False)  # "TC-0001"
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(_PROJECT_FK), nullable=False)
    requirement_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(_REQUIREMENT_FK), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    test_type: Mapped[str] = mapped_column(_str_enum(TestType), nullable=False)
    test_level: Mapped[str] = mapped_column(_str_enum(TestLevel), nullable=False)
    preconditions: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    steps: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    gherkin: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(8), nullable=False)  # P1|P2|P3
    status: Mapped[str] = mapped_column(_str_enum(ArtifactStatus), default=ArtifactStatus.DRAFT.value, nullable=False)
    upstream_req_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_by_agent: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("project_id", "tc_id", name="uq_testcase_project_tc_id"),
        _check("test_type", TestType), _check("test_level", TestLevel), _check("status", ArtifactStatus),
        CheckConstraint("priority IN ('P1','P2','P3')", name="ck_test_case_priority"),
    )


class TestScript(Base):
    __test__ = False
    __tablename__ = "test_script"

    id: Mapped[uuid.UUID] = _uuid_pk()
    ts_id: Mapped[str] = mapped_column(String(32), nullable=False)  # "TS-0001"
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(_PROJECT_FK), nullable=False)
    test_case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("test_case.id"), nullable=False)
    target: Mapped[str] = mapped_column(_str_enum(ScriptTarget), nullable=False)
    language: Mapped[str] = mapped_column(String(32), nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    page_objects: Mapped[dict | None] = mapped_column(JSONB)
    compiles: Mapped[bool | None] = mapped_column(Boolean)
    validation_output: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(_str_enum(ArtifactStatus), default=ArtifactStatus.DRAFT.value, nullable=False)
    upstream_tc_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    __table_args__ = (
        UniqueConstraint("project_id", "ts_id", name="uq_testscript_project_ts_id"),
        UniqueConstraint("test_case_id", "target", name="uq_testscript_case_target"),
        _check("target", ScriptTarget), _check("status", ArtifactStatus),
    )


# ── 3.3 Orchestration & Governance ───────────────────────────

class PipelineRun(Base):
    __tablename__ = "pipeline_run"

    id: Mapped[uuid.UUID] = _uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(_PROJECT_FK), nullable=False)
    stage: Mapped[str] = mapped_column(_str_enum(PipelineStage), nullable=False)
    status: Mapped[str] = mapped_column(_str_enum(RunStatus), default=RunStatus.QUEUED.value, nullable=False)
    scope: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    input_snapshot: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    stats: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    error: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    triggered_by: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = _now()

    __table_args__ = (_check("stage", PipelineStage), _check("status", RunStatus))


class Gate(Base):
    __tablename__ = "gate"

    id: Mapped[uuid.UUID] = _uuid_pk()
    pipeline_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(_PIPELINE_RUN_FK), nullable=False)
    required_role: Mapped[str] = mapped_column(_str_enum(GateRole), nullable=False)
    decision: Mapped[str] = mapped_column(_str_enum(GateDecision), default=GateDecision.PENDING.value, nullable=False)
    decided_by: Mapped[str | None] = mapped_column(String(255))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rationale: Mapped[str | None] = mapped_column(Text)  # MANDATORY on REJECTED — enforced in schema validator
    item_decisions: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    auto_approve: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (_check("required_role", GateRole), _check("decision", GateDecision))


class AuditEvent(Base):
    """Append-only. DB grants (see migration) revoke UPDATE/DELETE for the app role."""
    __tablename__ = "audit_event"

    id: Mapped[uuid.UUID] = _uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(_PROJECT_FK), nullable=False)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)  # user or agent name
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    before: Mapped[dict | None] = mapped_column(JSONB)
    after: Mapped[dict | None] = mapped_column(JSONB)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class LLMCall(Base):
    __tablename__ = "llm_call"

    id: Mapped[uuid.UUID] = _uuid_pk()
    pipeline_run_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey(_PIPELINE_RUN_FK))
    agent_name: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 0 for local Ollama — no metered cost
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    schema_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # §6.3 PERSIST_LLM_IO (off by default): populated only when the flag is on AND PII
    # redaction succeeded — see llm/metering.py. Raw PII never lands in these two
    # columns; anything Presidio classified as PII is segregated into pii_entity_map.
    prompt_text: Mapped[str | None] = mapped_column(Text)
    completion_text: Mapped[str | None] = mapped_column(Text)
    pii_entity_map: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class Artifact(Base):
    __tablename__ = "artifact"

    id: Mapped[uuid.UUID] = _uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(_PROJECT_FK), nullable=False)
    pipeline_run_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey(_PIPELINE_RUN_FK))
    kind: Mapped[str] = mapped_column(_str_enum(ArtifactKind), nullable=False)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    blob_uri: Mapped[str] = mapped_column(String(1024), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    generated_at: Mapped[datetime] = _now()
    # §6.2 suspect propagation: which requirements this doc's REQ_TABLE/GENERATED
    # sections reference, and whether any of them have since gone SUSPECT.
    requirement_ids: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    stale: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (_check("kind", ArtifactKind),)


class Template(Base):
    __tablename__ = "template"

    id: Mapped[uuid.UUID] = _uuid_pk()
    project_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey(_PROJECT_FK))  # nullable → global
    kind: Mapped[str] = mapped_column(_str_enum(TemplateKind), nullable=False)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    blob_uri: Mapped[str] = mapped_column(String(1024), nullable=False)
    section_map: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    __table_args__ = (_check("kind", TemplateKind),)


# ── ID allocation (P5: deterministic, never reused/renumbered) ──

class IdSequence(Base):
    """Monotonic per-(project, prefix) counter — REQ-/TC-/TS- numbers are allocated from
    here, never derived from COUNT(*), so deleting a row never frees up its number."""
    __tablename__ = "id_sequence"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(_PROJECT_FK), primary_key=True)
    prefix: Mapped[str] = mapped_column(String(16), primary_key=True)
    next_value: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


# ── Ingestion staging (§4.1 — raw incident rows for drill-down, not embedded directly) ──

class ServiceNowIncident(Base):
    __tablename__ = "servicenow_incident"

    id: Mapped[uuid.UUID] = _uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(_PROJECT_FK), nullable=False)
    number: Mapped[str] = mapped_column(String(32), nullable=False)
    cluster_id: Mapped[str | None] = mapped_column(String(64))
    fields: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    __table_args__ = (UniqueConstraint("project_id", "number", name="uq_incident_project_number"),)


# ── Test Plan (new this pass, alongside TestCase/TestScript) ────

class TestPlan(Base):
    __test__ = False
    """One per project per TEST_DESIGN run — scope/strategy/environments/schedule,
    same citation-grounded rigor as a Requirement (P1: TestPlanCitation is required)."""
    __tablename__ = "test_plan"

    id: Mapped[uuid.UUID] = _uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(_PROJECT_FK), nullable=False)
    pipeline_run_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey(_PIPELINE_RUN_FK))
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    scope: Mapped[str] = mapped_column(Text, nullable=False)
    strategy: Mapped[str] = mapped_column(Text, nullable=False)
    environments: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    schedule: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    entry_exit_criteria: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(_str_enum(ArtifactStatus), default=ArtifactStatus.DRAFT.value, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = _now()

    citations: Mapped[list["TestPlanCitation"]] = relationship(back_populates="test_plan", cascade="all, delete-orphan")

    __table_args__ = (_check("status", ArtifactStatus),)


class TestPlanCitation(Base):
    __test__ = False
    """Same P1 pattern as SourceCitation — see migration for the matching
    DEFERRABLE constraint trigger on test_plan."""
    __tablename__ = "test_plan_citation"

    id: Mapped[uuid.UUID] = _uuid_pk()
    test_plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("test_plan.id"), nullable=False)
    chunk_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chunk.id"), nullable=False)
    relevance: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    quoted_span: Mapped[str] = mapped_column(Text, nullable=False)

    test_plan: Mapped["TestPlan"] = relationship(back_populates="citations")

    __table_args__ = (UniqueConstraint("test_plan_id", "chunk_id", name="uq_tpcitation_plan_chunk"),)


# ── Connector configuration (non-secret; credentials are per-request, never stored) ──

class ConnectorConfig(Base):
    __tablename__ = "connector_config"

    id: Mapped[uuid.UUID] = _uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(_PROJECT_FK), nullable=False)
    connector_type: Mapped[str] = mapped_column(_str_enum(ConnectorType), nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)  # e.g. {"base_url": ..., "project_key": ...}
    created_at: Mapped[datetime] = _now()

    __table_args__ = (
        UniqueConstraint("project_id", "connector_type", name="uq_connector_project_type"),
        _check("connector_type", ConnectorType),
    )


class Baseline(Base):
    """Immutable, content-addressed snapshot of the lifecycle spine.

    The snapshot is deliberately JSON rather than a set of mutable foreign keys:
    a baseline must continue to describe the approved state even after live
    requirements, tests, scripts, or artifacts change.
    """
    __tablename__ = "baseline"

    id: Mapped[uuid.UUID] = _uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(_PROJECT_FK), nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = _now()

    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_baseline_project_name"),
        UniqueConstraint("project_id", "sha256", name="uq_baseline_project_sha256"),
    )
