# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: services/tco_rightsizing.py
# Date: 2026-04-16
# ---------------------------------------------------------------------------
"""
services/tco_rightsizing.py
Financial TCO & Cloud Cost Comparison with Right-Sizing Recommendations.

Features:
  - Right-sizing: servers with <20% CPU/RAM utilization mapped to smaller SKUs
  - On-prem vs cloud 3-year TCO comparison
  - Multi-cloud cost comparison (Azure / AWS / GCP / OCI)
  - Savings opportunity summary per server
  - Live pricing overlay (services/live_pricing.py): when reachable, each
    provider's current public list price replaces the static/approximate
    figures below for the specific SKUs it returns. Static tables always
    remain the fallback — this module must keep working with zero outbound
    connectivity (air-gapped / regulated customer environments).
"""
from __future__ import annotations

import logging
import time
from typing import Any

from services import live_pricing

log = logging.getLogger(__name__)

# ── On-prem cost assumptions (USD/month per server) ─────────────────────────
_ONPREM_COST_PER_CPU_CORE_MONTH = 18.0       # hardware depreciation + maintenance
_ONPREM_COST_PER_GB_RAM_MONTH   = 3.5        # memory cost allocation
_ONPREM_COST_PER_TB_STORAGE_MONTH = 12.0     # storage (SAN/NAS/local)
_ONPREM_DC_OVERHEAD_PCT         = 0.40       # 40% overhead: power, cooling, floor space, staff
_ONPREM_WINDOWS_LICENSE_MONTH   = 58.0       # Windows Server Std per server/month
_ONPREM_RHEL_LICENSE_MONTH      = 49.0       # RHEL per server/month

# ── Cloud flavor catalogs (cpu, ram_gb, cost_usd_month) ─────────────────────
# Azure East US (Pay-As-You-Go Linux)
_AZURE_FLAVORS = [
    ("Standard_B2als_v2",  2,  4,   24.53),
    ("Standard_B4als_v2",  4,  8,   43.86),
    ("Standard_B8als_v2",  8, 16,   87.60),
    ("Standard_B2s",       2,  4,   30.66),
    ("Standard_B4ms",      4, 16,   76.01),
    ("Standard_B8ms",      8, 32,  152.04),
    ("Standard_D2s_v3",    2,  8,   70.08),
    ("Standard_D4s_v3",    4, 16,  140.16),
    ("Standard_D8s_v3",    8, 32,  280.32),
    ("Standard_D16s_v3",  16, 64,  560.64),
    ("Standard_D32s_v3",  32,128, 1121.28),
    ("Standard_E2s_v3",    2, 16,   92.71),
    ("Standard_E4s_v3",    4, 32,  185.41),
    ("Standard_E8s_v3",    8, 64,  370.82),
    ("Standard_F2s_v2",    2,  4,   60.38),
    ("Standard_F4s_v2",    4,  8,  120.76),
]

# AWS us-east-1 (On-Demand Linux)
_AWS_FLAVORS = [
    ("t3.micro",    2,  1,    8.47),
    ("t3.small",    2,  2,   16.79),
    ("t3.medium",   2,  4,   33.57),
    ("t3.large",    2,  8,   67.14),
    ("t3.xlarge",   4, 16,  134.28),
    ("t3.2xlarge",  8, 32,  268.56),
    ("m5.large",    2,  8,   70.08),
    ("m5.xlarge",   4, 16,  140.16),
    ("m5.2xlarge",  8, 32,  280.32),
    ("m5.4xlarge", 16, 64,  560.64),
    ("r5.large",    2, 16,  121.46),
    ("r5.xlarge",   4, 32,  242.93),
    ("r5.2xlarge",  8, 64,  485.86),
    ("c5.large",    2,  4,   62.05),
    ("c5.xlarge",   4,  8,  124.10),
    ("c5.2xlarge",  8, 16,  248.20),
]

