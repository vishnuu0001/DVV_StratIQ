# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: GitHub connector — new this pass. Read: clone + walk source files as legacy-code
# Date: 2026-06-24
# ---------------------------------------------------------------------------
"""GitHub connector — new this pass. Read: clone + walk source files as legacy-code
SourceDocuments (spec §4.2's tree-sitter chunking, see parsing/code.py). Write: open a
branch + PR with generated TestScript files. Uses PyGithub + GitPython, the same
libraries CodeAnalysis/core/github_fetcher.py already uses elsewhere in this repo.
"""
from __future__ import annotations

import hashlib
import shutil
import stat
import uuid
from datetime import datetime, timezone
from pathlib import Path

import git
from github import Github, GithubException

from traceforge.config import STORAGE_DIR
from traceforge.db.models import Chunk, SourceDocument, TestScript
from traceforge.indexing.embedder import embed_texts
from traceforge.parsing.code import SUPPORTED_CODE_EXTENSIONS, parse_code

_CLONE_DIR = STORAGE_DIR / "_github_clones"
_MAX_FILES = 200
_MAX_FILE_BYTES = 300_000


class GitHubAuthError(Exception):
    pass


# Function: _robust_rmtree
def _robust_rmtree(path: Path) -> None:
    # Function: _on_error
    def _on_error(func, p, _exc_info):
        try:
            import os
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except Exception:  # noqa: BLE001
            pass
    shutil.rmtree(path, onerror=_on_error)


# Function: _clone
def _clone(repo_url: str, token: str | None, dest: Path) -> None:
    if dest.exists():
        _robust_rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    clone_url = repo_url
    if token and repo_url.startswith("https://"):
        clone_url = repo_url.replace("https://", f"https://x-access-token:{token}@", 1)
    git.Repo.clone_from(clone_url, dest, depth=1)


# Function: _walk_source_files
def _walk_source_files(root: Path) -> list[Path]:
    files: list[Path] = []
    skip_dirs = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"}
    for path in root.rglob("*"):
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.is_file() and path.suffix in SUPPORTED_CODE_EXTENSIONS and path.stat().st_size <= _MAX_FILE_BYTES:
            files.append(path)
        if len(files) >= _MAX_FILES:
            break
    return files


# Function: ingest_github_repo
async def ingest_github_repo(session, project_id: uuid.UUID, *, repo_url: str, token: str | None = None, ref: str | None = None) -> int:
    repo_slug = repo_url.rstrip("/").split("/")[-1].removesuffix(".git")
    dest = _CLONE_DIR / f"{project_id}_{repo_slug}_{uuid.uuid4().hex[:8]}"
    try:
        _clone(repo_url, token, dest)
    except git.GitCommandError as exc:
        raise GitHubAuthError(f"Could not clone {repo_url}: {exc}") from exc

    files = _walk_source_files(dest)
    total_chunks = 0
    for file_path in files:
        try:
            code_chunks = parse_code(str(file_path))
        except Exception:  # noqa: BLE001 — one bad file must not abort the whole repo
            continue
        if not code_chunks:
            continue

        rel_path = str(file_path.relative_to(dest))
        content = file_path.read_bytes()
        doc = SourceDocument(
            project_id=project_id, source_type="GIT_REPO",
            connector_ref={"repo_url": repo_url, "ref": ref, "path": rel_path},
            filename=rel_path, blob_uri=f"{repo_url}#{rel_path}",
            sha256=hashlib.sha256(content).hexdigest(),
            doc_class="LEGACY_CODE", status="INDEXED", ingested_at=datetime.now(timezone.utc),
        )
        session.add(doc)
        await session.flush()

        texts = [c.text for c in code_chunks]
        embeddings = await embed_texts(texts)
        for ordinal, (chunk, embedding) in enumerate(zip(code_chunks, embeddings)):
            session.add(Chunk(
                source_document_id=doc.id, project_id=project_id, ordinal=ordinal,
                text=chunk.text, token_count=chunk.token_count, locator=chunk.locator,
                embedding=embedding, chunk_metadata={"doc_class": "LEGACY_CODE"},
            ))
        total_chunks += len(code_chunks)

    await session.commit()
    _robust_rmtree(dest)
    return total_chunks


# Function: open_pr_with_scripts
def open_pr_with_scripts(
    *, repo_full_name: str, token: str, base_branch: str, new_branch: str,
    scripts: list[TestScript], pr_title: str, pr_body: str,
) -> str:
    """Creates a branch, commits every TestScript at its file_path, opens a PR.
    Synchronous (PyGithub has no async client) — call via asyncio.to_thread."""
    gh = Github(token)
    try:
        repo = gh.get_repo(repo_full_name)
        base_ref = repo.get_git_ref(f"heads/{base_branch}")
        try:
            repo.get_git_ref(f"heads/{new_branch}")
            raise GitHubAuthError(f"Branch {new_branch} already exists.")
        except GithubException as exc:
            if exc.status != 404:
                raise
        repo.create_git_ref(ref=f"refs/heads/{new_branch}", sha=base_ref.object.sha)

        for script in scripts:
            try:
                existing = repo.get_contents(script.file_path, ref=new_branch)
                repo.update_file(script.file_path, f"Update {script.ts_id}", script.code, existing.sha, branch=new_branch)
            except GithubException as exc:
                if exc.status != 404:
                    raise
                repo.create_file(script.file_path, f"Add {script.ts_id}", script.code, branch=new_branch)

        pr = repo.create_pull(title=pr_title, body=pr_body, head=new_branch, base=base_branch)
        return pr.html_url
    except GithubException as exc:
        if exc.status in (401, 403):
            raise GitHubAuthError("GitHub rejected the token or denied access to this repository.") from exc
        raise
