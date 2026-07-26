# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — backend/api (predictive.py)
# Date: 2025-08-08
# ---------------------------------------------------------------------------
from __future__ import annotations
import asyncio, json, logging, re, statistics
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Body, Depends, HTTPException
from backend.api.auth import get_current_user
import backend.config as cfg

router = APIRouter(prefix="/api/predictive", tags=["Predictive Analytics"])
logger = logging.getLogger(__name__)
_LLM_TIMEOUT = 90

_PRIORITY_MULT = {"P1": 2.5, "P2": 1.8, "P3": 1.2, "P4": 0.8}


# Function: _call_llm
def _call_llm(system_msg: str, user_msg: str) -> str:
    from langchain_ollama import ChatOllama
    from backend.llm.router import assert_ollama_gpu_available
    assert_ollama_gpu_available(cfg.OLLAMA_MODEL)
    llm = ChatOllama(
        model=cfg.OLLAMA_MODEL, base_url=cfg.OLLAMA_BASE_URL,
        temperature=0.1, num_predict=2048, num_ctx=6144,
        repeat_penalty=1.1, top_k=20, top_p=0.9,
        format="json", timeout=_LLM_TIMEOUT, keep_alive=cfg.OLLAMA_KEEP_ALIVE,
    )
    with ThreadPoolExecutor(max_workers=1) as pool:
        result = pool.submit(llm.invoke, [("system", system_msg), ("human", user_msg)]).result(timeout=_LLM_TIMEOUT)
    return result.content if hasattr(result, "content") else str(result)


# Function: _extract_json
def _extract_json(raw: str) -> dict | list | None:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except Exception:
        pass
    for sc, ec in [('{', '}'), ('[', ']')]:
        s, e = text.find(sc), text.rfind(ec)
        if s >= 0 and e > s:
            try:
                return json.loads(text[s:e+1])
            except Exception:
                pass
    return None


# Function: incident_prediction
@router.post("/incident-prediction")
async def incident_prediction(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    incidents = payload.get("historical_incidents", [])
    horizon = payload.get("prediction_horizon_days", 30)

    from collections import Counter
    cat_counts = Counter(i.get("category", "") for i in incidents)
    heuristic_predictions = [
        {"category": cat, "ci": "Various", "predicted_date_range": f"Next {horizon} days",
         "probability": min(0.9, count / max(len(incidents), 1) * 3),
         "basis": f"Occurred {count} times historically",
         "preventive_action": f"Review and patch systems prone to {cat} issues"}
        for cat, count in cat_counts.most_common(5)
    ]

    incidents_text = "\n".join(
        f"[{i.get('date','')}] {i.get('category','')} | CI:{i.get('ci','')} | {i.get('description','')[:80]}"
        for i in incidents[:50]
    )
    system_msg = (
        "You are an AIOps analyst. Predict likely incidents in the next period based on historical data. "
        "Return JSON: {\"predictions\": [{\"category\": str, \"ci\": str, \"predicted_date_range\": str, "
        "\"probability\": float, \"basis\": str, \"preventive_action\": str}], \"risk_summary\": str}"
    )
    user_msg = f"Horizon: {horizon} days\nHistorical incidents:\n{incidents_text}"
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, user_msg), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed["llm_used"] = True
        parsed.setdefault("predictions", heuristic_predictions)
        parsed.setdefault("risk_summary", "Analysis based on historical patterns.")
        return parsed
    except Exception as exc:
        logger.warning("incident_prediction LLM failed: %s", exc)
        return {"predictions": heuristic_predictions, "risk_summary": "Heuristic analysis.", "llm_used": False}


# Function: _sla_risk_level
def _sla_risk_level(prob: float) -> str:
    return "CRITICAL" if prob > 0.85 else "HIGH" if prob > 0.6 else "MEDIUM" if prob > 0.3 else "LOW"


# Function: _sla_recommended_action
def _sla_recommended_action(risk: str) -> str:
    return {
        "CRITICAL": "Immediate escalation required",
        "HIGH": "Escalate to senior agent",
        "MEDIUM": "Monitor closely",
    }.get(risk, "On track")