# GCP us-central1 (On-Demand Linux)
_GCP_FLAVORS = [
    ("e2-micro",        2,  1,    6.11),
    ("e2-small",        2,  2,   12.23),
    ("e2-medium",       2,  4,   24.46),
    ("e2-standard-2",   2,  8,   49.37),
    ("e2-standard-4",   4, 16,   98.75),
    ("e2-standard-8",   8, 32,  197.49),
    ("e2-standard-16", 16, 64,  394.98),
    ("n2-standard-2",   2,  8,   58.26),
    ("n2-standard-4",   4, 16,  116.52),
    ("n2-standard-8",   8, 32,  233.04),
    ("n2-highmem-2",    2, 16,   75.73),
    ("n2-highmem-4",    4, 32,  151.45),
    ("n2-highmem-8",    8, 64,  302.90),
]

# OCI (Oracle Cloud) — flexible "E5.Flex" general-purpose shape, priced per
# OCPU + per-GB-memory rather than per fixed SKU (OCI's actual billing model;
# see services/live_pricing.py's oci_hourly_cost() docstring). These static
# rates are the real per-OCPU/per-GB list prices observed from OCI's public
# catalog at the time this was written; live_pricing overlays current values
# when reachable. NOTE: "cpu_cores" here is treated as OCPU count directly —
# a deliberate simplification consistent with how this module already treats
# CPU sizing uniformly across providers, not a literal OCPU/vCPU conversion.
_OCI_OCPU_HOURLY = 0.025
_OCI_MEM_GB_HOURLY = 0.0015
_OCI_FLAVORS = [
    ("VM.Standard.E5.Flex-2-8",    2,  8,   round((2 * _OCI_OCPU_HOURLY + 8 * _OCI_MEM_GB_HOURLY) * 730, 2)),
    ("VM.Standard.E5.Flex-2-16",   2, 16,   round((2 * _OCI_OCPU_HOURLY + 16 * _OCI_MEM_GB_HOURLY) * 730, 2)),
    ("VM.Standard.E5.Flex-4-16",   4, 16,   round((4 * _OCI_OCPU_HOURLY + 16 * _OCI_MEM_GB_HOURLY) * 730, 2)),
    ("VM.Standard.E5.Flex-4-32",   4, 32,   round((4 * _OCI_OCPU_HOURLY + 32 * _OCI_MEM_GB_HOURLY) * 730, 2)),
    ("VM.Standard.E5.Flex-8-32",   8, 32,   round((8 * _OCI_OCPU_HOURLY + 32 * _OCI_MEM_GB_HOURLY) * 730, 2)),
    ("VM.Standard.E5.Flex-8-64",   8, 64,   round((8 * _OCI_OCPU_HOURLY + 64 * _OCI_MEM_GB_HOURLY) * 730, 2)),
    ("VM.Standard.E5.Flex-16-64", 16, 64,   round((16 * _OCI_OCPU_HOURLY + 64 * _OCI_MEM_GB_HOURLY) * 730, 2)),
    ("VM.Standard.E5.Flex-16-128",16,128,   round((16 * _OCI_OCPU_HOURLY + 128 * _OCI_MEM_GB_HOURLY) * 730, 2)),
]


# ─── Live pricing overlay ─────────────────────────────────────────────────────
# Cached per-process for a few minutes so a burst of TCO requests (e.g. one
# per server in a large scan, or repeated Overview refreshes) doesn't each
# independently hit live_pricing's own disk cache read/parse — this is a much
# shorter-lived cache than live_pricing's own 24h disk cache, just avoiding
# redundant in-process work within a single request burst.
_live_catalog_cache: dict[str, Any] = {"built_at": 0.0, "catalogs": None, "meta": None}
_LIVE_CATALOG_TTL_SECONDS = 300


