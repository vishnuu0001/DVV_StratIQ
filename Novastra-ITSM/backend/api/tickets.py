# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — backend/api (tickets.py)
# Date: 2025-09-08
# ---------------------------------------------------------------------------
from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, HTTPException
from backend.api.auth import get_current_user
from backend.services.operational_ingestion import get_all_incidents

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])

# Realistic ITSM sample tickets spanning all AI-feature categories
_SAMPLE_TICKETS = [
    {
        "number": "INC0012345",
        "sys_id": "a1b2c3d4e5f6000001",
        "category": "Network",
        "subcategory": "VPN",
        "short_description": "Unable to connect to VPN from remote location",
        "description": (
            "User John Smith reports inability to connect to corporate VPN from home. "
            "Error message: 'Authentication failed — check credentials'. "
            "VPN client: Cisco AnyConnect 4.10. OS: Windows 11 22H2. "
            "Issue started after Windows cumulative update KB5034441 installed on 2026-06-17. "
            "User has verified credentials are correct and can log into Office 365 without issue."
        ),
        "priority": "2 - High",
        "urgency": "2 - Medium",
        "impact": "2 - Medium",
        "state": "Open",
        "opened_at": "2026-06-18T08:30:00Z",
        "caller_id": "john.smith@company.com",
        "caller_name": "John Smith",
        "assigned_to": "",
        "assignment_group": "Network Operations",
        "cmdb_ci": "VPN-GATEWAY-PROD-01",
        "sla_due": "2026-06-18T20:30:00Z",
        "age_hours": 4.5,
        "work_notes": "Checked VPN gateway logs — multiple auth failures from this user since 08:30. Possible certificate issue after Windows update.",
        "resolution_notes": "",
    },
    {
        "number": "INC0012346",
        "sys_id": "a1b2c3d4e5f6000002",
        "category": "Access",
        "subcategory": "Password Reset",
        "short_description": "Account locked after multiple failed login attempts",
        "description": (
            "User Sarah Johnson (sarah.johnson@company.com) has been locked out of Active Directory account "
            "after 5 failed login attempts. User states she changed her password last week and may be using the old one "
            "on mobile devices. She also requires access to the HR self-service portal. "
            "Manager: Michael Davis. Department: Human Resources. Location: London HQ."
        ),
        "priority": "3 - Medium",
        "urgency": "3 - Medium",
        "impact": "3 - Medium",
        "state": "In Progress",
        "opened_at": "2026-06-18T09:15:00Z",
        "caller_id": "sarah.johnson@company.com",
        "caller_name": "Sarah Johnson",
        "assigned_to": "Level 1 Support",
        "assignment_group": "IT Service Desk",
        "cmdb_ci": "AD-DOMAIN-CONTROLLER-01",
        "sla_due": "2026-06-19T09:15:00Z",
        "age_hours": 3.75,
        "work_notes": "Unlocked AD account. Advised user to update saved passwords on all mobile devices.",
        "resolution_notes": "",
    },
    {
        "number": "INC0012347",
        "sys_id": "a1b2c3d4e5f6000003",
        "category": "Software",
        "subcategory": "Business Application",
        "short_description": "SAP ERP extremely slow — production users unable to process orders",
        "description": (
            "Multiple users (approx. 45) reporting SAP ERP system response times of 30–60 seconds per transaction. "
            "Normal response time is under 2 seconds. Issue started at approximately 07:00 this morning. "
            "SAP SM50/SM66 shows high DB wait times. Recent change CHG0004521 (DB index rebuild) was "
            "completed at 06:45 by the DBA team. Production environment. Business impact: order processing stopped."
        ),
        "priority": "1 - Critical",
        "urgency": "1 - Critical",
        "impact": "1 - Critical",
        "state": "Open",
        "opened_at": "2026-06-18T07:05:00Z",
        "caller_id": "operations.manager@company.com",
        "caller_name": "Ops Manager",
        "assigned_to": "SAP Basis Team",
        "assignment_group": "SAP Operations",
        "cmdb_ci": "SAP-ERP-PROD-01",
        "sla_due": "2026-06-18T11:05:00Z",
        "age_hours": 5.9,
        "work_notes": "SAP Basis investigating. Likely correlation with DB index rebuild CHG0004521. DBA team reviewing index stats.",
        "resolution_notes": "",
    },
    {
        "number": "INC0012348",
        "sys_id": "a1b2c3d4e5f6000004",
        "category": "Software",
        "subcategory": "Email",
        "short_description": "Microsoft Outlook not syncing emails — inbox stuck at 09:00",
        "description": (
            "User David Chen reports Outlook (Microsoft 365 version 2405) stopped syncing new emails at 09:00. "
            "Emails visible in OWA (web client) but not appearing in desktop Outlook. "
            "Tried restarting Outlook and running the OST repair tool — no improvement. "
            "Also affects Microsoft Teams notifications. OS: macOS Sonoma 14.5."
        ),
        "priority": "4 - Low",
        "urgency": "4 - Low",
        "impact": "4 - Low",
        "state": "Open",
        "opened_at": "2026-06-18T10:45:00Z",
        "caller_id": "david.chen@company.com",
        "caller_name": "David Chen",
        "assigned_to": "",
        "assignment_group": "End User Computing",
        "cmdb_ci": "M365-EXCHANGE-ONLINE",
        "sla_due": "2026-06-25T10:45:00Z",
        "age_hours": 2.25,
        "work_notes": "",
        "resolution_notes": "",
    },
    {
        "number": "INC0012349",
        "sys_id": "a1b2c3d4e5f6000005",
        "category": "Hardware",
        "subcategory": "Printer",
        "short_description": "HP LaserJet offline on Floor 3 — printing not possible for 12 users",
        "description": (
            "The shared HP LaserJet Pro M479 on Floor 3 (Asset: PRN-F3-001) shows as offline in the print queue "
            "for all 12 users in the Finance department. Printer shows a paper jam error on its display but paper "
            "jam was cleared 30 minutes ago. Printer was working normally until this morning. "
            "IP: 10.10.3.45. Network switch port: SW3-F3/24."
        ),
        "priority": "3 - Medium",
        "urgency": "3 - Medium",
        "impact": "2 - Medium",
        "state": "Open",
        "opened_at": "2026-06-18T11:00:00Z",
        "caller_id": "finance.admin@company.com",
        "caller_name": "Finance Admin",
        "assigned_to": "",
        "assignment_group": "Desktop Support",
        "cmdb_ci": "PRN-F3-001",
        "sla_due": "2026-06-19T11:00:00Z",
        "age_hours": 2.0,
        "work_notes": "",
        "resolution_notes": "",
    },
    {
        "number": "INC0012350",
        "sys_id": "a1b2c3d4e5f6000006",
        "category": "Database",
        "subcategory": "Connectivity",
        "short_description": "Oracle DB connection timeout causing CRM application failures",
        "description": (
            "CRM application (Salesforce on-prem) is throwing ORA-12170 TNS connection timeout errors. "
            "Error rate is 40% of all DB calls since 06:00. Oracle DB server CPU at 98%, memory 94%. "
            "DBA identified long-running queries from overnight batch job that did not complete. "
            "Approximately 300 users affected. Revenue impact estimated at £15k/hour."
        ),
        "priority": "1 - Critical",
        "urgency": "1 - Critical",
        "impact": "1 - Critical",
        "state": "In Progress",
        "opened_at": "2026-06-18T06:15:00Z",
        "caller_id": "crm.admin@company.com",
        "caller_name": "CRM Admin",
        "assigned_to": "Oracle DBA",
        "assignment_group": "Database Operations",
        "cmdb_ci": "ORA-DB-CRM-PROD-01",
        "sla_due": "2026-06-18T10:15:00Z",
        "age_hours": 6.75,
        "work_notes": "DBA killed runaway batch queries. DB CPU dropped to 65%. Monitoring recovery.",
        "resolution_notes": "",
    },
    {
        "number": "INC0012351",
        "sys_id": "a1b2c3d4e5f6000007",
        "category": "Hardware",
        "subcategory": "Laptop",
        "short_description": "Laptop battery draining to zero within 2 hours — brand new Dell XPS",
        "description": (
            "User Emma Wilson received a new Dell XPS 15 9530 (Asset: LPT-00567) 2 weeks ago. "
            "Battery life has progressively worsened — now only 2 hours from full charge. "
            "Windows battery report shows 'Battery capacity degradation: 48%' which is abnormal for a new device. "
            "Dell warranty serial: 8XYZ3K1. User is field sales and cannot be plugged in during client visits."
        ),
        "priority": "4 - Low",
        "urgency": "3 - Medium",
        "impact": "4 - Low",
        "state": "Open",
        "opened_at": "2026-06-17T14:00:00Z",
        "caller_id": "emma.wilson@company.com",
        "caller_name": "Emma Wilson",
        "assigned_to": "",
        "assignment_group": "Desktop Support",
        "cmdb_ci": "LPT-00567",
        "sla_due": "2026-06-24T14:00:00Z",
        "age_hours": 19.0,
        "work_notes": "",
        "resolution_notes": "",
    },
    {
        "number": "INC0012352",
        "sys_id": "a1b2c3d4e5f6000008",
        "category": "Software",
        "subcategory": "Collaboration",
        "short_description": "Microsoft Teams cannot join or start video meetings — black screen",
        "description": (
            "User Robert Taylor and 8 other users on macOS report that Microsoft Teams shows a black screen "
            "when attempting to join or start video meetings. Audio works but video is completely black. "
            "Camera works correctly in FaceTime and Zoom. Teams version 24112.300.3130.3590. "
            "Issue started after macOS Sonoma 14.5 update deployed via MDM on 2026-06-17. "
            "Affected users all received the same MDM update."
        ),
        "priority": "2 - High",
        "urgency": "2 - Medium",
        "impact": "2 - Medium",
        "state": "Open",
        "opened_at": "2026-06-18T08:00:00Z",
        "caller_id": "robert.taylor@company.com",
        "caller_name": "Robert Taylor",
        "assigned_to": "",
        "assignment_group": "End User Computing",
        "cmdb_ci": "M365-TEAMS",
        "sla_due": "2026-06-18T20:00:00Z",
        "age_hours": 5.0,
        "work_notes": "Possible Teams permissions conflict with macOS camera privacy settings post-update.",
        "resolution_notes": "",
    },
    {
        "number": "INC0012353",
        "sys_id": "a1b2c3d4e5f6000009",
        "category": "Security",
        "subcategory": "Suspicious Activity",
        "short_description": "Multiple failed login attempts detected on admin account — possible brute force",
        "description": (
            "SIEM alert triggered at 03:15 — 847 failed login attempts against admin account "
            "'svc-sap-admin' from IP 185.220.101.47 (Tor exit node) over a 15-minute window. "
            "Account has been automatically locked by Azure AD Conditional Access. "
            "No successful logins recorded. Source IP is on threat intelligence blocklist. "
            "This account has elevated privileges to SAP production environment."
        ),
        "priority": "1 - Critical",
        "urgency": "1 - Critical",
        "impact": "1 - Critical",
        "state": "In Progress",
        "opened_at": "2026-06-18T03:20:00Z",
        "caller_id": "soc@company.com",
        "caller_name": "SOC Team",
        "assigned_to": "Security Operations",
        "assignment_group": "Cyber Security",
        "cmdb_ci": "AD-DOMAIN-CONTROLLER-01",
        "sla_due": "2026-06-18T07:20:00Z",
        "age_hours": 9.7,
        "work_notes": "Account locked. Source IP blocked at firewall. MFA review in progress. Notified CISO.",
        "resolution_notes": "",
    },
    {
        "number": "INC0012354",
        "sys_id": "a1b2c3d4e5f6000010",
        "category": "Performance",
        "subcategory": "Server",
        "short_description": "Web server CPU pegged at 100% — portal loading times exceeding 30 seconds",
        "description": (
            "Customer-facing self-service portal (portal.company.com) experiencing severe performance degradation. "
            "Server WEB-PROD-02 CPU at 100% for past 2 hours. Load balancer health checks failing — "
            "server removed from pool. Root cause suspected: memory leak in new portal release v2.4.1 "
            "deployed at 04:00 by the DevOps team via automated pipeline. "
            "3,200 customers impacted. Customer complaints via Twitter increasing."
        ),
        "priority": "1 - Critical",
        "urgency": "1 - Critical",
        "impact": "1 - Critical",
        "state": "In Progress",
        "opened_at": "2026-06-18T05:00:00Z",
        "caller_id": "devops@company.com",
        "caller_name": "DevOps Team",
        "assigned_to": "Application Support",
        "assignment_group": "Web Operations",
        "cmdb_ci": "WEB-PROD-02",
        "sla_due": "2026-06-18T09:00:00Z",
        "age_hours": 8.0,
        "work_notes": "Rollback of v2.4.1 initiated. Server restarted. CPU normalizing. Monitoring.",
        "resolution_notes": "",
    },
    {
        "number": "INC0012355",
        "sys_id": "a1b2c3d4e5f6000011",
        "category": "Access",
        "subcategory": "File Share",
        "short_description": "Finance team cannot access shared drive after department move",
        "description": (
            "Following the departmental restructure on 2026-06-15, the Finance team (23 users) "
            "were moved to new OU 'OU=Finance-EMEA,DC=company,DC=com'. "
            "They can no longer access the shared drive \\\\fileserver01\\Finance. "
            "Error: 'Access Denied'. Investigation needed to verify AD group membership migration. "
            "Manager: Christine Lee (christine.lee@company.com). Month-end reporting is due tomorrow."
        ),
        "priority": "2 - High",
        "urgency": "1 - Critical",
        "impact": "2 - Medium",
        "state": "Open",
        "opened_at": "2026-06-18T09:30:00Z",
        "caller_id": "christine.lee@company.com",
        "caller_name": "Christine Lee",
        "assigned_to": "",
        "assignment_group": "IT Service Desk",
        "cmdb_ci": "FILESERVER01",
        "sla_due": "2026-06-18T21:30:00Z",
        "age_hours": 3.5,
        "work_notes": "",
        "resolution_notes": "",
    },
    {
        "number": "INC0012356",
        "sys_id": "a1b2c3d4e5f6000012",
        "category": "Hardware",
        "subcategory": "Monitor",
        "short_description": "Dual monitor setup not detected after docking station replacement",
        "description": (
            "User Thomas Brown had his docking station (Dell WD19S) replaced under warranty on 2026-06-16. "
            "The new docking station only drives one monitor; the second monitor is not detected. "
            "Previously used dual 27\" Dell monitors via DisplayPort. Laptop: Dell Latitude 5540, "
            "OS: Windows 11 23H2. Driver reinstall attempted — no change. "
            "New docking station firmware: 01.00.05."
        ),
        "priority": "4 - Low",
        "urgency": "4 - Low",
        "impact": "4 - Low",
        "state": "Open",
        "opened_at": "2026-06-17T16:00:00Z",
        "caller_id": "thomas.brown@company.com",
        "caller_name": "Thomas Brown",
        "assigned_to": "",
        "assignment_group": "Desktop Support",
        "cmdb_ci": "LPT-00489",
        "sla_due": "2026-06-24T16:00:00Z",
        "age_hours": 17.0,
        "work_notes": "",
        "resolution_notes": "",
    },
]


