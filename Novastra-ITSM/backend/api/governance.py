# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — backend/api (governance.py)
# Date: 2025-12-28
# ---------------------------------------------------------------------------
from __future__ import annotations
import asyncio, json, logging, os, re, sqlite3, time, uuid
from pathlib import Path
from fastapi import APIRouter, Body, Depends, HTTPException
from backend.api.auth import get_current_user
import backend.config as cfg

router = APIRouter(prefix="/api/governance", tags=["Security & Governance"])
logger = logging.getLogger(__name__)

_AUDIT_DB = Path(cfg.DATA_DIR) / "audit_log.db"

# PII patterns
_PII_PATTERNS: dict[str, re.Pattern] = {
    "email":       re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'),
    "phone_us":    re.compile(r'\b(?:\+1[\s-]?)?(?:\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}\b'),
    "phone_intl":  re.compile(r'\+\d{1,3}[\s-]?\d{6,12}\b'),
    "ssn":         re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
    "credit_card": re.compile(r'\b(?:\d{4}[\s-]?){3}\d{4}\b'),
    "ip_address":  re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
    "date_of_birth": re.compile(r'\bDOB:?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', re.IGNORECASE),
    "aadhaar":     re.compile(r'\b\d{4}\s\d{4}\s\d{4}\b'),
    "passport":    re.compile(r'\b[A-Z]{1,2}\d{7,8}\b'),
}

_REPLACEMENT_MAP = {
    "email": "[EMAIL_REDACTED]",
    "phone_us": "[PHONE_REDACTED]",
    "phone_intl": "[PHONE_REDACTED]",
    "ssn": "[SSN_REDACTED]",
    "credit_card": "[CC_REDACTED]",
    "ip_address": "[IP_REDACTED]",
    "date_of_birth": "[DOB_REDACTED]",
    "aadhaar": "[AADHAAR_REDACTED]",
    "passport": "[PASSPORT_REDACTED]",
}