# Function: _score_sla_ticket
def _score_sla_ticket(t: dict) -> dict:
    sla_h = max(float(t.get("sla_hours", 8)), 0.1)
    age_h = float(t.get("age_hours", 0))
    mult = _PRIORITY_MULT.get(t.get("priority", "P3"), 1.2)
    ratio = (age_h / sla_h) * mult
    prob = min(0.99, ratio)
    remaining = max(0.0, sla_h - age_h)
    risk = _sla_risk_level(prob)
    return {"id": t.get("id", ""), "breach_probability": round(prob, 3),
            "risk_level": risk, "hours_remaining": round(remaining, 1),
            "recommended_action": _sla_recommended_action(risk)}


# Function: sla_breach
@router.post("/sla-breach")
async def sla_breach(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    tickets = payload.get("tickets", [])

    scored = [_score_sla_ticket(t) for t in tickets]
    at_risk = sum(1 for s in scored if s["risk_level"] in ("CRITICAL", "HIGH"))

    scored.sort(key=lambda x: x["breach_probability"], reverse=True)
    return {"scored_tickets": scored, "at_risk_count": at_risk}


# Function: _change_risk_heuristic
def _change_risk_heuristic(title: str, description: str, cis: list, change_type: str) -> dict:
    score = 0.3
    if change_type == "emergency":
        score += 0.3
    if len(cis) > 5:
        score += 0.2
    if any(w in (title + description).lower() for w in ["database", "production", "core", "auth"]):
        score += 0.2
    score = min(0.99, score)
    level = "CRITICAL" if score > 0.8 else "HIGH" if score > 0.6 else "MEDIUM" if score > 0.35 else "LOW"
    return {"risk_score": round(score, 2), "risk_level": level,
            "impact_summary": f"Change affects {len(cis)} CI(s)", "concerns": [],
            "recommendations": ["Follow CAB approval process", "Test in staging first"],
            "approval_recommendation": "APPROVE WITH CONDITIONS" if score < 0.7 else "ESCALATE TO CAB",
            "llm_used": False}


# Function: change_risk
@router.post("/change-risk")
async def change_risk(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    title = payload.get("change_title", "")
    description = payload.get("change_description", "")
    cis = payload.get("affected_cis", [])
    planned = payload.get("planned_datetime", "")
    change_type = payload.get("change_type", "standard")

    system_msg = (
        "You are a change risk assessor. Evaluate the risk of this ITSM change request. "
        "Return JSON: {\"risk_score\": float (0-1), \"risk_level\": str, \"impact_summary\": str, "
        "\"concerns\": [str], \"recommendations\": [str], \"approval_recommendation\": str}"
    )
    user_msg = (f"Change: {title}\nType: {change_type}\nPlanned: {planned}\n"
                f"Affected CIs: {', '.join(cis)}\nDescription: {description}")
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, user_msg), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed["llm_used"] = True
        h = _change_risk_heuristic(title, description, cis, change_type)
        for k, v in h.items():
            parsed.setdefault(k, v)
        return parsed
    except Exception as exc:
        logger.warning("change_risk LLM failed: %s", exc)
        return _change_risk_heuristic(title, description, cis, change_type)


# Function: _metric_anomaly
def _metric_anomaly(m: dict) -> dict | None:
    value = float(m.get("value", 0))
    baseline = float(m.get("baseline", 1))
    if baseline == 0:
        return None
    dev_pct = abs((value - baseline) / baseline) * 100
    if dev_pct <= 50:
        return None
    sev = "CRITICAL" if dev_pct > 200 else "HIGH" if dev_pct > 100 else "MEDIUM"
    return {"timestamp": m.get("timestamp", ""), "metric_name": m.get("metric_name", ""),
            "value": value, "baseline": baseline,
            "deviation_pct": round(dev_pct, 1), "severity": sev}


# Function: anomaly_detect
@router.post("/anomaly-detect")
async def anomaly_detect(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    metrics = payload.get("metrics", [])

    anomalies = [a for a in (_metric_anomaly(m) for m in metrics) if a is not None]

    narrative = f"Detected {len(anomalies)} anomaly(ies) across {len(metrics)} metrics."
    if anomalies:
        try:
            a_text = "\n".join(f"{a['metric_name']}: {a['value']} vs baseline {a['baseline']} ({a['deviation_pct']}% off)"
                               for a in anomalies[:10])
            sys = "Provide a brief narrative explaining these metric anomalies and their likely cause. Return JSON: {\"narrative\": str}"
            raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, sys, a_text), timeout=60)
            parsed = _extract_json(raw) or {}
            narrative = parsed.get("narrative", narrative)
        except Exception as exc:
            logger.warning("anomaly_detect narrative LLM failed: %s", exc)

    return {"anomalies": anomalies, "narrative": narrative, "llm_used": bool(anomalies)}


