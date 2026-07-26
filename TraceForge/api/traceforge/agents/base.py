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
