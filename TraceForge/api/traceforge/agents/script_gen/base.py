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

from traceforge.config import SCRIPT_PLAN_MAX_TOKENS

CUSTOM_REGION_START = "// <traceforge:custom>"
CUSTOM_REGION_END = "// </traceforge:custom>"

# Few-shot anchors so the LLM's TypeScript matches each framework's real API shape
# instead of inventing plausible-but-wrong method names.
_FRAMEWORK_EXAMPLES = {
    "playwright": (
        "EXAMPLE (body statements only):\n"
        "  await test.step('Step 1: submit the order', async () => {\n"
        "    await executeReviewedStep(page, {\n"
        "      action: 'Submit the completed order',\n"
        "      expected: 'The confirmation is visible',\n"
        "      data: 'Use the worker-scoped order record',\n"
        "      scenario: 'Successful order submission',\n"
        "    });\n"
        "  });\n"
    ),
}


# Function: generate_script_body
async def generate_script_body(
    session: AsyncSession, provider, *, framework: str, test_case, requirement, ctx: dict,
    pipeline_run_id, agent_name: str,
) -> str:
    """Use Ollama for semantic planning and render compile-safe TypeScript locally."""
    reviewed_steps = test_case.steps or []
    steps_text = "\n".join(
        f"{s.get('step_no', '?')}. {s.get('action', '')} -> Expected: {s.get('expected_result', '')}"
        + (f" [test data: {s['test_data']}]" if s.get("test_data") else "")
        for s in reviewed_steps
    ) or "(no steps were generated for this test case)"

    system = (
        f"You are a senior SDET planning a production-grade {framework} test. "
        "Return compact semantic JSON only; TraceForge renders the TypeScript syntax. "
        "Never invent selectors, URLs, credentials, or unsupported test data. "
        "Return exactly one item per reviewed step in the same order using this schema: "
        '{"steps":[{"step_no":int,"action":str,"expected":str,"data":str,"scenario":str}]}. '
        "Keep every field under 30 words."
    )
    user = (
        f"REQUIREMENT {requirement.req_id}: {requirement.statement}\n\n"
        f"TEST CASE: {test_case.title} ({test_case.test_type})\n"
        f"PRECONDITIONS: {'; '.join(test_case.preconditions) or '(none)'}\n\n"
        f"STEPS:\n{steps_text}\n\n"
        "Return the semantic step plan now as JSON only."
    )
    from traceforge.llm.metering import record_llm_call

    validation_error = ""
    for attempt in range(2):
        retry_user = user
        if validation_error:
            retry_user += (
                "\n\nYour previous response was rejected by the safety validator: "
                f"{validation_error}. Regenerate the complete body and obey every critical rule."
            )
        response = await provider.generate(
            system, retry_user, temperature=0.2, max_tokens=SCRIPT_PLAN_MAX_TOKENS, json_mode=True,
        )
        planned_steps: list[dict] = []
        try:
            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text, flags=re.I).strip()
            parsed = json.loads(raw_text)
            planned_steps = parsed.get("steps", []) if isinstance(parsed, dict) else []
            if len(planned_steps) != len(reviewed_steps) or not all(isinstance(item, dict) for item in planned_steps):
                validation_error = f"expected {len(reviewed_steps)} semantic step objects"
            else:
                validation_error = ""
        except (json.JSONDecodeError, TypeError) as exc:
            validation_error = f"invalid semantic JSON: {exc}"
        await record_llm_call(
            session,
            pipeline_run_id=pipeline_run_id,
            agent_name=agent_name,
            response=response,
            retry_count=attempt,
            schema_valid=not validation_error,
            system=system,
            user_prompt=retry_user,
        )
        if not validation_error:
            return _render_playwright_body(
                reviewed_steps, planned_steps, scenario=getattr(test_case, "title", "Reviewed scenario"),
            )

    # The reviewed test case remains authoritative when Ollama's compact plan is
    # malformed. Rendering it locally is safe, complete, and compile deterministic.
    return _render_playwright_body(
        reviewed_steps, [], scenario=getattr(test_case, "title", "Reviewed scenario"),
    )


def _text_value(value, fallback: str) -> str:
    if value is None or value == "":
        return fallback
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _render_playwright_body(
    reviewed_steps: list[dict],
    planned_steps: list[dict],
    *,
    scenario: str,
) -> str:
    lines: list[str] = []
    for index, reviewed in enumerate(reviewed_steps):
        planned = planned_steps[index] if index < len(planned_steps) else {}
        step_no = reviewed.get("step_no", index + 1)
        action = _text_value(planned.get("action"), _text_value(reviewed.get("action"), "Execute reviewed action"))
        expected = _text_value(
            planned.get("expected"),
            _text_value(reviewed.get("expected_result"), "Verify the reviewed expected result"),
        )
        data = _text_value(planned.get("data"), _text_value(reviewed.get("test_data"), ""))
        step_scenario = _text_value(planned.get("scenario"), scenario)
        label = f"Step {step_no}: {action[:90]}"
        lines.extend([
            f"    await test.step({json.dumps(label, ensure_ascii=False)}, async () => {{",
            "      await executeReviewedStep(page, {",
            f"        action: {json.dumps(action, ensure_ascii=False)},",
            f"        expected: {json.dumps(expected, ensure_ascii=False)},",
            f"        data: {json.dumps(data, ensure_ascii=False)},",
            f"        scenario: {json.dumps(step_scenario, ensure_ascii=False)},",
            "      });",
            "    });",
        ])
    return "\n".join(lines)


def _validate_playwright_body(body: str, *, expected_steps: int) -> str:
    """Reject incomplete bodies and any model output that bypasses the reviewed-step runtime."""
    if not body:
        return "the body was empty"
    if body.count("executeReviewedStep(") != expected_steps:
        return f"expected {expected_steps} executeReviewedStep calls"
    if body.count("test.step(") != expected_steps:
        return f"expected {expected_steps} test.step blocks"

    forbidden_patterns = {
        r"\bpage\.": "direct page calls are forbidden",
        r"\b(?:locator|getBy\w*)\s*\(": "invented DOM locators are forbidden",
        r"\bwaitForTimeout\s*\(": "fixed sleeps are forbidden",
        r"^\s*import\b": "imports are forbidden in a test body",
        r"\btest\.(?:describe|before|after|use)\s*\(": "test wrappers and hooks are forbidden",
        r"```": "markdown fences are forbidden",
    }
    for pattern, message in forbidden_patterns.items():
        if re.search(pattern, body, flags=re.I | re.M):
            return message
    return ""


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
