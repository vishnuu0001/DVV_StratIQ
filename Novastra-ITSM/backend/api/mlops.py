# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — backend/api (mlops.py)
# Date: 2026-07-02
# ---------------------------------------------------------------------------
from __future__ import annotations
import asyncio, json, logging, math, os, re, time, uuid
from pathlib import Path
from fastapi import APIRouter, Body, Depends, HTTPException
from backend.api.auth import get_current_user
import backend.config as cfg

router = APIRouter(prefix="/api/mlops", tags=["MLOps"])
logger = logging.getLogger(__name__)

_REGISTRY_FILE = Path(cfg.DATA_DIR) / "mlops_registry.json"
_EXPERIMENTS_FILE = Path(cfg.DATA_DIR) / "mlops_experiments.json"


# Function: _load_json
def _load_json(path: Path, default: list | dict) -> list | dict:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default if not isinstance(default, type) else default()


# Function: _save_json
def _save_json(path: Path, data: list | dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


# Function: _compute_drift
def _compute_drift(reference: list[float], current: list[float]) -> dict:
    """Simple statistical drift: compare mean/std of two numeric distributions."""
    if not reference or not current:
        return {"drift_detected": False, "drift_score": 0.0, "method": "none"}
    ref_mean = sum(reference) / len(reference)
    cur_mean = sum(current) / len(current)
    ref_var = sum((x - ref_mean) ** 2 for x in reference) / max(len(reference), 1)
    cur_var = sum((x - cur_mean) ** 2 for x in current) / max(len(current), 1)
    ref_std = math.sqrt(ref_var) or 1e-9
    cur_std = math.sqrt(cur_var) or 1e-9

    # Normalized mean shift
    mean_shift = abs(cur_mean - ref_mean) / ref_std
    # Std ratio
    std_ratio = max(cur_std, ref_std) / min(cur_std, ref_std) if min(cur_std, ref_std) > 1e-12 else 1.0
    drift_score = round(min(1.0, mean_shift * 0.6 + (std_ratio - 1) * 0.1), 3)
    return {
        "drift_detected": drift_score > 0.3,
        "drift_score": drift_score,
        "reference_mean": round(ref_mean, 4),
        "current_mean": round(cur_mean, 4),
        "mean_shift_sigma": round(mean_shift, 3),
        "std_ratio": round(std_ratio, 3),
        "method": "statistical",
    }


# Function: list_models
@router.get("/models")
async def list_models(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    registry: list = _load_json(_REGISTRY_FILE, [])
    return {"models": registry, "total": len(registry)}


# Function: register_model
@router.post("/models/register")
async def register_model(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    model_name = payload.get("model_name", "")
    model_type = payload.get("model_type", "")
    version = payload.get("version", "1.0.0")
    metrics = payload.get("metrics", {})
    description = payload.get("description", "")
    tags = payload.get("tags", [])
    if not model_name:
        raise HTTPException(status_code=400, detail="model_name is required")

    registry: list = _load_json(_REGISTRY_FILE, [])
    model_id = str(uuid.uuid4())[:8]
    entry = {
        "model_id": model_id,
        "model_name": model_name,
        "model_type": model_type,
        "version": version,
        "description": description,
        "metrics": metrics,
        "tags": tags,
        "status": "registered",
        "registered_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "registered_by": current_user.get("username", ""),
    }
    registry.append(entry)
    _save_json(_REGISTRY_FILE, registry)
    logger.info("Model registered: %s v%s (id=%s)", model_name, version, model_id)
    return {"message": "Model registered", "model": entry}


# Function: update_model_status
@router.put("/models/{model_id}/status")
async def update_model_status(
    model_id: str,
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    status = payload.get("status", "")
    allowed = {"registered", "staging", "production", "archived", "deprecated"}
    if status not in allowed:
        raise HTTPException(status_code=400, detail=f"status must be one of {allowed}")
    registry: list = _load_json(_REGISTRY_FILE, [])
    for m in registry:
        if m["model_id"] == model_id:
            m["status"] = status
            m["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            _save_json(_REGISTRY_FILE, registry)
            return {"message": "Status updated", "model": m}
    raise HTTPException(status_code=404, detail="Model not found")


# Function: list_experiments
@router.get("/experiments")
async def list_experiments(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    experiments: list = _load_json(_EXPERIMENTS_FILE, [])
    return {"experiments": experiments, "total": len(experiments)}


# Function: log_experiment
@router.post("/experiments/log")
async def log_experiment(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    experiment_name = payload.get("experiment_name", "")
    model_name = payload.get("model_name", "")
    run_id = str(uuid.uuid4())[:12]
    metrics = payload.get("metrics", {})
    params = payload.get("params", {})
    tags = payload.get("tags", [])
    notes = payload.get("notes", "")
    if not experiment_name:
        raise HTTPException(status_code=400, detail="experiment_name is required")

    experiments: list = _load_json(_EXPERIMENTS_FILE, [])
    run = {
        "run_id": run_id,
        "experiment_name": experiment_name,
        "model_name": model_name,
        "metrics": metrics,
        "params": params,
        "tags": tags,
        "notes": notes,
        "status": "completed",
        "logged_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "logged_by": current_user.get("username", ""),
    }
    experiments.append(run)
    _save_json(_EXPERIMENTS_FILE, experiments)
    return {"message": "Experiment run logged", "run": run}


# Function: check_drift
@router.post("/drift/check")
async def check_drift(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    model_id = payload.get("model_id", "")
    feature_name = payload.get("feature_name", "feature")
    reference_values: list[float] = [float(v) for v in payload.get("reference_values", [])]
    current_values: list[float] = [float(v) for v in payload.get("current_values", [])]

    if not reference_values or not current_values:
        raise HTTPException(status_code=400, detail="reference_values and current_values are required")

    drift = _compute_drift(reference_values, current_values)
    drift["model_id"] = model_id
    drift["feature_name"] = feature_name
    drift["reference_sample_size"] = len(reference_values)
    drift["current_sample_size"] = len(current_values)
    drift["recommendation"] = (
        "Retrain model — significant feature drift detected." if drift["drift_detected"]
        else "No retraining required — distribution is stable."
    )
    return drift


# Function: batch_drift
@router.post("/drift/batch")
async def batch_drift(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    model_id = payload.get("model_id", "")
    features: list[dict] = payload.get("features", [])

    results = []
    drift_count = 0
    for feat in features:
        ref = [float(v) for v in feat.get("reference_values", [])]
        cur = [float(v) for v in feat.get("current_values", [])]
        drift = _compute_drift(ref, cur)
        drift["feature_name"] = feat.get("feature_name", "")
        results.append(drift)
        if drift["drift_detected"]:
            drift_count += 1

    overall_score = round(sum(r["drift_score"] for r in results) / max(len(results), 1), 3)
    return {
        "model_id": model_id,
        "features_checked": len(results),
        "drifted_features": drift_count,
        "overall_drift_score": overall_score,
        "retrain_recommended": drift_count > 0,
        "feature_drift_details": results,
    }


# Function: model_lineage
@router.get("/models/{model_id}/lineage")
async def model_lineage(model_id: str, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    registry: list = _load_json(_REGISTRY_FILE, [])
    model = next((m for m in registry if m["model_id"] == model_id), None)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    experiments: list = _load_json(_EXPERIMENTS_FILE, [])
    related_runs = [e for e in experiments if e.get("model_name") == model.get("model_name")]
    return {
        "model": model,
        "training_runs": len(related_runs),
        "experiment_history": related_runs[-10:],
        "data_lineage": {
            "input_schema": model.get("tags", []),
            "training_data_source": model.get("description", ""),
        },
    }
