# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: services/bcdr_analysis.py
# Date: 2026-04-16
# ---------------------------------------------------------------------------
"""
services/bcdr_analysis.py
Disaster Recovery & BCDR Gap Analysis.

Features:
  - SPOF detection: servers with no HA pair and ha_dr_requirements != None
  - Backup coverage check: backup agents detected via SSH/WinRM workload scan
  - RTO/RPO feasibility: given current architecture, is the stated RTO achievable?
  - Recovery readiness score: per-server score (0-100)
"""
from __future__ import annotations

import logging
from datetime import date
from typing import Any

log = logging.getLogger(__name__)

# ── RTO/RPO feasibility thresholds ──────────────────────────────────────────
# Maps RTO string → minimum required infrastructure features
_RTO_REQUIREMENTS: dict[str, dict] = {
    "<15min":  {"requires_ha": True,  "requires_replication": True,  "requires_lb": True,  "max_acceptable_tier": "Active-Active"},
    "<1h":     {"requires_ha": True,  "requires_replication": True,  "requires_lb": False, "max_acceptable_tier": "Active-Passive"},
    "<4h":     {"requires_ha": True,  "requires_replication": False, "requires_lb": False, "max_acceptable_tier": "Cold-Standby"},
    "<24h":    {"requires_ha": False, "requires_replication": False, "requires_lb": False, "max_acceptable_tier": "None"},
    "best-effort": {"requires_ha": False, "requires_replication": False, "requires_lb": False, "max_acceptable_tier": "None"},
}

_RPO_REQUIREMENTS: dict[str, dict] = {
    "<15min":  {"requires_replication": True,  "backup_frequency": "continuous"},
    "<1h":     {"requires_replication": True,  "backup_frequency": "hourly"},
    "<4h":     {"requires_replication": False, "backup_frequency": "4hourly"},
    "<24h":    {"requires_replication": False, "backup_frequency": "daily"},
    "best-effort": {"requires_replication": False, "backup_frequency": "weekly"},
}

# HA DR tier order (best → worst)
_HA_TIER_ORDER = ["Active-Active", "Active-Passive", "Cold-Standby", "None", ""]

# Known backup agent software names (detected in installed_software)
_BACKUP_AGENTS = [
    "veeam", "commvault", "arcserve", "veritas netbackup", "netbackup",
    "dell emc networker", "networker", "cohesity", "rubrik", "zerto",
    "azure backup", "aws backup", "google cloud backup", "bacula",
    "amanda", "rsync", "duplicati", "bareos", "restic", "borg",
    "windows server backup", "wbadmin", "backup exec",
]


# Function: _server_id
def _server_id(srv: dict) -> str:
    return (srv.get("server_ip") or srv.get("ip_address") or srv.get("ip") or
            srv.get("server_name") or srv.get("name") or "unknown")


# Function: _server_name
def _server_name(srv: dict) -> str:
    return srv.get("server_name") or srv.get("name") or _server_id(srv)


# Function: _normalize_rto_rpo
def _normalize_rto_rpo(val: str | None) -> str:
    """Normalize RTO/RPO string to canonical form."""
    if not val:
        return ""
    val = val.lower().strip()
    for key in _RTO_REQUIREMENTS:
        if key in val or val in key:
            return key
    if "best" in val or "effort" in val:
        return "best-effort"
    return val


# Function: _has_backup_agent
def _has_backup_agent(srv: dict) -> tuple[bool, str]:
    """Check if backup agent is present in installed software."""
    for sw in (srv.get("installed_software") or []):
        sw_name = (sw.get("name") or "").lower()
        for agent in _BACKUP_AGENTS:
            if agent in sw_name:
                return True, sw.get("name", agent)
    # Also check workload names
    for wl in (srv.get("workloads") or []):
        wl_name = (wl.get("name") or "").lower()
        for agent in _BACKUP_AGENTS:
            if agent in wl_name:
                return True, wl.get("name", agent)
    return False, ""


