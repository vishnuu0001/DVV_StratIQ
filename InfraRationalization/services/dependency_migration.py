# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: services/dependency_migration.py
# Date: 2025-07-20
# ---------------------------------------------------------------------------
"""
services/dependency_migration.py
Application Dependency Mapping & Migration Wave Planning.

Features:
  - Dependency graph: which servers communicate (via ARP, routes, open ports)
  - Migration wave planner: group into waves based on dependency chains
  - Effort estimation: complexity score per server
  - Migration sequencing: what must be migrated before what
"""
from __future__ import annotations

import logging
from collections import defaultdict, deque
from typing import Any

log = logging.getLogger(__name__)

# Ports that indicate a server is being USED BY others (downstream dependency)
_DB_PORTS   = {3306, 5432, 1433, 1521, 27017, 6379, 9042, 5984}
_APP_PORTS  = {8080, 8443, 8009, 8005, 7001, 9001, 4848, 9090}
_QUEUE_PORTS= {5672, 9092, 2181, 61616}
_SEARCH_PORTS = {9200, 8983}

# Effort scoring weights
_EFFORT_WEIGHTS = {
    "os_eos":              3,   # OS is end-of-support — needs upgrade first
    "workload_eos":        2,   # A workload is EOS
    "db_server":           3,   # Databases need migration planning
    "physical_server":     3,   # Physical servers are harder to lift
    "no_ssh_wmi_data":     1,   # Incomplete scan data
    "high_utilization":    2,   # Heavily loaded — risk of downtime
    "custom_workload":     2,   # Non-COTS / custom software
    "many_dependencies":   2,   # Many incoming connections
    "windows_licensed":    1,   # License migration complexity
    "mainframe_dep":       4,   # Mainframe dependency
    "ha_required":         2,   # HA/DR requirements add complexity
    "storage_large":       1,   # Large storage to migrate
}


# Function: _server_id
def _server_id(srv: dict) -> str:
    return (srv.get("server_ip") or srv.get("ip_address") or srv.get("ip") or
            srv.get("server_name") or srv.get("name") or "unknown")


# Function: _server_name
def _server_name(srv: dict) -> str:
    return srv.get("server_name") or srv.get("name") or _server_id(srv)


# Function: _get_open_ports
def _get_open_ports(srv: dict) -> set[int]:
    ports = set()
    for wl in srv.get("workloads") or []:
        p = wl.get("port")
        if p:
            try:
                ports.add(int(p))
            except (ValueError, TypeError):
                pass
    for p in srv.get("open_ports") or []:
        try:
            ports.add(int(p))
        except (ValueError, TypeError):
            pass
    return ports


# Function: _classify_by_port
def _classify_by_port(ports: set[int]) -> str | None:
    if ports & _DB_PORTS:
        return "database"
    if ports & _QUEUE_PORTS:
        return "middleware"
    if ports & _SEARCH_PORTS:
        return "search"
    if ports & _APP_PORTS:
        return "application"
    return None


_WORKLOAD_ROLE_KEYWORDS = [
    ("database", ["mysql", "postgres", "oracle", "mssql", "mongo", "redis", "db2"]),
    ("middleware", ["kafka", "rabbitmq", "activemq", "zookeeper"]),
    ("web", ["nginx", "apache", "iis", "haproxy"]),
    ("application", ["tomcat", "jboss", "wildfly", "weblogic", "glassfish"]),
]


# Function: _classify_by_workload_name
def _classify_by_workload_name(wl: str) -> str | None:
    for role, keywords in _WORKLOAD_ROLE_KEYWORDS:
        if any(x in wl for x in keywords):
            return role
    return None


# Function: _classify_server_role
def _classify_server_role(srv: dict) -> str:
    """Classify server as: database / middleware / web / app / utility / unknown."""
    ports = _get_open_ports(srv)
    role = _classify_by_port(ports)
    if role:
        return role

    for wl in (w.get("name", "").lower() for w in (srv.get("workloads") or [])):
        role = _classify_by_workload_name(wl)
        if role:
            return role

    env = (srv.get("environment") or "").lower()
    if "dev" in env or "test" in env or "qa" in env:
        return "dev_test"
    return "unknown"


