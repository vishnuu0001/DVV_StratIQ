# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: FastAPI server that exposes the CodeAnalysis engine as a REST API
# Date: 2025-09-24
# ---------------------------------------------------------------------------
"""
api/server.py
-------------
FastAPI server that exposes the CodeAnalysis engine as a REST API
consumed by the React UI.

Endpoints
~~~~~~~~~
POST /api/analyse          â€“ analyse a single repo or local path
POST /api/portfolio        â€“ analyse all repos in a GitHub org
GET  /api/reports          â€“ list existing report files
GET  /api/reports/{name}   â€“ download a specific JSON report
GET  /api/health           â€“ liveness check
"""
from __future__ import annotations

import dataclasses
import base64
import hashlib
import hmac
import json
import logging
import os
import shutil
import threading
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, List, Optional

import asyncio

import uvicorn
from fastapi import FastAPI, BackgroundTasks, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel

# Add project root to sys.path so relative imports work when launched from api/
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import (
    MAX_UPLOAD_EXTRACTED_BYTES,
    MAX_UPLOAD_FILE_COUNT,
    MAX_UPLOAD_ZIP_BYTES,
    REPORT_DIR,
    UPLOAD_DIR,
)
from core.analyzer import CodeAnalyzer
from core.github_fetcher import GitHubFetcher
from reports.json_reporter import write_json
from reports.html_reporter import write_html
from services.ollama_client import OllamaClient, RECOMMENDED_MODELS
from services.call_graph       import build_call_graph
from services.knowledge_graph  import build_knowledge_graph
from services.ai_analysis      import run_ai_analysis

try:
    from dotenv import load_dotenv
    # Load .env from the project root (parent of api/)
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# â”€â”€ Database layer â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
import json as _json_mod
from datetime import datetime as _dt, timezone as _timezone


ANALYSIS_COMPLETE_MESSAGE = "Analysis complete"
DATABASE_NOT_AVAILABLE_MESSAGE = "Database not available"
ANALYSIS_NOT_FOUND_MESSAGE = "Analysis not found in DB"

# Function: _dt_now
def _dt_now():
    return _dt.now(_timezone.utc)

try:
    from db import (
        init_db, SessionLocal,
        CAJob, CAAppProfile, CAHealth, CADebt, CACloud,
        CAOss, CAOssDep, CAImpact, CACo2, CAGreen, CAGreenDeficiency,
        CAArchitecture, CAArchLayer, CAArchNode, CACloudRecs,
        CALangReport, CALangFile, CAHealthPerLang,
        CAAiAnalysis, CAAiDebtHotspot, CAAiCloudBlocker,
        CAAiMicroservice, CAAiBusinessRule, CAAiTransformPath,
    )
    _DB_ENABLED = True
    init_db()
    logger.info("CodeAnalysis DB initialised")
except Exception as _db_init_err:
    logger.warning("DB layer unavailable: %s", _db_init_err)
    _DB_ENABLED = False

app = FastAPI(
    title="CodeAnalysis API",
    description="Deep source-code analysis for Java, .NET, Python, and Mainframe",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the React frontend (frontend/dist) from the same origin.
# Static assets are mounted at /assets. All unmatched non-/api paths fall
# through to index.html via the 404 exception handler below (SPA routing).
_DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if _DIST_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(_DIST_DIR / "assets")), name="assets")

    # Function: _favicon
    @app.get("/favicon.ico", include_in_schema=False)
    async def _favicon():
        ico = _DIST_DIR / "favicon.ico"
        return FileResponse(str(ico)) if ico.exists() else HTMLResponse("", status_code=204)

    # Function: _spa_or_error
    @app.exception_handler(StarletteHTTPException)
    async def _spa_or_error(request: Request, exc: StarletteHTTPException):
        """Serve index.html for 404s on non-API paths (SPA client-side routing)."""
        if exc.status_code == 404 and not request.url.path.startswith("/api"):
            return FileResponse(str(_DIST_DIR / "index.html"))
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

    # Function: _index
    @app.get("/", include_in_schema=False)
    async def _index():
        return FileResponse(str(_DIST_DIR / "index.html"))

CODE_ANALYSIS_APP = "CODE_ANALYSIS"


# Function: _auth_required
def _auth_required() -> bool:
    return os.getenv("AUTH_REQUIRED", "true").lower() in {"1", "true", "yes"}


# Function: _token_secret
def _token_secret() -> str:
    return (
        os.getenv("AUTH_TOKEN_SECRET")
        or os.getenv("JWT_SECRET")
        or os.getenv("SECRET_KEY")
        or "change_me_jwt_secret_in_production"
    )


# Function: _b64url_decode
def _b64url_decode(text: str) -> bytes:
    padding = "=" * ((4 - len(text) % 4) % 4)
    return base64.urlsafe_b64decode((text + padding).encode("ascii"))


# Function: _b64url_encode
def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


# Function: _extract_bearer_token
def _extract_bearer_token(authorization_header: str) -> str | None:
    if not authorization_header:
        return None
    parts = authorization_header.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1].strip()


# Function: _decode_access_token
def _decode_access_token(token: str) -> dict:
    if not token:
        raise ValueError("Missing token")

    parts = token.split(".")
    if len(parts) != 3 or parts[0] != "v1":
        raise ValueError("Malformed token")

    payload_encoded = parts[1]
    expected_signature = _b64url_encode(
        hmac.new(
            _token_secret().encode("utf-8"),
            payload_encoded.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    )
    if not hmac.compare_digest(expected_signature, parts[2]):
        raise ValueError("Invalid token signature")

    payload = json.loads(_b64url_decode(payload_encoded).decode("utf-8"))
    if payload.get("typ") != "access":
        raise ValueError("Invalid token type")

    exp = int(payload.get("exp", 0))
    if exp <= int(time.time()):
        raise ValueError("Token expired")

    return payload


# Function: enforce_auth
@app.middleware("http")
async def enforce_auth(request: Request, call_next):
    # Rewrite /api/codeanalysis/* â†’ /api/* so requests that arrive via an
    # IIS/nginx prefix-route work identically to direct /api/* requests.
    _scope_path = request.scope.get("path", "")
    if _scope_path.startswith("/api/codeanalysis"):
        _new_path = "/api" + _scope_path[len("/api/codeanalysis"):]
        request.scope["path"] = _new_path
        request.scope["raw_path"] = _new_path.encode("latin-1")
        request.__dict__.pop("_url", None)

    try:
        path = request.url.path
        public_paths = {"/api/health", "/api/modules", "/docs", "/openapi.json", "/redoc"}

        if not _auth_required() or not path.startswith("/api") or path in public_paths:
            return await call_next(request)

        token = _extract_bearer_token(request.headers.get("Authorization", ""))
        if not token:
            if path == "/api/auth/session":
                request.state.auth = None
                return await call_next(request)
            return JSONResponse(status_code=401, content={"error": "Authentication required"})

        try:
            payload = _decode_access_token(token)
        except ValueError as exc:
            if path == "/api/auth/session":
                request.state.auth = None
                return await call_next(request)
            return JSONResponse(status_code=401, content={"error": str(exc)})

        role = payload.get("role")
        apps = payload.get("apps") or []
        if role != "admin" and CODE_ANALYSIS_APP not in apps:
            return JSONResponse(
                status_code=403,
                content={"error": "Access denied for Code Analysis"},
            )

        request.state.auth = payload
        return await call_next(request)
    except Exception as exc:
        logger.exception("Auth middleware error: %s", exc)
        return JSONResponse(status_code=500, content={"error": "Internal server error in auth middleware"})

# â”€â”€â”€ Job store: in-memory cache + throttled disk flush â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# All reads/writes go through memory first (O(1)), so SSE streaming can poll
# at 5 Hz without any disk I/O. Disk is written at most every 2 s, or
# immediately on terminal status (done / error), for crash-safety.
_JOBS_DIR = Path(__file__).resolve().parent.parent / ".jobs"
_JOBS_DIR.mkdir(exist_ok=True)

_JOB_CACHE: dict = {}
_JOB_CACHE_LOCK = threading.Lock()
_JOB_FLUSH_TS: dict = {}        # job_id â†’ last flush monotonic time
_FLUSH_INTERVAL = 2.0           # seconds between non-terminal disk flushes


# Function: _job_path
def _job_path(job_id: str) -> Path:
    return _JOBS_DIR / f"{job_id}.json"


# Function: _job_read
def _job_read(job_id: str) -> dict | None:
    with _JOB_CACHE_LOCK:
        if job_id in _JOB_CACHE:
            return dict(_JOB_CACHE[job_id])
    # Cache miss (e.g. after a server restart) â€” load from disk once.
    p = _job_path(job_id)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text())
        with _JOB_CACHE_LOCK:
            _JOB_CACHE[job_id] = data
        return dict(data)
    except Exception:
        return None


# Function: _job_write
def _job_write(job_id: str, data: dict) -> None:
    with _JOB_CACHE_LOCK:
        _JOB_CACHE[job_id] = dict(data)
    _flush_job(job_id, data, force=True)


# Function: _job_update
def _job_update(job_id: str, **kwargs) -> None:
    is_terminal = kwargs.get("status") in ("done", "error")
    with _JOB_CACHE_LOCK:
        existing = dict(_JOB_CACHE.get(job_id, {}))
        existing.update(kwargs)
        _JOB_CACHE[job_id] = existing
        snapshot = dict(existing)
    _flush_job(job_id, snapshot, force=is_terminal)


# Function: _flush_job
def _flush_job(job_id: str, data: dict, force: bool = False) -> None:
    """Write *data* to disk if throttle allows or *force* is True."""
    now = time.monotonic()
    should_flush = False
    with _JOB_CACHE_LOCK:
        last = _JOB_FLUSH_TS.get(job_id, 0.0)
        if force or now - last >= _FLUSH_INTERVAL:
            _JOB_FLUSH_TS[job_id] = now
            should_flush = True
    if should_flush:
        try:
            _job_path(job_id).write_text(json.dumps(data))
        except Exception as exc:
            logger.warning("Job flush failed for %s: %s", job_id, exc)


