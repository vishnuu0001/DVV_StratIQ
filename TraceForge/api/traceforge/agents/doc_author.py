# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §5 Agent 2 (BRD Author), generalised to also drive FSD and Solution Documentation
# Date: 2025-07-29
# ---------------------------------------------------------------------------
"""§5 Agent 2 (BRD Author), generalised to also drive FSD and Solution Documentation
this pass (new scope: same citation/gate/traceability rigor as BRD, per the user's
explicit ask). One shared engine, three section-map configurations below.

The agent does NOT write the requirements (already fixed, already APPROVED) — it
writes the connective tissue (GENERATED, RAG-grounded, footnoted) and slots
deterministic REQ_TABLE/GLOSSARY/RTM_SUMMARY sections in, exactly per spec §5's mode
split.
"""
from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.agents.base import call_agent_llm
from traceforge.agents.docx_render import RenderedSection, render_document
from traceforge.config import FAST_PIPELINE, STORAGE_DIR
from traceforge.db.models import (
    Artifact, Chunk, Project, Requirement, SourceCitation, SourceDocument, Template,
)
from traceforge.llm.ollama import OllamaProvider


@dataclass
class SectionSpec:
    key: str
    heading: str
    mode: str  # GENERATED | REQ_TABLE | GLOSSARY | RTM_SUMMARY
    level_filter: list[str] | None = None  # REQ_TABLE
    max_words: int = 400  # GENERATED
    prompt_hint: str = ""  # GENERATED — what this section should cover


@dataclass
class DocDefinition:
    doc_kind: str          # "BRD" | "FSD" | "SOLUTION_DOC"
    artifact_kind: str      # ArtifactKind value
    title_suffix: str
    filename_prefix: str
    sections: list[SectionSpec]


BRD_DEFINITION = DocDefinition(
    doc_kind="BRD", artifact_kind="BRD_DOCX", title_suffix="Business Requirements Document", filename_prefix="BRD",
    sections=[
        SectionSpec("exec_summary", "1. Executive Summary", "GENERATED", max_words=400,
                    prompt_hint="A concise executive summary of the project's business objectives and scope."),
        SectionSpec("background", "2. Business Context", "GENERATED", max_words=800,
                    prompt_hint="The business context and problem this project addresses, grounded in the source material."),
        SectionSpec("scope", "3. Scope", "GENERATED", max_words=400,
                    prompt_hint="What is in scope and explicitly out of scope for this project."),
        SectionSpec("br", "4. Business Requirements", "REQ_TABLE", level_filter=["BUSINESS"]),
        SectionSpec("fr", "5. Functional Requirements", "REQ_TABLE", level_filter=["FUNCTIONAL"]),
        SectionSpec("nfr", "6. Non-Functional Requirements", "REQ_TABLE", level_filter=["NON_FUNCTIONAL"]),
        SectionSpec("assumptions", "7. Assumptions & Dependencies", "REQ_TABLE", level_filter=["ASSUMPTION", "CONSTRAINT"]),
        SectionSpec("glossary", "8. Glossary", "GLOSSARY"),
        SectionSpec("traceability", "9. Traceability Summary", "RTM_SUMMARY"),
    ],
)

FRD_DEFINITION = DocDefinition(
    doc_kind="FRD", artifact_kind="FRD_DOCX",
    title_suffix="Software and Functional Requirements Specification",
    filename_prefix="SRS_FRS",
    sections=[
        SectionSpec(
            "system_context", "1. System Context and Scope", "GENERATED", max_words=600,
            prompt_hint="The system boundary, actors, external systems, scope, and exclusions supported by the approved evidence.",
        ),
        SectionSpec(
            "functional_capabilities", "2. Functional Capabilities", "GENERATED", max_words=800,
            prompt_hint="The functional capabilities and observable system behaviours grouped into coherent business capabilities.",
        ),
        SectionSpec(
            "business_rules", "3. Business Rules and Validations", "GENERATED", max_words=700,
            prompt_hint="Business rules, validation conditions, decision logic, and error behaviours explicitly supported by the evidence.",
        ),
        SectionSpec(
            "interfaces", "4. External Interface Requirements", "GENERATED", max_words=700,
            prompt_hint="User, software, data, and integration interfaces, including known inputs, outputs, triggers, and constraints.",
        ),
        SectionSpec("fr", "5. Functional Requirements", "REQ_TABLE", level_filter=["FUNCTIONAL"]),
        SectionSpec("nfr", "6. Non-Functional Requirements", "REQ_TABLE", level_filter=["NON_FUNCTIONAL"]),
        SectionSpec(
            "constraints", "7. Constraints and Assumptions", "REQ_TABLE",
            level_filter=["CONSTRAINT", "ASSUMPTION"],
        ),
        SectionSpec("glossary", "8. Glossary", "GLOSSARY"),
        SectionSpec("traceability", "9. Traceability Summary", "RTM_SUMMARY"),
    ],
)

