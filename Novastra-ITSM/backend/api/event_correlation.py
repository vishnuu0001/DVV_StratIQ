# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — backend/api (event_correlation.py)
# Date: 2026-03-18
# ---------------------------------------------------------------------------
from __future__ import annotations
import asyncio, json, logging, re
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from fastapi import APIRouter, Body, Depends, HTTPException
from backend.api.auth import get_current_user
import backend.config as cfg

router = APIRouter(prefix="/api/events", tags=["Event Correlation"])
logger = logging.getLogger(__name__)
_LLM_TIMEOUT = 90


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


# Function: _parse_ts
def _parse_ts(ts: str) -> datetime | None:
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            return datetime.strptime(ts.strip(), fmt)
        except Exception:
            pass
    return None


# Function: _correlate_by_window
def _correlate_by_window(events: list[dict], window_minutes: int) -> list[dict]:
    """Group events that fall within `window_minutes` of each other."""
    if not events:
        return []
    parsed = []
    for ev in events:
        ts = _parse_ts(ev.get("timestamp", ""))
        if ts:
            parsed.append((ts, ev))
    parsed.sort(key=lambda x: x[0])

    groups: list[list[dict]] = []
    if not parsed:
        return []

    current_group = [parsed[0][1]]
    group_start = parsed[0][0]

    for ts, ev in parsed[1:]:
        if (ts - group_start).total_seconds() <= window_minutes * 60:
            current_group.append(ev)
        else:
            groups.append(current_group)
            current_group = [ev]
            group_start = ts
    groups.append(current_group)

    correlations = []
    for grp in groups:
        if len(grp) < 2:
            continue
        cis = list({e.get("ci", "Unknown") for e in grp if e.get("ci")})
        services = list({e.get("service", "") for e in grp if e.get("service")})
        severities = [e.get("severity", "LOW") for e in grp]
        top_sev = "CRITICAL" if "CRITICAL" in severities else "HIGH" if "HIGH" in severities else "MEDIUM"
        correlations.append({
            "group_id": f"CG-{len(correlations)+1:03d}",
            "event_count": len(grp),
            "event_ids": [e.get("id", e.get("event_id", "")) for e in grp],
            "timespan_minutes": round((
                _parse_ts(grp[-1].get("timestamp", "")) - _parse_ts(grp[0].get("timestamp", ""))
            ).total_seconds() / 60, 1) if len(grp) > 1 else 0,
            "affected_cis": cis[:5],
            "affected_services": services[:5],
            "correlation_type": "temporal",
            "peak_severity": top_sev,
            "likely_root_cause": f"Correlated {len(grp)} events affecting {', '.join(cis[:2]) or 'multiple systems'}",
        })
    return correlations


# Function: _detect_storms
def _detect_storms(events: list[dict], threshold: int = 5, window_minutes: int = 5) -> list[dict]:
    """Detect event storms: >threshold events in window_minutes."""
    if not events:
        return []
    parsed = [((_parse_ts(ev.get("timestamp", "")) or datetime.min), ev) for ev in events]
    parsed.sort(key=lambda x: x[0])
    storms = []
    checked = set()
    for i, (ts, ev) in enumerate(parsed):
        if i in checked:
            continue
        window_end = ts + timedelta(minutes=window_minutes)
        members = [j for j, (t2, _) in enumerate(parsed) if ts <= t2 <= window_end]
        if len(members) >= threshold:
            storms.append({
                "storm_id": f"STORM-{len(storms)+1:03d}",
                "start_time": ts.isoformat(),
                "end_time": parsed[members[-1]][0].isoformat(),
                "event_count": len(members),
                "events": [parsed[j][1].get("id", "") for j in members[:10]],
                "cis": list({parsed[j][1].get("ci", "") for j in members if parsed[j][1].get("ci")})[:5],
                "description": f"Event storm: {len(members)} events in {window_minutes} minutes",
            })
            checked.update(members)
    return storms


