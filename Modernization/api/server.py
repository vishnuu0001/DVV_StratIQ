# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: api/server.py
# Date: 2025-08-15
# ---------------------------------------------------------------------------
"""
api/server.py
Modernization FastAPI backend.

Endpoints:
  GET  /api/health                              — liveness check
  GET  /api/auth/session                        — validate JWT and return session info

  POST /api/modernize/analyze                   — start deep analysis of a legacy folder
  POST /api/modernize/analyze-prompt            — generate code from a text prompt + screenshots
  GET  /api/modernize/jobs                      — list in-memory analysis jobs
  GET  /api/modernize/jobs/{job_id}             — get job status / report
  GET  /api/modernize/jobs/{job_id}/stream      — SSE real-time progress stream
  GET  /api/modernize/jobs/{job_id}/output      — download modernized code as ZIP
  DELETE /api/modernize/jobs/{job_id}           — cancel / remove a job

Serves React SPA (frontend/dist) on all non-/api paths.
Port: 8084
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import io
import json
import logging
import os
import queue
import re
import subprocess
import shutil
import tempfile
import time
import threading
import uuid
import zipfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import uvicorn
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.governance import (
    ProjectStore, compare_directories, comparison_html, comparison_pdf, generate_contracts, generate_plan,
    semantic_index, transformation_context, validate_contracts,
)

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODERNIZATION_APP = "MODERNIZATION"
_INSECURE_DEFAULT_AUTH_SECRET = "change-this-auth-token-secret-in-production"

app = FastAPI(
    title="Modernization API",
    description="Legacy code deep analysis and modernization service",
    version="1.0.0",
)

_PROJECT_STORE = ProjectStore()
_TOOLCHAIN_INSTALL_JOBS: Dict[str, dict] = {}
_TOOLCHAIN_PACKAGES = {
    "dotnet8": "Microsoft.DotNet.SDK.8",
    "dotnet10": "Microsoft.DotNet.SDK.10",
    "java17": "EclipseAdoptium.Temurin.17.JDK",
    "java21": "EclipseAdoptium.Temurin.21.JDK",
    "node": "OpenJS.NodeJS.LTS",
    "python312": "Python.Python.3.12",
    "go": "GoLang.Go",
    "php": "PHP.PHP.8.3",
    "ruby": "RubyInstallerTeam.RubyWithDevKit.3.3",
    "llvm": "LLVM.LLVM",
    "git": "Git.Git",
}


# Function: _actor
def _actor(request: Request) -> str:
    """Return the authenticated subject for audit metadata (or local operator)."""
    state_payload = getattr(request.state, "auth", None)
    if state_payload:
        return str(state_payload.get("sub") or "local-operator")
    token = _extract_bearer_token(request.headers.get("Authorization", ""))
    if token:
        try:
            return str(_decode_access_token(token).get("sub") or "local-operator")
        except (ValueError, RuntimeError):
            pass
    return "local-operator"


# Function: _require_admin
def _require_admin(request: Request, action: str = "perform this action") -> None:
    if (getattr(request.state, "auth", None) or {}).get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail=f"Administrator access is required to {action}",
        )


# Function: _cors_origins
def _cors_origins() -> list[str]:
    configured = (os.getenv("CORS_ORIGINS") or os.getenv("ALLOWED_ORIGINS") or "").strip()
    defaults = [
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:8090",
        "http://127.0.0.1:8090",
    ]
    values = [origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip()]
    origins = values or defaults
    return list(dict.fromkeys(origins))


# ─── Serve React SPA ─────────────────────────────────────────────────────────
_DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if _DIST_DIR.exists():
    _assets_dir = _DIST_DIR / "assets"
    if _assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(_assets_dir)), name="assets")

    # Function: _favicon
    @app.get("/favicon.ico", include_in_schema=False)
    async def _favicon():
        ico = _DIST_DIR / "favicon.ico"
        return FileResponse(str(ico)) if ico.exists() else HTMLResponse("", status_code=204)

    # Function: _spa_or_error
    @app.exception_handler(StarletteHTTPException)
    async def _spa_or_error(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 404 and not request.url.path.startswith("/api"):
            return FileResponse(str(_DIST_DIR / "index.html"))
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

    # Function: _index
    @app.get("/", include_in_schema=False)
    async def _index():
        return FileResponse(str(_DIST_DIR / "index.html"))


# ─── Auth helpers ─────────────────────────────────────────────────────────────
# Function: _auth_required
def _auth_required() -> bool:
    return os.getenv("AUTH_REQUIRED", "true").lower() in {"1", "true", "yes"}


# Function: _token_secret
def _token_secret() -> str:
    secret = (os.getenv("AUTH_TOKEN_SECRET") or "").strip()
    if secret and secret != _INSECURE_DEFAULT_AUTH_SECRET:
        return secret
    if _auth_required():
        allow_insecure = os.getenv("ALLOW_INSECURE_AUTH_SECRET", "false").lower() in {"1", "true", "yes"}
        if allow_insecure:
            logger.warning("Using insecure AUTH_TOKEN_SECRET because ALLOW_INSECURE_AUTH_SECRET=true")
            return _INSECURE_DEFAULT_AUTH_SECRET
        raise RuntimeError(
            "AUTH_TOKEN_SECRET must be set to a strong non-default value when AUTH_REQUIRED=true"
        )
    return _INSECURE_DEFAULT_AUTH_SECRET


# Function: _fs_root_path
def _fs_root_path() -> Path | None:
    configured = (os.getenv("MODERNIZATION_FS_ROOT") or "").strip()
    if not configured:
        return None
    p = Path(configured)
    return p.resolve() if p.exists() else None


# Function: _is_path_within
def _is_path_within(base: Path, target: Path) -> bool:
    try:
        return os.path.commonpath([str(base), str(target)]) == str(base)
    except ValueError:
        return False


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


# Function: _validate_token_with_portal
def _validate_token_with_portal(token: str) -> dict:
    """Validate against the Portal when independently deployed secrets drift.

    The token payload is trusted only after the Portal confirms the exact token
    and its database-backed session are active.
    """
    url = (os.getenv("PORTAL_AUTH_VALIDATE_URL") or "http://127.0.0.1:5001/api/auth/session").strip()
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            if response.status != 200:
                raise ValueError("Portal rejected the session")
            portal_session = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            error = json.loads(exc.read().decode("utf-8")).get("error")
        except (ValueError, AttributeError):
            error = None
        raise ValueError(error or "Portal rejected the session") from exc
    except (OSError, ValueError) as exc:
        raise ValueError(f"Portal session validation unavailable: {exc}") from exc

    parts = token.split(".")
    if len(parts) != 3 or parts[0] != "v1":
        raise ValueError("Malformed token")
    payload = json.loads(_b64url_decode(parts[1]).decode("utf-8"))
    if payload.get("typ") != "access" or int(payload.get("exp", 0)) <= int(time.time()):
        raise ValueError("Invalid or expired access token")
    portal_user = portal_session.get("user") or {}
    payload["sub"] = portal_user.get("username") or payload.get("sub")
    payload["role"] = portal_user.get("role") or payload.get("role")
    payload["portal_validated"] = True
    return payload


# Function: enforce_auth
@app.middleware("http")
async def enforce_auth(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)
    # IIS normally strips the public /api/mod prefix. Azure App Service and
    # some reverse-proxy configurations preserve it, so normalize both forms
    # before authentication and route matching.
    path = request.scope.get("path", request.url.path)
    if path == "/api/mod" or path.startswith("/api/mod/"):
        path = "/api" + path[len("/api/mod"):]
        request.scope["path"] = path
        request.scope["raw_path"] = path.encode("utf-8")
    public_paths = {"/api/health", "/docs", "/openapi.json", "/redoc"}
    if not _auth_required() or not path.startswith("/api") or path in public_paths:
        return await call_next(request)
    # SSE streams, file downloads, and fs/ls cannot send custom headers — accept token via ?token= query param
    auth_header = request.headers.get("Authorization", "")
    if not auth_header and (path.endswith("/stream") or path.endswith("/output") or path.endswith("/export") or path.startswith("/api/fs/")):
        token_qp = request.query_params.get("token", "")
        if token_qp:
            auth_header = f"Bearer {token_qp}"
    token = _extract_bearer_token(auth_header)
    if not token:
        return JSONResponse(status_code=401, content={"error": "Authentication required"})
    try:
        payload = _decode_access_token(token)
    except ValueError as local_error:
        try:
            payload = await asyncio.to_thread(_validate_token_with_portal, token)
        except ValueError as portal_error:
            logger.info("Token rejected locally (%s) and by Portal (%s)", local_error, portal_error)
            return JSONResponse(status_code=401, content={"error": str(portal_error)})
    role = payload.get("role")
    apps = payload.get("apps") or []
    if role != "admin" and MODERNIZATION_APP not in apps:
        return JSONResponse(status_code=403, content={"error": "Access denied for Modernization"})
    request.state.auth = payload
    return await call_next(request)


# ─── In-memory job store ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


_JOBS: Dict[str, dict] = {}
_JOB_QUEUES: Dict[str, queue.Queue] = {}

# Job state is snapshotted to disk so a backend restart doesn't silently
# orphan every in-flight or completed job — this box restarts the
# Modernization process on its own every few minutes under load (see
# Data/logs/watchdog_master.log), which previously rebuilt `_JOBS` empty and
# turned every existing job_id into a permanent 404, download and all.
_JOBS_DIR = Path(tempfile.gettempdir()) / "modernization_jobs"
_JOBS_DIR.mkdir(parents=True, exist_ok=True)
_JOB_TTL_HOURS = 7 * 24  # keep completed job state (and its downloadable output) for a week


# Function: _job_file
def _job_file(job_id: str) -> Path:
    # job_id is always server-generated (uuid4, or uuid4()[:8] for prompt
    # jobs) but sanitize defensively before touching the filesystem with it.
    safe_id = re.sub(r"[^\w-]", "_", job_id)
    return _JOBS_DIR / f"{safe_id}.json"


# Function: _persist_job
def _persist_job(job_id: str) -> None:
    """Snapshot job state to disk. `events` is excluded — it can grow to
    thousands of entries over a long job and is only used for the live
    progress log, not for resuming or downloading, so persisting it on every
    progress tick would be wasted I/O for no benefit."""
    job = _JOBS.get(job_id)
    if not job:
        return
    snapshot = {k: v for k, v in job.items() if k != "events"}
    try:
        _job_file(job_id).write_text(json.dumps(snapshot, default=str), encoding="utf-8")
    except OSError:
        logger.warning("Failed to persist job %s to disk", job_id, exc_info=True)


# Function: _sweep_old_jobs
def _sweep_old_jobs(max_age_hours: float = _JOB_TTL_HOURS) -> None:
    """Best-effort cleanup of job snapshots older than max_age_hours."""
    cutoff = time.time() - max_age_hours * 3600
    for f in _JOBS_DIR.glob("*.json"):
        try:
            if f.stat().st_mtime < cutoff:
                f.unlink()
        except OSError:
            continue


# Function: _load_persisted_jobs
def _load_persisted_jobs() -> None:
    """Restore job state from disk at process startup. A job still marked
    "running" belonged to a worker thread in the PREVIOUS process — that
    thread no longer exists, so it can never actually finish. Surface that
    plainly instead of leaving the UI's progress bar frozen forever with no
    explanation."""
    _sweep_old_jobs()
    for f in _JOBS_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        job_id = data.get("job_id") or f.stem
        if data.get("status") in {"running", "pending", "queued"}:
            data["status"] = "failed"
            data["phase"] = "interrupted"
            partial = data.get("output") or {}
            data["error"] = (
                f"Job was interrupted by a backend restart after generating {len(partial)} "
                "file(s) — partial output is available for download below." if partial else
                "Job was interrupted by a backend restart. Please start a new job."
            )
        data.setdefault("events", [])
        _JOBS[job_id] = data
        _persist_job(job_id)


_load_persisted_jobs()


# Function: _get_job
def _get_job(job_id: str) -> dict:
    job = _JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job


# Function: _job_response
def _job_response(job: dict) -> dict:
    """Return a safe job payload with persisted event history."""
    data = dict(job)
    data["events"] = list(job.get("events", []))
    return data

# ─── Language / tech label maps (used by /api/fs/detect) ──────────────────────
_LANG_LABELS: Dict[str, str] = {
    "csharp":           "C# (.NET)",
    "visualbasic":      "VB.NET",
    "aspnet-webforms":  "ASP.NET WebForms",
    "aspnet-razor":     "ASP.NET Razor",
    "java":             "Java",
    "python":           "Python",
    "javascript":       "JavaScript",
    "typescript":       "TypeScript",
    "php":              "PHP",
    "ruby":             "Ruby",
    "go":               "Go",
    "cobol":            "COBOL",
    "sql":              "SQL",
}

_TECH_LABELS: Dict[str, str] = {
    "asp_net_webforms": "ASP.NET WebForms",
    "asp_net_mvc":      "ASP.NET MVC",
    "asp_net_core":     "ASP.NET Core",
    "java_ee":          "Java EE",
    "spring":           "Spring / Spring Boot",
    "oracle_db":        "Oracle Database",
    "sql_server":       "SQL Server",
    "entity_framework": "Entity Framework",
    "ado_net_raw":      "ADO.NET (raw SQL)",
    "jquery":           "jQuery",
    "react":            "React",
    "angular":          "Angular",
    "hibernate":        "Hibernate / JPA",
    "winforms":         "Windows Forms",
    "wpf":              "WPF",
}


# Function: _fs_list_no_path
def _fs_list_no_path(fs_root) -> dict:
    import string
    if fs_root is not None:
        target = fs_root
        try:
            subdirs = sorted(
                [p for p in target.iterdir() if p.is_dir() and not p.name.startswith(".")],
                key=lambda p: p.name.lower(),
            )
        except PermissionError:
            raise HTTPException(status_code=403, detail="Permission denied")
        return {
            "current": str(target),
            "parent": None,
            "dirs": [{"name": p.name, "path": str(p), "is_drive": False} for p in subdirs],
        }
    if os.name == "nt":
        drives = []
        for letter in string.ascii_uppercase:
            d = Path(f"{letter}:\\")
            if d.exists():
                drives.append({"name": str(d), "path": str(d), "is_drive": True})
        return {"current": "", "parent": None, "dirs": drives}
    root = Path("/")
    dirs = sorted(
        [{"name": p.name, "path": str(p), "is_drive": False}
         for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")],
        key=lambda x: x["name"].lower(),
    )
    return {"current": "/", "parent": None, "dirs": dirs}

# ─── Core API endpoints ───────────────────────────────────────────────────────

# Function: fs_list
@app.get("/api/fs/ls")
async def fs_list(path: Optional[str] = None):
    """List subdirectories at *path*. Optionally restricted by MODERNIZATION_FS_ROOT."""
    fs_root = _fs_root_path()

    if not path:
        return _fs_list_no_path(fs_root)

    target = Path(path).resolve()
    if fs_root is not None and not _is_path_within(fs_root, target):
        raise HTTPException(status_code=403, detail="Path outside allowed root")
    if not target.exists() or not target.is_dir():
        raise HTTPException(status_code=404, detail=f"Directory not found: {path}")

    try:
        subdirs = sorted(
            [p for p in target.iterdir() if p.is_dir() and not p.name.startswith(".")],
            key=lambda p: p.name.lower(),
        )
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")

    # Determine parent
    parent = str(target.parent) if target.parent != target else None
    if fs_root is not None and parent and not _is_path_within(fs_root, Path(parent)):
        parent = None

    return {
        "current": str(target),
        "parent": parent,
        "dirs": [{"name": p.name, "path": str(p), "is_drive": False} for p in subdirs],
    }


# ─── Upload-from-browser folder intake ─────────────────────────────────────
# The FolderBrowserModal ("Browse") only ever lists directories on the SERVER
# that runs this backend — a browser has no way to hand server-side code a
# path on the visitor's own machine. This endpoint is the other half: the
# frontend uses a native <input type="file" webkitdirectory> picker to read
# the user's chosen folder client-side, uploads every file (each UploadFile's
# `filename` carries its folder-relative path, e.g. "MyProject/src/Foo.cs" —
# see FormData.append(name, blob, file.webkitRelativePath) in the frontend),
# and this endpoint materializes them into a server-side temp directory. That
# temp path is then used exactly like a browsed path everywhere downstream
# (fs/detect, modernize/analyze) — zero changes needed to the analyze/
# modernize pipeline, which only ever consumed a folder_path string anyway.
_UPLOAD_SKIP_DIRS = {".git", ".vs", ".vscode", "bin", "obj", "node_modules",
                     "__pycache__", ".venv", "venv", "env", "dist", "build",
                     "target", "out", "packages", ".nuget", "TestResults",
                     ".gradle", ".idea", "coverage", ".next", ".nuxt",
                     ".mvn", ".svn", ".hg"}
_UPLOAD_MAX_FILES = 4000
_UPLOAD_MAX_BYTES = 200 * 1024 * 1024  # 200 MB — matches web.config maxAllowedContentLength
_UPLOAD_ROOT       = Path(tempfile.gettempdir()) / "modernization_uploads"


# Function: _sweep_old_uploads
def _sweep_old_uploads(max_age_hours: float = 6.0) -> None:
    """Best-effort cleanup of upload temp dirs older than max_age_hours."""
    if not _UPLOAD_ROOT.exists():
        return
    cutoff = time.time() - max_age_hours * 3600
    for child in _UPLOAD_ROOT.iterdir():
        try:
            if child.is_dir() and child.stat().st_mtime < cutoff:
                shutil.rmtree(child, ignore_errors=True)
        except OSError:
            continue


# Function: upload_folder
@app.post("/api/fs/upload-folder")
async def upload_folder(files: List[UploadFile] = File(...)):
    """Materialize a browser-uploaded folder into a server-side temp dir and
    return its path, for use exactly like a browsed folder_path."""
    if not files:
        raise HTTPException(status_code=400, detail="No files received")
    if len(files) > _UPLOAD_MAX_FILES:
        raise HTTPException(
            status_code=413,
            detail=f"Too many files ({len(files)}); limit is {_UPLOAD_MAX_FILES}. "
                   "Exclude build output / dependency folders and try again.",
        )

    _sweep_old_uploads()
    _UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    dest_root = Path(tempfile.mkdtemp(dir=str(_UPLOAD_ROOT), prefix="upload_")).resolve()

    total_bytes = 0
    written = 0
    try:
        for uf in files:
            raw_name = (uf.filename or "").replace("\\", "/")
            parts = [p for p in raw_name.split("/") if p not in ("", ".", "..")]
            if not parts or any(part in _UPLOAD_SKIP_DIRS for part in parts[:-1]):
                await uf.read()  # drain so the multipart stream stays consistent
                continue

            dest_path = dest_root.joinpath(*parts)
            if not _is_path_within(dest_root, dest_path.resolve()):
                continue  # defense in depth against path traversal

            data = await uf.read()
            total_bytes += len(data)
            if total_bytes > _UPLOAD_MAX_BYTES:
                shutil.rmtree(dest_root, ignore_errors=True)
                raise HTTPException(
                    status_code=413,
                    detail=f"Upload too large (limit {_UPLOAD_MAX_BYTES // (1024 * 1024)} MB). "
                           "Exclude build output / dependency folders and try again.",
                )

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_bytes(data)
            written += 1
    except HTTPException:
        raise
    except Exception as exc:
        shutil.rmtree(dest_root, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}")

    if written == 0:
        shutil.rmtree(dest_root, ignore_errors=True)
        raise HTTPException(status_code=400, detail="No usable files in upload after filtering")

    logger.info("Uploaded folder: %d files, %d bytes -> %s", written, total_bytes, dest_root)
    return {"path": str(dest_root), "file_count": written, "bytes": total_bytes}


# Function: health
@app.get("/api/health")
async def health():
    return {
        "status": "ok", "module": "Modernization", "port": 8084,
        "api_version": "2.0", "capabilities": ["governed_projects", "target_stack_catalog", "snapshot_governance", "toolchain_readiness"],
    }


# ── Governed, Git-independent projects ─────────────────────────────────────
# Function: _project_or_404
def _project_or_404(project_id: str) -> dict:
    try:
        return _PROJECT_STORE.get_project(project_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Modernization project not found")


# Function: _snapshot_or_404
def _snapshot_or_404(project_id: str, snapshot_id: str) -> dict:
    try:
        return _PROJECT_STORE.get_snapshot(project_id, snapshot_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Snapshot not found")


# Function: _latest
def _latest(project: dict, kind: str) -> dict | None:
    return next((item for item in project.get("snapshots", []) if item["kind"] == kind), None)


# Function: _artifact
def _artifact(snapshot: dict, filename: str = "artifact.json") -> dict:
    path = Path(snapshot["path"]) / filename
    if not path.exists():
        raise HTTPException(status_code=409, detail=f"Snapshot has no {filename}")
    return json.loads(path.read_text(encoding="utf-8"))


# Function: list_projects
@app.get("/api/projects")
async def list_projects():
    return {"projects": _PROJECT_STORE.list_projects()}


# Function: list_project_jobs
@app.get("/api/projects/{project_id}/jobs")
async def list_project_jobs(project_id: str):
    _project_or_404(project_id)
    jobs = [
        {"job_id": job["job_id"], "project_id": project_id, "status": job.get("status"),
         "phase": job.get("phase"), "progress": job.get("progress", 0), "error": job.get("error"),
         "created_at": job.get("created_at"), "updated_at": job.get("updated_at"),
         "target_stack": job.get("target_stack")}
        for job in _JOBS.values() if job.get("project_id") == project_id
    ]
    jobs.sort(key=lambda item: item.get("created_at") or "", reverse=True)
    return {"jobs": jobs}


# Function: create_project
@app.post("/api/projects")
async def create_project(request: Request):
    body = await request.json()
    configuration = body.get("configuration") or {}
    origin_mode = str(configuration.get("origin_mode") or body.get("origin_mode") or "existing_source")
    try:
        if origin_mode == "prompt":
            project = _PROJECT_STORE.create_prompt_project(
                str(body.get("name") or "New application"), str(body.get("project_prompt") or ""),
                _actor(request), configuration, max(1, int(body.get("retention_days", 365))),
            )
            source = _latest(project, "source")
            index = semantic_index(Path(source["path"]))
            analysis = {
                "summary": {
                    "project_origin": "Greenfield application generated from a governed prompt",
                    "business_context": configuration.get("description") or "Not provided",
                    "current_architecture": "No existing architecture; the approved project brief is the baseline.",
                    "architecture_constraint": configuration.get("architecture") or "To be defined during plan review",
                    "deployment_constraint": configuration.get("deployment") or "Not specified",
                },
                "project_type": "greenfield", "source": "prompt",
                "project_prompt": str(body.get("project_prompt") or ""),
                "tech_stack": ["Greenfield – no legacy source technology stack"],
                "requested_target": {
                    "name": configuration.get("target_stack_name"), "language": configuration.get("language"),
                    "framework": configuration.get("framework"), "runtime": configuration.get("runtime"),
                    "frontend": configuration.get("frontend"), "database": configuration.get("database"),
                    "architecture": configuration.get("architecture"), "deployment": configuration.get("deployment"),
                },
            }
            _PROJECT_STORE.add_json_snapshot(project["id"], "analysis", {"analysis": analysis, "semantic_index": index},
                _actor(request), {"target_stack": configuration.get("engine_target"),
                "custom_stack_desc": configuration.get("custom_stack_desc", ""), "parent_source": source["id"]}, source["id"])
            _PROJECT_STORE.set_status(project["id"], "Analyzed")
            return _PROJECT_STORE.get_project(project["id"])
        source = Path(str(body.get("source_path") or "")).resolve()
        return _PROJECT_STORE.create_project(str(body.get("name") or source.name or "Modernization project"), source,
            _actor(request), configuration, max(1, int(body.get("retention_days", 365))))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# Function: get_project
@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    return _project_or_404(project_id)


# Function: _delete_project_action
def _delete_project_action(project_id: str, request: Request):
    _require_admin(request, "delete governed projects")
    _project_or_404(project_id)
    active = [
        job.get("job_id") for job in _JOBS.values()
        if job.get("project_id") == project_id
        and job.get("status") not in ("completed", "validation_failed", "failed")
    ]
    if active:
        raise HTTPException(
            status_code=409,
            detail=f"Project has an active job and cannot be deleted: {active[0]}",
        )
    result = _PROJECT_STORE.delete_project(project_id, _actor(request))
    for job_id in [
        key for key, job in _JOBS.items() if job.get("project_id") == project_id
    ]:
        _JOBS.pop(job_id, None)
        _JOB_QUEUES.pop(job_id, None)
    return result


# Function: delete_project
@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str, request: Request):
    return _delete_project_action(project_id, request)


# Function: delete_project_via_action
@app.post("/api/projects/{project_id}/delete")
async def delete_project_via_action(project_id: str, request: Request):
    """Proxy-compatible destructive action for hosts that restrict DELETE."""
    return _delete_project_action(project_id, request)


# Function: analyze_governed_project
@app.post("/api/projects/{project_id}/analyze")
async def analyze_governed_project(project_id: str, request: Request):
    project = _project_or_404(project_id)
    source = _latest(project, "source")
    if not source:
        raise HTTPException(status_code=409, detail="Project has no source snapshot")
    body = await request.json()
    target_stack = str(body.get("target_stack") or "dotnet8_blazor")
    custom_stack_desc = str(body.get("custom_stack_desc") or project["configuration"].get("custom_stack_desc") or "")
    from services.analyzer import analyze_project
    analysis = await asyncio.to_thread(analyze_project, source["path"], None, target_stack)
    index = await asyncio.to_thread(semantic_index, Path(source["path"]))
    snapshot = _PROJECT_STORE.add_json_snapshot(
        project_id, "analysis", {"analysis": analysis, "semantic_index": index}, _actor(request),
        {"target_stack": target_stack, "custom_stack_desc": custom_stack_desc, "parent_source": source["id"]}, source["id"],
    )
    _PROJECT_STORE.set_status(project_id, "Analyzed")
    return {"snapshot": snapshot, "analysis": analysis, "semantic_index": index}


# Function: create_modernization_plan
@app.post("/api/projects/{project_id}/plans")
async def create_modernization_plan(project_id: str, request: Request):
    project = _project_or_404(project_id); analysis_snapshot = _latest(project, "analysis")
    if not analysis_snapshot:
        raise HTTPException(status_code=409, detail="Analyze the project before generating a plan")
    body = await request.json(); artifact = _artifact(analysis_snapshot)
    target = str(body.get("target_stack") or analysis_snapshot["metadata"].get("target_stack") or "dotnet8_blazor")
    custom_desc = str(body.get("custom_stack_desc") or project["configuration"].get("custom_stack_desc") or analysis_snapshot["metadata"].get("custom_stack_desc") or "")
    plan_analysis = dict(artifact["analysis"])
    if project["configuration"].get("origin_mode") == "prompt":
        plan_analysis["project_prompt"] = str(
            project["configuration"].get("project_prompt") or ""
        )
    plan_analysis["requested_target"] = {
        "name": project["configuration"].get("target_stack_name"),
        "language": project["configuration"].get("language"),
        "framework": project["configuration"].get("framework"),
        "runtime": project["configuration"].get("runtime"),
        "frontend": project["configuration"].get("frontend"),
        "database": project["configuration"].get("database"),
        "architecture": project["configuration"].get("architecture"),
        "deployment": project["configuration"].get("deployment"),
    }
    if project["configuration"].get("origin_mode") == "prompt":
        plan_analysis["project_type"] = "greenfield"
        plan_analysis["source"] = "prompt"
        plan_analysis["summary"] = {
            "project_origin": "Greenfield application generated from a governed prompt",
            "business_context": project["configuration"].get("description") or "Not provided",
            "current_architecture": "No existing architecture; the approved project brief is the baseline.",
            "architecture_constraint": project["configuration"].get("architecture") or "To be defined during plan review",
            "deployment_constraint": project["configuration"].get("deployment") or "Not specified",
        }
        plan_analysis["tech_stack"] = ["Greenfield – no legacy source technology stack"]
    plan = generate_plan(plan_analysis, artifact["semantic_index"], custom_desc if target == "custom" and custom_desc else target, body.get("excluded_modules"))
    configured_architecture = {
        "name": project["configuration"].get("target_stack_name"),
        "language": project["configuration"].get("language"),
        "framework": project["configuration"].get("framework"),
        "runtime": project["configuration"].get("runtime"),
        "frontend": project["configuration"].get("frontend"),
        "database": project["configuration"].get("database"),
        "style": project["configuration"].get("architecture"),
        "deployment": project["configuration"].get("deployment"),
    }
    plan["target_architecture"] = {
        **(plan.get("target_architecture") or {}),
        **{
            key: value for key, value in configured_architecture.items()
            if value not in (None, "", [], {})
        },
    }
    effective_target = custom_desc if target == "custom" and custom_desc else target
    snapshot = _PROJECT_STORE.add_json_snapshot(project_id, "plans", plan, _actor(request),
                                                 {"target_stack": target, "custom_stack_desc": custom_desc}, analysis_snapshot["id"], "plan.json")
    contracts = generate_contracts(artifact["semantic_index"], effective_target)
    contract_snapshot = _PROJECT_STORE.add_json_snapshot(project_id, "contracts", contracts, _actor(request),
                                                          {"target_stack": target, "locked_for_plan": snapshot["id"]}, snapshot["id"], "contracts.json")
    _PROJECT_STORE.set_status(project_id, "Plan Generated")
    return {"plan_snapshot": snapshot, "plan": plan, "contract_snapshot": contract_snapshot,
            "contracts": contracts, "contract_validation": validate_contracts(contracts)}


# Function: revise_modernization_plan
@app.patch("/api/projects/{project_id}/plans/{snapshot_id}")
async def revise_modernization_plan(project_id: str, snapshot_id: str, request: Request):
    _project_or_404(project_id)
    try:
        revised = _PROJECT_STORE.update_plan(project_id, snapshot_id, await request.json(), _actor(request))
        _PROJECT_STORE.set_status(project_id, "Plan Generated")
        return revised
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


# Function: decide_snapshot
@app.post("/api/projects/{project_id}/snapshots/{snapshot_id}/decision")
async def decide_snapshot(project_id: str, snapshot_id: str, request: Request):
    body = await request.json()
    try:
        decision = str(body.get("decision"))
        snapshot = _snapshot_or_404(project_id, snapshot_id)
        if snapshot["kind"] == "plans" and decision == "approved":
            plan = _artifact(snapshot, "plan.json")
            if not plan.get("ready_for_approval"):
                unresolved = plan.get("unresolved_requirements") or ["Plan completeness has not been established"]
                raise HTTPException(
                    status_code=409,
                    detail="Plan has unresolved requirements: " + "; ".join(map(str, unresolved[:8])),
                )
        return _PROJECT_STORE.decide(project_id, snapshot_id, decision, _actor(request))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


# Function: restore_snapshot
@app.post("/api/projects/{project_id}/snapshots/{snapshot_id}/restore")
async def restore_snapshot(project_id: str, snapshot_id: str, request: Request):
    _snapshot_or_404(project_id, snapshot_id)
    return _PROJECT_STORE.restore(project_id, snapshot_id, _actor(request))


# Function: get_snapshot_artifact
@app.get("/api/projects/{project_id}/snapshots/{snapshot_id}/artifact")
async def get_snapshot_artifact(project_id: str, snapshot_id: str):
    """Return structured content used by the governed review workspace."""
    snapshot = _snapshot_or_404(project_id, snapshot_id)
    filenames = {
        "analysis": "artifact.json", "plans": "plan.json", "contracts": "contracts.json",
        "validation": "artifact.json", "exports": "manifest.json",
    }
    filename = filenames.get(snapshot["kind"])
    if not filename:
        raise HTTPException(status_code=400, detail="This snapshot contains files, not a structured artifact")
    return {"snapshot": snapshot, "artifact": _artifact(snapshot, filename)}


# Function: review_snapshot_file
@app.post("/api/projects/{project_id}/snapshots/{snapshot_id}/files/review")
async def review_snapshot_file(project_id: str, snapshot_id: str, request: Request):
    _snapshot_or_404(project_id, snapshot_id); body = await request.json()
    try:
        return _PROJECT_STORE.review_file(snapshot_id, str(body.get("file_path") or ""),
                                          str(body.get("decision") or "pending"), str(body.get("comment") or ""), _actor(request))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# Function: compare_project_snapshots
@app.get("/api/projects/{project_id}/compare")
async def compare_project_snapshots(project_id: str, left_snapshot_id: str, right_snapshot_id: str,
                                    search: str = "", change_type: str = ""):
    left = _snapshot_or_404(project_id, left_snapshot_id); right = _snapshot_or_404(project_id, right_snapshot_id)
    return await asyncio.to_thread(compare_directories, Path(left["path"]), Path(right["path"]), search, change_type)


# Function: export_project_comparison
@app.get("/api/projects/{project_id}/compare/export")
async def export_project_comparison(project_id: str, left_snapshot_id: str, right_snapshot_id: str,
                                    format: str = "html"):
    left = _snapshot_or_404(project_id, left_snapshot_id); right = _snapshot_or_404(project_id, right_snapshot_id)
    comparison = await asyncio.to_thread(compare_directories, Path(left["path"]), Path(right["path"]))
    if format.lower() == "pdf":
        data, media, suffix = comparison_pdf(comparison), "application/pdf", "pdf"
    elif format.lower() == "html":
        data, media, suffix = comparison_html(comparison).encode(), "text/html", "html"
    else:
        raise HTTPException(status_code=400, detail="format must be html or pdf")
    return StreamingResponse(io.BytesIO(data), media_type=media,
                             headers={"Content-Disposition": f'attachment; filename="comparison.{suffix}"'})


# Function: transform_governed_project
@app.post("/api/projects/{project_id}/transform")
async def transform_governed_project(project_id: str, request: Request):
    project = _project_or_404(project_id); plan_snapshot = _latest(project, "plans"); source = _latest(project, "source")
    if not plan_snapshot or plan_snapshot.get("approval_decision") != "approved":
        raise HTTPException(status_code=409, detail="An approved modernization plan is required")
    body = await request.json(); plan = _artifact(plan_snapshot, "plan.json")
    configured_target = project["configuration"].get("engine_target") or project["configuration"].get("target_stack")
    target_stack = str(body.get("target_stack") or configured_target or (plan.get("target_technologies") or ["dotnet8_blazor"])[0])
    custom_stack_desc = str(body.get("custom_stack_desc") or project["configuration"].get("custom_stack_desc") or "")
    from services.build_runner import toolchain_compatibility_error
    config = project.get("configuration") or {}
    compatibility_error = toolchain_compatibility_error(" ".join(str(value or "") for value in (
        custom_stack_desc, config.get("target_stack_name"), config.get("language"),
        config.get("framework"), config.get("runtime"), config.get("dependency_versions"),
    )))
    if compatibility_error:
        raise HTTPException(status_code=409, detail=compatibility_error)
    job_id = str(uuid.uuid4()); now = datetime.now(timezone.utc).isoformat()
    _JOBS[job_id] = {"job_id": job_id, "project_id": project_id, "actor": _actor(request), "folder_path": source["path"],
        "target_stack": target_stack, "custom_stack_desc": custom_stack_desc, "output_mode": "project", "status": "running", "progress": 0,
        "phase": "starting", "created_at": now, "updated_at": now, "analysis": None, "output": None,
        "validation": None, "error": None, "events": [], "plan_snapshot_id": plan_snapshot["id"]}
    _persist_job(job_id); _JOB_QUEUES[job_id] = queue.Queue(); _PROJECT_STORE.set_status(project_id, "Transformation Running")
    contract_snapshot = _latest(project, "contracts")
    contract_text = json.dumps(_artifact(contract_snapshot, "contracts.json"), indent=2) if contract_snapshot else "{}"
    guide = "LOCKED CANONICAL CONTRACTS (all generated files must conform):\n" + contract_text
    correction_snapshot = _latest(project, "overrides")
    if correction_snapshot:
        correction = _artifact(correction_snapshot, "review.json")
        guide += "\n\nMANDATORY REVIEW CORRECTIONS FOR THIS RUN:\n" + str(correction.get("feedback") or "")
    if project["configuration"].get("origin_mode") == "prompt":
        user_prompt = str(project["configuration"].get("project_prompt") or "")
        threading.Thread(target=_prompt_worker, args=(job_id, user_prompt, target_stack, [], custom_stack_desc, guide, "project"), daemon=True).start()
    else:
        threading.Thread(target=_analysis_worker, args=(job_id, source["path"], target_stack, custom_stack_desc, guide, "project"), daemon=True).start()
    return {"job_id": job_id, "project_id": project_id, "status": "running"}


# Function: get_transformation_context
@app.post("/api/projects/{project_id}/context")
async def get_transformation_context(project_id: str, request: Request):
    project = _project_or_404(project_id); analysis = _latest(project, "analysis"); contracts = _latest(project, "contracts")
    if not analysis or not contracts:
        raise HTTPException(status_code=409, detail="Analysis and canonical contracts are required")
    body = await request.json()
    return transformation_context(_artifact(analysis)["semantic_index"], str(body.get("current_file") or ""),
                                  _artifact(contracts, "contracts.json"), body.get("architecture_decisions"))


# Function: validate_project_contracts
@app.get("/api/projects/{project_id}/contracts/validate")
async def validate_project_contracts(project_id: str):
    contracts = _latest(_project_or_404(project_id), "contracts")
    if not contracts: raise HTTPException(status_code=404, detail="Canonical contracts not generated")
    return validate_contracts(_artifact(contracts, "contracts.json"))


# Function: purge_project_snapshots
@app.post("/api/projects/{project_id}/retention/purge")
async def purge_project_snapshots(project_id: str):
    _project_or_404(project_id)
    return _PROJECT_STORE.purge(project_id)


# Function: review_generated_output
@app.post("/api/projects/{project_id}/reviews")
async def review_generated_output(project_id: str, request: Request):
    project = _project_or_404(project_id); body = await request.json()
    decision = str(body.get("decision") or "").strip()
    if decision not in {"corrections_requested", "rejected"}:
        raise HTTPException(status_code=400, detail="decision must be corrections_requested or rejected")
    feedback = str(body.get("feedback") or "").strip()
    if not feedback:
        raise HTTPException(status_code=400, detail="Review feedback is required")
    output_id = str(body.get("output_snapshot_id") or "")
    output = _snapshot_or_404(project_id, output_id) if output_id else _latest(project, "outputs")
    if not output or output["kind"] != "outputs":
        raise HTTPException(status_code=409, detail="A generated output snapshot is required")
    review = {"decision": decision, "feedback": feedback, "output_snapshot_id": output["id"],
              "file_feedback": body.get("file_feedback") or [], "reviewed_at": datetime.now(timezone.utc).isoformat(),
              "reviewed_by": _actor(request)}
    snapshot = _PROJECT_STORE.add_json_snapshot(project_id, "overrides", review, _actor(request),
        {"output_snapshot_id": output["id"], "decision": decision}, output["id"], "review.json")
    _PROJECT_STORE.decide(project_id, output["id"], "rejected", _actor(request))
    if decision == "corrections_requested":
        _PROJECT_STORE.set_status(project_id, "Plan Approved")
    return {"review_snapshot": snapshot, "project": _PROJECT_STORE.get_project(project_id)}


# Function: approve_release
def _security_findings(root: Path) -> list[str]:
    findings = []
    patterns = [
        (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "Embedded private key"),
        (re.compile(r"(?i)(?:client_secret|api_key|access_key)\s*[:=]\s*[\"'][A-Za-z0-9_+/=-]{12,}[\"']"), "Embedded credential"),
        (re.compile(r"(?i)password\s*[:=]\s*[\"'](?!change|replace|example|\$\{|<)[^\"']{8,}[\"']"), "Hard-coded password"),
    ]
    for path in root.rglob("*"):
        if not path.is_file() or path.stat().st_size > 2 * 1024 * 1024: continue
        try: content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError: continue
        for pattern, label in patterns:
            if pattern.search(content): findings.append(f"{label}: {path.relative_to(root).as_posix()}")
    return findings


# Function: _evaluate_release_gate
def _evaluate_release_gate(project: dict, output: dict, validation_snapshot: dict) -> dict:
    validation = _artifact(validation_snapshot)
    blockers, warnings = [], []
    if validation.get("production_ready") is False:
        blockers.append("Generator production-readiness acceptance failed")
    if int(validation.get("checked", 0)) <= 0: blockers.append("No generated files were validated")
    if int(validation.get("strict_checked", 0)) <= 0: blockers.append("No compiler or parser validation was completed")
    if int(validation.get("failed", 0)) > 0: blockers.append(f"{validation['failed']} file validation check(s) failed")
    build = validation.get("build")
    configuration = project.get("configuration", {})
    build_required = configuration.get("origin_mode") != "single_file"
    if build_required and not build: blockers.append("Required whole-project strict validation did not run")
    elif build and build.get("checker") in {"skipped", "unsupported-build-route"}:
        blockers.append("Required whole-project strict validation was not available")
    elif build and not build.get("passed"): blockers.append(f"Whole-project build failed ({build.get('checker')})")
    contracts = _latest(project, "contracts")
    if not contracts: blockers.append("Canonical contracts are missing")
    else:
        contract_result = validate_contracts(_artifact(contracts, "contracts.json"))
        if not contract_result.get("valid"): blockers.extend(contract_result.get("errors") or ["Canonical contract validation failed"])
        warnings.extend(contract_result.get("warnings") or [])
    security = _security_findings(Path(output["path"]))
    blockers.extend(security)
    if any(path.name == "_GENERATION_AUDIT.md" for path in Path(output["path"]).rglob("_GENERATION_AUDIT.md")):
        blockers.append("Generation audit reports unresolved issues")
    if not any("test" in path.name.lower() or "spec" in path.name.lower() for path in Path(output["path"]).rglob("*")):
        warnings.append("No generated automated tests were detected")
    return {"passed": not blockers, "blockers": blockers, "warnings": warnings,
            "checks": {"file_validation": int(validation.get("failed", 0)) == 0,
                       "whole_project_build": bool(build and build.get("passed")),
                       "canonical_contracts": bool(contracts), "security_scan": not security}}


# Function: get_release_quality_gate
@app.get("/api/projects/{project_id}/quality-gate")
async def get_release_quality_gate(project_id: str, output_snapshot_id: str = ""):
    project = _project_or_404(project_id)
    output = _snapshot_or_404(project_id, output_snapshot_id) if output_snapshot_id else _latest(project, "outputs")
    if not output: raise HTTPException(status_code=404, detail="Generated output not found")
    validation = next((s for s in project["snapshots"] if s["kind"] == "validation" and s["metadata"].get("output_snapshot_id") == output["id"]), None)
    if not validation: raise HTTPException(status_code=409, detail="Output has no validation results")
    return _evaluate_release_gate(project, output, validation)


# Function: approve_release
@app.post("/api/projects/{project_id}/releases")
async def approve_release(project_id: str, request: Request):
    project = _project_or_404(project_id); body = await request.json()
    output_id = str(body.get("output_snapshot_id") or "")
    output = _snapshot_or_404(project_id, output_id) if output_id else _latest(project, "outputs")
    if not output or output["kind"] != "outputs":
        raise HTTPException(status_code=409, detail="A generated output snapshot is required")
    validation = next((s for s in project["snapshots"] if s["kind"] == "validation" and
                       s["metadata"].get("output_snapshot_id") == output["id"]), None)
    if not validation:
        raise HTTPException(status_code=409, detail="Output has no validation results")
    quality_gate = _evaluate_release_gate(project, output, validation)
    if not quality_gate["passed"]:
        raise HTTPException(status_code=409, detail={"message": "Release quality gate failed", **quality_gate})
    release = _PROJECT_STORE.add_directory_snapshot(project_id, "approved", Path(output["path"]), _actor(request),
        {"output_snapshot_id": output["id"], "validation_snapshot_id": validation["id"],
         "approval_comment": str(body.get("comment") or "")}, output["id"])
    release = _PROJECT_STORE.decide(project_id, release["id"], "approved", _actor(request))
    _PROJECT_STORE.set_status(project_id, "Approved")
    return release


# Function: export_release
@app.get("/api/projects/{project_id}/releases/{snapshot_id}/export")
async def export_release(project_id: str, snapshot_id: str, request: Request):
    release = _snapshot_or_404(project_id, snapshot_id)
    if release["kind"] != "approved" or not release["locked"]:
        raise HTTPException(status_code=409, detail="Only locked approved releases can be exported")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as archive:
        root = Path(release["path"])
        for path in root.rglob("*"):
            if path.is_file(): archive.write(path, path.relative_to(root).as_posix())
        manifest = {"project_id": project_id, "release_snapshot_id": snapshot_id, "checksum": release["checksum"],
                    "exported_at": datetime.now(timezone.utc).isoformat(), "exported_by": _actor(request),
                    "metadata": release["metadata"]}
        archive.writestr("modernization-release-manifest.json", json.dumps(manifest, indent=2))
    buf.seek(0)
    _PROJECT_STORE.add_json_snapshot(project_id, "exports", manifest, _actor(request),
                                     {"release_snapshot_id": snapshot_id}, snapshot_id, "manifest.json")
    _PROJECT_STORE.set_status(project_id, "Exported")
    return StreamingResponse(buf, media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{project_id}-{snapshot_id}.zip"'})


# Function: llm_status
@app.get("/api/llm/status")
async def llm_status():
    """Check Ollama availability and return the best available code model."""
    try:
        from services.llm import check_status
        return check_status()
    except Exception as exc:
        return {"available": False, "error": str(exc), "recommended": "qwen2.5-coder:3b"}


_ADDITIONAL_STACK_PRESETS = [
    ("c_native", "C17 native application", "Native and systems", "C", "C17", "CLI / service", "Files / database"),
    ("cpp_native", "C++20 native application", "Native and systems", "C++", "C++20", "CLI / service", "Files / database"),
    ("dotnet_react", ".NET 8 Web API + React + PostgreSQL", "Microsoft", "C#", ".NET 8 Web API", "React + TypeScript", "PostgreSQL 16"),
    ("dotnet_angular", ".NET 8 Web API + Angular + SQL Server", "Microsoft", "C#", ".NET 8 Web API", "Angular 18", "SQL Server 2022"),
    ("dotnet_microservices", ".NET 8 Microservices + Kubernetes", "Microsoft", "C#", ".NET 8 + Aspire", "React", "PostgreSQL"),
    ("node_nest_react", "NestJS + React + PostgreSQL", "JavaScript", "TypeScript", "NestJS", "React + TypeScript", "PostgreSQL"),
    ("node_express_react", "Node.js Express + React + MongoDB", "JavaScript", "TypeScript", "Express.js", "React + TypeScript", "MongoDB"),
    ("nextjs_fullstack", "Next.js Full Stack + PostgreSQL", "JavaScript", "TypeScript", "Next.js API routes", "Next.js App Router", "PostgreSQL + Prisma"),
    ("java_quarkus", "Java 21 Quarkus + PostgreSQL", "Java", "Java", "Quarkus", "REST API", "PostgreSQL"),
    ("java_micronaut", "Java 21 Micronaut + PostgreSQL", "Java", "Java", "Micronaut", "REST API", "PostgreSQL"),
    ("kotlin_spring", "Kotlin + Spring Boot + PostgreSQL", "JVM", "Kotlin", "Spring Boot", "REST API", "PostgreSQL"),
    ("python_fastapi_react", "FastAPI + React + PostgreSQL", "Python", "Python", "FastAPI", "React + TypeScript", "PostgreSQL"),
    ("python_django_react", "Django DRF + React + PostgreSQL", "Python", "Python", "Django REST Framework", "React + TypeScript", "PostgreSQL"),
    ("go_gin_react", "Go Gin + React + PostgreSQL", "Cloud native", "Go", "Gin", "React + TypeScript", "PostgreSQL"),
    ("go_fiber_vue", "Go Fiber + Vue + PostgreSQL", "Cloud native", "Go", "Fiber", "Vue 3 + TypeScript", "PostgreSQL"),
    ("rust_axum_react", "Rust Axum + React + PostgreSQL", "Cloud native", "Rust", "Axum", "React + TypeScript", "PostgreSQL"),
    ("php_laravel_vue", "Laravel + Vue + MySQL", "PHP", "PHP", "Laravel", "Vue 3", "MySQL 8"),
    ("ruby_rails_react", "Ruby on Rails + React + PostgreSQL", "Ruby", "Ruby", "Rails", "React", "PostgreSQL"),
    ("flutter_dotnet", "Flutter + .NET 8 API", "Mobile", "Dart / C#", ".NET 8 Web API", "Flutter", "PostgreSQL"),
    ("react_native_node", "React Native + NestJS", "Mobile", "TypeScript", "NestJS", "React Native", "PostgreSQL"),
    ("cobol_java", "COBOL to Java Spring Boot", "Mainframe", "Java", "Spring Boot", "REST API", "PostgreSQL"),
    ("cobol_dotnet", "COBOL to .NET 8", "Mainframe", "C#", ".NET 8", "Blazor", "SQL Server"),
    ("javascript_node", "JavaScript + Node.js", "JavaScript / TypeScript", "JavaScript", "Node.js", "CLI / REST API", "Optional"),
    ("swift_vapor", "Swift + Vapor", "Native and systems", "Swift", "Vapor", "REST API", "PostgreSQL"),
    ("kotlin_ktor", "Kotlin + Ktor", "JVM languages", "Kotlin", "Ktor", "REST API", "PostgreSQL"),
    ("shell_automation", "Shell / Bash automation", "Scripting and analytics", "Shell", "Bash", "CLI", "Files / external services"),
    ("r_analytics", "R analytics application", "Scripting and analytics", "R", "R 4.x", "CLI / Shiny", "Files / database"),
    ("scala_play", "Scala + Play Framework", "JVM languages", "Scala", "Play Framework", "REST API", "PostgreSQL"),
    ("clojure_ring", "Clojure + Ring", "JVM languages", "Clojure", "Ring / Reitit", "REST API", "PostgreSQL"),
    ("haskell_servant", "Haskell + Servant", "Functional languages", "Haskell", "Servant", "REST API", "PostgreSQL"),
    ("common_lisp", "Common Lisp application", "Functional languages", "Common Lisp", "ANSI Common Lisp", "CLI / service", "Files / database"),
    ("elixir_phoenix", "Elixir + Phoenix", "BEAM languages", "Elixir", "Phoenix", "LiveView / REST API", "PostgreSQL"),
    ("erlang_otp", "Erlang/OTP application", "BEAM languages", "Erlang", "OTP", "Service / CLI", "Mnesia / external database"),
    ("dart_server", "Dart server application", "Mobile and Dart", "Dart", "Dart / Shelf", "REST API", "PostgreSQL"),
    ("julia_application", "Julia application", "Scripting and analytics", "Julia", "Julia 1.x", "CLI / HTTP service", "Files / database"),
    ("fortran_native", "Modernize Fortran → Java 21", "Legacy modernization", "Java", "Spring Boot 3", "REST / batch", "PostgreSQL"),
    ("ada_native", "Modernize Ada → Java 21", "Legacy modernization", "Java", "Spring Boot 3", "REST / service", "PostgreSQL"),
    ("pascal_delphi", "Modernize Object Pascal / Delphi → .NET 8", "Legacy modernization", "C#", ".NET 8 Web API", "React / desktop replacement", "SQL Server"),
    ("ocaml_application", "Modernize OCaml → Java 21", "Legacy modernization", "Java", "Spring Boot 3", "REST / service", "PostgreSQL"),
    ("prolog_application", "Modernize Prolog rules → Java 21", "Legacy modernization", "Java", "Spring Boot 3 / rules module", "REST / service", "PostgreSQL"),
    ("abap_application", "SAP ABAP application", "Vendor enterprise", "ABAP", "SAP ABAP", "SAP GUI / service", "SAP"),
    ("pli_batch", "Modernize Enterprise PL/I → Java 21", "Legacy modernization", "Java", "Spring Boot 3 / Spring Batch", "REST / batch", "PostgreSQL / DB2"),
    ("rpg_application", "Modernize IBM i RPG → Java 21", "Legacy modernization", "Java", "Spring Boot 3 / Spring Batch", "REST / batch", "PostgreSQL / Db2"),
    ("jcl_batch", "Modernize z/OS JCL → Java Spring Batch", "Legacy modernization", "Java", "Spring Boot 3 / Spring Batch", "Batch orchestration", "PostgreSQL / object storage"),
    ("mumps_application", "Modernize M/MUMPS → .NET 8", "Legacy modernization", "C#", ".NET 8 Web API", "REST / service", "PostgreSQL"),
    ("natural_application", "Modernize Software AG Natural → Java 21", "Legacy modernization", "Java", "Spring Boot 3", "REST / batch", "PostgreSQL"),
    ("progress_openedge", "Modernize OpenEdge ABL → .NET 8", "Legacy modernization", "C#", ".NET 8 Web API", "React / service", "PostgreSQL / SQL Server"),
    ("salesforce_apex", "Salesforce Apex application", "Vendor enterprise", "Apex", "Salesforce Apex", "Lightning / API", "Salesforce"),
    ("sql_generic", "ANSI SQL DDL/DML", "Data and schemas", "SQL", "ANSI SQL", "Database", "ANSI SQL"),
    ("postgresql_sql", "PostgreSQL and PL/pgSQL", "Data and schemas", "SQL", "PostgreSQL PL/pgSQL", "Database API", "PostgreSQL"),
    ("plsql_oracle", "Oracle PL/SQL", "Data and schemas", "PL/SQL", "Oracle PL/SQL", "Database API", "Oracle"),
    ("tsql_sqlserver", "Microsoft T-SQL", "Data and schemas", "T-SQL", "SQL Server T-SQL", "Database API", "SQL Server"),
    ("yaml_artifact", "YAML configuration", "Configuration formats", "YAML", "YAML 1.2", "Configuration", "N/A"),
    ("json_artifact", "JSON document", "Configuration formats", "JSON", "RFC 8259 JSON", "Configuration", "N/A"),
    ("toml_artifact", "TOML configuration", "Configuration formats", "TOML", "TOML 1.0", "Configuration", "N/A"),
    ("xml_artifact", "XML document", "Configuration formats", "XML", "XML 1.0", "Configuration", "N/A"),
    ("markdown_artifact", "Markdown document", "Documentation", "Markdown", "CommonMark", "Documentation", "N/A"),
    ("graphql_schema", "GraphQL schema or operations", "API contracts", "GraphQL", "GraphQL", "API contract", "N/A"),
    ("protobuf_schema", "Protocol Buffers schema", "API contracts", "Protobuf", "Protocol Buffers 3", "API contract", "N/A"),
    ("dockerfile_artifact", "Dockerfile", "DevOps and cloud", "Dockerfile", "Docker", "Container image", "N/A"),
    ("terraform_hcl", "Terraform / HCL infrastructure", "DevOps and cloud", "Terraform/HCL", "Terraform", "Infrastructure as code", "Providers"),
    ("cloudformation_template", "AWS CloudFormation template", "DevOps and cloud", "CloudFormation", "AWS CloudFormation", "Infrastructure as code", "AWS"),
    ("kubernetes_manifest", "Kubernetes manifests", "DevOps and cloud", "Kubernetes manifests", "Kubernetes", "Deployment manifests", "Kubernetes"),
    ("helm_chart", "Helm chart", "DevOps and cloud", "Helm", "Helm 3", "Kubernetes package", "Kubernetes"),
    ("ansible_playbook", "Ansible playbook", "DevOps and cloud", "Ansible", "Ansible", "Automation", "Managed hosts"),
    ("jenkins_pipeline", "Jenkins pipeline", "CI/CD", "Jenkinsfile", "Jenkins Pipeline", "CI/CD", "Jenkins"),
    ("github_actions_workflow", "GitHub Actions workflow", "CI/CD", "GitHub Actions", "GitHub Actions", "CI/CD", "GitHub"),
]


_STACK_LANGUAGE_TOOL = {
    "c#": "dotnet", "csharp": "dotnet", "c": "c", "c++": "cpp", "cpp": "cpp",
    "java": "java+maven", "typescript": "typescript",
    "javascript": "typescript", "python": "python", "go": "go", "php": "php+composer",
    "ruby": "ruby+bundler", "rust": "rust+rust_package_manager", "swift": "swift+swift_package_manager", "kotlin": "kotlin+gradle",
    "shell": "shell", "r": "r", "scala": "scala+sbt", "clojure": "java+maven",
    "haskell": "haskell+haskell_build", "common lisp": "lisp", "elixir": "elixir+mix",
    "erlang": "erlang", "dart": "dart", "julia": "julia", "cobol": "cobol",
    "fortran": "fortran", "ada": "ada", "pascal/delphi": "pascal",
    "ocaml": "ocaml", "prolog": "prolog", "abap": "abap", "pl/i": "pli",
    "rpg": "rpg", "jcl": "jcl", "mumps": "mumps", "natural": "natural",
    "progress 4gl": "progress4gl", "apex": "apex", "jenkinsfile": "jenkinsfile",
    "sql": "sql_parser", "pl/sql": "sql_parser", "t-sql": "sql_parser",
    "yaml": "yaml_parser", "json": "json_parser", "toml": "toml_parser",
    "xml": "xml_parser", "graphql": "graphql_parser", "protobuf": "protobuf",
    "terraform/hcl": "terraform", "cloudformation": "yaml_parser",
    "kubernetes manifests": "yaml_parser", "helm": "yaml_parser",
    "ansible": "yaml_parser", "github actions": "yaml_parser",
    "dart / c#": "flutter+dotnet", "dart": "dart",
}
_INTERNAL_PARSER_LANGUAGES = {"markdown", "dockerfile"}
_PROJECT_READY_LANGUAGES = {
    "c#", "csharp", "java", "typescript", "javascript", "python", "go",
    "sql", "pl/sql", "t-sql",
    # php/-l, ruby/-c, cobol/cobc, shell/bash -n already run across every file in
    # the generated project (see build_runner.py's _run_source_checks / dispatch),
    # the same whole-project rigor python's compileall/go's `go test ./...` get -
    # they were excluded here only by omission, not because the check is weaker.
    "php", "ruby", "cobol", "shell",
    # c/cpp now get a real compile-every-file + link-the-project build
    # (build_runner.py._run_c_family_build), not just a per-file syntax pass -
    # this is what makes them genuinely project-ready rather than single-file-only.
    "c", "cpp",
    # validators.py._EXTERNAL_VALIDATORS already runs a real compiler per file
    # across the whole project for all of these, same tier as php/ruby above.
    # NOTE: membership here must match the STACK's `language` string exactly as
    # used by _stack_readiness() below, not the _STACK_LANGUAGE_TOOL tool-key -
    # they differ for 4 of these (e.g. language "common lisp" -> tool key "lisp").
    "rust", "swift", "kotlin", "r", "scala", "haskell", "elixir", "dart",
    "julia", "fortran", "ada", "pascal/delphi", "erlang", "ocaml", "prolog",
    "common lisp", "progress 4gl", "pl/i", "dart / c#",
    # tree-sitter grammar-backed, not a compiler, but genuine whole-file syntax
    # parsing run across every file - clojure has no _EXTERNAL_VALIDATORS entry,
    # it dispatches straight to _TREE_SITTER_LANGUAGES.
    "clojure",
    # Heuristic structural validators (validators.py._LEGACY_HEURISTIC_VALIDATORS)
    # - no real compiler exists for these vendor-platform languages (see
    # _UNAVAILABLE_VENDOR_TOOLCHAINS's former contents) - honestly labeled
    # "heuristic" in validation_mode, but still run across every project file.
    # (pl/i and progress 4gl already added above with their correct language-
    # string form, not repeated here.)
    "abap", "rpg", "jcl", "mumps", "natural", "apex",
}
_HEURISTIC_ONLY_LANGUAGES = {
    # Must match the STACK's `language` string form (see _PROJECT_READY_LANGUAGES
    # note above) - "progress 4gl" and "pl/i", not the tool-key forms.
    "abap", "rpg", "jcl", "mumps", "natural", "progress 4gl", "apex", "pl/i",
}
_DISPLAY_LANGUAGE = {
    "csharp": "C#", "c": "C", "cpp": "C++", "java": "Java",
    "typescript": "TypeScript", "javascript": "JavaScript", "python": "Python",
    "go": "Go", "php": "PHP", "ruby": "Ruby", "cobol": "COBOL",
    "sql": "SQL", "lisp": "Common Lisp", "rpg": "RPG",
}
_ARTIFACT_LANGUAGES = {
    "YAML", "JSON", "TOML", "XML", "Markdown", "GraphQL", "Protobuf",
    "Dockerfile", "Terraform/HCL", "CloudFormation", "Kubernetes manifests",
    "Helm", "Ansible", "Jenkinsfile", "GitHub Actions",
}


# Function: _stack_readiness
def _stack_readiness(stack: dict, tools: dict) -> dict:
    language = str(stack.get("language") or "").strip().casefold()
    if language in _INTERNAL_PARSER_LANGUAGES:
        return {
            "available": True, "project_ready": True, "full_generation": False,
            "validation_mode": "parser", "blocked_reason": None,
        }
    tool_key = _STACK_LANGUAGE_TOOL.get(language)
    if not tool_key:
        return {
            "available": False,
            "project_ready": False,
            "full_generation": False,
            "validation_mode": "unsupported",
            "blocked_reason": f"No strict validator is registered for {stack.get('language') or 'this target'}",
        }
    required = tool_key.split("+")
    stack_text = " ".join(
        str(stack.get(key) or "") for key in ("name", "backend", "frontend")
    ).casefold()
    if language == "dart" and "flutter" in stack_text:
        required = ["flutter", "dotnet"]
    missing = [key for key in required if not tools.get(key, {}).get("ready")]
    if language == "typescript" or language == "javascript":
        missing = [
            key for key in ("npm", "typescript_validator")
            if not tools.get(key, {}).get("ready")
        ]
    if "db2" in " ".join(str(stack.get(key) or "") for key in ("name", "database")).casefold():
        if not tools.get("db2_sql_parser", {}).get("ready"):
            missing.append("db2_sql_parser")
    artifact = any(language == value.casefold() for value in _ARTIFACT_LANGUAGES)
    is_heuristic = language in _HEURISTIC_ONLY_LANGUAGES
    # Structural heuristics are useful preflight checks, but cannot establish
    # vendor-platform build readiness. Keep generation selectable while making
    # the external compiler/platform prerequisite explicit.
    if is_heuristic:
        missing.append(f"{stack.get('backend') or stack.get('language')} vendor toolchain")
    if language == "jenkinsfile":
        missing.append("Jenkins controller pipeline validation")
    missing = list(dict.fromkeys(missing))
    available = not missing
    # No open-source compiler exists for these languages (proprietary vendor
    # platforms - SAP, IBM i/z-OS, Software AG, Progress, Salesforce); validated
    # via validators.py._LEGACY_HEURISTIC_VALIDATORS structural checks instead of
    # a real compiler. Distinct validation_mode so this is never conflated with
    # genuine compiler/parser-backed validation elsewhere in the catalog.
    from services.build_runner import PRODUCTION_PROJECT_BUILD_LANGUAGES
    # PRODUCTION_PROJECT_BUILD_LANGUAGES is keyed by the internal language id
    # modernizer.py's target["language"] actually holds ("csharp"), not the
    # display string this function's `language` var is derived from ("C#" ->
    # casefold "c#") - _DISPLAY_LANGUAGE's "csharp"->"C#" mapping is the only
    # one of these that changes spelling on casefold, so it's the only alias
    # needed (java/typescript/javascript/python/go/sql all casefold back to
    # their own internal id unchanged).
    gate_language = {"c#": "csharp", "common lisp": "lisp"}.get(language, language)
    return {
        "available": available,
        "project_ready": available and (language in _PROJECT_READY_LANGUAGES or artifact),
        # Distinct from project_ready: project_ready is about *validation* rigor
        # (can a real compiler/parser check this language's code across the
        # whole project). full_generation is about *generation* capability (can
        # the engine actually write new domain code in this language, not just
        # validate it) - see services/build_runner.py's
        # PRODUCTION_PROJECT_BUILD_LANGUAGES, the single source of truth the
        # "project" output-mode gate itself uses (services/modernizer.py).
        "full_generation": available and gate_language in PRODUCTION_PROJECT_BUILD_LANGUAGES,
        "validation_mode": "heuristic" if is_heuristic else "compiler/parser",
        "blocked_reason": None if not missing else "Missing strict prerequisite(s): " + ", ".join(missing),
    }


# Function: target_stacks
@app.get("/api/modernize/target-stacks")
async def target_stacks():
    """Return engine-native and guided presets; custom is always supported."""
    from services.modernizer import TARGET_STACKS
    from services.build_runner import toolchain_status
    readiness = await asyncio.to_thread(toolchain_status)
    tools = readiness["tools"]
    native = []
    for stack_id, value in TARGET_STACKS.items():
        category = "Database migration" if value.get("language") == "sql" else value.get("language", "Other").title()
        display_language = _DISPLAY_LANGUAGE.get(value.get("language"), value.get("language"))
        native.append({"id": stack_id, "engine_target": stack_id, "name": value["name"], "category": category,
                       "language": display_language, "backend": value.get("backend_tech"),
                       "frontend": value.get("frontend_tech"), "database": value.get("db_tech"), "native": True})
    native_ids = {item["id"] for item in native}
    guided = [{"id": item[0], "engine_target": "custom", "name": item[1], "category": item[2],
               "language": item[3], "backend": item[4], "frontend": item[5], "database": item[6], "native": False}
              for item in _ADDITIONAL_STACK_PRESETS if item[0] not in native_ids]
    stacks = [{**stack, **_stack_readiness(stack, tools)} for stack in native + guided]
    production_ready = sorted({stack["language"] for stack in stacks if stack["available"] and stack.get("language")})
    externally_gated = sorted({stack["language"] for stack in stacks if not stack["available"] and stack.get("language")})
    ready_artifacts = sorted(
        language for language in production_ready if language in _ARTIFACT_LANGUAGES
    )
    gated_artifacts = sorted(
        language for language in externally_gated if language in _ARTIFACT_LANGUAGES
    )
    production_project_languages = sorted({
        stack["language"] for stack in stacks
        if stack.get("project_ready") and stack.get("language") not in _ARTIFACT_LANGUAGES
    })
    return {
        "stacks": stacks,
        "custom_supported": True,
        "supported_languages": [value for value in production_ready if value not in _ARTIFACT_LANGUAGES],
        "production_project_languages": production_project_languages,
        "externally_gated_languages": [value for value in externally_gated if value not in _ARTIFACT_LANGUAGES],
        "supported_artifacts": ready_artifacts,
        "externally_gated_artifacts": gated_artifacts,
        "validation_policy": (
            "Compiler/parser backed and fail-closed; vendor toolchains must be configured."
        ),
    }


# Function: modernization_toolchains
@app.get("/api/modernize/toolchains")
async def modernization_toolchains():
    """Report build-host prerequisites before a governed transformation starts."""
    from services.build_runner import toolchain_status
    return await asyncio.to_thread(toolchain_status)


# Function: _install_toolchain_job
def _install_toolchain_job(job_id: str, tool_id: str, package_id: str, actor: str) -> None:
    job = _TOOLCHAIN_INSTALL_JOBS[job_id]
    try:
        job.update(status="running", message=f"Installing {tool_id}")
        proc = subprocess.run([
            "winget", "install", "--id", package_id, "--exact", "--silent",
            "--accept-package-agreements", "--accept-source-agreements",
        ], capture_output=True, text=True, timeout=900)
        output = (proc.stdout + "\n" + proc.stderr).strip()[-4000:]
        if proc.returncode != 0:
            raise RuntimeError(output or f"Installer exited with code {proc.returncode}")
        job.update(status="completed", progress=100, message="Installation completed", output=output)
        logger.info("Toolchain %s installed by %s", tool_id, actor)
    except Exception as exc:
        job.update(status="failed", message=str(exc), output=str(exc))
        logger.exception("Toolchain installation %s failed for actor %s", tool_id, actor)
    finally:
        job["updated_at"] = datetime.now(timezone.utc).isoformat()


# Function: install_modernization_toolchain
@app.post("/api/modernize/toolchains/install")
async def install_modernization_toolchain(request: Request):
    _require_admin(request)
    body = await request.json()
    tool_id = str(body.get("tool_id") or "")
    package_id = _TOOLCHAIN_PACKAGES.get(tool_id)
    if not package_id:
        raise HTTPException(status_code=400, detail="This prerequisite is not in the approved installation catalog")
    if os.name != "nt" or not shutil.which("winget"):
        raise HTTPException(status_code=409, detail="Automated installation requires winget on the Windows build host")
    from services.build_runner import toolchain_status
    current = next((item for item in toolchain_status()["catalog"] if item["id"] == tool_id), None)
    if current and current["installed"]:
        return {"status": "completed", "message": f"{current['name']} is already installed"}
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    _TOOLCHAIN_INSTALL_JOBS[job_id] = {"job_id": job_id, "tool_id": tool_id, "status": "queued", "progress": 0,
        "message": "Installation queued", "created_at": now, "updated_at": now, "actor": _actor(request)}
    threading.Thread(target=_install_toolchain_job, args=(job_id, tool_id, package_id, _actor(request)), daemon=True).start()
    return _TOOLCHAIN_INSTALL_JOBS[job_id]


# Function: modernization_toolchain_install_status
@app.get("/api/modernize/toolchains/install/{job_id}")
async def modernization_toolchain_install_status(job_id: str, request: Request):
    _require_admin(request)
    if job_id not in _TOOLCHAIN_INSTALL_JOBS:
        raise HTTPException(status_code=404, detail="Installation job not found")
    return _TOOLCHAIN_INSTALL_JOBS[job_id]


# Function: detect_language
@app.get("/api/fs/detect")
async def detect_language(path: str):
    """Quick scan of a folder to detect primary language and suggest modernization targets."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from services.analyzer import _enumerate_files, _language_distribution, _detect_tech_stack

    target_path = Path(path)
    if not target_path.exists() or not target_path.is_dir():
        raise HTTPException(status_code=404, detail=f"Path not found: {path}")

    try:
        files    = _enumerate_files(target_path)[:300]   # cap for speed
        lang_dist = _language_distribution(files)
        tech     = _detect_tech_stack(files)

        # Primary = highest file count among real code languages
        primary_lang, primary_meta = max(
            lang_dist.items(),
            key=lambda x: x[1].get("files", 0),
            default=("unknown", {}),
        )

        detected_techs = list(tech.keys())
        suggested    = _suggest_targets(detected_techs, primary_lang)

        return {
            "primary_language": primary_lang,
            "primary_label":    _LANG_LABELS.get(primary_lang, primary_lang or "Unknown"),
            "languages":        lang_dist,
            "detected_techs":   detected_techs,
            "tech_labels":      {k: _TECH_LABELS.get(k, k) for k in detected_techs},
            "suggested_targets": suggested,
            "file_count":       len(files),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# Function: _suggest_targets
def _suggest_targets(techs: list, primary_lang: Optional[str]) -> list:
    """Map detected tech stack to suggested modernization target IDs."""
    s: list = []
    if any(t in techs for t in ("asp_net_webforms", "asp_net_mvc", "asp_net_core", "winforms", "wpf")):
        s.extend(["aveva_mes", "dotnet8_blazor", "dotnet8_mvc", "react_ts"])
    if any(t in techs for t in ("java_ee", "spring")) or primary_lang == "java":
        s.extend(["spring_boot", "spring_boot_react"])
    if any(t in techs for t in ("jquery", "angular", "react")) or primary_lang in ("javascript", "typescript"):
        s.extend(["react_ts", "angular_ts", "vue3"])
    if "oracle_db" in techs:
        s.extend(["oracle_to_mssql", "oracle_to_postgres", "oracle_to_mongodb"])
    if "sql_server" in techs:
        s.append("mssql_to_postgres")
    if primary_lang == "cobol":
        s.extend(["spring_boot", "dotnet8_blazor"])
    if not s:
        s = ["aveva_mes", "dotnet8_blazor", "spring_boot", "react_ts"]
    # deduplicate while preserving order
    seen: set = set()
    return [x for x in s if not (x in seen or seen.add(x))]  # type: ignore[func-returns-value]


# Function: get_session
@app.get("/api/auth/session")
async def get_session(request: Request):
    payload = getattr(request.state, "auth", None)
    if not payload:
        return JSONResponse(status_code=401, content={"error": "No validated session"})
    return {
        "authenticated": True,
        "user": {
            "username": payload.get("sub"),
            "role": payload.get("role"),
            "apps": payload.get("apps", []),
        },
    }


# ─── Modernization jobs ───────────────────────────────────────────────────────

# Function: list_jobs
@app.get("/api/modernize/jobs")
async def list_jobs():
    return {
        "jobs": [
            {
                "job_id":      j["job_id"],
                "project_id":  j.get("project_id"),
                "folder_path": j["folder_path"],
                "status":      j["status"],
                "progress":    j["progress"],
                "phase":       j.get("phase"),
                "target_stack": j.get("target_stack"),
                "created_at":  j["created_at"],
                "updated_at":  j["updated_at"],
            }
            for j in _JOBS.values()
        ]
    }


# Function: start_analysis
@app.post("/api/modernize/analyze")
async def start_analysis(request: Request):
    body = await request.json()
    folder_path       = (body.get("folder_path") or "").strip()
    target_stack      = (body.get("target_stack") or "aveva_mes").strip()
    custom_stack_desc = (body.get("custom_stack_desc") or "").strip()
    output_mode       = (body.get("output_mode") or "project").strip()
    if not folder_path:
        raise HTTPException(status_code=400, detail="folder_path is required")

    p = Path(folder_path)
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"Path not found: {folder_path}")
    if not p.is_dir():
        raise HTTPException(status_code=400, detail="folder_path must be a directory")

    job_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    _JOBS[job_id] = {
        "job_id":            job_id,
        "folder_path":       str(p.resolve()),
        "target_stack":      target_stack,
        "custom_stack_desc": custom_stack_desc,
        "output_mode":       output_mode,
        "status":       "running",
        "progress":     0,
        "phase":       "starting",
        "created_at":  now,
        "updated_at":  now,
        "analysis":    None,
        "output":      None,
        "validation":  None,
        "error":       None,
        "events":      [],
    }
    _persist_job(job_id)
    _JOB_QUEUES[job_id] = queue.Queue()

    thread = threading.Thread(
        target=_analysis_worker,
        args=(job_id, str(p.resolve()), target_stack, custom_stack_desc, "", output_mode),
        daemon=True,
    )
    thread.start()

    return {"job_id": job_id, "status": "running"}