FSD_DEFINITION = DocDefinition(
    doc_kind="FSD", artifact_kind="FSD_DOCX", title_suffix="Functional Specification Document", filename_prefix="FSD",
    sections=[
        SectionSpec("functional_overview", "1. Functional Overview", "GENERATED", max_words=400,
                    prompt_hint="A functional overview of how the system behaves, grounded in the approved requirements and source material."),
        SectionSpec("user_flows", "2. User Flows", "GENERATED", max_words=800,
                    prompt_hint="Step-by-step user flows implied by the functional requirements — describe the sequence of user/system interactions."),
        SectionSpec("screen_specs", "3. Screen-Level Specifications", "GENERATED", max_words=800,
                    prompt_hint="Screen or interface-level behaviour implied by the functional requirements — fields, actions, validations."),
        SectionSpec("api_contracts", "4. API / Integration Contracts", "GENERATED", max_words=600,
                    prompt_hint="Any API or system-integration contracts implied by the requirements — endpoints, data exchanged, triggers."),
        SectionSpec("fr", "5. Functional Requirements Reference", "REQ_TABLE", level_filter=["FUNCTIONAL"]),
        SectionSpec("nfr", "6. Non-Functional Requirements Reference", "REQ_TABLE", level_filter=["NON_FUNCTIONAL"]),
        SectionSpec("glossary", "7. Glossary", "GLOSSARY"),
    ],
)

SOLUTION_DOC_DEFINITION = DocDefinition(
    doc_kind="SOLUTION_DOC", artifact_kind="SOLUTION_DOC_DOCX", title_suffix="Solution Documentation", filename_prefix="SolutionDoc",
    sections=[
        SectionSpec("architecture_overview", "1. Architecture Overview", "GENERATED", max_words=600,
                    prompt_hint="A proposed solution architecture addressing the approved requirements, grounded in the source material."),
        SectionSpec("tech_stack", "2. Technology Stack", "GENERATED", max_words=400,
                    prompt_hint="The technology stack implied or required by the source material and non-functional requirements."),
        SectionSpec("deployment_approach", "3. Deployment Approach", "GENERATED", max_words=400,
                    prompt_hint="The deployment/hosting approach implied by the requirements and any infrastructure constraints in the source material."),
        SectionSpec("nfr_mapping", "4. Non-Functional Requirements Mapping", "REQ_TABLE", level_filter=["NON_FUNCTIONAL"]),
        SectionSpec("constraints", "5. Constraints", "REQ_TABLE", level_filter=["CONSTRAINT"]),
        SectionSpec("glossary", "6. Glossary", "GLOSSARY"),
    ],
)


# Function: _generate_section_prose
async def _generate_section_prose(
    session: AsyncSession, provider: OllamaProvider, *, spec: SectionSpec, project: Project,
    requirements: list[Requirement], chunk_context: str, pipeline_run_id: uuid.UUID | None, agent_name: str,
) -> tuple[str, list[str]]:
    system = (
        "You are a senior business/solution analyst writing one section of a formal "
        f"project document for '{project.name}'. Write ONLY the section body — no heading, "
        f"no markdown, plain prose paragraphs separated by blank lines. Target under {spec.max_words} words. "
        "Ground every claim in the provided source context and approved requirements; do not invent facts. "
        "If the source material doesn't cover something, say so briefly rather than fabricating detail."
    )
    req_summary = "\n".join(f"- {r.req_id} [{r.level}]: {r.statement}" for r in requirements[:40])
    user = (
        f"SECTION TO WRITE: {spec.heading}\nFOCUS: {spec.prompt_hint}\n\n"
        f"APPROVED REQUIREMENTS:\n{req_summary or '(none yet)'}\n\n"
        f"SOURCE CONTEXT:\n{chunk_context or '(no additional source context)'}\n\n"
        "Return plain prose text only, nothing else (no JSON, no markdown fences)."
    )
    # json_mode=False: this call wants plain prose, not the ABC's default JSON-grammar
    # mode — forcing JSON here previously fought the prompt's own "no JSON" instruction.
    # max_tokens sized for the largest section spec (800 words * ~1.3 tokens/word) with
    # real headroom, not the prior flat 1200 that could cut an 800-word section short.
    response = await provider.generate(system, user, temperature=0.3, max_tokens=1800, json_mode=False)
    from traceforge.llm.metering import record_llm_call
    await record_llm_call(session, pipeline_run_id=pipeline_run_id, agent_name=agent_name, response=response)
    return response.text.strip(), []