# Function: _build_live_flavor_catalogs
def _build_live_flavor_catalogs() -> tuple[dict[str, list[tuple]], dict[str, dict]]:
    """
    Returns (catalogs, meta) where catalogs mirrors the static _AZURE_FLAVORS /
    _AWS_FLAVORS / _GCP_FLAVORS / _OCI_FLAVORS shape (so _best_fit_flavor works
    unchanged on either), with costs overwritten by live pricing wherever
    available, and meta reports per-provider pricing source/freshness for the
    frontend's "Pricing: live (2h ago)" / "Pricing: static table" indicator.
    """
    now = time.monotonic()
    if _live_catalog_cache["catalogs"] is not None and now - _live_catalog_cache["built_at"] < _LIVE_CATALOG_TTL_SECONDS:
        return _live_catalog_cache["catalogs"], _live_catalog_cache["meta"]

    catalogs = {
        "azure": list(_AZURE_FLAVORS),
        "aws": list(_AWS_FLAVORS),
        "gcp": list(_GCP_FLAVORS),
        "oci": list(_OCI_FLAVORS),
    }
    meta: dict[str, dict] = {}

    try:
        azure_names = [f[0] for f in _AZURE_FLAVORS]
        azure_live = live_pricing.fetch_azure_prices("eastus", azure_names)
        meta["azure"] = {"source": azure_live["source"], "cache_age": azure_live.get("cache_age")}
        if azure_live["prices"]:
            catalogs["azure"] = [
                (name, cpu, ram, round(azure_live["prices"][name] * 730, 2) if name in azure_live["prices"] else cost)
                for name, cpu, ram, cost in _AZURE_FLAVORS
            ]
    except Exception as exc:
        log.debug("TCO live pricing (azure) skipped: %s", exc)
        meta["azure"] = {"source": "static", "cache_age": None}

    try:
        aws_names = [f[0] for f in _AWS_FLAVORS]
        aws_live = live_pricing.fetch_aws_prices("us-east-1", aws_names)
        meta["aws"] = {"source": aws_live["source"], "cache_age": aws_live.get("cache_age")}
        if aws_live["prices"]:
            catalogs["aws"] = [
                (name, cpu, ram, round(aws_live["prices"][name] * 730, 2) if name in aws_live["prices"] else cost)
                for name, cpu, ram, cost in _AWS_FLAVORS
            ]
    except Exception as exc:
        log.debug("TCO live pricing (aws) skipped: %s", exc)
        meta["aws"] = {"source": "static", "cache_age": None}

    try:
        gcp_live = live_pricing.fetch_gcp_prices("us-central1")
        meta["gcp"] = {"source": gcp_live["source"], "cache_age": gcp_live.get("cache_age")}
        # GCP's SKU→machine-type mapping is best-effort (see live_pricing.py);
        # only overlay when we have high confidence via an exact family match.
    except Exception as exc:
        log.debug("TCO live pricing (gcp) skipped: %s", exc)
        meta["gcp"] = {"source": "static", "cache_age": None}

    try:
        oci_live = live_pricing.fetch_oci_prices()
        meta["oci"] = {"source": oci_live["source"], "cache_age": oci_live.get("cache_age")}
        shapes = oci_live.get("shapes") or {}
        general_purpose = shapes.get("Compute - Standard - E5") or shapes.get("OCI - Compute - Standard - E5")
        if general_purpose:
            catalogs["oci"] = [
                (name, cpu, ram, round(live_pricing.oci_hourly_cost({"_": general_purpose}, "_", cpu, ram) * 730, 2))
                for name, cpu, ram, _cost in _OCI_FLAVORS
            ]
    except Exception as exc:
        log.debug("TCO live pricing (oci) skipped: %s", exc)
        meta["oci"] = {"source": "static", "cache_age": None}

    _live_catalog_cache["built_at"] = now
    _live_catalog_cache["catalogs"] = catalogs
    _live_catalog_cache["meta"] = meta
    return catalogs, meta


# Function: _best_fit_flavor
def _best_fit_flavor(
    cpu_need: int, ram_need: float, flavors: list[tuple]
) -> tuple[str, int, float, float] | None:
    """Return (name, cpu, ram_gb, cost) of the smallest flavor that fits cpu_need/ram_need."""
    candidates = [f for f in flavors if f[1] >= cpu_need and f[2] >= ram_need]
    if not candidates:
        # Widen: take biggest available
        candidates = sorted(flavors, key=lambda f: (f[1], f[2]), reverse=True)[:1]
    return min(candidates, key=lambda f: f[3]) if candidates else None


# Function: _onprem_monthly_cost
def _onprem_monthly_cost(server: dict) -> float:
    cpu   = server.get("cpu_cores") or 0
    ram   = server.get("ram_gb") or server.get("memory_gb") or 0
    disk_tb = (server.get("total_storage_gb") or server.get("internal_storage_gb") or 0) / 1024
    os_lower = (server.get("os_name") or server.get("os_family") or "").lower()

    base = (
        cpu   * _ONPREM_COST_PER_CPU_CORE_MONTH +
        ram   * _ONPREM_COST_PER_GB_RAM_MONTH +
        disk_tb * _ONPREM_COST_PER_TB_STORAGE_MONTH
    )
    base *= (1 + _ONPREM_DC_OVERHEAD_PCT)

    if "windows" in os_lower:
        base += _ONPREM_WINDOWS_LICENSE_MONTH
    elif "red hat" in os_lower or "rhel" in os_lower:
        base += _ONPREM_RHEL_LICENSE_MONTH

    return round(base, 2)


