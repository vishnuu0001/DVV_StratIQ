# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/traceforge (main.py)
# Date: 2026-03-04
# ---------------------------------------------------------------------------
from __future__ import annotations

import asyncio
import json

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from traceforge.auth import (
    TRACEFORGE_APP, allow_local_auth_bypass, auth_required,
    decode_access_token, extract_bearer_token, is_local_origin,
)
from traceforge.config import CORS_ORIGINS, OLLAMA_EMBED_MODEL, OLLAMA_MODEL
from traceforge.routers import (
    artifacts, audit, coverage, gates, projects, requirements,
    runs, scripts, sources, testcases, workspace,
)

app = FastAPI(title="TraceForge API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Function: enforce_auth
@app.middleware("http")
async def enforce_auth(request: Request, call_next):
    path = request.url.path
    public_paths = {"/api/v1/health", "/docs", "/openapi.json", "/redoc"}
    if (
        request.method == "OPTIONS"
        or not auth_required()
        or path in public_paths
        or path.startswith("/api/v1/health")
    ):
        return await call_next(request)

    if allow_local_auth_bypass() and is_local_origin(request):
        request.state.auth = {"uid": 0, "username": "local-admin", "role": "admin", "apps": [TRACEFORGE_APP]}
        return await call_next(request)

    token = extract_bearer_token(request.headers.get("Authorization", ""))
    if not token:
        return JSONResponse(status_code=401, content={"error": "Authentication required"})
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        return JSONResponse(status_code=401, content={"error": str(exc)})

    if payload.get("role") != "admin" and TRACEFORGE_APP not in (payload.get("apps") or []):
        return JSONResponse(status_code=403, content={"error": "Access denied for TraceForge"})

    request.state.auth = payload
    return await call_next(request)


# Function: health
@app.get("/api/v1/health")
async def health():
    return {
        "status": "ok", "service": "traceforge-api",
        "llm_model": OLLAMA_MODEL, "embedding_model": OLLAMA_EMBED_MODEL,
    }


# Function: sse_test
@app.get("/api/v1/health/sse-test")
async def sse_test():
    """Phase 0 acceptance probe (spec §10): proves SSE streams live through IIS
    instead of being buffered and released as one burst at the end."""
    # Function: event_stream
    async def event_stream():
        for i in range(10):
            yield f"data: {json.dumps({'tick': i})}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


app.include_router(projects.router)
app.include_router(sources.router)
app.include_router(runs.router)
app.include_router(gates.router)
app.include_router(requirements.router)
app.include_router(testcases.router)
app.include_router(scripts.router)
app.include_router(artifacts.router)
app.include_router(coverage.router)
app.include_router(audit.router)
app.include_router(workspace.router)
