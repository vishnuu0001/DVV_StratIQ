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
from traceforge.agents.script_gen.semantic_runtime import PLAYWRIGHT_RUNTIME


class PlaywrightEmitter:
    target = "PLAYWRIGHT_TS"

    # Function: can_handle
    def can_handle(self, test_case) -> bool:
        return True

    # Function: generate
    async def generate(
        self, session: AsyncSession, provider, test_case, requirement, ctx: dict, pipeline_run_id,
    ) -> tuple[str, str, dict | None]:
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
        slug = re.sub(r"[^a-z0-9]+", "_", test_case.title.lower()).strip("_") or "scenario"
        safe_title = json.dumps(
            f"@{requirement.req_id} @{test_case.tc_id} {test_case.title}",
            ensure_ascii=False,
        )
        generated = (
            f"{header}"
            "import { test, expect, type Locator, type Page } from '@playwright/test';\n\n"
            f"{PLAYWRIGHT_RUNTIME}\n"
            f"test.describe({json.dumps(requirement.title, ensure_ascii=False)}, () => {{\n"
            "  test.beforeEach(async ({ page }) => {\n"
            "    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });\n"
            "    await expect(page.locator('body')).toBeVisible();\n"
            "  });\n\n"
            f"  test({safe_title}, async ({{ page }}, testInfo) => {{\n"
            f"    testInfo.annotations.push({{ type: 'requirement', description: {json.dumps(requirement.req_id)} }});\n"
            f"    testInfo.annotations.push({{ type: 'test-case', description: {json.dumps(test_case.tc_id)} }});\n"
            f"{body}\n"
            "  });\n"
            "});\n\n"
            "// <traceforge:custom>\n"
            "// Add project-specific fixtures or assertions here; this region survives regeneration.\n"
            "// </traceforge:custom>\n"
        )
        code = preserve_custom_regions(ctx.get("previous_code"), generated)
        return code, f"tests/e2e/{test_case.tc_id.lower()}_{slug}.spec.ts", None
