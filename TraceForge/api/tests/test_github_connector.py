# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: GitHub connector — no live repo/token available this pass (per the user's answer),
# Date: 2026-04-18
# ---------------------------------------------------------------------------
"""GitHub connector — no live repo/token available this pass (per the user's answer),
so this verifies open_pr_with_scripts's real PyGithub call shape against mocks, not a
live clone/PR round-trip."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from github import GithubException

from traceforge.connectors.github import GitHubAuthError, open_pr_with_scripts


# Function: _make_script
def _make_script(ts_id: str, file_path: str, code: str) -> MagicMock:
    script = MagicMock()
    script.ts_id, script.file_path, script.code = ts_id, file_path, code
    return script


# Function: test_open_pr_creates_branch_commits_files_and_opens_pr
def test_open_pr_creates_branch_commits_files_and_opens_pr():
    scripts = [_make_script("TS-0001", "tests/e2e/order.spec.ts", "test('x', async () => {})")]

    mock_repo = MagicMock()
    mock_base_ref = MagicMock()
    mock_base_ref.object.sha = "abc123"
    mock_repo.get_git_ref.side_effect = [mock_base_ref, GithubException(404, {}, {})]  # base ref ok, new branch doesn't exist yet
    mock_repo.get_contents.side_effect = GithubException(404, {}, {})  # file doesn't exist yet -> create, not update
    mock_pr = MagicMock()
    mock_pr.html_url = "https://github.com/acme/repo/pull/7"
    mock_repo.create_pull.return_value = mock_pr

    mock_gh = MagicMock()
    mock_gh.get_repo.return_value = mock_repo

    with patch("traceforge.connectors.github.Github", return_value=mock_gh):
        url = open_pr_with_scripts(
            repo_full_name="acme/repo", token="ghp_x", base_branch="main", new_branch="traceforge/tests-1",
            scripts=scripts, pr_title="TraceForge tests", pr_body="Generated tests",
        )

    assert url == "https://github.com/acme/repo/pull/7"
    mock_repo.create_git_ref.assert_called_once_with(ref="refs/heads/traceforge/tests-1", sha="abc123")
    mock_repo.create_file.assert_called_once()
    create_call = mock_repo.create_file.call_args
    assert create_call.args[0] == "tests/e2e/order.spec.ts"
    assert create_call.kwargs["branch"] == "traceforge/tests-1"
    mock_repo.create_pull.assert_called_once()


# Function: test_open_pr_updates_existing_file_instead_of_creating
def test_open_pr_updates_existing_file_instead_of_creating():
    scripts = [_make_script("TS-0002", "tests/e2e/order.spec.ts", "test('y', async () => {})")]

    mock_repo = MagicMock()
    mock_base_ref = MagicMock()
    mock_base_ref.object.sha = "abc123"
    mock_repo.get_git_ref.side_effect = [mock_base_ref, GithubException(404, {}, {})]
    existing_file = MagicMock(sha="def456")
    mock_repo.get_contents.return_value = existing_file
    mock_pr = MagicMock(html_url="https://github.com/acme/repo/pull/8")
    mock_repo.create_pull.return_value = mock_pr

    mock_gh = MagicMock()
    mock_gh.get_repo.return_value = mock_repo

    with patch("traceforge.connectors.github.Github", return_value=mock_gh):
        open_pr_with_scripts(
            repo_full_name="acme/repo", token="ghp_x", base_branch="main", new_branch="traceforge/tests-2",
            scripts=scripts, pr_title="t", pr_body="b",
        )

    mock_repo.update_file.assert_called_once()
    mock_repo.create_file.assert_not_called()


# Function: test_open_pr_raises_github_auth_error_on_403
def test_open_pr_raises_github_auth_error_on_403():
    mock_repo = MagicMock()
    mock_repo.get_git_ref.side_effect = GithubException(403, {}, {})
    mock_gh = MagicMock()
    mock_gh.get_repo.return_value = mock_repo

    with patch("traceforge.connectors.github.Github", return_value=mock_gh):
        with pytest.raises(GitHubAuthError):
            open_pr_with_scripts(
                repo_full_name="acme/repo", token="bad", base_branch="main", new_branch="x",
                scripts=[_make_script("TS-1", "a.ts", "x")], pr_title="t", pr_body="b",
            )