# Function: get_job
@app.get("/api/modernize/jobs/{job_id}")
async def get_job(job_id: str):
    return _job_response(_get_job(job_id))


# Function: stream_job
@app.get("/api/modernize/jobs/{job_id}/stream")
async def stream_job(job_id: str):
    _get_job(job_id)  # 404 if not found
    q = _JOB_QUEUES.get(job_id) or queue.Queue()

    # Function: event_generator
    async def event_generator():
        while True:
            try:
                event = q.get(timeout=0.5)
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("type") in ("complete", "validation_failed", "error"):
                    break
            except queue.Empty:
                job = _JOBS.get(job_id, {})
                if job.get("status") in ("completed", "validation_failed", "failed"):
                    break
                yield ": keepalive\n\n"
                await asyncio.sleep(0)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# Function: download_output
@app.get("/api/modernize/jobs/{job_id}/output")
async def download_output(job_id: str):
    job = _get_job(job_id)
    output = job.get("output")
    if job["status"] == "validation_failed":
        raise HTTPException(
            status_code=409,
            detail="Output failed strict build/semantic acceptance and is not production-ready",
        )
    # A "failed" job that was interrupted mid-run (backend restart) can still
    # have partial output worth downloading — see on_file in _prompt_worker.
    # A job that failed with no output at all (e.g. the LLM was unreachable
    # from the first call) has nothing to serve.
    if job["status"] not in ("completed", "failed") or not output:
        raise HTTPException(status_code=400, detail="Job not yet completed")

    # Build a ZIP in memory
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, content in output.items():
            zf.writestr(filename, content)
    buf.seek(0)

    folder_path = job.get("folder_path")
    if folder_path:
        raw_name = Path(folder_path).name
    else:
        # Prompt-driven jobs have no folder_path — every output key is
        # "<ProjectName>/relative/path" (see generate_from_prompt's
        # project_name derivation), so recover the name from that common
        # prefix instead of falling back to the opaque job_id hash.
        first_key = next(iter(output), "")
        raw_name = first_key.split("/", 1)[0] if "/" in first_key else job_id
    safe_name = re.sub(r"[^\w-]", "_", raw_name) or job_id
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="modernized_{safe_name}.zip"'},
    )


