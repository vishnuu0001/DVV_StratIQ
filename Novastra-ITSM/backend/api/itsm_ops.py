# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: ITSM Operations Dashboard — real-time KPI APIs with synthetic data simulation.
# Date: 2025-08-20
# ---------------------------------------------------------------------------
"""
ITSM Operations Dashboard — real-time KPI APIs with synthetic data simulation.

KPIs: MTTA, MTTR, SLA compliance, FCR, Reopen rate, Backlog aging,
      Change success rate, Incident volume by service, Top recurring problems.

Every number shown on the dashboard is derived from ONE synthetic ticket
population (and one change population) generated per scenario/refresh and
cached server-side in _STATE. KPI cards, the per-service bars, the recurring
problems list and the backlog table are all aggregations of that same
population, so they reconcile with each other and are drillable down to the
individual ticket record that produced them (see /tickets and /tickets/{id}).
"""
from __future__ import annotations
import asyncio, json, logging, random, re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from statistics import mean

from fastapi import APIRouter, Body, Depends, HTTPException
from backend.api.auth import get_current_user
import backend.config as cfg

router = APIRouter(prefix="/api/itsm-ops", tags=["ITSM Operations Dashboard"])
logger = logging.getLogger(__name__)
_LLM_TIMEOUT = 90

SERVICES = [
    "SAP ERP", "ServiceNow", "Office 365", "Azure AD", "Oracle DB",
    "SAP BW / BI", "Network Infra", "VPN Gateway", "Print Services", "Storage / SAN",
    "Active Directory", "JIRA / Confluence",
]
SERVICE_WEIGHTS = [18, 6, 14, 10, 9, 7, 8, 9, 5, 5, 6, 3]

PROBLEM_CATEGORIES = [
    "Password Reset / Lockout", "VPN Connectivity", "SAP Login Issues", "Printer Offline",
    "Email Delivery Failure", "Slow System Performance", "Access Denied / Permission",
    "Software Installation", "Data Sync Failure", "Backup Job Failure",
    "MFA / 2FA Issues", "Certificate Expiry",
]
PROBLEM_WEIGHTS = [16, 11, 9, 8, 10, 9, 7, 6, 6, 5, 7, 6]
KNOWN_ERROR_CATEGORIES = {
    "Password Reset / Lockout", "VPN Connectivity", "Certificate Expiry",
    "MFA / 2FA Issues", "Backup Job Failure",
}

PRIORITIES = ["P1", "P2", "P3", "P4"]
PRIORITY_WEIGHTS = [4, 14, 47, 35]
SLA_TARGET_HOURS = {"P1": 4, "P2": 8, "P3": 24, "P4": 72}
ASSIGNEES = ["L1-Team", "L2-SAP", "L2-Network", "L2-Database", "L3-Platform", "Unassigned"]
CHANGE_TYPES = ["Standard", "Normal", "Emergency"]
CHANGE_TYPE_WEIGHTS = [55, 35, 10]

# Scenario profiles bias the *generation* of the population so every derived
# KPI naturally lands in the right band, rather than overwriting aggregates
# after the fact (which is what made the old numbers inconsistent).
SCENARIO_PROFILES = {
    "normal":   dict(resolved_frac=0.66, fcr=0.65, reopen=0.08, mtta_mean=2.0,  mttr_mean=12.0, change_success=0.90, backlog_age_mean=28),
    "good":     dict(resolved_frac=0.80, fcr=0.85, reopen=0.03, mtta_mean=0.8,  mttr_mean=4.5,  change_success=0.97, backlog_age_mean=10),
    "degraded": dict(resolved_frac=0.60, fcr=0.45, reopen=0.18, mtta_mean=4.5,  mttr_mean=22.0, change_success=0.80, backlog_age_mean=55),
    "critical": dict(resolved_frac=0.45, fcr=0.28, reopen=0.32, mtta_mean=10.0, mttr_mean=55.0, change_success=0.65, backlog_age_mean=110),
}

# Server-side cache of the last-generated population, so every read endpoint
# (and the drill-down endpoints) aggregate the SAME tickets that produced the
# numbers currently on screen, instead of re-randomizing independently.
_STATE: dict = {"scenario": None, "tickets": None, "changes": None, "generated_at": None}


