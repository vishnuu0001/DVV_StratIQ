# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Signal Inspector FastAPI application entry point.
# Date: 2026-07-02
# ---------------------------------------------------------------------------
"""Signal Inspector FastAPI application entry point."""

from __future__ import annotations

import os
import re
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import httpx
import structlog
import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis, from_url

from inspector.adapters.base import BaseAdapter, AdapterHealth
from inspector.adapters.erp_webhook import ErpWebhookAdapter
from inspector.adapters.manual import ManualAdapter
from inspector.adapters.mes_mqtt import MesMqttAdapter
from inspector.adapters.supplier_portal_csv import SupplierPortalCsvAdapter
from inspector.adapters.tms_webhook import TmsWebhookAdapter
from inspector.adapters.wms_poll import WmsPollAdapter
from inspector.bus.redis_streams import RedisStreamsPublisher
from inspector.config import get_settings
from inspector.normalizer import pipeline
from inspector.routers import adapters, events, health, incidents, ingest, schemas
from inspector.store.database import close_engine, ensure_schema, get_engine

logger = structlog.get_logger(__name__)


# Function: _resolve_env_vars
def _resolve_env_vars(value: Any) -> Any:
    """Expand ${ENV_VAR} references in config values."""
    if isinstance(value, str):
        return re.sub(r"\$\{([^}]+)\}", lambda m: os.environ.get(m.group(1), ""), value)
    if isinstance(value, dict):
        return {k: _resolve_env_vars(v) for k, v in value.items()}
    return value


class AdapterManager:
    """Reads adapters.yaml, instantiates enabled adapters, manages lifecycle."""

    # Function: __init__
    def __init__(self) -> None:
        self._adapters: dict[str, BaseAdapter] = {}
        self._config: dict[str, Any] = {}

    # Function: load_config
    def load_config(self) -> None:
        settings = get_settings()
        config_path: Path = settings.config_dir / "adapters.yaml"
        with config_path.open("r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
        self._config = _resolve_env_vars(raw.get("adapters", {}))

    # Function: build_adapters
    def build_adapters(
        self,
        on_poll_event: Any = None,
    ) -> None:
        """Instantiate adapter objects based on config."""
        cfg = self._config

        # Manual (always available)
        manual_cfg = cfg.get("manual", {"enabled": True})
        self._adapters["manual"] = ManualAdapter(manual_cfg)

        # ERP webhook
        erp_cfg = cfg.get("erp_webhook", {})
        if erp_cfg.get("enabled", False):
            self._adapters["erp_webhook"] = ErpWebhookAdapter(erp_cfg)

        # TMS webhook
        tms_cfg = cfg.get("tms_webhook", {})
        if tms_cfg.get("enabled", False):
            self._adapters["tms_webhook"] = TmsWebhookAdapter(tms_cfg)

        # WMS poll
        wms_cfg = cfg.get("wms_poll", {})
        if wms_cfg.get("enabled", False) and on_poll_event:
            self._adapters["wms_poll"] = WmsPollAdapter(wms_cfg, on_poll_event)

        # Supplier portal CSV
        csv_cfg = cfg.get("supplier_portal_csv", {})
        if csv_cfg.get("enabled", False) and on_poll_event:
            self._adapters["supplier_portal_csv"] = SupplierPortalCsvAdapter(
                csv_cfg, on_poll_event
            )

        # MES MQTT
        mqtt_cfg = cfg.get("mes_mqtt", {})
        if mqtt_cfg.get("enabled", False) and on_poll_event:
            self._adapters["mes_mqtt"] = MesMqttAdapter(mqtt_cfg, on_poll_event)

        logger.info("adapters.loaded", names=list(self._adapters.keys()))

    # Function: start_all
    async def start_all(self) -> None:
        for name, adapter in self._adapters.items():
            if adapter.enabled:
                await adapter.start()
                logger.info("adapter.started", name=name)

    # Function: stop_all
    async def stop_all(self) -> None:
        for name, adapter in self._adapters.items():
            await adapter.stop()
            logger.info("adapter.stopped", name=name)

    # Function: get
    def get(self, name: str) -> BaseAdapter | None:
        return self._adapters.get(name)

    # Function: get_all_health
    def get_all_health(self) -> list[AdapterHealth]:
        return [a.get_health() for a in self._adapters.values()]


# Function: _configure_logging
def _configure_logging(settings: Any) -> None:
    import logging
    import structlog

    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(level=log_level)

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.log_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Function: lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    settings = get_settings()
    _configure_logging(settings)

    logger.info("signal_inspector.starting", env=settings.environment)

    # ── Redis ───────────────────────────────────────────────────────────────
    redis: Redis = from_url(settings.redis_url, decode_responses=True, protocol=2)
    app.state.redis = redis

    publisher = RedisStreamsPublisher(redis)
    app.state.publisher = publisher

    # ── HTTP client ─────────────────────────────────────────────────────────
    http_client = httpx.AsyncClient()
    app.state.http_client = http_client

    # ── Database engine ─────────────────────────────────────────────────────
    get_engine()  # initialise pool
    await ensure_schema()

    # ── Adapters ─────────────────────────────────────────────────────────────
    adapter_manager = AdapterManager()
    adapter_manager.load_config()
    app.state.adapter_manager = adapter_manager

    # Callback for background adapters (wms_poll, csv, mqtt)
    # Function: on_poll_event
    async def on_poll_event(adapter_event: Any) -> None:
        from inspector.store.database import get_session_factory
        from inspector.store.event_repo import EventRepo
        from inspector.normalizer import pipeline as pl

        factory = get_session_factory()
        async with factory() as session:
            repo = EventRepo(session)
            await pl.run_pipeline(
                adapter_event=adapter_event,
                redis=redis,
                publisher=publisher,
                http_client=http_client,
                event_repo=repo,
            )
            await session.commit()

    adapter_manager.build_adapters(on_poll_event=on_poll_event)
    await adapter_manager.start_all()

    logger.info("signal_inspector.ready", port=8003)

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────────
    logger.info("signal_inspector.stopping")
    await adapter_manager.stop_all()
    await http_client.aclose()
    await redis.aclose()
    await close_engine()
    logger.info("signal_inspector.stopped")


# Function: create_app
def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Signal Inspector",
        description="Supply chain event ingestion, normalisation, and routing service.",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()
        ],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(ingest.router)
    app.include_router(events.router)
    app.include_router(adapters.router)
    app.include_router(schemas.router)
    app.include_router(incidents.router)

    return app


app = create_app()
