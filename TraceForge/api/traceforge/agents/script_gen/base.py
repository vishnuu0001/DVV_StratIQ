# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §5 Agent 4 — Script Generator. Pluggable emitters, one shared TypeScript
# Date: 2025-09-29
# ---------------------------------------------------------------------------
"""§5 Agent 4 — Script Generator. Pluggable emitters, one shared TypeScript
traceability-header convention, so a test case's provenance survives regeneration."""
from __future__ import annotations

import re
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.config import SCRIPT_MAX_TOKENS

CUSTOM_REGION_START = "// <traceforge:custom>"
CUSTOM_REGION_END = "// </traceforge:custom>"

# Few-shot anchors so the LLM's TypeScript matches each framework's real API shape
# instead of inventing plausible-but-wrong method names.
_FRAMEWORK_EXAMPLES = {
    "playwright": (
        "EXAMPLE (Playwright + @playwright/test):\n"
        "  await test.step('Step 1: Click [Submit Order]', async () => {\n"
        "    await page.getByRole('button', { name: TODO_LOCATOR('Submit Order button') }).click();\n"
        "  });\n"
        "  await test.step('Step 2: Verify confirmation', async () => {\n"
        "    await expect(page.getByText(TODO_LOCATOR('order confirmation message'))).toBeVisible();\n"
        "  });\n"
    ),
    "selenium": (
        "EXAMPLE (selenium-webdriver + Mocha):\n"
        "  // Step 1: Click [Submit Order]\n"
        "  await driver.findElement(By.css(TODO_LOCATOR('Submit Order button'))).click();\n"
        "  // Step 2: Verify confirmation\n"
        "  const bodyText = await driver.findElement(By.css('body')).getText();\n"
        "  assert.ok(bodyText.includes(TODO_LOCATOR('order confirmation message')));\n"
    ),
}


# Function: generate_script_body
async def generate_script_body(
    session: AsyncSession, provider, *, framework: str, test_case, requirement, ctx: dict,
    pipeline_run_id, agent_name: str,
) -> str:
    """LLM-authored test body for one (test case, framework) pair — replaces the prior
    fixed step->code template so the actual test logic/wording is generated, not
    pattern-matched. Selectors stay constrained to TODO_LOCATOR('hint'): the LLM never
    sees the real DOM, so a concrete selector it invents (e.g. '#submit-btn') only ever
    looks plausible — spec's rule that a fabricated selector is worse than an explicit
    gap still holds regardless of how the surrounding code gets written."""
    steps_text = "\n".join(
        f"{s.get('step_no', '?')}. {s.get('action', '')} -> Expected: {s.get('expected_result', '')}"
        + (f" [test data: {s['test_data']}]" if s.get("test_data") else "")
        for s in (test_case.steps or [])
    ) or "(no steps were generated for this test case)"

    system = (
        f"You are a senior SDET writing a {framework} test in TypeScript. Write ONLY the test "
        "body -- the statements that go inside the test/it callback, covering every numbered step "
        "below. Do not write imports, the test/describe wrapper, or a traceability header -- those "
        "are added separately.\n\n"
        "CRITICAL RULE: you cannot see the real UI, so you must NEVER invent a concrete selector "
        "(no '#id', '.class', or guessed CSS/XPath/role names). For every element you need to "
        "interact with or assert against, call TODO_LOCATOR('a short human-readable hint describing "
        "the element') exactly as shown below -- a human resolves these against the real DOM before "
        "the suite runs. Fabricating a selector that merely looks plausible is a critical failure; "
        "an explicit TODO_LOCATOR gap is always correct, a guessed selector is never correct.\n\n"
        + _FRAMEWORK_EXAMPLES[framework]
    )
    user = (
        f"REQUIREMENT {requirement.req_id}: {requirement.statement}\n\n"
        f"TEST CASE: {test_case.title} ({test_case.test_type})\n"
        f"PRECONDITIONS: {'; '.join(test_case.preconditions) or '(none)'}\n\n"
        f"STEPS:\n{steps_text}\n\n"
        "Write the test body now. Return TypeScript statements only, no markdown fences, no explanation."
    )
    response = await provider.generate(system, user, temperature=0.2, max_tokens=SCRIPT_MAX_TOKENS, json_mode=False)
    from traceforge.llm.metering import record_llm_call
    await record_llm_call(session, pipeline_run_id=pipeline_run_id, agent_name=agent_name, response=response)
    body = response.text.strip()
    if body.startswith("```"):
        body = re.sub(r"^```(?:typescript|ts)?\s*|\s*```$", "", body, flags=re.I).strip()
    return body


