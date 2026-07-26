# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/traceforge/routers (workspace.py)
# Date: 2026-07-06
# ---------------------------------------------------------------------------
from __future__ import annotations

import hashlib
import json
import re
import uuid
from collections import defaultdict
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.auth import current_user
from traceforge.config import STORAGE_DIR
from traceforge.db.models import (
    Artifact, AuditEvent, Baseline, ConnectorConfig, Gate, PipelineRun,
    Project, Requirement, SourceCitation, Template, TestCase, TestScript,
)
from traceforge.db.session import get_session
from traceforge.schemas.workspace import (
    BaselineCreate, BaselineOut, ConnectorConfigOut, ConnectorConfigUpsert,
    ReviewOut, TemplateOut,
)

router = APIRouter(prefix="/api/v1", tags=["workspace"])

_TEMPLATE_KINDS = {
    "BRD", "FRD", "FSD", "SOLUTION_DOC", "RTM", "TEST_PLAN", "TEST_CASE",
}
_TEMPLATE_EXTENSIONS = {".docx", ".dotx", ".xlsx"}
_MAX_TEMPLATE_BYTES = 10 * 1024 * 1024


# Function: _project_or_404
async def _project_or_404(session: AsyncSession, project_id: uuid.UUID) -> Project:
    project = await session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# Function: _canonical_hash
def _canonical_hash(payload: dict) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


# Function: _baseline_snapshot
async def _baseline_snapshot(session: AsyncSession, project_id: uuid.UUID) -> dict:
    requirements = list((await session.scalars(
        select(Requirement).where(Requirement.project_id == project_id)
        .order_by(Requirement.req_id)
    )).all())
    test_cases = list((await session.scalars(
        select(TestCase).where(TestCase.project_id == project_id)
        .order_by(TestCase.tc_id)
    )).all())
    scripts = list((await session.scalars(
        select(TestScript).where(TestScript.project_id == project_id)
        .order_by(TestScript.ts_id)
    )).all())
    artifacts = list((await session.scalars(
        select(Artifact).where(Artifact.project_id == project_id)
        .order_by(Artifact.kind, Artifact.version)
    )).all())
    return {
        "schema_version": 1,
        "requirements": [
            {
                "id": str(item.id), "req_id": item.req_id, "version": item.version,
                "status": item.status, "content_hash": item.content_hash,
            }
            for item in requirements
        ],
        "test_cases": [
            {
                "id": str(item.id), "tc_id": item.tc_id,
                "requirement_id": str(item.requirement_id),
                "version": item.version, "content_hash": item.content_hash,
                "status": item.status,
            }
            for item in test_cases
        ],
        "test_scripts": [
            {
                "id": str(item.id), "ts_id": item.ts_id,
                "test_case_id": str(item.test_case_id),
                "version": item.version, "status": item.status,
                "target": item.target,
            }
            for item in scripts
        ],
        "artifacts": [
            {
                "id": str(item.id), "kind": item.kind, "version": item.version,
                "sha256": item.sha256, "stale": item.stale,
            }
            for item in artifacts
        ],
    }