# Function: _build_ip_to_id_index
def _build_ip_to_id_index(servers: list[dict]) -> dict[str, str]:
    """Index servers by IP (primary IP + all interface IPs)."""
    ip_to_id: dict[str, str] = {}
    for srv in servers:
        sid = _server_id(srv)
        ip  = srv.get("ip_address") or srv.get("ip") or srv.get("server_ip") or ""
        if ip:
            ip_to_id[ip] = sid
        for iface in (srv.get("interfaces") or []):
            iface_ip = iface.get("ip_address") or iface.get("ip") or ""
            if iface_ip:
                ip_to_id[iface_ip] = sid
    return ip_to_id


# Function: _add_peer_dependencies
def _add_peer_dependencies(entries: list, ip_key: str, ip_to_id: dict, sid: str, target_list: list) -> None:
    """Resolve a list of neighbor/route entries to peer server ids and append new ones to target_list."""
    for entry in entries:
        peer_ip = entry.get(ip_key) or ""
        if peer_ip in ip_to_id and ip_to_id[peer_ip] != sid:
            target = ip_to_id[peer_ip]
            if target not in target_list:
                target_list.append(target)


# Function: _add_role_based_dependencies
def _add_role_based_dependencies(servers: list[dict], deps: dict[str, list[str]], role_map: dict[str, str]) -> None:
    """Heuristic: app/web servers depend on servers hosting DB/queue services."""
    db_server_ids = [sid for sid, role in role_map.items() if role == "database"]
    mw_server_ids = [sid for sid, role in role_map.items() if role == "middleware"]

    for srv in servers:
        sid  = _server_id(srv)
        role = role_map[sid]
        if role not in ("application", "web"):
            continue
        for db_sid in db_server_ids:
            if db_sid != sid and db_sid not in deps[sid]:
                deps[sid].append(db_sid)
        for mw_sid in mw_server_ids:
            if mw_sid != sid and mw_sid not in deps[sid]:
                deps[sid].append(mw_sid)


# Function: _build_dependency_graph
def _build_dependency_graph(servers: list[dict]) -> dict[str, list[str]]:
    """
    Build directed graph: server_id → [list of server_ids it depends on].
    Uses ARP neighbors, routes, and port connectivity heuristics.
    """
    ip_to_id = _build_ip_to_id_index(servers)
    deps: dict[str, list[str]] = {_server_id(s): [] for s in servers}

    for srv in servers:
        sid = _server_id(srv)
        _add_peer_dependencies(srv.get("arp_neighbors") or [], "ip", ip_to_id, sid, deps[sid])
        _add_peer_dependencies(srv.get("routes") or [], "gateway", ip_to_id, sid, deps[sid])
        _add_peer_dependencies(srv.get("lldp_neighbors") or [], "ip", ip_to_id, sid, deps[sid])

    # Heuristic: servers hosting DB/queue services are depended on by app servers
    role_map: dict[str, str] = {_server_id(s): _classify_server_role(s) for s in servers}
    _add_role_based_dependencies(servers, deps, role_map)

    return deps


# Function: _compute_in_degree
def _compute_in_degree(deps: dict[str, list[str]]) -> dict[str, int]:
    in_degree: dict[str, int] = {node: 0 for node in deps}
    for edges in deps.values():
        for target in edges:
            if target in in_degree:
                in_degree[target] += 1
    return in_degree


# Function: _release_ready_dependents
def _release_ready_dependents(node: str, deps: dict[str, list[str]], in_degree: dict[str, int], queue: deque) -> None:
    for target in deps.get(node, []):
        if target in in_degree:
            in_degree[target] -= 1
            if in_degree[target] == 0:
                queue.append(target)


# Function: _topological_sort
def _topological_sort(deps: dict[str, list[str]]) -> list[str]:
    """
    Topological sort of dependency graph (Kahn's algorithm).
    Returns ordered list from most-independent to most-depended-upon.
    Handles cycles by treating cyclic nodes as same level.
    """
    in_degree = _compute_in_degree(deps)

    queue = deque([n for n, d in in_degree.items() if d == 0])
    ordered: list[str] = []
    while queue:
        node = queue.popleft()
        ordered.append(node)
        _release_ready_dependents(node, deps, in_degree, queue)

    # Add any remaining (cyclic) nodes
    remaining = [n for n in deps if n not in ordered]
    ordered.extend(remaining)
    return ordered


