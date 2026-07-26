# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Communications tool mocks — email, Slack, SMS, portal notifications.
# Date: 2026-04-28
# ---------------------------------------------------------------------------
"""Communications tool mocks — email, Slack, SMS, portal notifications."""
from __future__ import annotations

import asyncio
import uuid


# Function: send_email
async def send_email(
    to: str | list[str],
    subject: str,
    body: str,
    cc: list[str] | None = None,
    priority: str = "normal",
) -> dict:
    """Send email notification."""
    await asyncio.sleep(0)
    recipients = [to] if isinstance(to, str) else to
    return {
        "message_id": f"EMAIL-{str(uuid.uuid4())[:8].upper()}",
        "to": recipients,
        "cc": cc or [],
        "subject": subject,
        "priority": priority,
        "sent": True,
        "sent_at": "2026-06-27T10:00:00Z",
    }


# Function: send_slack
async def send_slack(
    channel: str,
    message: str,
    mention_users: list[str] | None = None,
    blocks: list[dict] | None = None,
) -> dict:
    """Post to Slack channel."""
    await asyncio.sleep(0)
    return {
        "ts": "1719480000.000001",
        "channel": channel,
        "message_preview": message[:80],
        "mention_users": mention_users or [],
        "sent": True,
    }


# Function: send_sms
async def send_sms(phone: str, message: str, priority: str = "normal") -> dict:
    """Send SMS alert."""
    await asyncio.sleep(0)
    return {
        "sms_id": f"SMS-{str(uuid.uuid4())[:8].upper()}",
        "to": phone,
        "message_preview": message[:50],
        "sent": True,
        "sent_at": "2026-06-27T10:00:00Z",
        "priority": priority,
    }


# Function: create_jira_ticket
async def create_jira_ticket(
    project: str,
    issue_type: str,
    summary: str,
    description: str,
    assignee: str | None = None,
    priority: str = "High",
) -> dict:
    """Create a Jira ticket for escalation tracking."""
    await asyncio.sleep(0)
    ticket_key = f"{project}-{str(uuid.uuid4())[:4].upper()}"
    return {
        "ticket_key": ticket_key,
        "project": project,
        "issue_type": issue_type,
        "summary": summary,
        "assignee": assignee,
        "priority": priority,
        "status": "Open",
        "url": f"https://jira.example.com/browse/{ticket_key}",
        "created_at": "2026-06-27T10:00:00Z",
    }


# Function: send_portal_notification
async def send_portal_notification(
    user_id: str,
    title: str,
    body: str,
    severity: str = "info",
    action_url: str | None = None,
) -> dict:
    """Send in-app portal notification."""
    await asyncio.sleep(0)
    return {
        "notification_id": f"NOTIF-{str(uuid.uuid4())[:8].upper()}",
        "user_id": user_id,
        "title": title,
        "severity": severity,
        "action_url": action_url,
        "delivered": True,
        "delivered_at": "2026-06-27T10:00:00Z",
    }


# Function: escalate_to_management
async def escalate_to_management(
    incident_id: str,
    severity: str,
    summary: str,
    notify_users: list[str],
) -> dict:
    """Escalate incident to management tier via multiple channels."""
    await asyncio.sleep(0)
    results = []
    for user in notify_users:
        results.append({
            "user": user,
            "channels": ["email", "slack"],
            "sent": True,
        })
    return {
        "incident_id": incident_id,
        "escalated": True,
        "severity": severity,
        "notified": results,
        "escalated_at": "2026-06-27T10:00:00Z",
    }
