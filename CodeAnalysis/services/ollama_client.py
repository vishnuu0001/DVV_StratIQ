# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Thin wrapper around the Ollama Python SDK.
# Date: 2026-02-03
# ---------------------------------------------------------------------------
"""
services/ollama_client.py
--------------------------
Thin wrapper around the Ollama Python SDK.

Responsibilities
~~~~~~~~~~~~~~~~
* Health-check / connectivity test
* List locally installed models
* Pull (download) a model in the background with progress reporting
* Synchronous and streaming chat/generate calls
* Model selection priority: Qwen 2.5 14B → CodeLlama 13b → DeepSeek-Coder 6.7b → Llama 3.2 3b (fastest fallback)

Performance notes
~~~~~~~~~~~~~~~~~
* num_gpu=99   — forces all transformer layers onto the GPU (Ollama/llama.cpp
                  treats this as n-gpu-layers; 99 > any real model's layer count).
* use_mmap=True — memory-maps weight files so successive calls reuse OS page cache.
* keep_alive="-1" — instructs Ollama to keep the model hot in VRAM indefinitely
                  between requests (avoids the ~30-60 s reload penalty each call).
* num_ctx tuned per call — 32 768 tokens creates a ~5 GB KV-cache on a 12 GB GPU;
                  each service now passes the smallest ctx that fits its prompt.
* Timeout pool reuse — a single module-level ThreadPoolExecutor (_TIMEOUT_POOL)
                  is created once; per-call pool creation was ~5 ms overhead × N calls.
"""
from __future__ import annotations

import concurrent.futures as _cf
import logging
import threading
from typing import Any

import httpx
import ollama as _ollama

# Module-level pool reused for all timeout-gated generate() calls.
# Creating a new ThreadPoolExecutor per call added measurable overhead across
# the 6+ parallel AI analyses run for each repo analysis.
_TIMEOUT_POOL = _cf.ThreadPoolExecutor(max_workers=4, thread_name_prefix="ollama_timeout")

# Global serialization lock for all Ollama LLM calls.
# Sub-analyses within a module dispatch their preprocessing (file scanning,
# radon, anti-pattern) in parallel, but LLM inference is single-GPU and must
# run one at a time. Without this lock, parallel sub-analyses all queue inside
# Ollama simultaneously: the last call in the queue waits (N-1) * generation_time
# before starting, causing timeouts even when individual generation is fast.
_OLLAMA_LOCK = threading.Lock()

logger = logging.getLogger(__name__)

# ── Recommended models ordered by accuracy for code tasks ───────────────────
RECOMMENDED_MODELS: list[dict] = [
    {
        "id":   "qwen3.5:9b",
        "name": "Qwen 3.5 9B",
        "desc": "Shared default model. Strong at reasoning and multi-language refactoring; fits fully in the 12 GB GPU.",
        "size": "~6.6 GB",
    },
    {
        "id":   "codellama:13b",
        "name": "CodeLlama 13B",
        "desc": "Meta's code-focused LLM. Best accuracy for call-graph and tech-debt reasoning.",
        "size": "~7 GB",
    },
    {
        "id":   "deepseek-coder:6.7b",
        "name": "DeepSeek-Coder 6.7B",
        "desc": "Highest accuracy-per-GB for code understanding and refactoring tasks.",
        "size": "~4 GB",
    },
    {
        "id":   "llama3.1:8b",
        "name": "Llama 3.1 8B",
        "desc": "General reasoning. Good for business-rule extraction and documentation.",
        "size": "~5 GB",
    },
    {
        "id":   "llama3.2:3b",
        "name": "Llama 3.2 3B",
        "desc": "Fast fallback for low-VRAM environments. Lower accuracy.",
        "size": "~2 GB",
    },
]

_DEFAULT_HOST = "http://localhost:11434"

# ── Module-level model-id cache ───────────────────────────────────────────────
# best_available_model() was calling self._client.list() (HTTP round-trip to
# Ollama) on every single AI service call — 6-7 calls per analysis run.
# Cache the resolved model id with a 5-minute TTL so the list() call happens
# at most once per analysis batch, not once per service module invocation.
import time as _time
_model_cache: dict = {"model": None, "expires": 0.0}


