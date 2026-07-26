# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — backend/api (reports.py)
# Date: 2026-01-25
# ---------------------------------------------------------------------------
from __future__ import annotations
import asyncio, json, logging, re
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Body, Depends, HTTPException
from backend.api.auth import get_current_user
import backend.config as cfg

router = APIRouter(prefix="/api/reports", tags=["Reports & Insights"])
logger = logging.getLogger(__name__)
_LLM_TIMEOUT = 90


# Function: _call_llm
def _call_llm(system_msg: str, user_msg: str) -> str:
    from langchain_ollama import ChatOllama
    from backend.llm.router import assert_ollama_gpu_available
    assert_ollama_gpu_available(cfg.OLLAMA_MODEL)
    llm = ChatOllama(
        model=cfg.OLLAMA_MODEL, base_url=cfg.OLLAMA_BASE_URL,
        temperature=0.2, num_predict=3072, num_ctx=6144,
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


# Function: generate_report
@router.post("/generate")
async def generate_report(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    report_type = payload.get("report_type", "Weekly Summary")
    date_range = payload.get("date_range", "")
    metrics = payload.get("metrics", {})
    filters = payload.get("filters", {})

    metrics_text = "\n".join(f"- {k}: {v}" for k, v in metrics.items())
    system_msg = (
        "You are an executive report writer for IT operations. Generate a professional narrative report. "
        "Return JSON: {\"report_title\": str, \"period\": str, \"executive_summary\": str, "
        "\"sections\": [{\"heading\": str, \"content\": str}], "
        "\"key_findings\": [str], \"recommendations\": [str], \"report_markdown\": str}"
    )
    user_msg = f"Report Type: {report_type}\nPeriod: {date_range}\nMetrics:\n{metrics_text}\nFilters: {json.dumps(filters)}"

    # Function: _heuristic
    def _heuristic():
        md = f"# {report_type}\n**Period:** {date_range}\n\n## Metrics\n{metrics_text}"
        return {"report_title": report_type, "period": date_range,
                "executive_summary": f"{report_type} for {date_range}.",
                "sections": [{"heading": "Metrics Overview", "content": metrics_text}],
                "key_findings": [], "recommendations": [],
                "report_markdown": md, "llm_used": False}

    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, user_msg), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed["llm_used"] = True
        h = _heuristic()
        for k, v in h.items():
            parsed.setdefault(k, v)
        return parsed
    except Exception as exc:
        logger.warning("generate_report LLM failed: %s", exc)
        return _heuristic()


# Function: narrate_trend
@router.post("/narrate-trend")
async def narrate_trend(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    metric_name = payload.get("metric_name", "")
    current_value = float(payload.get("current_value", 0))
    previous_value = float(payload.get("previous_value", 0))
    unit = payload.get("unit", "")
    context = payload.get("context", {})

    change_pct = round(((current_value - previous_value) / max(abs(previous_value), 0.001)) * 100, 1)
    direction = "increased" if change_pct > 0 else "decreased" if change_pct < 0 else "unchanged"

    system_msg = (
        "You are a business intelligence analyst. Narrate what this metric movement means and what to do about it. "
        "Return JSON: {\"narrative\": str, \"contributing_factors\": [str], \"recommended_actions\": [str]}"
    )
    user_msg = (f"Metric: {metric_name} ({unit})\nCurrent: {current_value}\nPrevious: {previous_value}\n"
                f"Change: {change_pct}% ({direction})\nContext: {json.dumps(context)}")
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, user_msg), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed["metric_name"] = metric_name
        parsed["current_value"] = current_value
        parsed["previous_value"] = previous_value
        parsed["change_pct"] = change_pct
        parsed["direction"] = direction
        parsed["llm_used"] = True
        parsed.setdefault("narrative", f"{metric_name} has {direction} by {abs(change_pct)}%.")
        parsed.setdefault("contributing_factors", [])
        parsed.setdefault("recommended_actions", [])
        return parsed
    except Exception as exc:
        logger.warning("narrate_trend LLM failed: %s", exc)
        return {"metric_name": metric_name, "current_value": current_value, "previous_value": previous_value,
                "change_pct": change_pct, "direction": direction,
                "narrative": f"{metric_name} has {direction} by {abs(change_pct)}%.",
                "contributing_factors": [], "recommended_actions": [], "llm_used": False}


# Function: _metric_avg
def _metric_avg(lst):
    return round(sum(lst) / len(lst), 2) if lst else None


# Function: _metric_median
def _metric_median(lst):
    s = sorted(lst)
    n = len(s)
    return round((s[n // 2] + s[(n - 1) // 2]) / 2, 2) if s else None


# Function: _metric_pct
def _metric_pct(val, total):
    return round(val / total * 100, 1) if total else 0


# Function: _accumulate_ticket_metrics
def _accumulate_ticket_metrics(tickets: list[dict]) -> tuple[list, list, int, int, dict, dict]:
    acknowledged, resolved, first_contact, sla_met, by_priority, by_category = [], [], 0, 0, {}, {}
    for t in tickets:
        priority = t.get("priority", "P3")
        category = t.get("category", "Other")
        by_priority[priority] = by_priority.get(priority, 0) + 1
        by_category[category] = by_category.get(category, 0) + 1

        ack_hrs = t.get("time_to_acknowledge_hours")
        res_hrs = t.get("time_to_resolve_hours")
        is_fcr = t.get("first_contact_resolution", False)
        sla_ok = t.get("sla_met", None)

        if ack_hrs is not None:
            try:
                acknowledged.append(float(ack_hrs))
            except (TypeError, ValueError):
                pass
        if res_hrs is not None:
            try:
                resolved.append(float(res_hrs))
            except (TypeError, ValueError):
                pass
        if is_fcr:
            first_contact += 1
        if sla_ok is True:
            sla_met += 1

    return acknowledged, resolved, first_contact, sla_met, by_priority, by_category


# Function: _compute_sla_by_priority
def _compute_sla_by_priority(tickets: list[dict], by_priority: dict) -> dict:
    sla_targets = {"P1": 4, "P2": 8, "P3": 24, "P4": 72}
    sla_by_priority = {}
    for priority, count in by_priority.items():
        prio_tickets = [t for t in tickets if t.get("priority") == priority]
        prio_met = sum(1 for t in prio_tickets if t.get("sla_met") is True)
        sla_by_priority[priority] = {
            "count": count,
            "sla_met": prio_met,
            "sla_rate_pct": _metric_pct(prio_met, count),
            "target_hours": sla_targets.get(priority, 24),
        }
    return sla_by_priority


# Function: itsm_metrics
@router.post("/itsm-metrics")
async def itsm_metrics(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    """Compute MTTA, MTTR, FCR, SLA compliance and other ITSM KPIs from raw ticket data."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    tickets: list[dict] = payload.get("tickets", [])
    period_label: str = payload.get("period_label", "")
    if not tickets:
        raise HTTPException(status_code=400, detail="tickets list is required")

    total = len(tickets)
    acknowledged, resolved, first_contact, sla_met, by_priority, by_category = _accumulate_ticket_metrics(tickets)

    mtta = _metric_avg(acknowledged)
    mttr = _metric_avg(resolved)
    median_ttr = _metric_median(resolved)
    fcr_rate = _metric_pct(first_contact, total)
    sla_rate = _metric_pct(sla_met, total)

    sla_by_priority = _compute_sla_by_priority(tickets, by_priority)

    metrics = {
        "period": period_label,
        "total_tickets": total,
        "mtta_hours": mtta,
        "mttr_hours": mttr,
        "median_ttr_hours": median_ttr,
        "fcr_rate_pct": fcr_rate,
        "sla_compliance_pct": sla_rate,
        "tickets_resolved": len(resolved),
        "tickets_with_acknowledgement": len(acknowledged),
        "sla_by_priority": sla_by_priority,
        "by_category": by_category,
        "by_priority": by_priority,
    }

    system_msg = (
        "You are an IT operations analyst. Interpret these ITSM KPIs and provide strategic insights. "
        "Return JSON: {\"health_score\": int (0-100), \"trend\": str, \"key_insights\": [str], "
        "\"improvement_areas\": [str], \"narrative\": str}"
    )
    kpi_text = (f"Period: {period_label} | Total: {total}\n"
                f"MTTA: {mtta}h | MTTR: {mttr}h | FCR: {fcr_rate}% | SLA: {sla_rate}%")
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, kpi_text), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed.update(metrics)
        parsed.setdefault("health_score", max(0, min(100, int(sla_rate * 0.4 + fcr_rate * 0.3 + (1 - min(1, (mttr or 24) / 24)) * 30))))
        parsed["llm_used"] = True
        return parsed
    except Exception as exc:
        logger.warning("itsm_metrics LLM failed: %s", exc)
        health = max(0, min(100, int(sla_rate * 0.4 + fcr_rate * 0.3 + (1 - min(1, (mttr or 24) / 24)) * 30)))
        return {**metrics, "health_score": health, "key_insights": [], "improvement_areas": [], "llm_used": False}
