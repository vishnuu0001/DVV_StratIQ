# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Omnichannel "Email" channel — real IMAP intake.
# Date: 2026-07-15
# ---------------------------------------------------------------------------
"""Polls a real mailbox (Titan Email via IMAP) and turns every new inbound
message into a real Omnichannel ticket, through the exact same ServiceNow
creation + local persistence pipeline backend/api/omnichannel.py's
"Simulate Intake" button uses — this is the non-simulated counterpart to it.

Runs as an in-process asyncio background task (see main.py's lifespan), not a
separate watchdog-managed process: IMAP polling is lightweight I/O with no GPU
work and no multi-hour job risk, unlike TraceForge's agent runs, so it doesn't
need process isolation from an app-pool recycle."""
from __future__ import annotations

import asyncio
import email
import hashlib
import imaplib
import json
import logging
import random
import re
from datetime import datetime, timedelta
from email.header import decode_header
from email.message import Message
from email.utils import parsedate_to_datetime
from pathlib import Path

import backend.config as cfg
from backend.api.omnichannel import (
    CHANNELS,
    _ASSIGNEES,
    _SLA_HOURS,
    _create_in_servicenow_or_skip,
    _persist_created_tickets,
)

logger = logging.getLogger(__name__)

_LLM_TIMEOUT = 20  # seconds — bounds a single ticket's classification call, same rationale as omnichannel.py's _LLM_TIMEOUT

_URGENT_RE = re.compile(r"\b(down|outage|critical|urgent|p1|cannot access any|blocked|emergency)\b", re.IGNORECASE)
_HIGH_RE = re.compile(r"\b(locked out|not working|error|failure|failed|broken|unable to)\b", re.IGNORECASE)
_REQUEST_RE = re.compile(r"\b(request|please provide|need access|would like|can i get|license)\b", re.IGNORECASE)

_ASSIGNEE_KEYWORDS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bsap\b", re.IGNORECASE), "L2-SAP"),
    (re.compile(r"\b(vpn|network|wifi|firewall)\b", re.IGNORECASE), "L2-Network"),
    (re.compile(r"\b(password|mfa|login|account locked|sso)\b", re.IGNORECASE), "L1-Team Alpha"),
    (re.compile(r"\b(laptop|printer|hardware|monitor)\b", re.IGNORECASE), "L1-Team Beta"),
]

# No one submits a real support request from one of these — receipts, security
# alerts, and newsletters landing unread in the mailbox must not become tickets.
_AUTOMATED_SENDER_RE = re.compile(
    r"(no-?reply|do-?not-?reply|notifications?|newsletter|mailer-daemon|"
    r"postmaster|marketing|updates?|alerts?|receipts?|billing|donotreply)@",
    re.IGNORECASE,
)


# Function: _extract_email_address
def _extract_email_address(sender: str) -> str:
    """Pulls the bare address out of a '"Display Name" <addr@domain>' From
    header — filtering must match the actual address, not the free-text
    display name a sender can set to anything."""
    match = re.search(r"<([^<>]+)>", sender)
    return (match.group(1) if match else sender).strip().lower()


# Function: _sender_filter_reason
def _sender_filter_reason(sender: str) -> str | None:
    """Returns a reason string if this sender should be skipped (no ticket
    created), or None if the message should be ticketed normally."""
    address = _extract_email_address(sender)
    if not address:
        return None

    if cfg.EMAIL_IMAP_BLOCKED_SENDERS and any(
        address == b or (b.startswith("@") and address.endswith(b)) for b in cfg.EMAIL_IMAP_BLOCKED_SENDERS
    ):
        return "sender is on EMAIL_IMAP_BLOCKED_SENDERS"

    if cfg.EMAIL_IMAP_ALLOWED_SENDERS:
        if not any(
            address == a or (a.startswith("@") and address.endswith(a)) for a in cfg.EMAIL_IMAP_ALLOWED_SENDERS
        ):
            return "sender is not on EMAIL_IMAP_ALLOWED_SENDERS"
        return None  # explicitly allowlisted — skip the automated-sender heuristic below

    if cfg.EMAIL_IMAP_FILTER_AUTOMATED_SENDERS and _AUTOMATED_SENDER_RE.search(address):
        return "sender address matches automated/bulk-mail pattern"

    return None


# Function: _processed_ids_path
def _processed_ids_path() -> Path:
    return Path(cfg.DATA_DIR) / "email_intake_processed_ids.json"