# Function: _build_feature_matrix
def _build_feature_matrix(data_points: list[dict], feature_fields: list[str]) -> list[list[float]]:
    matrix = []
    for dp in data_points:
        row = []
        for f in feature_fields:
            try:
                row.append(float(dp.get(f, 0)))
            except (TypeError, ValueError):
                row.append(0.0)
        matrix.append(row)
    return matrix


# Function: _ml_anomaly_isolation_forest
def _ml_anomaly_isolation_forest(data_points: list[dict], contamination: float, feature_fields: list[str]) -> dict:
    import numpy as np
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler

    X_arr = np.array(_build_feature_matrix(data_points, feature_fields))
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_arr)

    clf = IsolationForest(contamination=contamination, random_state=42, n_estimators=100)
    labels = clf.fit_predict(X_scaled)
    scores = clf.decision_function(X_scaled)

    anomalies = []
    for i, (label, score) in enumerate(zip(labels, scores)):
        if label == -1:
            dp = data_points[i]
            anomaly_score = round(float(-score), 4)
            anomalies.append({
                "index": i,
                "timestamp": dp.get("timestamp", ""),
                "features": {f: dp.get(f) for f in feature_fields},
                "anomaly_score": anomaly_score,
                "severity": "HIGH" if anomaly_score > 0.5 else "MEDIUM",
                "algorithm": "IsolationForest",
            })
    return {
        "total_points": len(data_points),
        "anomalies_detected": len(anomalies),
        "contamination_rate": contamination,
        "anomalies": anomalies,
        "algorithm": "IsolationForest",
        "sklearn_used": True,
    }


# Function: _ml_anomaly_statistical_fallback
def _ml_anomaly_statistical_fallback(data_points: list[dict], feature_fields: list[str]) -> dict:
    logger.warning("scikit-learn not available, falling back to statistical anomaly detection")
    values = []
    for dp in data_points:
        try:
            values.append(float(dp.get(feature_fields[0], 0)))
        except Exception:
            values.append(0.0)
    if len(values) < 3:
        return {"total_points": len(data_points), "anomalies_detected": 0, "anomalies": [], "algorithm": "statistical_fallback", "sklearn_used": False}
    mean = statistics.mean(values)
    std = statistics.stdev(values) or 1.0
    threshold = 3.0
    anomalies = []
    for i, (val, dp) in enumerate(zip(values, data_points)):
        z = abs(val - mean) / std
        if z > threshold:
            anomalies.append({
                "index": i,
                "timestamp": dp.get("timestamp", ""),
                "features": {feature_fields[0]: val},
                "anomaly_score": round(z / 6.0, 4),
                "z_score": round(z, 3),
                "severity": "HIGH" if z > 4.0 else "MEDIUM",
                "algorithm": "z_score",
            })
    return {"total_points": len(data_points), "anomalies_detected": len(anomalies), "anomalies": anomalies, "algorithm": "z_score", "sklearn_used": False}