# Function: _matches
def _matches(ticket: dict, q: str) -> bool:
    if not q:
        return True
    ql = q.lower()
    return (
        ql in ticket["number"].lower()
        or ql in ticket["short_description"].lower()
        or ql in ticket["category"].lower()
        or ql in ticket["subcategory"].lower()
        or ql in ticket.get("caller_name", "").lower()
        or ql in ticket.get("state", "").lower()
        or ql in ticket.get("assignment_group", "").lower()
    )


# Function: search_tickets
@router.get("/search")
async def search_tickets(
    q: str = Query("", description="Search term: number, keyword, or category"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        from fastapi import HTTPException
        raise HTTPException(status_code=401)
    try:
        results, total = get_all_incidents(
            limit=limit, offset=offset, search=q.strip() or None,
        )
        if total > 0:
            return {
                "tickets": results, "total": total, "limit": limit, "offset": offset,
                "has_more": offset + len(results) < total, "source": "operational_store",
            }

        # Do not inject demo tickets for an empty search result when the operational
        # store itself is populated.
        if q.strip():
            _, store_total = get_all_incidents(limit=1, offset=0)
            if store_total > 0:
                return {
                    "tickets": [], "total": 0, "limit": limit, "offset": offset,
                    "has_more": False, "source": "operational_store",
                }
    except Exception:
        # Demo/local installations retain the curated sample fallback when no
        # operational database is configured.
        pass

    matches = [ticket for ticket in _SAMPLE_TICKETS if _matches(ticket, q)]
    results = matches[offset:offset + limit]
    return {
        "tickets": results, "total": len(matches), "limit": limit, "offset": offset,
        "has_more": offset + len(results) < len(matches), "source": "sample_fallback",
    }


# Function: get_ticket
@router.get("/{number}")
async def get_ticket(
    number: str,
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401)
    number = number.upper()
    try:
        incidents, _ = get_all_incidents(limit=25, offset=0, search=number)
        for incident in incidents:
            if str(incident.get("number") or "").upper() == number:
                return incident
    except Exception:
        pass
    for t in _SAMPLE_TICKETS:
        if t["number"] == number:
            return t
    raise HTTPException(status_code=404, detail=f"Ticket {number} not found")
