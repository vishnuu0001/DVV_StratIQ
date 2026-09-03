# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: FastAPI application entry point.
# Date: 2025-09-25
# ---------------------------------------------------------------------------
"""
FastAPI application entry point.
Run with: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8086
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class SPAStaticFiles(StaticFiles):
    """Serve a React SPA: return index.html for any unknown path."""

    # Function: get_response
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404:
                return await super().get_response("index.html", scope)
            raise

import backend.config as cfg
from backend.api.agent import router as agent_router
from backend.api.admin import router as admin_router
from backend.api.auth import router as auth_router
from backend.api.chat_history import router as chat_history_router
from backend.api.dashboard import router as dashboard_router
from backend.api.datasources import router as datasources_router
from backend.api.feedback import router as feedback_router
from backend.api.incident_workbench import router as incident_workbench_router
from backend.api.knowledgegraph import router as kg_router
from backend.api.search import router as search_router
from backend.api.servicenow import router as sn_router
from backend.api.settings import router as settings_router
from backend.api.ticket_analysis import router as ticket_analysis_router
from backend.api.ticket_intelligence import router as ticket_intelligence_router
from backend.api.virtual_agent import router as virtual_agent_router
from backend.api.knowledge_mgmt import router as knowledge_mgmt_router
from backend.api.predictive import router as predictive_router
from backend.api.automation_engine import router as automation_router
from backend.api.rca import router as rca_router
from backend.api.sentiment import router as sentiment_router
from backend.api.cmdb import router as cmdb_router
from backend.api.reports import router as reports_router
from backend.api.compliance import router as compliance_router
from backend.api.tickets import router as tickets_router
from backend.api.event_correlation import router as event_correlation_router
from backend.api.nlp import router as nlp_router
from backend.api.recommendation import router as recommendation_router
from backend.api.mlops import router as mlops_router
from backend.api.governance import router as governance_router
from backend.api.itsm_ops import router as itsm_ops_router
from backend.api.omnichannel import router as omnichannel_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)
READ_ONLY_USERNAMES = {"vishnuu", "prasanna", "siva"}


# ── /api/novastra-itsm/ → /api/ rewrite ──────────────────────────────────
# Production builds use VITE_NOVASTRA_ITSM_API_URL=/api/novastra-itsm (base: '/novastra-itsm/').
# This middleware transparently maps every /api/novastra-itsm/... request to
# the canonical /api/... route so no duplicate registrations are needed.
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as _Req

class _NovastraItsmPrefixMiddleware(BaseHTTPMiddleware):
    # Function: dispatch
    async def dispatch(self, request: _Req, call_next):
        if request.scope["path"].startswith("/api/novastra-itsm/"):
            request.scope["path"] = request.scope["path"].replace("/api/novastra-itsm/", "/api/", 1)
            request.scope["raw_path"] = request.scope["path"].encode()
        return await call_next(request)


# Function: lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure data directory exists
    Path(cfg.DATA_DIR).mkdir(parents=True, exist_ok=True)
    from backend.services.chat_history_store import ensure_schema as ensure_chat_schema
    from backend.services.sync_status_store import ensure_schema as ensure_sync_status_schema
    from backend.api.auth import _ensure_schema as ensure_auth_schema
    from backend.services import settings_store
    ensure_auth_schema()
    ensure_chat_schema()
    ensure_sync_status_schema()

    # Hydrate LLM settings from the database (encrypted at rest) so a restart
    # picks up the last value saved via the Settings UI, not stale .env values.
    try:
        persisted = settings_store.get_llm_settings()
        cfg.LLM_PROVIDER = persisted["llm_provider"] or cfg.LLM_PROVIDER
        cfg.OLLAMA_BASE_URL = persisted["ollama_base_url"] or cfg.OLLAMA_BASE_URL
        cfg.OLLAMA_MODEL = persisted["ollama_model"] or cfg.OLLAMA_MODEL
        if persisted["openai_api_key"]:
            cfg.OPENAI_API_KEY = persisted["openai_api_key"]
        cfg.OPENAI_MODEL = persisted["openai_model"] or cfg.OPENAI_MODEL
    except Exception as exc:
        logger.warning("Failed to load persisted LLM settings, using .env defaults: %s", exc)

    logger.info("Novastra-ITSM Support Agent starting — LLM provider: %s", cfg.LLM_PROVIDER)

    # Pre-warm vectorstore and LLM so the first user query has no cold-start delay
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    # Function: _warmup
    def _warmup():
        try:
            from backend.rag.vectorstore import get_collection_stats
            stats = get_collection_stats()
            logger.info("Vectorstore pre-warmed — %d chunks in collection.", stats.get("total_chunks", 0))
        except Exception as exc:
            logger.warning("Vectorstore pre-warm failed: %s", exc)
        try:
            from backend.llm.router import get_llm, get_ollama_runtime_status
            get_llm(cfg.LLM_PROVIDER)
            logger.info("LLM pre-warmed — provider: %s", cfg.LLM_PROVIDER)
            if cfg.LLM_PROVIDER == "ollama":
                runtime = get_ollama_runtime_status()
                logger.info(
                    "Ollama runtime: reachable=%s model_loaded=%s gpu_active=%s active_model=%s",
                    runtime.get("reachable"),
                    runtime.get("model_loaded"),
                    runtime.get("gpu_active"),
                    runtime.get("active_model"),
                )
        except Exception as exc:
            if cfg.LLM_PROVIDER == "ollama" and cfg.OLLAMA_REQUIRE_GPU:
                logger.error(
                    "LLM pre-warm failed with OLLAMA_REQUIRE_GPU=true; refusing startup: %s",
                    exc,
                )
                raise
            logger.warning("LLM pre-warm failed (non-fatal): %s", exc)

    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, _warmup)

    from backend.services.email_intake import run_email_poll_loop
    email_poll_task = asyncio.create_task(run_email_poll_loop())

    yield

    email_poll_task.cancel()
    try:
        await email_poll_task
    except asyncio.CancelledError:
        pass
    logger.info("Novastra-ITSM Support Agent shutting down.")


app = FastAPI(
    title="Novastra-ITSM – AI Support Agent",
    description=(
        "RAG-powered support agent backed by a knowledge repository. "
        "Supports Ollama (open-source) and OpenAI LLMs. "
        "Includes ServiceNow integration, admin knowledge management, and feedback collection."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── Auth ──────────────────────────────────────────────────────
# Route-level auth (Depends(get_current_user)) is opt-in per file, and an
# audit found 6 of the module's 31 route files never opt in at all
# (dashboard.py, agent.py, feedback.py, search.py, servicenow.py,
# settings.py) — meaning real ITSM ticket data, the RAG query engine, and
# ServiceNow sync controls were reachable with no token. This middleware
# closes that at the perimeter instead of touching every route file,
# reusing the exact same get_current_user() verification (including its
# bypass logic) that already-protected routes call directly — so behavior
# for those routes doesn't change, it's just now also enforced for the
# ones that were missing it.
from fastapi.security import HTTPAuthorizationCredentials
from starlette.responses import JSONResponse
from backend.api.auth import get_current_user

_PUBLIC_API_PATHS = {
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/portal-sso",
    "/api/auth/logout",
    "/api/auth/oauth/providers",
    "/api/auth/github",
    "/api/auth/github/callback",
    "/api/auth/google",
    "/api/auth/google/callback",
    "/docs",
    "/openapi.json",
    "/redoc",
}


# Function: _normalized_api_path
def _normalized_api_path(request: Request) -> str:
    # Mirrors _NovastraItsmPrefixMiddleware's rewrite so path checks below
    # are correct regardless of ASGI middleware registration order.
    path = request.url.path
    if path.startswith("/api/novastra-itsm/"):
        path = path.replace("/api/novastra-itsm/", "/api/", 1)
    return path


# Function: enforce_auth
@app.middleware("http")
async def enforce_auth(request: Request, call_next):
    path = _normalized_api_path(request)
    if request.method == "OPTIONS" or not path.startswith("/api") or path in _PUBLIC_API_PATHS:
        return await call_next(request)
    auth_header = request.headers.get("Authorization", "")
    credentials = None
    if auth_header.lower().startswith("bearer "):
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=auth_header[7:].strip())
    try:
        current_user = get_current_user(request, credentials)
    except HTTPException as exc:
        return JSONResponse({"error": exc.detail}, status_code=exc.status_code)
    if (
        (current_user.get("username") or "").strip().lower() in READ_ONLY_USERNAMES
        and request.method not in {"GET", "HEAD", "OPTIONS"}
    ):
        return JSONResponse(
            {
                "error": "Read-only access: operations are disabled for this account",
                "code": "READ_ONLY_ACCOUNT",
            },
            status_code=403,
        )
    return await call_next(request)


# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(_NovastraItsmPrefixMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(chat_history_router)
app.include_router(agent_router)
app.include_router(admin_router)
app.include_router(sn_router)
app.include_router(dashboard_router)
app.include_router(feedback_router)
app.include_router(settings_router)
app.include_router(datasources_router)
app.include_router(kg_router)
app.include_router(search_router)
app.include_router(ticket_analysis_router)
app.include_router(incident_workbench_router)
app.include_router(ticket_intelligence_router)
app.include_router(virtual_agent_router)
app.include_router(knowledge_mgmt_router)
app.include_router(predictive_router)
app.include_router(automation_router)
app.include_router(rca_router)
app.include_router(sentiment_router)
app.include_router(cmdb_router)
app.include_router(reports_router)
app.include_router(compliance_router)
app.include_router(tickets_router)
app.include_router(event_correlation_router)
app.include_router(nlp_router)
app.include_router(recommendation_router)
app.include_router(mlops_router)
app.include_router(governance_router)
app.include_router(itsm_ops_router)
app.include_router(omnichannel_router)


# ── Health check ──────────────────────────────────────────────
# Function: health
@app.get("/health", tags=["System"])
async def health():
    ollama_runtime = None
    if cfg.LLM_PROVIDER == "ollama":
        try:
            from backend.llm.router import get_ollama_runtime_status
            ollama_runtime = get_ollama_runtime_status()
        except Exception:
            ollama_runtime = {"reachable": False, "model_loaded": False, "gpu_active": None}
    return {
        "status": "ok",
        "llm_provider": cfg.LLM_PROVIDER,
        "ollama_model": cfg.OLLAMA_MODEL,
        "embed_model": cfg.OLLAMA_EMBED_MODEL,
        "vector_backend": cfg.VECTOR_BACKEND,
        "modern_pipeline_enabled": cfg.MODERN_PIPELINE_ENABLED,
        "sync_require_dual_write": cfg.SYNC_REQUIRE_DUAL_WRITE,
        "qdrant_collection": cfg.QDRANT_COLLECTION,
        "openai_configured": bool(cfg.OPENAI_API_KEY),
        "ollama_runtime": ollama_runtime,
    }


# ── Serve React frontend (after `npm run build`) ───────────────
_frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount("/", SPAStaticFiles(directory=str(_frontend_dist), html=True), name="frontend")