# â”€â”€â”€ AI concurrency limiter â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Ollama processes one LLM call at a time. Running more than 1 concurrent
# module-level AI analysis causes severe Ollama queue contention (each module
# dispatches 5 parallel sub-analyses; 2 modules = 10 simultaneous LLM calls
# all serialised inside Ollama with heavy context-switch overhead).
# Process modules strictly one at a time â€” individual sub-analyses within
# each module still run in parallel for preprocessing overlap.
_AI_SEMAPHORE = threading.Semaphore(1)


# â”€â”€â”€ Pydantic models â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class AnalyseRequest(BaseModel):
    repo:    Optional[str] = None   # GitHub URL or owner/repo
    local:   Optional[str] = None   # Local path
    users:   int   = 100
    revenue: float = 0.0

class PortfolioRequest(BaseModel):
    org:   str
    limit: int = 20


# â”€â”€â”€ Serialisation helper â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# Function: _dc_to_dict
def _dc_to_dict(obj: Any) -> Any:
    """Recursively convert dataclasses / Path / set to JSON-safe types."""
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {k: _dc_to_dict(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, set):
        return sorted(obj)
    if isinstance(obj, list):
        return [_dc_to_dict(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _dc_to_dict(v) for k, v in obj.items()}
    return obj


# Function: _oss_detail_to_dict
def _oss_detail_to_dict(d) -> dict:
    return {
        "name":           d.name,
        "ecosystem":      d.ecosystem,
        "latest_version": d.latest_version,
        "license":        d.license,
        "license_risk":   d.license_risk,
        "vulnerable":     d.vulnerable,
        "vuln_count":     d.vuln_count,
        "cve_severity":   d.cve_severity,
        "cve_ids":        d.cve_ids,
        "age_years":      round(d.age_years, 1),
        "age_ok":         d.age_ok,
    }


# Function: _lang_file_to_dict
def _lang_file_to_dict(fm) -> dict:
    return {
        "name":          "/".join(str(fm.path).replace("\\", "/").split("/")[-4:]),
        "sloc":          fm.code_lines,
        "total_lines":   fm.total_lines,
        "comment_lines": fm.comment_lines,
        "blank_lines":   fm.blank_lines,
        "complexity":    fm.cyclomatic,
        "cognitive":     fm.cognitive,
        "functions":     fm.functions,
        "classes":       fm.classes,
        "long_methods":  fm.long_methods,
        "deep_nesting":  fm.deep_nesting,
        "magic_numbers": fm.magic_numbers,
        "todo_comments": fm.todo_comments,
        "commented_out_lines": fm.commented_out_lines,
        "comment_ratio": round(fm.comment_lines / fm.code_lines, 3) if fm.code_lines else 0,
        "error":         fm.error,
    }


# Function: _lang_report_to_dict
def _lang_report_to_dict(r) -> dict:
    return {
        "language":         r.language,
        "file_count":       r.file_count,
        "total_sloc":       r.total_sloc,
        "avg_complexity":   round(r.avg_complexity, 2),
        "max_complexity":   r.max_complexity,
        "total_functions":  r.total_functions,
        "total_classes":    r.total_classes,
        "long_methods_pct": round(r.long_methods_pct, 2),
        "deep_nesting_pct": round(r.deep_nesting_pct, 2),
        "comment_ratio":    round(r.comment_ratio, 3),
        "commented_out_lines": r.commented_out_lines,
        "commented_out_ratio": round(r.commented_out_ratio, 3),
        "bad_practices":    r.bad_practices,
        "dependencies":     sorted(r.dependencies),
        "files":            [_lang_file_to_dict(fm) for fm in r.files],
    }


# Function: _green_impact_to_dict
def _green_impact_to_dict(result) -> Any:
    if not result.green_impact:
        return None
    gi = result.green_impact
    return {
        "total_occurrences": gi.total_occurrences,
        "total_effort_days": gi.total_effort_days,
        "green_score":       gi.green_score,
        "risk_label":        gi.risk_label,
        "category_totals":   gi.category_totals,
        "deficiencies": [
            {
                "rule_key":       d.rule_key,
                "category":       d.category,
                "label":          d.label,
                "language":       d.language,
                "occurrences":    d.occurrences,
                "effort_days":    d.effort_days,
                "affected_files": d.affected_files,
            }
            for d in gi.deficiencies
        ],
    }


# Function: _architecture_to_dict
def _architecture_to_dict(result) -> Any:
    if not result.architecture:
        return None
    ar = result.architecture
    return {
        "total_files":  ar.total_files,
        "has_data":     ar.has_data,
        "layer_counts": ar.layer_counts,
        "layer_sloc":   ar.layer_sloc,
        "layers": [
            {"name": l.name, "file_count": l.file_count, "sloc": l.sloc,
             "pct": l.pct, "technologies": l.technologies}
            for l in ar.layers
        ],
        "nodes": [
            {"name": n.name, "layer": n.layer, "language": n.language, "sloc": n.sloc}
            for n in ar.nodes
        ],
    }


# Function: _cloud_recs_to_dict
def _cloud_recs_to_dict(result) -> Any:
    if not result.cloud_recommendations:
        return None
    cr = result.cloud_recommendations
    return {
        "total_services":    cr.total_services,
        "detected_triggers": cr.detected_triggers,
        "by_category": {
            cat: [
                {"service": e.service, "category": e.category, "reason": e.reason, "count": e.count}
                for e in entries
            ]
            for cat, entries in cr.by_category.items()
        },
    }


# Function: _result_to_dict
def _result_to_dict(result) -> dict:
    return {
        "repo_name":          result.repo_name,
        "repo_url":           result.repo_url,
        "total_sloc":         result.total_sloc,
        "total_files":        result.total_files,
        "languages_detected": result.languages_detected,
        "health":             _dc_to_dict(result.health),
        "debt":               _dc_to_dict(result.debt),
        "cloud":              {
            **_dc_to_dict(result.cloud),
            "boosters": result.cloud.boosters,
            "blockers": result.cloud.blockers,
        },
        "oss":                {
            **_dc_to_dict(result.oss),
            "details": [_oss_detail_to_dict(d) for d in result.oss.details],
        },
        "impact":             _dc_to_dict(result.impact),
        "co2":                _dc_to_dict(result.co2),
        "language_reports":   [
            _lang_report_to_dict(r)
            for r in sorted(result.language_reports, key=lambda r: r.total_sloc, reverse=True)
        ],
        "green_impact":           _green_impact_to_dict(result),
        "architecture":           _architecture_to_dict(result),
        "cloud_recommendations":  _cloud_recs_to_dict(result),
        "health_per_language": result.health_per_language or [],
        "quality_coverage": _dc_to_dict(result.quality_coverage) if getattr(result, "quality_coverage", None) else None,
        "ml_predictions":   getattr(result, "ml_predictions", None),
        "legacy_modernization": getattr(result, "legacy_modernization", None),
        # convenience flat fields for portfolio table
        "sloc":            result.total_sloc,
        "file_count":      result.total_files,
        "languages":       result.languages_detected,
        "health_score":    result.health.health,
        "debt_person_months": result.debt.debt_months,
        "cloud_score":     result.cloud.total,
        "oss_score":       result.oss.total,
        "impact_score":    result.impact.total,
        "rebuild_cost":    result.debt.debt_usd,
        "vulnerable_deps": result.oss.vulnerable_count,
        "risk_label":      result.health.risk_label,
        "rationalization_profile": _compute_rationalization_profile(result),
    }


# Function: _rp_server_name
def _rp_server_name(result) -> str:
    import socket as _socket
    try:
        if result.repo_url:
            from urllib.parse import urlparse as _up
            _h = _up(result.repo_url).hostname or ''
            return _h if _h else _socket.gethostname()
        return _socket.gethostname()
    except Exception:
        return 'localhost'


# Function: _rp_architecture
def _rp_architecture(result) -> str:
    if not result.architecture:
        return 'Monolithic'
    lc    = result.architecture.layer_counts
    total = sum(lc.values()) or 1
    svc   = lc.get('Services', 0)
    pres  = lc.get('Presentation', 0)
    pers  = lc.get('Persistence', 0)
    coord = lc.get('Coordination', 0)
    if svc / total > 0.50:
        return 'Service-Oriented (SOA)'
    if pres > 0 and pers > 0 and svc > 0:
        return 'Layered / N-Tier (MVC)'
    if pres > 0 and pers > 0:
        return 'Two-Tier / Client-Server'
    if svc > 0 or coord > 0:
        return 'Layered'
    return 'Monolithic'


# Function: _rp_api_readiness
def _rp_api_readiness(result, cloud_score) -> str:
    if result.cloud_recommendations:
        api_cats = [c for c in result.cloud_recommendations.by_category
                    if any(k in c.lower() for k in ('api', 'gateway', 'service', 'message'))]
        if api_cats:
            return 'API-Ready'
        if cloud_score >= 50:
            return 'Partial API Integration'
    elif cloud_score >= 50:
        return 'Partial API Integration'
    return 'Not Detected'


# Function: _rp_distributed
def _rp_distributed(result) -> str:
    is_distributed   = False
    dist_evidence: list = []
    if result.architecture:
        lc = result.architecture.layer_counts
        if lc.get('Services', 0) >= 3:
            is_distributed = True
            dist_evidence.append('Multiple service layers detected')
    if result.cloud_recommendations:
        gw_cats = [c for c in result.cloud_recommendations.by_category
                   if any(k in c.lower() for k in ('gateway', 'service bus', 'messaging', 'event'))]
        if gw_cats:
            is_distributed = True
            dist_evidence.append('API gateway / messaging patterns detected')
    return ('Yes - ' + '; '.join(dist_evidence)) if is_distributed else 'No - Centralized Architecture'


# Function: _rp_coupling_label
def _rp_coupling_label(dep_per_file: float, total_deps: int) -> str:
    if dep_per_file >= 5 or total_deps >= 100:
        return 'High'
    if dep_per_file >= 2 or total_deps >= 30:
        return 'Medium'
    return 'Low'


# Function: _rp_cloud_suitability
def _rp_cloud_suitability(cloud_score: float) -> str:
    if cloud_score >= 70:
        return 'Cloud-Ready'
    if cloud_score >= 45:
        return 'Partially Ready'
    return 'Lift-and-Shift Required'


# Function: _rp_dep_volume_label
def _rp_dep_volume_label(total_unique_deps: int) -> str:
    if total_unique_deps >= 50:
        return 'High'
    if total_unique_deps >= 15:
        return 'Medium'
    return 'Low'


# Function: _rp_protocol_degree
def _rp_protocol_degree(elegance: float, avg_comment: float) -> str:
    if elegance >= 70 and avg_comment >= 0.10:
        return 'High'
    if elegance >= 45 or avg_comment >= 0.05:
        return 'Moderate'
    return 'Low'


# Function: _rp_code_design
def _rp_code_design(elegance: float, total_bad: int) -> str:
    if elegance >= 70 and total_bad < 10:
        return 'Good'
    if elegance >= 45 or total_bad < 50:
        return 'Fair'
    return 'Poor'


# Function: _rp_complexity_level
def _rp_complexity_level(total_sloc: int, avg_cc: float) -> str:
    if total_sloc >= 50_000 or avg_cc >= 10:
        return 'High'
    if total_sloc >= 10_000 or avg_cc >= 5:
        return 'Medium'
    return 'Low'


# Function: _compute_rationalization_profile
def _compute_rationalization_profile(result) -> dict:
    """Derive the 14-field rationalization scorecard from analysis results."""
    import re as _re

    # 1. APP ID
    base = _re.sub(r'[^A-Z0-9]', '', result.repo_name.upper())
    app_id = (base[:10] if base else 'APP') + '_001'

    arch        = _rp_architecture(result)
    server_name = _rp_server_name(result)
    src_avail   = 'Available' if result.total_files > 0 else 'Not Available'
    repo_name   = result.repo_url or result.repo_name

    primary_lang = 'N/A'
    if result.language_reports:
        primary_lang = max(result.language_reports, key=lambda r: r.total_sloc).language
    all_langs = ', '.join(result.languages_detected) if result.languages_detected else 'N/A'

    total_deps   = sum(len(r.dependencies) for r in result.language_reports)
    dep_per_file = total_deps / max(result.total_files, 1)
    coupling     = _rp_coupling_label(dep_per_file, total_deps)

    cloud_score = result.cloud.total
    cloud_suit  = _rp_cloud_suitability(cloud_score)

    total_unique_deps = total_deps
    dep_volume_label  = _rp_dep_volume_label(total_unique_deps)

    api_ready = _rp_api_readiness(result, cloud_score)

    avg_comment = 0.0
    if result.language_reports:
        avg_comment = sum(r.comment_ratio for r in result.language_reports) / len(result.language_reports)
    elegance = result.health.elegance
    protocol_degree = _rp_protocol_degree(elegance, avg_comment)

    total_bad = sum(len(r.bad_practices) for r in result.language_reports if r.bad_practices)
    code_design = _rp_code_design(elegance, total_bad)

    avg_cc = 0.0
    if result.language_reports:
        avg_cc = sum(r.avg_complexity for r in result.language_reports) / len(result.language_reports)
    complexity_level = _rp_complexity_level(result.total_sloc, avg_cc)

    distributed_label = _rp_distributed(result)

    return {
        'app_id':                       app_id,
        'app_name':                     result.repo_name,
        'server_name':                  server_name,
        'repo_name':                    repo_name,
        'application_architecture':     arch,
        'source_code_availability':     src_avail,
        'programming_language':         all_langs,
        'primary_language':             primary_lang,
        'component_coupling':           coupling,
        'cloud_suitability':            cloud_suit,
        'cloud_score':                  round(cloud_score, 1),
        'volume_external_dependencies': f'{dep_volume_label} ({total_unique_deps} deps)',
        'total_deps_count':             total_unique_deps,
        'api_readiness':                api_ready,
        'code_protocol_degree':         protocol_degree,
        'code_design':                  code_design,
        'elegance_score':               round(elegance, 1),
        'complexity_volume':            f'{complexity_level} ({result.total_sloc:,} SLOC, avg CC={avg_cc:.1f})',
        'complexity_level':             complexity_level,
        'avg_cyclomatic':               round(avg_cc, 1),
        'distributed_architecture':     distributed_label,
    }


# â”€â”€â”€ DB persistence helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


# Function: _persist_green_impact
def _persist_green_impact(db, job_id: str, gi: dict) -> None:
    existing_green = db.query(CAGreen).filter_by(job_id=job_id).first()
    if existing_green:
        db.delete(existing_green)
        db.flush()
    green_row = CAGreen(
        job_id=job_id, green_score=gi.get("green_score"),
        total_occurrences=gi.get("total_occurrences"),
        total_effort_days=gi.get("total_effort_days"),
        risk_label=gi.get("risk_label"),
        category_totals=_json_mod.dumps(gi.get("category_totals") or {}),
    )
    db.add(green_row)
    db.flush()
    for deficiency in (gi.get("deficiencies") or []):
        db.add(CAGreenDeficiency(
            green_id=green_row.id, job_id=job_id,
            rule_key=deficiency.get("rule_key"), category=deficiency.get("category"),
            label=deficiency.get("label"), language=deficiency.get("language"),
            occurrences=deficiency.get("occurrences"), effort_days=deficiency.get("effort_days"),
            affected_files=_json_mod.dumps(deficiency.get("affected_files") or []),
        ))


# Function: _persist_architecture_data
def _persist_architecture_data(db, job_id: str, arch: dict) -> None:
    existing_arch = db.query(CAArchitecture).filter_by(job_id=job_id).first()
    if existing_arch:
        db.delete(existing_arch)
        db.flush()
    arch_row = CAArchitecture(
        job_id=job_id, total_files=arch.get("total_files"),
        has_data=arch.get("has_data"),
        layer_counts=_json_mod.dumps(arch.get("layer_counts") or {}),
        layer_sloc=_json_mod.dumps(arch.get("layer_sloc") or {}),
    )
    db.add(arch_row)
    db.flush()
    for layer in (arch.get("layers") or []):
        db.add(CAArchLayer(
            arch_id=arch_row.id, job_id=job_id,
            name=layer.get("name"), file_count=layer.get("file_count"),
            sloc=layer.get("sloc"), pct=layer.get("pct"),
            technologies=_json_mod.dumps(layer.get("technologies") or []),
        ))
    for node in (arch.get("nodes") or []):
        db.add(CAArchNode(
            arch_id=arch_row.id, job_id=job_id,
            name=node.get("name"), layer=node.get("layer"),
            language=node.get("language"), sloc=node.get("sloc"),
        ))


# Function: _persist_language_reports_data
def _persist_language_reports_data(db, job_id: str, result: dict) -> None:
    db.query(CALangReport).filter_by(job_id=job_id).delete(synchronize_session="fetch")
    for lr in (result.get("language_reports") or []):
        lang_row = CALangReport(
            job_id=job_id, language=lr.get("language"),
            file_count=lr.get("file_count"), total_sloc=lr.get("total_sloc"),
            avg_complexity=lr.get("avg_complexity"), max_complexity=lr.get("max_complexity"),
            total_functions=lr.get("total_functions"), total_classes=lr.get("total_classes"),
            long_methods_pct=lr.get("long_methods_pct"),
            deep_nesting_pct=lr.get("deep_nesting_pct"),
            comment_ratio=lr.get("comment_ratio"),
            bad_practices=_json_mod.dumps(lr.get("bad_practices") or {}),
            dependencies=_json_mod.dumps(lr.get("dependencies") or []),
        )
        db.add(lang_row)
        db.flush()
        for f in (lr.get("files") or []):
            db.add(CALangFile(
                lang_report_id=lang_row.id, job_id=job_id,
                name=f.get("name"), sloc=f.get("sloc"), total_lines=f.get("total_lines"),
                comment_lines=f.get("comment_lines"), blank_lines=f.get("blank_lines"),
                complexity=f.get("complexity"), cognitive=f.get("cognitive"),
                functions=f.get("functions"), classes=f.get("classes"),
                long_methods=f.get("long_methods"), deep_nesting=f.get("deep_nesting"),
                magic_numbers=f.get("magic_numbers"), todo_comments=f.get("todo_comments"),
                comment_ratio=f.get("comment_ratio"), error=f.get("error"),
            ))


# Function: _persist_to_db
def _replace_1to1(db, job_id: str, cls, **kwargs):
    existing = db.query(cls).filter_by(job_id=job_id).first()
    if existing:
        db.delete(existing)
        db.flush()
    obj = cls(job_id=job_id, **kwargs)
    db.add(obj)
    return obj


# Function: _persist_app_profile
def _persist_app_profile(db, job_id: str, result: dict) -> None:
    rp = result.get("rationalization_profile") or {}
    _replace_1to1(db, job_id, CAAppProfile,
        app_id=rp.get("app_id"), app_name=rp.get("app_name"),
        server_name=rp.get("server_name"), repo_name=result.get("repo_name"),
        total_sloc=result.get("total_sloc"), total_files=result.get("total_files"),
        languages_detected=_json_mod.dumps(result.get("languages_detected") or []),
        application_architecture=rp.get("application_architecture"),
        source_code_availability=rp.get("source_code_availability"),
        programming_language=rp.get("programming_language"),
        primary_language=rp.get("primary_language"),
        component_coupling=rp.get("component_coupling"),
        cloud_suitability=rp.get("cloud_suitability"),
        cloud_score=rp.get("cloud_score"),
        volume_external_deps=rp.get("volume_external_dependencies"),
        total_deps_count=rp.get("total_deps_count"),
        api_readiness=rp.get("api_readiness"),
        code_protocol_degree=rp.get("code_protocol_degree"),
        code_design=rp.get("code_design"),
        elegance_score=rp.get("elegance_score"),
        complexity_volume=rp.get("complexity_volume"),
        complexity_level=rp.get("complexity_level"),
        avg_cyclomatic=rp.get("avg_cyclomatic"),
        distributed_architecture=rp.get("distributed_architecture"),
    )


# Function: _persist_health_debt
def _persist_health_debt(db, job_id: str, result: dict) -> None:
    h = result.get("health") or {}
    _replace_1to1(db, job_id, CAHealth,
        health=h.get("health"), maintainability=h.get("maintainability"),
        reliability=h.get("reliability"), elegance=h.get("elegance"),
        risk_label=h.get("risk_label"),
    )

    d = result.get("debt") or {}
    _replace_1to1(db, job_id, CADebt,
        debt_months=d.get("debt_months"), debt_usd=d.get("debt_usd"),
        density=d.get("density"), interest_rate=d.get("interest_rate"),
        risk_label=d.get("risk_label"),
    )


# Function: _persist_cloud_and_oss
def _persist_cloud_and_oss(db, job_id: str, result: dict) -> None:
    cl = result.get("cloud") or {}
    _replace_1to1(db, job_id, CACloud,
        total=cl.get("total"), cloud_ready_scan=cl.get("cloud_ready_scan"),
        boosters_score=cl.get("boosters_score"), blockers_score=cl.get("blockers_score"),
        stateless_design=cl.get("stateless_design"), containerization=cl.get("containerization"),
        api_surface=cl.get("api_surface"), config_externalization=cl.get("config_externalization"),
        logging_observability=cl.get("logging_observability"), ci_cd_artifacts=cl.get("ci_cd_artifacts"),
        roadblocks_count=cl.get("roadblocks_count"),
        boosters=_json_mod.dumps(cl.get("boosters") or []),
        blockers=_json_mod.dumps(cl.get("blockers") or []),
    )

    # oss header
    oss = result.get("oss") or {}
    _replace_1to1(db, job_id, CAOss,
        total=oss.get("total"), vulnerable_count=oss.get("vulnerable_count"),
        cve_critical=oss.get("cve_critical"), cve_high=oss.get("cve_high"),
        cve_medium=oss.get("cve_medium"), cve_low=oss.get("cve_low"),
        license_high_risk=oss.get("license_high_risk"),
        license_medium_risk=oss.get("license_medium_risk"),
        license_low_risk=oss.get("license_low_risk"),
    )
    # oss deps (delete-all + re-insert)
    db.query(CAOssDep).filter_by(job_id=job_id).delete()
    for dep in (oss.get("details") or []):
        db.add(CAOssDep(
            job_id=job_id, name=dep.get("name"), ecosystem=dep.get("ecosystem"),
            latest_version=dep.get("latest_version"), license=dep.get("license"),
            license_risk=dep.get("license_risk"), vulnerable=dep.get("vulnerable"),
            vuln_count=dep.get("vuln_count"), cve_severity=dep.get("cve_severity"),
            cve_ids=_json_mod.dumps(dep.get("cve_ids") or []),
            age_years=dep.get("age_years"), age_ok=dep.get("age_ok"),
        ))


# Function: _persist_impact_co2
def _persist_impact_co2(db, job_id: str, result: dict) -> None:
    imp = result.get("impact") or {}
    _replace_1to1(db, job_id, CAImpact,
        total=imp.get("total"), criticality=imp.get("criticality"),
        reach=imp.get("reach"), revenue_risk=imp.get("revenue_risk"),
    )

    co2 = result.get("co2") or {}
    _replace_1to1(db, job_id, CACo2,
        co2_tons_year=co2.get("co2_tons_year"), energy_kwh_year=co2.get("energy_kwh_year"),
        cost_saving_usd=co2.get("cost_saving_usd"), trees_equivalent=co2.get("trees_equivalent"),
    )


# Function: _persist_green_and_arch
def _persist_green_and_arch(db, job_id: str, result: dict) -> None:
    # green impact (has child rows)
    gi = result.get("green_impact") or {}
    if gi:
        _persist_green_impact(db, job_id, gi)

    # architecture (has child rows)
    arch = result.get("architecture") or {}
    if arch:
        _persist_architecture_data(db, job_id, arch)

    # cloud recommendations
    crecs = result.get("cloud_recommendations") or {}
    if crecs:
        _replace_1to1(db, job_id, CACloudRecs,
            total_services=crecs.get("total_services"),
            detected_triggers=_json_mod.dumps(crecs.get("detected_triggers") or []),
            by_category=_json_mod.dumps(crecs.get("by_category") or {}),
        )


# Function: _persist_health_per_language
def _persist_health_per_language(db, job_id: str, result: dict) -> None:
    db.query(CAHealthPerLang).filter_by(job_id=job_id).delete()
    for hpl in (result.get("health_per_language") or []):
        if isinstance(hpl, dict):
            extras = {k: v for k, v in hpl.items()
                      if k not in ("language", "lang", "health", "debt_months", "risk_label")}
            db.add(CAHealthPerLang(
                job_id=job_id,
                language=hpl.get("language") or hpl.get("lang"),
                health=hpl.get("health"),
                debt_months=hpl.get("debt_months"),
                risk_label=hpl.get("risk_label"),
                extras=_json_mod.dumps(extras) if extras else None,
            ))


# Function: _persist_to_db
def _persist_to_db(job_id: str, result: dict, json_path: str, html_path: str) -> None:
    """Persist a completed analysis result and all tab data to SQLite."""
    if not _DB_ENABLED:
        return
    db = SessionLocal()
    try:
        job = db.get(CAJob, job_id)
        if not job:
            job = CAJob(job_id=job_id, job_type="single")
            db.add(job)
        job.status       = "done"
        job.progress     = 100
        job.repo_name    = result.get("repo_name")
        job.repo_url     = result.get("repo_url")
        job.json_path    = json_path
        job.html_path    = html_path
        job.completed_at = _dt_now()
        db.flush()

        _persist_app_profile(db, job_id, result)
        _persist_health_debt(db, job_id, result)
        _persist_cloud_and_oss(db, job_id, result)
        _persist_impact_co2(db, job_id, result)
        _persist_green_and_arch(db, job_id, result)

        # language reports + per-file rows
        _persist_language_reports_data(db, job_id, result)

        # health per language
        _persist_health_per_language(db, job_id, result)

        db.commit()
        logger.info("DB: persisted analysis job %s", job_id)
    except Exception as exc:
        db.rollback()
        logger.warning("DB persist failed for job %s: %s", job_id, exc)
    finally:
        db.close()


# Function: _build_ai_analysis_row
def _build_ai_analysis_row(parent_job_id: str, ai_job_id: str, report: dict, td: dict, cb: dict, ms: dict, br: dict, tr: dict, tabs: dict):
    return CAAiAnalysis(
        job_id=parent_job_id, ai_job_id=ai_job_id,
        model_used=report.get("model_used"), status="done",
        debt_summary=td.get("summary"),
        cloud_blockers_summary=cb.get("summary"),
        microservices_summary=ms.get("summary"),
        business_rules_summary=br.get("summary"),
        transformation_summary=tr.get("summary"),
        migration_readiness=cb.get("migration_readiness"),
        target_architecture=cb.get("target_architecture"),
        current_maturity=tr.get("current_maturity"),
        target_state=tr.get("target_state"),
        total_effort_months=tr.get("total_effort_months"),
        roi_narrative=tr.get("roi_narrative"),
        domain=br.get("domain"),
        key_entities=_json_mod.dumps(br.get("key_entities") or []),
        decomposition_strategy=ms.get("decomposition_strategy"),
        data_store_strategy=ms.get("data_store_strategy"),
        tab_assessments=_json_mod.dumps(tabs),
    )


# Function: _persist_ai_debt_hotspots
def _persist_ai_debt_hotspots(db, ai_row, parent_job_id: str, td: dict) -> None:
    for spot in (td.get("hotspots") or []):
        db.add(CAAiDebtHotspot(
            ai_analysis_id=ai_row.id, job_id=parent_job_id,
            file=spot.get("file"), priority=spot.get("priority"),
            issue=spot.get("issue"), recommendation=spot.get("recommendation"),
            root_cause=spot.get("root_cause"), impact=spot.get("impact"),
            effort_days=spot.get("effort_days"), debt_category=spot.get("debt_category"),
            metrics=_json_mod.dumps(spot.get("metrics") or {}),
        ))


# Function: _persist_ai_cloud_blockers_rows
def _persist_ai_cloud_blockers_rows(db, ai_row, parent_job_id: str, cb: dict) -> None:
    for blocker in (cb.get("blockers") or []):
        db.add(CAAiCloudBlocker(
            ai_analysis_id=ai_row.id, job_id=parent_job_id,
            title=blocker.get("title"), type=blocker.get("type"),
            severity=blocker.get("severity"), description=blocker.get("description"),
            fix_suggestion=blocker.get("fix_suggestion"),
            remediation=blocker.get("remediation"),
            effort_days=blocker.get("effort_days"),
        ))


# Function: _persist_ai_microservices_rows
def _persist_ai_microservices_rows(db, ai_row, parent_job_id: str, ms: dict) -> None:
    for svc in (ms.get("microservices") or []):
        db.add(CAAiMicroservice(
            ai_analysis_id=ai_row.id, job_id=parent_job_id,
            name=svc.get("name"), responsibility=svc.get("responsibility"),
            api_type=svc.get("api_type"), estimated_kloc=svc.get("estimated_kloc"),
            dependencies=_json_mod.dumps(svc.get("dependencies") or []),
            migration_order=svc.get("migration_order"),
        ))


# Function: _persist_ai_business_rules_rows
def _persist_ai_business_rules_rows(db, ai_row, parent_job_id: str, br: dict) -> None:
    for rule in (br.get("business_rules") or []):
        db.add(CAAiBusinessRule(
            ai_analysis_id=ai_row.id, job_id=parent_job_id,
            title=rule.get("title"), type=rule.get("type"),
            description=rule.get("description"), confidence=rule.get("confidence"),
            source_file=rule.get("source_file"),
        ))


# Function: _persist_ai_transform_paths_rows
def _persist_ai_transform_paths_rows(db, ai_row, parent_job_id: str, tr: dict) -> None:
    for path in (tr.get("transformation_paths") or []):
        db.add(CAAiTransformPath(
            ai_analysis_id=ai_row.id, job_id=parent_job_id,
            current=path.get("current"), recommended=path.get("recommended"),
            category=path.get("category"), value_score=path.get("value_score"),
            risk=path.get("risk"), steps=_json_mod.dumps(path.get("steps") or []),
        ))


# Function: _persist_ai_to_db
def _persist_ai_to_db(ai_job_id: str, parent_job_id: str, report: dict) -> None:
    """Persist a completed AI analysis result and all sub-analysis rows to SQLite."""
    if not _DB_ENABLED:
        return
    db = SessionLocal()
    try:
        parent = db.get(CAJob, parent_job_id)
        if not parent:
            logger.warning("DB: parent job %s not found, skipping AI persist", parent_job_id)
            return

        existing = db.query(CAAiAnalysis).filter_by(job_id=parent_job_id).first()
        if existing:
            db.delete(existing)
            db.flush()

        analyses = report.get("analyses") or {}
        td  = analyses.get("tech_debt") or {}
        cb  = analyses.get("cloud_blockers") or {}
        ms  = analyses.get("microservices") or {}
        br  = analyses.get("business_rules") or {}
        tr  = analyses.get("transformation") or {}
        tabs = report.get("tab_assessments") or {}

        ai_row = _build_ai_analysis_row(parent_job_id, ai_job_id, report, td, cb, ms, br, tr, tabs)
        db.add(ai_row)
        db.flush()

        _persist_ai_debt_hotspots(db, ai_row, parent_job_id, td)
        _persist_ai_cloud_blockers_rows(db, ai_row, parent_job_id, cb)
        _persist_ai_microservices_rows(db, ai_row, parent_job_id, ms)
        _persist_ai_business_rules_rows(db, ai_row, parent_job_id, br)
        _persist_ai_transform_paths_rows(db, ai_row, parent_job_id, tr)

        db.commit()
        logger.info("DB: persisted AI analysis %s for job %s", ai_job_id, parent_job_id)
    except Exception as exc:
        db.rollback()
        logger.warning("DB AI persist failed for %s: %s", ai_job_id, exc)
    finally:
        db.close()


# â”€â”€â”€ Background worker â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# Function: _run_analysis
def _run_analysis(job_id: str, req: AnalyseRequest):
    _job_write(job_id, {"status": "running", "progress": 5, "message": "Starting..."})
    try:
        repo_meta = None

        if req.local:
            repo_path = Path(req.local).expanduser().resolve()
            if not repo_path.exists():
                raise FileNotFoundError(f"Local path not found: {repo_path}")
            _job_update(job_id, progress=20, message="Reading local repository...")
        else:
            _job_update(job_id, progress=10, message="Fetching repository from GitHub...")
            fetcher   = GitHubFetcher()
            repo_meta = fetcher.fetch_repo(req.repo)
            repo_path = repo_meta.local_path
            if repo_path is None or not repo_path.exists():
                raise RuntimeError(
                    f"Clone of '{req.repo}' failed or produced an empty directory. "
                    "Check GitHub access, network connectivity, and core.longpaths setting."
                )
            _job_update(job_id, progress=35, message="Repository cloned. Analysing...")

        _job_update(job_id, progress=38, message="Starting code analysis...")

        # Function: _progress
        def _progress(pct: int, msg: str):
            # Map analyzer's 0-100 internal scale into 38-88 on overall job
            overall = 38 + int(pct * 0.50)
            _job_update(job_id, progress=overall, message=msg)

        result = CodeAnalyzer(
            repo_path = repo_path,
            repo_meta = repo_meta,
            users     = req.users,
            revenue   = req.revenue,
        ).run(progress_cb=_progress)

        _job_update(job_id, progress=90, message="Generating reports...")
        json_path = write_json(result, REPORT_DIR)
        html_path = write_html(result, REPORT_DIR)

        _job_write(job_id, {
            "status":    "done",
            "progress":  100,
            "message":   ANALYSIS_COMPLETE_MESSAGE,
            "result":    _result_to_dict(result),
            "json_path": str(json_path),
            "html_path": str(html_path),
            "repo_path": str(repo_path),   # persisted for AI analysis
        })
        try:
            _persist_to_db(job_id, _result_to_dict(result), str(json_path), str(html_path))
        except Exception as _dbe:
            logger.warning("DB persist skipped for job %s: %s", job_id, _dbe)
    except Exception as exc:
        logger.exception("Analysis job %s failed", job_id)
        _job_write(job_id, {
            "status":  "error",
            "progress": 0,
            "message": str(exc),
        })


# Function: _safe_extract_zip
def _safe_extract_zip(zip_path: Path, dest_dir: Path) -> None:
    """
    Extract *zip_path* into *dest_dir*, guarding against zip-slip path
    traversal and zip-bomb-style abuse â€” checked BEFORE any file is written:
      - Absolute paths and any entry containing a '..' path component are
        rejected outright.
      - Every remaining entry's resolved destination must stay within
        dest_dir (defense in depth beyond the '..' check, e.g. against
        platform-specific path quirks).
      - Cumulative uncompressed size and file count are capped; extraction
        aborts the moment either limit is exceeded, so a small malicious
        archive can't exhaust disk space or file-count limits.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_root = dest_dir.resolve()
    total_bytes = 0
    total_files = 0

    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.infolist():
            if member.is_dir():
                continue
            name = member.filename
            if name.startswith(("/", "\\")) or ".." in Path(name).parts:
                raise ValueError(f"Refusing to extract unsafe archive entry: {name!r}")

            target = (dest_root / name).resolve()
            if target != dest_root and dest_root not in target.parents:
                raise ValueError(f"Refusing to extract archive entry outside target directory: {name!r}")

            total_files += 1
            if total_files > MAX_UPLOAD_FILE_COUNT:
                raise ValueError(f"Upload exceeds the {MAX_UPLOAD_FILE_COUNT}-file limit.")
            total_bytes += member.file_size
            if total_bytes > MAX_UPLOAD_EXTRACTED_BYTES:
                raise ValueError(
                    f"Upload exceeds the {MAX_UPLOAD_EXTRACTED_BYTES // (1024 * 1024)} MB decompressed-size limit."
                )

            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(member) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)


# Function: _run_analysis_from_upload
def _run_analysis_from_upload(job_id: str, zip_path: Path, users: int, revenue: float):
    """
    Same pipeline as _run_analysis, but the source is a client-uploaded zip of
    a local folder rather than a GitHub clone or a server-local path string.
    Needed because 'Local Path' analysis can only ever see paths that already
    exist on THIS server's filesystem â€” it has no way to reach a folder that
    only exists on the browser's own machine. The frontend zips the selected
    folder client-side and uploads it here; we extract it into a scratch
    directory and analyse it exactly like any other local repo.

    The extracted directory is kept on disk (not deleted after analysis) for
    parity with GitHub-cloned repos, which persist under CLONE_DIR â€” the
    'AI Analysis' follow-on feature reads job['repo_path'] and re-scans the
    actual files later for call-graph/knowledge-graph/deep-LLM analysis, so
    deleting it immediately would silently break that feature only for
    uploaded repos. Only the now-redundant uploaded .zip itself is removed
    (its contents are already extracted, so keeping it would just double the
    disk usage for no benefit).
    """
    extract_dir = UPLOAD_DIR / job_id / "extracted"
    _job_write(job_id, {"status": "running", "progress": 5, "message": "Extracting uploaded folder..."})
    try:
        _safe_extract_zip(zip_path, extract_dir)
        if not any(extract_dir.iterdir()):
            raise ValueError("Uploaded archive was empty after extraction.")

        _job_update(job_id, progress=20, message="Uploaded folder extracted. Analysing...")

        # Function: _progress
        def _progress(pct: int, msg: str):
            overall = 38 + int(pct * 0.50)
            _job_update(job_id, progress=overall, message=msg)

        _job_update(job_id, progress=38, message="Starting code analysis...")
        result = CodeAnalyzer(
            repo_path = extract_dir,
            repo_meta = None,
            users     = users,
            revenue   = revenue,
        ).run(progress_cb=_progress)

        _job_update(job_id, progress=90, message="Generating reports...")
        json_path = write_json(result, REPORT_DIR)
        html_path = write_html(result, REPORT_DIR)

        _job_write(job_id, {
            "status":    "done",
            "progress":  100,
            "message":   ANALYSIS_COMPLETE_MESSAGE,
            "result":    _result_to_dict(result),
            "json_path": str(json_path),
            "html_path": str(html_path),
            "repo_path": str(extract_dir),   # persisted for AI analysis, matching _run_analysis
        })
        try:
            _persist_to_db(job_id, _result_to_dict(result), str(json_path), str(html_path))
        except Exception as _dbe:
            logger.warning("DB persist skipped for job %s: %s", job_id, _dbe)
    except Exception as exc:
        logger.exception("Upload analysis job %s failed", job_id)
        _job_write(job_id, {
            "status":  "error",
            "progress": 0,
            "message": str(exc),
        })
    finally:
        # The zip's contents are already extracted onto disk â€” keeping the
        # archive itself around too would just double disk usage for nothing.
        try:
            zip_path.unlink(missing_ok=True)
        except Exception:
            pass


# Function: _run_portfolio
def _run_portfolio(job_id: str, req: PortfolioRequest):
    _job_write(job_id, {"status": "running", "progress": 5, "message": "Fetching organisation..."})
    try:
        fetcher = GitHubFetcher()
        repos   = fetcher.fetch_organisation(req.org, limit=req.limit)
        if not repos:
            raise ValueError(f"No repositories found for org: {req.org}")

        results = []
        for i, meta in enumerate(repos):
            pct = 10 + int((i / len(repos)) * 80)
            _job_update(
                job_id,
                progress=pct,
                message=f"Analysing {meta.full_name} ({i+1}/{len(repos)})..."
            )
            try:
                result = CodeAnalyzer(repo_path=meta.local_path, repo_meta=meta).run()
                write_json(result, REPORT_DIR)
                write_html(result, REPORT_DIR)
                results.append(_result_to_dict(result))
            except Exception as exc:
                logger.warning("Skipping %s: %s", meta.full_name, exc)

        _job_write(job_id, {
            "status":   "done",
            "progress": 100,
            "message":  f"Portfolio analysis complete - {len(results)} repos",
            "results":  results,
        })
    except Exception as exc:
        logger.exception("Portfolio job %s failed", job_id)
        _job_write(job_id, {"status": "error", "progress": 0, "message": str(exc)})


# â”€â”€â”€ Routes â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# Function: health
@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


# Function: auth_session
@app.get("/api/auth/session")
def auth_session(request: Request):
    try:
        payload = getattr(request.state, "auth", None)
        if not payload:
            return {
                "authenticated": False,
                "user": None,
                "expires_at": None,
            }

        return {
            "authenticated": True,
            "user": {
                "id": payload.get("uid"),
                "username": payload.get("username"),
                "role": payload.get("role"),
                "apps": payload.get("apps") or [],
            },
            "expires_at": payload.get("exp"),
        }
    except Exception as exc:
        logger.exception("auth_session error: %s", exc)
        return JSONResponse(
            status_code=200,
            content={
                "authenticated": False,
                "user": None,
                "expires_at": None,
                "error": str(exc),
            },
        )


_MODULES_EXCLUDE_DIRS = {
    'node_modules', '.venv', 'venv', '__pycache__', '.git', '.pytest_cache',
    'dist', 'build', 'htmlcov', '.tox', 'env', '.env',
    '.next', '.nuxt', 'out', '.cache', 'vendor', 'target', 'bin', 'obj',
    '.mypy_cache', '.eggs', 'release', 'debug',
}
_MODULES_SOURCE_EXTS = {
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".java", ".cs", ".go", ".rs", ".cpp", ".c", ".h",
    ".html", ".css", ".scss", ".xml", ".json", ".yaml", ".yml",
    ".sql", ".sh", ".bash", ".ps1", ".vb", ".swift", ".kt",
    ".rb", ".php", ".pl", ".r", ".lua", ".dart", ".scala",
}
# Project-marker files that indicate a standalone project
_MODULES_PROJECT_MARKERS = [
    "package.json", "requirements.txt", "setup.py", "pyproject.toml",
    "pom.xml", "build.gradle", "build.gradle.kts", "Cargo.toml",
    "go.mod", "composer.json", "Gemfile", "CMakeLists.txt",
    "Makefile", "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
]
_MODULES_GLOB_MARKERS = ["*.csproj", "*.sln", "*.vbproj"]


# Function: _count_module_files
def _count_module_files(path: Path) -> int:
    try:
        count = 0
        for fp in path.rglob("*"):
            if any(ex in fp.parts for ex in _MODULES_EXCLUDE_DIRS):
                continue
            if any(p.endswith('.egg-info') for p in fp.parts):
                continue
            if fp.is_file() and fp.suffix.lower() in _MODULES_SOURCE_EXTS:
                count += 1
        return count
    except Exception:
        return 0


# Function: _is_standalone_project
def _is_standalone_project(path: Path) -> bool:
    for marker in _MODULES_PROJECT_MARKERS:
        if (path / marker).exists():
            return True
    for glob_pat in _MODULES_GLOB_MARKERS:
        if list(path.glob(glob_pat)):
            return True
    root_sources = [f for f in path.iterdir() if f.is_file() and f.suffix.lower() in _MODULES_SOURCE_EXTS]
    return len(root_sources) >= 5


# Function: _resolve_modules_scan_root
def _resolve_modules_scan_root(job_id: Optional[str]) -> Path:
    if job_id:
        job_data = _job_read(job_id)
        repo_path_str = (job_data or {}).get("repo_path", "")
        if repo_path_str:
            candidate = Path(repo_path_str)
            if candidate.exists():
                return candidate
    # Fall back: workspace root (two levels up from CodeAnalysis/api/)
    return Path(__file__).resolve().parent.parent.parent


# Function: _discover_modules
def _discover_modules(scan_root: Path) -> list:
    modules = []
    try:
        for entry in sorted(scan_root.iterdir()):
            if not entry.is_dir():
                continue
            if entry.name in _MODULES_EXCLUDE_DIRS or entry.name.startswith('.'):
                continue
            file_count = _count_module_files(entry)
            if file_count > 0:
                modules.append({
                    "name":       entry.name,
                    "path":       str(entry),
                    "exists":     True,
                    "file_count": file_count,
                    "is_project": _is_standalone_project(entry),
                })
    except Exception:
        pass
    return modules


# Function: list_aqorynth_modules
@app.get("/api/modules")
def list_aqorynth_modules(job_id: Optional[str] = None):
    """Discover project modules.

    When *job_id* is supplied the subdirectories of that job's scanned
    repository are returned, so the module list always reflects the project
    that was actually scanned.  Falls back to workspace-root discovery when
    no job_id is given.
    """
    scan_root = _resolve_modules_scan_root(job_id)
    modules = _discover_modules(scan_root)
    return {"modules": modules, "workspace_root": str(scan_root)}


# â”€â”€â”€ Strat-Aqorynth Module Analysis â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class StratAqorynthModuleItem(BaseModel):
    name: str
    path: str

class StratAqorynthAnalyseRequest(BaseModel):
    modules: List[StratAqorynthModuleItem]


# Function: _run_aqorynth_analysis
def _run_aqorynth_analysis(job_id: str, modules: List[dict]) -> None:
    try:
        from services.aqorynth_analysis import run_aqorynth_module_analysis
    except ImportError as exc:
        _job_update(job_id, status="error", progress=100, message=f"Service unavailable: {exc}")
        return

    total = len(modules)
    results_map: dict = {}
    completed_count = [0]
    lock = threading.Lock()

    # Function: _analyse_module
    def _analyse_module(mod: dict) -> dict:
        # Function: _on_progress
        def _on_progress(phase, pct, msg):
            with lock:
                done = completed_count[0]
            base_pct = int((done / total) * 90)
            overall = base_pct + int(pct / 100 * (90 / total))
            _job_update(job_id, progress=overall, message=msg, current_module=mod["name"])

        try:
            return run_aqorynth_module_analysis(
                module_path=mod["path"],
                module_name=mod["name"],
                on_progress=_on_progress,
            )
        except Exception as exc:
            logger.warning("Strat-Aqorynth analysis failed for %s: %s", mod["name"], exc)
            return {"module_name": mod["name"], "module_path": mod["path"], "error": str(exc)}

    # Run up to 3 modules concurrently; each module itself uses up to 6 internal threads,
    # so the total thread pool stays bounded (3 Ã— 6 = 18 threads maximum).
    max_workers = min(3, total)
    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="strat-aqorynth-mod") as pool:
        future_to_mod = {pool.submit(_analyse_module, mod): mod for mod in modules}
        for future in as_completed(future_to_mod):
            mod = future_to_mod[future]
            result = future.result()
            results_map[mod["path"]] = result
            with lock:
                completed_count[0] += 1
            pct = int((completed_count[0] / total) * 90)
            # Publish partial results immediately so the SSE stream delivers
            # completed module cards to the UI without waiting for all modules.
            partial = [results_map[m["path"]] for m in modules if m["path"] in results_map]
            _job_update(job_id, progress=pct, message=f"Completed {mod['name']}",
                        current_module=mod["name"], results=partial)

    # Final ordered results list (order matches what the user selected).
    results = [results_map[mod["path"]] for mod in modules if mod["path"] in results_map]
    _job_update(job_id, status="done", progress=100, message=ANALYSIS_COMPLETE_MESSAGE, results=results)


# Function: aqorynth_analyse
@app.post("/api/strat-aqorynth/analyse")
def aqorynth_analyse(req: StratAqorynthAnalyseRequest, bg: BackgroundTasks):
    if not req.modules:
        raise HTTPException(400, "No modules selected")
    import uuid
    job_id = str(uuid.uuid4())
    mods = [{"name": m.name, "path": m.path} for m in req.modules]
    _job_write(job_id, {
        "status": "running", "progress": 0,
        "message": "Starting Strat-Aqorynth Module Analysis...",
        "current_module": None, "results": [],
    })
    bg.add_task(_run_aqorynth_analysis, job_id, mods)
    return {"job_id": job_id}


# Function: get_aqorynth_job
@app.get("/api/strat-aqorynth/jobs/{job_id}")
def get_aqorynth_job(job_id: str):
    job = _job_read(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job


# Function: stream_aqorynth_job
@app.get("/api/strat-aqorynth/jobs/{job_id}/stream")
async def stream_aqorynth_job(job_id: str, request: Request):
    """Server-Sent Events stream for real-time Strat-Aqorynth job progress.

    Polls the in-memory job cache at 5 Hz and pushes state changes as SSE
    events.  The client can send an Authorization header via fetch() (SSE via
    EventSource does not support custom headers).
    """
    # Function: event_generator
    async def event_generator():
        last_key = None
        while True:
            if await request.is_disconnected():
                break

            job = _job_read(job_id)
            if job is None:
                yield f"data: {json.dumps({'status': 'error', 'message': 'Job not found'})}\n\n"
                break

            # Only push when something changed to avoid redundant events.
            key = (job.get("progress"), job.get("status"),
                   job.get("current_module"), len(job.get("results") or []))
            if key != last_key:
                last_key = key
                yield f"data: {json.dumps(job)}\n\n"

            if job.get("status") in ("done", "error"):
                break

            await asyncio.sleep(0.2)   # 5 Hz â€” reads only memory, no disk I/O

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# Function: start_analyse
@app.post("/api/analyse")
def start_analyse(req: AnalyseRequest, bg: BackgroundTasks):
    if not req.repo and not req.local:
        raise HTTPException(400, "Provide 'repo' or 'local'")
    import uuid
    job_id = str(uuid.uuid4())
    bg.add_task(_run_analysis, job_id, req)
    return {"job_id": job_id}


# Function: _write_upload_to_disk
def _write_upload_to_disk(source, destination: Path) -> None:
    """Copy an uploaded file without blocking the async request event loop."""
    written = 0
    with open(destination, "wb") as output:
        while chunk := source.read(1024 * 1024):
            written += len(chunk)
            if written > MAX_UPLOAD_ZIP_BYTES:
                raise HTTPException(
                    413,
                    f"Upload exceeds the {MAX_UPLOAD_ZIP_BYTES // (1024 * 1024)} MB limit.",
                )
            output.write(chunk)


# Function: start_analyse_upload
@app.post("/api/analyse/upload")
async def start_analyse_upload(
    bg: BackgroundTasks,
    file: UploadFile = File(...),
    users: int = Form(100),
    revenue: float = Form(0.0),
):
    """
    Analyse a local folder that only exists on the caller's own machine.
    'Local Path' analysis can only see paths already on this server's
    filesystem â€” this endpoint is the actual way to analyse code that lives
    solely on the user's own computer: the frontend zips the selected folder
    client-side and posts it here as a multipart file upload.
    """
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(400, "Upload must be a .zip archive of the folder to analyse")

    import uuid
    job_id = str(uuid.uuid4())
    zip_path = UPLOAD_DIR / f"{job_id}.zip"

    # Stream to disk with an early size cutoff â€” never buffer the whole
    # upload in memory, and never let a request past MAX_UPLOAD_ZIP_BYTES
    # write anything beyond that limit to disk.
    try:
        await asyncio.to_thread(_write_upload_to_disk, file.file, zip_path)
    except HTTPException:
        zip_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        zip_path.unlink(missing_ok=True)
        raise HTTPException(400, f"Failed to read upload: {exc}") from exc

    if not zipfile.is_zipfile(zip_path):
        zip_path.unlink(missing_ok=True)
        raise HTTPException(400, "Uploaded file is not a valid zip archive")

    bg.add_task(_run_analysis_from_upload, job_id, zip_path, users, revenue)
    return {"job_id": job_id}


# Function: start_portfolio
@app.post("/api/portfolio")
def start_portfolio(req: PortfolioRequest, bg: BackgroundTasks):
    import uuid
    job_id = str(uuid.uuid4())
    bg.add_task(_run_portfolio, job_id, req)
    return {"job_id": job_id}


# Function: get_job
@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    job = _job_read(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job


# Function: list_reports
@app.get("/api/reports")
def list_reports():
    reports = []
    if REPORT_DIR.exists():
        for f in sorted(REPORT_DIR.glob("*.json"), reverse=True)[:50]:
            reports.append({
                "name":     f.name,
                "size":     f.stat().st_size,
                "modified": f.stat().st_mtime,
            })
    return {"reports": reports}


# Function: get_report
@app.get("/api/reports/{filename}")
def get_report(filename: str):
    path = REPORT_DIR / filename
    if not path.exists() or path.suffix != ".json":
        raise HTTPException(404, "Report not found")
    return FileResponse(path, media_type="application/json")


# â”€â”€â”€ AI / Ollama routes â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class AIAnalyseRequest(BaseModel):
    job_id:   str               # completed analysis job_id to enrich with AI
    model:    Optional[str] = None
    selected: Optional[List[str]] = None  # subset of analyses to run

class PullModelRequest(BaseModel):
    model_id: str

_ai_client = OllamaClient()

# Function: ai_health
@app.get("/api/ai/health")
def ai_health():
    """Check Ollama connectivity and return installed models."""
    health  = _ai_client.health()
    models  = _ai_client.list_models() if health.get("ok") else []
    best    = _ai_client.best_available_model()
    return {
        "ollama":      health,
        "models":      models,
        "best_model":  best,
        "recommended": RECOMMENDED_MODELS,
    }


# Function: ai_models
@app.get("/api/ai/models")
def ai_models():
    """List locally installed Ollama models with recommended metadata."""
    return {"models": _ai_client.list_models(), "best": _ai_client.best_available_model()}


# Function: ai_pull_model
@app.post("/api/ai/pull-model")
def ai_pull_model(req: PullModelRequest, bg: BackgroundTasks):
    """Trigger a background pull of an Ollama model."""
    import uuid
    job_id = f"pull_{req.model_id.replace(':', '_')}_{uuid.uuid4().hex[:8]}"

    # Function: _do_pull
    def _do_pull(jid: str, mid: str):
        _job_write(jid, {"status": "running", "progress": 0, "message": f"Pulling {mid}...", "model_id": mid})
        # Function: _cb
        def _cb(status, total, completed):
            pct = int(completed / total * 100) if total else 0
            _job_update(jid, progress=pct, message=f"{status} ({pct}%)")
        result = _ai_client.pull_model(mid, progress_callback=_cb)
        if result["ok"]:
            _job_write(jid, {"status": "done", "progress": 100, "message": f"{mid} ready", "model_id": mid})
        else:
            _job_write(jid, {"status": "error", "progress": 0, "message": result.get("error", "pull failed"), "model_id": mid})

    bg.add_task(_do_pull, job_id, req.model_id)
    return {"job_id": job_id, "model_id": req.model_id}


# Function: _resolve_repo_path_for_ai
def _resolve_repo_path_for_ai(src: dict, analysis_result: dict) -> str:
    # Primary: repo_path is stored directly in the analysis job (added in _run_analysis)
    repo_path_resolved = src.get("repo_path", "")
    if repo_path_resolved and Path(repo_path_resolved).exists():
        return repo_path_resolved

    # Fallback: reconstruct from cloned_repos using repo_name field
    cloned_root = Path(__file__).resolve().parent.parent / "cloned_repos"
    repo_name   = analysis_result.get("repo_name", "")
    # repo_name is stored as "owner/repo" â€” reconstruct OS path
    if repo_name and "/" in repo_name:
        owner, name = repo_name.split("/", 1)
        candidate = cloned_root / owner / name
    else:
        # Try wildcard search as last resort
        safe_name = repo_name.replace("/", "_").replace(" ", "_")
        matches = list(cloned_root.glob(f"*/{safe_name}")) if cloned_root.exists() else []
        candidate = matches[0] if matches else cloned_root
    return str(candidate) if candidate.exists() else str(cloned_root)


# Function: _run_ai_analysis_job
def _run_ai_analysis_job(jid: str, src: dict, model: str | None, selected, orig_job_id: str) -> None:
    _job_write(jid, {"status": "running", "progress": 5, "message": "Starting AI analysis...", "type": "ai"})
    analysis_result = src.get("result", {})
    repo_path_resolved = _resolve_repo_path_for_ai(src, analysis_result)

    # Function: _prog
    def _prog(name, cur, tot):
        pct = int(cur / tot * 95) + 5
        _job_update(jid, progress=pct, message=f"Running: {name} ({cur}/{tot})...")

    try:
        report = run_ai_analysis(
            analysis_result = analysis_result,
            repo_path       = repo_path_resolved,
            model           = model,
            progress_callback = _prog,
            selected        = selected,
        )
        _job_write(jid, {
            "status":   "done",
            "progress": 100,
            "message":  "AI analysis complete",
            "type":     "ai",
            "result":   report,
        })
        try:
            _persist_ai_to_db(jid, orig_job_id, report)
        except Exception as _dbe:
            logger.warning("AI DB persist skipped for %s: %s", jid, _dbe)
    except Exception as exc:
        logger.exception("AI job %s failed", jid)
        _job_write(jid, {"status": "error", "progress": 0, "message": str(exc), "type": "ai"})


# Function: _run_ai_with_semaphore
def _run_ai_with_semaphore(jid: str, src: dict, model: str | None, selected, orig_job_id: str) -> None:
    _job_write(jid, {"status": "queued", "progress": 0, "message": "Queued - waiting for a free analysis slot...", "type": "ai"})
    _AI_SEMAPHORE.acquire()
    try:
        _run_ai_analysis_job(jid, src, model, selected, orig_job_id)
    finally:
        _AI_SEMAPHORE.release()


# Function: start_ai_analyse
@app.post("/api/ai/analyse")
def start_ai_analyse(req: AIAnalyseRequest, bg: BackgroundTasks):
    """
    Launch an AI intelligence analysis on top of an existing completed analysis job.
    Returns an ai_job_id to poll via GET /api/ai/jobs/{ai_job_id}.
    """
    src_job = _job_read(req.job_id)
    if not src_job:
        raise HTTPException(404, f"Analysis job {req.job_id!r} not found")
    if src_job.get("status") != "done":
        raise HTTPException(400, f"Analysis job {req.job_id!r} not finished (status={src_job.get('status')})")

    import uuid
    ai_job_id = f"ai_{uuid.uuid4().hex}"

    bg.add_task(_run_ai_with_semaphore, ai_job_id, src_job, req.model, req.selected, req.job_id)
    return {"ai_job_id": ai_job_id}


# Function: get_ai_job
@app.get("/api/ai/jobs/{job_id}")
def get_ai_job(job_id: str):
    job = _job_read(job_id)
    if not job:
        raise HTTPException(404, "AI job not found")
    return job


# Function: get_call_graph
@app.get("/api/ai/call-graph")
def get_call_graph(job_id: str, max_files: int = 200):
    """Build and return the call graph for a completed analysis job."""
    src_job = _job_read(job_id)
    if not src_job or src_job.get("status") != "done":
        raise HTTPException(404, "Completed analysis job not found")
    analysis_result = src_job.get("result", {})
    repo_name = analysis_result.get("repo_name", "")
    cloned_root = Path(__file__).resolve().parent.parent / "cloned_repos"
    safe_name   = repo_name.replace("/", "_").replace(" ", "_")
    candidate   = cloned_root / safe_name
    if not candidate.exists():
        matches = list(cloned_root.glob(f"*{safe_name}*")) if cloned_root.exists() else []
        candidate = matches[0] if matches else cloned_root
    try:
        cg = build_call_graph(str(candidate), max_files=max_files)
        return cg
    except Exception as exc:
        raise HTTPException(500, str(exc))


# Function: _find_cloned_repo_candidate
def _find_cloned_repo_candidate(repo_name: str, cloned_root: Path) -> "Path | None":
    # Try user/repo nested structure  (e.g. "owner/BankingPortal-API")
    parts = [p for p in repo_name.replace("\\", "/").split("/") if p]
    for depth in range(len(parts), 0, -1):
        deep = cloned_root.joinpath(*parts[:depth])
        if deep.exists():
            return deep

    safe_name = repo_name.replace("/", "_").replace(" ", "_")
    flat = cloned_root / safe_name
    if flat.exists():
        return flat

    matches = list(cloned_root.glob(f"*{safe_name}*")) if cloned_root.exists() else []
    return matches[0] if matches else None


# Function: _resolve_repo_path_for_kg
def _resolve_repo_path_for_kg(src_job: dict, job_id: str) -> str:
    # â”€â”€ Resolve repository path (same logic as _run_ai) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Primary: repo_path is stored top-level in the job dict (set in _run_analysis).
    # This covers local-path repos which are never inside cloned_repos/.
    repo_path_resolved = src_job.get("repo_path", "")
    if repo_path_resolved and Path(repo_path_resolved).exists():
        return repo_path_resolved

    # Fallback: reconstruct from cloned_repos/ using the repo_name field.
    analysis_result = src_job.get("result", {})
    repo_name       = analysis_result.get("repo_name", "")
    cloned_root     = Path(__file__).resolve().parent.parent / "cloned_repos"

    candidate = _find_cloned_repo_candidate(repo_name, cloned_root)
    if candidate is None or not candidate.exists():
        raise HTTPException(
            404,
            f"Repository source not found on disk for job {job_id}. "
            "Re-run the analysis so the path is recorded."
        )
    return str(candidate)


# Function: get_knowledge_graph
@app.get("/api/ai/knowledge-graph")
def get_knowledge_graph(job_id: str, max_files: int = 300):
    """Build and return the full codebase knowledge graph for a completed analysis job.

    Nodes: modules (files), classes, functions/methods.
    Edges: contains, imports, inherits, calls.
    """
    src_job = _job_read(job_id)
    if not src_job or src_job.get("status") != "done":
        raise HTTPException(404, "Completed analysis job not found")

    repo_path_resolved = _resolve_repo_path_for_kg(src_job, job_id)

    try:
        kg = build_knowledge_graph(repo_path_resolved, max_files=max_files)
        return kg
    except Exception as exc:
        raise HTTPException(500, str(exc))


# â”€â”€â”€ Database Query Endpoints â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# Function: db_list_analyses
@app.get("/api/db/analyses")
def db_list_analyses(limit: int = 50, offset: int = 0):
    """List all single-repo analysis jobs stored in the DB."""
    if not _DB_ENABLED:
        raise HTTPException(503, DATABASE_NOT_AVAILABLE_MESSAGE)
    from sqlalchemy import desc as _desc
    db = SessionLocal()
    try:
        jobs  = (db.query(CAJob)
                   .filter(CAJob.job_type == "single")
                   .order_by(_desc(CAJob.created_at))
                   .offset(offset).limit(limit).all())
        total = db.query(CAJob).filter(CAJob.job_type == "single").count()
        return {"analyses": [j.to_dict() for j in jobs], "total": total}
    finally:
        db.close()


# Function: db_get_analysis
@app.get("/api/db/analyses/{job_id}")
def db_get_analysis(job_id: str):
    """Get full analysis including all tab data rows."""
    if not _DB_ENABLED:
        raise HTTPException(503, DATABASE_NOT_AVAILABLE_MESSAGE)
    db = SessionLocal()
    try:
        job = db.get(CAJob, job_id)
        if not job:
            raise HTTPException(404, ANALYSIS_NOT_FOUND_MESSAGE)
        result = job.to_dict()
        result["app_profile"]     = job.app_profile.to_dict() if job.app_profile else None
        result["health"]          = job.health.to_dict() if job.health else None
        result["debt"]            = job.debt.to_dict() if job.debt else None
        result["cloud"]           = job.cloud.to_dict() if job.cloud else None
        result["oss"]             = job.oss.to_dict() if job.oss else None
        result["oss_deps"]        = [d.to_dict() for d in job.oss_deps]
        result["impact"]          = job.impact.to_dict() if job.impact else None
        result["co2"]             = job.co2.to_dict() if job.co2 else None
        result["green"]           = job.green.to_dict() if job.green else None
        result["architecture"]    = job.architecture.to_dict() if job.architecture else None
        result["cloud_recs"]      = job.cloud_recs.to_dict() if job.cloud_recs else None
        result["lang_reports"]    = [lr.to_dict() for lr in job.lang_reports]
        result["health_per_lang"] = [hl.to_dict() for hl in job.health_per_lang]
        result["ai_analysis"]     = job.ai_analysis.to_dict() if job.ai_analysis else None
        return result
    finally:
        db.close()


# Function: db_get_ai_analysis
@app.get("/api/db/analyses/{job_id}/ai")
def db_get_ai_analysis(job_id: str):
    """Get AI analysis for a job including all sub-analysis rows."""
    if not _DB_ENABLED:
        raise HTTPException(503, DATABASE_NOT_AVAILABLE_MESSAGE)
    db = SessionLocal()
    try:
        ai = db.query(CAAiAnalysis).filter_by(job_id=job_id).first()
        if not ai:
            raise HTTPException(404, "No AI analysis found for this job")
        result = ai.to_dict()
        result["debt_hotspots"]   = [h.to_dict() for h in ai.debt_hotspots]
        result["cloud_blockers"]  = [b.to_dict() for b in ai.cloud_blockers]
        result["microservices"]   = [m.to_dict() for m in ai.microservices]
        result["business_rules"]  = [r.to_dict() for r in ai.business_rules]
        result["transform_paths"] = [p.to_dict() for p in ai.transform_paths]
        return result
    finally:
        db.close()


# Function: _dict_or_none
def _dict_or_none(obj):
    return obj.to_dict() if obj else None


# Function: _tab_overview_data
def _tab_overview_data(job) -> dict:
    return {
        "health": _dict_or_none(job.health),
        "debt":   _dict_or_none(job.debt),
        "cloud":  _dict_or_none(job.cloud),
        "oss":    _dict_or_none(job.oss),
        "impact": _dict_or_none(job.impact),
    }


# Function: _tab_security_data
def _tab_security_data(job) -> dict:
    return {
        "oss":      _dict_or_none(job.oss),
        "oss_deps": [d.to_dict() for d in job.oss_deps],
    }


# Function: _tab_practices_data
def _tab_practices_data(job) -> list:
    return [
        {"language": lr.language, "bad_practices": lr.to_dict().get("bad_practices")}
        for lr in job.lang_reports
    ]


# Function: _build_tab_map
def _build_tab_map(job) -> dict:
    return {
        "app_profile":    lambda: _dict_or_none(job.app_profile),
        "overview":       lambda: _tab_overview_data(job),
        "security":       lambda: _tab_security_data(job),
        "cloud":          lambda: _dict_or_none(job.cloud),
        "cloud_services": lambda: _dict_or_none(job.cloud_recs),
        "co2":            lambda: _dict_or_none(job.co2),
        "green":          lambda: _dict_or_none(job.green),
        "architecture":   lambda: _dict_or_none(job.architecture),
        "languages":      lambda: [lr.to_dict() for lr in job.lang_reports],
        "health_tech":    lambda: [hl.to_dict() for hl in job.health_per_lang],
        "debt_detail":    lambda: _dict_or_none(job.debt),
        "practices":      lambda: _tab_practices_data(job),
        "ai_insights":    lambda: _dict_or_none(job.ai_analysis),
    }


# Function: db_get_tab_data
@app.get("/api/db/analyses/{job_id}/tab/{tab_key}")
def db_get_tab_data(job_id: str, tab_key: str):
    """Get data for a specific dashboard tab from the DB."""
    if not _DB_ENABLED:
        raise HTTPException(503, DATABASE_NOT_AVAILABLE_MESSAGE)
    db = SessionLocal()
    try:
        job = db.get(CAJob, job_id)
        if not job:
            raise HTTPException(404, ANALYSIS_NOT_FOUND_MESSAGE)
        tab_map = _build_tab_map(job)
        if tab_key not in tab_map:
            raise HTTPException(400, f"Unknown tab '{tab_key}'. Valid: {sorted(tab_map)}")
        return {"tab": tab_key, "job_id": job_id, "data": tab_map[tab_key]()}
    finally:
        db.close()


# Function: db_delete_analysis
@app.delete("/api/db/analyses/{job_id}")
def db_delete_analysis(job_id: str):
    """Cascade-delete an analysis record and all child rows."""
    if not _DB_ENABLED:
        raise HTTPException(503, DATABASE_NOT_AVAILABLE_MESSAGE)
    db = SessionLocal()
    try:
        job = db.get(CAJob, job_id)
        if not job:
            raise HTTPException(404, ANALYSIS_NOT_FOUND_MESSAGE)
        db.delete(job)
        db.commit()
        return {"deleted": True, "job_id": job_id}
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(500, str(exc))
    finally:
        db.close()


# Function: db_stats
@app.get("/api/db/stats")
def db_stats():
    """Aggregate statistics across all persisted analyses."""
    if not _DB_ENABLED:
        raise HTTPException(503, DATABASE_NOT_AVAILABLE_MESSAGE)
    from sqlalchemy import func as sqlfunc
    db = SessionLocal()
    try:
        return {
            "total_analyses":     db.query(CAJob).filter(CAJob.job_type == "single").count(),
            "total_ai_analyses":  db.query(CAAiAnalysis).count(),
            "avg_health":         round(v, 1) if (v := db.query(sqlfunc.avg(CAHealth.health)).scalar()) else None,
            "avg_debt_months":    round(v, 1) if (v := db.query(sqlfunc.avg(CADebt.debt_months)).scalar()) else None,
            "avg_cloud_score":    round(v, 1) if (v := db.query(sqlfunc.avg(CACloud.total)).scalar()) else None,
            "total_lang_reports": db.query(sqlfunc.count(CALangReport.id)).scalar(),
            "total_oss_deps":     db.query(sqlfunc.count(CAOssDep.id)).scalar(),
        }
    finally:
        db.close()


if __name__ == "__main__":
    import os
    _src_dirs = ["api", "core", "analyzers", "metrics", "config", "reports", "services"]
    uvicorn.run(
        "api.server:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=8000,
        reload=True,
        reload_dirs=_src_dirs,
    )