# Function: _weighted_choice
def _weighted_choice(r: random.Random, items: list, weights: list):
    return r.choices(items, weights=weights, k=1)[0]


# Function: _make_ticket
def _make_ticket(r: random.Random, i: int, now: datetime, profile: dict) -> dict:
    service = _weighted_choice(r, SERVICES, SERVICE_WEIGHTS)
    category = _weighted_choice(r, PROBLEM_CATEGORIES, PROBLEM_WEIGHTS)
    priority = _weighted_choice(r, PRIORITIES, PRIORITY_WEIGHTS)

    resolved = r.random() < profile["resolved_frac"]
    resolved_at = None
    resolve_hours = None
    sla_breached = None
    first_contact_resolved = None
    reopened = False

    if resolved:
        # Resolved tickets are spread uniformly across the reporting window.
        created_at = now - timedelta(hours=r.uniform(0.1, 30 * 24))
        mtta_hours = max(0.05, r.gauss(profile["mtta_mean"], profile["mtta_mean"] * 0.5))
        resolve_hours = max(mtta_hours + 0.1, abs(r.gauss(profile["mttr_mean"], profile["mttr_mean"] * 0.6)))
        resolved_at = created_at + timedelta(hours=resolve_hours)
        if resolved_at > now:
            resolved_at = now
            resolve_hours = max(0.1, (resolved_at - created_at).total_seconds() / 3600)
        sla_breached = resolve_hours > SLA_TARGET_HOURS[priority]
        first_contact_resolved = r.random() < profile["fcr"]
        reopened = r.random() < profile["reopen"]
        status = r.choice(["Resolved", "Closed"])
    else:
        # Backlog age is drawn from a scenario-tuned exponential distribution
        # (most open tickets are recent, with a long tail of aged/stuck ones)
        # rather than uniformly across the whole 30-day window — a uniform
        # draw would make the average backlog age ~360h regardless of scenario.
        age_hours = min(30 * 24, r.expovariate(1 / profile["backlog_age_mean"]))
        created_at = now - timedelta(hours=age_hours)
        mtta_hours = max(0.05, r.gauss(profile["mtta_mean"], profile["mtta_mean"] * 0.5))
        status = r.choice(["Open", "In Progress", "Awaiting Info"])

    acknowledged_at = min(now, created_at + timedelta(hours=mtta_hours))

    return {
        "id": f"INC{2024000 + i}",
        "service": service,
        "category": category,
        "priority": priority,
        "status": status,
        "resolved": resolved,
        "created_at": created_at,
        "acknowledged_at": acknowledged_at,
        "resolved_at": resolved_at,
        "mtta_hours": round(mtta_hours, 2),
        "resolve_hours": round(resolve_hours, 2) if resolve_hours is not None else None,
        "sla_breached": sla_breached,
        "first_contact_resolved": first_contact_resolved,
        "reopened": reopened,
        "known_error": category in KNOWN_ERROR_CATEGORIES,
        "assignee": r.choice(ASSIGNEES),
        "summary": category,
    }


# Function: _make_changes
def _make_changes(r: random.Random, profile: dict, now: datetime) -> list[dict]:
    n = r.randint(30, 90)
    changes = []
    for i in range(1, n + 1):
        service = _weighted_choice(r, SERVICES, SERVICE_WEIGHTS)
        ctype = _weighted_choice(r, CHANGE_TYPES, CHANGE_TYPE_WEIGHTS)
        success = r.random() < profile["change_success"]
        status = "Success" if success else r.choice(["Failed", "Rolled Back"])
        implemented_at = now - timedelta(hours=r.uniform(0.5, 30 * 24))
        changes.append({
            "id": f"CHG{3024000 + i}",
            "service": service,
            "type": ctype,
            "status": status,
            "implemented_at": implemented_at.isoformat() + "Z",
            "summary": f"{ctype} change — {service}",
        })
    return changes


# Function: _ticket_age_hours
def _ticket_age_hours(t: dict, now: datetime) -> float:
    if t["resolved"]:
        return t["resolve_hours"]
    return round((now - t["created_at"]).total_seconds() / 3600, 1)


