# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Clones or updates GitHub repositories and gathers repository-level metadata
# Date: 2026-02-24
# ---------------------------------------------------------------------------
"""
github_fetcher.py
-----------------
Clones or updates GitHub repositories and gathers repository-level metadata
(languages, contributors, release cadence, open issues) used by the
Business Impact and Cloud Maturity metrics.
"""
from __future__ import annotations

import logging
import os
import shutil
import stat
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import git
from github import Github, GithubException, RateLimitExceededException

from config.settings import CLONE_DIR, GITHUB_TOKEN

logger = logging.getLogger(__name__)

_longpaths_configured = False


# Function: _ensure_longpaths_enabled
def _ensure_longpaths_enabled() -> None:
    """Enable Windows long paths in git's global config — once per process,
    not once per clone/pull. Previously this spawned a `git config --global`
    subprocess on every single call to _clone_or_pull, which for an
    organisation-wide scan means one redundant process spawn per repo (the
    setting is a persistent global config value; it does not need re-applying
    once it has already been set for this process)."""
    global _longpaths_configured
    if _longpaths_configured:
        return
    import subprocess as _subp
    _subp.run(["git", "config", "--global", "core.longpaths", "true"], capture_output=True)
    _longpaths_configured = True


# Function: _robust_rmtree
def _robust_rmtree(path: Path) -> None:
    """Delete a directory tree on Windows, stripping read-only bits first.

    Plain ``shutil.rmtree(ignore_errors=True)`` silently fails on Windows
    when ``.git`` directories contain read-only files, leaving the folder
    behind and causing ``git clone`` to abort with exit-code 128.
    """
    # Function: _on_error
    def _on_error(func, p, _exc_info):
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except Exception:  # noqa: BLE001
            pass

    shutil.rmtree(path, onerror=_on_error)


@dataclass
class RepoMetadata:
    """Repository-level information collected from the GitHub API."""
    full_name:        str
    url:              str
    default_branch:   str
    language:         Optional[str]
    languages:        Dict[str, int]     = field(default_factory=dict)
    stars:            int = 0
    forks:            int = 0
    open_issues:      int = 0
    contributors:     int = 0
    releases:         int = 0
    last_commit_days: int = 0           # days since last commit
    topics:           List[str]         = field(default_factory=list)
    has_ci:           bool = False
    has_dockerfile:   bool = False
    has_kubernetes:   bool = False
    description:      str = ""
    local_path:       Path = field(default=Path("."))


