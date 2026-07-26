# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: services/llm_intelligence.py
# Date: 2025-11-14
# ---------------------------------------------------------------------------
"""
services/llm_intelligence.py
GPU-accelerated LLM Intelligence for InfraRationalization.

Uses Ollama (local GPU inference) with automatic best-model selection.
Model priority (highest reasoning capability first):
  deepseek-r1:32b → qwen2.5:32b → qwen2.5:7b → deepseek-r1:14b
  → phi4:14b → llama3.3:70b → llama3.1:8b → qwen2.5:7b
  → mistral:7b → llama3.2:3b

Provides:
  - analyze_infrastructure_failures(scan_report)  → failure predictions
  - get_model_info()                              → current model status
"""
from __future__ import annotations

import json
import logging
import re
from datetime import date
from typing import Any

import requests

log = logging.getLogger(__name__)

OLLAMA_BASE = "http://localhost:11434"

# Models ordered by reasoning capability — first available wins
_MODEL_PRIORITY = [
    "qwen3.5:9b",
    "deepseek-r1:32b",
    "qwen2.5:32b",
    "qwen2.5:7b",
    "deepseek-r1:14b",
    "phi4:14b",
    "llama3.3:70b",
    "qwen2.5:7b",
    "llama3.1:8b",
    "mistral:7b",
    "llama3.2:3b",
    "phi3:mini",
]

_cached_model: str | None = None
_models_unavailable: bool = False


# Function: _get_best_gpu_model
def _get_best_gpu_model() -> str | None:
    """Auto-detect best available Ollama model. Returns None if Ollama is unreachable."""
    global _cached_model, _models_unavailable
    if _models_unavailable:
        return None
    if _cached_model:
        return _cached_model
    try:
        resp = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
        if resp.status_code != 200:
            _models_unavailable = True
            return None
        data = resp.json()
        available_full: set[str] = {m.get("name", "") for m in data.get("models", [])}

        # Try exact priority order first
        for model in _MODEL_PRIORITY:
            if model in available_full:
                _cached_model = model
                log.info("InfraLLM: using %s (GPU-accelerated via Ollama)", model)
                return model

        # Partial prefix match (e.g. "deepseek-r1" found as "deepseek-r1:14b")
        for model in _MODEL_PRIORITY:
            base = model.split(":")[0]
            match = next(
                (name for name in sorted(available_full) if name.startswith(base + ":")),
                None,
            )
            if match:
                _cached_model = match
                log.info("InfraLLM: using %s (GPU-accelerated via Ollama)", match)
                return match

        # Fall back to whatever is installed
        if available_full:
            _cached_model = sorted(available_full)[-1]
            log.info("InfraLLM: fallback model %s", _cached_model)
            return _cached_model

        _models_unavailable = True
        return None
    except Exception as exc:
        log.debug("Ollama not reachable: %s", exc)
        _models_unavailable = True
        return None


# Function: _call_ollama
def _call_ollama(model: str, prompt: str, system: str = "") -> str:
    """Call Ollama /api/generate. Returns raw text response."""
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.05,
            "top_p": 0.9,
            "num_predict": 6000,
            "num_gpu": 99,        # force all layers to GPU
            "num_thread": 8,
        },
    }
    if system:
        payload["system"] = system
    try:
        resp = requests.post(f"{OLLAMA_BASE}/api/generate", json=payload, timeout=240)
        resp.raise_for_status()
        return resp.json().get("response", "")
    except Exception as exc:
        log.warning("Ollama call failed: %s", exc)
        return ""


# Function: _extract_json
def _extract_json(text: str) -> dict:
    """Robustly extract JSON object from LLM output (handles markdown fences)."""
    # Direct parse
    try:
        return json.loads(text.strip())
    except Exception:
        pass
    # Code-fence strip
    m = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # First { ... } block
    m2 = re.search(r"(\{[\s\S]+\})", text)
    if m2:
        try:
            return json.loads(m2.group(1))
        except Exception:
            pass
    return {}


_SYSTEM_PROMPT = (
    "You are a senior infrastructure reliability engineer and cloud architect. "
    "You analyze on-premises and cloud infrastructure scan data to identify "
    "failure risks, cascading impact chains, root causes, and preventive measures. "
    "Always respond with valid JSON only — no prose, no markdown outside code blocks."
)