# Function: delete_job
@app.delete("/api/modernize/jobs/{job_id}")
async def delete_job(job_id: str):
    _get_job(job_id)
    _JOBS.pop(job_id, None)
    _JOB_QUEUES.pop(job_id, None)
    try:
        _job_file(job_id).unlink(missing_ok=True)
    except OSError:
        pass
    return {"deleted": job_id}


# ─── Guide/document text extraction helper ───────────────────────────────────

# Function: _extract_guide_text
# Function: _extract_pdf_text
def _extract_pdf_text(fname: str, content: bytes) -> str:
    try:
        import fitz  # PyMuPDF
        doc  = fitz.open(stream=content, filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return f"=== {fname} [PDF] ===\n{text}"
    except ImportError:
        return f"=== {fname} [PDF — install PyMuPDF to extract] ==="
    except Exception as exc:
        return f"=== {fname} [PDF extraction error: {exc}] ==="


# Function: _extract_docx_text
def _extract_docx_text(fname: str, content: bytes) -> str:
    try:
        import docx  # python-docx
        import io as _io
        document = docx.Document(_io.BytesIO(content))
        text = "\n".join(p.text for p in document.paragraphs)
        return f"=== {fname} [DOCX] ===\n{text}"
    except ImportError:
        return f"=== {fname} [DOCX — install python-docx to extract] ==="
    except Exception as exc:
        return f"=== {fname} [DOCX extraction error: {exc}] ==="


# Function: _extract_guide_text
async def _extract_guide_text(files: List[UploadFile]) -> tuple[list, str]:
    """
    Split uploaded files into image blobs + plain guide text.
    Supported text types: .txt .md .py .js .ts .json .yaml .yml .csv .xml .html .cs .java .sql
    Supported doc types:  .pdf (if fitz/PyMuPDF available), .docx (if python-docx available)
    Returns (images_data, guide_text)
    """
    images_data: list = []
    guide_parts: list = []

    TEXT_EXTS = {
        ".txt", ".md", ".py", ".js", ".ts", ".jsx", ".tsx", ".json",
        ".yaml", ".yml", ".csv", ".xml", ".html", ".htm", ".cs",
        ".java", ".sql", ".sh", ".bat", ".ps1", ".go", ".rs",
    }

    for f in files:
        if not f or not f.filename:
            continue
        content = await f.read()
        fname   = f.filename
        ct      = (f.content_type or "").lower()
        ext     = Path(fname).suffix.lower()

        if ct.startswith("image/") or ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"):
            images_data.append({"filename": fname, "content_type": ct or "image/png", "data": content})

        elif ext in TEXT_EXTS or ct.startswith("text/"):
            try:
                text = content.decode("utf-8", errors="replace")
                guide_parts.append(f"=== {fname} ===\n{text}")
            except Exception:
                pass

        elif ext == ".pdf":
            guide_parts.append(_extract_pdf_text(fname, content))

        elif ext in (".docx", ".doc"):
            guide_parts.append(_extract_docx_text(fname, content))

    return images_data, "\n\n".join(guide_parts)


# ─── Prompt-based analysis endpoint ─────────────────────────────────────────

# Function: analyze_from_prompt
@app.post("/api/modernize/analyze-prompt")
async def analyze_from_prompt(
    prompt: str = Form(...),
    target_stack: str = Form("aveva_mes"),
    custom_stack_desc: str = Form(""),
    output_mode: str = Form("project"),
    files: List[UploadFile] = File(default=[]),
    # Legacy field alias kept for backward compat
    images: List[UploadFile] = File(default=[]),
):
    """Start code generation from a natural-language prompt with optional file attachments
    (images, PDFs, text docs, source files, CSV, etc.)."""
    if not prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    from services.modernizer import _unresolved_requirement_placeholders
    unresolved = _unresolved_requirement_placeholders(prompt)
    if unresolved:
        raise HTTPException(
            status_code=400,
            detail=(
                "Replace unresolved requirement placeholders before generation: "
                + ", ".join(unresolved[:8])
            ),
        )

    all_uploads = list(files or []) + list(images or [])
    images_data, guide_text = await _extract_guide_text(all_uploads)

    job_id = str(uuid.uuid4())[:8]
    now    = datetime.utcnow().isoformat()
    _JOBS[job_id] = {
        "job_id":            job_id,
        "folder_path":       None,
        "prompt":            prompt,
        "target_stack":      target_stack,
        "custom_stack_desc": custom_stack_desc.strip(),
        "output_mode":       output_mode,
        "attached_files":    len(all_uploads),
        "status":       "pending",
        "progress":     0,
        "phase":        "",
        "analysis":     None,
        "output":       None,
        "validation":   None,
        "error":        None,
        "created_at":   now,
        "updated_at":   now,
        "events":       [],
    }
    _persist_job(job_id)
    _JOB_QUEUES[job_id] = queue.Queue()

    threading.Thread(
        target=_prompt_worker,
        args=(job_id, prompt, target_stack, images_data, custom_stack_desc.strip(), guide_text, output_mode),
        daemon=True,
    ).start()

    return {"job_id": job_id}


# Function: analyze_folder_with_guides
@app.post("/api/modernize/analyze-with-guides")
async def analyze_folder_with_guides(
    folder_path: str = Form(...),
    target_stack: str = Form("aveva_mes"),
    custom_stack_desc: str = Form(""),
    output_mode: str = Form("project"),
    files: List[UploadFile] = File(default=[]),
):
    """Start folder analysis with optional reference guide file attachments."""
    folder_path = folder_path.strip()
    if not folder_path:
        raise HTTPException(status_code=400, detail="folder_path is required")

    p = Path(folder_path)
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"Path not found: {folder_path}")
    if not p.is_dir():
        raise HTTPException(status_code=400, detail="folder_path must be a directory")

    _, guide_text = await _extract_guide_text(files or [])

    job_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    _JOBS[job_id] = {
        "job_id":            job_id,
        "folder_path":       str(p.resolve()),
        "target_stack":      target_stack,
        "custom_stack_desc": custom_stack_desc.strip(),
        "output_mode":       output_mode,
        "attached_files":    len(files or []),
        "status":       "running",
        "progress":     0,
        "phase":        "starting",
        "created_at":   now,
        "updated_at":   now,
        "analysis":     None,
        "output":       None,
        "validation":   None,
        "error":        None,
        "events":       [],
    }
    _persist_job(job_id)
    _JOB_QUEUES[job_id] = queue.Queue()

    threading.Thread(
        target=_analysis_worker,
        args=(job_id, str(p.resolve()), target_stack, custom_stack_desc.strip(), guide_text, output_mode),
        daemon=True,
    ).start()

    return {"job_id": job_id, "status": "running"}


