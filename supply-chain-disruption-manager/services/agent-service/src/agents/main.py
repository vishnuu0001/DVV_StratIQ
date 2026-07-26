# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: FastAPI application entry point for the Agent Service.
# Date: 2025-10-24
# ---------------------------------------------------------------------------
"""FastAPI application entry point for the Agent Service."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as aioredis
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents.config import get_settings
from agents.store.database import init_db, close_db
from agents.bus.consumer import StreamConsumer
from agents.routers import agents, health, disruption, incident
from agents.routers.incident import sse_broadcaster

log = structlog.get_logger(__name__)

_consumer_task: asyncio.Task | None = None
_redis_client: aioredis.Redis | None = None


# Function: _configure_logging
def _configure_logging() -> None:
    import logging
    settings = get_settings()
    processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    if settings.log_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Function: lifespan
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global _consumer_task, _redis_client

    _configure_logging()
    settings = get_settings()

    log.info("agent_service_starting", environment=settings.environment)

    # Init DB
    await init_db()

    # Init Redis
    # socket_timeout must exceed BLOCK_MS (5 s) so the XREADGROUP blocking call
    # returns normally instead of racing against the socket read timeout.
    # socket_connect_timeout is kept short for fast failure on startup.
    _redis_client = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        protocol=2,
        socket_timeout=10.0,
        socket_connect_timeout=5.0,
    )
    app.state.redis = _redis_client

    # Attach redis to sse_broadcaster
    sse_broadcaster.redis = _redis_client

    # Start stream consumer in background
    consumer = StreamConsumer(redis_client=_redis_client)
    _consumer_task = asyncio.create_task(consumer.run(), name="stream-consumer")
    log.info("stream_consumer_started")

    yield

    # Shutdown
    log.info("agent_service_stopping")
    if _consumer_task and not _consumer_task.done():
        _consumer_task.cancel()
        try:
            await _consumer_task
        except asyncio.CancelledError:
            pass

    if _redis_client:
        await _redis_client.aclose()

    await close_db()
    log.info("agent_service_stopped")


# Function: create_app
def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Agent Service",
        description="Agentic orchestration layer for Supply Chain Disruption Management",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url=None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(agents.router)
    app.include_router(disruption.router)
    app.include_router(incident.router)

    return app


app = create_app()