# ─── Main LLM analysis ────────────────────────────────────────────────────────

# Function: _build_infra_data
def _build_infra_data(scan_report):
    # Report schema nests these under "sections" — only "servers" is top-level.
    # Reading them at the top level (as this used to) silently resolved every
    # one of them to {}/[] regardless of what the scan actually found.
    sections = scan_report.get("sections", {}) or {}
    servers = scan_report.get("servers", [])
    net_topo = sections.get("network_topology", {}) or {}
    sw_inv = sections.get("software_inventory", {}) or {}
    eos_os = sections.get("eos_advisory_os", []) or []
    eos_wl = sections.get("eos_advisory_workload", []) or []
    capacity = sections.get("capacity_planning", {}) or {}
    cr = sections.get("cloud_readiness", {}) or {}
    server_summaries = []
    for s in servers[:25]:
        srv_name = s.get("server_name") or s.get("name", "unknown")
        server_summaries.append({
            "name": srv_name,
            "ip": s.get("ip_address") or s.get("ip", ""),
            "os": s.get("os_name") or s.get("os", ""),
            "cpu_cores": s.get("cpu_cores", 0),
            "ram_gb": s.get("ram_gb", 0),
            "cpu_util_pct": s.get("cpu_util_pct", -1),
            "ram_util_pct": s.get("ram_util_pct", -1),
            "utilization": s.get("utilization_band", "unknown"),
            "os_eos_date": s.get("os_end_of_support", ""),
            "workloads": [w.get("name", "") for w in (s.get("workloads") or [])],
            "nic_count": len(s.get("interfaces") or []),
            "has_routes": bool(s.get("routes")),
            "arp_count": len(s.get("arp_neighbors") or []),
            "ha_dr": s.get("ha_dr_requirements", ""),
            "migration_strategy": s.get("migration_strategy", ""),
            "cloud_suitability": s.get("cloud_suitability", ""),
        })
    subnets = [
        {"subnet": sn.get("subnet", ""), "gateway": sn.get("gateway", ""), "host_count": sn.get("host_count", 0)}
        for sn in net_topo.get("subnets", [])[:10]
    ]
    # De-duplicated package list — the counts below tell an LLM "how many" but
    # not "which ones", so questions like "what are the unique packages" had
    # nothing to ground an answer in even once the counts were fixed.
    seen_packages: set[str] = set()
    unique_package_list = []
    for item in sw_inv.get("items", []):
        name = item.get("name")
        if name and name not in seen_packages:
            seen_packages.add(name)
            unique_package_list.append({
                "name": name,
                "vendor": item.get("vendor", ""),
                "category": item.get("category", ""),
                "is_eos": item.get("is_eos", False),
            })
    return {
        "total_servers": len(servers),
        "servers": server_summaries,
        "subnets": subnets,
        "eos_summary": {
            "os_eos_count": len(eos_os),
            "workload_eos_count": len(eos_wl),
            "software_eos_packages": sw_inv.get("eos_count", 0),
            "software_expiring_soon": sw_inv.get("expiring_soon_count", 0),
            "commercial_packages": sw_inv.get("commercial_count", 0),
            "open_source_packages": sw_inv.get("open_source_count", 0),
        },
        "software_packages": {
            "total_packages": sw_inv.get("total_packages", 0),
            "unique_package_count": sw_inv.get("unique_packages", 0),
            "vendor_distribution": sw_inv.get("vendor_distribution", {}),
            "category_distribution": sw_inv.get("category_distribution", {}),
            "unique_package_list": unique_package_list,
        },
        "cloud_readiness": cr,
        "capacity_match": capacity.get("equivalence_match", {}),
    }


