# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: FastAPI application entry point for the KG service.
# Date: 2025-10-26
# ---------------------------------------------------------------------------
"""FastAPI application entry point for the KG service."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from kg.config import get_settings
from kg.db import close_driver, init_driver
from kg.routers import (
    compat_router,
    edge_router,
    entity_router,
    health_router,
    owners_router,
    search_router,
    seed_router,
    traverse_router,
)


# Function: _configure_logging
def _configure_logging(level: str) -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if level == "DEBUG" else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(level)),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )


# Function: lifespan
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    _configure_logging(settings.log_level)
    log = structlog.get_logger(__name__)
    log.info("kg_service_starting", environment=settings.environment)
    await init_driver()
    yield
    await close_driver()
    log.info("kg_service_stopped")


app = FastAPI(
    title="KG Service",
    description="Supply Chain Knowledge Graph — FastAPI + Neo4j",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Exception handlers — RFC 7807 problem+json
# ---------------------------------------------------------------------------

# Function: not_found_handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "type": "urn:kg:error:not-found",
            "title": "Not Found",
            "status": 404,
            "detail": str(exc),
        },
        media_type="application/problem+json",
    )


# Function: server_error_handler
@app.exception_handler(500)
async def server_error_handler(request: Request, exc: Exception) -> JSONResponse:
    log = structlog.get_logger(__name__)
    log.exception("unhandled_error", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "type": "urn:kg:error:internal-server-error",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred",
        },
        media_type="application/problem+json",
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(health_router)
app.include_router(compat_router)
app.include_router(entity_router)
app.include_router(edge_router)
app.include_router(traverse_router)
app.include_router(owners_router)
app.include_router(search_router)
app.include_router(seed_router)


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "kg.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
    )
