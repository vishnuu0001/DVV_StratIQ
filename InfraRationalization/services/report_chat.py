# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: services/report_chat.py
# Date: 2025-09-24
# ---------------------------------------------------------------------------
"""
services/report_chat.py
"Chat with your report" — a conversational AI assistant grounded in one
specific scan report, so a user can ask plain-language questions ("which
servers are the biggest migration risk?", "summarize the EOS exposure") instead
of reading raw report output.

Reuses the same Ollama model-selection/calling machinery already validated in
services/llm_intelligence.py (GPU-accelerated, auto-selects the best installed
model) rather than duplicating it — this is intentionally the SAME model that
answers infrastructure failure-prediction, just used in a multi-turn chat
shape instead of a single structured-JSON-output shape.
"""
from __future__ import annotations

import logging
from typing import Any

import requests

from services.llm_intelligence import OLLAMA_BASE, _build_infra_data, _get_best_gpu_model

log = logging.getLogger(__name__)

_MAX_HISTORY_TURNS = 8   # cap conversation length fed back to the model — keeps prompts bounded

_SYSTEM_PROMPT_TEMPLATE = """You are an infrastructure migration and cloud cost advisor. You are answering \
questions about ONE SPECIFIC infrastructure scan report — ground every answer in the data below, and say so \
plainly if the report doesn't contain enough information to answer a question (never invent server names, \
counts, or figures that aren't in the data).

SCAN REPORT DATA (JSON):
{infra_json}

Answer conversationally, in plain English, like a knowledgeable colleague — not as JSON, not as a bulleted \
spec sheet unless a list genuinely helps. Keep answers focused and specific to what was asked; reference \
actual server names/counts/figures from the data above where relevant. If asked about something this report \
doesn't cover (e.g. live pricing, a different scan), say so rather than guessing.
"""


# Function: _format_history
def _format_history(history: list[dict[str, str]]) -> str:
    trimmed = history[-_MAX_HISTORY_TURNS * 2:]
    lines = []
    for turn in trimmed:
        role = "User" if turn.get("role") == "user" else "Assistant"
        lines.append(f"{role}: {turn.get('content', '')}")
    return "\n".join(lines)


# Function: _call_ollama_chat
def _call_ollama_chat(model: str, system: str, conversation: str) -> str:
    payload: dict[str, Any] = {
        "model": model,
        "prompt": conversation,
        "system": system,
        "stream": False,
        "options": {
            "temperature": 0.3,   # a bit higher than the structured-analysis calls — conversational, not extraction
            "top_p": 0.9,
            "num_predict": 1200,
            "num_ctx": 12288,     # scan JSON now includes the full unique-package list; default num_ctx truncates it
            "num_gpu": 99,
            "num_thread": 8,
        },
    }
    resp = requests.post(f"{OLLAMA_BASE}/api/generate", json=payload, timeout=120)
    resp.raise_for_status()
    return (resp.json().get("response") or "").strip()


# Function: chat_about_report
def chat_about_report(
    scan_report: dict,
    history: list[dict[str, str]],
    message: str,
) -> dict[str, Any]:
    """
    Returns {"reply": str, "model_used": str|None, "available": bool}.
    Never raises — a failure (Ollama unreachable, malformed report, etc.)
    surfaces as available=False with a clear, honest reply rather than a 500,
    since a chat UI mid-conversation is a poor place for a stack trace.
    """
    model = _get_best_gpu_model()
    if not model:
        return {
            "reply": (
                "The AI assistant needs a local Ollama model to answer questions, and none is currently "
                "reachable. Check that Ollama is running (see the Network Intelligence tab's status "
                "indicator) — the rest of this report's analysis tabs still work normally without it."
            ),
            "model_used": None,
            "available": False,
        }

    try:
        infra_data = _build_infra_data(scan_report)
    except Exception as exc:
        log.warning("report_chat: failed to condense scan report: %s", exc)
        infra_data = {"error": "Could not read this scan's data in detail."}

    import json as _json
    system = _SYSTEM_PROMPT_TEMPLATE.format(infra_json=_json.dumps(infra_data, indent=2, default=str))
    conversation = _format_history(history)
    conversation = f"{conversation}\nUser: {message}\nAssistant:" if conversation else f"User: {message}\nAssistant:"

    try:
        reply = _call_ollama_chat(model, system, conversation)
        if not reply:
            raise ValueError("empty response")
        return {"reply": reply, "model_used": model, "available": True}
    except Exception as exc:
        log.warning("report_chat: Ollama call failed: %s", exc)
        return {
            "reply": "I couldn't reach the AI model just now — please try again in a moment.",
            "model_used": model,
            "available": False,
        }
