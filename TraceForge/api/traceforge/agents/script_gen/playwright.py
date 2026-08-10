# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Playwright TypeScript emitter with executable semantic locator resolution.
# Date: 2026-02-28
# ---------------------------------------------------------------------------
"""Playwright TypeScript emitter with executable semantic locator resolution."""
from __future__ import annotations

import json
import re

from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.agents.script_gen.base import (
    _render_playwright_body,
    generate_script_body,
    preserve_custom_regions,
    traceability_header,
)
from traceforge.agents.script_gen.semantic_runtime import (
    PLAYWRIGHT_RUNTIME,
    RUNTIME_REGION_END,
    RUNTIME_REGION_START,
)


def _parse_tc_metadata(test_case) -> dict:
    """Parse rich metadata stored in the gherkin column."""
    raw = getattr(test_case, "gherkin", None) or ""
    if raw and raw.strip().startswith("{"):
        try:
            return json.loads(raw)
        except ValueError:
            pass
    return {}


def _automation_blocked_report(test_case, requirement, blockers: list[str]) -> str:
    """Generate a clearly labelled blocked-automation file instead of fake runnable code."""
    safe_title = json.dumps(f"[AUTOMATION BLOCKED] {test_case.title}", ensure_ascii=False)
    blocker_comments = "\n".join(f"   * {b}" for b in (blockers or ["Automation metadata not supplied"]))
    return (
        "/**\n"
        f" * AUTOMATION STATUS: BLOCKED\n"
        f" * Test Case: {test_case.tc_id} — {test_case.title}\n"
        f" * Requirement: {requirement.req_id} — {requirement.statement[:120]}\n"
        f" *\n"
        f" * This test case cannot be automated until the following are resolved:\n"
        f"{blocker_comments}\n"
        f" *\n"
        f" * Steps required by the business owner:\n"
        + "\n".join(
            f" *   Step {s.get('step_no','?')}: {s.get('action','')[:150]}"
            for s in (test_case.steps or [])
        )
        + "\n"
        " *\n"
        " * Once all blockers are resolved, re-run TraceForge script generation\n"
        " * with the completed automation context pack to produce executable code.\n"
        " */\n"
        "import { test } from '@playwright/test';\n\n"
        f"test.skip({safe_title}, () => {{\n"
        "  // This test is skipped because automation metadata is not yet available.\n"
        "  // Resolve the blockers listed above, then regenerate this file.\n"
        "});\n"
    )


def _verified_automation_status(test_case, metadata: dict) -> tuple[str, list[str]]:
    """Fail closed unless the case contains a complete automation contract."""
    requested = metadata.get("automation_status", "AUTOMATION_BLOCKED")
    blockers = list(metadata.get("automation_blockers", []))
    context = metadata.get("automation_context") or {}
    if test_case.test_level in {"INTEGRATION", "UAT"}:
        return "MANUAL_ONLY", []
    if requested in {"AUTOMATION_BLOCKED", "MANUAL_ONLY"}:
        return requested, blockers
    if test_case.test_level != "UI_E2E":
        blockers.append(f"{test_case.test_level} case requires its matching API/integration runner, not the UI Playwright emitter")
        return "AUTOMATION_BLOCKED", blockers
    if requested == "READY_FOR_HYBRID_AUTOMATION":
        blockers.append("Hybrid UI/API execution is not implemented by the current Playwright emitter")
        return "AUTOMATION_BLOCKED", blockers
    required = {
        "READY_FOR_UI_AUTOMATION": ("base_url", "auth", "locators", "assertions", "test_data_factory", "cleanup"),
        "READY_FOR_API_AUTOMATION": ("base_url", "auth", "endpoints", "schemas", "test_data_factory", "cleanup"),
        "READY_FOR_HYBRID_AUTOMATION": ("base_url", "auth", "locators", "assertions", "endpoints", "schemas", "test_data_factory", "cleanup"),
    }.get(requested)
    if not required:
        return requested, blockers
    missing = [key for key in required if not context.get(key)]
    if any(
        "[EXECUTION DETAIL BLOCKED" in str(step.get("action", ""))
        or "[PENDING BUSINESS CONFIRMATION" in str(step.get("expected_result", ""))
        for step in (getattr(test_case, "steps", None) or [])
    ):
        missing.append("reviewed executable steps")
    if missing:
        blockers.append("Missing concrete automation contract: " + ", ".join(missing))
        return "AUTOMATION_BLOCKED", blockers
    return requested, blockers


