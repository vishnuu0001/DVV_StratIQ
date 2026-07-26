# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Settings API — runtime configuration of LLM provider and model.
# Date: 2025-08-18
# ---------------------------------------------------------------------------
"""
Settings API — runtime configuration of LLM provider and model.
Changes are applied immediately (LLM cache is cleared).
"""
from fastapi import APIRouter, HTTPException

import backend.config as cfg
from backend.llm.router import clear_llm_cache
from backend.models.schemas import SettingsResponse, SettingsUpdate
from backend.services import settings_store

router = APIRouter(prefix="/api/settings", tags=["Settings"])


# Function: get_settings
@router.get("", response_model=SettingsResponse)
async def get_settings():
    """Read persisted LLM settings from the database (URL/API key encrypted at rest)."""
    saved = settings_store.get_llm_settings()
    return SettingsResponse(
        llm_provider=saved["llm_provider"],
        ollama_model=saved["ollama_model"],
        ollama_base_url=saved["ollama_base_url"],
        openai_model=saved["openai_model"],
        openai_configured=bool(saved["openai_api_key"]),
    )


# Function: update_settings
@router.post("", response_model=SettingsResponse)
async def update_settings(update: SettingsUpdate):
    """Apply runtime LLM settings (no restart required) and persist them to the
    database, encrypted, so they survive a restart instead of reverting to .env."""
    cfg.LLM_PROVIDER = update.llm_provider.value

    if update.ollama_model:
        cfg.OLLAMA_MODEL = update.ollama_model
    if update.ollama_base_url:
        cfg.OLLAMA_BASE_URL = update.ollama_base_url
    if update.openai_api_key is not None:
        cfg.OPENAI_API_KEY = update.openai_api_key
    if update.openai_model:
        cfg.OPENAI_MODEL = update.openai_model

    # Validate OpenAI if selected
    if cfg.LLM_PROVIDER == "openai" and not cfg.OPENAI_API_KEY:
        raise HTTPException(
            status_code=400,
            detail="OpenAI was selected as provider but no API key was provided.",
        )

    settings_store.save_llm_settings(
        llm_provider=cfg.LLM_PROVIDER,
        ollama_base_url=cfg.OLLAMA_BASE_URL,
        ollama_model=cfg.OLLAMA_MODEL,
        openai_api_key=cfg.OPENAI_API_KEY,
        openai_model=cfg.OPENAI_MODEL,
    )

    # Reset embedding cache when provider changes
    from backend.rag.vectorstore import reset_vectorstore
    reset_vectorstore()
    clear_llm_cache()

    return SettingsResponse(
        llm_provider=cfg.LLM_PROVIDER,
        ollama_model=cfg.OLLAMA_MODEL,
        ollama_base_url=cfg.OLLAMA_BASE_URL,
        openai_model=cfg.OPENAI_MODEL,
        openai_configured=bool(cfg.OPENAI_API_KEY),
    )
