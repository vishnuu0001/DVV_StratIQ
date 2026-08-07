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
from traceforge.agents.script_gen.playwright import _parse_tc_metadata, _verified_automation_status
from traceforge.agents.script_gen.semantic_runtime import (
    PLAYWRIGHT_RUNTIME_MODULE,
    RUNTIME_REGION_END,
    RUNTIME_REGION_START,
)
from traceforge.auth import current_user
from traceforge.connectors.github import GitHubAuthError, open_pr_with_scripts
from traceforge.db.models import AuditEvent, Project, TestCase, TestScript
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
    approved_cases = list((await session.scalars(
        select(TestCase)
        .where(TestCase.project_id == project_id, TestCase.status == "APPROVED")
        .order_by(TestCase.tc_id)
    )).all())
    if not approved_cases:
        raise HTTPException(status_code=409, detail="No APPROVED test cases are available for an automation manifest.")
    scripts_by_case = {script.test_case_id: script for script in scripts}
    ready_cases = [
        case for case in approved_cases
        if _verified_automation_status(case, _parse_tc_metadata(case))[0] == "READY_FOR_UI_AUTOMATION"
    ]
    missing = [case.tc_id for case in ready_cases if case.id not in scripts_by_case]
    stale = [
        case.tc_id for case in ready_cases
        if case.id in scripts_by_case and scripts_by_case[case.id].upstream_tc_hash != case.content_hash
    ]
    if missing or stale:
        details = []
        if missing:
            details.append(f"missing scripts: {', '.join(missing[:20])}{'...' if len(missing) > 20 else ''}")
        if stale:
            details.append(f"stale scripts: {', '.join(stale[:20])}{'...' if len(stale) > 20 else ''}")
        raise HTTPException(
            status_code=409,
            detail="Playwright bundle completeness check failed; " + "; ".join(details),
        )
    scripts = [scripts_by_case[case.id] for case in ready_cases]
    test_cases = {
        case.id: case for case in approved_cases
    }

    package_json = {
        "name": f"{project.key.lower()}-playwright-tests",
        "private": True,
        "scripts": {
            "test": "playwright test",
            "test:headed": "playwright test --headed",
            "test:debug": "playwright test --debug",
            "test:blocked": "playwright test --grep AUTOMATION_BLOCKED",
            "report": "playwright show-report",
        },
        "devDependencies": {"@playwright/test": "^1.61.1", "typescript": "^7.0.2"},
    }

    total = len(approved_cases)
    blocked_count = total - len(ready_cases)
    skipped_count = 0

    playwright_config = f"""\
import {{ defineConfig, devices }} from '@playwright/test';

/**
 * TraceForge-generated Playwright configuration for {project.name}.
 *
 * IMPORTANT BEFORE RUNNING:
 * 1. Set PLAYWRIGHT_BASE_URL to your test environment URL.
 * 2. Populate TRACEFORGE_LOCATORS with a JSON map of business field names to stable selectors.
 * 3. Implement authentication in tests/fixtures/auth.fixture.ts.
 * 4. Resolve all [EXECUTION DETAIL BLOCKED] markers in the test steps.
 *
 * Automation readiness: {total - blocked_count}/{total} cases are not blocked.
 * {blocked_count} cases are AUTOMATION_BLOCKED — they are test.skip() and will not run.
 */
export default defineConfig({{
  testDir: './tests/e2e',
  /* fullyParallel is intentionally false — generated tests may share balances, stock,
     production records, warehouse inventory, deliveries, and invoice records.
     Enable only when worker-isolated test data is provisioned. */
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: [
    ['html', {{ open: 'never' }}],
    ['junit', {{ outputFile: 'test-results/junit.xml' }}],
    ['list'],
  ],
  use: {{
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:3000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    /* storageState: 'tests/fixtures/storage-states/order-entry.json', */
  }},
  projects: [
    {{ name: 'chromium', use: {{ ...devices['Desktop Chrome'] }} }},
  ],
}});
"""

    tsconfig = """\
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "moduleResolution": "node",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "strict": false,
    "baseUrl": "."
  },
  "include": ["tests/**/*.ts"]
}
"""

    env_example = f"""\
# Copy to .env and fill in real values before running tests.
# Never commit real credentials to source control.

# Required: URL of the test environment
PLAYWRIGHT_BASE_URL=http://localhost:3000

# Required: JSON map of business field names to stable CSS/testId selectors.
# Example:
# TRACEFORGE_LOCATORS={{"Product Code Field": "[data-testid=product-code]", "Order Submit": "[data-testid=submit-order]"}}
TRACEFORGE_LOCATORS=

# Required: map each reviewed expected-result string to a field/status selector.
# Body-wide text assertions are intentionally unsupported.
TRACEFORGE_ASSERTIONS=

# Optional: Override default correlation ID prefix for test data
TRACEFORGE_TEST_VALUE=

# Optional: Path to auth storage state (see tests/fixtures/auth.fixture.ts)
PLAYWRIGHT_AUTH_STATE=tests/fixtures/storage-states/order-entry.json
"""

    auth_fixture = """\
/**
 * tests/fixtures/auth.fixture.ts
 *
 * Authentication fixture for TraceForge-generated tests.
 *
 * SETUP REQUIRED: Implement the login flow for each role used in the test suite.
 * The roles required for this scenario are:
 *   - Order Entry Clerk
 *   - Production Supervisor
 *   - Quality Technician
 *   - Quality Approver
 *   - Warehouse Operator
 *   - Outbound Logistics Coordinator
 *   - Billing Clerk
 *   - Finance Approver
 *
 * Recommended approach: Use Playwright storage states so authentication
 * is performed once and reused across tests.
 *
 * See: https://playwright.dev/docs/auth
 */
import { test as base, type Page } from '@playwright/test';

export type UserRole =
  | 'order-entry'
  | 'production'
  | 'quality-technician'
  | 'quality-approver'
  | 'warehouse'
  | 'outbound'
  | 'billing'
  | 'finance';

export type AuthFixtures = {
  /** Authenticated page for the given role. Replace stub with real login logic. */
  loginAs: (role: UserRole) => Promise<Page>;
};

export const test = base.extend<AuthFixtures>({
  loginAs: async ({ page }, use) => {
    await use(async (role: UserRole) => {
      // TODO: Implement real authentication for each role.
      // Example with storage state:
      //   await page.context().addCookies([...]);
      //   await page.goto(BASE_URL);
      //
      // Or use page.goto() + form fill:
      //   await page.goto(`${BASE_URL}/login`);
      //   await page.getByLabel('Username').fill(process.env[`${role.toUpperCase()}_USER`] ?? '');
      //   await page.getByLabel('Password').fill(process.env[`${role.toUpperCase()}_PASS`] ?? '');
      //   await page.getByRole('button', { name: 'Sign in' }).click();
      throw new Error(
        `Authentication not implemented for role: ${role}. ` +
        'Implement the login flow in tests/fixtures/auth.fixture.ts before running tests.'
      );
    });
  },
});

export { expect } from '@playwright/test';
"""

    test_data_fixture = """\
/**
 * tests/fixtures/test-data.fixture.ts
 *
 * Test-data factory for TraceForge-generated tests.
 *
 * SETUP REQUIRED: Generate this contract from reviewed test-case metadata.
 * Do not add entities, values, units, roles, or lifecycle methods unless they
 * are present in cited evidence and approved in the Automation Context Pack.
 */
import { type APIRequestContext } from '@playwright/test';

export interface ReviewedTestData {
  correlationId: string;
  values: Record<string, unknown>;
}

export interface TestDataFactory {
  create(data: ReviewedTestData): Promise<{ recordId: string }>;
  cleanup(recordId: string): Promise<void>;
}

// TODO: Implement using the application's API or test-setup endpoints.
export class NotImplementedDataFactory implements TestDataFactory {
  private readonly request: APIRequestContext;
  constructor(request: APIRequestContext) { this.request = request; }

  async create(_data: ReviewedTestData): Promise<{ recordId: string }> {
    throw new Error('Test-data factory not implemented. Map create() to the approved setup contract.');
  }
  async cleanup(_recordId: string): Promise<void> {
    throw new Error('Test-data cleanup not implemented. Map cleanup() to the approved reversal contract.');
  }
}
"""

    pages_readme = """\
# Page Objects (tests/pages/)

Page objects are not yet implemented. TraceForge generates test-step logic grounded
in the requirement document. Once application screen/transaction/API metadata is
supplied to TraceForge via the Automation Context Pack, page objects can be generated.

## Required page objects

No page objects are inferred from prose. Generate one only when a reviewed case
supplies its real screen or transaction name and stable locator contract.

## What each page object must expose

Each page object must provide:
- Stable getByTestId/getByRole locators for every business field
- Role-specific navigation (login, transaction, tab)
- Field-level business-state assertions from the reviewed assertion map
- Setup and cleanup methods

Do NOT derive locators from English step text. Map real application element IDs.
"""

    automation_readiness = f"""\
# Automation Readiness Assessment — {project.name}

Generated by TraceForge. Review before attempting execution.

## Summary

| Metric                        | Value                     |
|-------------------------------|---------------------------|
| Total test cases              | {total}                   |
| Automation blocked            | {blocked_count}           |
| Skipped (blocked)             | {skipped_count}           |
| Potentially executable        | {total - blocked_count}   |
| `fullyParallel`               | false (shared state)      |
| `workers`                     | 1 (serial execution)      |

## Blockers requiring business owner resolution

1. **Application metadata not supplied** — No system names, transaction codes, screen URLs, or stable selectors are available. Tests cannot be automated without this.
2. **Authentication not implemented** — `tests/fixtures/auth.fixture.ts` is a stub. Implement only source-confirmed roles before execution.
3. **Test-data factory not implemented** — `tests/fixtures/test-data.fixture.ts` is a stub. Implement API-based data creation and cleanup.
4. **Open source ambiguities** — Resolve every contradiction recorded in case metadata before provisioning test data.
5. **Units and calculation rules** — Confirm source units and formulas; never substitute a monetary or boundary value.
6. **Manual activities** — Keep physical or human-presence steps manual unless an approved simulation contract exists.
7. **Page objects not implemented** — `tests/pages/` contains only a README. Implement page objects with real application selectors.
8. **Shared state** — Do NOT enable `fullyParallel` until worker-isolated test data is provisioned.

## How to unblock

1. Collect the automation context pack: base URL, auth method, stable selectors, API endpoints, test-data factory, cleanup process.
2. Re-run TraceForge with the populated automation context pack.
3. Implement `tests/fixtures/auth.fixture.ts` with real login logic for each role.
4. Implement `tests/fixtures/test-data.fixture.ts` with API clients for data setup and cleanup.
5. Implement `tests/pages/*.page.ts` with real locators mapped from the application.
6. Re-run TraceForge script generation to replace AUTOMATION_BLOCKED placeholders with executable code.
"""

    readme = f"""\
# {project.name} Playwright Test Suite

Generated by TraceForge with requirement and test-case traceability.

## ⚠️ Read before running

This suite is an AI-generated test inventory. **{blocked_count} of {total} tests are AUTOMATION_BLOCKED** (test.skip) because the following are not yet available:

- Application screen/transaction metadata and stable selectors
- Authentication implementation for all required roles
- Test-data factory and cleanup process
- Resolved business ambiguities (see AUTOMATION-READINESS.md)

**Do not run against any shared or production environment until all blockers in AUTOMATION-READINESS.md are resolved.**

## Prerequisites

```bash
npm install
npx playwright install --with-deps chromium
```

## Configuration

```bash
cp .env.example .env
# Fill in real values — never commit credentials
```

Set `PLAYWRIGHT_BASE_URL`, implement `tests/fixtures/auth.fixture.ts`, implement `tests/fixtures/test-data.fixture.ts`, and populate `tests/pages/*.page.ts` with real locators before running.

## Run

```bash
npm test           # Run all non-blocked tests (serial)
npm run report     # Open HTML report
```

## Package structure

```
playwright.config.ts          — Test configuration (fullyParallel: false for shared state)
tsconfig.json                 — TypeScript compiler configuration
.env.example                  — Environment variable template
AUTOMATION-READINESS.md       — Full blocker list and resolution guide
tests/
  helpers/
    traceforge-runtime.ts     — Shared automation helpers (one copy, not 84)
  fixtures/
    auth.fixture.ts           — Authentication fixture stub (IMPLEMENT THIS FIRST)
    test-data.fixture.ts      — Test-data factory stub (IMPLEMENT SECOND)
  pages/
    README.md                 — Page object guide (IMPLEMENT THIRD)
  e2e/
    *.spec.ts                 — Generated test specifications ({total} files)
```

## Test case lifecycle

Test cases are generated in `DRAFT` status. They require business owner review before execution. The gate approval process in TraceForge promotes cases to `APPROVED` status, after which scripts are generated.

Cases marked `[AUTOMATION BLOCKED]` in their steps require the business owner to supply application metadata. They are `test.skip()` and will not run until regenerated with a complete automation context pack.
"""

    _RUNTIME_REGION_RE = re.compile(
        re.escape(RUNTIME_REGION_START) + r".*?" + re.escape(RUNTIME_REGION_END) + r"\n?",
        re.DOTALL,
    )
    _SHARED_IMPORT = (
        "import { test, expect } from '@playwright/test';\n"
        "import { executeReviewedStep, assertBusinessState, semanticLocator, BASE_URL } "
        "from '../../helpers/traceforge-runtime';\n"
    )

    manifest = []
    for test_case in approved_cases:
        metadata = _parse_tc_metadata(test_case)
        verified_status, readiness_blockers = _verified_automation_status(test_case, metadata)
        script = scripts_by_case.get(test_case.id) if verified_status == "READY_FOR_UI_AUTOMATION" else None
        manifest.append({
            "ts_id": script.ts_id if script else None,
            "test_case_id": str(test_case.id),
            "test_case_ref": test_case.tc_id,
            "test_level": test_case.test_level,
            "path": _suite_path(script) if script else None,
            "compiles": script.compiles if script else None,
            "syntax_status": "PASS" if script and script.compiles is True else "FAIL" if script and script.compiles is False else "NOT_APPLICABLE",
            "automation_status": verified_status,
            "lifecycle_status": test_case.status,
            "runnable": bool(script and script.compiles is True),
            "excluded_from_playwright": script is None,
            "blockers": readiness_blockers,
            "version": script.version if script else None,
        })

    archive = io.BytesIO()
    used_paths: set[str] = set()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for script in scripts:
            path = _suite_path(script)
            if path in used_paths:
                stem = PurePosixPath(path).stem
                path = str(PurePosixPath(path).with_name(f"{stem}_{script.ts_id.lower()}.spec.ts"))
            used_paths.add(path)
            # Strip inline runtime block and replace with shared module import
            code = _RUNTIME_REGION_RE.sub("", script.code)
            # Remove duplicate @playwright/test import left after stripping the inline block
            code = re.sub(
                r"^import \{ test, expect, type Locator, type Page \} from '@playwright/test';?\n",
                _SHARED_IMPORT,
                code,
                count=1,
                flags=re.MULTILINE,
            )
            bundle.writestr(path, code)

        bundle.writestr("tests/helpers/traceforge-runtime.ts", PLAYWRIGHT_RUNTIME_MODULE)
        bundle.writestr("tests/fixtures/auth.fixture.ts", auth_fixture)
        bundle.writestr("tests/fixtures/test-data.fixture.ts", test_data_fixture)
        bundle.writestr("tests/pages/README.md", pages_readme)
        bundle.writestr("package.json", json.dumps(package_json, indent=2) + "\n")
        bundle.writestr("playwright.config.ts", playwright_config)
        bundle.writestr("tsconfig.json", tsconfig)
        bundle.writestr(".env.example", env_example)
        bundle.writestr("AUTOMATION-READINESS.md", automation_readiness)
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
