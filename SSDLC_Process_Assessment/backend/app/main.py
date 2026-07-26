# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — backend/app (main.py)
# Date: 2026-04-05
# ---------------------------------------------------------------------------
from __future__ import annotations

import asyncio
import json
import os
import threading
import uuid
from asyncio import to_thread
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from .auth import SSDLC_APP, allow_local_auth_bypass, auth_required, decode_access_token, extract_bearer_token, is_local_origin
from .ollama_client import list_models, ollama_settings, stream_executive_summary
from .service import AssessmentService

# Consolidation Savings Model routes
from .csm.api.routes_upload import router as csm_upload_router
from .csm.api.routes_workbook import router as csm_workbook_router
from .csm.api.routes_dashboard import router as csm_dashboard_router
from .csm.api.routes_scenarios import router as csm_scenarios_router
from .csm.api.routes_calculations import router as csm_calculations_router

MODULE_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = MODULE_ROOT / "frontend" / "dist"
WORKBOOK_PATH = MODULE_ROOT / "data" / "Assessment_PR_Enhanced Version.xlsx"
UI_WORKBOOK_PATH = MODULE_ROOT / "data" / "UI.xlsx"
DBDATA_PATH = MODULE_ROOT / "data" / "DBData.sqlite"
STATE_DIR = MODULE_ROOT / "data" / "assessments"
EVIDENCE_FILES_DIR = MODULE_ROOT / "data" / "evidence-files"

ALLOWED_EVIDENCE_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".pptx", ".ppt", ".png", ".jpg", ".jpeg", ".gif", ".webp"}

service = AssessmentService(
    workbook_path=WORKBOOK_PATH,
    state_dir=STATE_DIR,
    ui_workbook_path=UI_WORKBOOK_PATH,
    dbdata_path=DBDATA_PATH,
)