# Function: _load_processed_ids
def _load_processed_ids() -> set[str]:
    path = _processed_ids_path()
    if not path.exists():
        return set()
    try:
        with path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
        return set(data) if isinstance(data, list) else set()
    except (json.JSONDecodeError, OSError):
        return set()


# Function: _save_processed_id
def _save_processed_id(msg_hash: str, known: set[str]) -> None:
    known.add(msg_hash)
    path = _processed_ids_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    # Cap the store so it can't grow unbounded across years of mail — dedup only
    # needs to cover messages IMAP could plausibly re-surface as UNSEEN, not
    # every message ever processed.
    trimmed = list(known)[-5000:]
    with path.open("w", encoding="utf-8") as fp:
        json.dump(trimmed, fp)


# Function: _message_hash
def _message_hash(msg: Message) -> str:
    """Message-ID is the standard dedup key; fall back to a content hash for
    the rare message that omits it rather than skipping dedup entirely."""
    message_id = msg.get("Message-ID")
    if message_id:
        return hashlib.sha256(message_id.encode("utf-8", "ignore")).hexdigest()
    fallback = f"{msg.get('From', '')}|{msg.get('Subject', '')}|{msg.get('Date', '')}"
    return hashlib.sha256(fallback.encode("utf-8", "ignore")).hexdigest()


# Function: _decode_header_value
def _decode_header_value(raw: str | None) -> str:
    if not raw:
        return ""
    parts = decode_header(raw)
    decoded = ""
    for text, charset in parts:
        if isinstance(text, bytes):
            decoded += text.decode(charset or "utf-8", errors="replace")
        else:
            decoded += text
    return decoded.strip()


# Function: _extract_plain_text_body
def _extract_plain_text_body(msg: Message) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition", "")):
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace").strip()
        return ""
    payload = msg.get_payload(decode=True)
    if not payload:
        return ""
    charset = msg.get_content_charset() or "utf-8"
    return payload.decode(charset, errors="replace").strip()


# Function: _classify_heuristic
def _classify_heuristic(subject: str, body: str) -> dict:
    """Deterministic keyword fallback — never fabricates a random priority for
    a real inbound support email the way the synthetic simulator does."""
    text = f"{subject} {body[:1000]}"
    if _URGENT_RE.search(text):
        priority = "P1"
    elif _HIGH_RE.search(text):
        priority = "P2"
    else:
        priority = "P3"
    category = "Service Request" if _REQUEST_RE.search(text) else "Incident"
    assignee = next((label for pattern, label in _ASSIGNEE_KEYWORDS if pattern.search(text)), None) or random.choice(_ASSIGNEES)
    return {
        "priority": priority,
        "category": category,
        "assignee": assignee,
        "summary": f"[Email] {subject}".strip()[:500],
    }


# Function: _classify_with_llm
def _classify_with_llm(subject: str, body: str) -> dict | None:
    try:
        from concurrent.futures import ThreadPoolExecutor
        from langchain_ollama import ChatOllama
        from backend.llm.router import assert_ollama_gpu_available

        assert_ollama_gpu_available(cfg.OLLAMA_MODEL)
        system_msg = (
            "You are an ITSM triage coordinator classifying one inbound support email. "
            "Return JSON only: {\"priority\": \"P1\"|\"P2\"|\"P3\"|\"P4\", "
            "\"category\": \"Incident\"|\"Service Request\"|\"Problem\"|\"Change\", "
            "\"assignee\": str, \"summary\": str (<=200 chars, what the requester needs)}. "
            "P1 = full outage/blocked/critical business impact, P2 = broken but has a workaround, "
            "P3 = routine issue, P4 = minor/cosmetic. Base the judgement only on the email content."
        )
        user_msg = f"SUBJECT: {subject}\n\nBODY:\n{body[:2000]}"
        llm = ChatOllama(
            model=cfg.OLLAMA_MODEL, base_url=cfg.OLLAMA_BASE_URL,
            temperature=0.1, num_predict=256, format="json",
            timeout=_LLM_TIMEOUT, keep_alive=cfg.OLLAMA_KEEP_ALIVE,
        )
        # Same "abandon, don't wait" rationale as omnichannel.py's _call_llm — a
        # wedged Ollama must not hang the whole poll loop.
        pool = ThreadPoolExecutor(max_workers=1)
        future = pool.submit(llm.invoke, [("system", system_msg), ("human", user_msg)])
        try:
            res = future.result(timeout=_LLM_TIMEOUT)
        finally:
            pool.shutdown(wait=False)
        text = res.content if hasattr(res, "content") else str(res)
        text = (text or "").strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
            text = re.sub(r"\s*```$", "", text)
        parsed = json.loads(text)
        if parsed.get("priority") not in {"P1", "P2", "P3", "P4"}:
            return None
        parsed.setdefault("category", "Incident")
        parsed.setdefault("assignee", random.choice(_ASSIGNEES))
        parsed.setdefault("summary", f"[Email] {subject}".strip()[:500])
        return parsed
    except Exception as exc:  # noqa: BLE001 — classification is best-effort; heuristic fallback covers this
        logger.warning("Email intake: LLM classification failed, using heuristic: %s", exc)
        return None


