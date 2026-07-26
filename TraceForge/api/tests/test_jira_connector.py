# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: JIRA connector — no live instance available this pass (per the user's answer), so
# Date: 2025-07-30
# ---------------------------------------------------------------------------
"""JIRA connector — no live instance available this pass (per the user's answer), so
this verifies the real HTTP-call shape (URL, auth, payload) against mocked responses,
not a live round-trip."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from traceforge.connectors.jira import JiraAuthError, _adf_to_text, create_issue_from_requirement, search_issues


# Function: _mock_response
def _mock_response(status_code: int, json_data: dict) -> MagicMock:
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        resp.raise_for_status.side_effect = httpx.HTTPStatusError("error", request=MagicMock(), response=resp)
    return resp


# Function: test_search_issues_paginates_and_uses_basic_auth
async def test_search_issues_paginates_and_uses_basic_auth():
    page1 = _mock_response(200, {"issues": [{"key": "PROJ-1"}], "total": 2})
    page2 = _mock_response(200, {"issues": [{"key": "PROJ-2"}], "total": 2})

    with patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=[page1, page2])) as mock_get:
        issues = await search_issues("https://acme.atlassian.net", "user@acme.com", "token123", "project = PROJ")

    assert [i["key"] for i in issues] == ["PROJ-1", "PROJ-2"]
    assert mock_get.call_count == 2
    first_call = mock_get.call_args_list[0]
    assert first_call.args[0] == "https://acme.atlassian.net/rest/api/3/search"
    assert "Authorization" in first_call.kwargs["headers"]
    assert first_call.kwargs["headers"]["Authorization"].startswith("Basic ")


# Function: test_search_issues_raises_jira_auth_error_on_401
async def test_search_issues_raises_jira_auth_error_on_401():
    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=_mock_response(401, {}))):
        with pytest.raises(JiraAuthError):
            await search_issues("https://acme.atlassian.net", "user@acme.com", "bad-token", "project = PROJ")


# Function: test_create_issue_from_requirement_posts_correct_payload
async def test_create_issue_from_requirement_posts_correct_payload():
    requirement = MagicMock(req_id="REQ-0042", title="Reject over-limit orders", statement="The system shall reject orders exceeding the credit limit.", acceptance_criteria=["Order rejected", "Error shown"])
    created = _mock_response(201, {"id": "10001", "key": "PROJ-99"})

    with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=created)) as mock_post:
        result = await create_issue_from_requirement("https://acme.atlassian.net", "user@acme.com", "token123", "PROJ", requirement)

    assert result["key"] == "PROJ-99"
    call = mock_post.call_args
    assert call.args[0] == "https://acme.atlassian.net/rest/api/3/issue"
    payload = call.kwargs["json"]
    assert payload["fields"]["project"]["key"] == "PROJ"
    assert "REQ-0042" in payload["fields"]["summary"]


# Function: test_adf_to_text_extracts_nested_text_nodes
def test_adf_to_text_extracts_nested_text_nodes():
    adf = {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Hello"}, {"type": "text", "text": "world"}]}]}
    assert _adf_to_text(adf) == "Hello world"


# Function: test_adf_to_text_handles_none_and_plain_string
def test_adf_to_text_handles_none_and_plain_string():
    assert _adf_to_text(None) == ""
    assert _adf_to_text("already plain") == "already plain"