# Function: _ticket_risk
def _ticket_risk(age_hours: float | None) -> str | None:
    if age_hours is None:
        return None
    if age_hours > 120: return "Critical"
    if age_hours > 72:  return "High"
    if age_hours > 24:  return "Medium"
    return "Low"


# Function: _public_ticket
def _public_ticket(t: dict, now: datetime) -> dict:
    age_hours = _ticket_age_hours(t, now)
    return {
        "id": t["id"],
        "service": t["service"],
        "category": t["category"],
        "priority": t["priority"],
        "status": t["status"],
        "resolved": t["resolved"],
        "created_at": t["created_at"].isoformat() + "Z",
        "acknowledged_at": t["acknowledged_at"].isoformat() + "Z",
        "resolved_at": t["resolved_at"].isoformat() + "Z" if t["resolved_at"] else None,
        "mtta_hours": t["mtta_hours"],
        "resolve_hours": t["resolve_hours"],
        "age_hours": age_hours,
        "risk": _ticket_risk(age_hours if not t["resolved"] else None),
        "sla_breached": t["sla_breached"],
        "first_contact_resolved": t["first_contact_resolved"],
        "reopened": t["reopened"],
        "known_error": t["known_error"],
        "assignee": t["assignee"],
        "summary": t["summary"],
    }


# Function: _narrative
def _narrative(t: dict, now: datetime) -> dict:
    opener = f"{t['category']} reported against {t['service']}."
    urgency = (
        "Escalated immediately on intake due to business-impact priority."
        if t["priority"] in ("P1", "P2") else
        "Queued for standard service-desk triage."
    )
    description = f"{opener} {urgency}"

    timeline = [
        {"time": t["created_at"].isoformat() + "Z", "event": "Ticket created", "actor": "End User"},
        {"time": t["acknowledged_at"].isoformat() + "Z", "event": "Acknowledged by service desk", "actor": t["assignee"]},
    ]
    if t["resolved"]:
        timeline.append({
            "time": t["resolved_at"].isoformat() + "Z",
            "event": f"Marked {t['status']}", "actor": t["assignee"],
        })
        if t["reopened"]:
            timeline.append({
                "time": t["resolved_at"].isoformat() + "Z",
                "event": "Reopened by requester — resolution did not hold", "actor": "End User",
            })
        resolution_notes = (
            f"Root cause: {t['category']}. Resolved by {t['assignee']} in {t['resolve_hours']}h "
            f"({'within' if not t['sla_breached'] else 'outside'} the {SLA_TARGET_HOURS[t['priority']]}h "
            f"{t['priority']} SLA target)."
            + (" First-contact resolution." if t["first_contact_resolved"] else " Required follow-up beyond first contact.")
        )
    else:
        age = _ticket_age_hours(t, now)
        resolution_notes = f"Still open — {age}h since creation, currently with {t['assignee']}."

    return {
        "description": description,
        "timeline": timeline,
        "resolution_notes": resolution_notes,
    }


# Function: _aggregate_kpis
def _aggregate_kpis(tickets: list[dict], changes: list[dict], now: datetime, rng: random.Random) -> dict:
    total = len(tickets)
    ack = [t for t in tickets if t["acknowledged_at"] <= now]
    resolved = [t for t in tickets if t["resolved"]]
    backlog = [t for t in tickets if not t["resolved"]]

    mtta = mean(t["mtta_hours"] for t in ack) if ack else 0.0
    mttr = mean(t["resolve_hours"] for t in resolved) if resolved else 0.0
    sla_pct = 100 * sum(1 for t in resolved if not t["sla_breached"]) / len(resolved) if resolved else 100.0
    fcr_pct = 100 * sum(1 for t in resolved if t["first_contact_resolved"]) / len(resolved) if resolved else 0.0
    reopen_pct = 100 * sum(1 for t in resolved if t["reopened"]) / len(resolved) if resolved else 0.0
    avg_backlog_age = mean(_ticket_age_hours(t, now) for t in backlog) if backlog else 0.0

    change_total = len(changes)
    change_success = sum(1 for c in changes if c["status"] == "Success")
    change_success_pct = round(change_success / change_total * 100, 1) if change_total else 100.0

    health = round(
        sla_pct * 0.30 + fcr_pct * 0.25 + change_success_pct * 0.20
        + (100 - reopen_pct) * 0.15 + min(100, 100 - (mtta - 0.5) * 5) * 0.10
    )
    health = max(0, min(100, health))

    return {
        "timestamp": now.isoformat() + "Z",
        "period": "Last 30 Days",
        "total_tickets": total,
        "acknowledged_tickets": len(ack),
        "resolved_tickets": len(resolved),
        "mtta_hours": round(mtta, 2),
        "mttr_hours": round(mttr, 2),
        "sla_compliance_pct": round(sla_pct, 1),
        "fcr_pct": round(fcr_pct, 1),
        "reopen_rate_pct": round(reopen_pct, 1),
        "backlog_count": len(backlog),
        "avg_backlog_age_hours": round(avg_backlog_age, 1),
        "change_total": change_total,
        "change_success": change_success,
        "change_success_rate_pct": change_success_pct,
        "health_score": health,
        "trends": {
            "mtta": rng.choice(["up", "down", "stable"]),
            "mttr": rng.choice(["up", "down", "stable"]),
            "sla": rng.choice(["up", "down", "stable"]),
            "fcr": rng.choice(["up", "down", "stable"]),
            "reopen": rng.choice(["up", "down", "stable"]),
        },
    }


