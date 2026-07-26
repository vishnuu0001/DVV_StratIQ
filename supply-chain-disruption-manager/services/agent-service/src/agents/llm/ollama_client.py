# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Minimal async client for a local Ollama chat completion call.
# Date: 2026-06-20
# ---------------------------------------------------------------------------
"""Minimal async client for a local Ollama chat completion call."""
from __future__ import annotations

import httpx


class OllamaResult:
    # Function: __init__
    def __init__(self, text: str, prompt_tokens: int, completion_tokens: int) -> None:
        self.text = text
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


# Function: chat
async def chat(
    base_url: str,
    model: str,
    system: str,
    user: str,
    max_tokens: int = 2048,
    timeout: float = 120.0,
) -> OllamaResult:
    """Call Ollama's /api/chat endpoint and return the response text plus token counts."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "options": {"num_predict": max_tokens},
    }
    async with httpx.AsyncClient(base_url=base_url, timeout=timeout) as client:
        response = await client.post("/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()

    return OllamaResult(
        text=data.get("message", {}).get("content", ""),
        prompt_tokens=data.get("prompt_eval_count", 0),
        completion_tokens=data.get("eval_count", 0),
    )
