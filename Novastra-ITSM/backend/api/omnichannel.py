# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Omnichannel Ticket Intake — simulate and manage ticket ingestion from
# Date: 2026-02-24
# ---------------------------------------------------------------------------
"""
Omnichannel Ticket Intake — simulate and manage ticket ingestion from
Web Portal, Email, Chat, Phone, Mobile App, Monitoring Tools, and API.

Ticket content (subject, priority, channel, AI triage) is synthetic/simulated.
Each simulated ticket is also written to ServiceNow as a real `incident` record
when SERVICENOW_BASE_URL/USERNAME/PASSWORD are configured (see
backend/services/servicenow_intake.py) — the simulation isn't just a UI demo,
it drives the actual configured ServiceNow instance. When credentials aren't
configured, ticket generation still works and each ticket's `servicenow.status`
is reported as `skipped_no_credentials`.
"""
from __future__ import annotations
import asyncio, json, logging, random, re, uuid
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Body, Depends, HTTPException
from backend.api.auth import get_current_user
from backend.services.servicenow_intake import PRIORITY_TO_SN, create_incidents_batch
from backend.services.operational_ingestion import (
    load_local_created_incidents,
    persist_created_incidents,
    reembed_incidents,
)
import backend.config as cfg

router = APIRouter(prefix="/api/omnichannel", tags=["Omnichannel Ticket Intake"])
logger = logging.getLogger(__name__)
# The triage summary is supplementary AI commentary with an existing synthetic
# fallback (see simulate_intake's except block) — it must never be what makes
# ticket creation feel slow. 25s comfortably covers a real qwen2.5-coder:7b
# response (~16-20s observed) without letting a wedged/overloaded Ollama (this
# box's GPU can't fully fit the 14B model — seen live, generate calls sometimes
# hang) hold up the response for anywhere near as long as the old 90s bound did.
_LLM_TIMEOUT = 25

CHANNELS: dict[str, dict] = {
    "web_portal": {
        "label": "Web Portal",
        "icon": "Globe",
        "color": "blue",
        "description": "Employee self-service portal",
        "example": "Employee raises hardware/software requests online",
        "avg_response_secs": 2.1,
    },
    "email": {
        "label": "Email",
        "icon": "Mail",
        "color": "orange",
        "description": "Auto-create tickets from support mailbox",
        "example": "Parses inbound emails, creates and classifies tickets",
        "avg_response_secs": 45.0,
    },
    "chat": {
        "label": "Chat",
        "icon": "MessageSquare",
        "color": "purple",
        "description": "Teams, Slack, web chat",
        "example": "MS Teams bot, Slack app, embedded web widget",
        "avg_response_secs": 4.8,
    },
    "phone": {
        "label": "Phone",
        "icon": "Phone",
        "color": "green",
        "description": "Service desk agent logging",
        "example": "L1 agent logs caller issue; AI transcribes and classifies",
        "avg_response_secs": 90.0,
    },
    "mobile": {
        "label": "Mobile App",
        "icon": "Smartphone",
        "color": "cyan",
        "description": "Field support and approvals",
        "example": "Field technicians log issues; managers approve from mobile",
        "avg_response_secs": 6.5,
    },
    "monitoring": {
        "label": "Monitoring Tools",
        "icon": "Activity",
        "color": "red",
        "description": "Auto-create incidents from alerts",
        "example": "Nagios / Dynatrace / Zabbix alert → P1/P2 incident",
        "avg_response_secs": 0.8,
    },
    "api": {
        "label": "API",
        "icon": "Code2",
        "color": "violet",
        "description": "Application/system-generated tickets",
        "example": "CI/CD pipeline, batch jobs, health-check failures",
        "avg_response_secs": 0.5,
    },
}