# Function: _regenerate_state
def _regenerate_state(scenario: str, seed=None) -> dict:
    r = random.Random(seed) if seed is not None else random.Random()
    profile = SCENARIO_PROFILES.get(scenario, SCENARIO_PROFILES["normal"])
    now = datetime.utcnow()
    total_n = r.randint(450, 900)
    tickets = [_make_ticket(r, i + 1, now, profile) for i in range(total_n)]
    changes = _make_changes(r, profile, now)
    _STATE.update(scenario=scenario, tickets=tickets, changes=changes, generated_at=now.isoformat() + "Z")
    metrics = _aggregate_kpis(tickets, changes, now, r)
    metrics["scenario"] = scenario
    return metrics


# Function: _ensure_state
def _ensure_state() -> tuple[list[dict], list[dict]]:
    if not _STATE.get("tickets"):
        _regenerate_state("normal")
    return _STATE["tickets"], _STATE["changes"]


# Function: _call_llm
def _call_llm(system_msg: str, user_msg: str) -> str:
    from langchain_ollama import ChatOllama
    from backend.llm.router import assert_ollama_gpu_available
    assert_ollama_gpu_available(cfg.OLLAMA_MODEL)
    llm = ChatOllama(
        model=cfg.OLLAMA_MODEL, base_url=cfg.OLLAMA_BASE_URL,
        temperature=0.2, num_predict=1024, num_ctx=4096,
        format="json", timeout=_LLM_TIMEOUT, keep_alive=cfg.OLLAMA_KEEP_ALIVE,
    )
    with ThreadPoolExecutor(max_workers=1) as pool:
        result = pool.submit(llm.invoke, [("system", system_msg), ("human", user_msg)]).result(timeout=_LLM_TIMEOUT)
    return result.content if hasattr(result, "content") else str(result)


# Function: _extract_json
def _extract_json(raw: str) -> dict | None:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except Exception:
        pass
    s, e = text.find("{"), text.rfind("}")
    if s >= 0 and e > s:
        try:
            return json.loads(text[s:e + 1])
        except Exception:
            pass
    return None


# ── Endpoints ────────────────────────────────────────────────────────────────