# Function: _has_replication
def _has_replication(srv: dict) -> bool:
    """Detect if any replication mechanism is present."""
    for wl in (srv.get("workloads") or []):
        name = (wl.get("name") or "").lower()
        if any(x in name for x in ["zerto", "veeam replication", "drbd", "rsync", "replication"]):
            return True
    for sw in (srv.get("installed_software") or []):
        name = (sw.get("name") or "").lower()
        if any(x in name for x in ["zerto", "drbd", "rsync", "replication"]):
            return True
    # Cloud: RDS multi-AZ, Azure geo-redundant = replication assumed
    if srv.get("cloud_provider") in ("aws", "azure", "gcp"):
        if "rds" in (srv.get("os_name") or "").lower():
            return True
    return False


# Function: _has_load_balancer
def _has_load_balancer(srv: dict, all_servers: list[dict]) -> bool:
    """Check if server is behind a load balancer (workload or topology hint)."""
    for wl in (srv.get("workloads") or []):
        name = (wl.get("name") or "").lower()
        if any(x in name for x in ["haproxy", "nginx", "load balancer", "elb", "alb", "f5"]):
            return True
    # Check if another server acts as LB for this one (simplified: any LB in environment)
    for other in all_servers:
        for wl in (other.get("workloads") or []):
            name = (wl.get("name") or "").lower()
            if any(x in name for x in ["haproxy", "nginx lb", "load balancer", "f5"]):
                return True
    return False


# Function: _spof_analysis
def _spof_analysis(srv: dict, all_servers: list[dict]) -> tuple[bool, list[str]]:
    """Detect if server is a Single Point of Failure."""
    spof_reasons: list[str] = []
    ha_dr = (srv.get("ha_dr_requirements") or "").strip()
    if not ha_dr or ha_dr.lower() in ("none", ""):
        return False, []  # No HA requirement — not a SPOF concern

    ha_tier = ha_dr
    has_ha = any(
        t in ha_dr for t in ["Active-Active", "Active-Passive", "Hot-Standby"]
    )

    # Check if any other server appears to be a standby/replica for this one
    srv_name  = _server_name(srv).lower()
    srv_ip    = (srv.get("ip_address") or srv.get("ip") or "").split(".")[:-1]
    has_pair  = False
    for other in all_servers:
        if other is srv:
            continue
        other_name = _server_name(other).lower()
        # Heuristic: similar name (e.g. "app-server-01" and "app-server-02")
        if (
            srv_name[:-2] in other_name or
            other_name[:-2] in srv_name
        ):
            has_pair = True
            break

    if ha_dr and not has_pair:
        spof_reasons.append(f"No HA pair detected for server with HA requirement: {ha_dr}")

    if "Active-Active" in ha_dr and not _has_load_balancer(srv, all_servers):
        spof_reasons.append("Active-Active HA requires load balancer — none detected")

    if not has_pair and ha_dr:
        return True, spof_reasons
    return False, spof_reasons


# Function: _rto_feasibility
def _rto_feasibility(srv: dict, all_servers: list[dict]) -> dict:
    """Evaluate if current architecture can meet stated RTO."""
    rto_raw  = srv.get("rto_requirements") or ""
    rto_norm = _normalize_rto_rpo(rto_raw)
    if not rto_norm:
        return {"rto_stated": "", "feasible": None, "gaps": [], "recommendation": "No RTO requirement stated"}

    reqs = _RTO_REQUIREMENTS.get(rto_norm, {})
    gaps: list[str] = []

    ha_dr = (srv.get("ha_dr_requirements") or "").strip()
    ha_tier_idx = next(
        (i for i, t in enumerate(_HA_TIER_ORDER) if t and t in ha_dr),
        len(_HA_TIER_ORDER) - 1
    )
    max_idx = _HA_TIER_ORDER.index(reqs.get("max_acceptable_tier", "None"))

    if reqs.get("requires_ha") and ha_tier_idx > max_idx:
        gaps.append(
            f"RTO {rto_norm} requires at least {reqs['max_acceptable_tier']} HA — "
            f"current: '{ha_dr}'"
        )

    if reqs.get("requires_replication") and not _has_replication(srv):
        gaps.append(f"RTO {rto_norm} requires data replication — none detected")

    if reqs.get("requires_lb") and not _has_load_balancer(srv, all_servers):
        gaps.append(f"RTO {rto_norm} requires a load balancer — none detected")

    feasible = len(gaps) == 0
    return {
        "rto_stated":    rto_raw,
        "rto_canonical": rto_norm,
        "feasible":      feasible,
        "gaps":          gaps,
        "recommendation": (
            "Architecture meets RTO requirement" if feasible
            else f"Architecture gaps prevent meeting {rto_raw} RTO: {'; '.join(gaps)}"
        ),
    }