# Function: _gather_chunk_context
async def _gather_chunk_context(session: AsyncSession, project_id: uuid.UUID, limit: int = 30) -> str:
    # Deterministic, document-order selection — an unordered LIMIT lets Postgres return
    # any arbitrary slice, which for a multi-document project could silently omit one
    # source document's content from every section's context entirely.
    result = await session.execute(
        select(Chunk).join(SourceDocument, Chunk.source_document_id == SourceDocument.id)
        .where(Chunk.project_id == project_id)
        .order_by(SourceDocument.ingested_at, Chunk.ordinal)
        .limit(limit)
    )
    chunks = list(result.scalars().all())
    return "\n---\n".join(c.text[:800] for c in chunks)


# Function: _source_labels_for_requirements
async def _source_labels_for_requirements(
    session: AsyncSession, requirements: list[Requirement],
) -> list[str]:
    if not requirements:
        return []
    rows = (await session.execute(
        select(SourceDocument.filename, Chunk.locator)
        .join(Chunk, Chunk.source_document_id == SourceDocument.id)
        .join(SourceCitation, SourceCitation.chunk_id == Chunk.id)
        .where(SourceCitation.requirement_id.in_([item.id for item in requirements]))
        .order_by(SourceDocument.filename, Chunk.ordinal)
    )).all()
    labels: list[str] = []
    for filename, locator in rows:
        locator_text = ", ".join(
            f"{key}={value}" for key, value in (locator or {}).items()
            if value not in (None, "", [])
        )
        label = f"{filename} ({locator_text})" if locator_text else filename
        if label not in labels:
            labels.append(label)
    return labels[:25]


# Function: _build_glossary_rows
def _build_glossary_rows(project: Project) -> list[dict]:
    return [{"Term": term, "Definition": ""} for term in sorted(project.config.get("glossary", []))]


# Function: _build_rtm_summary_rows
async def _build_rtm_summary_rows(session: AsyncSession, project_id: uuid.UUID, requirements: list[Requirement]) -> list[dict]:
    cited_ids = set((await session.scalars(
        select(SourceCitation.requirement_id).where(SourceCitation.requirement_id.in_([r.id for r in requirements])).distinct()
    )).all())
    return [
        {"REQ-ID": req.req_id, "Level": req.level, "Status": req.status, "Has Citation": "Yes" if req.id in cited_ids else "No"}
        for req in requirements
    ]


# Function: _fast_section_prose
def _fast_section_prose(spec: SectionSpec, project: Project, requirements: list[Requirement]) -> str:
    """Produce concise, grounded connective text from already AI-extracted and
    human-approved requirements without another GPU call for every document section."""
    relevant = requirements
    heading = spec.heading.lower()
    if "business" in heading:
        relevant = [r for r in requirements if r.level == "BUSINESS"] or requirements
    elif any(word in heading for word in ("functional", "screen", "flow", "api", "integration")):
        relevant = [r for r in requirements if r.level == "FUNCTIONAL"] or requirements
    elif any(word in heading for word in ("architecture", "technology", "deployment")):
        relevant = [r for r in requirements if r.level in {"NON_FUNCTIONAL", "CONSTRAINT"}] or requirements
    statements = " ".join(f"{r.req_id}: {r.statement}" for r in relevant[:10])
    return (
        f"This section addresses {spec.prompt_hint.rstrip('.').lower()} for {project.name}. "
        f"It is grounded in the approved requirement baseline. {statements}"
    )[: max(500, spec.max_words * 6)]


