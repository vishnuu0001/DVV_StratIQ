# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — backend/api (automation_engine.py)
# Date: 2025-08-26
# ---------------------------------------------------------------------------
from __future__ import annotations
import asyncio, json, logging, re
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Body, Depends, HTTPException
from backend.api.auth import get_current_user
import backend.config as cfg

router = APIRouter(prefix="/api/automation", tags=["Automation Engine"])
logger = logging.getLogger(__name__)
_LLM_TIMEOUT = 90

_PLAYBOOKS: dict[str, dict] = {
    "service_restart": {
        "name": "Service Restart", "estimated_mins": 5,
        "automated": ["Stop service", "Clear temp files", "Start service", "Verify health endpoint"],
        "manual": ["Notify stakeholders", "Confirm recovery"],
    },
    "cache_clear": {
        "name": "Cache Clear", "estimated_mins": 3,
        "automated": ["Identify cache location", "Flush cache", "Restart cache service"],
        "manual": ["Verify application behavior post-clear"],
    },
    "disk_cleanup": {
        "name": "Disk Cleanup", "estimated_mins": 15,
        "automated": ["Scan disk usage", "Archive logs older than 30 days", "Remove temp files", "Report freed space"],
        "manual": ["Approve deletion of flagged files"],
    },
    "password_reset": {
        "name": "Password Reset", "estimated_mins": 2,
        "automated": ["Verify user identity", "Generate temp password", "Send via secure channel"],
        "manual": ["Confirm user received credentials"],
    },
    "vpn_reconnect": {
        "name": "VPN Reconnect", "estimated_mins": 5,
        "automated": ["Test VPN endpoint", "Restart VPN client", "Re-authenticate"],
        "manual": ["Verify connectivity from user end"],
    },
    "cert_renewal": {
        "name": "Certificate Renewal", "estimated_mins": 30,
        "automated": ["Generate CSR", "Submit to CA", "Install new cert", "Restart affected services"],
        "manual": ["Approve CSR", "Verify certificate chain"],
    },
    "db_connection_reset": {
        "name": "DB Connection Reset", "estimated_mins": 10,
        "automated": ["Kill idle connections", "Reset connection pool", "Test query execution"],
        "manual": ["Coordinate with DBA", "Validate application DB connectivity"],
    },
    "memory_leak_fix": {
        "name": "Memory Leak Mitigation", "estimated_mins": 20,
        "automated": ["Capture heap dump", "Restart offending process", "Enable GC logging"],
        "manual": ["Analyze heap dump", "Schedule patch deployment"],
    },
    "network_route_reset": {
        "name": "Network Route Reset", "estimated_mins": 10,
        "automated": ["Flush route table", "Re-apply static routes", "Test connectivity"],
        "manual": ["Coordinate with network team", "Validate routing from affected zones"],
    },
    "log_rotation": {
        "name": "Log Rotation", "estimated_mins": 5,
        "automated": ["Compress current logs", "Archive to cold storage", "Reset log file handles"],
        "manual": ["Verify application continues logging correctly"],
    },
}


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


# Function: _heuristic_playbook
def _heuristic_playbook(title: str, category: str, description: str) -> dict:
    text = (title + " " + category + " " + description).lower()
    key = "service_restart"
    if any(w in text for w in ["disk", "storage", "space"]):
        key = "disk_cleanup"
    elif any(w in text for w in ["password", "credential", "account", "locked"]):
        key = "password_reset"
    elif any(w in text for w in ["vpn", "network", "connectivity"]):
        key = "vpn_reconnect"
    elif any(w in text for w in ["certificate", "cert", "ssl", "tls"]):
        key = "cert_renewal"
    elif any(w in text for w in ["database", "db", "connection pool"]):
        key = "db_connection_reset"
    elif any(w in text for w in ["memory", "heap", "oom", "out of memory"]):
        key = "memory_leak_fix"
    elif any(w in text for w in ["cache", "redis", "memcache"]):
        key = "cache_clear"
    elif any(w in text for w in ["log", "rotation"]):
        key = "log_rotation"
    pb = _PLAYBOOKS[key]
    all_steps = pb["automated"] + pb["manual"]
    return {"playbook_name": pb["name"], "playbook_steps": all_steps,
            "automated_steps": pb["automated"], "manual_steps": pb["manual"],
            "estimated_resolution_mins": pb["estimated_mins"], "confidence": 0.6, "llm_used": False}


# Function: map_playbook
@router.post("/map-playbook")
async def map_playbook(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    title = payload.get("incident_title", "")
    category = payload.get("category", "")
    description = payload.get("description", "")
    ci = payload.get("ci", "")

    playbook_list = "\n".join(f"- {v['name']}: {', '.join(v['automated'][:2])}" for v in _PLAYBOOKS.values())
    system_msg = (
        "You are an ITSM automation expert. Map the incident to the most suitable remediation playbook. "
        "Return JSON: {\"playbook_name\": str, \"playbook_steps\": [str], \"automated_steps\": [str], "
        "\"manual_steps\": [str], \"estimated_resolution_mins\": int, \"confidence\": float}"
        f"\nAvailable playbooks:\n{playbook_list}"
    )
    user_msg = f"Incident: {title}\nCategory: {category}\nCI: {ci}\nDescription: {description}"
    try:
        # Outer bound on top of _LLM_TIMEOUT: assert_ollama_gpu_available() inside
        # _call_llm runs before the timed invoke and has its own up-to-120s warm-up
        # path, unbounded by _LLM_TIMEOUT — without this, total latency can exceed
        # IIS/ARR's 2-minute proxy timeout and surface as a 502/500 to the browser.
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, user_msg), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed["llm_used"] = True
        h = _heuristic_playbook(title, category, description)
        for k, v in h.items():
            parsed.setdefault(k, v)
        return parsed
    except Exception as exc:
        logger.warning("map_playbook LLM failed: %s", exc)
        return _heuristic_playbook(title, category, description)


# Function: build_workflow
@router.post("/build-workflow")
async def build_workflow(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    description = payload.get("description", "")
    trigger_event = payload.get("trigger_event", "")
    actions = payload.get("actions", [])

    # Function: _heuristic
    def _heuristic():
        steps = [{"step_num": i+1, "action": a, "target": "System", "parameters": {}, "on_failure": "notify_admin"}
                 for i, a in enumerate(actions)] or [
            {"step_num": 1, "action": "Trigger event handler", "target": "Automation Engine",
             "parameters": {}, "on_failure": "log_and_continue"}
        ]
        return {"workflow_name": "Custom Workflow", "trigger": {"event": trigger_event or "manual", "conditions": []},
                "steps": steps, "notifications": [], "estimated_execution_secs": 30, "llm_used": False}

    system_msg = (
        "You are a workflow automation designer. Convert the natural language description into a structured workflow. "
        "Return JSON: {\"workflow_name\": str, \"trigger\": {\"event\": str, \"conditions\": [str]}, "
        "\"steps\": [{\"step_num\": int, \"action\": str, \"target\": str, \"parameters\": {}, \"on_failure\": str}], "
        "\"notifications\": [{\"channel\": str, \"recipient\": str, \"condition\": str}], "
        "\"estimated_execution_secs\": int}"
    )
    user_msg = f"Description: {description}\nTrigger: {trigger_event}\nRequested actions: {', '.join(actions)}"
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, user_msg), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed["llm_used"] = True
        h = _heuristic()
        for k, v in h.items():
            parsed.setdefault(k, v)
        return parsed
    except Exception as exc:
        logger.warning("build_workflow LLM failed: %s", exc)
        return _heuristic()
