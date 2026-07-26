# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/traceforge/routers (requirements.py)
# Date: 2026-05-04
# ---------------------------------------------------------------------------
from __future__ import annotations

import hashlib
import json
import uuid

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.agents.ambiguity import score_requirement
from traceforge.agents.base import _extract_json
from traceforge.auth import current_user
from traceforge.connectors.jira import JiraAuthError, create_issue_from_requirement
from traceforge.db.models import AuditEvent, Chunk, Requirement, SourceCitation, SourceDocument
from traceforge.db.session import get_session
from traceforge.llm.ollama import OllamaProvider
from traceforge.orchestration.suspect import get_requirement_impact, propagate_suspect
from traceforge.schemas.requirement import CitationOut, RequirementDetailOut, RequirementOut, RequirementPatch, RequirementPatchOut

router = APIRouter(prefix="/api/v1", tags=["requirements"])


class JiraIssueRequest(BaseModel):
    base_url: str
    email: str
    api_token: str
    project_key: str
    issue_type: str = "Story"


# Function: list_requirements
@router.get("/projects/{project_id}/requirements", response_model=list[RequirementOut])
async def list_requirements(
    project_id: uuid.UUID,
    status: str | None = None,
    level: str | None = None,
    min_ambiguity: float | None = Query(default=None),
    q: str | None = None,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(current_user),
):
    stmt = select(Requirement).where(Requirement.project_id == project_id)
    if status:
        stmt = stmt.where(Requirement.status == status)
    if level:
        stmt = stmt.where(Requirement.level == level)
    if min_ambiguity is not None:
        stmt = stmt.where(Requirement.ambiguity_score >= min_ambiguity)
    if q:
        stmt = stmt.where(Requirement.statement.ilike(f"%{q}%"))
    stmt = stmt.order_by(Requirement.ambiguity_score.desc(), Requirement.req_id)
    result = await session.execute(stmt)
    return list(result.scalars().all())