# Function: _ensure_audit_db
def _ensure_audit_db():
    _AUDIT_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_AUDIT_DB))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            actor TEXT,
            action TEXT NOT NULL,
            resource_type TEXT,
            resource_id TEXT,
            outcome TEXT,
            ip_address TEXT,
            extra_json TEXT
        )
    """)
    conn.commit()
    conn.close()


_ensure_audit_db()


# Function: _mask_pii
def _mask_pii(text: str, types_to_mask: list[str] | None = None) -> tuple[str, dict]:
    masked = text
    found: dict[str, int] = {}
    patterns = {k: v for k, v in _PII_PATTERNS.items() if types_to_mask is None or k in types_to_mask}
    for pii_type, pattern in patterns.items():
        matches = pattern.findall(masked)
        if matches:
            found[pii_type] = len(matches)
            masked = pattern.sub(_REPLACEMENT_MAP[pii_type], masked)
    return masked, found


# Function: mask_pii
@router.post("/pii-mask")
async def mask_pii(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    text = payload.get("text", "")
    types_to_mask: list[str] | None = payload.get("pii_types", None)
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    masked_text, found = _mask_pii(text, types_to_mask)
    total_masked = sum(found.values())
    return {
        "original_length": len(text),
        "masked_text": masked_text,
        "pii_types_found": found,
        "total_pii_instances_masked": total_masked,
        "is_clean": total_masked == 0,
    }


# Function: mask_pii_batch
@router.post("/pii-mask-batch")
async def mask_pii_batch(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    texts: list[str] = payload.get("texts", [])
    types_to_mask: list[str] | None = payload.get("pii_types", None)
    if not texts:
        raise HTTPException(status_code=400, detail="texts list is required")

    results = []
    for i, text in enumerate(texts):
        masked, found = _mask_pii(text, types_to_mask)
        results.append({
            "index": i,
            "masked_text": masked,
            "pii_found": found,
            "is_clean": sum(found.values()) == 0,
        })
    return {
        "results": results,
        "total_documents": len(texts),
        "documents_with_pii": sum(1 for r in results if not r["is_clean"]),
    }


# Function: log_audit_event
@router.post("/audit/log")
async def log_audit_event(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    action = payload.get("action", "")
    resource_type = payload.get("resource_type", "")
    resource_id = payload.get("resource_id", "")
    outcome = payload.get("outcome", "success")
    extra = payload.get("extra", {})
    if not action:
        raise HTTPException(status_code=400, detail="action is required")

    entry_id = str(uuid.uuid4())
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    actor = current_user.get("username", "system")

    conn = sqlite3.connect(str(_AUDIT_DB))
    conn.execute(
        "INSERT INTO audit_log VALUES (?,?,?,?,?,?,?,?,?)",
        (entry_id, timestamp, actor, action, resource_type, resource_id, outcome, "", json.dumps(extra)),
    )
    conn.commit()
    conn.close()
    return {"message": "Audit event logged", "entry_id": entry_id, "timestamp": timestamp}


# Function: get_audit_logs
@router.get("/audit/logs")
async def get_audit_logs(
    limit: int = 100,
    actor: str = "",
    action: str = "",
    resource_type: str = "",
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    clauses = []
    params: list = []
    if actor:
        clauses.append("actor = ?")
        params.append(actor)
    if action:
        clauses.append("action LIKE ?")
        params.append(f"%{action}%")
    if resource_type:
        clauses.append("resource_type = ?")
        params.append(resource_type)

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    params.append(min(limit, 1000))

    conn = sqlite3.connect(str(_AUDIT_DB))
    rows = conn.execute(
        f"SELECT id, timestamp, actor, action, resource_type, resource_id, outcome, extra_json "
        f"FROM audit_log {where} ORDER BY timestamp DESC LIMIT ?",
        params,
    ).fetchall()
    conn.close()

    logs = [
        {
            "id": r[0], "timestamp": r[1], "actor": r[2], "action": r[3],
            "resource_type": r[4], "resource_id": r[5], "outcome": r[6],
            "extra": json.loads(r[7] or "{}"),
        }
        for r in rows
    ]
    return {"logs": logs, "total": len(logs)}


# Function: check_bias
@router.post("/bias-check")
async def check_bias(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    dataset: list[dict] = payload.get("dataset", [])
    sensitive_attributes: list[str] = payload.get("sensitive_attributes", ["gender", "age_group", "region"])
    outcome_field: str = payload.get("outcome_field", "outcome")
    if not dataset:
        raise HTTPException(status_code=400, detail="dataset is required")

    bias_results = []
    for attr in sensitive_attributes:
        groups: dict[str, list] = {}
        for row in dataset:
            key = str(row.get(attr, "unknown"))
            val = row.get(outcome_field)
            if val is not None:
                groups.setdefault(key, []).append(float(val))

        if len(groups) < 2:
            continue

        group_stats = {k: {"mean": sum(v) / len(v), "count": len(v)} for k, v in groups.items()}
        means = [s["mean"] for s in group_stats.values()]
        max_disparity = round(max(means) - min(means), 4) if means else 0.0
        bias_detected = max_disparity > 0.1

        bias_results.append({
            "attribute": attr,
            "group_stats": group_stats,
            "max_disparity": max_disparity,
            "bias_detected": bias_detected,
            "severity": "HIGH" if max_disparity > 0.3 else "MEDIUM" if max_disparity > 0.1 else "LOW",
            "recommendation": (
                "Investigate and mitigate — high outcome disparity across groups." if max_disparity > 0.3
                else "Monitor — moderate disparity detected." if bias_detected
                else "No significant bias detected."
            ),
        })

    overall_bias = any(r["bias_detected"] for r in bias_results)
    return {
        "dataset_size": len(dataset),
        "attributes_checked": sensitive_attributes,
        "bias_detected": overall_bias,
        "results": bias_results,
        "recommendation": "Review flagged attributes and apply bias mitigation techniques." if overall_bias else "Dataset appears balanced.",
    }


# Function: record_lineage
@router.post("/data-lineage/record")
async def record_lineage(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    lineage_path = Path(cfg.DATA_DIR) / "data_lineage.json"
    entries: list = []
    try:
        if lineage_path.exists():
            entries = json.loads(lineage_path.read_text(encoding="utf-8"))
    except Exception:
        pass

    entry = {
        "lineage_id": str(uuid.uuid4())[:12],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "recorded_by": current_user.get("username", ""),
        "source_system": payload.get("source_system", ""),
        "destination": payload.get("destination", ""),
        "transformation": payload.get("transformation", ""),
        "data_type": payload.get("data_type", ""),
        "record_count": payload.get("record_count", 0),
        "tags": payload.get("tags", []),
    }
    entries.append(entry)
    lineage_path.parent.mkdir(parents=True, exist_ok=True)
    lineage_path.write_text(json.dumps(entries[-500:], indent=2), encoding="utf-8")
    return {"message": "Lineage recorded", "entry": entry}


# Function: get_lineage
@router.get("/data-lineage")
async def get_lineage(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    lineage_path = Path(cfg.DATA_DIR) / "data_lineage.json"
    entries: list = []
    try:
        if lineage_path.exists():
            entries = json.loads(lineage_path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"lineage": entries[-100:], "total": len(entries)}
