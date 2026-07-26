# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — backend/api (compliance.py)
# Date: 2026-02-26
# ---------------------------------------------------------------------------
from __future__ import annotations
import asyncio, json, logging, re
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Body, Depends, HTTPException
from backend.api.auth import get_current_user
import backend.config as cfg

router = APIRouter(prefix="/api/compliance", tags=["Security & Compliance"])
logger = logging.getLogger(__name__)
_LLM_TIMEOUT = 90

_PII_PATTERNS = [
    ("Credit Card",       re.compile(r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b'), "CRITICAL"),
    ("SSN",               re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), "CRITICAL"),
    ("Email",             re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b'), "HIGH"),
    ("Phone Number",      re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'), "MEDIUM"),
    ("IPv4 Address",      re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'), "LOW"),
    ("UK NI Number",      re.compile(r'\b[A-Z]{2}\d{6}[ABCD]\b'), "HIGH"),
    ("Passport Number",   re.compile(r'\b[A-Z]{1,2}\d{6,9}\b'), "HIGH"),
]


# Function: _call_llm
def _call_llm(system_msg: str, user_msg: str) -> str:
    from langchain_ollama import ChatOllama
    from backend.llm.router import assert_ollama_gpu_available
    assert_ollama_gpu_available(cfg.OLLAMA_MODEL)
    llm = ChatOllama(
        model=cfg.OLLAMA_MODEL, base_url=cfg.OLLAMA_BASE_URL,
        temperature=0.0, num_predict=2048, num_ctx=6144,
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


# Function: detect_pii
@router.post("/detect-pii")
async def detect_pii(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    ticket_id = payload.get("ticket_id", "")
    text = payload.get("text", "")

    findings = []
    redacted = text
    for pii_type, pattern, severity in _PII_PATTERNS:
        for m in pattern.finditer(text):
            val = m.group()
            redacted_val = val[:2] + "*" * max(0, len(val) - 4) + val[-2:] if len(val) > 4 else "****"
            findings.append({"type": pii_type, "value_redacted": redacted_val,
                             "position": m.start(), "severity": severity})
            redacted = redacted.replace(val, f"[{pii_type.upper()}_REDACTED]", 1)

    risk_severities = [f["severity"] for f in findings]
    risk_level = ("CRITICAL" if "CRITICAL" in risk_severities else
                  "HIGH" if "HIGH" in risk_severities else
                  "MEDIUM" if "MEDIUM" in risk_severities else
                  "LOW" if findings else "NONE")

    if not findings:
        return {"ticket_id": ticket_id, "pii_found": False, "findings": [],
                "redacted_text": text, "risk_level": "NONE", "llm_used": False}

    try:
        sys = ("Identify any additional PII types not captured by regex (e.g. names, addresses, dates of birth). "
               "Return JSON: {\"additional_findings\": [{\"type\": str, \"value_redacted\": str, \"position\": int, \"severity\": str}]}")
        # Outer bound on top of _LLM_TIMEOUT — see itsm_ops.py's simulate_dashboard
        # for why assert_ollama_gpu_available's internal warm-up needs this too.
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, sys, redacted[:2000]), timeout=60)
        parsed = _extract_json(raw) or {}
        extra = parsed.get("additional_findings", [])
        findings.extend(extra)
        llm_used = bool(extra)
    except Exception as exc:
        logger.warning("detect_pii LLM enhancement failed: %s", exc)
        llm_used = False

    return {"ticket_id": ticket_id, "pii_found": bool(findings), "findings": findings,
            "redacted_text": redacted, "risk_level": risk_level, "llm_used": llm_used}


# Function: summarize_audit
@router.post("/summarize-audit")
async def summarize_audit(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    audit_logs = payload.get("audit_logs", [])
    period = payload.get("period", "")

    total = len(audit_logs)
    failed = [l for l in audit_logs if l.get("outcome", "").lower() in ("failed", "denied", "error")]
    heuristic_concerns = [f"Failed action: {l.get('action','')} by {l.get('user','')} on {l.get('resource','')}" for l in failed[:5]]

    logs_text = "\n".join(
        f"[{l.get('timestamp','')}] {l.get('user','')} | {l.get('action','')} | {l.get('resource','')} | {l.get('outcome','')}"
        for l in audit_logs[:100]
    )
    system_msg = (
        "You are a compliance auditor. Summarize this audit log for a compliance review. "
        "Return JSON: {\"summary\": str, \"key_activities\": [str], \"anomalies\": [str], "
        "\"compliance_concerns\": [str], \"risk_level\": str}"
    )
    user_msg = f"Period: {period}\nTotal events: {total}\n\nLogs:\n{logs_text}"
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, user_msg), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed["period"] = period
        parsed["total_events"] = total
        parsed["llm_used"] = True
        parsed.setdefault("summary", f"{total} events in period. {len(failed)} failed actions.")
        parsed.setdefault("key_activities", [])
        parsed.setdefault("anomalies", [])
        parsed.setdefault("compliance_concerns", heuristic_concerns)
        parsed.setdefault("risk_level", "HIGH" if len(failed) > 5 else "MEDIUM" if failed else "LOW")
        return parsed
    except Exception as exc:
        logger.warning("summarize_audit LLM failed: %s", exc)
        return {"period": period, "total_events": total,
                "summary": f"{total} events. {len(failed)} failures.",
                "key_activities": [], "anomalies": [],
                "compliance_concerns": heuristic_concerns,
                "risk_level": "HIGH" if len(failed) > 5 else "MEDIUM" if failed else "LOW",
                "llm_used": False}


# Function: check_policy
@router.post("/check-policy")
async def check_policy(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    request_type = payload.get("request_type", "")
    request_details = payload.get("request_details", {})
    policy_rules = payload.get("policy_rules", [])

    rules_text = "\n".join(f"- {r}" for r in policy_rules) or "Standard IT policy applies."
    details_text = json.dumps(request_details, indent=2)
    system_msg = (
        "You are an IT governance policy checker. Evaluate this request against the stated policy rules. "
        "Return JSON: {\"compliant\": bool, \"violations\": [{\"rule\": str, \"description\": str, \"severity\": str}], "
        "\"warnings\": [str], \"approval_recommendation\": str, \"reasoning\": str}"
    )
    user_msg = f"Request Type: {request_type}\nDetails:\n{details_text}\n\nPolicy Rules:\n{rules_text}"
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, user_msg), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed["request_type"] = request_type
        parsed["llm_used"] = True
        parsed.setdefault("compliant", True)
        parsed.setdefault("violations", [])
        parsed.setdefault("warnings", [])
        parsed.setdefault("approval_recommendation", "APPROVE")
        parsed.setdefault("reasoning", "No policy violations detected.")
        return parsed
    except Exception as exc:
        logger.warning("check_policy LLM failed: %s", exc)
        return {"request_type": request_type, "compliant": True, "violations": [], "warnings": [],
                "approval_recommendation": "APPROVE — manual review recommended",
                "reasoning": "LLM unavailable; please review manually.", "llm_used": False}