# Function: _effort_factor_os_eos
def _effort_factor_os_eos(srv: dict, in_degree: int):
    eos_date = srv.get("os_end_of_support") or ""
    if eos_date:
        try:
            from datetime import date
            if date.fromisoformat(eos_date) < date.today():
                return "os_eos", "OS is end-of-support"
        except ValueError:
            pass
    return None


# Function: _effort_factor_workload_eos
def _effort_factor_workload_eos(srv: dict, in_degree: int):
    for sw in (srv.get("installed_software") or []):
        if sw.get("is_eos"):
            return "workload_eos", f"EOS software: {sw.get('name','')}"
    return None


# Function: _effort_factor_physical_server
def _effort_factor_physical_server(srv: dict, in_degree: int):
    if (srv.get("server_type") or "").lower() == "physical":
        return "physical_server", "Physical server (P2V required)"
    return None


# Function: _effort_factor_db_server
def _effort_factor_db_server(srv: dict, in_degree: int):
    if _classify_server_role(srv) == "database":
        return "db_server", "Database server (data migration required)"
    return None


# Function: _effort_factor_high_utilization
def _effort_factor_high_utilization(srv: dict, in_degree: int):
    cpu_util = srv.get("cpu_util_pct", -1)
    if cpu_util > 75:
        return "high_utilization", f"High CPU utilization ({cpu_util:.0f}%)"
    return None


# Function: _effort_factor_many_dependencies
def _effort_factor_many_dependencies(srv: dict, in_degree: int):
    if in_degree >= 3:
        return "many_dependencies", f"{in_degree} servers depend on this"
    return None


# Function: _effort_factor_windows_licensed
def _effort_factor_windows_licensed(srv: dict, in_degree: int):
    if "windows" in (srv.get("os_name") or srv.get("os_family") or "").lower():
        return "windows_licensed", "Windows license migration"
    return None


# Function: _effort_factor_mainframe_dep
def _effort_factor_mainframe_dep(srv: dict, in_degree: int):
    if srv.get("mainframe_dependency") == "Yes":
        return "mainframe_dep", "Mainframe dependency"
    return None


# Function: _effort_factor_ha_required
def _effort_factor_ha_required(srv: dict, in_degree: int):
    if srv.get("ha_dr_requirements") not in (None, "", "None"):
        return "ha_required", "HA/DR requirements"
    return None


# Function: _effort_factor_storage_large
def _effort_factor_storage_large(srv: dict, in_degree: int):
    storage_gb = srv.get("total_storage_gb") or srv.get("internal_storage_gb") or 0
    if storage_gb > 500:
        return "storage_large", f"Large storage ({storage_gb:.0f} GB)"
    return None


_EFFORT_FACTOR_CHECKS = [
    _effort_factor_os_eos,
    _effort_factor_workload_eos,
    _effort_factor_physical_server,
    _effort_factor_db_server,
    _effort_factor_high_utilization,
    _effort_factor_many_dependencies,
    _effort_factor_windows_licensed,
    _effort_factor_mainframe_dep,
    _effort_factor_ha_required,
    _effort_factor_storage_large,
]


# Function: _effort_score
def _effort_score(srv: dict, in_degree: int) -> dict:
    """Compute effort score (0-100) and contributing factors."""
    score = 0
    factors: list[str] = []

    for check in _EFFORT_FACTOR_CHECKS:
        result = check(srv, in_degree)
        if result:
            weight_key, factor = result
            score += _EFFORT_WEIGHTS[weight_key]
            factors.append(factor)

    level = "Low" if score <= 3 else "Medium" if score <= 6 else "High"
    return {"score": score, "level": level, "factors": factors}


