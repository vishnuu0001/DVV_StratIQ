# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Selenium TypeScript emitter with executable semantic locator resolution.
# Date: 2026-02-07
# ---------------------------------------------------------------------------
"""Selenium TypeScript emitter with executable semantic locator resolution."""
from __future__ import annotations

import re

from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.agents.script_gen.base import (
    deterministic_script_body,
    preserve_custom_regions,
    traceability_header,
)
from traceforge.agents.script_gen.semantic_runtime import SELENIUM_RUNTIME


class SeleniumEmitter:
    target = "SELENIUM_TS"

    # Function: can_handle
    def can_handle(self, test_case) -> bool:
        return test_case.test_level == "UI_E2E"

    # Function: generate
    async def generate(
        self, session: AsyncSession, provider, test_case, requirement, ctx: dict, pipeline_run_id,
    ) -> tuple[str, str, dict | None]:
        body = deterministic_script_body("selenium", test_case, requirement)
        header = traceability_header(
            req_id=requirement.req_id, req_statement=requirement.statement, tc_id=test_case.tc_id,
            tc_title=test_case.title, test_type=test_case.test_type,
            sources=ctx.get("sources_label", "(no source citation available)"),
        )
        slug = re.sub(r"[^a-z0-9]+", "_", test_case.title.lower()).strip("_") or test_case.tc_id.lower()
        generated = (
            f"{header}"
            "import { Builder, By, WebDriver, WebElement } from 'selenium-webdriver';\n"
            "import { describe, it, before, after } from 'mocha';\n"
            "import assert from 'assert';\n\n"
            f"{SELENIUM_RUNTIME}\n"
            f"describe('@{requirement.req_id} @{test_case.tc_id} {test_case.title}', function () {{\n"
            "  let driver: WebDriver;\n\n"
            "  before(async function () { driver = await new Builder().forBrowser('chrome').build(); });\n"
            "  after(async function () { await driver.quit(); });\n\n"
            f"  it('{test_case.title}', async function () {{\n"
            f"{body}\n"
            "  });\n"
            "});\n\n"
            "// <traceforge:custom>\n"
            "// Add project-specific fixtures or assertions here.\n"
            "// </traceforge:custom>\n"
        )
        code = preserve_custom_regions(ctx.get("previous_code"), generated)
        return code, f"tests/e2e/selenium/{slug}.spec.ts", None
