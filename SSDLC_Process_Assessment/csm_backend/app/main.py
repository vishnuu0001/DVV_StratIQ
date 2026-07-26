# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — csm_backend/app (main.py)
# Date: 2025-11-14
# ---------------------------------------------------------------------------
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import CORS_ORIGINS, API_PREFIX, MODULE_NAME, APP_PORT
from app.api.routes_upload import router as upload_router
from app.api.routes_workbook import router as workbook_router
from app.api.routes_dashboard import router as dashboard_router
from app.api.routes_scenarios import router as scenarios_router
from app.api.routes_calculations import router as calculations_router

app = FastAPI(
    title="Consolidation Savings Model API",
    description="Parse and analyse a Consolidation Savings Model workbook, exposing all calculations as REST APIs.",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers under /api prefix
app.include_router(upload_router,       prefix=API_PREFIX)
app.include_router(workbook_router,     prefix=API_PREFIX)
app.include_router(dashboard_router,    prefix=API_PREFIX)
app.include_router(scenarios_router,    prefix=API_PREFIX)
app.include_router(calculations_router, prefix=API_PREFIX)


# Function: health_check
@app.get(f"{API_PREFIX}/csm/health")
def health_check() -> dict:
    return {"status": "ok", "module": MODULE_NAME, "port": APP_PORT}


# Static file serving for SPA frontend (optional)
_frontend_dist = Path(__file__).parent.parent.parent / "csm_frontend" / "dist"
if _frontend_dist.exists():
    _assets_path = _frontend_dist / "assets"
    if _assets_path.exists():
        app.mount("/assets", StaticFiles(directory=str(_assets_path)), name="assets")

    # Function: spa_fallback
    @app.exception_handler(404)
    async def spa_fallback(request: Request, exc: Exception) -> FileResponse:
        index_html = _frontend_dist / "index.html"
        if index_html.exists() and not request.url.path.startswith(API_PREFIX):
            return FileResponse(str(index_html))
        return JSONResponse(status_code=404, content={"detail": "Not found"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=APP_PORT,
        reload=True,
        log_level="info",
    )