app = FastAPI(title="SSDLC Process Assessment API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5182",
        "http://localhost:8090",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5182",
        "http://127.0.0.1:8090",
        *[origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()],
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Function: enforce_auth
@app.middleware("http")
async def enforce_auth(request: Request, call_next):
    path = request.url.path
    public_paths = {"/api/health", "/docs", "/openapi.json", "/redoc"}
    if request.method == "OPTIONS" or not auth_required() or not path.startswith("/api") or path in public_paths or path.startswith("/api/csm"):
        return await call_next(request)

    if allow_local_auth_bypass() and is_local_origin(request):
        request.state.auth = {
            "uid": 0,
            "username": "local-admin",
            "role": "admin",
            "apps": [SSDLC_APP],
        }
        return await call_next(request)

    token = extract_bearer_token(request.headers.get("Authorization", ""))
    if not token:
        if path == "/api/auth/session":
            request.state.auth = None
            return await call_next(request)
        return JSONResponse(status_code=401, content={"error": "Authentication required"})

    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        if path == "/api/auth/session":
            request.state.auth = None
            return await call_next(request)
        return JSONResponse(status_code=401, content={"error": str(exc)})

    if payload.get("role") != "admin" and SSDLC_APP not in (payload.get("apps") or []):
        return JSONResponse(status_code=403, content={"error": "Access denied for SSDLC Process Assessment"})

    request.state.auth = payload
    return await call_next(request)


app.include_router(csm_upload_router,       prefix="/api")
app.include_router(csm_workbook_router,     prefix="/api")
app.include_router(csm_dashboard_router,    prefix="/api")
app.include_router(csm_scenarios_router,    prefix="/api")
app.include_router(csm_calculations_router, prefix="/api")


# Function: csm_health
@app.get("/api/csm/health")
def csm_health() -> dict:
    return {"status": "ok", "module": "Consolidation Savings Model", "port": 8091}


if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    # Function: spa_or_error
    @app.exception_handler(StarletteHTTPException)
    async def spa_or_error(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 404 and not request.url.path.startswith("/api"):
            return FileResponse(str(FRONTEND_DIST / "index.html"))
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

    # Function: index
    @app.get("/", include_in_schema=False)
    async def index():
        return FileResponse(str(FRONTEND_DIST / "index.html"))


# Function: health
@app.get("/api/health")
def health() -> dict[str, str | int]:
    return {"status": "ok", "module": "SSDLC Process Assessment", "port": 8091}


# Function: auth_session
@app.get("/api/auth/session")
def auth_session(request: Request):
    payload = getattr(request.state, "auth", None)
    return {
        "authenticated": bool(payload),
        "user": None if not payload else {
            "id": payload.get("uid"),
            "username": payload.get("username"),
            "role": payload.get("role"),
            "apps": payload.get("apps") or [],
        },
        "expires_at": None if not payload else payload.get("exp"),
    }


# Function: ollama_status
@app.get("/api/ollama/status")
def ollama_status():
    return {**ollama_settings(), **list_models()}


# Function: bootstrap
@app.get("/api/bootstrap")
def bootstrap():
    return {**service.bootstrap(), "ollama": ollama_status()}


# Function: get_tower
@app.get("/api/towers/{tower_key}")
def get_tower(tower_key: str):
    try:
        return {"tower": service.get_tower(tower_key), "dashboard": service.build_dashboard()}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# Function: update_tower
@app.put("/api/towers/{tower_key}")
async def update_tower(tower_key: str, request: Request):
    try:
        payload = await request.json()
        tower = service.update_tower(tower_key, payload)
        return {"tower": tower, "dashboard": service.build_dashboard()}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# Function: predict_recommendations
@app.post("/api/towers/{tower_key}/recommendations")
async def predict_recommendations(tower_key: str, request: Request):
    try:
        payload = await request.json()
        tower = service.generate_recommendations(
            tower_key,
            row_ids=payload.get("rowIds") or [],
            force=bool(payload.get("force")),
            requested_model=payload.get("model"),
        )
        return {"tower": tower, "dashboard": service.build_dashboard(), "ollama": ollama_status()}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# Function: predict_row
@app.post("/api/towers/{tower_key}/row-predictions")
async def predict_row(tower_key: str, request: Request):
    try:
        payload = await request.json()
        tower = service.generate_row_predictions(
            tower_key=tower_key,
            row_id=payload.get("rowId"),
            selected_level_key=payload.get("selectedLevelKey"),
            evidence=payload.get("evidence") or "",
            current_state=payload.get("currentState") or "",
            requested_model=payload.get("model"),
        )
        return {"tower": tower, "dashboard": service.build_dashboard(), "ollama": ollama_status()}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# Function: predict_adhoc
@app.post("/api/predict")
async def predict_adhoc(request: Request):
    payload = await request.json()
    result = service.generate_adhoc_prediction(
        application_name=payload.get("applicationName") or "",
        dimension=payload.get("dimension") or "",
        phase=payload.get("phase") or "",
        question=payload.get("question") or "",
        selected_level_key=payload.get("selectedLevelKey"),
        evidence=payload.get("evidence") or "",
        current_state=payload.get("currentState") or "",
        requested_model=payload.get("model"),
    )
    return {**result, "ollama": ollama_status()}


# Function: predict_batch
@app.post("/api/predict-batch")
async def predict_batch(request: Request):
    """Stream gap/recommendation predictions for every row submitted in one request.

    Ollama is mandatory — returns 503 if Ollama is unreachable, 400 if the required model
    is not loaded. Each SSE event carries one row result so the UI can update progressively.
    """
    ollama_info = ollama_status()
    if not ollama_info.get("available"):
        raise HTTPException(
            status_code=503,
            detail="Ollama is not available. Run: ollama serve",
        )

    default_model = ollama_info.get("default_model", "llama3.1")
    loaded_names = [m.get("name", "") for m in (ollama_info.get("models") or [])]
    if not any(n == default_model or n.startswith(f"{default_model}:") for n in loaded_names):
        raise HTTPException(
            status_code=400,
            detail=f"Model '{default_model}' is not loaded. Run: ollama pull {default_model}",
        )

    payload = await request.json()
    rows: list[dict] = payload.get("rows") or []
    requested_model: str | None = payload.get("model")

    # Function: event_generator
    async def event_generator():
        total = len(rows)
        for i, row_item in enumerate(rows):
            result = await to_thread(
                service.generate_single_prediction_for_batch,
                row_item,
                requested_model,
            )
            data = json.dumps({
                "index": i,
                "total": total,
                "uiId": row_item.get("uiId", ""),
                **result,
            })
            yield f"data: {data}\n\n"
        yield 'data: {"done":true}\n\n'

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# Function: dashboard
@app.get("/api/dashboard")
def dashboard():
    return service.build_dashboard()


# Function: executive_summary
@app.post("/api/executive-summary")
async def executive_summary(request: Request):
    """Stream an Ollama-generated executive narrative for the current dashboard."""
    ollama_info = ollama_status()
    if not ollama_info.get("available"):
        raise HTTPException(status_code=503, detail="Ollama is not available. Run: ollama serve")

    payload = await request.json()
    dashboard_data: dict = payload.get("dashboard") or service.build_dashboard()
    requested_model: str | None = payload.get("model")

    # Function: event_gen
    async def event_gen():
        loop = asyncio.get_running_loop()
        token_queue: asyncio.Queue = asyncio.Queue()

        # Function: blocking
        def blocking() -> None:
            try:
                for token in stream_executive_summary(dashboard_data, requested_model):
                    loop.call_soon_threadsafe(token_queue.put_nowait, {"text": token})
            except Exception:  # noqa: BLE001
                pass
            finally:
                loop.call_soon_threadsafe(token_queue.put_nowait, None)

        t = threading.Thread(target=blocking, daemon=True)
        t.start()

        while True:
            item = await token_queue.get()
            if item is None:
                yield 'data: {"done":true}\n\n'
                break
            yield f"data: {json.dumps(item)}\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# Function: upload_evidence_file
@app.post("/api/towers/{tower_key}/rows/{row_id}/evidence-files")
async def upload_evidence_file(tower_key: str, row_id: str, file: UploadFile = File(...)):
    try:
        service._require_template(tower_key)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EVIDENCE_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type '{ext}' is not allowed.")

    stored_name = f"{uuid.uuid4().hex}{ext}"
    dest_dir = EVIDENCE_FILES_DIR / tower_key / row_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    (dest_dir / stored_name).write_bytes(content)

    service.add_evidence_file(tower_key, row_id, stored_name, file.filename or stored_name)
    tower = service.get_tower(tower_key)
    return {
        "storedName": stored_name,
        "originalName": file.filename,
        "tower": tower,
        "dashboard": service.build_dashboard(),
    }


# Function: download_evidence_file
@app.get("/api/towers/{tower_key}/rows/{row_id}/evidence-files/{stored_name}")
async def download_evidence_file(tower_key: str, row_id: str, stored_name: str):
    if "/" in stored_name or "\\" in stored_name or stored_name.startswith("."):
        raise HTTPException(status_code=400, detail="Invalid filename.")
    file_path = EVIDENCE_FILES_DIR / tower_key / row_id / stored_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")
    state = service._load_state(tower_key)
    original_name = stored_name
    for row in state.get("responses") or []:
        if row.get("id") == row_id:
            for f in row.get("evidenceFiles") or []:
                if f.get("storedName") == stored_name:
                    original_name = f.get("originalName", stored_name)
            break
    return FileResponse(str(file_path), filename=original_name)


# Function: delete_evidence_file
@app.delete("/api/towers/{tower_key}/rows/{row_id}/evidence-files/{stored_name}")
async def delete_evidence_file(tower_key: str, row_id: str, stored_name: str):
    if "/" in stored_name or "\\" in stored_name or stored_name.startswith("."):
        raise HTTPException(status_code=400, detail="Invalid filename.")
    file_path = EVIDENCE_FILES_DIR / tower_key / row_id / stored_name
    service.remove_evidence_file(tower_key, row_id, stored_name)
    if file_path.exists():
        file_path.unlink()
    tower = service.get_tower(tower_key)
    return {"tower": tower, "dashboard": service.build_dashboard()}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=os.getenv("HOST", "0.0.0.0"), port=8091, reload=True)