# Function: _assign_wave
def _assign_wave(role: str, effort_level: str, in_degree: int) -> int:
    """
    Wave assignment logic:
      Wave 1 — Dev/Test, low-effort independent servers
      Wave 2 — Utility & web/app servers with no upstream deps
      Wave 3 — Middleware (message queues, load balancers)
      Wave 4 — Application servers with dependencies
      Wave 5 — Databases and high-effort servers
    """
    if role == "dev_test":
        return 1
    if effort_level == "Low" and in_degree == 0:
        return 2
    if role in ("web",):
        return 2
    if role == "middleware":
        return 3
    if role == "application":
        return 4
    if role == "database":
        return 5
    if effort_level == "High":
        return 5
    return 3


# Function: build_dependency_map
def build_dependency_map(report: dict) -> dict:
    """Main entry point. Returns dependency analysis section."""
    servers = report.get("servers") or []
    if not servers:
        return {"error": "No servers in report", "nodes": [], "edges": [], "waves": {}}

    # Build graph
    deps  = _build_dependency_graph(servers)
    order = _topological_sort(deps)

    # Compute in-degree (how many servers depend on each)
    in_degree_map: dict[str, int] = defaultdict(int)
    for edges in deps.values():
        for target in edges:
            in_degree_map[target] += 1

    # Build per-server node info
    srv_map = {_server_id(s): s for s in servers}
    nodes: list[dict] = []
    waves: dict[int, list[str]] = defaultdict(list)

    for sid in order:
        srv  = srv_map.get(sid, {})
        role = _classify_server_role(srv)
        in_deg = in_degree_map.get(sid, 0)
        effort = _effort_score(srv, in_deg)
        wave   = _assign_wave(role, effort["level"], in_deg)

        node = {
            "id":           sid,
            "name":         _server_name(srv),
            "ip":           srv.get("ip_address") or srv.get("ip") or srv.get("server_ip") or "",
            "role":         role,
            "environment":  srv.get("environment") or "",
            "os":           srv.get("os_name") or srv.get("os_family") or "",
            "dependencies": deps.get(sid, []),
            "dependents":   [n for n, edges in deps.items() if sid in edges],
            "in_degree":    in_deg,
            "effort":       effort,
            "wave":         wave,
            "migration_order": order.index(sid) + 1,
        }
        nodes.append(node)
        waves[wave].append(sid)

    # Build edge list for graph rendering
    edges: list[dict] = []
    for src, targets in deps.items():
        for tgt in targets:
            edges.append({
                "source": src,
                "target": tgt,
                "source_name": _server_name(srv_map.get(src, {})),
                "target_name": _server_name(srv_map.get(tgt, {})),
            })

    # Wave summary
    wave_summary: list[dict] = []
    wave_labels = {
        1: "Wave 1 — Dev/Test Environments",
        2: "Wave 2 — Independent Web / Utility Servers",
        3: "Wave 3 — Middleware & Integration Layer",
        4: "Wave 4 — Application Servers",
        5: "Wave 5 — Databases & High-Effort Servers",
    }
    for w in sorted(waves.keys()):
        wave_servers = [n for n in nodes if n["wave"] == w]
        total_effort = sum(n["effort"]["score"] for n in wave_servers)
        wave_summary.append({
            "wave":        w,
            "label":       wave_labels.get(w, f"Wave {w}"),
            "server_ids":  waves[w],
            "server_names": [_server_name(srv_map.get(sid, {})) for sid in waves[w]],
            "server_count": len(waves[w]),
            "total_effort_score": total_effort,
            "avg_effort_score": round(total_effort / len(waves[w]), 1) if waves[w] else 0,
        })

    return {
        "nodes":       nodes,
        "edges":       edges,
        "wave_plan":   wave_summary,
        "summary": {
            "total_servers":   len(nodes),
            "total_edges":     len(edges),
            "total_waves":     len(waves),
            "high_effort_count":   sum(1 for n in nodes if n["effort"]["level"] == "High"),
            "medium_effort_count": sum(1 for n in nodes if n["effort"]["level"] == "Medium"),
            "low_effort_count":    sum(1 for n in nodes if n["effort"]["level"] == "Low"),
            "database_servers":    sum(1 for n in nodes if n["role"] == "database"),
            "middleware_servers":  sum(1 for n in nodes if n["role"] == "middleware"),
        },
    }