# ─── Analysis worker (runs in background thread) ──────────────────────────────

# Function: _push
def _push(job_id: str, event: dict):
    """Send an SSE event and update job state."""
    job = _JOBS.get(job_id)
    if not job:
        return

    enriched_event = {
        **event,
        "ts": datetime.utcnow().isoformat(),
    }

    events = job.setdefault("events", [])
    events.append(enriched_event)

    q = _JOB_QUEUES.get(job_id)
    if q:
        q.put(enriched_event)
    job["updated_at"] = datetime.utcnow().isoformat()
    _persist_job(job_id)


# Function: _analysis_worker
def _analysis_worker(job_id: str, folder_path: str, target_stack: str = "aveva_mes", custom_stack_desc: str = "", guide_text: str = "", output_mode: str = "project"):
    try:
        from services.analyzer   import analyze_project
        from services.modernizer import modernize_project
    except ImportError as exc:
        _JOBS[job_id]["status"] = "failed"
        _JOBS[job_id]["error"]  = str(exc)
        _push(job_id, {"type": "error", "message": f"Service unavailable: {exc}"})
        return

    try:
        _JOBS[job_id]["status"] = "running"

        # Function: on_progress
        def on_progress(phase: str, pct: int, message: str):
            _JOBS[job_id]["status"]   = "running"
            _JOBS[job_id]["phase"]    = phase
            _JOBS[job_id]["progress"] = pct
            _push(job_id, {
                "type":     "progress",
                "phase":    phase,
                "progress": pct,
                "message":  message,
            })

        # Phase 1: deep analysis
        analysis = analyze_project(folder_path, on_progress, target_stack)
        _JOBS[job_id]["analysis"] = analysis

        _push(job_id, {
            "type":     "analysis_complete",
            "progress": 50,
            "analysis": analysis,
        })

        # Phase 2: generate modernized code
        output, validation = modernize_project(folder_path, analysis, target_stack, on_progress, custom_stack_desc, guide_text=guide_text, output_mode=output_mode)
        _JOBS[job_id]["output"]     = output
        _JOBS[job_id]["validation"] = validation
        validation_failed = _failed_strict_validation(validation, output_mode == "project")
        _JOBS[job_id]["status"]   = "validation_failed" if validation_failed else "completed"
        _JOBS[job_id]["progress"] = 100
        _JOBS[job_id]["phase"] = "validation_failed" if validation_failed else "complete"

        project_id = _JOBS[job_id].get("project_id")
        if project_id:
            actor = _JOBS[job_id].get("actor", "local-operator")
            parent = _JOBS[job_id].get("plan_snapshot_id")
            output_snapshot = _PROJECT_STORE.add_output_snapshot(
                project_id, output, actor,
                {"target_stack": target_stack, "job_id": job_id, "model": os.getenv("OLLAMA_MODEL"),
                 "prompt_template_version": "governed-contracts-v1"}, parent,
            )
            _PROJECT_STORE.set_status(project_id, "Validation Running")
            validation_snapshot = _PROJECT_STORE.add_json_snapshot(
                project_id, "validation", validation, actor,
                {"job_id": job_id, "output_snapshot_id": output_snapshot["id"]}, output_snapshot["id"],
            )
            _JOBS[job_id]["output_snapshot_id"] = output_snapshot["id"]
            _JOBS[job_id]["validation_snapshot_id"] = validation_snapshot["id"]
            _PROJECT_STORE.set_status(project_id, "Review Required")

        _push(job_id, {
            "type":     "validation_failed" if validation_failed else "complete",
            "progress": 100,
            "message":  "Generated code failed strict validation" if validation_failed else "Modernization complete",
            "output":   output if output.get("__single_file__") else None,
            "validation": validation,
        })

    except Exception as exc:
        logger.exception("Analysis worker failed for job %s", job_id)
        _JOBS[job_id]["status"] = "failed"
        _JOBS[job_id]["error"]  = str(exc)
        _push(job_id, {"type": "error", "message": str(exc)})