_SUBJECTS: dict[str, list[str]] = {
    "web_portal": [
        "Password reset – cannot log in after vacation",
        "VPN not connecting from home office",
        "Request: Adobe Acrobat Pro license",
        "Laptop fan noise unusually loud",
        "Outlook calendar not syncing with mobile",
        "Request new laptop – old one out of warranty",
    ],
    "email": [
        "Cannot access SAP – system says account locked",
        "Email quota exceeded – bouncing outgoing mail",
        "Teams meeting link not working for external guests",
        "Printer on 3rd floor showing offline in queue",
        "SharePoint site permissions changed without notice",
    ],
    "chat": [
        "Quick Q: how to reset MFA authenticator?",
        "Teams calls drop after exactly 2 minutes",
        "Need SharePoint edit permission for project X",
        "Excel keeps crashing when opening large files",
        "Can someone help reset my OneDrive sync?",
    ],
    "phone": [
        "User completely locked out – cannot access any systems",
        "CRITICAL: SAP production system down – P1",
        "Network drive G: not mapped after PC restart",
        "Blue screen on startup – data not accessible",
        "Cannot receive calls in Teams since this morning",
    ],
    "mobile": [
        "Approval request stuck – cannot approve from mobile",
        "Corporate calendar not syncing to iOS device",
        "VPN certificate expired on mobile device",
        "Mobile app crashes on launch after iOS 17 update",
        "Push notifications stopped working for approvals",
    ],
    "monitoring": [
        "ALERT: CPU spike >95% sustained on APPSVR01",
        "ALERT: Disk /var at 92% – storage threshold breached",
        "ALERT: API Gateway latency >2000ms for 5 min",
        "ALERT: Memory leak detected in JVM process – heap at 98%",
        "ALERT: Health check timeout – DB connection pool exhausted",
        "ALERT: SSL certificate expiry in 7 days – WEBPRD02",
    ],
    "api": [
        "AUTO: Build pipeline #4821 failed – deployment blocked",
        "AUTO: Nightly DB backup job returned exit code 1",
        "AUTO: Certificate expiry warning – 14 days remaining",
        "AUTO: Scheduled report generation timed out",
        "AUTO: Data sync job failed – source unreachable",
    ],
}

_PRIORITY_WEIGHTS: dict[str, list[tuple[str, float]]] = {
    "web_portal": [("P3", 0.55), ("P4", 0.35), ("P2", 0.10), ("P1", 0.00)],
    "email":      [("P3", 0.50), ("P4", 0.30), ("P2", 0.18), ("P1", 0.02)],
    "chat":       [("P3", 0.60), ("P4", 0.30), ("P2", 0.10), ("P1", 0.00)],
    "phone":      [("P2", 0.40), ("P1", 0.25), ("P3", 0.30), ("P4", 0.05)],
    "mobile":     [("P3", 0.45), ("P4", 0.35), ("P2", 0.18), ("P1", 0.02)],
    "monitoring": [("P1", 0.40), ("P2", 0.45), ("P3", 0.15), ("P4", 0.00)],
    "api":        [("P1", 0.30), ("P2", 0.40), ("P3", 0.28), ("P4", 0.02)],
}

_SLA_HOURS = {"P1": 4, "P2": 8, "P3": 24, "P4": 72}
_ASSIGNEES = ["L1-Team Alpha", "L1-Team Beta", "L2-SAP", "L2-Network", "L2-EndUser", "L3-Platform", "On-call Eng"]


# Function: _weighted_choice
def _weighted_choice(weights: list[tuple[str, float]], r: random.Random) -> str:
    keys, probs = zip(*weights)
    cum = 0.0
    rnd = r.random()
    for k, p in zip(keys, probs):
        cum += p
        if rnd <= cum:
            return k
    return keys[-1]


