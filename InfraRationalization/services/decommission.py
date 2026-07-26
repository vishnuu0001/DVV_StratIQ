# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: services/decommission.py
# Date: 2025-10-22
# ---------------------------------------------------------------------------
"""
services/decommission.py
Decommissioning Candidate Identification.

Features:
  - Zombie server detection: 0 active workloads + <5% utilization
  - Duplicate service detection: same service on multiple underutilized servers
  - Dev/Test in Production: environment mismatch
  - Orphaned resources: unattached storage, unused NICs, stopped VMs
"""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

log = logging.getLogger(__name__)

# Known production subnet prefixes (heuristic)
_PROD_SUBNET_HINTS = ["10.", "172.16.", "172.17.", "172.18.", "172.19.",
                       "172.20.", "172.21.", "172.22.", "172.23.", "172.24.",
                       "172.25.", "172.26.", "172.27.", "172.28.", "172.29.",
                       "172.30.", "172.31.", "192.168."]

_DEV_TEST_ENVS = {"development", "dev", "test", "qa", "staging", "sandbox", "uat"}
_PROD_ENVS     = {"production", "prod", "live"}


# Function: _server_id
def _server_id(srv: dict) -> str:
    return (srv.get("server_ip") or srv.get("ip_address") or srv.get("ip") or
            srv.get("server_name") or srv.get("name") or "unknown")


# Function: _server_name
def _server_name(srv: dict) -> str:
    return srv.get("server_name") or srv.get("name") or _server_id(srv)


# Function: _is_zombie
def _is_zombie(srv: dict) -> tuple[bool, list[str]]:
    """Detect zombie server: no workloads + very low utilization."""
    reasons: list[str] = []
    workloads = srv.get("workloads") or []
    sw        = srv.get("installed_software") or []
    cpu_util  = srv.get("cpu_util_pct", -1)
    ram_util  = srv.get("ram_util_pct", -1)
    util_band = (srv.get("utilization_band") or srv.get("utilization") or "").lower()

    # Filter meaningful workloads (ignore SSH/HTTP/HTTPS which are always present)
    meaningful_workloads = [
        w for w in workloads
        if (w.get("name") or "").upper() not in {"SSH", "HTTP", "HTTPS", "RDP", "SNMP"}
    ]

    has_no_workload = len(meaningful_workloads) == 0
    is_underutilized = (
        util_band == "underutilized" or
        (cpu_util >= 0 and cpu_util < 5) or
        (ram_util >= 0 and ram_util < 5)
    )

    if has_no_workload:
        reasons.append("No meaningful workloads running")
    if cpu_util >= 0 and cpu_util < 5:
        reasons.append(f"CPU utilization extremely low ({cpu_util:.1f}%)")
    if ram_util >= 0 and ram_util < 5:
        reasons.append(f"RAM utilization extremely low ({ram_util:.1f}%)")

    # Cloud: stopped VM still incurring cost
    state = (srv.get("raw_metadata") or {}).get("aws_state") or (srv.get("raw_metadata") or {}).get("power_state") or ""
    if state and state.lower() in ("stopped", "deallocated"):
        reasons.append(f"VM is stopped/deallocated but still exists (state: {state})")
        return True, reasons

    is_zombie = has_no_workload and is_underutilized and len(reasons) >= 2
    return is_zombie, reasons


# Function: _dev_test_in_production
def _dev_test_in_production(srv: dict) -> tuple[bool, str]:
    """Detect Dev/Test servers in production subnets."""
    env = (srv.get("environment") or "").lower().strip()
    if not env:
        return False, ""

    is_dev_test = any(d in env for d in _DEV_TEST_ENVS)
    if not is_dev_test:
        return False, ""

    # Check if IP suggests production network
    ip = srv.get("ip_address") or srv.get("ip") or srv.get("server_ip") or ""
    is_prod_ip = any(ip.startswith(p) for p in _PROD_SUBNET_HINTS)

    # Check platform_host hint
    platform = (srv.get("platform_host") or "").lower()
    is_prod_platform = any(p in platform for p in ["prod", "production", "live", "prd"])

    if is_prod_ip or is_prod_platform:
        reason = f"Server tagged as '{env}' but runs in production network ({ip})"
        return True, reason

    return False, ""


# Function: _orphaned_resources
def _orphaned_resources(srv: dict) -> list[dict]:
    """Detect orphaned storage, NICs, and stopped VMs."""
    orphans: list[dict] = []

    # Stopped VM (cloud)
    raw_meta = srv.get("raw_metadata") or {}
    state    = raw_meta.get("aws_state") or raw_meta.get("power_state") or ""
    if state and state.lower() in ("stopped", "deallocated", "terminated"):
        orphans.append({
            "type":        "stopped_vm",
            "description": f"VM is {state} but still provisioned",
            "risk":        "Cost",
            "action":      "Verify if needed; decommission if unused for 30+ days",
        })

    # Unattached / zero-usage disks
    disks = srv.get("disks") or []
    for disk in disks:
        if disk.get("used_gb", -1) == 0 and disk.get("size_gb", 0) > 0:
            orphans.append({
                "type":        "unused_disk",
                "description": f"Disk at {disk.get('mount_point','?')} has 0 GB used of {disk.get('size_gb')} GB",
                "risk":        "Cost",
                "action":      "Verify if disk is intentionally empty; consider deleting or repurposing",
            })

    # Interfaces with no IP or DOWN state
    for iface in (srv.get("interfaces") or []):
        if iface.get("link_state") == "down":
            orphans.append({
                "type":        "unused_nic",
                "description": f"Network interface {iface.get('interface_name','?')} is DOWN",
                "risk":        "Unused resource",
                "action":      "Remove unused NIC to reduce attack surface and cost",
            })

    return orphans