# Function: _build_llm_prompt
def _build_llm_prompt(infra_data):
    return f"""Analyze this infrastructure scan and produce a comprehensive failure prediction analysis.

Infrastructure Data (JSON):
{json.dumps(infra_data, indent=2)}

Respond with ONLY valid JSON matching this exact schema (no prose, no markdown):
{{
  "risk_score": <integer 0-100>,
  "risk_level": "<Critical|High|Medium|Low>",
  "executive_summary": "<2-3 sentences covering overall risk posture, main threats, and urgency>",
  "predicted_failures": [
    {{
      "id": "pf-1",
      "component": "<server_name | subnet | service_name | 'Infrastructure'>",
      "component_type": "<server|network|service|security|storage>",
      "failure_type": "<hardware_failure|software_crash|network_outage|security_breach|capacity_exhaustion|eos_vulnerability|config_error|missing_redundancy>",
      "probability": "<critical|high|medium|low>",
      "timeframe": "<immediate|30_days|90_days|6_months|1_year>",
      "description": "<clear description of what could fail and why>",
      "impact_chain": ["<component_name_1>", "<component_name_2>"],
      "blast_radius": "<critical|major|moderate|minor>",
      "affected_services": ["<service_name>"]
    }}
  ],
  "root_causes": [
    {{
      "id": "rc-1",
      "category": "<eos_os|eos_software|single_point_of_failure|capacity_exhaustion|security_gap|missing_redundancy|network_segmentation|config_drift>",
      "description": "<root cause description>",
      "contributing_factors": ["<factor>"],
      "linked_failures": ["pf-1"]
    }}
  ],
  "preventive_measures": [
    {{
      "id": "pm-1",
      "priority": "<P1_critical|P2_high|P3_medium|P4_low>",
      "action": "<specific actionable step>",
      "rationale": "<why this prevents the failure>",
      "effort": "<low|medium|high>",
      "linked_root_causes": ["rc-1"],
      "deadline_days": <integer>
    }}
  ],
  "topology_risks": {{
    "single_points_of_failure": ["<component>"],
    "isolated_segments": ["<subnet>"],
    "overloaded_servers": ["<server>"],
    "unpatched_services": ["<service>"],
    "missing_ha": ["<server>"]
  }}
}}"""


# Function: analyze_infrastructure_failures
def analyze_infrastructure_failures(scan_report: dict) -> dict:
    """
    Use GPU-accelerated LLM to analyze infrastructure for failure prediction.
    Falls back to heuristic analysis if Ollama is unavailable.
    """
    model = _get_best_gpu_model()
    if not model:
        result = _heuristic_analysis(scan_report)
        result["model_used"] = "heuristic (Ollama unavailable)"
        return result

    infra_data = _build_infra_data(scan_report)
    prompt = _build_llm_prompt(infra_data)
    raw = _call_ollama(model, prompt, system=_SYSTEM_PROMPT)
    result = _extract_json(raw)

    if not result or "predicted_failures" not in result:
        log.warning("LLM returned invalid JSON — falling back to heuristic analysis")
        result = _heuristic_analysis(scan_report)
        result["model_used"] = f"{model} (json_parse_failed — heuristic used)"
    else:
        result["model_used"] = model

    return result


# ─── Heuristic (rule-based) fallback ─────────────────────────────────────────

# Function: _add_rc
def _add_rc(root_causes, rc_map, cat, desc, factors, linked):
    if cat in rc_map:
        rc = next(r for r in root_causes if r["id"] == rc_map[cat])
        rc["linked_failures"] = list(set(rc["linked_failures"] + linked))
        return rc_map[cat]
    rc_id = f"rc-{len(root_causes) + 1}"
    rc_map[cat] = rc_id
    root_causes.append({"id": rc_id, "category": cat, "description": desc,
                         "contributing_factors": factors, "linked_failures": linked})
    return rc_id