# Function: _make_ticket
def _make_ticket(channel: str, subject: str | None = None, priority: str | None = None, r: random.Random | None = None) -> dict:
    if r is None:
        r = random.Random()
    ch = CHANNELS.get(channel, CHANNELS["api"])
    subj = subject or r.choice(_SUBJECTS.get(channel, ["Unclassified request"]))
    prio = priority or _weighted_choice(_PRIORITY_WEIGHTS.get(channel, [("P3", 1.0)]), r)
    now = datetime.utcnow()
    sla_deadline = now + timedelta(hours=_SLA_HOURS[prio])
    return {
        "ticket_id": f"INC{now.strftime('%Y%m%d')}{r.randint(1000, 9999)}",
        "channel": channel,
        "channel_label": ch["label"],
        "subject": subj,
        "priority": prio,
        "status": "Open",
        "created_at": now.isoformat() + "Z",
        "sla_deadline": sla_deadline.isoformat() + "Z",
        "sla_hours": _SLA_HOURS[prio],
        "auto_classified": True,
        "ai_summary": f"[{ch['label']}] {subj} — Priority: {prio}, SLA: {_SLA_HOURS[prio]}h",
        "suggested_assignee": r.choice(_ASSIGNEES),
        "similar_ticket_count": r.randint(0, 14),
        "confidence_score": round(r.uniform(0.72, 0.99), 2),
        "category": r.choice(["Incident", "Service Request", "Problem", "Change"]),
        "sub_category": channel.replace("_", " ").title(),
    }


# Function: _create_in_servicenow_or_skip
async def _create_in_servicenow_or_skip(tickets: list[dict]) -> list[dict]:
    """Creates one real ServiceNow incident per simulated ticket. Mirrors
    update_ticket's existing convention (backend/api/servicenow.py): if
    SERVICENOW_BASE_URL/USERNAME/PASSWORD aren't configured, every ticket is
    reported 'skipped_no_credentials' rather than failing the intake/simulate
    call — simulation still works in demo/dev environments with no live SN."""
    if not all([cfg.SERVICENOW_BASE_URL, cfg.SERVICENOW_USERNAME, cfg.SERVICENOW_PASSWORD]):
        return [{"status": "skipped_no_credentials", "error": None, "number": None, "sys_id": None} for _ in tickets]
    try:
        return await create_incidents_batch(
            base_url=cfg.SERVICENOW_BASE_URL, username=cfg.SERVICENOW_USERNAME, password=cfg.SERVICENOW_PASSWORD,
            tickets=tickets, timeout_seconds=cfg.SERVICENOW_TIMEOUT_SECONDS, verify_ssl=cfg.SERVICENOW_VERIFY_SSL,
        )
    except Exception as exc:  # noqa: BLE001 — ServiceNow being unreachable must not break the simulation itself
        logger.warning("ServiceNow batch incident creation failed: %s", exc)
        return [{"status": "failed", "error": str(exc), "number": None, "sys_id": None} for _ in tickets]


_SN_PRIORITY_LABEL = {"1": "1 - Critical", "2": "2 - High", "3": "3 - Moderate", "4": "4 - Low"}


# Function: _local_record_for_created_ticket
def _local_record_for_created_ticket(ticket: dict) -> dict:
    """Builds a dashboard-shaped incident record for a ticket that was just
    created in ServiceNow, from the SAME fields actually sent to ServiceNow
    (servicenow_intake._ticket_to_incident_payload) — assigned_to/category are
    left blank here for the same reason they're left unset in that payload:
    ServiceNow doesn't actually have that data for this ticket, so showing a
    fabricated value locally would just be a second thing to un-teach later."""
    sn = ticket["servicenow"]
    now = datetime.utcnow().isoformat() + "Z"
    priority_code = PRIORITY_TO_SN.get(ticket.get("priority"), "3")
    return {
        "incident_id": sn.get("sys_id") or sn["number"],
        "number": sn["number"],
        "short_description": ticket.get("subject", ""),
        "description": ticket.get("ai_summary", ""),
        "category": "",
        "subcategory": "",
        "state": "Open",
        "priority": _SN_PRIORITY_LABEL.get(priority_code, priority_code),
        "assignment_group": "",
        "assigned_to": "",
        "opened_at": now,
        "resolved_at": "",
        "closed_at": "",
        "close_notes": "",
        "work_notes": "",
        "source_name": "omnichannel_intake",
        "last_synced_at": now,
        # Extra fields beyond the standard dashboard-incident shape — used for the
        # Omnichannel page's own channel-level stats/drill-down, not by the Synced
        # Incidents Dashboard. operational_ingestion.normalize_created_incident
        # passes these through unchanged.
        "channel": ticket.get("channel", ""),
        "channel_label": ticket.get("channel_label", ""),
        "local_ticket_id": ticket.get("ticket_id", ""),
    }