# Function: ml_anomaly_detect
@router.post("/ml-anomaly")
async def ml_anomaly_detect(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    """Isolation Forest-based anomaly detection for numeric metric streams."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    data_points: list[dict] = payload.get("data_points", [])
    contamination: float = float(payload.get("contamination", 0.05))
    feature_fields: list[str] = payload.get("feature_fields", ["value"])

    if not data_points:
        raise HTTPException(status_code=400, detail="data_points required")

    try:
        return _ml_anomaly_isolation_forest(data_points, contamination, feature_fields)
    except ImportError:
        # Fallback to statistical method if scikit-learn not installed
        return _ml_anomaly_statistical_fallback(data_points, feature_fields)


# Function: _compute_failure_score
def _compute_failure_score(cpu: float, mem: float, disk: float, error_rate: float, uptime_pct: float, age_days: float) -> float:
    failure_score = 0.0
    failure_score += min(0.25, (cpu - 70) / 120) if cpu > 70 else 0
    failure_score += min(0.25, (mem - 75) / 100) if mem > 75 else 0
    failure_score += min(0.20, (disk - 80) / 100) if disk > 80 else 0
    failure_score += min(0.15, error_rate / 20)
    failure_score += min(0.10, (100 - uptime_pct) / 50)
    failure_score += min(0.05, age_days / 1825)
    return min(0.99, max(0.0, round(failure_score, 3)))


# Function: _maintenance_actions
def _maintenance_actions(cpu: float, mem: float, disk: float, error_rate: float, uptime_pct: float, age_days: float) -> list:
    actions = []
    if cpu > 85:
        actions.append("Scale or rebalance CPU-intensive workloads")
    if mem > 90:
        actions.append("Investigate memory leaks; consider vertical scaling")
    if disk > 85:
        actions.append("Archive data or expand storage capacity")
    if error_rate > 5:
        actions.append("Investigate and resolve elevated error rate")
    if uptime_pct < 99:
        actions.append("Review restart logs and implement watchdog")
    if age_days > 1095:
        actions.append("Consider hardware refresh — asset over 3 years old")
    return actions


# Function: predictive_maintenance
@router.post("/predictive-maintenance")
async def predictive_maintenance(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    """Predict equipment/service failure probability and MTTR."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    asset_id = payload.get("asset_id", "")
    asset_type = payload.get("asset_type", "server")
    metrics = payload.get("metrics", {})
    incident_history = payload.get("incident_history", [])
    age_days = float(payload.get("age_days", 0))

    cpu = float(metrics.get("cpu_utilization_pct", 0))
    mem = float(metrics.get("memory_utilization_pct", 0))
    disk = float(metrics.get("disk_utilization_pct", 0))
    error_rate = float(metrics.get("error_rate_per_hour", 0))
    uptime_pct = float(metrics.get("uptime_pct_30d", 100))

    failure_score = _compute_failure_score(cpu, mem, disk, error_rate, uptime_pct, age_days)

    inc_count = len(incident_history)
    avg_resolution_hrs = (
        sum(float(i.get("resolution_hours", 4)) for i in incident_history) / inc_count
        if inc_count > 0 else 4.0
    )
    predicted_mttr = round(avg_resolution_hrs * (1 + failure_score), 1)

    risk = "CRITICAL" if failure_score > 0.7 else "HIGH" if failure_score > 0.4 else "MEDIUM" if failure_score > 0.2 else "LOW"
    actions = _maintenance_actions(cpu, mem, disk, error_rate, uptime_pct, age_days)

    system_msg = (
        "You are a predictive maintenance engineer. Predict failure probability and maintenance windows. "
        "Return JSON: {\"failure_probability\": float, \"predicted_failure_window\": str, "
        "\"maintenance_actions\": [str], \"maintenance_window_recommendation\": str, \"confidence\": float}"
    )
    metrics_text = "\n".join(f"{k}: {v}" for k, v in metrics.items())
    history_text = "\n".join(
        f"[{i.get('date','')}] {i.get('type','')} - Resolution: {i.get('resolution_hours',0)}h"
        for i in incident_history[-10:]
    )
    user_msg = f"Asset: {asset_id} ({asset_type}) | Age: {age_days:.0f} days\nMetrics:\n{metrics_text}\nIncident History:\n{history_text}"
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, user_msg), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed["asset_id"] = asset_id
        parsed["asset_type"] = asset_type
        parsed.setdefault("failure_probability", failure_score)
        parsed.setdefault("risk_level", risk)
        parsed.setdefault("predicted_mttr_hours", predicted_mttr)
        parsed.setdefault("maintenance_actions", actions)
        parsed.setdefault("maintenance_window_recommendation", "Schedule maintenance within 7 days" if failure_score > 0.4 else "No immediate maintenance required")
        parsed["heuristic_score"] = failure_score
        parsed["llm_used"] = True
        return parsed
    except Exception as exc:
        logger.warning("predictive_maintenance LLM failed: %s", exc)
        return {
            "asset_id": asset_id,
            "asset_type": asset_type,
            "failure_probability": failure_score,
            "risk_level": risk,
            "predicted_mttr_hours": predicted_mttr,
            "maintenance_actions": actions,
            "maintenance_window_recommendation": "Schedule maintenance within 7 days" if failure_score > 0.4 else "No immediate maintenance required",
            "heuristic_score": failure_score,
            "llm_used": False,
        }
