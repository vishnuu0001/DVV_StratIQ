# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Shared Ollama plumbing — model resolution, JSON-only prompting, robust
# Date: 2026-07-15
# ---------------------------------------------------------------------------
"""Shared Ollama plumbing — model resolution, JSON-only prompting, robust
parsing. Extracted from wave_llm_service.py (a pure move, no behavior change)
so financial_llm_service.py doesn't duplicate it. Both feature-specific LLM
services import from here rather than talking to Ollama directly."""
from __future__ import annotations

import json
from typing import Any

import httpx

from config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT_SECONDS

PREFERRED_OLLAMA_MODELS = [
    "qwen3.5:9b",
    "qwen2.5:7b",
    "mistral:latest",
    "llama3.1:8b",
    "llama2:latest",
]

# Ollama options tuned for NVIDIA A10-8Q (7 GB VRAM) — matches Dashboard's convention.
OLLAMA_GPU_OPTIONS_BASE = {
    "num_ctx": 4096,
    "num_batch": 512,
    "num_gpu": 99,
}


# Function: extract_json_object
def extract_json_object(text: str) -> dict[str, Any]:
    text = (text or "").strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
        raise


# Function: get_available_ollama_models
def get_available_ollama_models(base_url: str = OLLAMA_BASE_URL, timeout: float = 10.0) -> list[str]:
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(f"{base_url}/api/tags")
            resp.raise_for_status()
            payload = resp.json() if isinstance(resp.json(), dict) else {}
            models = payload.get("models", [])
            names = [str(m.get("name", "")).strip() for m in models if isinstance(m, dict)]
            return [n for n in names if n]
    except Exception:
        return []


# Function: resolve_ollama_model
def resolve_ollama_model(configured_model: str = OLLAMA_MODEL, base_url: str = OLLAMA_BASE_URL, timeout: float = 10.0) -> str:
    installed = get_available_ollama_models(base_url=base_url, timeout=timeout)
    if not installed:
        return configured_model

    configured = str(configured_model or "").strip()
    if configured in installed:
        return configured

    cfg_base = configured.split(":")[0].lower() if configured else ""
    if cfg_base:
        for model_name in installed:
            if model_name.split(":")[0].lower() == cfg_base:
                return model_name

    for preferred in PREFERRED_OLLAMA_MODELS:
        if preferred in installed:
            return preferred

    return installed[0]


# Function: call_ollama
def call_ollama(prompt: str, model: str, num_predict: int) -> str:
    with httpx.Client(timeout=OLLAMA_TIMEOUT_SECONDS) as client:
        resp = client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "keep_alive": "30m",
                "format": "json",
                "options": {
                    **OLLAMA_GPU_OPTIONS_BASE,
                    "temperature": 0.2,
                    "num_predict": num_predict,
                },
            },
        )
        resp.raise_for_status()
        return resp.json().get("response", "")