# Function: _persist_created_tickets
def _persist_created_tickets(tickets: list[dict]) -> int:
    """Writes every successfully-SN-created ticket into local storage and the
    vector store, so it's immediately findable via dashboard search/list and
    chat/RAG — without this, a ticket is real in ServiceNow but invisible
    everywhere else in the app until the next full resync. Synchronous (file
    I/O + embedding); callers run it via asyncio.to_thread.

    persist_created_incidents (local search/list) and reembed_incidents (vector
    store) are two independent failure domains — a slow/wedged Ollama embedding
    call must not take down local persistence with it. Seen live: reembed_incidents
    raising httpx.ReadTimeout here was propagating all the way out of the /simulate
    endpoint uncaught, turning it into a 500 even though the ticket had already
    been created in ServiceNow and written to local storage by that point — the
    client saw a hard failure for work that had actually mostly succeeded."""
    records = [
        _local_record_for_created_ticket(t) for t in tickets
        if t.get("servicenow", {}).get("status") == "created"
    ]
    if not records:
        return 0
    persist_created_incidents(records)
    try:
        reembed_incidents(records, "omnichannel_intake")
    except Exception as exc:  # noqa: BLE001 — embedding is best-effort here; the ticket is already real and searchable
        logger.warning("Vector re-embed failed for %d newly-created ticket(s): %s", len(records), exc)
    return len(records)


# Function: _real_omnichannel_tickets
def _real_omnichannel_tickets() -> list[dict]:
    """Every ticket actually created via Omnichannel Ticket Intake (real ServiceNow
    incidents, persisted by _persist_created_tickets) — the single source of truth
    for Channel Overview / 24h Stats / Open Queue / drill-down, replacing the
    random per-request numbers those views used to show. A stat with nothing
    real behind it can't be drilled into, which was the actual problem."""
    return load_local_created_incidents()


# Function: _parse_opened_at
def _parse_opened_at(record: dict) -> datetime | None:
    raw = record.get("opened_at")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


# Function: _tickets_within
def _tickets_within(records: list[dict], hours: float) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    out = []
    for rec in records:
        opened = _parse_opened_at(rec)
        if opened is not None and opened >= cutoff:
            out.append(rec)
    return out


# Function: _ticket_priority_bucket
def _ticket_priority_bucket(record: dict) -> str:
    # record["priority"] is stored as "N - Label" (see _SN_PRIORITY_LABEL) — take the
    # leading digit and map back onto the P1-P4 scale the rest of this page uses.
    priority = record.get("priority", "")
    code = priority.split(" ", 1)[0] if priority else ""
    return f"P{code}" if code in {"1", "2", "3", "4"} else "P4"


