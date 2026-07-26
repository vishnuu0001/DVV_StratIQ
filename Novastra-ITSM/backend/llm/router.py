# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: LLM router — returns the appropriate LangChain chat model
# Date: 2025-08-20
# ---------------------------------------------------------------------------
"""
LLM router — returns the appropriate LangChain chat model
based on the selected provider ("ollama" or "openai").
"""
import logging
from functools import lru_cache
from typing import Any, Optional

import httpx

from backend.config import (
    OLLAMA_BASE_URL,
    OLLAMA_KEEP_ALIVE,
    OLLAMA_MODEL,
    OLLAMA_NUM_CTX,
    OLLAMA_NUM_GPU,
    OLLAMA_NUM_PREDICT,
    OLLAMA_REQUIRE_GPU,
    OLLAMA_TIMEOUT_SECONDS,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)

logger = logging.getLogger(__name__)


# Function: _timeout_seconds
def _timeout_seconds() -> float:
    return max(2.0, min(10.0, float(OLLAMA_TIMEOUT_SECONDS) / 12.0))


# Function: _is_gpu_active
def _is_gpu_active(model_payload: dict[str, Any]) -> bool:
    details = model_payload.get("details") if isinstance(model_payload.get("details"), dict) else {}
    proc = details if details else model_payload
    gpu_fields = (
        proc.get("gpu"),
        proc.get("gpu_layers"),
        proc.get("num_gpu"),
        proc.get("n_gpu_layers"),
        proc.get("size_vram"),
        model_payload.get("size_vram"),
        model_payload.get("vram"),
    )
    if any(isinstance(v, (int, float)) and v > 0 for v in gpu_fields):
        return True

    processor = str(proc.get("processor") or details.get("processor") or "").lower()
    return "gpu" in processor and "cpu" not in processor


# Function: _select_ollama_model
def _select_ollama_model(models: list[Any], preferred_model: Optional[str]) -> dict[str, Any]:
    """Pick the model matching preferred_model (by exact name or name:tag prefix),
    falling back to whichever entry Ollama reports as active."""
    if preferred_model:
        preferred_lower = preferred_model.lower()
        for item in models:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "").lower()
            if name == preferred_lower or name.startswith(preferred_lower + ":"):
                return item
    return models[0] if isinstance(models[0], dict) else {}


# Function: get_ollama_runtime_status
def get_ollama_runtime_status(preferred_model: Optional[str] = None) -> dict[str, Any]:
    """Return Ollama runtime health and whether active model appears GPU-backed."""
    status: dict[str, Any] = {
        "reachable": False,
        "model_loaded": False,
        "gpu_active": None,
        "active_model": None,
    }
    try:
        with httpx.Client(timeout=_timeout_seconds()) as client:
            ps_resp = client.get(f"{OLLAMA_BASE_URL.rstrip('/')}/api/ps")
            if ps_resp.status_code >= 400:
                return status

            status["reachable"] = True
            payload = ps_resp.json() if ps_resp.content else {}
            models = payload.get("models") or []
            if not isinstance(models, list) or not models:
                return status

            selected = _select_ollama_model(models, preferred_model)
            status["model_loaded"] = True
            status["active_model"] = selected.get("name")
            status["gpu_active"] = _is_gpu_active(selected)
            return status
    except Exception:
        return status


# Function: _warm_ollama_model
def _warm_ollama_model(model_name: str) -> None:
    """Force-load model so runtime GPU state can be verified before serving traffic."""
    with httpx.Client(timeout=max(8.0, float(OLLAMA_TIMEOUT_SECONDS))) as client:
        client.post(
            f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate",
            json={
                "model": model_name,
                "prompt": "healthcheck",
                "stream": False,
                "keep_alive": OLLAMA_KEEP_ALIVE,
                "options": {
                    "num_predict": 1,
                    "num_gpu": OLLAMA_NUM_GPU,
                    "num_ctx": min(1024, OLLAMA_NUM_CTX),
                },
            },
        ).raise_for_status()


# Function: assert_ollama_gpu_available
def assert_ollama_gpu_available(model_name: Optional[str] = None) -> None:
    """Raise when GPU-only mode is enabled but Ollama is not actively using GPU."""
    if not OLLAMA_REQUIRE_GPU:
        return

    if OLLAMA_NUM_GPU == 0:
        raise RuntimeError("OLLAMA_REQUIRE_GPU=true but OLLAMA_NUM_GPU=0 disables GPU usage.")

    target_model = model_name or OLLAMA_MODEL
    runtime = get_ollama_runtime_status(target_model)
    if not runtime.get("reachable"):
        raise RuntimeError("OLLAMA_REQUIRE_GPU=true but Ollama runtime is unreachable.")

    # If model is not loaded yet, warm it once and re-check runtime mode.
    if not runtime.get("model_loaded"):
        _warm_ollama_model(target_model)
        runtime = get_ollama_runtime_status(target_model)

    if not runtime.get("model_loaded"):
        raise RuntimeError(
            f"OLLAMA_REQUIRE_GPU=true but model '{target_model}' is not loaded in Ollama runtime."
        )

    if runtime.get("gpu_active") is not True:
        active_model = runtime.get("active_model") or target_model
        raise RuntimeError(
            "OLLAMA_REQUIRE_GPU=true but Ollama model "
            f"'{active_model}' is not running with GPU acceleration."
        )


# Function: get_llm
@lru_cache(maxsize=4)
def get_llm(provider: str) -> Any:
    """
    Returns a cached LangChain chat model.
    provider: "ollama" | "openai"
    Raises ValueError if OpenAI is requested without a key.
    """
    if provider == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key is not configured. Set OPENAI_API_KEY in .env.")
        from langchain_openai import ChatOpenAI
        logger.info("Using OpenAI LLM: %s", OPENAI_MODEL)
        return ChatOpenAI(
            model=OPENAI_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.0,        # Zero temperature — grounded RAG answers, no hallucination
            max_tokens=2048,
        )

    # Default: Ollama
    from langchain_ollama import ChatOllama
    assert_ollama_gpu_available(OLLAMA_MODEL)
    logger.info(
        "Using Ollama LLM: %s @ %s (num_gpu=%s, num_ctx=%s, num_predict=%s, timeout=%ss)",
        OLLAMA_MODEL,
        OLLAMA_BASE_URL,
        OLLAMA_NUM_GPU,
        OLLAMA_NUM_CTX,
        OLLAMA_NUM_PREDICT,
        OLLAMA_TIMEOUT_SECONDS,
    )
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.0,    # Zero temperature — deterministic, grounded responses
        num_predict=OLLAMA_NUM_PREDICT,
        num_gpu=OLLAMA_NUM_GPU,
        num_ctx=OLLAMA_NUM_CTX,
        repeat_penalty=1.15,  # Penalise repeated tokens — reduces verbosity and hallucination loops
        top_k=10,           # Narrow candidate pool at each token position for precision
        top_p=0.9,          # Nucleus sampling complement to top_k
        timeout=OLLAMA_TIMEOUT_SECONDS,
        keep_alive=OLLAMA_KEEP_ALIVE,
    )
    return llm


# Function: clear_llm_cache
def clear_llm_cache():
    get_llm.cache_clear()