# Function: _rpo_feasibility
def _rpo_feasibility(srv: dict) -> dict:
    """Evaluate if current backup/replication meets stated RPO."""
    rpo_raw  = srv.get("rpo_requirements") or ""
    rpo_norm = _normalize_rto_rpo(rpo_raw)
    if not rpo_norm:
        return {"rpo_stated": "", "feasible": None, "gaps": [], "recommendation": "No RPO requirement stated"}

    reqs = _RPO_REQUIREMENTS.get(rpo_norm, {})
    gaps: list[str] = []
    has_backup, agent_name = _has_backup_agent(srv)
    has_replication_flag   = _has_replication(srv)

    if reqs.get("requires_replication") and not has_replication_flag:
        gaps.append(f"RPO {rpo_norm} requires continuous replication — none detected")

    if not has_backup and reqs.get("backup_frequency") not in ("continuous",):
        gaps.append(f"No backup agent detected — {reqs.get('backup_frequency','daily')} backup required")

    feasible = len(gaps) == 0
    return {
        "rpo_stated":    rpo_raw,
        "rpo_canonical": rpo_norm,
        "backup_agent_detected": has_backup,
        "backup_agent_name":     agent_name,
        "replication_detected":  has_replication_flag,
        "feasible":      feasible,
        "gaps":          gaps,
        "recommendation": (
            "Architecture meets RPO requirement" if feasible
            else f"RPO {rpo_raw} gaps: {'; '.join(gaps)}"
        ),
    }


# Function: _recovery_readiness_score
def _recovery_readiness_score(srv: dict, all_servers: list[dict]) -> dict:
    """Compute 0-100 recovery readiness score."""
    score   = 0
    factors : list[dict] = []

    # Backup agent present (+25)
    has_backup, agent_name = _has_backup_agent(srv)
    if has_backup:
        score += 25
        factors.append({"factor": f"Backup agent detected ({agent_name})", "points": 25, "status": "pass"})
    else:
        factors.append({"factor": "No backup agent detected", "points": 0, "status": "fail"})

    # HA/DR configured (+25)
    ha_dr = (srv.get("ha_dr_requirements") or "").strip()
    if ha_dr and ha_dr.lower() not in ("none", ""):
        score += 25
        factors.append({"factor": f"HA/DR configured: {ha_dr}", "points": 25, "status": "pass"})
    else:
        factors.append({"factor": "No HA/DR configuration", "points": 0, "status": "fail"})

    # Replication present (+20)
    if _has_replication(srv):
        score += 20
        factors.append({"factor": "Data replication detected", "points": 20, "status": "pass"})
    else:
        factors.append({"factor": "No data replication", "points": 0, "status": "warn"})

    # RTO feasibility (+15)
    rto_result = _rto_feasibility(srv, all_servers)
    if rto_result.get("feasible") is True:
        score += 15
        factors.append({"factor": f"RTO {rto_result['rto_stated']} achievable", "points": 15, "status": "pass"})
    elif rto_result.get("feasible") is False:
        factors.append({"factor": f"RTO not achievable: {rto_result['rto_stated']}", "points": 0, "status": "fail"})

    # RPO feasibility (+15)
    rpo_result = _rpo_feasibility(srv)
    if rpo_result.get("feasible") is True:
        score += 15
        factors.append({"factor": f"RPO {rpo_result['rpo_stated']} achievable", "points": 15, "status": "pass"})
    elif rpo_result.get("feasible") is False:
        factors.append({"factor": f"RPO not achievable: {rpo_result['rpo_stated']}", "points": 0, "status": "fail"})

    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F"
    return {
        "score":    score,
        "grade":    grade,
        "factors":  factors,
    }