# Function: _incident_to_omnichannel_ticket
def _incident_to_omnichannel_ticket(record: dict) -> dict:
    """Projects a stored dashboard-shaped incident record (see
    _local_record_for_created_ticket) back into the omnichannel-ticket shape the
    frontend's TicketCard/queue table already render — so Queue/drill-down can
    reuse that UI unchanged, now backed by real created tickets instead of
    freshly-randomized ones. Fields we never captured (similarity count, AI
    confidence) are surfaced as None/0 rather than fabricated.

    "ticket_id" is the real ServiceNow number, not the synthetic local id this
    ticket was first generated with — every record passed here already has a
    ServiceNow number (_persist_created_tickets only calls this for tickets
    whose SN creation succeeded), and the SN number is the identifier that's
    actually searchable in the Synced Incidents Dashboard, so showing the
    internal id here instead just meant the same ticket appeared under two
    different, uncorrelated numbers depending which page you looked at."""
    priority = _ticket_priority_bucket(record)
    return {
        "ticket_id": record["number"],
        "servicenow_number": record["number"],
        "local_ticket_id": record.get("local_ticket_id", ""),
        "channel": record.get("channel", ""),
        "channel_label": record.get("channel_label") or record.get("channel", ""),
        "subject": record.get("short_description", ""),
        "priority": priority,
        "status": record.get("state", "Open"),
        "created_at": record.get("opened_at", ""),
        "sla_hours": _SLA_HOURS.get(priority, 24),
        "auto_classified": True,
        "ai_summary": record.get("description", ""),
        "suggested_assignee": record.get("assigned_to") or "Unassigned",
        "similar_ticket_count": 0,
        "confidence_score": None,
        "category": "Incident",
        "sub_category": record.get("channel_label") or record.get("channel", ""),
    }


# ── Endpoints ────────────────────────────────────────────────────────────────

# Function: get_channels_status
@router.get("/channels/status")
async def get_channels_status(current_user: dict = Depends(get_current_user)):
    """Return real ticket volume for all intake channels, computed from tickets
    actually created via this page (see _real_omnichannel_tickets). `status` is
    still a simple heuristic (no real per-channel health signal exists to
    monitor), but the counts are real and every one of them corresponds to an
    actual list of tickets reachable via GET /tickets?channel=X."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    all_tickets = _real_omnichannel_tickets()
    last_hour = _tickets_within(all_tickets, 1)
    today = _tickets_within(all_tickets, 24)

    statuses = {}
    for ch_id, info in CHANNELS.items():
        ch_today = [t for t in today if t.get("channel") == ch_id]
        ch_last_hour = [t for t in last_hour if t.get("channel") == ch_id]
        statuses[ch_id] = {
            **info,
            "status": "active",
            "tickets_last_hour": len(ch_last_hour),
            "tickets_today": len(ch_today),
            "avg_response_secs": info["avg_response_secs"],
            "auto_classify_accuracy_pct": 100.0 if ch_today else None,
        }
    return {"channels": statuses, "timestamp": datetime.utcnow().isoformat() + "Z"}


# Function: list_omnichannel_tickets
@router.get("/tickets")
async def list_omnichannel_tickets(
    channel: str | None = None,
    hours: float = 24,
    current_user: dict = Depends(get_current_user),
):
    """The drill-down data source: every real Omnichannel-created ticket, optionally
    filtered to one channel and/or a time window. Channel Overview and 24h Stats
    cards link here — this is the L2 list behind each number on those cards."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    tickets = _tickets_within(_real_omnichannel_tickets(), hours) if hours else _real_omnichannel_tickets()
    if channel and channel != "all":
        tickets = [t for t in tickets if t.get("channel") == channel]
    tickets.sort(key=lambda t: t.get("opened_at") or "", reverse=True)
    projected = [_incident_to_omnichannel_ticket(t) for t in tickets]
    return {"tickets": projected, "total": len(projected)}


