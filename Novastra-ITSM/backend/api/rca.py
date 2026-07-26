# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — backend/api (rca.py)
# Date: 2025-11-21
# ---------------------------------------------------------------------------
from __future__ import annotations
import asyncio, json, logging, re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Body, Depends, HTTPException
from backend.api.auth import get_current_user
import backend.config as cfg

router = APIRouter(prefix="/api/rca", tags=["Root Cause Analysis"])
logger = logging.getLogger(__name__)
_LLM_TIMEOUT = 90


# Function: _call_llm
def _call_llm(system_msg: str, user_msg: str) -> str:
    from langchain_ollama import ChatOllama
    from backend.llm.router import assert_ollama_gpu_available
    assert_ollama_gpu_available(cfg.OLLAMA_MODEL)
    llm = ChatOllama(
        model=cfg.OLLAMA_MODEL, base_url=cfg.OLLAMA_BASE_URL,
        temperature=0.1, num_predict=3072, num_ctx=6144,
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


# Function: generate_rca
@router.post("/generate")
async def generate_rca(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    incident_id = payload.get("incident_id", "")
    title = payload.get("title", "")
    description = payload.get("description", "")
    timeline = payload.get("timeline", [])
    affected_services = payload.get("affected_services", [])
    related_changes = payload.get("related_changes", [])

    timeline_text = "\n".join(f"[{e.get('timestamp','')}] ({e.get('source','')}) {e.get('event','')}" for e in timeline)
    system_msg = (
        "You are an ITSM Root Cause Analysis expert. Generate a structured RCA document. "
        "Return JSON: {\"executive_summary\": str, \"probable_cause\": str, "
        "\"contributing_factors\": [str], \"timeline_analysis\": str, "
        "\"impact_assessment\": str, \"preventive_actions\": [str], \"rca_markdown\": str}"
    )
    user_msg = (
        f"Incident ID: {incident_id}\nTitle: {title}\nDescription: {description}\n"
        f"Affected Services: {', '.join(affected_services)}\nRelated Changes: {', '.join(related_changes)}\n"
        f"Timeline:\n{timeline_text}"
    )

    # Function: _heuristic
    def _heuristic():
        return {
            "incident_id": incident_id,
            "executive_summary": f"Incident {incident_id}: {title}. Investigation identified probable systemic causes.",
            "probable_cause": "To be determined through further investigation.",
            "contributing_factors": ["Insufficient monitoring", "Lack of redundancy"],
            "timeline_analysis": timeline_text or "No timeline data provided.",
            "impact_assessment": f"Affected services: {', '.join(affected_services) or 'Unknown'}",
            "preventive_actions": ["Implement automated monitoring", "Review change management process"],
            "rca_markdown": f"# RCA: {title}\n\n**Incident ID:** {incident_id}\n\n## Timeline\n{timeline_text}",
            "llm_used": False,
        }

    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, user_msg), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed["incident_id"] = incident_id
        parsed["llm_used"] = True
        h = _heuristic()
        for k, v in h.items():
            parsed.setdefault(k, v)
        return parsed
    except Exception as exc:
        logger.warning("generate_rca LLM failed: %s", exc)
        return _heuristic()


# Function: find_patterns
@router.post("/find-patterns")
async def find_patterns(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    incidents = payload.get("incidents", [])

    clusters_map: dict[str, list] = defaultdict(list)
    for inc in incidents:
        key = f"{inc.get('category','General')}::{inc.get('ci','Unknown')}"
        clusters_map[key].append(inc.get("id", ""))

    heuristic_clusters = [
        {"cluster_name": key.replace("::", " - "), "incident_ids": ids,
         "pattern_description": f"Recurring {key.split('::')[0]} issues on {key.split('::')[1]}",
         "frequency": len(ids), "systemic_issue": "Root cause not yet identified",
         "recommended_fix": "Investigate and address recurring pattern"}
        for key, ids in sorted(clusters_map.items(), key=lambda x: -len(x[1]))[:10]
    ]

    incidents_text = "\n".join(
        f"ID:{i.get('id','')} [{i.get('category','')}] CI:{i.get('ci','')} {i.get('date','')} | {i.get('title','')[:60]}"
        for i in incidents[:60]
    )
    system_msg = (
        "You are an incident pattern analyst. Cluster incidents to identify systemic issues. "
        "Return JSON: {\"clusters\": [{\"cluster_name\": str, \"incident_ids\": [str], "
        "\"pattern_description\": str, \"frequency\": int, \"systemic_issue\": str, "
        "\"recommended_fix\": str}]}"
    )
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, incidents_text), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed["total_incidents"] = len(incidents)
        parsed["llm_used"] = True
        parsed.setdefault("clusters", heuristic_clusters)
        return parsed
    except Exception as exc:
        logger.warning("find_patterns LLM failed: %s", exc)
        return {"clusters": heuristic_clusters, "total_incidents": len(incidents), "llm_used": False}