# Function: _heuristic_server_health
def _heuristic_server_health(servers, eos_os_l, failures, root_causes, measures, rc_map, overloaded):
    for srv in eos_os_l:
        name = srv.get("server_name", "unknown")
        pf = f"pf-{len(failures) + 1}"
        failures.append({
            "id": pf, "component": name, "component_type": "server",
            "failure_type": "eos_vulnerability", "probability": "critical",
            "timeframe": "immediate",
            "description": f"{name} runs {srv.get('os','')} which reached end-of-support {srv.get('end_of_support','')}. "
                           "No security patches are released — active CVEs remain unmitigated.",
            "impact_chain": [name],
            "blast_radius": "critical",
            "affected_services": [],
        })
        rc = _add_rc(root_causes, rc_map, "eos_os",
            "End-of-life OS receives no patches; known exploits accumulate without remediation.",
            ["No OS upgrade roadmap", "Missing patch management policy"], [pf])
        measures.append({
            "id": f"pm-{len(measures) + 1}", "priority": "P1_critical",
            "action": f"Immediately upgrade OS on {name} to a supported release or migrate workloads.",
            "rationale": "EOL OS has published CVEs that attackers actively exploit.",
            "effort": "high", "linked_root_causes": [rc], "deadline_days": 30,
        })
    for s in servers:
        name = s.get("server_name") or s.get("name", "unknown")
        cpu  = s.get("cpu_util_pct", -1) or -1
        ram  = s.get("ram_util_pct", -1) or -1
        wl   = [w.get("name") for w in (s.get("workloads") or [])]
        if cpu >= 85 or ram >= 85:
            overloaded.append(name)
            res  = "CPU" if cpu >= 85 else "RAM"
            val  = cpu if cpu >= 85 else ram
            pf   = f"pf-{len(failures) + 1}"
            failures.append({
                "id": pf, "component": name, "component_type": "server",
                "failure_type": "capacity_exhaustion", "probability": "high",
                "timeframe": "30_days",
                "description": f"{name} {res} utilization is {val:.0f}%. "
                               "Sustained saturation causes OOM kills and service crashes.",
                "impact_chain": [name] + wl[:4], "blast_radius": "major",
                "affected_services": wl[:4],
            })
            rc = _add_rc(root_causes, rc_map, "capacity_exhaustion",
                "Servers running near capacity have no headroom for load spikes.",
                ["No auto-scaling", "Workload growth unmonitored"], [pf])
            measures.append({
                "id": f"pm-{len(measures) + 1}", "priority": "P2_high",
                "action": f"Right-size {name}: reduce {res} load below 70% threshold. "
                          "Migrate workloads or increase {res} capacity.",
                "rationale": f"High {res} utilization leads to OOM errors and service degradation.",
                "effort": "medium", "linked_root_causes": [rc], "deadline_days": 14,
            })


# Function: _heuristic_network_health
def _heuristic_network_health(servers, net_topo, failures, root_causes, measures, rc_map, spof):
    for s in servers:
        name  = s.get("server_name") or s.get("name", "unknown")
        ifaces = s.get("interfaces") or []
        wl    = [w.get("name") for w in (s.get("workloads") or [])]
        if len(ifaces) <= 1 and wl:
            spof.append(name)
            pf = f"pf-{len(failures) + 1}"
            failures.append({
                "id": pf, "component": name, "component_type": "network",
                "failure_type": "network_outage", "probability": "medium",
                "timeframe": "6_months",
                "description": f"{name} has a single NIC with no bonding/teaming. "
                               "One NIC failure isolates the server completely.",
                "impact_chain": [name], "blast_radius": "major",
                "affected_services": wl[:4],
            })
            rc = _add_rc(root_causes, rc_map, "single_point_of_failure",
                "Single NIC provides no path redundancy. Any NIC failure = server unreachable.",
                ["No NIC bonding/LACP configured", "No secondary network path"], [pf])
            measures.append({
                "id": f"pm-{len(measures) + 1}", "priority": "P3_medium",
                "action": f"Add secondary NIC and configure bonding/teaming on {name}.",
                "rationale": "NIC redundancy eliminates single network path as a failure point.",
                "effort": "medium", "linked_root_causes": [rc], "deadline_days": 60,
            })
    subnets = net_topo.get("subnets", []) or []
    if len(subnets) <= 1 and len(servers) > 3:
        pf = f"pf-{len(failures) + 1}"
        failures.append({
            "id": pf, "component": "Network Architecture",
            "component_type": "network", "failure_type": "security_breach",
            "probability": "medium", "timeframe": "90_days",
            "description": "All servers reside in a single flat network segment. "
                           "A breach on one server enables lateral movement to all others.",
            "impact_chain": [s.get("server_name") or s.get("name","") for s in servers[:5]],
            "blast_radius": "critical", "affected_services": [],
        })
        rc = _add_rc(root_causes, rc_map, "network_segmentation",
            "Flat network topology enables unrestricted lateral movement after initial breach.",
            ["No VLAN segmentation", "No micro-segmentation", "No east-west firewall"], [pf])
        measures.append({
            "id": f"pm-{len(measures) + 1}", "priority": "P2_high",
            "action": "Implement VLAN segmentation: DMZ, App, DB, Management zones with firewall rules.",
            "rationale": "Segmentation limits blast radius of lateral movement after breach.",
            "effort": "high", "linked_root_causes": [rc], "deadline_days": 60,
        })