def runtime_with_context(metadata: dict, source: str = PLAYWRIGHT_RUNTIME) -> str:
    context = metadata.get("automation_context") or {}
    base_url = json.dumps(context.get("base_url") or "http://localhost:3000", ensure_ascii=False)
    locators = json.dumps(context.get("locators") or {}, ensure_ascii=False, sort_keys=True)
    assertions = json.dumps(context.get("assertions") or {}, ensure_ascii=False, sort_keys=True)
    auth_method = json.dumps((context.get("auth") or {}).get("method") or "execution-environment authentication", ensure_ascii=False)
    runtime = source.replace(
        "?? 'http://localhost:3000';",
        f"?? {base_url};",
    )
    runtime = runtime.replace(
        "const raw = process.env.TRACEFORGE_LOCATORS;\n  if (!raw) return {};",
        f"const raw = process.env.TRACEFORGE_LOCATORS;\n  if (!raw) return {locators};",
    )
    runtime = runtime.replace(
        "const raw = process.env.TRACEFORGE_ASSERTIONS;\n  if (!raw) return {};",
        f"const raw = process.env.TRACEFORGE_ASSERTIONS;\n  if (!raw) return {assertions};",
    )
    return runtime.replace(
        "declare const process: { env: Record<string, string | undefined> };",
        "declare const process: { env: Record<string, string | undefined> };\n"
        f"const TRACEFORGE_AUTH_METHOD = {auth_method};",
    )


class PlaywrightEmitter:
    target = "PLAYWRIGHT_TS"

    def can_handle(self, test_case) -> bool:
        metadata = _parse_tc_metadata(test_case)
        status, _ = _verified_automation_status(test_case, metadata)
        return status == "READY_FOR_UI_AUTOMATION"

    async def generate(
        self, session: AsyncSession, provider, test_case, requirement, ctx: dict, pipeline_run_id,
    ) -> tuple[str, str, dict | None]:
        slug = re.sub(r"[^a-z0-9]+", "_", test_case.title.lower()).strip("_") or "scenario"
        file_path = f"tests/e2e/{test_case.tc_id.lower()}_{slug}.spec.ts"

        # Check automation status from stored metadata
        metadata = _parse_tc_metadata(test_case)
        automation_status, blockers = _verified_automation_status(test_case, metadata)

        # Also block if any step contains the EXECUTION DETAIL BLOCKED marker
        blocked_steps = [
            s for s in (test_case.steps or [])
            if "[EXECUTION DETAIL BLOCKED" in (s.get("action") or "")
        ]
        if blocked_steps:
            automation_status = "AUTOMATION_BLOCKED"
            blockers = list(set(blockers + [
                f"Step {s.get('step_no','?')}: {(s.get('action') or '')[:120]}"
                for s in blocked_steps
            ]))

        if automation_status == "AUTOMATION_BLOCKED":
            header = traceability_header(
                req_id=requirement.req_id, req_statement=requirement.statement,
                tc_id=test_case.tc_id, tc_title=test_case.title,
                test_type=test_case.test_type,
                sources=ctx.get("sources_label", "(no source citation available)"),
            )
            code = header + _automation_blocked_report(test_case, requirement, blockers)
            return preserve_custom_regions(ctx.get("previous_code"), code), file_path, None

        if ctx.get("compile_repair") or ctx.get("batch_scenario"):
            body = _render_playwright_body(
                test_case.steps or [],
                [],
                scenario=ctx.get("batch_scenario") or test_case.title,
            )
        else:
            body = await generate_script_body(
                session,
                provider,
                framework="playwright",
                test_case=test_case,
                requirement=requirement,
                ctx=ctx,
                pipeline_run_id=pipeline_run_id,
                agent_name="script_generator_playwright",
            )
        header = traceability_header(
            req_id=requirement.req_id, req_statement=requirement.statement, tc_id=test_case.tc_id,
            tc_title=test_case.title, test_type=test_case.test_type,
            sources=ctx.get("sources_label", "(no source citation available)"),
        )
        safe_title = json.dumps(
            f"@{requirement.req_id} @{test_case.tc_id} {test_case.title}",
            ensure_ascii=False,
        )
        # Warn when parallel execution is unsafe for shared-state resources
        parallel_safe = metadata.get("parallel_safe", False)
        serial_annotation = "  test.describe.configure({ mode: 'serial' });\n\n" if not parallel_safe else ""

        generated = (
            f"{header}"
            "import { test, expect, type Locator, type Page } from '@playwright/test';\n\n"
            f"{RUNTIME_REGION_START}\n"
            f"{runtime_with_context(metadata)}\n"
            f"{RUNTIME_REGION_END}\n"
            f"test.describe({json.dumps(requirement.title, ensure_ascii=False)}, () => {{\n"
            f"{serial_annotation}"
            "  test.beforeEach(async ({ page }) => {\n"
            "    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });\n"
            "    await expect(page.locator('body')).toBeVisible();\n"
            "  });\n\n"
            f"  test({safe_title}, async ({{ page }}, testInfo) => {{\n"
            f"    testInfo.annotations.push({{ type: 'requirement', description: {json.dumps(requirement.req_id)} }});\n"
            f"    testInfo.annotations.push({{ type: 'test-case', description: {json.dumps(test_case.tc_id)} }});\n"
            f"    testInfo.annotations.push({{ type: 'test-level', description: {json.dumps(test_case.test_level)} }});\n"
            f"    testInfo.annotations.push({{ type: 'automation-status', description: {json.dumps(automation_status)} }});\n"
            f"{body}\n"
            "  });\n"
            "});\n\n"
            "// <traceforge:custom>\n"
            "// Add project-specific fixtures or assertions here; this region survives regeneration.\n"
            "// </traceforge:custom>\n"
        )
        code = preserve_custom_regions(ctx.get("previous_code"), generated)
        return code, file_path, None