# Function: run_doc_author
async def run_doc_author(
    session: AsyncSession, *, project_id: uuid.UUID, definition: DocDefinition, pipeline_run_id: uuid.UUID | None,
) -> Artifact:
    project = await session.get(Project, project_id)
    if project is None:
        raise ValueError(f"project {project_id} not found")

    result = await session.execute(
        select(Requirement).where(Requirement.project_id == project_id, Requirement.status == "APPROVED")
        .order_by(Requirement.req_id)
    )
    requirements = list(result.scalars().all())
    if not requirements:
        raise ValueError("No APPROVED requirements — cannot author a document from an empty requirement set.")

    provider = OllamaProvider()
    chunk_context = "" if FAST_PIPELINE else await _gather_chunk_context(session, project_id)
    source_labels = await _source_labels_for_requirements(session, requirements)

    rendered_sections: list[RenderedSection] = []
    for spec in definition.sections:
        if spec.mode == "GENERATED":
            if FAST_PIPELINE:
                body, citations = _fast_section_prose(spec, project, requirements), source_labels
            else:
                body, _ = await _generate_section_prose(
                    session, provider, spec=spec, project=project, requirements=requirements,
                    chunk_context=chunk_context, pipeline_run_id=pipeline_run_id, agent_name=definition.doc_kind.lower(),
                )
                citations = source_labels
            rendered_sections.append(RenderedSection(key=spec.key, heading=spec.heading, mode="GENERATED", body_text=body, citations=citations))
        elif spec.mode == "REQ_TABLE":
            filtered = [r for r in requirements if r.level in (spec.level_filter or [])]
            rows = [{"REQ-ID": r.req_id, "Statement": r.statement, "Priority": r.priority,
                      "Acceptance Criteria": "; ".join(r.acceptance_criteria), "Source": r.level} for r in filtered]
            rendered_sections.append(RenderedSection(key=spec.key, heading=spec.heading, mode="REQ_TABLE",
                                                       table_columns=["REQ-ID", "Statement", "Priority", "Acceptance Criteria", "Source"], table_rows=rows))
        elif spec.mode == "GLOSSARY":
            rendered_sections.append(RenderedSection(key=spec.key, heading=spec.heading, mode="GLOSSARY",
                                                       table_columns=["Term", "Definition"], table_rows=_build_glossary_rows(project)))
        elif spec.mode == "RTM_SUMMARY":
            rows = await _build_rtm_summary_rows(session, project_id, requirements)
            rendered_sections.append(RenderedSection(key=spec.key, heading=spec.heading, mode="RTM_SUMMARY",
                                                       table_columns=["REQ-ID", "Level", "Status", "Has Citation"], table_rows=rows))

    await session.commit()  # persist LLMCall rows written during generation

    project_dir = STORAGE_DIR / str(project_id) / "artifacts"
    project_dir.mkdir(parents=True, exist_ok=True)
    previous_version = await session.scalar(
        select(func.max(Artifact.version)).where(
            Artifact.project_id == project_id,
            Artifact.kind == definition.artifact_kind,
        )
    )
    version = int(previous_version or 0) + 1
    filename = f"{definition.filename_prefix}_{project.key}_v{version}.docx"
    output_path = project_dir / filename

    template = (await session.scalars(
        select(Template).where(
            Template.kind == definition.doc_kind,
            (Template.project_id == project_id) | (Template.project_id.is_(None)),
        ).order_by(Template.project_id.desc().nullslast())
    )).first()
    template_path = template.blob_uri if template else None

    render_document(
        template_path=template_path, title=f"{project.name} — {definition.title_suffix}",
        subtitle=project.client_name or "", sections=rendered_sections, output_path=str(output_path),
    )

    sha256 = hashlib.sha256(output_path.read_bytes()).hexdigest()
    artifact = Artifact(
        project_id=project_id, pipeline_run_id=pipeline_run_id, kind=definition.artifact_kind,
        filename=filename, blob_uri=str(output_path), sha256=sha256, version=version,
        requirement_ids=[r.req_id for r in requirements],
    )
    session.add(artifact)
    await session.commit()
    await session.refresh(artifact)
    return artifact