# Function: _heuristic_storage_health
def _heuristic_storage_health(sw_inv, failures, root_causes, measures, rc_map):
    eos_sw = sw_inv.get("eos_count", 0)
    exp_sw = sw_inv.get("expiring_soon_count", 0)
    if eos_sw > 0:
        pf = f"pf-{len(failures) + 1}"
        failures.append({
            "id": pf, "component": "Installed Software",
            "component_type": "security", "failure_type": "eos_vulnerability",
            "probability": "high", "timeframe": "immediate",
            "description": f"{eos_sw} installed packages are EOS; {exp_sw} more expire within 180 days. "
                           "These constitute a broad attack surface for known CVEs.",
            "impact_chain": [], "blast_radius": "moderate", "affected_services": [],
        })
        rc = _add_rc(root_causes, rc_map, "eos_software",
            "Accumulated EOS packages enlarge the attack surface.",
            ["No automated patching", "Version lock by dependencies"], [pf])
        measures.append({
            "id": f"pm-{len(measures) + 1}", "priority": "P2_high",
            "action": f"Audit and update {eos_sw} EOS packages; prioritise "
                      "security-category (openssl, openssh, libc).",
            "rationale": "EOS packages are actively targeted by automated exploit scanners.",
            "effort": "medium", "linked_root_causes": [rc], "deadline_days": 14,
        })


# Function: _heuristic_application_health
def _heuristic_application_health(servers, eos_wl_l, failures, root_causes, measures, rc_map, missing_ha):
    for eos in eos_wl_l[:6]:
        name = eos.get("server_name", "unknown")
        wl   = eos.get("workload", "unknown")
        pf   = f"pf-{len(failures) + 1}"
        failures.append({
            "id": pf, "component": f"{name}/{wl}", "component_type": "service",
            "failure_type": "eos_vulnerability", "probability": "high",
            "timeframe": "30_days",
            "description": f"{wl} on {name} reached end-of-support. "
                           "Published CVEs are no longer patched by the vendor.",
            "impact_chain": [name, wl], "blast_radius": "major",
            "affected_services": [wl],
        })
        rc = _add_rc(root_causes, rc_map, "eos_software",
            "EOS middleware/apps have unpatched CVEs exposing the host to exploit.",
            ["No version upgrade policy", "Legacy dependency lock"], [pf])
        measures.append({
            "id": f"pm-{len(measures) + 1}", "priority": "P2_high",
            "action": f"Upgrade {wl} on {name} to a vendor-supported version.",
            "rationale": "EOS software is actively exploited by automated scanners.",
            "effort": "medium", "linked_root_causes": [rc], "deadline_days": 30,
        })
    for s in servers:
        name = s.get("server_name") or s.get("name", "unknown")
        ha   = (s.get("ha_dr_requirements") or "").lower()
        wl   = s.get("workloads") or []
        if not ha or ha in ("none", "n/a") and wl:
            missing_ha.append(name)
    if missing_ha:
        pf = f"pf-{len(failures) + 1}"
        failures.append({
            "id": pf, "component": "Infrastructure HA",
            "component_type": "server", "failure_type": "missing_redundancy",
            "probability": "medium", "timeframe": "90_days",
            "description": f"{len(missing_ha)} server(s) have no HA/DR configuration "
                           f"({', '.join(missing_ha[:3])}{'…' if len(missing_ha) > 3 else ''}). "
                           "Any hardware failure causes service downtime with no automatic recovery.",
            "impact_chain": missing_ha[:5], "blast_radius": "major",
            "affected_services": [],
        })
        rc = _add_rc(root_causes, rc_map, "missing_redundancy",
            "Absence of HA clustering or failover means hardware failure = unplanned downtime.",
            ["No clustering solution", "No automated failover", "Missing DR runbooks"], [pf])
        measures.append({
            "id": f"pm-{len(measures) + 1}", "priority": "P2_high",
            "action": "Deploy HA clustering (active-passive minimum) for workload-bearing servers. "
                      "Define RTO/RPO per service.",
            "rationale": "HA prevents single server failure from causing extended service outage.",
            "effort": "high", "linked_root_causes": [rc], "deadline_days": 90,
        })