# Function: analyze_bcdr
def analyze_bcdr(report: dict) -> dict:
    """Main entry point. Returns BCDR gap analysis section."""
    servers = report.get("servers") or []
    if not servers:
        return {"error": "No servers in report", "server_results": [], "summary": {}}

    server_results: list[dict] = []
    spof_servers:   list[dict] = []
    no_backup:      list[dict] = []
    rto_gaps:       list[dict] = []
    rpo_gaps:       list[dict] = []

    for srv in servers:
        name = _server_name(srv)
        ip   = srv.get("ip_address") or srv.get("ip") or srv.get("server_ip") or ""

        # SPOF
        is_spof, spof_reasons = _spof_analysis(srv, servers)
        if is_spof:
            spof_servers.append({
                "server_name": name, "server_ip": ip,
                "ha_dr_requirements": srv.get("ha_dr_requirements"),
                "reasons": spof_reasons,
            })

        # Backup
        has_backup, agent_name = _has_backup_agent(srv)
        has_rto = bool(srv.get("rto_requirements"))
        has_rpo = bool(srv.get("rpo_requirements"))
        if not has_backup and (has_rto or has_rpo):
            no_backup.append({"server_name": name, "server_ip": ip,
                               "rto": srv.get("rto_requirements"), "rpo": srv.get("rpo_requirements")})

        # RTO
        rto_result = _rto_feasibility(srv, servers)
        if rto_result.get("feasible") is False:
            rto_gaps.append({"server_name": name, "server_ip": ip,
                              "rto_stated": rto_result["rto_stated"],
                              "gaps": rto_result["gaps"]})

        # RPO
        rpo_result = _rpo_feasibility(srv)
        if rpo_result.get("feasible") is False:
            rpo_gaps.append({"server_name": name, "server_ip": ip,
                              "rpo_stated": rpo_result["rpo_stated"],
                              "gaps": rpo_result["gaps"]})

        # Readiness score
        readiness = _recovery_readiness_score(srv, servers)

        server_results.append({
            "server_name":       name,
            "server_ip":         ip,
            "ha_dr_requirements": srv.get("ha_dr_requirements") or "",
            "rto_requirements":  srv.get("rto_requirements") or "",
            "rpo_requirements":  srv.get("rpo_requirements") or "",
            "is_spof":           is_spof,
            "spof_reasons":      spof_reasons,
            "has_backup_agent":  has_backup,
            "backup_agent_name": agent_name,
            "has_replication":   _has_replication(srv),
            "rto_analysis":      rto_result,
            "rpo_analysis":      rpo_result,
            "readiness_score":   readiness,
        })

    # Sort by readiness score ascending (worst first)
    server_results.sort(key=lambda r: r["readiness_score"]["score"])

    avg_score = sum(r["readiness_score"]["score"] for r in server_results) / len(server_results) if server_results else 0

    return {
        "server_results":    server_results,
        "spof_servers":      spof_servers,
        "servers_no_backup": no_backup,
        "rto_gap_servers":   rto_gaps,
        "rpo_gap_servers":   rpo_gaps,
        "summary": {
            "total_servers_analyzed":   len(server_results),
            "spof_count":               len(spof_servers),
            "no_backup_agent_count":    len(no_backup),
            "rto_gap_count":            len(rto_gaps),
            "rpo_gap_count":            len(rpo_gaps),
            "avg_readiness_score":      round(avg_score, 1),
            "critical_readiness_count": sum(1 for r in server_results if r["readiness_score"]["score"] < 40),
            "servers_with_ha_dr":       sum(1 for s in servers if s.get("ha_dr_requirements") not in (None, "", "None")),
            "servers_with_backup":      sum(1 for r in server_results if r["has_backup_agent"]),
        },
    }
