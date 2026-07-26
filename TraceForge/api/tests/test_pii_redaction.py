# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §6.3 PERSIST_LLM_IO — prompt/completion text is only ever persisted after a
#   successful PII redaction pass; redaction being unavailable must fail closed
#   (skip persistence), never fall back to writing raw text.
# Date: 2026-07-24
# ---------------------------------------------------------------------------
from __future__ import annotations

import uuid

from traceforge.llm import metering
from traceforge.llm.provider import LLMResponse
from traceforge.security import pii


# Function: test_redact_pii_returns_empty_map_for_empty_text
async def test_redact_pii_returns_empty_map_for_empty_text():
    assert pii.redact_pii("") == ("", {})


# Function: test_redact_pii_fails_closed_when_engines_unavailable
def test_redact_pii_fails_closed_when_engines_unavailable(monkeypatch):
    # Function: _boom
    def _boom():
        raise RuntimeError("spaCy model not installed")

    monkeypatch.setattr(pii, "_get_engines", _boom)
    assert pii.redact_pii("Contact Jane Doe at jane@example.com") is None


# Function: test_record_llm_call_skips_prompt_persistence_when_flag_off
async def test_record_llm_call_skips_prompt_persistence_when_flag_off(session, monkeypatch):
    monkeypatch.setattr(metering, "PERSIST_LLM_IO", False)
    response = LLMResponse(text="output", model="test", prompt_tokens=1, completion_tokens=1, latency_ms=1)

    await metering.record_llm_call(
        session, pipeline_run_id=None, agent_name="test_agent", response=response,
        system="system prompt", user_prompt="user prompt",
    )
    added = next(obj for obj in session.new if type(obj).__name__ == "LLMCall")
    assert added.prompt_text is None
    assert added.completion_text is None
    assert added.pii_entity_map == {}


# Function: test_record_llm_call_persists_redacted_text_when_flag_on
async def test_record_llm_call_persists_redacted_text_when_flag_on(session, monkeypatch):
    monkeypatch.setattr(metering, "PERSIST_LLM_IO", True)

    # Function: fake_redact
    def fake_redact(text: str):
        return f"REDACTED[{len(text)}]", {"PERSON": ["Jane Doe"]}

    monkeypatch.setattr(metering, "redact_pii", fake_redact)
    response = LLMResponse(text="Jane Doe's account was flagged.", model="test", prompt_tokens=1, completion_tokens=1, latency_ms=1)

    await metering.record_llm_call(
        session, pipeline_run_id=None, agent_name="test_agent", response=response,
        system="system prompt", user_prompt="user prompt",
    )
    added = next(obj for obj in session.new if type(obj).__name__ == "LLMCall")
    assert added.prompt_text.startswith("REDACTED[")
    assert added.completion_text.startswith("REDACTED[")
    assert added.pii_entity_map == {"prompt": {"PERSON": ["Jane Doe"]}, "completion": {"PERSON": ["Jane Doe"]}}


# Function: test_record_llm_call_skips_persistence_when_redaction_unavailable
async def test_record_llm_call_skips_persistence_when_redaction_unavailable(session, monkeypatch):
    monkeypatch.setattr(metering, "PERSIST_LLM_IO", True)
    monkeypatch.setattr(metering, "redact_pii", lambda text: None)
    response = LLMResponse(text="Jane Doe's account was flagged.", model="test", prompt_tokens=1, completion_tokens=1, latency_ms=1)

    await metering.record_llm_call(
        session, pipeline_run_id=None, agent_name="test_agent", response=response,
        system="system prompt", user_prompt="user prompt",
    )
    added = next(obj for obj in session.new if type(obj).__name__ == "LLMCall")
    assert added.prompt_text is None
    assert added.completion_text is None
    assert added.pii_entity_map == {}