class OllamaClient:
    """High-level Ollama interface used by all AI services."""

    # Function: __init__
    def __init__(self, host: str = _DEFAULT_HOST):
        self.host   = host
        # Pass timeout directly as kwargs — ollama.Client forwards them to httpx.Client.
        # 600s covers worst-case token generation (700-1000 tokens on single GPU).
        self._client = _ollama.Client(host=host, timeout=600.0)

    # ── Connectivity ─────────────────────────────────────────────────────────

    # Function: health
    def health(self) -> dict:
        """Return {ok, version, host} or {ok: False, error: ...}."""
        try:
            resp = httpx.get(f"{self.host}/api/version", timeout=5)
            resp.raise_for_status()
            return {"ok": True, "version": resp.json().get("version", "unknown"), "host": self.host}
        except Exception as exc:
            return {"ok": False, "error": str(exc), "host": self.host}

    # ── Model management ─────────────────────────────────────────────────────

    # Function: list_models
    def list_models(self) -> list[dict]:
        """Return a list of locally installed models enriched with recommended metadata."""
        try:
            local = self._client.list()
            installed_ids = {m.model for m in local.models}
            enriched = []
            for rec in RECOMMENDED_MODELS:
                entry = {**rec}
                # Normalize: strip tags like :latest before checking
                entry["installed"] = any(
                    rec["id"].split(":")[0] in mid for mid in installed_ids
                ) or rec["id"] in installed_ids
                enriched.append(entry)

            # Also surface any locally installed models not in recommended list
            known_ids = {r["id"] for r in RECOMMENDED_MODELS}
            known_bases = {r["id"].split(":")[0] for r in RECOMMENDED_MODELS}
            for m in local.models:
                base = m.model.split(":")[0]
                if base not in known_bases and m.model not in known_ids:
                    enriched.append({
                        "id":        m.model,
                        "name":      m.model,
                        "desc":      "Locally installed model",
                        "size":      f"{round(m.size / 1e9, 1)} GB" if m.size else "?",
                        "installed": True,
                    })
            return enriched
        except Exception as exc:
            logger.error("list_models error: %s", exc)
            return []

    # Function: best_available_model
    def best_available_model(self) -> str | None:
        """Return the id of the best locally installed recommended model.

        Result is cached for 5 minutes to avoid repeated HTTP calls to Ollama
        on every AI service invocation during a single analysis batch.
        """
        global _model_cache
        now = _time.monotonic()
        if _model_cache["model"] is not None and now < _model_cache["expires"]:
            return _model_cache["model"]
        try:
            local_models = self._client.list()
            installed_ids = {m.model for m in local_models.models}

            selected: str | None = None
            for rec in RECOMMENDED_MODELS:
                rec_id = rec["id"]
                base   = rec_id.split(":")[0]
                if rec_id in installed_ids:
                    selected = rec_id
                    break
                # Accept any tag of the same base model
                for mid in installed_ids:
                    if mid.startswith(base + ":") or mid == base:
                        selected = mid
                        break
                if selected:
                    break
            _model_cache = {"model": selected, "expires": now + 300.0}  # 5-min TTL
            return selected
        except Exception:
            return None

    # Function: pull_model
    def pull_model(self, model_id: str, progress_callback=None) -> dict:
        """Pull a model from Ollama registry. Blocks until done. Returns {ok, model_id, error?}."""
        try:
            for chunk in self._client.pull(model_id, stream=True):
                if progress_callback:
                    status  = getattr(chunk, "status", "")
                    total   = getattr(chunk, "total",  0) or 0
                    completed = getattr(chunk, "completed", 0) or 0
                    progress_callback(status, total, completed)
            return {"ok": True, "model_id": model_id}
        except Exception as exc:
            return {"ok": False, "model_id": model_id, "error": str(exc)}

    # ── Generation ───────────────────────────────────────────────────────────

    # Function: generate
    def generate(
        self,
        prompt: str,
        model: str | None = None,
        system: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 8192,
        json_mode: bool = False,
        num_ctx: int = 10240,
        timeout: float = 0,
    ) -> str:
        """Single-shot generation. Returns the response text.

        Parameters
        ----------
        temperature : float
            0.0 = greedy decoding — fully deterministic, no sampling overhead,
            lowest hallucination risk for structured JSON tasks.
        max_tokens : int
            Maximum tokens to generate.  8192 supports large structured JSON
            responses (10+ hotspots, 6+ quick wins, etc.).
        json_mode : bool
            Pass format="json" to Ollama, constraining output to valid JSON.
        num_ctx : int
            Context window (input + output tokens combined).  The actual value
            is clamped to max(4096, estimated_input_tokens + max_tokens + 512)
            so small prompts never over-allocate the KV-cache.
            Callers pass an upper-bound; this method shrinks it if the prompt fits
            in a smaller window (quadratic attention cost reduction).
        timeout : float
            If > 0, wrap the call in a future with this timeout in seconds.
        """
        use_model = model or self.best_available_model()
        if not use_model:
            raise RuntimeError(
                "No Ollama model installed. Pull one of: "
                + ", ".join(r["id"] for r in RECOMMENDED_MODELS[:3])
            )
        messages: list[dict] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # Adaptive num_ctx: shrink context window to the minimum needed for this
        # specific prompt so that attention computation (quadratic in ctx length)
        # is not wasted on KV-cache slots that will never be used.
        # ~3 chars per token for mixed code/prose; 512 token safety margin.
        estimated_input_tokens = (len(prompt) + len(system or "")) // 3
        adaptive_ctx = max(4096, estimated_input_tokens + max_tokens + 512)
        effective_ctx = min(num_ctx, adaptive_ctx)

        options = self._build_ollama_options(temperature, max_tokens, effective_ctx)

        kwargs: dict = dict(model=use_model, messages=messages, options=options)
        if json_mode:
            kwargs["format"] = "json"

        try:
            # Serialize all Ollama inference calls globally so parallel
            # sub-analyses don't queue inside Ollama simultaneously.
            # Preprocessing for the next analysis continues while this lock
            # is held, so wall-clock time is still reduced by parallelism.
            with _OLLAMA_LOCK:
                if timeout > 0:
                    # Reuse module-level pool — avoids creating/destroying a thread
                    # pool on every call (was ~5 ms overhead per AI analysis call).
                    fut = _TIMEOUT_POOL.submit(self._client.chat, **kwargs)
                    try:
                        resp = fut.result(timeout=timeout)
                    except _cf.TimeoutError:
                        raise TimeoutError(
                            f"Ollama call timed out after {timeout:.0f}s "
                            f"(model={use_model}, max_tokens={max_tokens}). "
                            f"Heavy load detected — token generation exceeded time limit. "
                            f"Try: (1) reduce num_ctx, (2) lower max_tokens, (3) use faster model."
                        )
                else:
                    resp = self._client.chat(**kwargs)
            return resp.message.content.strip()
        except TimeoutError:
            raise
        except Exception as exc:
            logger.error("generate error (model=%s): %s", use_model, exc)
            raise

    # ── JSON repair helper ───────────────────────────────────────────────────

    # Function: _build_ollama_options
    @staticmethod
    def _build_ollama_options(temperature: float, max_tokens: int, num_ctx: int) -> dict:
        """Build Ollama generation options dict."""
        return {
            "temperature":   temperature,
            "num_predict":   max_tokens,
            "num_ctx":       num_ctx,
            "num_gpu":       99,
            "use_mmap":      True,
            "keep_alive":    -1,
            "use_mlock":     False,
            # Penalise repetition to prevent degenerate output loops that waste
            # tokens without adding content (common at low temperature).
            "repeat_penalty": 1.05,
        }


    # Function: _fix_json_syntax
    @staticmethod
    def _fix_json_syntax(text: str) -> str:
        """Fix common LLM JSON syntax errors before attempting full parse.

        Handles:
        - Trailing commas before } or ]  (very common in LLM output)
        - Missing colon between key and value  e.g. ``"key" "value"``
        - Missing colon before { or [  e.g. ``"key" {``
        """
        import re
        # Fix trailing commas:  ,\n  }  ->  }
        text = re.sub(r",\s*([\}\]])", r"\1", text)
        # Fix missing colon between quoted key and any JSON value token
        text = re.sub(
            r'("(?:[^"\\]|\\.)*")\s+("|-?\d|\{|\[|true\b|false\b|null\b)',
            r'\1: \2',
            text,
        )
        return text

    # Function: _process_repair_char
    @staticmethod
    def _process_repair_char(ch: str, state: dict) -> None:
        if state["escape_next"]:
            state["escape_next"] = False
            return
        if ch == "\\" and state["in_string"]:
            state["escape_next"] = True
            return
        if ch == '"':
            state["in_string"] = not state["in_string"]
            return
        if state["in_string"]:
            return
        if ch in ("{", "["):
            state["stack"].append("}" if ch == "{" else "]")
        elif ch in ("}", "]"):
            if state["stack"] and state["stack"][-1] == ch:
                state["stack"].pop()

    # Function: _repair_json
    @staticmethod
    def _repair_json(text: str) -> str:
        """Attempt to close a JSON object/array truncated mid-stream.

        Walks the string tracking open brackets/braces while respecting quoted
        strings, then appends the missing closing tokens in reverse order.
        """
        state = {"stack": [], "in_string": False, "escape_next": False}
        for ch in text:
            OllamaClient._process_repair_char(ch, state)
        return text + "".join(reversed(state["stack"]))

    # Function: _parse_json_with_fallbacks
    @staticmethod
    def _parse_json_with_fallbacks(raw: str) -> "Any":
        """Clean LLM output and attempt JSON parsing through multiple fallback strategies."""
        import json, re
        cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        fixed = OllamaClient._fix_json_syntax(cleaned)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

        m = re.search(r"(\{.*\}|\[.*\])", fixed, re.DOTALL)
        if m:
            candidate = m.group(1)
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                try:
                    repaired = OllamaClient._repair_json(candidate)
                    return json.loads(repaired)
                except json.JSONDecodeError:
                    pass

        try:
            return json.loads(OllamaClient._repair_json(fixed))
        except json.JSONDecodeError:
            pass

        m2 = re.search(r"(\{.*\}|\[.*\])", cleaned, re.DOTALL)
        if m2:
            try:
                return json.loads(OllamaClient._repair_json(m2.group(1)))
            except json.JSONDecodeError:
                pass

        raise ValueError(f"Model did not return valid JSON. Raw output (first 400 chars): {raw[:400]}")


    # Function: generate_json
    def generate_json(
        self,
        prompt: str,
        model: str | None = None,
        system: str | None = None,
        max_tokens: int = 4096,
        num_ctx: int = 8192,
        timeout: float = 480,
        temperature: float = 0.0,
    ) -> Any:
        """Generate and parse JSON output with one automatic retry on parse failure.

        Uses json_mode=True (Ollama format="json") and caller-specified
        max_tokens / num_ctx so that each analysis can be tuned independently.
        temperature=0.0 gives fully greedy, deterministic decoding — best for
        structured JSON where reproducibility matters more than diversity.

        Retry strategy:
          If the first attempt returns something JSON-like ({...} or [...]) but
          fails all parse repair strategies, a second attempt is made with an
          explicit reminder prepended to the prompt.  The retry is skipped when
          the raw output contains no JSON structure at all (saves a full LLM call
          on catastrophic failures).
        """
        _RETRY_PREFIX = (
            "REMINDER: Output ONLY a valid JSON object matching the schema below. "
            "No prose, no markdown, no triple-backticks. Start with '{' and end with '}'.\n\n"
        )
        for attempt in range(2):
            _prompt = prompt if attempt == 0 else (_RETRY_PREFIX + prompt)
            raw = self.generate(
                _prompt,
                model=model,
                system=system,
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=True,
                num_ctx=num_ctx,
                timeout=timeout,
            )
            try:
                return self._parse_json_with_fallbacks(raw)
            except ValueError:
                if attempt == 0 and ('{' in raw or '[' in raw):
                    logger.warning(
                        "generate_json: malformed JSON on first attempt (raw[:80]=%r), retrying",
                        raw[:80],
                    )
                    continue
                raise ValueError(
                    f"Model did not return valid JSON after {attempt + 1} attempt(s). "
                    f"Raw output (first 400 chars): {raw[:400]}"
                )
