# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Every LLM call is logged (spec §5.3, §6.3): writes one LLMCall row per call.
# Date: 2026-05-10
# ---------------------------------------------------------------------------
"""Every LLM call is logged (spec §5.3, §6.3): writes one LLMCall row per call."""
from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.config import PERSIST_LLM_IO
from traceforge.db.models import LLMCall
from traceforge.llm.provider import LLMResponse
from traceforge.security.pii import redact_pii


# Function: _redacted_io
def _redacted_io(system: str | None, user_prompt: str | None, completion: str) -> tuple[str | None, str | None, dict]:
    """§6.3: only persists prompt/completion text when PERSIST_LLM_IO is on, and only
    after a successful PII redaction pass — if redaction is unavailable or fails, this
    returns (None, None, {}) rather than ever writing raw text (fail closed)."""
    if not PERSIST_LLM_IO:
        return None, None, {}
    combined_prompt = "\n\n".join(part for part in (system, user_prompt) if part)
    prompt_result = redact_pii(combined_prompt) if combined_prompt else ("", {})
    completion_result = redact_pii(completion)
    if prompt_result is None or completion_result is None:
        return None, None, {}
    prompt_text, prompt_map = prompt_result
    completion_text, completion_map = completion_result
    return prompt_text, completion_text, {"prompt": prompt_map, "completion": completion_map}


# Function: record_llm_call
async def record_llm_call(
    session: AsyncSession,
    *,
    pipeline_run_id: uuid.UUID | None,
    agent_name: str,
    response: LLMResponse,
    retry_count: int = 0,
    schema_valid: bool = True,
    system: str | None = None,
    user_prompt: str | None = None,
) -> None:
    prompt_text, completion_text, pii_entity_map = _redacted_io(system, user_prompt, response.text)
    session.add(
        LLMCall(
            pipeline_run_id=pipeline_run_id,
            agent_name=agent_name,
            model=response.model,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            cost_usd=0.0,  # local Ollama — no metered API cost
            latency_ms=response.latency_ms,
            retry_count=retry_count,
            schema_valid=schema_valid,
            prompt_text=prompt_text,
            completion_text=completion_text,
            pii_entity_map=pii_entity_map,
        )
    )