# Function: get_dashboard_metrics
@router.get("/dashboard/metrics")
async def get_dashboard_metrics(current_user: dict = Depends(get_current_user)):
    """Live ITSM KPI snapshot, aggregated from the current cached ticket population."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    tickets, changes = _ensure_state()
    return _aggregate_kpis(tickets, changes, datetime.utcnow(), random.Random())


# Function: simulate_dashboard
@router.post("/dashboard/simulate")
async def simulate_dashboard(
    payload: dict = Body(default={}),
    current_user: dict = Depends(get_current_user),
):
    """
    Regenerate the synthetic ticket population for a scenario and return the
    KPIs aggregated from it, plus an LLM executive summary.
    scenario: 'normal' | 'degraded' | 'critical' | 'good'
    This is the single point where the underlying data changes — the other
    GET endpoints below only read/aggregate whatever this last generated.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    scenario = payload.get("scenario", "normal")
    seed = payload.get("seed")
    metrics = _regenerate_state(scenario, seed)

    system_msg = (
        "You are an ITSM operations manager. Interpret these live KPI metrics and write a brief executive summary. "
        "Return JSON: {\"executive_summary\": str, \"risk_flags\": [str], \"quick_wins\": [str]}"
    )
    kpi_subset = {k: v for k, v in metrics.items() if k not in ("trends", "timestamp")}
    try:
        # _call_llm's internal _LLM_TIMEOUT (90s) only bounds the actual
        # llm.invoke() call — assert_ollama_gpu_available() runs before that,
        # and _warm_ollama_model() inside it has its own up-to-120s timeout,
        # unbounded by _LLM_TIMEOUT. Worst case (warm + invoke) could run past
        # 200s, well beyond IIS/ARR's 2-minute proxy timeout, surfacing as a
        # 502/500 to the browser even though this endpoint has a fast, correct
        # non-LLM fallback below. Wrap the whole call so total latency always
        # stays safely under the proxy timeout regardless of Ollama's health.
        raw = await asyncio.wait_for(
            asyncio.to_thread(_call_llm, system_msg, json.dumps(kpi_subset)),
            timeout=60,
        )
        parsed = _extract_json(raw) or {}
        metrics.update(parsed)
        metrics["llm_used"] = True
    except Exception as exc:
        logger.warning("simulate_dashboard LLM failed: %s", exc)
        h = metrics["health_score"]
        if h >= 80:
            summary = f"Operations performing well (health {h}/100). SLA compliance and FCR are strong. Focus on sustaining change discipline."
        elif h >= 55:
            summary = f"Moderate performance (health {h}/100). Elevated reopen rate and SLA slippage need attention. Review L1 resolution quality."
        else:
            summary = f"Critical state (health {h}/100). High MTTR and SLA breach risk. Immediate escalation and resource reallocation required."
        metrics.update(executive_summary=summary, risk_flags=[], quick_wins=[], llm_used=False)

    return metrics


# Function: get_backlog_aging
@router.get("/backlog/aging")
async def get_backlog_aging(current_user: dict = Depends(get_current_user)):
    """Backlog aging distribution + aged tickets, aggregated from the current ticket population."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    tickets, _ = _ensure_state()
    now = datetime.utcnow()
    backlog = [t for t in tickets if not t["resolved"]]

    buckets = {"0–4 h": 0, "4–8 h": 0, "8–24 h": 0, "1–3 d": 0, "3–7 d": 0, ">7 d": 0}
    for t in backlog:
        age = _ticket_age_hours(t, now)
        if age <= 4: buckets["0–4 h"] += 1
        elif age <= 8: buckets["4–8 h"] += 1
        elif age <= 24: buckets["8–24 h"] += 1
        elif age <= 72: buckets["1–3 d"] += 1
        elif age <= 168: buckets["3–7 d"] += 1
        else: buckets[">7 d"] += 1

    ranked = sorted(backlog, key=lambda t: -_ticket_age_hours(t, now))
    return {
        "buckets": buckets,
        "tickets": [_public_ticket(t, now) for t in ranked[:30]],
        "total_backlog": len(backlog),
        "timestamp": now.isoformat() + "Z",
    }


# Function: get_incidents_by_service
@router.get("/incidents/by-service")
async def get_incidents_by_service(current_user: dict = Depends(get_current_user)):
    """Incident volume breakdown by service, aggregated from the current ticket population."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    tickets, _ = _ensure_state()
    now = datetime.utcnow()
    rng = random.Random()
    data = []
    for svc in SERVICES:
        svc_tickets = [t for t in tickets if t["service"] == svc]
        total = len(svc_tickets)
        if total == 0:
            continue
        resolved = [t for t in svc_tickets if t["resolved"]]
        data.append({
            "service": svc,
            "total": total,
            "p1": sum(1 for t in svc_tickets if t["priority"] == "P1"),
            "p2": sum(1 for t in svc_tickets if t["priority"] == "P2"),
            "p3": sum(1 for t in svc_tickets if t["priority"] == "P3"),
            "p4": sum(1 for t in svc_tickets if t["priority"] == "P4"),
            "resolved_pct": round(100 * len(resolved) / total, 1),
            "avg_mttr_hours": round(mean(t["resolve_hours"] for t in resolved), 1) if resolved else 0.0,
            "trend": rng.choice(["increasing", "decreasing", "stable"]),
        })
    data.sort(key=lambda x: -x["total"])
    return {"services": data, "timestamp": now.isoformat() + "Z"}


