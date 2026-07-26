# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Creates real ServiceNow incidents from Omnichannel Ticket Intake simulations.
# Date: 2026-06-30
# ---------------------------------------------------------------------------
"""
Creates real ServiceNow incidents from Omnichannel Ticket Intake simulations.
Every simulated ticket becomes a real `incident` table record — the omnichannel
simulator's "category" field (Incident/Service Request/Problem/Change) is UI
flavor only, not a distinct target table; ServiceNow's incident table is the
only one written to here.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# ServiceNow priority is a 1 (Critical) – 5 (Planning) choice list; the omnichannel
# simulator's P1-P4 scale maps directly onto the top four.
PRIORITY_TO_SN = {"P1": "1", "P2": "2", "P3": "3", "P4": "4"}

# OOB `contact_type` choice list values — chat has no exact OOB match, "virtual agent"
# is the closest built-in choice for a bot/chat-originated ticket.
_CHANNEL_TO_CONTACT_TYPE = {
    "web_portal": "self-service",
    "email": "email",
    "chat": "virtual agent",
    "phone": "phone",
    "mobile": "self-service",
    "monitoring": "self-service",
    "api": "self-service",
}


# Function: _ticket_to_incident_payload
def _ticket_to_incident_payload(ticket: dict) -> dict:
    priority = PRIORITY_TO_SN.get(ticket.get("priority"), "3")
    return {
        "short_description": ticket.get("subject", "Untitled ticket"),
        "description": (
            f"{ticket.get('ai_summary', '')}\n\n"
            f"Source channel: {ticket.get('channel_label', ticket.get('channel', 'Unknown'))}\n"
            f"Suggested assignee: {ticket.get('suggested_assignee', 'Unassigned')}\n"
            f"AI confidence: {ticket.get('confidence_score', 'n/a')}\n"
            f"Simulated by Novastra-ITSM Omnichannel Ticket Intake — external ticket ref {ticket.get('ticket_id', 'n/a')}."
        ),
        "priority": priority,
        "urgency": priority,
        "impact": priority,
        "contact_type": _CHANNEL_TO_CONTACT_TYPE.get(ticket.get("channel"), "self-service"),
        # ServiceNow's own default for a new incident is state=1 ("New") anyway, but set
        # it explicitly — "New" is what the dashboard's normalize_state() maps to "Open",
        # and every simulated ticket must start Open regardless of what the instance's
        # own default happens to be configured as.
        "state": "1",
    }


# Function: create_incident
async def create_incident(
    client: httpx.AsyncClient,
    base_url: str,
    username: str,
    password: str,
    ticket: dict,
) -> dict[str, Any]:
    """POSTs one simulated ticket to ServiceNow as a real incident. Never raises —
    failures are returned in the result dict so a batch simulate can report a
    per-ticket outcome instead of failing the whole request over one bad ticket."""
    payload = _ticket_to_incident_payload(ticket)
    url = f"{base_url.rstrip('/')}/api/now/table/incident"
    try:
        response = await client.post(
            url, json=payload, auth=(username, password),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
    except httpx.HTTPError as exc:
        logger.warning("ServiceNow incident create failed for %s: %s", ticket.get("ticket_id"), exc)
        return {"status": "failed", "error": f"Transport error: {exc}", "number": None, "sys_id": None}

    if response.status_code not in (200, 201):
        logger.warning(
            "ServiceNow incident create for %s returned HTTP %s: %s",
            ticket.get("ticket_id"), response.status_code, response.text[:200],
        )
        return {
            "status": "failed",
            "error": f"HTTP {response.status_code}: {response.text[:200]}",
            "number": None, "sys_id": None,
        }

    try:
        result = response.json().get("result", {})
    except Exception as exc:  # noqa: BLE001 — malformed JSON degrades to a reported failure, not a crash
        return {"status": "failed", "error": f"Unparseable ServiceNow response: {exc}", "number": None, "sys_id": None}

    return {"status": "created", "error": None, "number": result.get("number"), "sys_id": result.get("sys_id")}


# Function: create_incidents_batch
async def create_incidents_batch(
    base_url: str, username: str, password: str, tickets: list[dict],
    timeout_seconds: int, verify_ssl: bool, max_concurrency: int = 5,
) -> list[dict[str, Any]]:
    """Creates one ServiceNow incident per ticket, bounded-concurrent so a burst of
    up to 30 simulated tickets doesn't serialize into a multi-minute request against
    a (possibly slow) ServiceNow instance."""
    semaphore = asyncio.Semaphore(max_concurrency)

    # Function: _bounded
    async def _bounded(client: httpx.AsyncClient, ticket: dict) -> dict:
        async with semaphore:
            return await create_incident(client, base_url, username, password, ticket)

    async with httpx.AsyncClient(timeout=timeout_seconds, verify=verify_ssl) as client:
        return await asyncio.gather(*(_bounded(client, t) for t in tickets))