# Function: _heuristic_build_summary
def _heuristic_build_summary(servers, failures, root_causes, measures, eos_wl_l, spof, overloaded, missing_ha):
    crit  = sum(1 for f in failures if f["probability"] == "critical")
    high  = sum(1 for f in failures if f["probability"] == "high")
    med   = sum(1 for f in failures if f["probability"] == "medium")
    score = min(100, crit * 25 + high * 10 + med * 5)
    level = ("Critical" if score >= 75 else "High" if score >= 50
             else "Medium" if score >= 25 else "Low")
    return {
        "model_used": "heuristic",
        "risk_score": score,
        "risk_level": level,
        "executive_summary": (
            f"Analysis of {len(servers)} server(s) identified {len(failures)} failure risk(s). "
            f"{crit} critical and {high} high-priority issues require immediate action. "
            f"Primary threats: EOS OS/software, missing HA/DR, and single-NIC exposure."
        ),
        "predicted_failures": failures,
        "root_causes": root_causes,
        "preventive_measures": sorted(
            measures,
            key=lambda m: {"P1_critical": 0, "P2_high": 1, "P3_medium": 2, "P4_low": 3}.get(m["priority"], 9),
        ),
        "topology_risks": {
            "single_points_of_failure": spof,
            "isolated_segments": [],
            "overloaded_servers": overloaded,
            "unpatched_services": [e.get("workload", "") for e in eos_wl_l[:5]],
            "missing_ha": missing_ha,
        },
    }


# Function: _heuristic_analysis
def _heuristic_analysis(scan_report: dict) -> dict:
    """
    Rule-based failure prediction when LLM is unavailable.
    Covers the most common failure patterns systematically.
    """
    today = date.today()
    servers    = scan_report.get("servers", []) or []
    eos_os_l   = scan_report.get("eos_advisory_os", []) or []
    eos_wl_l   = scan_report.get("eos_advisory_workload", []) or []
    sw_inv     = scan_report.get("software_inventory", {}) or {}
    net_topo   = scan_report.get("network_topology", {}) or {}

    failures: list[dict] = []
    root_causes: list[dict] = []
    measures: list[dict] = []
    rc_map: dict[str, str] = {}  # category → rc_id
    spof: list[str] = []
    overloaded: list[str] = []
    missing_ha: list[str] = []

    _heuristic_server_health(servers, eos_os_l, failures, root_causes, measures, rc_map, overloaded)
    _heuristic_network_health(servers, net_topo, failures, root_causes, measures, rc_map, spof)
    _heuristic_storage_health(sw_inv, failures, root_causes, measures, rc_map)
    _heuristic_application_health(servers, eos_wl_l, failures, root_causes, measures, rc_map, missing_ha)
    return _heuristic_build_summary(servers, failures, root_causes, measures, eos_wl_l, spof, overloaded, missing_ha)


# ─── Model status ─────────────────────────────────────────────────────────────

# Function: get_model_info
def get_model_info() -> dict:
    """Return current LLM model status."""
    global _cached_model, _models_unavailable
    # Reset cache so we always check fresh
    _models_unavailable = False
    _cached_model = None
    model = _get_best_gpu_model()
    if not model:
        return {
            "available": False,
            "model": None,
            "inference_type": "heuristic",
            "message": "Ollama not running or no models installed. Using rule-based analysis.",
            "ollama_url": OLLAMA_BASE,
        }
    return {
        "available": True,
        "model": model,
        "inference_type": "gpu_llm",
        "base_url": OLLAMA_BASE,
        "message": f"GPU-accelerated inference via Ollama — model: {model}",
        "priority_list": _MODEL_PRIORITY,
    }