# Function: deterministic_script_body
def deterministic_script_body(framework: str, test_case, requirement=None) -> str:
    """Render each reviewed step as executable semantic automation."""
    lines: list[str] = []
    scenario = getattr(requirement, "title", None) or getattr(test_case, "title", "Reviewed scenario")
    for step in (test_case.steps or []):
        number = step.get("step_no", "?")
        payload = ", ".join(
            f"{key}: {json.dumps(str(value), ensure_ascii=False)}"
            for key, value in (
                ("action", step.get("action", "")),
                ("expected", step.get("expected_result", "")),
                ("data", step.get("test_data", "")),
                ("scenario", scenario),
            )
        )
        if framework == "playwright":
            lines.extend([
                f"  await test.step('Step {number}', async () => {{",
                f"    await executeReviewedStep(page, {{ {payload} }});",
                "  });",
            ])
        else:
            lines.extend([
                f"    // Step {number}",
                f"    await executeReviewedStep(driver, {{ {payload} }});",
            ])
    return "\n".join(lines) or "  throw new Error('No reviewed steps were available for this test case.');"


@dataclass
class ValidationResult:
    compiles: bool | None  # None = not validated (toolchain unavailable)
    output: str


# Function: traceability_header
def traceability_header(*, req_id: str, req_statement: str, tc_id: str, tc_title: str, test_type: str, sources: str) -> str:
    wrapped = "\n *                          ".join(_wrap(req_statement, 70))
    return f"""/**
 * @generated-by TraceForge
 * @requirement {req_id} — "{wrapped}"
 * @test-case  {tc_id} ({test_type}) — {tc_title}
 * @source     {sources}
 * @generated  {datetime.now(timezone.utc).isoformat(timespec="seconds")}
 * DO NOT EDIT the traceability header. Edits inside {CUSTOM_REGION_START} ... {CUSTOM_REGION_END} are preserved on regeneration.
 */
"""


# Function: _wrap
def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return lines or [""]


# Function: preserve_custom_regions
def preserve_custom_regions(previous_code: str | None, new_code: str) -> str:
    """If the previous version of this script has a <traceforge:custom> region with
    human edits, splice it into the newly regenerated code so regeneration never
    silently discards a reviewer's changes (spec §4 Gate 4)."""
    if not previous_code or CUSTOM_REGION_START not in previous_code:
        return new_code
    match = re.search(re.escape(CUSTOM_REGION_START) + r"(.*?)" + re.escape(CUSTOM_REGION_END), previous_code, re.DOTALL)
    if not match:
        return new_code
    custom_block = match.group(0)
    if CUSTOM_REGION_START in new_code:
        return re.sub(re.escape(CUSTOM_REGION_START) + r".*?" + re.escape(CUSTOM_REGION_END), custom_block, new_code, flags=re.DOTALL)
    return new_code + "\n" + custom_block + "\n"


class ScriptEmitter(Protocol):
    target: str

    # Function: can_handle
    def can_handle(self, test_case) -> bool: ...
    # Function: generate
    async def generate(self, session: AsyncSession, provider, test_case, requirement, ctx: dict, pipeline_run_id) -> tuple[str, str, dict | None]:
        """Returns (code, file_path, page_objects)."""
        ...
