# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §5 Agent 4 (Script Generator) output — real this pass, plus the GitHub write-back
# Date: 2025-09-21
# ---------------------------------------------------------------------------
"""§5 Agent 4 (Script Generator) output — real this pass, plus the GitHub write-back
(open a PR with the generated scripts) that's new scope beyond the original spec."""
from __future__ import annotations

import asyncio
import io
import json
import re
import uuid
import zipfile
from pathlib import PurePosixPath

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.agents.script_gen.validation import validate_typescript
from traceforge.auth import current_user
from traceforge.connectors.github import GitHubAuthError, open_pr_with_scripts
from traceforge.db.models import AuditEvent, Project, TestScript
from traceforge.db.session import get_session
from traceforge.schemas.script import TestScriptOut, TestScriptPatch

router = APIRouter(prefix="/api/v1", tags=["scripts"])


class GitHubPrRequest(BaseModel):
    repo_full_name: str
    token: str
    base_branch: str = "main"
    new_branch: str | None = None
    test_script_ids: list[uuid.UUID] | None = None  # None = all APPROVED scripts for the project


# Function: _download_name
def _download_name(file_path: str, fallback: str) -> str:
    name = PurePosixPath((file_path or "").replace("\\", "/")).name
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return safe or fallback


# Function: _suite_path
def _suite_path(script: TestScript) -> str:
    parts = PurePosixPath((script.file_path or "").replace("\\", "/")).parts
    if not parts or ".." in parts or any(part in {"", ".", "/"} for part in parts):
        return f"tests/e2e/{script.ts_id.lower()}.spec.ts"
    return "/".join(parts)


# Function: list_scripts
@router.get("/projects/{project_id}/scripts", response_model=list[TestScriptOut])
async def list_scripts(
    project_id: uuid.UUID, target: str | None = None, compiles: bool | None = None,
    session: AsyncSession = Depends(get_session), user: dict = Depends(current_user),
):
    stmt = select(TestScript).where(
        TestScript.project_id == project_id,
        TestScript.target == "PLAYWRIGHT_TS",
    )
    if target:
        stmt = stmt.where(TestScript.target == target)
    if compiles is not None:
        stmt = stmt.where(TestScript.compiles == compiles)
    result = await session.execute(stmt.order_by(TestScript.ts_id))
    return list(result.scalars().all())


