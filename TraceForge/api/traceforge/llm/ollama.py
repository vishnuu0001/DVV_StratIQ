# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/traceforge/llm (ollama.py)
# Date: 2025-08-29
# ---------------------------------------------------------------------------
from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import Awaitable, Callable

import httpx

from traceforge.config import OLLAMA_BASE_URL, OLLAMA_EMBED_MODEL, OLLAMA_MODEL, OLLAMA_NUM_CTX, OLLAMA_TIMEOUT_SECONDS
from traceforge.llm.provider import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)

# This Ollama instance is shared across every module on the box (Modernization,
# InfraRationalization, TraceForge, ...) on a single ~8GB GPU — a large model load
# elsewhere (e.g. Modernization's qwen2.5-coder:14b) can starve or stall a request
# here for minutes even though the request itself is trivial (confirmed empirically:
# a single-string nomic-embed-text call went from 0.04s uncontended to a full
# 600s ReadTimeout while a 14b model was loaded). Retrying with backoff turns that
# transient contention into a delay instead of a hard pipeline-stage failure.
_RETRY_ATTEMPTS = 3
_RETRY_BACKOFF_SECONDS = [3, 8, 20]
_TRANSIENT_EXCEPTIONS = (httpx.TimeoutException, httpx.ConnectError, httpx.ReadError)


# Function: _post_with_retry
async def _post_with_retry(url: str, json_body: dict, *, timeout: float, label: str) -> dict:
    last_exc: Exception | None = None
    for attempt in range(_RETRY_ATTEMPTS):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, json=json_body)
                resp.raise_for_status()
                return resp.json()
        except _TRANSIENT_EXCEPTIONS as exc:
            last_exc = exc
            if attempt < _RETRY_ATTEMPTS - 1:
                wait = _RETRY_BACKOFF_SECONDS[attempt]
                logger.warning(
                    "%s: transient failure on attempt %d/%d (%s) — retrying in %ds",
                    label, attempt + 1, _RETRY_ATTEMPTS, type(exc).__name__, wait,
                )
                await asyncio.sleep(wait)
    raise RuntimeError(f"{label}: failed after {_RETRY_ATTEMPTS} attempts") from last_exc


# Function: _consume_ndjson_line
async def _consume_ndjson_line(
    line: str, label: str, content: list[str], response_chunks: int,
    progress: Callable[[int], Awaitable[None]] | None,
) -> tuple[int, dict | None]:
    """Handle one NDJSON line; returns (updated response_chunks, final-event-or-None)."""
    event = json.loads(line)
    if event.get("error"):
        raise RuntimeError(f"{label}: {event['error']}")
    content.append(event.get("message", {}).get("content", ""))
    response_chunks += 1
    if progress and response_chunks % 50 == 0:
        await progress(response_chunks)
    return response_chunks, (event if event.get("done") else None)


# Function: _stream_chat_once
async def _stream_chat_once(
    url: str, json_body: dict, *, timeout: float, label: str,
    progress: Callable[[int], Awaitable[None]] | None,
) -> dict:
    content: list[str] = []
    final: dict = {}
    response_chunks = 0
    async with httpx.AsyncClient(timeout=timeout) as client:
        async with client.stream("POST", url, json=json_body) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                response_chunks, done_event = await _consume_ndjson_line(line, label, content, response_chunks, progress)
                if done_event is not None:
                    final = done_event
    if progress:
        await progress(response_chunks)
    final["message"] = {"content": "".join(content)}
    return final


# Function: _stream_chat_with_retry
async def _stream_chat_with_retry(
    url: str, json_body: dict, *, timeout: float, label: str,
    progress: Callable[[int], Awaitable[None]] | None = None,
) -> dict:
    """Consume Ollama's NDJSON stream so long generations do not hit a timeout
    merely because no response body is returned until the full completion is ready."""
    last_exc: Exception | None = None
    for attempt in range(_RETRY_ATTEMPTS):
        try:
            return await _stream_chat_once(url, json_body, timeout=timeout, label=label, progress=progress)
        except _TRANSIENT_EXCEPTIONS as exc:
            last_exc = exc
            if attempt < _RETRY_ATTEMPTS - 1:
                wait = _RETRY_BACKOFF_SECONDS[attempt]
                logger.warning(
                    "%s: transient streaming failure on attempt %d/%d (%s) — retrying in %ds",
                    label, attempt + 1, _RETRY_ATTEMPTS, type(exc).__name__, wait,
                )
                await asyncio.sleep(wait)
    raise RuntimeError(f"{label}: failed after {_RETRY_ATTEMPTS} streaming attempts") from last_exc


class OllamaProvider(LLMProvider):
    # Function: __init__
    def __init__(self, model: str | None = None, base_url: str | None = None):
        self.model = model or OLLAMA_MODEL
        self.base_url = (base_url or OLLAMA_BASE_URL).rstrip("/")

    # Function: generate
    async def generate(
        self, system: str, user: str, *, temperature: float, max_tokens: int,
        json_mode: bool = True, progress: Callable[[int], Awaitable[None]] | None = None,
    ) -> LLMResponse:
        started = time.monotonic()
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            # Ollama's non-streaming mode sends no bytes until the entire response
            # is complete. Large extraction batches can legitimately exceed the
            # read timeout, causing the same expensive batch to restart repeatedly.
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_ctx": OLLAMA_NUM_CTX,
            },
        }
        if json_mode:
            body["format"] = "json"
        payload = await _stream_chat_with_retry(
            f"{self.base_url}/api/chat",
            body,
            timeout=OLLAMA_TIMEOUT_SECONDS,
            label=f"generate[{self.model}]",
            progress=progress,
        )
        latency_ms = int((time.monotonic() - started) * 1000)
        return LLMResponse(
            text=payload.get("message", {}).get("content", ""),
            model=self.model,
            prompt_tokens=int(payload.get("prompt_eval_count") or 0),
            completion_tokens=int(payload.get("eval_count") or 0),
            latency_ms=latency_ms,
        )

    # Function: embed
    async def embed(self, texts: list[str]) -> list[list[float]]:
        # Embedding a handful of chunks is normally sub-second (confirmed: ~0.04s
        # uncontended) — a short per-attempt timeout means contention shows up as a
        # few quick retries instead of blocking the whole ingest job for 10 minutes.
        #
        # keep_alive=30s (Ollama's multi-minute default otherwise applies): extraction
        # now calls embed() and generate() close together every RAG-augmented batch, so
        # the default keep_alive kept BOTH nomic-embed-text and qwen2.5-coder:7b loaded
        # simultaneously for the whole run on an 8GB GPU with nothing free — confirmed
        # empirically (283MB free, a trivial embed call took 14.5s instead of ~0.04s,
        # and under sustained load timed out after 3 retries). Evicting the small embed
        # model quickly frees that headroom for the much larger generate model between
        # the infrequent embed calls; the reload cost for a 323MB model is negligible
        # next to a multi-second contention stall.
        payload = await _post_with_retry(
            f"{self.base_url}/api/embed",
            {"model": OLLAMA_EMBED_MODEL, "input": texts, "keep_alive": "30s"},
            timeout=60,
            label="embed",
        )
        return payload.get("embeddings", [])