# Function: _build_ticket
def _build_ticket(sender: str, subject: str, body: str, received_at: datetime) -> dict:
    subject = subject or "(no subject)"
    classification = _classify_with_llm(subject, body) or _classify_heuristic(subject, body)
    priority = classification["priority"]
    sla_deadline = received_at + timedelta(hours=_SLA_HOURS[priority])
    return {
        "ticket_id": f"INC{received_at.strftime('%Y%m%d')}{random.randint(1000, 9999)}",
        "channel": "email",
        "channel_label": CHANNELS["email"]["label"],
        "subject": subject[:500],
        "priority": priority,
        "status": "Open",
        "created_at": received_at.isoformat() + "Z",
        "sla_deadline": sla_deadline.isoformat() + "Z",
        "sla_hours": _SLA_HOURS[priority],
        "auto_classified": True,
        "ai_summary": f"{classification['summary']} (from {sender})",
        "suggested_assignee": classification["assignee"],
        "similar_ticket_count": 0,
        "confidence_score": None,
        "category": classification["category"],
        "sub_category": "Email",
    }


# Function: _fetch_and_create_tickets
def _fetch_and_create_tickets() -> list[dict]:
    """Blocking IMAP fetch — always run via asyncio.to_thread. Returns tickets
    successfully built from newly-seen messages (creation/persistence happens
    in the async caller so it can share the same event loop as the rest of
    the app instead of opening a second one here)."""
    processed = _load_processed_ids()
    tickets: list[dict] = []

    imap_cls = imaplib.IMAP4_SSL if cfg.EMAIL_IMAP_USE_SSL else imaplib.IMAP4
    conn = imap_cls(cfg.EMAIL_IMAP_HOST, cfg.EMAIL_IMAP_PORT)
    try:
        conn.login(cfg.EMAIL_IMAP_USERNAME, cfg.EMAIL_IMAP_PASSWORD)
        conn.select(cfg.EMAIL_IMAP_FOLDER)
        status, data = conn.search(None, "UNSEEN")
        if status != "OK":
            logger.warning("Email intake: IMAP search failed: %s", status)
            return tickets

        message_nums = data[0].split() if data and data[0] else []
        for num in message_nums:
            status, msg_data = conn.fetch(num, "(RFC822)")
            if status != "OK" or not msg_data or not msg_data[0]:
                continue
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            msg_hash = _message_hash(msg)
            if msg_hash in processed:
                conn.store(num, "+FLAGS", "\\Seen")
                continue

            subject = _decode_header_value(msg.get("Subject"))
            sender = _decode_header_value(msg.get("From"))

            skip_reason = _sender_filter_reason(sender)
            if skip_reason:
                logger.info("Email intake: skipping message from %s (%s): %s", sender, skip_reason, subject)
                conn.store(num, "+FLAGS", "\\Seen")
                _save_processed_id(msg_hash, processed)
                continue

            body = _extract_plain_text_body(msg)
            try:
                received_at = parsedate_to_datetime(msg.get("Date")) if msg.get("Date") else datetime.utcnow()
                if received_at.tzinfo is not None:
                    received_at = received_at.replace(tzinfo=None)
            except (TypeError, ValueError):
                received_at = datetime.utcnow()

            try:
                ticket = _build_ticket(sender, subject, body, received_at)
            except Exception as exc:  # noqa: BLE001 — one malformed email must not stall the whole poll
                logger.warning("Email intake: failed to build ticket for message %s: %s", msg_hash[:12], exc)
                continue

            tickets.append(ticket)
            # Only mark \Seen + record processed once the ticket is actually
            # queued for creation — if creation fails downstream (ServiceNow
            # unreachable), the caller must leave this message alone so the
            # next poll retries it instead of silently losing it.
            ticket["_msg_hash"] = msg_hash
            ticket["_imap_num"] = num
    finally:
        try:
            conn.logout()
        except Exception:  # noqa: BLE001 — best-effort cleanup only
            pass

    return tickets