# Function: download_script
@router.get("/scripts/{ts_id}/download")
async def download_script(
    ts_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(current_user),
):
    script = await session.get(TestScript, ts_id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    filename = _download_name(script.file_path, f"{script.ts_id.lower()}.spec.ts")
    return Response(
        content=script.code.encode("utf-8"),
        media_type="text/typescript; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# Function: download_project_scripts
@router.get("/projects/{project_id}/scripts/download")
async def download_project_scripts(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(current_user),
):
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    scripts = list((await session.scalars(
        select(TestScript)
        .where(TestScript.project_id == project_id, TestScript.target == "PLAYWRIGHT_TS")
        .order_by(TestScript.ts_id)
    )).all())
    if not scripts:
        raise HTTPException(status_code=404, detail="No Playwright scripts are available to download.")

    package_json = {
        "name": f"{project.key.lower()}-playwright-tests",
        "private": True,
        "scripts": {
            "test": "playwright test",
            "test:headed": "playwright test --headed",
            "test:debug": "playwright test --debug",
            "report": "playwright show-report",
        },
        "devDependencies": {"@playwright/test": "^1.61.1", "typescript": "^7.0.2"},
    }
    playwright_config = """import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: [['html', { open: 'never' }], ['junit', { outputFile: 'test-results/junit.xml' }]],
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:3000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});
"""
    readme = f"""# {project.name} Playwright test suite

Generated by TraceForge with requirement and test-case traceability.

1. Run `npm install`
2. Run `npx playwright install --with-deps chromium`
3. Set `PLAYWRIGHT_BASE_URL` to the test environment
4. Optionally set `TRACEFORGE_LOCATORS` to a JSON map of semantic locator keys to reviewed selectors
5. Run `npm test`

The suite contains {len(scripts)} Playwright TypeScript specifications. Review environment
credentials, locator mappings, and test data before running against any shared environment.
"""
    manifest = [
        {
            "ts_id": script.ts_id,
            "test_case_id": str(script.test_case_id),
            "path": _suite_path(script),
            "compiles": script.compiles,
            "version": script.version,
        }
        for script in scripts
    ]

    archive = io.BytesIO()
    used_paths: set[str] = set()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for script in scripts:
            path = _suite_path(script)
            if path in used_paths:
                stem = PurePosixPath(path).stem
                path = str(PurePosixPath(path).with_name(f"{stem}_{script.ts_id.lower()}.spec.ts"))
            used_paths.add(path)
            bundle.writestr(path, script.code)
        bundle.writestr("package.json", json.dumps(package_json, indent=2) + "\n")
        bundle.writestr("playwright.config.ts", playwright_config)
        bundle.writestr("README.md", readme)
        bundle.writestr("traceforge-manifest.json", json.dumps(manifest, indent=2) + "\n")

    safe_key = re.sub(r"[^A-Za-z0-9._-]+", "_", project.key).strip("._") or "traceforge"
    return Response(
        content=archive.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{safe_key}-playwright-tests.zip"'},
    )


# Function: patch_script
@router.patch("/scripts/{ts_id}", response_model=TestScriptOut)
async def patch_script(ts_id: uuid.UUID, body: TestScriptPatch, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    script = await session.get(TestScript, ts_id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    before = {"status": script.status, "compiles": script.compiles}
    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(script, field, value)
    if "code" in updates:
        script.version += 1
        compiles, output = await validate_typescript(script.code)
        script.compiles, script.validation_output = compiles, output
    session.add(AuditEvent(project_id=script.project_id, actor=user.get("username", "unknown"), action="SCRIPT_EDITED",
                            entity_type="TestScript", entity_id=str(script.id), before=before, after=updates))
    await session.commit()
    await session.refresh(script)
    return script


# Function: validate_script
@router.post("/scripts/{ts_id}/validate", response_model=TestScriptOut)
async def validate_script(ts_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    script = await session.get(TestScript, ts_id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    compiles, output = await validate_typescript(script.code)
    script.compiles, script.validation_output = compiles, output
    await session.commit()
    await session.refresh(script)
    return script


# Function: open_github_pr
@router.post("/projects/{project_id}/scripts/github-pr")
async def open_github_pr(project_id: uuid.UUID, body: GitHubPrRequest, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    """Credentials (the PAT) are used for this request only and are not stored."""
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    stmt = select(TestScript).where(TestScript.project_id == project_id, TestScript.status == "APPROVED")
    if body.test_script_ids:
        stmt = stmt.where(TestScript.id.in_(body.test_script_ids))
    scripts = list((await session.execute(stmt)).scalars().all())
    if not scripts:
        raise HTTPException(status_code=422, detail="No APPROVED test scripts to include in the PR.")

    new_branch = body.new_branch or f"traceforge/{project.key.lower()}-tests-{uuid.uuid4().hex[:8]}"
    try:
        pr_url = await asyncio.to_thread(
            open_pr_with_scripts, repo_full_name=body.repo_full_name, token=body.token, base_branch=body.base_branch,
            new_branch=new_branch, scripts=scripts, pr_title=f"TraceForge: generated test scripts for {project.key}",
            pr_body=f"Auto-generated by TraceForge from {len(scripts)} approved test case(s). Review before merging.",
        )
    except GitHubAuthError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    session.add(AuditEvent(project_id=project_id, actor=user.get("username", "unknown"), action="GITHUB_PR_OPENED",
                            entity_type="TestScript", entity_id=str(project_id), after={"pr_url": pr_url, "script_count": len(scripts)}))
    await session.commit()
    return {"pr_url": pr_url, "scripts_included": len(scripts)}