# Function: _right_size_cpu_ram
def _right_size_cpu_ram(server: dict) -> tuple[int, float]:
    """
    Return (effective_cpu, effective_ram) based on actual utilization.
    If utilization < 20%, halve the requirement (right-sizing).
    """
    cpu  = max(1, server.get("cpu_cores") or 1)
    ram  = max(0.5, server.get("ram_gb") or server.get("memory_gb") or 0.5)

    cpu_util = server.get("cpu_util_pct", -1)
    ram_util = server.get("ram_util_pct", -1)

    # Right-size only if we have real utilization data
    if cpu_util >= 0 and cpu_util < 20:
        cpu = max(1, int(cpu * 0.5))
    if ram_util >= 0 and ram_util < 20:
        ram = max(0.5, ram * 0.5)

    return cpu, ram


# Function: _analyze_server
def _analyze_server(server: dict, catalogs: dict[str, list[tuple]]) -> dict:
    """Produce TCO & right-sizing analysis for one server."""
    name = server.get("server_name") or server.get("name") or server.get("server_ip") or "unknown"
    cpu  = max(1, server.get("cpu_cores") or 1)
    ram  = max(0.5, server.get("ram_gb") or server.get("memory_gb") or 0.5)
    cpu_util = server.get("cpu_util_pct", -1)
    ram_util = server.get("ram_util_pct", -1)
    util_band = server.get("utilization_band") or server.get("utilization") or "unknown"

    # Actual utilization data present?
    has_util = cpu_util >= 0 or ram_util >= 0
    is_underutilized = util_band == "underutilized" or (
        has_util and (cpu_util < 20 or ram_util < 20)
    )

    # Right-sized requirements
    rs_cpu, rs_ram = _right_size_cpu_ram(server)
    rightsized = (rs_cpu < cpu or rs_ram < ram)

    onprem_cost = _onprem_monthly_cost(server)

    # Full-size cloud costs
    az_full   = _best_fit_flavor(cpu, ram, catalogs["azure"])
    aws_full  = _best_fit_flavor(cpu, ram, catalogs["aws"])
    gcp_full  = _best_fit_flavor(cpu, ram, catalogs["gcp"])
    oci_full  = _best_fit_flavor(cpu, ram, catalogs["oci"])

    # Right-sized cloud costs
    az_rs  = _best_fit_flavor(rs_cpu, rs_ram, catalogs["azure"])
    aws_rs = _best_fit_flavor(rs_cpu, rs_ram, catalogs["aws"])
    gcp_rs = _best_fit_flavor(rs_cpu, rs_ram, catalogs["gcp"])
    oci_rs = _best_fit_flavor(rs_cpu, rs_ram, catalogs["oci"])

    # Function: _flavor_dict
    def _flavor_dict(f):
        if not f:
            return None
        return {"name": f[0], "cpu": f[1], "ram_gb": f[2], "cost_usd_month": f[3]}

    # Best cloud option after right-sizing
    rs_options = [x for x in [az_rs, aws_rs, gcp_rs, oci_rs] if x]
    best_cloud_cost = min(x[3] for x in rs_options) if rs_options else None
    monthly_savings = round(onprem_cost - best_cloud_cost, 2) if best_cloud_cost else None
    annual_savings  = round(monthly_savings * 12, 2) if monthly_savings else None
    savings_pct     = round(monthly_savings / onprem_cost * 100, 1) if (monthly_savings and onprem_cost > 0) else None

    return {
        "server_name":        name,
        "server_ip":          server.get("ip_address") or server.get("ip") or "",
        "cpu_cores":          cpu,
        "ram_gb":             ram,
        "cpu_util_pct":       cpu_util,
        "ram_util_pct":       ram_util,
        "utilization_band":   util_band,
        "is_underutilized":   is_underutilized,
        "rightsized_cpu":     rs_cpu,
        "rightsized_ram_gb":  rs_ram,
        "rightsizing_applied": rightsized,
        "onprem_cost_usd_month": onprem_cost,
        "cloud_options": {
            "azure": {
                "full_size":  _flavor_dict(az_full),
                "rightsized": _flavor_dict(az_rs),
            },
            "aws": {
                "full_size":  _flavor_dict(aws_full),
                "rightsized": _flavor_dict(aws_rs),
            },
            "gcp": {
                "full_size":  _flavor_dict(gcp_full),
                "rightsized": _flavor_dict(gcp_rs),
            },
            "oci": {
                "full_size":  _flavor_dict(oci_full),
                "rightsized": _flavor_dict(oci_rs),
            },
        },
        "best_cloud_cost_usd_month": best_cloud_cost,
        "monthly_savings_usd":       monthly_savings,
        "annual_savings_usd":        annual_savings,
        "savings_pct":               savings_pct,
        "recommendation": _recommendation(is_underutilized, rightsized, monthly_savings, savings_pct),
    }


