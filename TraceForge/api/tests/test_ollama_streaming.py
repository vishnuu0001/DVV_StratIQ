# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/tests (test_ollama_streaming.py)
# Date: 2026-05-27
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Scope: TraceForge — Ollama streaming generation regression coverage
# ---------------------------------------------------------------------------
from __future__ import annotations

from traceforge.llm.ollama import OllamaProvider


class _FakeResponse:
    # Function: raise_for_status
    def raise_for_status(self) -> None:
        return None

    # Function: aiter_lines
    async def aiter_lines(self):
        yield '{"message":{"content":"{\\"requirements\\":"},"done":false}'
        yield '{"message":{"content":"[]}"},"done":true,"prompt_eval_count":12,"eval_count":3}'


class _FakeStream:
    # Function: __aenter__
    async def __aenter__(self):
        return _FakeResponse()

    # Function: __aexit__
    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeClient:
    last_body: dict | None = None

    # Function: __init__
    def __init__(self, *, timeout: float):
        self.timeout = timeout

    # Function: __aenter__
    async def __aenter__(self):
        return self

    # Function: __aexit__
    async def __aexit__(self, exc_type, exc, tb):
        return False

    # Function: stream
    def stream(self, method: str, url: str, *, json: dict):
        assert method == "POST"
        assert url.endswith("/api/chat")
        _FakeClient.last_body = json
        return _FakeStream()


# Function: test_generate_assembles_streamed_ollama_events
async def test_generate_assembles_streamed_ollama_events(monkeypatch):
    monkeypatch.setattr("traceforge.llm.ollama.httpx.AsyncClient", _FakeClient)
    progress_updates: list[int] = []

    # Function: progress
    async def progress(chunks: int) -> None:
        progress_updates.append(chunks)

    response = await OllamaProvider(model="test-model").generate(
        "system", "user", temperature=0.2, max_tokens=100, json_mode=True, progress=progress,
    )

    assert _FakeClient.last_body is not None
    assert _FakeClient.last_body["stream"] is True
    assert _FakeClient.last_body["format"] == "json"
    assert response.text == '{"requirements":[]}'
    assert response.prompt_tokens == 12
    assert response.completion_tokens == 3
    assert progress_updates == [2]
