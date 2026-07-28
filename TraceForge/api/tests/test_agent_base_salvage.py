# ---------------------------------------------------------------------------
# Author: GitHub Copilot
# Scope: TraceForge — LLM JSON salvage regressions
# Date: 2026-07-28
# ---------------------------------------------------------------------------
from __future__ import annotations

from traceforge.agents.base import call_agent_llm
from traceforge.llm.provider import LLMResponse


class _FakeProvider:
    # Function: generate
    async def generate(self, system, user, *, temperature, max_tokens, json_mode=True, progress=None):
        return LLMResponse(
            text=(
                '{"requirements":[{"title":"A","statement":"B","ears_pattern":"UBIQUITOUS","ears_parts":'
                '{"trigger":null,"precondition":null,"system_name":"System","system_response":"Do X"},'
                '"level":"FUNCTIONAL","priority":"SHOULD","rationale":"ok","acceptance_criteria":["1"],'
                '"citations":[{"chunk_id":"chunk-1","quoted_span":"quoted"}]},'
                '{"title":"B","statement":"C","ears_pattern":"UBIQUITOUS","ears_parts":'
                '{"trigger":null,"precondition":null,"system_name":"System","system_response":"Do Y"},'
                '"level":"FUNCTIONAL","priority":"SHOULD","rationale":"broken'
                ']} '
            ),
            model="fake-model",
            prompt_tokens=1,
            completion_tokens=42,
            latency_ms=1,
        )


# Function: test_call_agent_llm_salvages_completed_items_before_malformed_tail
async def test_call_agent_llm_salvages_completed_items_before_malformed_tail(session):
    parsed, warnings = await call_agent_llm(
        _FakeProvider(),
        session,
        agent_name="extractor",
        system="system",
        user="user",
        pipeline_run_id=None,
        max_tokens=100,
    )

    assert isinstance(parsed, dict)
    assert len(parsed["requirements"]) == 1
    assert parsed["requirements"][0]["title"] == "A"
    assert any("malformed JSON" in warning for warning in warnings)


# Function: test_call_agent_llm_repairs_unescaped_quotes_inside_string_fields
async def test_call_agent_llm_repairs_unescaped_quotes_inside_string_fields(session):
    class _BadQuoteProvider:
        async def generate(self, system, user, *, temperature, max_tokens, json_mode=True, progress=None):
            return LLMResponse(
                text=(
                    '{"requirements":[{"title":"A","statement":"B","ears_pattern":"UBIQUITOUS","ears_parts":'
                    '{"trigger":null,"precondition":null,"system_name":"System","system_response":"Do X"},'
                    '"level":"FUNCTIONAL","priority":"SHOULD","rationale":"keep the "quoted" value intact",'
                    '"acceptance_criteria":["1"],"citations":[{"chunk_id":"chunk-1","quoted_span":"quoted"}]}]}'
                ),
                model="fake-model",
                prompt_tokens=1,
                completion_tokens=42,
                latency_ms=1,
            )

    parsed, warnings = await call_agent_llm(
        _BadQuoteProvider(),
        session,
        agent_name="extractor",
        system="system",
        user="user",
        pipeline_run_id=None,
        max_tokens=100,
    )

    assert parsed["requirements"][0]["rationale"] == 'keep the "quoted" value intact'
    assert warnings == []