# Function: requirement_quality
@router.get("/projects/{project_id}/quality")
async def requirement_quality(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(current_user),
):
    await _project_or_404(session, project_id)
    requirements = list((await session.scalars(
        select(Requirement).where(Requirement.project_id == project_id)
        .order_by(Requirement.req_id)
    )).all())
    cited = set((await session.scalars(
        select(SourceCitation.requirement_id).join(
            Requirement, SourceCitation.requirement_id == Requirement.id,
        ).where(Requirement.project_id == project_id)
    )).all())

    findings: list[dict] = []
    normalized: dict[str, list[Requirement]] = defaultdict(list)
    contradiction_candidates: dict[str, list[tuple[Requirement, bool]]] = defaultdict(list)
    for requirement in requirements:
        key = re.sub(r"\W+", " ", requirement.statement.lower()).strip()
        normalized[key].append(requirement)
        is_negative = bool(re.search(r"\b(?:shall|must|may)\s+not\b", key))
        contradiction_key = re.sub(
            r"\b(shall|must|may)\s+not\b", r"\1", key,
        )
        contradiction_candidates[contradiction_key].append((requirement, is_negative))
        if requirement.id not in cited:
            findings.append({
                "code": "MISSING_CITATION", "severity": "BLOCKER",
                "requirement_ids": [requirement.req_id],
                "message": "Requirement has no source citation.",
            })
        if requirement.ambiguity_score >= 0.4:
            findings.append({
                "code": "AMBIGUOUS_REQUIREMENT", "severity": "HIGH",
                "requirement_ids": [requirement.req_id],
                "message": (
                    f"Ambiguity score {requirement.ambiguity_score:.2f}; "
                    f"{len(requirement.ambiguity_flags)} rule(s) triggered."
                ),
            })
        if not requirement.acceptance_criteria:
            findings.append({
                "code": "MISSING_ACCEPTANCE_CRITERIA", "severity": "HIGH",
                "requirement_ids": [requirement.req_id],
                "message": "Requirement has no acceptance criteria.",
            })
    for duplicates in normalized.values():
        if len(duplicates) > 1:
            findings.append({
                "code": "EXACT_DUPLICATE", "severity": "MEDIUM",
                "requirement_ids": [item.req_id for item in duplicates],
                "message": "Requirements contain the same normalized statement.",
            })
    for candidates in contradiction_candidates.values():
        polarities = {negative for _, negative in candidates}
        if len(candidates) > 1 and len(polarities) > 1:
            findings.append({
                "code": "POTENTIAL_CONFLICT", "severity": "HIGH",
                "requirement_ids": [item.req_id for item, _ in candidates],
                "message": (
                    "Requirements contain equivalent statements with opposing "
                    "shall/must/may-not polarity and require analyst resolution."
                ),
            })
    blockers = sum(item["severity"] == "BLOCKER" for item in findings)
    high = sum(item["severity"] == "HIGH" for item in findings)
    return {
        "total_requirements": len(requirements),
        "finding_count": len(findings),
        "blocker_count": blockers,
        "high_count": high,
        "quality_gate": "FAIL" if blockers else ("REVIEW" if high else "PASS"),
        "findings": findings,
    }


# Function: create_baseline
@router.post(
    "/projects/{project_id}/baselines", response_model=BaselineOut, status_code=201,
)
async def create_baseline(
    project_id: uuid.UUID,
    body: BaselineCreate,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(current_user),
):
    await _project_or_404(session, project_id)
    snapshot = await _baseline_snapshot(session, project_id)
    if not snapshot["requirements"]:
        raise HTTPException(
            status_code=409, detail="Cannot baseline a project with no requirements.",
        )
    baseline = Baseline(
        project_id=project_id, name=body.name.strip(),
        description=body.description, snapshot=snapshot,
        sha256=_canonical_hash(snapshot),
        created_by=user.get("username", "unknown"),
    )
    session.add(baseline)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="A baseline with this name or identical content already exists.",
        ) from exc
    session.add(AuditEvent(
        project_id=project_id, actor=user.get("username", "unknown"),
        action="BASELINE_CREATED", entity_type="Baseline",
        entity_id=str(baseline.id),
        after={"name": baseline.name, "sha256": baseline.sha256},
    ))
    await session.commit()
    await session.refresh(baseline)
    return baseline


# Function: list_baselines
@router.get("/projects/{project_id}/baselines", response_model=list[BaselineOut])
async def list_baselines(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(current_user),
):
    await _project_or_404(session, project_id)
    return list((await session.scalars(
        select(Baseline).where(Baseline.project_id == project_id)
        .order_by(Baseline.created_at.desc())
    )).all())


# Function: list_reviews
@router.get("/projects/{project_id}/reviews", response_model=list[ReviewOut])
async def list_reviews(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(current_user),
):
    await _project_or_404(session, project_id)
    rows = (await session.execute(
        select(Gate, PipelineRun)
        .join(PipelineRun, Gate.pipeline_run_id == PipelineRun.id)
        .where(PipelineRun.project_id == project_id)
        .order_by(PipelineRun.created_at.desc())
    )).all()
    return [
        ReviewOut(
            id=gate.id, run_id=run.id, stage=run.stage,
            required_role=gate.required_role, decision=gate.decision,
            decided_by=gate.decided_by, decided_at=gate.decided_at,
            rationale=gate.rationale, created_at=run.created_at,
        )
        for gate, run in rows
    ]