# Function: get_requirement
@router.get("/requirements/{req_id}", response_model=RequirementDetailOut)
async def get_requirement(req_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    requirement = await session.get(Requirement, req_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    result = await session.execute(
        select(SourceCitation, Chunk, SourceDocument)
        .join(Chunk, SourceCitation.chunk_id == Chunk.id)
        .join(SourceDocument, Chunk.source_document_id == SourceDocument.id)
        .where(SourceCitation.requirement_id == req_id)
    )
    citations = [
        CitationOut(
            id=citation.id, chunk_id=chunk.id, relevance=citation.relevance,
            quoted_span=citation.quoted_span, locator=chunk.locator,
            source_document_filename=source_doc.filename,
        )
        for citation, chunk, source_doc in result.all()
    ]
    return RequirementDetailOut(**RequirementOut.model_validate(requirement).model_dump(), citations=citations)


# Function: patch_requirement
@router.patch("/requirements/{req_id}", response_model=RequirementPatchOut)
async def patch_requirement(req_id: uuid.UUID, body: RequirementPatch, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    requirement = await session.get(Requirement, req_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    before = {"statement": requirement.statement, "status": requirement.status}
    was_approved = requirement.status == "APPROVED"
    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(requirement, field, value)

    content_changed = "statement" in updates or "acceptance_criteria" in updates
    if content_changed:
        # A human edit re-scores and un-marks agent authorship (spec §5 Gate 1: "edit
        # sets created_by_agent=false and re-runs the ambiguity scorer").
        requirement.created_by_agent = False
        score, flags = score_requirement(
            requirement.statement, requirement.ears_parts, requirement.ears_pattern, level=requirement.level,
        )
        requirement.ambiguity_score = score
        requirement.ambiguity_flags = [f.__dict__ for f in flags]
        payload = json.dumps({"statement": requirement.statement, "acceptance_criteria": requirement.acceptance_criteria}, sort_keys=True)
        requirement.content_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        requirement.version += 1

    session.add(AuditEvent(project_id=requirement.project_id, actor=user.get("username", "unknown"), action="REQUIREMENT_EDITED",
                            entity_type="Requirement", entity_id=str(requirement.id), before=before, after=updates))

    impact = None
    if content_changed and was_approved:
        # §6.2: editing an APPROVED requirement's content cascades SUSPECT downstream —
        # never silently deleted, never auto-regenerated without a human click.
        await session.flush()
        impact = await propagate_suspect(session, requirement, user.get("username", "unknown"))

    await session.commit()
    await session.refresh(requirement)
    response = RequirementOut.model_validate(requirement).model_dump()
    if impact:
        response["suspect_impact"] = impact
    return response


# Function: rewrite_requirement
@router.post("/requirements/{req_id}/rewrite")
async def rewrite_requirement(req_id: uuid.UUID, body: dict = Body(default={}), session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    """spec §8.3: click a red ambiguity flag -> [Fix] -> LLM proposes a quantified
    rewrite -> accept/reject diff. This returns the proposal only; the caller applies
    it via the normal PATCH endpoint (which re-scores and re-hashes)."""
    requirement = await session.get(Requirement, req_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    flag_code = (body or {}).get("flag_code")
    flag = next((f for f in requirement.ambiguity_flags if f.get("code") == flag_code), None) if flag_code else (requirement.ambiguity_flags[0] if requirement.ambiguity_flags else None)
    if not flag:
        raise HTTPException(status_code=422, detail="Requirement has no ambiguity flags to fix.")

    provider = OllamaProvider()
    system = (
        "You are a business analyst fixing one specific ambiguity in a requirement statement. "
        "Return JSON only: {\"statement\": str}. Rewrite ONLY to resolve the named issue — "
        "keep the EARS pattern, keep everything else about the requirement's meaning unchanged. "
        "Do not invent new scope. If the issue calls for a numeric target the source doesn't "
        "provide, use a clearly-marked placeholder like '[TBD: target value]' rather than inventing one."
    )
    user_msg = (
        f"REQUIREMENT: {requirement.statement}\nAMBIGUITY ISSUE: {flag['code']} — {flag['explanation']}\n"
        f"SUGGESTION: {flag['suggestion']}\nSPAN: {flag['span']}"
    )
    response = await provider.generate(system, user_msg, temperature=0.2, max_tokens=300)
    try:
        parsed = _extract_json(response.text)
        proposed_statement = parsed.get("statement", "").strip()
    except Exception:  # noqa: BLE001
        proposed_statement = response.text.strip()

    if not proposed_statement:
        raise HTTPException(status_code=502, detail="LLM did not return a usable rewrite.")

    new_score, new_flags = score_requirement(
        proposed_statement, requirement.ears_parts, requirement.ears_pattern, level=requirement.level,
    )
    return {
        "original_statement": requirement.statement, "proposed_statement": proposed_statement,
        "original_ambiguity_score": requirement.ambiguity_score, "proposed_ambiguity_score": new_score,
        "fixed_flag": flag_code,
    }


# Function: requirement_impact
@router.get("/requirements/{req_id}/impact")
async def requirement_impact(req_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    requirement = await session.get(Requirement, req_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return await get_requirement_impact(session, requirement)


# Function: push_requirement_to_jira
@router.post("/requirements/{req_id}/jira-issue")
async def push_requirement_to_jira(req_id: uuid.UUID, body: JiraIssueRequest, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    """JIRA write-back: create one issue per approved Requirement. Credentials are
    used for this request only and are not stored."""
    requirement = await session.get(Requirement, req_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    if requirement.status != "APPROVED":
        raise HTTPException(status_code=422, detail="Only APPROVED requirements can be pushed to JIRA.")

    try:
        issue = await create_issue_from_requirement(
            body.base_url, body.email, body.api_token, body.project_key, requirement, body.issue_type,
        )
    except JiraAuthError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    issue_key = issue.get("key")
    session.add(AuditEvent(project_id=requirement.project_id, actor=user.get("username", "unknown"), action="JIRA_ISSUE_CREATED",
                            entity_type="Requirement", entity_id=str(requirement.id), after={"jira_issue_key": issue_key}))
    await session.commit()
    return {"jira_issue_key": issue_key, "jira_url": f"{body.base_url.rstrip('/')}/browse/{issue_key}"}