# Function: _find_duplicate_services
def _find_duplicate_services(servers: list[dict]) -> list[dict]:
    """Find same service running on multiple underutilized servers."""
    # Group by workload name
    service_servers: dict[str, list[dict]] = defaultdict(list)
    for srv in servers:
        util_band = (srv.get("utilization_band") or srv.get("utilization") or "").lower()
        is_under  = util_band == "underutilized" or srv.get("cpu_util_pct", 100) < 30

        for wl in (srv.get("workloads") or []):
            wl_name = (wl.get("name") or "").strip()
            if wl_name and wl_name.upper() not in {"SSH", "HTTP", "HTTPS", "RDP", "SNMP"}:
                service_servers[wl_name].append({
                    "server_name": _server_name(srv),
                    "server_ip":   srv.get("ip_address") or srv.get("ip") or "",
                    "version":     wl.get("version") or "",
                    "utilization": util_band,
                    "cpu_util_pct": srv.get("cpu_util_pct", -1),
                    "is_underutilized": is_under,
                })

    duplicates: list[dict] = []
    for svc_name, svc_servers in service_servers.items():
        if len(svc_servers) < 2:
            continue
        underutil_count = sum(1 for s in svc_servers if s["is_underutilized"])
        if underutil_count < 2:
            continue  # Only flag if multiple are underutilized
        duplicates.append({
            "service_name":        svc_name,
            "total_instances":     len(svc_servers),
            "underutilized_count": underutil_count,
            "servers":             svc_servers,
            "recommendation": (
                f"Consider consolidating {underutil_count} underutilized {svc_name} instances "
                f"onto a single server or managed cloud service"
            ),
        })

    return sorted(duplicates, key=lambda d: d["underutilized_count"], reverse=True)


# Function: identify_decommission_candidates
def identify_decommission_candidates(report: dict) -> dict:
    """Main entry point. Returns decommissioning analysis section."""
    servers = report.get("servers") or []
    if not servers:
        return {"error": "No servers in report", "candidates": [], "summary": {}}

    candidates: list[dict] = []
    dev_test_in_prod: list[dict] = []
    all_orphans: list[dict] = []

    for srv in servers:
        name = _server_name(srv)
        sid  = _server_id(srv)
        rec: dict[str, Any] = {
            "server_name": name,
            "server_ip":   srv.get("ip_address") or srv.get("ip") or srv.get("server_ip") or "",
            "environment": srv.get("environment") or "",
            "os":          srv.get("os_name") or srv.get("os_family") or "",
            "flags":       [],
            "recommendation": "",
            "priority":    "Low",
        }

        flag_count = 0

        # Zombie detection
        is_zombie, zombie_reasons = _is_zombie(srv)
        if is_zombie:
            rec["flags"].append({"type": "zombie", "reasons": zombie_reasons})
            flag_count += 3
            rec["recommendation"] = "Strong decommission candidate — no workloads and extremely low utilization"
            rec["priority"] = "High"

        # Dev/Test in Production
        is_env_mismatch, env_reason = _dev_test_in_production(srv)
        if is_env_mismatch:
            rec["flags"].append({"type": "dev_test_in_production", "reason": env_reason})
            dev_test_in_prod.append({
                "server_name": name,
                "server_ip":   srv.get("ip_address") or srv.get("ip") or "",
                "environment": srv.get("environment"),
                "reason":      env_reason,
            })
            flag_count += 2
            if not rec["recommendation"]:
                rec["recommendation"] = "Dev/Test server in production network — move to isolated environment or decommission"
            rec["priority"] = "High"

        # Orphaned resources
        orphans = _orphaned_resources(srv)
        if orphans:
            rec["flags"].append({"type": "orphaned_resources", "items": orphans})
            all_orphans.extend([{**o, "server_name": name} for o in orphans])
            flag_count += len(orphans)
            if not rec["recommendation"]:
                rec["recommendation"] = "Has orphaned/unused resources — review and clean up"
            rec["priority"] = max(rec["priority"], "Medium",
                                   key=lambda p: {"Low": 0, "Medium": 1, "High": 2}[p])

        if flag_count > 0:
            candidates.append(rec)

    # Duplicate services
    duplicates = _find_duplicate_services(servers)

    # Sort candidates by priority
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    candidates.sort(key=lambda c: priority_order.get(c["priority"], 3))

    return {
        "candidates":          candidates,
        "duplicate_services":  duplicates,
        "dev_test_in_prod":    dev_test_in_prod,
        "orphaned_resources":  all_orphans,
        "summary": {
            "total_candidates":       len(candidates),
            "high_priority":          sum(1 for c in candidates if c["priority"] == "High"),
            "medium_priority":        sum(1 for c in candidates if c["priority"] == "Medium"),
            "duplicate_service_types": len(duplicates),
            "dev_test_in_prod_count": len(dev_test_in_prod),
            "orphaned_resource_count": len(all_orphans),
            "estimated_monthly_savings_usd": _estimate_savings(candidates, servers),
        },
    }


# Function: _estimate_savings
def _estimate_savings(candidates: list[dict], servers: list[dict]) -> float:
    """Very rough cost savings estimate for decommission candidates."""
    savings = 0.0
    srv_map = {
        (s.get("server_name") or s.get("name") or ""): s for s in servers
    }
    for c in candidates:
        srv = srv_map.get(c["server_name"], {})
        cpu = srv.get("cpu_cores") or 2
        ram = (srv.get("ram_gb") or srv.get("memory_gb") or 4)
        # Rough on-prem cost estimate
        savings += cpu * 18 + ram * 3.5
    return round(savings * 1.4, 2)  # include DC overhead