# Function: get_recurring_problems
@router.get("/problems/recurring")
async def get_recurring_problems(current_user: dict = Depends(get_current_user)):
    """Top recurring problems, aggregated from the current ticket population."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    tickets, _ = _ensure_state()
    now = datetime.utcnow()
    rng = random.Random()
    problems = []
    for cat in PROBLEM_CATEGORIES:
        cat_tickets = [t for t in tickets if t["category"] == cat]
        count = len(cat_tickets)
        if count == 0:
            continue
        resolved = [t for t in cat_tickets if t["resolved"]]
        dominant_service = Counter(t["service"] for t in cat_tickets).most_common(1)[0][0]
        problems.append({
            "problem": cat,
            "count": count,
            "service": dominant_service,
            "avg_resolution_hours": round(mean(t["resolve_hours"] for t in resolved), 1) if resolved else 0.0,
            "reopen_count": sum(1 for t in cat_tickets if t["reopened"]),
            "trend": rng.choice(["increasing", "decreasing", "stable"]),
            "root_cause_identified": cat in KNOWN_ERROR_CATEGORIES,
            "known_error": cat in KNOWN_ERROR_CATEGORIES,
        })
    problems.sort(key=lambda x: -x["count"])
    return {"problems": problems[:8], "timestamp": now.isoformat() + "Z"}


# Function: list_tickets
@router.get("/tickets")
async def list_tickets(current_user: dict = Depends(get_current_user)):
    """
    Full current ticket population (drill-down source). Every KPI card,
    service bar, recurring-problem row and backlog row on the dashboard is an
    aggregation of exactly this list — filter/sort it client-side to get the
    tickets behind any given number.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    tickets, _ = _ensure_state()
    now = datetime.utcnow()
    return {
        "tickets": [_public_ticket(t, now) for t in tickets],
        "total": len(tickets),
        "scenario": _STATE["scenario"],
        "generated_at": _STATE["generated_at"],
    }


# Function: get_ticket_detail
@router.get("/tickets/{ticket_id}")
async def get_ticket_detail(ticket_id: str, current_user: dict = Depends(get_current_user)):
    """Full detail for a single ticket from the current population, including narrative/timeline (L3)."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    tickets, _ = _ensure_state()
    t = next((x for x in tickets if x["id"] == ticket_id), None)
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found in the current simulated population — refresh the dashboard and try again.")
    now = datetime.utcnow()
    detail = _public_ticket(t, now)
    detail.update(_narrative(t, now))
    return detail


# Function: list_changes
@router.get("/changes")
async def list_changes(current_user: dict = Depends(get_current_user)):
    """Full current change population (drill-down source for Change Success Rate)."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    _, changes = _ensure_state()
    return {"changes": changes, "total": len(changes)}


# Function: simulate_change_metrics
@router.post("/change/simulate")
async def simulate_change_metrics(
    payload: dict = Body(default={}),
    current_user: dict = Depends(get_current_user),
):
    """Change management KPIs for the current change population."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    _, changes = _ensure_state()
    total = len(changes)
    success = sum(1 for c in changes if c["status"] == "Success")
    failed = sum(1 for c in changes if c["status"] == "Failed")
    rolled_back = sum(1 for c in changes if c["status"] == "Rolled Back")
    emergency = sum(1 for c in changes if c["type"] == "Emergency")
    return {
        "period": payload.get("period", "Last 30 Days"),
        "total_changes": total,
        "successful": success,
        "failed": failed,
        "rolled_back": rolled_back,
        "emergency_changes": emergency,
        "success_rate_pct": round(success / total * 100, 1) if total else 100.0,
        "failure_rate_pct": round(failed / total * 100, 1) if total else 0.0,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