# Function: _mark_processed
def _mark_processed(tickets: list[dict]) -> None:
    """Marks \\Seen and records dedup ids for tickets that were successfully
    created — re-opens the IMAP connection since the fetch connection above
    already closed; a second short-lived connection is simpler and safer than
    holding one open across the ServiceNow round-trip."""
    successful = [t for t in tickets if t.get("servicenow", {}).get("status") == "created"]
    if not successful:
        return
    processed = _load_processed_ids()
    imap_cls = imaplib.IMAP4_SSL if cfg.EMAIL_IMAP_USE_SSL else imaplib.IMAP4
    conn = imap_cls(cfg.EMAIL_IMAP_HOST, cfg.EMAIL_IMAP_PORT)
    try:
        conn.login(cfg.EMAIL_IMAP_USERNAME, cfg.EMAIL_IMAP_PASSWORD)
        conn.select(cfg.EMAIL_IMAP_FOLDER)
        for ticket in successful:
            try:
                conn.store(ticket["_imap_num"], "+FLAGS", "\\Seen")
            except Exception as exc:  # noqa: BLE001 — dedup store below still prevents a duplicate ticket
                logger.warning("Email intake: failed to mark message %s seen: %s", ticket.get("_imap_num"), exc)
            _save_processed_id(ticket["_msg_hash"], processed)
    finally:
        try:
            conn.logout()
        except Exception:  # noqa: BLE001
            pass


# Function: poll_once
async def poll_once() -> int:
    """Runs one fetch-classify-create cycle. Returns the number of tickets
    actually created in ServiceNow. Exposed separately from the loop so it can
    be triggered on demand (e.g. a manual 'check now' admin action) later."""
    tickets = await asyncio.to_thread(_fetch_and_create_tickets)
    if not tickets:
        return 0

    servicenow_results = await _create_in_servicenow_or_skip(tickets)
    for ticket, sn in zip(tickets, servicenow_results):
        ticket["servicenow"] = sn

    created = sum(1 for sn in servicenow_results if sn["status"] == "created")
    if created:
        logger.info("Email intake: created %d ticket(s) from inbound mail.", created)
    failed = [t for t, sn in zip(tickets, servicenow_results) if sn["status"] != "created"]
    if failed:
        logger.warning(
            "Email intake: %d message(s) fetched but not ticketed (will retry next poll): %s",
            len(failed), [f.get("subject") for f in failed],
        )

    await asyncio.to_thread(_persist_created_tickets, tickets)
    await asyncio.to_thread(_mark_processed, tickets)
    return created


# Function: run_email_poll_loop
async def run_email_poll_loop() -> None:
    """Background task started from main.py's lifespan. Never raises — a
    single bad poll (mailbox unreachable, IMAP auth failure, etc.) is logged
    and retried on the next interval rather than killing the whole app."""
    if not cfg.EMAIL_IMAP_ENABLED:
        logger.info("Email intake: disabled (EMAIL_IMAP_ENABLED=false).")
        return
    if not (cfg.EMAIL_IMAP_HOST and cfg.EMAIL_IMAP_USERNAME and cfg.EMAIL_IMAP_PASSWORD):
        logger.info("Email intake: EMAIL_IMAP_USERNAME/PASSWORD not configured — Email channel poller not started.")
        return

    logger.info(
        "Email intake: polling %s@%s:%s/%s every %ss.",
        cfg.EMAIL_IMAP_USERNAME, cfg.EMAIL_IMAP_HOST, cfg.EMAIL_IMAP_PORT,
        cfg.EMAIL_IMAP_FOLDER, cfg.EMAIL_IMAP_POLL_SECONDS,
    )
    while True:
        try:
            await poll_once()
        except Exception as exc:  # noqa: BLE001 — must never take the poll loop down
            logger.warning("Email intake: poll cycle failed: %s", exc)
        await asyncio.sleep(cfg.EMAIL_IMAP_POLL_SECONDS)