# Function: correlate_events
@router.post("/correlate")
async def correlate_events(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    events = payload.get("events", [])
    window_minutes = int(payload.get("window_minutes", 15))
    detect_storms = payload.get("detect_storms", True)

    correlations = _correlate_by_window(events, window_minutes)
    storms = _detect_storms(events) if detect_storms else []

    ci_counts = Counter(e.get("ci", "Unknown") for e in events if e.get("ci"))
    hotspots = [{"ci": ci, "event_count": cnt} for ci, cnt in ci_counts.most_common(5)]

    if correlations and events:
        events_text = "\n".join(
            f"[{e.get('timestamp','')}] {e.get('type','')} CI:{e.get('ci','')} {e.get('message','')[:60]}"
            for e in events[:40]
        )
        system_msg = (
            "You are an AIOps event correlation analyst. Analyze the events and identify causal chains. "
            "Return JSON: {\"causal_chains\": [{\"chain_id\": str, \"root_event\": str, \"downstream_events\": [str], \"hypothesis\": str}], "
            "\"narrative\": str, \"recommended_action\": str}"
        )
        try:
            raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, events_text), timeout=60)
            llm_result = _extract_json(raw) or {}
            llm_used = True
        except Exception as exc:
            logger.warning("correlate LLM failed: %s", exc)
            llm_result = {}
            llm_used = False
    else:
        llm_result = {}
        llm_used = False

    return {
        "total_events": len(events),
        "correlations": correlations,
        "storms": storms,
        "hotspot_cis": hotspots,
        "causal_chains": llm_result.get("causal_chains", []),
        "narrative": llm_result.get("narrative", f"Identified {len(correlations)} correlation group(s) across {len(events)} events."),
        "recommended_action": llm_result.get("recommended_action", "Investigate correlated events as a single incident."),
        "llm_used": llm_used,
    }


# Function: build_timeline
@router.post("/timeline")
async def build_timeline(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    events = payload.get("events", [])
    incident_id = payload.get("incident_id", "")

    parsed = []
    for ev in events:
        ts = _parse_ts(ev.get("timestamp", ""))
        if ts:
            parsed.append((ts, ev))
    parsed.sort(key=lambda x: x[0])

    timeline = []
    for i, (ts, ev) in enumerate(parsed):
        severity = ev.get("severity", "LOW")
        timeline.append({
            "seq": i + 1,
            "timestamp": ts.isoformat(),
            "event_id": ev.get("id", ev.get("event_id", f"EV-{i+1}")),
            "type": ev.get("type", ""),
            "ci": ev.get("ci", ""),
            "service": ev.get("service", ""),
            "message": ev.get("message", ""),
            "severity": severity,
            "marker": "CRITICAL" if severity in ("CRITICAL", "HIGH") else None,
        })

    span_minutes = 0
    if len(parsed) > 1:
        span_minutes = round((parsed[-1][0] - parsed[0][0]).total_seconds() / 60, 1)

    return {
        "incident_id": incident_id,
        "timeline": timeline,
        "total_events": len(timeline),
        "timespan_minutes": span_minutes,
        "first_event": parsed[0][0].isoformat() if parsed else None,
        "last_event": parsed[-1][0].isoformat() if parsed else None,
    }


# Function: impact_blast_radius
@router.post("/impact-blast-radius")
async def impact_blast_radius(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    root_ci = payload.get("root_ci", "")
    cmdb_relationships = payload.get("relationships", [])
    events = payload.get("recent_events", [])

    affected_cis: set[str] = {root_ci}
    for rel in cmdb_relationships:
        if rel.get("source") == root_ci or rel.get("target") == root_ci:
            affected_cis.add(rel.get("source", ""))
            affected_cis.add(rel.get("target", ""))
    affected_cis.discard("")
    affected_cis.discard(root_ci)

    recent_on_ci = [e for e in events if e.get("ci") in affected_cis]
    severity_scores = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    blast_score = sum(severity_scores.get(e.get("severity", "LOW"), 1) for e in recent_on_ci)
    blast_level = "CRITICAL" if blast_score > 15 else "HIGH" if blast_score > 8 else "MEDIUM" if blast_score > 3 else "LOW"

    return {
        "root_ci": root_ci,
        "directly_affected_cis": list(affected_cis)[:20],
        "affected_ci_count": len(affected_cis),
        "recent_events_on_affected_cis": len(recent_on_ci),
        "blast_score": blast_score,
        "blast_level": blast_level,
        "summary": f"Root CI '{root_ci}' has blast radius affecting {len(affected_cis)} dependent CIs.",
    }