# Function: intake_ticket
@router.post("/intake")
async def intake_ticket(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Submit a ticket from a specific channel.
    Provide: channel, optionally subject and priority.
    All missing fields are AI-filled with synthetic values.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    channel = payload.get("channel", "web_portal")
    if channel not in CHANNELS:
        raise HTTPException(status_code=400, detail=f"Unknown channel. Valid: {list(CHANNELS.keys())}")
    ticket = _make_ticket(channel, payload.get("subject"), payload.get("priority"))
    ticket["servicenow"] = await _create_in_servicenow_or_skip([ticket])
    ticket["servicenow"] = ticket["servicenow"][0]
    await asyncio.to_thread(_persist_created_tickets, [ticket])
    return {"ticket": ticket, "ingested": True, "channel_info": CHANNELS[channel]}


# Function: simulate_intake
@router.post("/simulate")
async def simulate_intake(
    payload: dict = Body(default={}),
    current_user: dict = Depends(get_current_user),
):
    """
    Simulate a burst of incoming tickets.
    channel: specific channel id or 'all'
    count: number of tickets to generate (max 30)
    Returns tickets + breakdown + LLM triage summary.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    channel = payload.get("channel", "all")
    count = max(1, min(int(payload.get("count", 5)), 30))
    if channel != "all" and channel not in CHANNELS:
        raise HTTPException(status_code=400, detail="Unknown channel")

    r = random.Random()
    channel_pool = list(CHANNELS.keys()) if channel == "all" else [channel]
    tickets = [_make_ticket(r.choice(channel_pool), r=r) for _ in range(count)]

    breakdown: dict[str, int] = {}
    priority_breakdown: dict[str, int] = {}
    for t in tickets:
        breakdown[t["channel"]] = breakdown.get(t["channel"], 0) + 1
        priority_breakdown[t["priority"]] = priority_breakdown.get(t["priority"], 0) + 1

    result = {
        "tickets": tickets,
        "count": len(tickets),
        "channel_breakdown": breakdown,
        "priority_breakdown": priority_breakdown,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "llm_triage": None,
    }

    # Kick off ServiceNow incident creation AND the LLM triage summary at the same
    # time — they're independent, and the actual point of this endpoint (real
    # tickets, findable everywhere) must never sit behind the LLM triage summary
    # (supplementary commentary with its own synthetic fallback below). The old
    # code awaited the LLM call to completion BEFORE even starting the ServiceNow
    # work, so a slow/wedged Ollama (this box's GPU can't reliably fit the 14B
    # model — seen live) made ticket creation itself feel hung for up to 90s+,
    # which is exactly backwards.
    servicenow_task = asyncio.create_task(_create_in_servicenow_or_skip(tickets))

    system_msg = (
        "You are an ITSM triage coordinator. Given a batch of newly-arrived tickets, "
        "quickly summarize what's happening and flag urgent action. "
        "Return JSON: {\"triage_summary\": str, \"urgent_tickets\": [str], \"suggested_routing\": str}"
    )
    batch_text = json.dumps([{"id": t["ticket_id"], "subject": t["subject"], "priority": t["priority"], "channel": t["channel_label"]} for t in tickets[:10]])

    # Function: _call_llm
    def _call_llm():
        from langchain_ollama import ChatOllama
        from backend.llm.router import assert_ollama_gpu_available
        assert_ollama_gpu_available(cfg.OLLAMA_MODEL)
        llm = ChatOllama(model=cfg.OLLAMA_MODEL, base_url=cfg.OLLAMA_BASE_URL,
                         temperature=0.2, num_predict=512, format="json",
                         timeout=_LLM_TIMEOUT, keep_alive=cfg.OLLAMA_KEEP_ALIVE)
        # Deliberately not `with ThreadPoolExecutor(...) as pool:` — __exit__ calls
        # shutdown(wait=True), which blocks until the submitted call returns even
        # after .result(timeout=...) below has already raised. A wedged Ollama
        # (seen live: /api/generate hangs indefinitely while /api/ps stays
        # responsive) then hangs this "bounded" call forever too, defeating the
        # entire point of the timeout. shutdown(wait=False) abandons the stuck
        # thread instead — a thread blocked on a synchronous HTTP read can't be
        # force-killed anyway, so waiting for it buys nothing.
        pool = ThreadPoolExecutor(max_workers=1)
        future = pool.submit(llm.invoke, [("system", system_msg), ("human", batch_text)])
        try:
            res = future.result(timeout=_LLM_TIMEOUT)
        finally:
            pool.shutdown(wait=False)
        return res.content if hasattr(res, "content") else str(res)

    llm_task = asyncio.create_task(asyncio.to_thread(_call_llm))

    # ServiceNow creation + local/vector persistence run while llm_task is still
    # in flight above — persistence needs the SN results merged in first, so it's
    # sequential relative to servicenow_task, but both proceed concurrently with
    # the (now much shorter, 25s-bounded) LLM call.
    servicenow_results = await servicenow_task
    for ticket, sn in zip(tickets, servicenow_results):
        ticket["servicenow"] = sn
    result["servicenow_created_count"] = sum(1 for sn in servicenow_results if sn["status"] == "created")
    result["servicenow_failed_count"] = sum(1 for sn in servicenow_results if sn["status"] == "failed")
    result["local_db_persisted_count"] = await asyncio.to_thread(_persist_created_tickets, tickets)

    try:
        # _LLM_TIMEOUT (25s) only bounds the llm.invoke() call inside _call_llm —
        # assert_ollama_gpu_available() runs before that and its own internal
        # warm-up step can take up to ~120s, unbounded by _LLM_TIMEOUT. Bound the
        # whole task here too, so this stays well under IIS/ARR's 2-minute proxy
        # timeout regardless of Ollama's health (see itsm_ops.py's
        # simulate_dashboard for the same fix and full explanation).
        raw = await asyncio.wait_for(llm_task, timeout=45)
        text = (raw or "").strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
            text = re.sub(r"\s*```$", "", text)
        parsed = json.loads(text) if text else {}
        result["llm_triage"] = parsed
        result["llm_used"] = True
    except Exception as exc:
        logger.warning("simulate_intake LLM failed: %s", exc)
        p1_count = priority_breakdown.get("P1", 0)
        result["llm_triage"] = {
            "triage_summary": f"{count} tickets ingested across {len(breakdown)} channel(s). {p1_count} P1 incidents require immediate attention.",
            "urgent_tickets": [t["ticket_id"] for t in tickets if t["priority"] == "P1"][:3],
            "suggested_routing": "Route P1/P2 to on-call; P3/P4 to L1 queue.",
        }
        result["llm_used"] = False

    return result


# Function: get_queue
@router.get("/queue")
async def get_queue(current_user: dict = Depends(get_current_user)):
    """Real open queue: every Omnichannel-created ticket whose ServiceNow state
    isn't Closed, sorted by priority. Previously regenerated 8-25 random tickets
    on every call, unrelated to anything actually created."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    open_tickets = [t for t in _real_omnichannel_tickets() if t.get("state") != "Closed"]
    queue = [_incident_to_omnichannel_ticket(t) for t in open_tickets]
    queue.sort(key=lambda x: ["P1", "P2", "P3", "P4"].index(x["priority"]))
    breakdown: dict[str, int] = {}
    for t in queue:
        breakdown[t["channel_label"]] = breakdown.get(t["channel_label"], 0) + 1
    return {
        "queue": queue,
        "total": len(queue),
        "channel_breakdown": breakdown,
        "p1_count": sum(1 for t in queue if t["priority"] == "P1"),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# Function: get_intake_stats
@router.get("/stats/summary")
async def get_intake_stats(current_user: dict = Depends(get_current_user)):
    """24-hour intake statistics by channel, computed from tickets actually
    created via this page. satisfaction_score has no real signal behind it (no
    CSAT survey flow exists) and is reported as null rather than a fabricated
    number; everything else here corresponds to a real, drillable ticket list."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    today = _tickets_within(_real_omnichannel_tickets(), 24)
    stats = {}
    for ch_id, info in CHANNELS.items():
        ch_tickets = [t for t in today if t.get("channel") == ch_id]
        total = len(ch_tickets)
        buckets = [_ticket_priority_bucket(t) for t in ch_tickets]
        stats[ch_id] = {
            "label": info["label"],
            "color": info["color"],
            "total_24h": total,
            "auto_classified": total,
            "avg_response_secs": info["avg_response_secs"],
            "p1_count": buckets.count("P1"),
            "p2_count": buckets.count("P2"),
            "satisfaction_score": None,
        }
    return {"stats": stats, "period": "Last 24 hours", "timestamp": datetime.utcnow().isoformat() + "Z"}
