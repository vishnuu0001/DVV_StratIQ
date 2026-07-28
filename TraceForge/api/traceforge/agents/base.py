# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §5 'Universal rules for all agents' — shared contract, retry-once-on-schema-failure,
# Date: 2025-08-19
# ---------------------------------------------------------------------------
"""§5 'Universal rules for all agents' — shared contract, retry-once-on-schema-failure,
map-reduce batching. Every concrete agent (extractor.py today; brd_author.py etc. in
later phases) builds on this instead of re-implementing the retry/logging dance."""
from __future__ import annotations

import json
import logging
import uuid
from collections.abc import Awaitable, Callable
from typing import Generic, TypeVar

from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.config import AGENT_MAX_TOKENS, AGENT_TEMPERATURE
from traceforge.llm.metering import record_llm_call
from traceforge.llm.provider import LLMProvider

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0


class AgentResult(BaseModel, Generic[T]):
    items: list[T]
    citations: dict[str, list[str]] = {}
    warnings: list[str] = []
    tokens: TokenUsage = TokenUsage()


# Function: _extract_json
def _extract_json(raw: str) -> object:
    text = (raw or "").strip()
    if text.startswith("```"):
        import re
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I)
    return json.loads(text)


# Function: _salvage_truncated_json
def _salvage_truncated_json(text: str) -> object | None:
    """Recover a partial result when the model's response was cut off mid-array
    (hit its generation token cap on a large batch) rather than genuinely
    malformed. Every agent's schema (spec §5) is a single top-level key holding
    an array of items, so this scans for the outermost array, tracks bracket
    depth to find the last item whose closing `}` is fully balanced, and
    reparses just that much — trading the tail item(s) that never finished
    for keeping everything the model did complete (spec §5 rule 1: 'Never
    silently drop')."""
    array_start = text.find("[")
    if array_start == -1:
        return None
    prefix = text[:array_start]

    depth = 0
    array_depth = 0
    in_string = False
    escape = False
    last_item_end = None
    for i, ch in enumerate(text[array_start:], start=array_start):
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "[":
            array_depth += 1
        elif ch == "]":
            array_depth -= 1
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and array_depth == 1:
                last_item_end = i

    if last_item_end is None:
        return None
    salvaged = f"{prefix}{text[array_start:last_item_end + 1]}]}}"
    try:
        return json.loads(salvaged)
    except json.JSONDecodeError:
        return None


# Function: call_agent_llm
async def call_agent_llm(
    provider: LLMProvider,
    session: AsyncSession,
    *,
    agent_name: str,
    system: str,
    user: str,
    pipeline_run_id: uuid.UUID | None,
    max_tokens: int = AGENT_MAX_TOKENS,
    progress: Callable[[int], Awaitable[None]] | None = None,
) -> tuple[object, list[str]]:
    """One map-reduce batch call. On a schema/JSON failure, retries once with the
    error appended to the prompt; on a second failure, returns (None, warnings) so the
    caller can mark that batch's items FAILED rather than silently dropping them
    (spec §5 rule 1: 'Never silently drop.')."""
    warnings: list[str] = []
    current_user = user
    for attempt in range(2):
        response = await provider.generate(
            system, current_user, temperature=AGENT_TEMPERATURE,
            max_tokens=max_tokens, progress=progress,
        )
        try:
            parsed = _extract_json(response.text)
        except (json.JSONDecodeError, ValidationError) as exc:
            # Salvage any fully closed items before the malformed tail. Ollama
            # often produces a mostly-valid batch and then corrupts one later string
            # or gets clipped by the token cap; in either case, dropping the whole
            # batch is unnecessarily brittle.
            hit_token_cap = response.completion_tokens >= max_tokens
            salvaged = _salvage_truncated_json(response.text)
            if salvaged is not None:
                await record_llm_call(
                    session, pipeline_run_id=pipeline_run_id, agent_name=agent_name,
                    response=response, retry_count=attempt, schema_valid=True,
                    system=system, user_prompt=current_user,
                )
                if hit_token_cap:
                    warnings.append(
                        f"{agent_name}: response hit the {max_tokens}-token cap and was truncated; "
                        f"recovered the items that finished before the cutoff"
                    )
                else:
                    warnings.append(
                        f"{agent_name}: response contained malformed JSON after some complete items; "
                        f"recovered the items that finished before the failure"
                    )
                return salvaged, warnings
            await record_llm_call(
                session, pipeline_run_id=pipeline_run_id, agent_name=agent_name,
                response=response, retry_count=attempt, schema_valid=False,
                system=system, user_prompt=current_user,
            )
            warnings.append(f"{agent_name}: JSON parse failure on attempt {attempt + 1}: {exc}")
            current_user = (
                f"{user}\n\nYour previous response failed to parse as JSON: {exc}\n"
                f"Return ONLY valid JSON matching the schema, nothing else."
            )
            continue
        await record_llm_call(
            session, pipeline_run_id=pipeline_run_id, agent_name=agent_name,
            response=response, retry_count=attempt, schema_valid=True,
            system=system, user_prompt=current_user,
        )
        return parsed, warnings
    logger.warning("%s: batch failed after retry, marking items FAILED", agent_name)
    return None, warnings


# Function: batched
def batched(items: list, batch_size: int):
    for i in range(0, len(items), batch_size):
        yield items[i : i + batch_size]
