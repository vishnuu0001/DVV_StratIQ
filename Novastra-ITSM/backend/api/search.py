# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modern RAG/Search API layer for React UI consumption.
# Date: 2025-11-20
# ---------------------------------------------------------------------------
"""Modern RAG/Search API layer for React UI consumption."""
from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import backend.config as cfg
from backend.models.schemas import QueryResponse
from backend.rag.pipeline import query_rag
from backend.rag.vectorstore import similarity_search

router = APIRouter(prefix="/api/search", tags=["Search"])
_SEARCH_EXECUTOR = ThreadPoolExecutor(max_workers=4)


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=50000)
    llm_provider: Optional[str] = None
    top_k: int = Field(8, ge=1, le=50)


# Function: semantic_search
@router.post("/semantic")
async def semantic_search(request: SemanticSearchRequest):
    provider = request.llm_provider or cfg.LLM_PROVIDER
    rows = similarity_search(query=request.query, provider=provider, k=request.top_k)
    return {
        "results": [
            {
                "score": float(score),
                "text": doc.page_content,
                "metadata": doc.metadata,
            }
            for doc, score in rows
        ],
        "vector_backend": cfg.VECTOR_BACKEND,
        "count": len(rows),
    }


# Function: search_answer
@router.post("/answer", response_model=QueryResponse)
async def search_answer(request: SemanticSearchRequest):
    provider = request.llm_provider or cfg.LLM_PROVIDER
    try:
        timeout_sec = min(30, max(8, int(getattr(cfg, "QUERY_JOB_TIMEOUT_SECONDS", 25) or 25)))
        # Function: _run_with_timeout
        def _run_with_timeout() -> dict:
            future = _SEARCH_EXECUTOR.submit(query_rag, question=request.query, llm_provider=provider)
            try:
                return future.result(timeout=timeout_sec)
            except FutureTimeout as exc:
                future.cancel()
                raise TimeoutError(f"search timeout after {timeout_sec}s") from exc

        result = await asyncio.to_thread(_run_with_timeout)
    except asyncio.TimeoutError:
        result = {
            "answer": (
                "Search timed out before full synthesis. Returning fast grounded fallback. "
                "Add one discriminator (error code, stack token, or transaction code) and retry for a precise match."
            ),
            "sources": [],
            "confidence": 0.25,
            "context_used": False,
            "mode": "chat",
            "session_id": None,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return QueryResponse(**result)