# Function: _prompt_worker
def _single_file_failed_validation(output: dict, validation: dict) -> bool:
    """Backward-compatible helper retained for callers outside this module."""
    return bool(output.get("__single_file__")) and int((validation or {}).get("failed", 0)) > 0


# Function: _failed_strict_validation
def _failed_strict_validation(validation: dict, require_project_build: bool) -> bool:
    """A job may complete only after strict checks, and projects also require
    their registered whole-output validation route."""
    result = validation or {}
    if result.get("production_ready") is False:
        return True
    if int(result.get("failed", 0)) > 0 or int(result.get("strict_checked", 0)) <= 0:
        return True
    build = result.get("build")
    return bool(require_project_build and (not build or not build.get("passed")))


# Function: _prompt_worker
def _prompt_worker(job_id: str, user_prompt: str, target_stack: str, images_data: list, custom_stack_desc: str = "", guide_text: str = "", output_mode: str = "project"):
    try:
        from services.modernizer import generate_from_prompt
    except ImportError as exc:
        _JOBS[job_id]["status"] = "failed"
        _JOBS[job_id]["error"]  = str(exc)
        _push(job_id, {"type": "error", "message": f"Service unavailable: {exc}"})
        return

    try:
        _JOBS[job_id]["status"] = "running"
        _JOBS[job_id]["output"] = {}

        # Function: on_progress
        def on_progress(phase: str, pct: int, message: str):
            _JOBS[job_id]["status"]   = "running"
            _JOBS[job_id]["phase"]    = phase
            _JOBS[job_id]["progress"] = pct
            _push(job_id, {
                "type":     "progress",
                "phase":    phase,
                "progress": pct,
                "message":  message,
            })

        # Function: on_file
        def on_file(path: str, content: str):
            """Persist each file the instant it's generated. This backend
            gets killed by something outside the app roughly every 3-5
            minutes under load — often shorter than a full multi-file
            generation — so without this, a job interrupted mid-run loses
            every file it had already finished, not just the ones in flight."""
            _JOBS[job_id]["output"][path] = content
            _persist_job(job_id)

        output, validation = generate_from_prompt(
            user_prompt, target_stack, images_data, on_progress, custom_stack_desc,
            guide_text=guide_text, output_mode=output_mode, on_file=on_file,
        )
        _JOBS[job_id]["output"]     = output
        _JOBS[job_id]["validation"] = validation
        validation_failed = _failed_strict_validation(validation, output_mode == "project")
        _JOBS[job_id]["status"]   = "validation_failed" if validation_failed else "completed"
        _JOBS[job_id]["progress"] = 100
        _JOBS[job_id]["phase"] = "validation_failed" if validation_failed else "complete"

        project_id = _JOBS[job_id].get("project_id")
        if project_id:
            actor = _JOBS[job_id].get("actor", "local-operator")
            parent = _JOBS[job_id].get("plan_snapshot_id")
            output_snapshot = _PROJECT_STORE.add_output_snapshot(project_id, output, actor,
                {"target_stack": target_stack, "job_id": job_id, "model": os.getenv("OLLAMA_MODEL"),
                 "prompt_template_version": "governed-prompt-contracts-v1"}, parent)
            _PROJECT_STORE.set_status(project_id, "Validation Running")
            validation_snapshot = _PROJECT_STORE.add_json_snapshot(project_id, "validation", validation, actor,
                {"job_id": job_id, "output_snapshot_id": output_snapshot["id"]}, output_snapshot["id"])
            _JOBS[job_id]["output_snapshot_id"] = output_snapshot["id"]
            _JOBS[job_id]["validation_snapshot_id"] = validation_snapshot["id"]
            _PROJECT_STORE.set_status(project_id, "Review Required")

        _push(job_id, {
            "type":     "validation_failed" if validation_failed else "complete",
            "progress": 100,
            "message":  "Generated code failed strict validation" if validation_failed else "Code generation complete",
            "output":   output if output.get("__single_file__") else None,
            "validation": validation,
        })

    except Exception as exc:
        logger.exception("Prompt worker failed for job %s", job_id)
        _JOBS[job_id]["status"] = "failed"
        _JOBS[job_id]["error"]  = str(exc)
        _push(job_id, {"type": "error", "message": str(exc)})


# ─── Entry point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    uvicorn.run(
        "api.server:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=8084,
        reload=False,
        log_level="info",
    )