class GitHubFetcher:
    """
    Fetches a GitHub repository – either a single repo or every repo in an
    organisation – clones it locally, and returns rich RepoMetadata objects.
    """

    # Function: __init__
    def __init__(self, token: str = GITHUB_TOKEN):
        self._token = (token or "").strip()
        self._gh = Github(self._token) if self._token else Github()
        self._anon_gh = Github()
        self._token_invalid = False

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    # Function: fetch_repo
    def fetch_repo(self, repo_url_or_name: str) -> RepoMetadata:
        """
        Fetch a single repository by its GitHub URL or ``owner/repo`` slug.

        Returns a :class:`RepoMetadata` instance with the repository cloned
        into ``CLONE_DIR/<owner>/<repo>``.
        """
        slug = self._slug_from_input(repo_url_or_name)
        logger.info("Fetching repository: %s", slug)
        gh_repo = self._get_gh_repo(slug)
        meta    = self._build_metadata(gh_repo)
        meta.local_path = self._clone_or_pull(
            slug,
            gh_repo.clone_url,
            use_token=bool(getattr(gh_repo, "private", False) and self._token and not self._token_invalid),
        )
        return meta

    # Function: fetch_organisation
    def fetch_organisation(self, org_name: str,
                           limit: int = 50) -> List[RepoMetadata]:
        """
        Fetch all (up to *limit*) non-fork repositories in a GitHub organisation.
        """
        logger.info("Fetching organisation: %s (limit=%d)", org_name, limit)
        try:
            org   = self._get_gh_org(org_name)
            repos = [r for r in org.get_repos(type="public") if not r.fork]
        except RuntimeError as exc:
            logger.error("Cannot access organisation %s: %s", org_name, exc)
            return []

        # Each repo's fetch (GitHub API metadata calls + git clone/pull) is fully
        # independent I/O-bound work, so this is a prime candidate for
        # concurrency — previously it ran strictly one repo at a time (4+ GitHub
        # API calls plus a blocking clone per repo, sequentially), which for an
        # organisation scan at the frontend's default limit=20 meant 20 serial
        # round-trip batches with zero overlap. Result order doesn't matter to
        # either caller (api/server.py just enumerates for progress reporting),
        # so returning in completion order rather than input order is safe.
        # Worker count matches the pool size already used elsewhere in this
        # codebase for similar I/O-bound fan-out (core/analyzer.py, services/ai_analysis.py).
        results: List[RepoMetadata] = []
        target_repos = repos[:limit]

        # Function: _fetch_one
        def _fetch_one(gh_repo):
            meta = self._build_metadata(gh_repo)
            meta.local_path = self._clone_or_pull(
                gh_repo.full_name,
                gh_repo.clone_url,
                use_token=bool(getattr(gh_repo, "private", False) and self._token and not self._token_invalid),
            )
            return meta

        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = {pool.submit(_fetch_one, gh_repo): gh_repo for gh_repo in target_repos}
            for future in as_completed(futures):
                gh_repo = futures[future]
                try:
                    results.append(future.result())
                except Exception as exc:   # noqa: BLE001
                    logger.warning("Skipping %s: %s", gh_repo.full_name, exc)
        return results

    # ──────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _slug_from_input
    def _slug_from_input(self, value: str) -> str:
        """Convert a full GitHub URL to an ``owner/repo`` slug."""
        value = value.rstrip("/")
        if value.startswith("http"):
            parts = value.split("github.com/")
            if len(parts) < 2:
                raise ValueError(f"Not a GitHub URL: {value}")
            slug = parts[1].removesuffix(".git")
        else:
            slug = value
        if slug.count("/") != 1:
            raise ValueError(f"Expected owner/repo format, got: {slug}")
        return slug

    # Function: _is_bad_credentials
    @staticmethod
    def _is_bad_credentials(exc: GithubException) -> bool:
        status = getattr(exc, "status", None)
        payload = getattr(exc, "data", None)
        message = ""
        if isinstance(payload, dict):
            message = str(payload.get("message", ""))
        if not message:
            message = str(exc)
        return status == 401 and "bad credentials" in message.lower()

    # Function: _mark_token_invalid
    def _mark_token_invalid(self) -> None:
        if self._token_invalid:
            return
        self._token_invalid = True
        logger.warning(
            "Configured GITHUB_TOKEN was rejected by GitHub. Public repositories will be fetched anonymously."
        )

    # Function: _run_with_retries
    def _run_with_retries(self, action, rate_limit_client: Github, subject: str):
        for _attempt in range(3):
            try:
                return action()
            except RateLimitExceededException:
                reset = rate_limit_client.get_rate_limit().core.reset.timestamp()
                wait = max(0, reset - time.time()) + 5
                logger.warning("Rate-limited while fetching %s. Sleeping %.0fs …", subject, wait)
                time.sleep(wait)
            except GithubException:
                raise
        raise RuntimeError(f"GitHub rate-limit exceeded after 3 retries for {subject}")

    # Function: _get_gh_repo
    def _get_gh_repo(self, slug: str):
        """Return the PyGithub repository object, handling rate-limits."""
        if self._token and not self._token_invalid:
            try:
                return self._run_with_retries(lambda: self._gh.get_repo(slug), self._gh, slug)
            except GithubException as exc:
                if not self._is_bad_credentials(exc):
                    raise RuntimeError(f"GitHub API error for {slug}: {exc}") from exc
                self._mark_token_invalid()

        try:
            repo = self._run_with_retries(lambda: self._anon_gh.get_repo(slug), self._anon_gh, slug)
            logger.info("Fetched public repository %s without GitHub authentication", slug)
            return repo
        except GithubException as exc:
            raise RuntimeError(
                f"GitHub API error for {slug}: repository is not accessible anonymously or does not exist."
            ) from exc

    # Function: _get_gh_org
    def _get_gh_org(self, org_name: str):
        """Return the PyGithub organization object, with anonymous fallback for public orgs."""
        if self._token and not self._token_invalid:
            try:
                return self._run_with_retries(lambda: self._gh.get_organization(org_name), self._gh, org_name)
            except GithubException as exc:
                if not self._is_bad_credentials(exc):
                    raise RuntimeError(f"GitHub API error for organisation {org_name}: {exc}") from exc
                self._mark_token_invalid()

        try:
            org = self._run_with_retries(lambda: self._anon_gh.get_organization(org_name), self._anon_gh, org_name)
            logger.info("Fetched public organisation %s without GitHub authentication", org_name)
            return org
        except GithubException as exc:
            raise RuntimeError(
                f"GitHub API error for organisation {org_name}: organisation is not accessible anonymously or does not exist."
            ) from exc

    # Function: _build_metadata
    def _build_metadata(self, gh_repo) -> RepoMetadata:
        """Populate a RepoMetadata from a PyGithub Repository object."""
        # Basic info
        try:
            lang_bytes = dict(gh_repo.get_languages())
        except Exception:   # noqa: BLE001
            lang_bytes = {}

        try:
            contributors = gh_repo.get_contributors().totalCount
        except Exception:   # noqa: BLE001
            contributors = 0

        try:
            releases = gh_repo.get_releases().totalCount
        except Exception:   # noqa: BLE001
            releases = 0

        # Days since last commit
        try:
            last_pushed = gh_repo.pushed_at
            last_commit_days = (
                (time.time() - last_pushed.timestamp()) / 86_400
            ) if last_pushed else 9999
        except Exception:   # noqa: BLE001
            last_commit_days = 9999

        # Cloud readiness signals from repo metadata
        topics      = list(gh_repo.get_topics())
        has_ci      = any(t in topics for t in ("ci", "cd", "devops", "github-actions"))
        has_docker  = "docker" in topics or "dockerfile" in topics
        has_k8s     = any(t in topics for t in ("kubernetes", "k8s", "helm"))

        return RepoMetadata(
            full_name        = gh_repo.full_name,
            url              = gh_repo.html_url,
            default_branch   = gh_repo.default_branch or "main",
            language         = gh_repo.language,
            languages        = lang_bytes,
            stars            = gh_repo.stargazers_count,
            forks            = gh_repo.forks_count,
            open_issues      = gh_repo.open_issues_count,
            contributors     = contributors,
            releases         = releases,
            last_commit_days = int(last_commit_days),
            topics           = topics,
            has_ci           = has_ci,
            has_dockerfile   = has_docker,
            has_kubernetes   = has_k8s,
            description      = gh_repo.description or "",
        )

    # Function: _clone_or_pull
    def _clone_or_pull(self, slug: str, clone_url: str, use_token: bool = False) -> Path:
        """Clone if not present; pull latest if already cloned."""
        owner, name  = slug.split("/", 1)
        local_path   = CLONE_DIR / owner / name

        # Inject token into HTTPS URL for private repos
        if use_token and self._token and "github.com" in clone_url:
            clone_url = clone_url.replace(
                "https://", f"https://{self._token}@"
            )

        # Enable Windows long paths before any git subprocess is spawned (once per process).
        _ensure_longpaths_enabled()

        # Shallow-clone kwargs — depth=1 avoids pulling the full history of
        # very large repos (e.g. Elasticsearch). 
        # IMPORTANT: do NOT pass 'env' here — GitPython forwards it as a
        # *complete* replacement of os.environ, which strips PATH and causes
        # the git subprocess to fail silently on Windows.
        clone_kwargs: dict = {
            "depth": 1,
            "single_branch": True,
        }

        # Function: _do_clone
        def _do_clone() -> None:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            git.Repo.clone_from(clone_url, local_path, **clone_kwargs)
            # Verify the clone actually produced files; an empty directory
            # means git failed silently (network / permissions / long-path).
            if not any(local_path.iterdir()):
                raise RuntimeError(
                    f"Clone of {slug} produced an empty directory. "
                    "Check network connectivity and ensure core.longpaths=true."
                )

        if not local_path.exists():
            logger.info("Cloning: %s → %s", slug, local_path)
            _do_clone()
            return local_path

        repo, is_valid = self._open_existing_repo(local_path)
        if is_valid:
            self._pull_or_reclone(repo, local_path, clone_url, use_token, slug, _do_clone)
        else:
            # Folder exists but not a valid repo — wipe and re-clone
            logger.warning("Invalid/empty repo at %s; re-cloning …", local_path)
            self._wipe_and_reclone(local_path, _do_clone)

        return local_path

    # Function: _open_existing_repo
    @staticmethod
    def _open_existing_repo(local_path: Path):
        """Check if `local_path` is a valid, non-bare git repo. Returns (repo, is_valid)."""
        try:
            repo = git.Repo(local_path)
            return repo, not repo.bare
        except (git.InvalidGitRepositoryError, git.NoSuchPathError, Exception):
            return None, False

    # Function: _wipe_and_reclone
    @staticmethod
    def _wipe_and_reclone(local_path: Path, do_clone) -> None:
        _robust_rmtree(local_path)
        if not local_path.exists():
            do_clone()
        else:
            logger.error("Could not remove %s; skipping re-clone", local_path)

    # Function: _pull_or_reclone
    def _pull_or_reclone(self, repo, local_path: Path, clone_url: str, use_token: bool, slug: str, do_clone) -> None:
        try:
            if not use_token:
                try:
                    repo.remotes.origin.set_url(clone_url)
                except Exception:  # noqa: BLE001
                    pass
            logger.info("Pulling latest: %s", slug)
            repo.remotes.origin.pull()
        except Exception as exc:   # noqa: BLE001
            logger.warning("Pull failed (%s); re-cloning …", exc)
            self._wipe_and_reclone(local_path, do_clone)
