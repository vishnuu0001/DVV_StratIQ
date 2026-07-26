# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: JIRA connector — new this pass (not in the original spec). Raw httpx REST calls
# Date: 2026-06-02
# ---------------------------------------------------------------------------
"""JIRA connector — new this pass (not in the original spec). Raw httpx REST calls
against the Jira REST API v3, no heavyweight SDK, matching this repo's existing
ServiceNow-integration convention (see servicenow.py / Novastra-ITSM's CMDB client).

Read: JQL search -> one SourceDocument+Chunk per issue (issues are already
document-granular, unlike ServiceNow incidents — no aggregation pass needed).
Write: create/update issues from approved Requirements; comment-link TestCases back
to their JIRA ticket.
"""
from __future__ import annotations

import base64
import uuid
from datetime import datetime, timezone

import httpx

from traceforge.db.models import Chunk, Requirement, SourceDocument
from traceforge.indexing.embedder import embed_texts


class JiraAuthError(Exception):
    pass


# Function: _auth_header
def _auth_header(email: str, api_token: str) -> dict[str, str]:
    token = base64.b64encode(f"{email}:{api_token}".encode()).decode()
    return {"Authorization": f"Basic {token}", "Accept": "application/json", "Content-Type": "application/json"}


# Function: _issue_text
def _issue_text(issue: dict) -> str:
    fields = issue.get("fields", {})
    description = _adf_to_text(fields.get("description"))
    lines = [
        f"Issue: {issue.get('key')}",
        f"Type: {(fields.get('issuetype') or {}).get('name', '')}",
        f"Summary: {fields.get('summary', '')}",
        f"Status: {(fields.get('status') or {}).get('name', '')}",
        f"Priority: {(fields.get('priority') or {}).get('name', '')}",
        f"Description: {description}",
    ]
    return "\n".join(lines)


# Function: _adf_to_text
def _adf_to_text(adf: dict | str | None) -> str:
    """Jira Cloud descriptions are Atlassian Document Format (nested JSON), not plain
    text. Walk it and concatenate 'text' leaf nodes — good enough for RAG grounding,
    not a full ADF renderer."""
    if adf is None:
        return ""
    if isinstance(adf, str):
        return adf
    parts: list[str] = []

    # Function: walk
    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "text":
                parts.append(str(node.get("text", "")))
            for child in node.get("content", []) or []:
                walk(child)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(adf)
    return " ".join(parts)


# Function: search_issues
async def search_issues(base_url: str, email: str, api_token: str, jql: str, max_results: int = 200, timeout_seconds: int = 30) -> list[dict]:
    issues: list[dict] = []
    start_at = 0
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        while True:
            response = await client.get(
                f"{base_url.rstrip('/')}/rest/api/3/search",
                params={"jql": jql, "startAt": start_at, "maxResults": min(100, max_results - len(issues)),
                        "fields": "summary,description,status,priority,issuetype,created,updated"},
                headers=_auth_header(email, api_token),
            )
            if response.status_code in (401, 403):
                raise JiraAuthError("Jira rejected the credentials or denied access to this project/JQL.")
            response.raise_for_status()
            payload = response.json()
            batch = payload.get("issues", [])
            issues.extend(batch)
            start_at += len(batch)
            if not batch or len(issues) >= max_results or start_at >= payload.get("total", 0):
                break
    return issues


# Function: ingest_jira
async def ingest_jira(session, project_id: uuid.UUID, *, base_url: str, email: str, api_token: str, jql: str, max_results: int = 200) -> int:
    issues = await search_issues(base_url, email, api_token, jql, max_results)
    if not issues:
        return 0

    doc = SourceDocument(
        project_id=project_id, source_type="JIRA",
        connector_ref={"base_url": base_url, "jql": jql},
        filename=f"JIRA issues ({len(issues)} — {jql[:80]})",
        blob_uri=f"jira://{base_url}?jql={jql}", sha256="0" * 64,
        doc_class="AS_IS_DOC", status="INDEXED", ingested_at=datetime.now(timezone.utc),
    )
    session.add(doc)
    await session.flush()

    texts = [_issue_text(issue) for issue in issues]
    embeddings = await embed_texts(texts)
    for ordinal, (issue, text, embedding) in enumerate(zip(issues, texts, embeddings)):
        session.add(Chunk(
            source_document_id=doc.id, project_id=project_id, ordinal=ordinal,
            text=text, token_count=len(text.split()),
            locator={"issue_key": issue.get("key"), "issue_url": f"{base_url.rstrip('/')}/browse/{issue.get('key')}"},
            embedding=embedding, chunk_metadata={"doc_class": "AS_IS_DOC", "jira_id": issue.get("id")},
        ))
    await session.commit()
    return len(issues)


# Function: create_issue_from_requirement
async def create_issue_from_requirement(
    base_url: str, email: str, api_token: str, project_key: str, requirement: Requirement, issue_type: str = "Story",
) -> dict:
    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": f"[{requirement.req_id}] {requirement.title}",
            "description": {
                "type": "doc", "version": 1,
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": f"{requirement.statement}\n\nAcceptance criteria:\n" + "\n".join(f"- {ac}" for ac in requirement.acceptance_criteria)}],
                }],
            },
            "issuetype": {"name": issue_type},
        }
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(f"{base_url.rstrip('/')}/rest/api/3/issue", json=payload, headers=_auth_header(email, api_token))
        if response.status_code in (401, 403):
            raise JiraAuthError("Jira rejected the credentials or denied access to create issues in this project.")
        response.raise_for_status()
        return response.json()


# Function: comment_on_issue
async def comment_on_issue(base_url: str, email: str, api_token: str, issue_key: str, comment_text: str) -> None:
    payload = {"body": {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment_text}]}]}}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(f"{base_url.rstrip('/')}/rest/api/3/issue/{issue_key}/comment", json=payload, headers=_auth_header(email, api_token))
        if response.status_code in (401, 403):
            raise JiraAuthError("Jira rejected the credentials or denied access to comment on this issue.")
        response.raise_for_status()