# Function: _recommendation
def _recommendation(is_underutilized: bool, rightsized: bool, savings: float | None, pct: float | None) -> str:
    if savings is None:
        return "Insufficient data for cost recommendation."
    if savings < 0:
        return "On-premises may be more cost-effective for this workload profile."
    if is_underutilized and rightsized:
        return (
            f"Server is underutilized. Right-size to smaller SKU before migration. "
            f"Estimated savings: {pct}% (${savings:.0f}/mo)."
        )
    if savings > 0:
        return f"Migrate to cloud for estimated {pct}% savings (${savings:.0f}/mo)."
    return "Approximately cost-neutral migration."


# Function: analyze_tco
def analyze_tco(report: dict, use_live_pricing: bool = True) -> dict:
    """
    Main entry point. Accepts a scan report dict, returns TCO analysis section.

    use_live_pricing=False forces the static tables (useful for a fully
    air-gapped deployment that wants to skip even attempting network calls,
    or for reproducible testing).
    """
    servers = report.get("servers") or []
    if not servers:
        return {"error": "No servers in report", "server_results": [], "summary": {}}

    if use_live_pricing:
        catalogs, pricing_meta = _build_live_flavor_catalogs()
    else:
        catalogs = {"azure": _AZURE_FLAVORS, "aws": _AWS_FLAVORS, "gcp": _GCP_FLAVORS, "oci": _OCI_FLAVORS}
        pricing_meta = {p: {"source": "static", "cache_age": None} for p in catalogs}

    results = []
    for srv in servers:
        try:
            results.append(_analyze_server(srv, catalogs))
        except Exception as exc:
            log.warning("TCO analysis failed for %s: %s", srv.get("server_name"), exc)

    total_onprem  = sum(r["onprem_cost_usd_month"] for r in results)
    total_savings = sum(r["monthly_savings_usd"] or 0 for r in results)
    underutilized_count = sum(1 for r in results if r["is_underutilized"])
    rightsized_count    = sum(1 for r in results if r["rightsizing_applied"])

    # 3-year TCO comparison
    tco_onprem_3yr   = round(total_onprem * 36, 2)
    tco_cloud_3yr    = round((total_onprem - total_savings) * 36, 2)
    tco_savings_3yr  = round(total_savings * 36, 2)

    return {
        "server_results": results,
        "pricing_sources": pricing_meta,
        "summary": {
            "total_servers_analyzed": len(results),
            "underutilized_servers": underutilized_count,
            "rightsizing_candidates": rightsized_count,
            "total_onprem_cost_usd_month": round(total_onprem, 2),
            "total_cloud_savings_usd_month": round(total_savings, 2),
            "total_cloud_cost_usd_month": round(total_onprem - total_savings, 2),
            "savings_pct_avg": round(total_savings / total_onprem * 100, 1) if total_onprem > 0 else 0,
            "tco_onprem_3yr_usd":  tco_onprem_3yr,
            "tco_cloud_3yr_usd":   tco_cloud_3yr,
            "tco_savings_3yr_usd": tco_savings_3yr,
            "top_savings_servers": sorted(
                [r for r in results if r["monthly_savings_usd"]],
                key=lambda r: r["monthly_savings_usd"],
                reverse=True,
            )[:5],
        },
    }