# Function: list_integrations
@router.get(
    "/projects/{project_id}/integrations",
    response_model=list[ConnectorConfigOut],
)
async def list_integrations(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(current_user),
):
    await _project_or_404(session, project_id)
    return list((await session.scalars(
        select(ConnectorConfig).where(ConnectorConfig.project_id == project_id)
        .order_by(ConnectorConfig.connector_type)
    )).all())


# Function: upsert_integration
@router.put(
    "/projects/{project_id}/integrations/{connector_type}",
    response_model=ConnectorConfigOut,
)
async def upsert_integration(
    project_id: uuid.UUID,
    connector_type: str,
    body: ConnectorConfigUpsert,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(current_user),
):
    await _project_or_404(session, project_id)
    normalized = connector_type.upper()
    if normalized != body.connector_type:
        raise HTTPException(
            status_code=400, detail="Path and body connector types must match.",
        )
    existing = (await session.scalars(
        select(ConnectorConfig).where(
            ConnectorConfig.project_id == project_id,
            ConnectorConfig.connector_type == normalized,
        )
    )).first()
    before = dict(existing.config) if existing else None
    if existing:
        existing.config = body.config
        integration = existing
    else:
        integration = ConnectorConfig(
            project_id=project_id, connector_type=normalized, config=body.config,
        )
        session.add(integration)
    await session.flush()
    session.add(AuditEvent(
        project_id=project_id, actor=user.get("username", "unknown"),
        action="INTEGRATION_CONFIGURED", entity_type="ConnectorConfig",
        entity_id=str(integration.id), before={"config": before},
        after={"connector_type": normalized, "config": body.config},
    ))
    await session.commit()
    await session.refresh(integration)
    return integration


# Function: list_templates
@router.get("/projects/{project_id}/templates", response_model=list[TemplateOut])
async def list_templates(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(current_user),
):
    await _project_or_404(session, project_id)
    return list((await session.scalars(
        select(Template).where(
            (Template.project_id == project_id) | (Template.project_id.is_(None))
        ).order_by(Template.kind, Template.filename)
    )).all())


# Function: upload_template
@router.post(
    "/projects/{project_id}/templates", response_model=TemplateOut, status_code=201,
)
async def upload_template(
    project_id: uuid.UUID,
    kind: str = Form(...),
    section_map: str = Form("{}"),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(current_user),
):
    await _project_or_404(session, project_id)
    normalized_kind = kind.strip().upper()
    if normalized_kind not in _TEMPLATE_KINDS:
        raise HTTPException(status_code=400, detail="Unsupported template kind.")
    safe_name = Path(file.filename or "").name
    suffix = Path(safe_name).suffix.lower()
    if not safe_name or suffix not in _TEMPLATE_EXTENSIONS:
        raise HTTPException(
            status_code=400, detail="Template must be DOCX, DOTX, or XLSX.",
        )
    if normalized_kind == "RTM" and suffix != ".xlsx":
        raise HTTPException(status_code=400, detail="RTM templates must be XLSX.")
    if normalized_kind != "RTM" and suffix not in {".docx", ".dotx"}:
        raise HTTPException(
            status_code=400, detail=f"{normalized_kind} templates must be DOCX or DOTX.",
        )
    content = await file.read(_MAX_TEMPLATE_BYTES + 1)
    if len(content) > _MAX_TEMPLATE_BYTES:
        raise HTTPException(status_code=413, detail="Template exceeds the 10 MB limit.")
    try:
        parsed_map = json.loads(section_map)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="section_map must be valid JSON.") from exc
    if not isinstance(parsed_map, dict):
        raise HTTPException(status_code=400, detail="section_map must be a JSON object.")

    target_dir = STORAGE_DIR / str(project_id) / "templates"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{uuid.uuid4().hex}_{safe_name}"
    target.write_bytes(content)
    template = Template(
        project_id=project_id, kind=normalized_kind, filename=safe_name,
        blob_uri=str(target), section_map=parsed_map,
    )
    session.add(template)
    await session.flush()
    session.add(AuditEvent(
        project_id=project_id, actor=user.get("username", "unknown"),
        action="TEMPLATE_UPLOADED", entity_type="Template",
        entity_id=str(template.id),
        after={"kind": normalized_kind, "filename": safe_name},
    ))
    await session.commit()
    await session.refresh(template)
    return template
