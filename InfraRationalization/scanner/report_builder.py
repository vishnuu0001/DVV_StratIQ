# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: scanner/report_builder.py
# Date: 2025-08-08
# ---------------------------------------------------------------------------
"""
scanner/report_builder.py
Converts a list[DiscoveredServer] into a Corent MaaS™-compatible JSON report dict.

Sections produced:
  1. summary           — total_servers, scan metadata
  2. cloud_assessment  — OS/server-type/IP/utilization/storage distribution
  3. cloud_readiness   — migration strategy counts
  4. capacity_planning — equivalence vs best-match totals
  5. vm_flavors        — placeholder flavor recommendations
  6. workload_consolidation — MySQL / Tomcat consolidation hints
  7. paas_recommendations  — managed-service candidates
  8. eos_advisory_os       — OS end-of-support data
  9. eos_advisory_workload — workload end-of-support data
 10. storage_recommendation
 11. kubernetes_recommendation
 12. sustainability         — CO₂/power estimates
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from datetime import date, datetime
from typing import Any

from .models import DiscoveredServer, ScanTarget, ScanJob
from . import cloud_pricing as pricing

# ── EOS reference tables ────────────────────────────────────────────────────

_OS_EOS: dict[str, tuple[str, str | None]] = {
    # (end_of_support, extended_support)
    "windows server 2003": ("2015-07-14", None),
    "windows server 2008": ("2020-01-14", "2023-01-10"),
    "windows server 2012": ("2023-10-10", "2026-10-13"),
    "windows server 2016": ("2027-01-12", None),
    "windows server 2019": ("2029-01-09", None),
    "windows server 2022": ("2031-10-14", None),
    "red hat enterprise linux 6": ("2020-11-30", None),
    "red hat enterprise linux 7": ("2024-06-30", None),
    "red hat enterprise linux 8": ("2029-05-31", None),
    "red hat enterprise linux 9": ("2032-05-31", None),
    "centos 6": ("2020-11-30", None),
    "centos 7": ("2024-06-30", None),
    "centos 8": ("2021-12-31", None),
    "ubuntu 16.04": ("2021-04-30", None),
    "ubuntu 18.04": ("2023-04-30", "2028-04-30"),
    "ubuntu 20.04": ("2025-04-30", "2030-04-30"),
    "ubuntu 22.04": ("2027-04-30", "2032-04-30"),
    "ubuntu 24.04": ("2029-04-30", "2034-04-30"),
    "debian 9": ("2022-06-30", None),
    "debian 10": ("2024-06-30", None),
    "debian 11": ("2026-06-30", None),
}

# Recommended migration target OS per source OS (for EOS advisory text)
_OS_MIGRATION_TARGET: dict[str, str] = {
    "windows server 2003": "Windows Server 2022",
    "windows server 2008": "Windows Server 2022",
    "windows server 2012": "Windows Server 2022",
    "windows server 2016": "Windows Server 2022",
    "windows server 2019": "Windows Server 2022",
    "windows server 2022": "Windows Server 2025",
    "red hat enterprise linux 6": "Red Hat Enterprise Linux 9.3",
    "red hat enterprise linux 7": "Red Hat Enterprise Linux 9.3",
    "red hat enterprise linux 8": "Red Hat Enterprise Linux 9.3",
    "red hat enterprise linux 9": "Red Hat Enterprise Linux 9.3",
    "centos 6": "Red Hat Enterprise Linux 9.3",
    "centos 7": "Red Hat Enterprise Linux 9.3",
    "centos 8": "Red Hat Enterprise Linux 9.3",
    "ubuntu 16.04": "Ubuntu 22.04 LTS",
    "ubuntu 18.04": "Ubuntu 22.04 LTS",
    "ubuntu 20.04": "Ubuntu 22.04 LTS",
    "ubuntu 22.04": "Ubuntu 24.04 LTS",
    "ubuntu 24.04": "Ubuntu 24.04 LTS",
    "debian 9": "Debian 12",
    "debian 10": "Debian 12",
    "debian 11": "Debian 12",
}

_WORKLOAD_EOS: dict[str, str] = {
    # workload_name_lower: end_of_support date
    "mysql 5.5": "2018-12-31",
    "mysql 5.6": "2021-02-28",
    "mysql 5.7": "2023-10-31",
    "mysql 8.0": "2026-04-30",
    "postgresql 9.6": "2021-11-11",
    "postgresql 10": "2022-11-10",
    "postgresql 11": "2023-11-09",
    "postgresql 12": "2024-11-14",
    "postgresql 13": "2025-11-13",
    "postgresql 14": "2026-11-12",
    "postgresql 15": "2027-11-11",
    "mssql server 2014": "2024-07-09",
    "mssql server 2016": "2026-07-14",
    "mssql server 2019": "2030-01-08",
    "apache tomcat 7": "2021-03-31",
    "apache tomcat 8.5": "2024-03-31",
    "apache tomcat 9": "2027-03-31",
    "apache tomcat 9.0": "2027-03-31",
    "apachetomcat 9": "2027-03-31",
    "apachetomcat 9.0": "2027-03-31",
    "apache tomcat 10": "2028-12-31",
    "node.js 14": "2023-04-30",
    "node.js 16": "2024-09-11",
    "node.js 18": "2025-04-30",
    "node.js 20": "2026-04-30",
}

# ── Software package EOS table (for installed_software analysis) ─────────────

_SOFTWARE_EOS: dict[str, str] = {
    # ── Python runtimes ───────────────────────────────────────────────────
    "python2": "2020-01-01",
    "python2.7": "2020-01-01",
    "python3.6": "2021-12-23",
    "python3.7": "2023-06-27",
    "python3.8": "2024-10-07",
    "python3.9": "2025-10-05",
    "python3.10": "2026-10-04",
    "python3.11": "2027-10-24",
    "python3.12": "2028-10-02",
    "python3.13": "2029-10-31",
    "python3": "2027-10-24",  # default to latest stable LTS
    "python": "2027-10-24",
    # ── Node.js / npm ─────────────────────────────────────────────────────
    "nodejs-12": "2022-04-30",
    "nodejs-14": "2023-04-30",
    "nodejs-16": "2024-09-11",
    "nodejs-18": "2025-04-30",
    "nodejs-20": "2026-04-30",
    "nodejs-22": "2027-04-30",
    "nodejs": "2025-04-30",
    "node": "2025-04-30",
    "npm": "2025-04-30",
    # ── Java / JDK ────────────────────────────────────────────────────────
    "java-8-openjdk": "2026-03-31",
    "java-11-openjdk": "2027-09-30",
    "java-17-openjdk": "2029-09-30",
    "java-21-openjdk": "2031-09-30",
    "openjdk-8": "2026-03-31",
    "openjdk-11": "2027-09-30",
    "openjdk-17": "2029-09-30",
    "openjdk-21": "2031-09-30",
    "java-8": "2026-03-31",
    "java-11": "2027-09-30",
    "java-17": "2029-09-30",
    "java-21": "2031-09-30",
    "jdk-8": "2026-03-31",
    "jdk-11": "2027-09-30",
    "jdk-17": "2029-09-30",
    "jdk-21": "2031-09-30",
    "jre-8": "2026-03-31",
    "jre-11": "2027-09-30",
    # ── PHP ───────────────────────────────────────────────────────────────
    "php5": "2016-12-31",
    "php7.0": "2019-01-01",
    "php7.1": "2019-12-01",
    "php7.2": "2020-11-30",
    "php7.3": "2021-12-06",
    "php7.4": "2022-11-28",
    "php8.0": "2023-11-26",
    "php8.1": "2025-12-31",
    "php8.2": "2026-12-31",
    "php8.3": "2027-12-31",
    "php": "2026-12-31",
    # ── Ruby ──────────────────────────────────────────────────────────────
    "ruby2.4": "2020-04-05",
    "ruby2.5": "2021-04-05",
    "ruby2.6": "2022-04-12",
    "ruby2.7": "2023-03-31",
    "ruby3.0": "2024-04-23",
    "ruby3.1": "2025-03-31",
    "ruby3.2": "2026-03-31",
    "ruby3.3": "2027-03-31",
    "ruby": "2026-03-31",
    # ── MySQL / MariaDB ───────────────────────────────────────────────────
    "mysql-server-5.5": "2018-12-31",
    "mysql-server-5.6": "2021-02-28",
    "mysql-server-5.7": "2023-10-31",
    "mysql-server-8.0": "2026-04-30",
    "mysql-server-8.4": "2032-04-30",
    "mysql-community-server": "2026-04-30",
    "mysql-server": "2026-04-30",
    "mysql-client": "2026-04-30",
    "mysql": "2026-04-30",
    "mariadb-server-10.3": "2023-05-25",
    "mariadb-server-10.4": "2024-06-18",
    "mariadb-server-10.5": "2025-06-24",
    "mariadb-server-10.6": "2026-07-06",
    "mariadb-server-10.11": "2028-02-16",
    "mariadb-server-11.4": "2029-05-29",
    "mariadb-server": "2026-07-06",
    "mariadb": "2026-07-06",
    # ── PostgreSQL ────────────────────────────────────────────────────────
    "postgresql-9.6": "2021-11-11",
    "postgresql-10": "2022-11-10",
    "postgresql-11": "2023-11-09",
    "postgresql-12": "2024-11-14",
    "postgresql-13": "2025-11-13",
    "postgresql-14": "2026-11-12",
    "postgresql-15": "2027-11-11",
    "postgresql-16": "2028-11-09",
    "postgresql-17": "2029-11-08",
    "postgresql": "2027-11-11",
    # ── MongoDB ───────────────────────────────────────────────────────────
    "mongodb-org-3.6": "2021-04-30",
    "mongodb-org-4.0": "2022-04-30",
    "mongodb-org-4.2": "2023-04-30",
    "mongodb-org-4.4": "2024-02-29",
    "mongodb-org-5.0": "2024-10-01",
    "mongodb-org-6.0": "2025-07-01",
    "mongodb-org-7.0": "2027-08-01",
    "mongodb-org": "2025-07-01",
    "mongodb": "2025-07-01",
    # ── Redis / Memcached ─────────────────────────────────────────────────
    "redis": "2027-12-31",
    "redis-server": "2027-12-31",
    "redis-tools": "2027-12-31",
    "memcached": "2028-12-31",
    # ── Web servers ───────────────────────────────────────────────────────
    "apache2": "2028-12-31",
    "httpd": "2028-12-31",
    "nginx": "2028-12-31",
    "nginx-full": "2028-12-31",
    "nginx-common": "2028-12-31",
    "lighttpd": "2028-12-31",
    # ── Application servers / middleware ──────────────────────────────────
    "tomcat7": "2021-03-31",
    "tomcat8": "2024-03-31",
    "tomcat8.5": "2024-03-31",
    "tomcat9": "2027-03-31",
    "tomcat10": "2028-12-31",
    "tomcat10.1": "2028-12-31",
    "tomcat": "2027-03-31",
    "jetty": "2028-12-31",
    "jboss": "2027-06-30",
    "wildfly": "2028-12-31",
    "glassfish": "2022-09-30",
    "weblogic": "2025-12-31",
    "websphere": "2025-09-30",
    "iis": "2029-01-09",
    # ── Message brokers / search ──────────────────────────────────────────
    "rabbitmq-server": "2028-12-31",
    "rabbitmq": "2028-12-31",
    "kafka": "2028-12-31",
    "activemq": "2027-12-31",
    "elasticsearch": "2028-12-31",
    "elasticsearch-oss": "2025-02-01",
    "opensearch": "2028-12-31",
    "kibana": "2028-12-31",
    "logstash": "2028-12-31",
    "zookeeper": "2027-12-31",
    # ── TLS/SSL / security ────────────────────────────────────────────────
    "openssl": "2027-11-23",
    "openssl1.0": "2019-09-11",
    "openssl1.1": "2023-09-11",
    "openssl3.0": "2026-09-07",
    "openssl3.1": "2025-03-14",
    "openssl3.2": "2027-11-23",
    "openssh-server": "2029-12-31",
    "openssh-client": "2029-12-31",
    "fail2ban": "2028-12-31",
    "ufw": "2028-12-31",
    # ── .NET ─────────────────────────────────────────────────────────────
    "dotnet-sdk-3.1": "2022-12-13",
    "dotnet-runtime-3.1": "2022-12-13",
    "dotnet-sdk-5.0": "2022-05-10",
    "dotnet-runtime-5.0": "2022-05-10",
    "dotnet-sdk-6.0": "2024-11-12",
    "dotnet-runtime-6.0": "2024-11-12",
    "dotnet-sdk-7.0": "2024-05-14",
    "dotnet-runtime-7.0": "2024-05-14",
    "dotnet-sdk-8.0": "2026-11-10",
    "dotnet-runtime-8.0": "2026-11-10",
    "dotnet-sdk-9.0": "2026-05-12",
    "dotnet-runtime-9.0": "2026-05-12",
    "aspnetcore-runtime-8.0": "2026-11-10",
    "aspnetcore-runtime-6.0": "2024-11-12",
    # ── Go ────────────────────────────────────────────────────────────────
    "golang-1.18": "2023-08-01",
    "golang-1.20": "2024-02-06",
    "golang-1.21": "2024-11-05",
    "golang-1.22": "2025-08-06",
    "golang-1.23": "2026-08-06",
    "golang": "2026-08-06",
    # ── Windows software ──────────────────────────────────────────────────
    "microsoft visual c++ 2010": "2020-07-14",
    "microsoft visual c++ 2013": "2023-04-11",
    "microsoft visual c++ 2015": "2025-10-14",
    "microsoft visual c++ 2017": "2027-04-13",
    "microsoft visual c++ 2019": "2029-04-10",
    "microsoft .net framework 3.5": "2029-01-09",
    "microsoft .net framework 4.5": "2022-04-26",
    "microsoft .net framework 4.6": "2022-04-26",
    "microsoft .net framework 4.7": "2027-01-12",
    "microsoft .net framework 4.8": "2031-10-14",
    "visual studio 2019": "2029-04-10",
    "visual studio 2022": "2032-07-14",
    "sql server 2014": "2024-07-09",
    "sql server 2016": "2026-07-14",
    "sql server 2019": "2030-01-08",
    "sql server 2022": "2033-01-11",
    "iis 7.5": "2020-01-14",
    "iis 8.5": "2023-10-10",
    "iis 10.0": "2031-10-14",
    # ── Docker / Kubernetes ───────────────────────────────────────────────
    "docker-ce": "2028-12-31",
    "docker-ce-cli": "2028-12-31",
    "containerd.io": "2028-12-31",
    "kubectl": "2027-12-31",
    "kubeadm": "2027-12-31",
    "kubelet": "2027-12-31",
    # ── Utilities ─────────────────────────────────────────────────────────
    "git": "2030-12-31",
    "curl": "2030-12-31",
    "wget": "2030-12-31",
    "openssh": "2029-12-31",
    "bash": "2030-12-31",
    "vim": "2030-12-31",
    "nano": "2030-12-31",
    "rsync": "2030-12-31",
}



# Function: build_report
def build_report(
    servers: list[DiscoveredServer],
    target: ScanTarget,
    report_name: str,
    scan_job: ScanJob | None = None,
) -> dict[str, Any]:
    now = datetime.utcnow().isoformat()
    report: dict[str, Any] = {
        "report_name": report_name,
        "generated_at": now,
        "provider": target.provider,
        "scan_id": scan_job.scan_id if scan_job else "",
        "sections": {},
    }

    secs = report["sections"]

    # Run analysis
    provider = target.provider
    secs["summary"] = _build_summary(servers, target)
    secs["cloud_assessment"] = _build_cloud_assessment(servers)
    secs["cloud_readiness"] = _build_cloud_readiness(servers)
    secs["capacity_planning"] = _build_capacity_planning(servers)
    secs["vm_flavors"] = _build_vm_flavors(servers)
    secs["cloud_resources_recommendation"] = _build_cloud_resources_recommendation(servers, provider)
    secs["pricing_plans"] = _build_pricing_plans(servers, provider)
    secs["dedicated_host_capacity"] = _build_dedicated_host_capacity(servers, provider)
    secs["vmware_openstack_capacity"] = _build_vmware_openstack_capacity(servers, provider)
    secs["workload_consolidation"] = _build_workload_consolidation(servers)
    secs["paas_recommendations"] = _build_paas_recommendations(servers, provider)
    secs["eos_advisory_os"] = _build_eos_os(servers)
    secs["eos_advisory_workload"] = _build_eos_workload(servers)
    secs["software_inventory"] = _build_software_inventory(servers)
    secs["storage_recommendation"] = _build_storage_recommendation(servers, provider)
    secs["kubernetes_recommendation"] = _build_kubernetes_recommendation(servers, provider)
    secs["sustainability"] = _build_sustainability(servers)
    secs["network_summary"] = _build_network_utilization(servers)
    secs["network_topology"] = _build_network_topology(servers)

    # Include raw server list for detail view
    report["servers"] = [_server_to_dict(s) for s in servers]

    return report


# ── Section builders ────────────────────────────────────────────────────────

# Function: _build_summary
def _build_summary(servers: list[DiscoveredServer], target: ScanTarget) -> dict:
    return {
        "total_servers": len(servers),
        "provider": target.provider,
        "scan_target": target.network_range or target.gcp_project_id or target.azure_subscription_id or "",
        "cloud_providers": list({s.cloud_provider for s in servers if s.cloud_provider}),
        "regions": list({s.region for s in servers if s.region}),
    }


_MAJOR_WORKLOAD_KEYWORDS = {
    "mysql", "postgresql", "postgres", "mssql", "oracle", "mongodb", "redis",
    "apache", "nginx", "iis", "tomcat", "apachetomcat", "jetty", "undertow",
    "kafka", "rabbitmq", "activemq", "elasticsearch", "opensearch", "memcached",
    "haproxy", "varnish", "keycloak", "ldap", "openldap",
}


# Function: _build_cloud_assessment
def _build_cloud_assessment(servers: list[DiscoveredServer]) -> dict:
    os_dist: dict[str, int] = defaultdict(int)
    os_version_dist: dict[str, int] = defaultdict(int)  # exact OS name counts
    util_dist: dict[str, int] = defaultdict(int)
    server_type_dist: dict[str, int] = defaultdict(int)
    boot_type_dist: dict[str, int] = defaultdict(int)
    ip_dist: dict[str, int] = defaultdict(int)
    workload_dist: dict[str, int] = defaultdict(int)
    total_storage_tb = 0.0
    total_ram_gb = 0.0
    total_cpu = 0
    total_workloads = 0
    major_workload_count = 0

    for s in servers:
        os_key = s.os_family or "unknown"
        if "windows" in (s.os_name or "").lower():
            os_key = "Windows"
        elif "linux" in (s.os_name or "").lower() or os_key == "linux":
            os_key = "Linux"
        elif os_key == "managed":
            os_key = "Managed Service"
        os_dist[os_key] += 1
        # Track exact OS version
        if s.os_name:
            os_version_dist[s.os_name] += 1

        util_dist[s.utilization_band or "unknown"] += 1
        server_type_dist[s.server_type or "Virtual"] += 1
        boot_type_dist[s.boot_type or "BIOS"] += 1

        for iface in s.interfaces:
            ip_dist[iface.ip_type or "private"] += 1

        total_storage_tb += (s.total_storage_gb or 0) / 1024
        total_ram_gb += s.ram_gb or 0
        total_cpu += s.cpu_cores or 0

        for w in s.workloads:
            workload_dist[w.name or "Other"] += 1
            total_workloads += 1
            wl_lower = (w.name or "").lower().replace(" ", "")
            if any(kw in wl_lower for kw in _MAJOR_WORKLOAD_KEYWORDS):
                major_workload_count += 1

    other_workload_count = total_workloads - major_workload_count

    # IP distribution as percentage strings
    total_ips = sum(ip_dist.values()) or 1
    ip_pct = {k: f"{round(v / total_ips * 100)}% {k.title()} IP" for k, v in ip_dist.items()}

    return {
        "total_servers": len(servers),
        "os_distribution": dict(os_dist),
        "os_version_distribution": dict(os_version_dist),
        "utilization_distribution": dict(util_dist),
        "server_type_distribution": dict(server_type_dist),
        "boot_type_distribution": dict(boot_type_dist),
        "ip_type_distribution": dict(ip_dist),
        "ip_distribution_summary": ip_pct,
        "total_storage_tb": round(total_storage_tb, 2),
        "total_ram_gb": round(total_ram_gb, 1),
        "total_cpu_cores": total_cpu,
        "workload_components": {
            "total": total_workloads,
            "major_count": major_workload_count,
            "other_count": other_workload_count,
            "distribution": dict(workload_dist),
        },
    }


# OS versions not available as standard cloud template images
_CLOUD_UNAVAILABLE_OS = [
    "ubuntu 24", "ubuntu 23",
    "red hat enterprise linux 9.4", "red hat enterprise linux 9.5",
    "red hat enterprise linux 9.6", "rhel 9.4", "rhel 9.5", "rhel 9.6",
]


# Function: _migration_recommendation_text
def _migration_recommendation_text(server: DiscoveredServer, strategy: str) -> str:
    os = server.os_name or "unknown OS"
    os_lower = os.lower()
    if strategy == "smart_shift_effort":
        if "ubuntu 24" in os_lower or "ubuntu 23" in os_lower:
            rec = "Ubuntu 22.04 LTS"
        elif "red hat enterprise linux 9." in os_lower or "rhel 9." in os_lower:
            rec = "Red Hat Enterprise Linux 9.3"
        else:
            rec = "a supported OS version"
        return (
            f"Your server's Operating System ({os}) is not available in Cloud. "
            f"MaaS\u00ae recommends the OS to {rec} to move your application to Cloud."
        )
    if strategy == "smart_shift":
        return f"Migrate {os} \u2014 end-of-support reached. Upgrade OS version before migrating."
    if strategy == "lift_and_shift":
        return "Server can be migrated as-is using Lift and Shift mode."
    if strategy in ("paas_shift", "paas_shift_effort"):
        return "Workload components suitable for managed PaaS services."
    if strategy == "decommission":
        return (
            f"Server running EOL OS ({os}) with no active workloads and very low utilization. "
            "Recommend decommissioning or repurposing before cloud migration."
        )
    return ""


# Function: _is_os_eol
def _is_os_eol(server: DiscoveredServer) -> bool:
    eos = _os_eos_date(server.os_name or "")
    return eos is not None and eos < date.today()


# Function: _is_paas_web_candidate
def _is_paas_web_candidate(wl_types: set[str]) -> bool:
    return ("web" in wl_types or "app" in wl_types) and "db" not in wl_types


# Function: _is_cloud_unavailable_os
def _is_cloud_unavailable_os(os_lower: str) -> bool:
    return any(pat in os_lower for pat in _CLOUD_UNAVAILABLE_OS)


# Function: _assign_migration_strategy
def _assign_migration_strategy(server: DiscoveredServer) -> str:
    """Classify: lift_and_shift / smart_shift / smart_shift_effort / paas_shift / paas_shift_effort / decommission."""
    os_lower = (server.os_name or "").lower()
    wl_types = {w.component_type for w in server.workloads}

    # Decommission: EOL OS + no active workloads + underutilized
    is_eos_os = _is_os_eol(server)
    is_underutil = server.utilization_band in ("underutilized",)
    no_workloads = len(server.workloads) == 0
    if is_eos_os and is_underutil and no_workloads:
        return "decommission"

    # Managed service → PaaS
    if server.server_type == "Managed" or server.os_family == "managed":
        return "paas_shift"

    # OS not available as standard cloud image → Smart Shift with Service Effort
    if _is_cloud_unavailable_os(os_lower):
        return "smart_shift_effort"

    # End-of-life OS (but still active workloads) → Smart Shift (must upgrade before migrating)
    if is_eos_os:
        return "smart_shift"

    # Stateless web/app tier without DB → PaaS candidate
    if _is_paas_web_candidate(wl_types):
        if len(server.workloads) > 2:
            return "paas_shift_effort"
        return "paas_shift"

    # DB workload → Smart Shift (containerise / managed DB)
    if "db" in wl_types:
        return "smart_shift"

    # Windows → Lift & Shift
    if "windows" in os_lower:
        return "lift_and_shift"

    # Default: Lift & Shift
    return "lift_and_shift"


# Function: _build_cloud_readiness
def _build_cloud_readiness(servers: list[DiscoveredServer]) -> dict:
    strategy_counts: dict[str, int] = defaultdict(int)
    details = []
    smart_effort_details = []

    for s in servers:
        strat = _assign_migration_strategy(s)
        strategy_counts[strat] += 1
        rec = _migration_recommendation_text(s, strat)
        detail = {
            "cloud_name": s.cloud_provider or "OnPrem",
            "server_name": s.server_name,
            "server_ip": s.ip_address,
            "os": s.os_name,
            "source_spec": f"{s.os_name or ''} {s.architecture or '64 bit'}".strip(),
            "cpu_cores": s.cpu_cores,
            "ram_gb": s.ram_gb,
            "migration_strategy": strat,
            "cloud_ready": True,
            "recommendation": rec,
        }
        details.append(detail)
        if strat == "smart_shift_effort":
            smart_effort_details.append(detail)

    # Cloud Ready = no changes needed (lift_and_shift + paas_shift)
    cloud_ready_no_changes = strategy_counts["lift_and_shift"] + strategy_counts["paas_shift"]
    # Cloud Ready with effort = needs OS/arch changes but still migratable
    cloud_ready_with_effort = (
        strategy_counts["smart_shift_effort"] +
        strategy_counts["paas_shift_effort"] +
        strategy_counts["smart_shift"]
    )

    return {
        "cloud_ready": cloud_ready_no_changes,
        "cloud_ready_with_effort": cloud_ready_with_effort,
        "lift_and_shift": strategy_counts["lift_and_shift"],
        "smart_shift": strategy_counts["smart_shift"],
        "smart_shift_with_effort": strategy_counts["smart_shift_effort"],
        "paas_shift": strategy_counts["paas_shift"],
        "paas_shift_with_effort": strategy_counts["paas_shift_effort"],
        "decommission": strategy_counts["decommission"],
        "total": len(servers),
        "details": details,
        "smart_shift_effort_details": smart_effort_details,
    }


# Function: _build_capacity_planning
def _build_capacity_planning(servers: list[DiscoveredServer]) -> dict:
    """Equivalence match vs best match resource summary with hardware/platform cost estimates."""
    total_cpu = sum(s.cpu_cores or 0 for s in servers)
    total_ram = sum(s.ram_gb or 0.0 for s in servers)
    total_disk_tb = sum((s.total_storage_gb or 0) for s in servers) / 1024

    # Best match: right-size using utilization data (~60% of equivalence)
    best_cpu = max(1, math.ceil(total_cpu * 0.6))
    best_ram = round(total_ram * 0.65, 1)
    physical_count = len([s for s in servers if s.server_type == "Physical"])
    virtual_count = len(servers) - physical_count
    n = len(servers)

    best_n = max(1, math.ceil(n * 0.65))

    return {
        "equivalence_match": {
            "total_servers": n,
            "virtual_servers": virtual_count,
            "physical_servers": physical_count,
            "total_cpu_cores": total_cpu,
            "total_ram_gb": round(total_ram, 1),
            "total_disk_tb": round(total_disk_tb, 2),
        },
        "best_match": {
            "total_servers": best_n,
            "total_cpu_cores": best_cpu,
            "total_ram_gb": best_ram,
            "total_disk_tb": round(total_disk_tb * 0.7, 2),
            "estimated_saving_pct": 35,
        },
    }


# Function: _estimate_power_kw_month
def _estimate_power_kw_month(cpu_cores: int, ram_gb: float) -> float:
    """Estimate monthly energy consumption (kWh/month) based on CPU/RAM profile.
    Based on Dell PowerEdge R6615 class hardware power consumption data.
    """
    cores = cpu_cores or 2
    ram   = ram_gb or 8
    if cores >= 8 or ram >= 32:
        return 397.08
    if cores >= 4 or ram >= 16:
        return 127.02
    return 91.27


# Function: _autosize_flavor
def _autosize_flavor(cpu: int, ram: float) -> str:
    cpu_tag = cpu or 2
    ram_tag = int(ram or 8)
    return f"PowerEdge_R6615_{cpu_tag}X{ram_tag}"



# Function: _build_vm_flavors
def _build_vm_flavors(servers: list[DiscoveredServer]) -> dict:
    """Group discovered servers by size profile (kept for backward compat)."""
    flavor_map: dict[str, list[str]] = defaultdict(list)
    for s in servers:
        key = s.instance_type or _autosize_flavor(s.cpu_cores or 2, s.ram_gb or 8)
        flavor_map[key].append(s.server_name)
    flavors = []
    for flavor, names in flavor_map.items():
        flavors.append({"flavor": flavor, "count": len(names), "servers": names[:5]})
    return {"flavors": sorted(flavors, key=lambda x: -x["count"])}


# Function: _build_cloud_resources_recommendation
def _build_cloud_resources_recommendation(servers: list[DiscoveredServer], provider: str = "azure") -> dict:
    """Per-server flavor recommendations with equivalence and best-match sizing,
    using the cloud_pricing catalog for real flavor names and PAYG costs.
    """
    from collections import OrderedDict
    equiv_map: dict[tuple, dict] = OrderedDict()
    best_map:  dict[tuple, dict] = OrderedDict()

    # Function: _entry
    def _entry(s: DiscoveredServer, flavor: pricing.VMFlavor) -> dict:
        return {
            "cloud_name": s.cloud_provider or _provider_label(provider),
            "flavor_name": (
                f"{flavor.name}\n"
                f"RAM: {int(flavor.ram_gb)}.00 GB, CPU\n"
                f"Core:{flavor.cpu_cores}"
            ),
            "flavor_display": flavor.name,
            "flavor_family": flavor.family,
            "os_name": s.os_name or "",
            "ram_gb": int(flavor.ram_gb),
            "cpu_cores": flavor.cpu_cores,
            "cost_per_month": flavor.cost_for("Pay As You Go", s.os_name),
            "equivalence_servers": 0,
            "equivalence_total_cost": 0.0,
            "best_servers": 0,
            "best_total_cost": 0.0,
        }

    per_server = []
    for s in servers:
        wl_types = {w.component_type for w in s.workloads}
        preferred_family = pricing._workload_family(wl_types)
        equiv_fl = pricing.find_equivalence_flavor(
            s.cpu_cores or 2, s.ram_gb or 8, provider, preferred_family
        )
        best_fl = pricing.find_best_match_flavor(
            s.cpu_cores or 2, s.ram_gb or 8, provider,
            s.utilization_band or "unknown", preferred_family
        )
        if equiv_fl is None:
            equiv_fl = pricing.find_equivalence_flavor(2, 4, provider, "General Purpose")
        if best_fl is None:
            best_fl = equiv_fl

        os_key      = (s.os_name or "unknown", equiv_fl.name if equiv_fl else "")
        best_os_key = (s.os_name or "unknown", best_fl.name if best_fl else "")

        if os_key not in equiv_map and equiv_fl:
            equiv_map[os_key] = _entry(s, equiv_fl)
        if os_key in equiv_map:
            equiv_map[os_key]["equivalence_servers"] += 1
            unit_cost = (equiv_fl.cost_for("Pay As You Go", s.os_name) if equiv_fl else 0)
            equiv_map[os_key]["equivalence_total_cost"] = round(
                equiv_map[os_key]["equivalence_total_cost"] + unit_cost, 3
            )

        if best_fl and best_fl.name != (equiv_fl.name if equiv_fl else ""):
            if best_os_key not in best_map:
                best_map[best_os_key] = _entry(s, best_fl)
            best_map[best_os_key]["best_servers"] += 1
            unit_cost = best_fl.cost_for("Pay As You Go", s.os_name)
            best_map[best_os_key]["best_total_cost"] = round(
                best_map[best_os_key]["best_total_cost"] + unit_cost, 3
            )
        elif os_key in equiv_map:
            equiv_map[os_key]["best_servers"] += 1
            unit_cost = (equiv_fl.cost_for("Pay As You Go", s.os_name) if equiv_fl else 0)
            equiv_map[os_key]["best_total_cost"] = round(
                equiv_map[os_key]["best_total_cost"] + unit_cost, 3
            )

        per_server.append({
            "server_name":  s.server_name,
            "server_ip":    s.ip_address,
            "os_name":      s.os_name or "",
            "equiv_flavor": equiv_fl.name if equiv_fl else "",
            "best_flavor":  best_fl.name if best_fl else "",
        })

    merged = {**equiv_map}
    for k, v in best_map.items():
        if k not in merged:
            merged[k] = v
        else:
            merged[k]["best_servers"]     = v["best_servers"]
            merged[k]["best_total_cost"]  = v["best_total_cost"]

    rows = list(merged.values())
    equiv_total = sum(r["equivalence_total_cost"] for r in rows)
    best_total  = sum(r["best_total_cost"] for r in rows)

    return {
        "total_servers": len(servers),
        "equivalence_total_cost_month": round(equiv_total, 2),
        "best_match_total_cost_month":  round(best_total, 2),
        "flavors":    rows,
        "per_server": per_server,
        "notes": (
            "Equivalence Match: exact or closest flavor to current spec. "
            "Best Match: optimal sizing based on server utilisation data."
        ),
    }


# Function: _provider_label
def _provider_label(provider: str) -> str:
    return {
        "azure": "Azure East US",
        "aws": "AWS us-east-1",
        "gcp": "GCP us-central1",
        "onprem": "OnPrem",
    }.get(provider, provider.title())


# ── Pricing Plans ─────────────────────────────────────────────────────────────

# Function: _build_pricing_plans
def _build_pricing_plans(servers: list[DiscoveredServer], provider: str = "azure") -> list[dict]:
    """Build all pricing plan tables — one dict per plan, with equivalence and best-match rows.

    Each row: cloud_name, flavor_name, os_name, flavor_family, cost/month,
              equivalence server count + total, best server count + total.
    Mirrors the multi-plan pricing tables in the PDF reference report.
    """
    plans = pricing.PROVIDER_PLANS.get(provider, [])
    if not plans:
        return []

    result = []
    for plan_name in plans:
        equiv_map: dict[tuple, dict] = {}
        best_map:  dict[tuple, dict] = {}

        for s in servers:
            wl_types = {w.component_type for w in s.workloads}
            preferred_family = pricing._workload_family(wl_types)
            equiv_fl = pricing.find_equivalence_flavor(
                s.cpu_cores or 2, s.ram_gb or 8, provider, preferred_family
            )
            best_fl = pricing.find_best_match_flavor(
                s.cpu_cores or 2, s.ram_gb or 8, provider,
                s.utilization_band or "unknown", preferred_family
            )
            if not equiv_fl:
                continue
            if not best_fl:
                best_fl = equiv_fl

            os_key      = (s.os_name or "unknown", equiv_fl.name)
            best_os_key = (s.os_name or "unknown", best_fl.name)
            unit_equiv = equiv_fl.cost_for(plan_name, s.os_name)
            unit_best  = best_fl.cost_for(plan_name, s.os_name)

            if os_key not in equiv_map:
                equiv_map[os_key] = {
                    "cloud_name": _provider_label(provider),
                    "flavor_name": equiv_fl.name,
                    "flavor_details": (
                        f"RAM: {int(equiv_fl.ram_gb):.2f} GB, CPU Core:{equiv_fl.cpu_cores}"
                    ),
                    "os_name": s.os_name or "",
                    "flavor_family": equiv_fl.family,
                    "ram_gb": int(equiv_fl.ram_gb),
                    "cpu_cores": equiv_fl.cpu_cores,
                    "cost_per_month": round(unit_equiv, 3),
                    "no_of_servers": 0,
                    "total_cost_month": 0.0,
                }
            equiv_map[os_key]["no_of_servers"] += 1
            equiv_map[os_key]["total_cost_month"] = round(
                equiv_map[os_key]["total_cost_month"] + unit_equiv, 3
            )

            # Best match (only add row if flavor differs)
            if best_fl.name != equiv_fl.name:
                if best_os_key not in best_map:
                    best_map[best_os_key] = {
                        "cloud_name": _provider_label(provider),
                        "flavor_name": best_fl.name,
                        "flavor_details": (
                            f"RAM: {int(best_fl.ram_gb):.2f} GB, CPU Core:{best_fl.cpu_cores}"
                        ),
                        "os_name": s.os_name or "",
                        "flavor_family": best_fl.family,
                        "ram_gb": int(best_fl.ram_gb),
                        "cpu_cores": best_fl.cpu_cores,
                        "cost_per_month": round(unit_best, 3),
                        "no_of_servers": 0,
                        "total_cost_month": 0.0,
                    }
                best_map[best_os_key]["no_of_servers"] += 1
                best_map[best_os_key]["total_cost_month"] = round(
                    best_map[best_os_key]["total_cost_month"] + unit_best, 3
                )

        equiv_rows  = list(equiv_map.values())
        best_rows   = list(best_map.values())
        equiv_total = round(sum(r["total_cost_month"] for r in equiv_rows), 2)
        best_total  = round(sum(r["total_cost_month"] for r in best_rows), 2)
        equiv_srv   = sum(r["no_of_servers"] for r in equiv_rows)
        best_srv    = sum(r["no_of_servers"] for r in best_rows)

        result.append({
            "plan_name": plan_name,
            "equivalence_match": {
                "total_servers": equiv_srv,
                "total_cost_month": equiv_total,
                "rows": equiv_rows,
            },
            "best_match": {
                "total_servers": best_srv,
                "total_cost_month": best_total,
                "rows": best_rows,
                "note": (
                    "Equivalence Match has been suggested as the Best Match for servers "
                    "with no utilization data." if not best_rows else ""
                ),
            },
        })

    return result


# ── Dedicated Host Capacity Planning ─────────────────────────────────────────

# Function: _build_dedicated_host_capacity
def _build_dedicated_host_capacity(servers: list[DiscoveredServer], provider: str = "azure") -> dict:
    """Group servers into dedicated host families and compute host-level sizing.

    For Azure: groups servers by flavor family (Memory Optimized → Eav5 host series,
    General Purpose → Bsv2 / Dalsv5 series).
    For AWS / GCP / OnPrem: simplified grouping by workload type.
    """
    if provider == "onprem":
        # On-prem dedicated hosts don't apply in the same way
        return {"supported": False, "note": "Dedicated host planning is cloud-specific."}

    # Map flavor families to Azure dedicated host series
    HOST_SERIES = {
        "Memory Optimized":    {"series": "Eav5 Dedicated Host", "host_cpu_cores": 96,  "host_ram_gb": 672,  "payg_month": 4580.0},
        "General Purpose":     {"series": "Bsv2 Dedicated Host", "host_cpu_cores": 128, "host_ram_gb": 512,  "payg_month": 3200.0},
        "Compute Optimized":   {"series": "Fsv2 Dedicated Host", "host_cpu_cores": 72,  "host_ram_gb": 144,  "payg_month": 2700.0},
        "Storage Optimized":   {"series": "Lsv3 Dedicated Host", "host_cpu_cores": 80,  "host_ram_gb": 640,  "payg_month": 4100.0},
    }
    if provider == "aws":
        HOST_SERIES = {
            "Memory Optimized":  {"series": "r6i Dedicated Host",  "host_cpu_cores": 64, "host_ram_gb": 512, "payg_month": 4100.0},
            "General Purpose":   {"series": "m6i Dedicated Host",  "host_cpu_cores": 64, "host_ram_gb": 256, "payg_month": 2800.0},
            "Compute Optimized": {"series": "c6i Dedicated Host",  "host_cpu_cores": 64, "host_ram_gb": 128, "payg_month": 2200.0},
        }
    elif provider == "gcp":
        HOST_SERIES = {
            "Memory Optimized":  {"series": "n2-highmem Node",  "host_cpu_cores": 80, "host_ram_gb": 640, "payg_month": 3800.0},
            "General Purpose":   {"series": "n2-standard Node", "host_cpu_cores": 80, "host_ram_gb": 320, "payg_month": 2600.0},
            "Compute Optimized": {"series": "c2 Node",          "host_cpu_cores": 60, "host_ram_gb": 240, "payg_month": 2200.0},
        }

    # Assign each server to a flavor family
    family_buckets: dict[str, list[DiscoveredServer]] = defaultdict(list)
    for s in servers:
        wl_types = {w.component_type for w in s.workloads}
        preferred_family = pricing._workload_family(wl_types)
        family_buckets[preferred_family].append(s)

    hosts = []
    host_idx = 1
    for family, fam_servers in sorted(family_buckets.items()):
        host_spec = HOST_SERIES.get(family, HOST_SERIES.get("General Purpose", {}))
        host_cpu  = host_spec.get("host_cpu_cores", 128)
        host_ram  = host_spec.get("host_ram_gb", 512)
        series    = host_spec.get("series", f"{family} Host")
        payg      = host_spec.get("payg_month", 3000.0)

        # Calculate how many servers fit per host based on CPU
        servers_per_host = max(1, host_cpu // max(s.cpu_cores or 2 for s in fam_servers))
        total_hosts_needed = math.ceil(len(fam_servers) / servers_per_host)

        for host_num in range(total_hosts_needed):
            chunk = fam_servers[host_num * servers_per_host:(host_num + 1) * servers_per_host]
            used_cpu = sum(s.cpu_cores or 2 for s in chunk)
            used_ram = sum(s.ram_gb or 8 for s in chunk)
            used_stor = sum(s.total_storage_gb or 50 for s in chunk)
            os_lic_count = sum(
                1 for s in chunk
                if pricing.detect_license_type(s.os_name or "") not in ("None", "")
            )
            db_lic_count = sum(
                1 for s in chunk
                for w in s.workloads
                if w.name.lower() in ("mssql", "oracle")
            )

            server_rows = []
            for s in chunk:
                wl_types = {w.component_type for w in s.workloads}
                preferred_family = pricing._workload_family(wl_types)
                equiv_fl = pricing.find_equivalence_flavor(
                    s.cpu_cores or 2, s.ram_gb or 8, provider, preferred_family
                )
                stor_tier = pricing.find_storage_tier(
                    s.total_storage_gb or 50, provider, wl_types
                )
                os_lic = pricing.detect_license_type(s.os_name or "")
                server_rows.append({
                    "server_ip": s.ip_address,
                    "server_name": s.server_name,
                    "os_name": s.os_name or "",
                    "flavor_name": equiv_fl.name if equiv_fl else "",
                    "flavor_family": equiv_fl.family if equiv_fl else family,
                    "ram_gb": int(equiv_fl.ram_gb if equiv_fl else s.ram_gb or 8),
                    "cpu_cores": equiv_fl.cpu_cores if equiv_fl else (s.cpu_cores or 2),
                    "storage_type": stor_tier.tier_label,
                    "storage_size_gb": stor_tier.size_gb,
                    "storage_cost_month": stor_tier.cost_per_disk_month,
                    "os_license_type": os_lic,
                    "os_license_count": 1 if os_lic not in ("None", "") else 0,
                    "db_license_count": sum(
                        1 for w in s.workloads
                        if w.name.lower() in ("mssql", "oracle")
                    ),
                    "payg_cost_month": (
                        equiv_fl.cost_for("Pay As You Go", s.os_name) if equiv_fl else 0.0
                    ),
                })

            hosts.append({
                "host_name": f"Host {host_idx}",
                "vm_series": series,
                "flavor_family": family,
                "host_cpu_total_cores": host_cpu,
                "host_cpu_used_cores": used_cpu,
                "host_cpu_used_pct": round(used_cpu / host_cpu * 100, 1),
                "host_ram_total_gb": host_ram,
                "host_ram_used_gb": round(used_ram, 1),
                "server_count": len(chunk),
                "total_storage_gb": round(used_stor, 1),
                "payg_cost_month": round(payg, 2),
                "os_license_count": os_lic_count,
                "db_license_count": db_lic_count,
                "storage_cost_month": round(sum(r["storage_cost_month"] for r in server_rows), 2),
                "servers": server_rows,
            })
            host_idx += 1

    return {
        "provider": _provider_label(provider),
        "total_hosts": len(hosts),
        "hosts": hosts,
    }


# ── VMware / OpenStack Capacity Planning ─────────────────────────────────────

# Function: _build_vmware_openstack_capacity
def _build_vmware_openstack_capacity(servers: list[DiscoveredServer], provider: str = "azure") -> dict:
    """Build VMware (AVS) or OpenStack capacity planning section."""
    total_cpu  = sum(s.cpu_cores or 2 for s in servers)
    total_ram  = sum(s.ram_gb or 8 for s in servers)
    total_stor = sum((s.total_storage_gb or 50) for s in servers) / 1024  # TB

    if provider == "azure":
        avs = pricing.recommend_avs_cluster(total_cpu, total_ram, total_stor)
        return {
            "type": "VMware Azure VMware Solution (AVS)",
            **avs,
            "note": (
                "AVS cluster sized with 30% headroom for HA failover and future growth. "
                "Minimum 3 hosts required per AVS cluster."
            ),
        }
    elif provider == "onprem":
        ostack = pricing.recommend_openstack_cluster(total_cpu, total_ram, total_stor)
        return {
            "type": "Red Hat OpenStack / On-Prem Private Cloud",
            **ostack,
        }
    else:
        # AWS VMware Cloud on AWS / GCP bare-metal
        avs_like = pricing.recommend_avs_cluster(total_cpu, total_ram, total_stor, "AV36")
        return {
            "type": f"Bare-Metal / VMware on {provider.upper()}",
            **avs_like,
        }


# Function: _build_workload_consolidation
def _build_workload_consolidation(servers: list[DiscoveredServer]) -> list[dict]:
    """Identify workloads that run on many VMs and could be consolidated."""
    workload_instances: dict[str, list[dict]] = defaultdict(list)
    for s in servers:
        cloud_name = s.cloud_provider or "OnPrem"
        if cloud_name.lower() == "onprem":
            cloud_name = "OnPrem"
        for w in s.workloads:
            workload_instances[w.name].append({
                "cloud_name": cloud_name,
                "server_name": s.server_name,
                "server_ip": s.ip_address,
                "workload_name": w.name,
                "version": w.version or "",
                "location": getattr(w, "location", "") or s.region or s.resource_group or "OnPrem",
            })

    results = []
    for wl_name, instances in workload_instances.items():
        if len(instances) >= 2:  # consolidation candidate
            cloud_name = instances[0]["cloud_name"] if instances else "OnPrem"
            n = len(instances)
            rec_count = max(1, math.ceil(n * 0.4))
            results.append({
                "cloud_name": cloud_name,
                "workload": wl_name,
                "current_vm_count": n,
                "no_of_workload_components": n,
                "recommended_vm_count": rec_count,
                "servers": [i["server_name"] for i in instances],  # backwards compat
                "instances": instances,
                "recommendation": (
                    f"Reduce the number of {wl_name} servers from {n} VMs to "
                    f"{rec_count} VM(s) by sharing it among "
                    "multiple applications to reduce the server cost."
                ),
            })
    return sorted(results, key=lambda x: -x["current_vm_count"])


# Function: _build_paas_recommendations
def _build_paas_recommendations(servers: list[DiscoveredServer], provider: str = "azure") -> list[dict]:
    """Per-server-workload PaaS migration recommendations with cloud service, configuration, and cost.

    Mirrors the PDF PaaS Recommendation table:
    cloud_name | server_ip | server_name | source_config | workload | type | paas_service | paas_config | cost/month
    """
    recs = []
    for s in servers:
        source_config = (
            f"{s.cpu_cores or 0} core, {s.ram_gb or 0:.2f}GB RAM"
        )
        for w in s.workloads:
            wl_lower = (w.name or "").lower()
            # Determine component type if not set
            ctype = w.component_type or ""
            if not ctype:
                if any(k in wl_lower for k in ("mysql", "postgresql", "postgres", "mssql", "oracle", "mongodb")):
                    ctype = "db"
                elif any(k in wl_lower for k in ("tomcat", "nginx", "apache", "iis", "jetty")):
                    ctype = "web"
                elif any(k in wl_lower for k in ("redis", "memcached")):
                    ctype = "cache"
                elif any(k in wl_lower for k in ("kafka", "rabbitmq", "activemq")):
                    ctype = "queue"

            svc = pricing.find_paas_service(w.name, ctype, provider)
            if svc is None:
                continue

            recs.append({
                "cloud_name": _provider_label(provider),
                "server_ip": s.ip_address,
                "server_name": s.server_name,
                "source_config": source_config,
                "workload_name": w.name,
                "workload_version": w.version or "",
                "workload_location": getattr(w, "location", "") or "",
                "workload_type": ctype or "app",
                "paas_service": svc.paas_service,
                "paas_tier": svc.paas_tier,
                "paas_configuration": svc.paas_config,
                "cost_per_month": svc.cost_month,
            })

    # Compute PaaS consolidation summary per workload type
    wl_summary: dict[str, dict] = {}
    for r in recs:
        wl_name = r["workload_name"]
        if wl_name not in wl_summary:
            wl_summary[wl_name] = {
                "workload_name": wl_name,
                "paas_service": r["paas_service"],
                "current_server_count": 0,
                "recommended_paas_count": 1,
                "recommendation": "",
            }
        wl_summary[wl_name]["current_server_count"] += 1

    for wl_name, summary in wl_summary.items():
        n = summary["current_server_count"]
        summary["recommendation"] = (
            f"Reduce the number of {wl_name} PaaS services from {n} PaaS services to 1 "
            "PaaS service by sharing it among multiple applications to reduce the PaaS service cost."
        )

    return {
        "items": recs,
        "consolidation_summary": list(wl_summary.values()),
        "total_paas_services": len(recs),
        "estimated_total_cost_month": round(sum(r["cost_per_month"] for r in recs), 2),
    }


# Function: _os_eos_date
def _os_eos_date(os_name: str) -> date | None:
    os_lower = os_name.lower()
    for key, (eos, _ext) in _OS_EOS.items():
        if key in os_lower:
            return date.fromisoformat(eos)
    return None


# Function: _build_eos_os
def _build_eos_os(servers: list[DiscoveredServer]) -> list[dict]:
    rows = []
    today = date.today()
    for s in servers:
        os_lower = (s.os_name or "").lower()
        for key, (eos, ext) in _OS_EOS.items():
            if key in os_lower:
                eos_date = date.fromisoformat(eos)
                cloud_name = s.cloud_provider or "OnPrem"
                if cloud_name.lower() == "onprem":
                    cloud_name = "OnPrem"
                # Look up a specific recommended migration target OS
                target_os = None
                for mk, mv in _OS_MIGRATION_TARGET.items():
                    if mk in os_lower:
                        target_os = mv
                        break
                if target_os and target_os != s.os_name:
                    advisory = (
                        f"{cloud_name}: Migrate to {target_os} using Smart Migration with Service Effort."
                    )
                elif eos_date < today:
                    advisory = f"{cloud_name}: Migrate from {s.os_name} to a supported OS version immediately."
                else:
                    advisory = f"{cloud_name}: Plan migration before {eos} end-of-support date."
                rows.append({
                    "server_name": s.server_name,
                    "ip_address": s.ip_address,
                    "os_name": s.os_name,
                    "end_of_support": eos,
                    "extended_support": ext,
                    "is_eos": eos_date < today,
                    "days_to_eos": (eos_date - today).days,
                    "migration_advisory": advisory,
                })
                break
    return sorted(rows, key=lambda x: x["end_of_support"])


# Function: _build_eos_workload
def _build_eos_workload(servers: list[DiscoveredServer]) -> list[dict]:
    rows = []
    today = date.today()
    for s in servers:
        for w in s.workloads:
            key = f"{w.name.lower()} {(w.version or '').lower()}".strip()
            eos = None
            for eos_key, eos_date in _WORKLOAD_EOS.items():
                if key == eos_key or (w.name.lower() in eos_key and
                                       (w.version or "").lower() in eos_key):
                    eos = eos_date
                    break
            if eos:
                eos_d = date.fromisoformat(eos)
                rows.append({
                    "server_name": s.server_name,
                    "ip_address": s.ip_address,
                    "workload": w.name,
                    "version": w.version or "",
                    "end_of_support": eos,
                    "is_eos": eos_d < today,
                    "days_to_eos": (eos_d - today).days,
                    "migration_advisory": (
                        f"Upgrade {w.name} {w.version} — EOS reached {eos}."
                        if eos_d < today else
                        f"Plan {w.name} upgrade before {eos}."
                    ),
                })
    return sorted(rows, key=lambda x: x["end_of_support"])


# Function: _build_software_inventory
def _build_software_inventory(servers: list[DiscoveredServer]) -> dict:
    """Aggregate installed software across all servers with validity/EOS analysis."""
    today = date.today()
    all_software: list[dict] = []
    eos_count = 0
    expiring_soon_count = 0   # EOS within 180 days
    commercial_count = 0
    open_source_count = 0
    category_dist: dict[str, int] = defaultdict(int)
    license_dist: dict[str, int] = defaultdict(int)
    name_dist: dict[str, int] = defaultdict(int)    # top packages across all servers
    vendor_dist: dict[str, int] = defaultdict(int)
    # per-server summary: {server_name, server_ip, total, eos_count, expiring_count}
    per_server_map: dict[str, dict] = {}

    for s in servers:
        srv_key = s.ip_address or s.server_name
        if srv_key not in per_server_map:
            per_server_map[srv_key] = {
                "server_name": s.server_name,
                "server_ip":   s.ip_address,
                "total":       0,
                "eos_count":   0,
                "expiring_count": 0,
            }
        for sw in getattr(s, "installed_software", []):
            is_eos = sw.is_eos or False
            days = sw.days_to_eos or 0
            expiring_soon = bool(sw.eos_date and not is_eos and days <= 180)
            if is_eos:
                eos_count += 1
                per_server_map[srv_key]["eos_count"] += 1
            elif expiring_soon:
                expiring_soon_count += 1
                per_server_map[srv_key]["expiring_count"] += 1
            per_server_map[srv_key]["total"] += 1
            category_dist[sw.category or "other"] += 1
            lic = sw.license_type or "unknown"
            license_dist[lic] += 1
            if lic == "commercial":
                commercial_count += 1
            elif lic == "open_source":
                open_source_count += 1
            name_dist[sw.name] += 1
            vnd = (sw.vendor or "").strip() or "Unknown"
            vendor_dist[vnd] += 1

            # Human-readable support period label
            if sw.eos_date:
                abs_days = abs(days)
                if is_eos:
                    support_label = f"Expired {abs_days}d ago ({sw.eos_date})"
                elif days <= 180:
                    support_label = f"Expiring in {days}d ({sw.eos_date})"
                elif days <= 365:
                    support_label = f"Active – expires {sw.eos_date} (~{days}d)"
                else:
                    yrs = round(days / 365, 1)
                    support_label = f"Active – expires {sw.eos_date} (~{yrs}y)"
            else:
                support_label = "No EOS data"

            all_software.append({
                "server_name":      s.server_name,
                "server_ip":        s.ip_address,
                "name":             sw.name,
                "version":          sw.version,
                "vendor":           sw.vendor,
                "install_date":     sw.install_date,
                "category":         sw.category,
                "license_type":     sw.license_type,
                "eos_date":         sw.eos_date,
                "is_eos":           is_eos,
                "days_to_eos":      days,
                "days_remaining":   days,
                "arch":             getattr(sw, "arch", ""),
                "install_location": getattr(sw, "install_location", ""),
                "source":           getattr(sw, "source", ""),
                "support_period_label": support_label,
                "validity_status":  (
                    "expired" if is_eos else
                    "expiring_soon" if expiring_soon else
                    "current"
                ),
            })

    # Sort EOS items first, then expiring soon
    all_software.sort(key=lambda x: (
        0 if x["is_eos"] else (1 if x["validity_status"] == "expiring_soon" else 2),
        x["eos_date"] or "9999-99-99",
    ))

    # Top 20 installed packages by frequency
    top_packages = sorted(name_dist.items(), key=lambda x: -x[1])[:20]
    # Top 10 vendors
    top_vendors = sorted(vendor_dist.items(), key=lambda x: -x[1])[:10]

    return {
        "total_packages": len(all_software),
        "unique_packages": len(name_dist),
        "eos_count": eos_count,
        "expiring_soon_count": expiring_soon_count,
        "commercial_count": commercial_count,
        "open_source_count": open_source_count,
        "category_distribution": dict(category_dist),
        "license_distribution": dict(license_dist),
        "vendor_distribution": dict(top_vendors),
        "top_packages": [{"name": n, "server_count": c} for n, c in top_packages],
        "per_server_summary": sorted(per_server_map.values(), key=lambda x: -x["total"]),
        "items": all_software,
    }


# Function: _build_storage_recommendation
def _build_storage_recommendation(servers: list[DiscoveredServer], provider: str = "onprem") -> dict:
    """Build per-tier storage recommendation with IOPS, throughput, disk count, and cost.
    Matches the PDF Storage Recommendation table format:
    cloud_name | type | spec (size, IOPS, MB/s) | disk_count | total_storage | proposed_storage | cost/month
    """
    # Aggregate per storage tier
    tier_buckets: dict[tuple, dict] = {}   # key: (tier_label, size_gb)

    for s in servers:
        wl_types = {w.component_type for w in s.workloads}
        for d in s.disks:
            disk_gb = d.size_gb or 50
            tier = pricing.find_storage_tier(disk_gb, provider, wl_types)
            key = (tier.tier_label, tier.size_gb)
            if key not in tier_buckets:
                tier_buckets[key] = {
                    "cloud_name": _provider_label(provider),
                    "type_of_storage": tier.tier_label,
                    "specification": (
                        f"{tier.size_gb} GB, {tier.iops} IOPS, {tier.throughput_mbps} MB/s"
                    ),
                    "iops": tier.iops,
                    "throughput_mbps": tier.throughput_mbps,
                    "cost_per_disk_month": tier.cost_per_disk_month,
                    "no_of_disks": 0,
                    "total_storage_gb": 0.0,
                    "proposed_storage_gb": 0,   # round up to tier size × count
                    "total_cost_month": 0.0,
                }
            tier_buckets[key]["no_of_disks"] += 1
            tier_buckets[key]["total_storage_gb"] += disk_gb
            tier_buckets[key]["proposed_storage_gb"] = (
                tier_buckets[key]["no_of_disks"] * tier.size_gb
            )
            tier_buckets[key]["total_cost_month"] = round(
                tier_buckets[key]["no_of_disks"] * tier.cost_per_disk_month, 3
            )

        # If no disks list but we have total_storage_gb, create a single generic entry
        if not s.disks and (s.total_storage_gb or 0) > 0:
            wl_types = {w.component_type for w in s.workloads}
            tier = pricing.find_storage_tier(s.total_storage_gb, provider, wl_types)
            key = (tier.tier_label, tier.size_gb)
            if key not in tier_buckets:
                tier_buckets[key] = {
                    "cloud_name": _provider_label(provider),
                    "type_of_storage": tier.tier_label,
                    "specification": (
                        f"{tier.size_gb} GB, {tier.iops} IOPS, {tier.throughput_mbps} MB/s"
                    ),
                    "iops": tier.iops,
                    "throughput_mbps": tier.throughput_mbps,
                    "cost_per_disk_month": tier.cost_per_disk_month,
                    "no_of_disks": 0,
                    "total_storage_gb": 0.0,
                    "proposed_storage_gb": 0,
                    "total_cost_month": 0.0,
                }
            tier_buckets[key]["no_of_disks"] += 1
            tier_buckets[key]["total_storage_gb"] += s.total_storage_gb
            tier_buckets[key]["proposed_storage_gb"] = (
                tier_buckets[key]["no_of_disks"] * tier.size_gb
            )
            tier_buckets[key]["total_cost_month"] = round(
                tier_buckets[key]["no_of_disks"] * tier.cost_per_disk_month, 3
            )

    tiers = list(tier_buckets.values())
    # Format storage values
    for t in tiers:
        t["total_storage_gb"] = round(t["total_storage_gb"], 2)
        t["total_storage_tb"] = round(t["total_storage_gb"] / 1024, 3)
        t["proposed_storage_tb"] = round(t["proposed_storage_gb"] / 1024, 3)

    total_tb = round(sum(t["total_storage_gb"] for t in tiers) / 1024, 2)
    total_cost = round(sum(t["total_cost_month"] for t in tiers), 2)

    return {
        "cloud_name": _provider_label(provider),
        "total_storage_tb": total_tb,
        "total_cost_month": total_cost,
        "tiers": tiers,
        "notes": (
            "Storage recommendations are aligned with cloud provider guidelines for workload types "
            "(DB servers get Premium SSD, web/app servers get Standard SSD/HDD). "
            "IOPS and throughput specifications are the minimum guaranteed by the selected tier."
        ),
    }


# Function: _build_kubernetes_recommendation
def _build_kubernetes_recommendation(servers: list[DiscoveredServer], provider: str = "azure") -> dict:
    """Identify containerization candidates and build per-pod Kubernetes recommendation.

    Produces:
    - Per pod row: cluster_name, node_name, node_flavor_details, pod_name,
                   target_workload + server IP/name, cost_per_month, cost_1yr, cost_3yr
    - Summary: total pods, cluster list, node flavors, aggregate costs
    """
    import random
    import string

    # Function: _random_pod_suffix
    def _random_pod_suffix(length: int = 5) -> str:
        return "".join(random.choices(string.ascii_lowercase, k=length))

    # Group containerizable workloads by workload-name + OS family
    # Cluster assignment: DB workloads on Linux → separate cluster from Windows app servers
    cluster_groups: dict[str, list[dict]] = defaultdict(list)

    for s in servers:
        for w in s.workloads:
            if w.component_type not in ("web", "app", "middleware", "db", "cache"):
                continue
            # Cluster grouping logic:
            # DB workloads → LinuxCluster or separate DB cluster
            # Windows app workloads → WindowsCluster
            # Linux app workloads → LinuxCluster
            os_lower = (s.os_name or "").lower()
            if w.component_type == "db":
                cluster_key = "LinuxDB"
            elif "windows" in os_lower:
                cluster_key = "Windows"
            else:
                cluster_key = "Linux"
            cluster_groups[cluster_key].append({
                "server": s,
                "workload": w,
            })

    pods = []
    cluster_names: dict[str, str] = {}
    cluster_counter = 1
    node_counter: dict[str, int] = {}

    for cluster_key, items in cluster_groups.items():
        cluster_label = f"AKS Cluster{cluster_counter}" if provider == "azure" else \
                        f"EKS Cluster{cluster_counter}" if provider == "aws" else \
                        f"GKE Cluster{cluster_counter}"
        cluster_names[cluster_key] = cluster_label
        cluster_counter += 1

        # Determine node OS / flavor
        os_tag = "Windows" if cluster_key == "Windows" else "Linux"
        node_key = f"{os_tag}Node"
        node_idx = node_counter.get(node_key, 1)

        for item in items:
            s  = item["server"]
            w  = item["workload"]
            cpu_req = max(0.5, (s.cpu_cores or 2) * 0.25)
            mem_mi  = max(512, int((s.ram_gb or 4) * 256))

            # Node flavor sized to fit these pods
            node_fl = pricing.find_equivalence_flavor(
                max(2, int(cpu_req * 4)),   # scale pod CPU req to node
                max(8, int(mem_mi / 256)),   # convert Mi → GB headroom
                provider, "General Purpose"
            )
            if not node_fl:
                node_fl = pricing.FLAVOR_CATALOG.get(provider, pricing.AZURE_FLAVORS)[0]

            pod_suffix = _random_pod_suffix()
            pod_name = f"pod_{pod_suffix}"
            cost_month = node_fl.cost_for("Pay As You Go", s.os_name)
            cost_1yr   = round(cost_month * 12 * 0.75, 0)  # ~25% reserved discount
            cost_3yr   = round(cost_month * 36 * 0.60, 0)  # ~40% 3yr discount

            pods.append({
                "cloud_name": _provider_label(provider),
                "cluster_name": cluster_label,
                "node_name": f"{os_tag}Node_{node_idx}",
                "node_flavor_details": (
                    f"Flavor Details:\nName :{node_fl.name}\n"
                    f"RAM :{node_fl.ram_gb:.2f} GB\n"
                    f"Architecture :64 bit\n"
                    f"CPU Core :{node_fl.cpu_cores}"
                ),
                "node_flavor_name": node_fl.name,
                "node_ram_gb": node_fl.ram_gb,
                "node_cpu_cores": node_fl.cpu_cores,
                "pod_name": pod_name,
                "target_workload": f"{w.name} {w.version or ''}".strip(),
                "target_server_ip": s.ip_address,
                "target_server_name": s.server_name,
                "cost_per_month": round(cost_month, 2),
                "cost_1yr": int(cost_1yr),
                "cost_3yr": int(cost_3yr),
            })

    cluster_summaries = []
    for ckey, cname in cluster_names.items():
        cpods = [p for p in pods if p["cluster_name"] == cname]
        cluster_summaries.append({
            "cluster_name": cname,
            "node_count": len({p["node_name"] for p in cpods}),
            "pod_count": len(cpods),
            "total_cost_month": round(sum(p["cost_per_month"] for p in cpods), 2),
            "total_cost_1yr": sum(p["cost_1yr"] for p in cpods),
            "total_cost_3yr": sum(p["cost_3yr"] for p in cpods),
        })

    return {
        "containerization_candidates": len(pods),
        "clusters": cluster_summaries,
        "pods": pods,
        "total_cost_month": round(sum(p["cost_per_month"] for p in pods), 2),
        "total_cost_1yr": sum(p["cost_1yr"] for p in pods),
        "total_cost_3yr": sum(p["cost_3yr"] for p in pods),
        "notes": (
            "Kubernetes recommendations are based on containerizable workloads identified during scan. "
            "Pod CPU/memory requests are sized at 25% of source server specs. "
            "Migration of legacy workloads may require OS/runtime version upgrades."
        ),
    }


# Function: _build_sustainability
def _build_sustainability(servers: list[DiscoveredServer]) -> dict:
    """Per-server power consumption and CO₂ emission breakdown at varied utilisation bands,
    matching the Cloud Server Sustainability – Power & CO2 section of the feasibility report.

    Power column (kWh/month) represents the baseline energy at idle/25% load.
    CO2 figures are calculated at 25 / 50 / 75 / 100% utilisation.
    Conversion factor: 0.000379 metric tonnes CO₂ per kWh (global average grid).
    """
    CO2_FACTOR = 0.000379   # MT CO₂ per kWh

    per_server = []
    total_power = 0.0
    total_co2_25 = 0.0

    for s in servers:
        power = _estimate_power_kw_month(s.cpu_cores or 2, s.ram_gb or 8)
        flavor = _autosize_flavor(s.cpu_cores or 2, s.ram_gb or 8)
        co2_25  = round(power * CO2_FACTOR,     2)
        co2_50  = round(power * CO2_FACTOR * 2, 2)
        co2_75  = round(power * CO2_FACTOR * 3, 2)
        co2_100 = round(power * CO2_FACTOR * 4, 2)
        total_power  += power
        total_co2_25 += co2_25

        # Try to get cloud flavor name if provider is known
        cloud_provider = (s.cloud_provider or "onprem").lower()
        cloud_fl = pricing.find_equivalence_flavor(
            s.cpu_cores or 2, s.ram_gb or 8, cloud_provider,
            pricing._workload_family({w.component_type for w in s.workloads})
        )
        flavor_details = (
            f"Name: {cloud_fl.name}( RAM: {int(cloud_fl.ram_gb)} GB, CPU Core: {cloud_fl.cpu_cores} )\n"
            f"Family: {cloud_fl.family}"
        ) if cloud_fl else (
            f"Name: {flavor} (RAM: {int(s.ram_gb or 8)} GB, CPU Core: {s.cpu_cores or 2})"
        )

        per_server.append({
            "server_ip":           s.ip_address,
            "server_name":         s.server_name,
            "configuration_match": "Equivalence Match",
            "flavor_details":      flavor_details,
            "power_kw_month":      round(power, 2),
            "co2_mt_25pct":        co2_25,
            "co2_mt_50pct":        co2_50,
            "co2_mt_75pct":        co2_75,
            "co2_mt_100pct":       co2_100,
            "utilization_band":    s.utilization_band or "underutilized",
        })

    total_co2_mt = round(total_co2_25, 2)   # headline figure at 25% usage band
    # Cloud-equivalent estimate: cloud infra is typically ~60% more efficient
    cloud_power = round(total_power * 0.4, 2)
    cloud_co2   = round(cloud_power * CO2_FACTOR, 2)

    # Usage band distribution for bar charts
    band_counts: dict[str, int] = {"underutilized": 0, "moderate": 0, "utilized": 0, "unknown": 0}
    for ps in per_server:
        band = ps.get("utilization_band", "unknown")
        band_counts[band] = band_counts.get(band, 0) + 1

    return {
        "server_count":                len(per_server),
        "total_power_kw_month":        round(total_power, 2),
        "total_co2_mt_month":          total_co2_mt,
        "cloud_equivalent_power_kw_month": cloud_power,
        "cloud_equivalent_co2_mt_month":   cloud_co2,
        "annual_power_saving_kwh":     round((total_power - cloud_power) * 12, 0),
        "annual_co2_saving_mt":        round((total_co2_mt - cloud_co2) * 12, 3),
        "usage_band_distribution":     band_counts,
        "per_server":                  per_server,
        "notes": (
            "Power figures represent baseline kWh/month per server. "
            "CO\u2082 figures are calculated at 25/50/75/100% utilisation using 0.379 kg CO\u2082/kWh. "
            "Highlighted CO\u2082 emissions are derived from source utilisation data when available."
        ),
    }

# Function: _build_network_utilization
def _build_network_utilization(servers: list[DiscoveredServer]) -> list[dict]:
    """Estimate per-server network data utilisation (MB/month) for the network summary.
    Values are estimated from server role and workload type when live monitoring data
    is not available from the scan.
    """
    rows = []
    for s in servers:
        wl_types = {w.component_type for w in s.workloads}
        # Rough MB/month estimates based on server role
        if "db" in wl_types:
            inbound  = 50_000
            outbound = 80_000
        elif "web" in wl_types or "app" in wl_types:
            inbound  = 200_000
            outbound = 300_000
        elif "cache" in wl_types or "queue" in wl_types:
            inbound  = 100_000
            outbound = 100_000
        else:
            inbound  = 30_000
            outbound = 50_000
        rows.append({
            "server_name": s.server_name,
            "server_ip":   s.ip_address,
            "inbound_mb_month":  inbound,
            "outbound_mb_month": outbound,
            "note": "Estimated — upload extended utilisation data for precise figures.",
        })
    return rows


# Function: _build_network_utilization
def _build_network_utilization(servers: list[DiscoveredServer]) -> list[dict]:
    """Estimate per-server network data utilisation (MB/month) for the network summary.
    Values are estimated from server role and workload type when live monitoring data
    is not available from the scan.
    """
    rows = []
    for s in servers:
        wl_types = {w.component_type for w in s.workloads}
        if "db" in wl_types:
            inbound, outbound = 50_000, 80_000
        elif "web" in wl_types or "app" in wl_types:
            inbound, outbound = 200_000, 300_000
        elif "cache" in wl_types or "queue" in wl_types:
            inbound, outbound = 100_000, 100_000
        else:
            inbound, outbound = 30_000, 50_000
        rows.append({
            "server_name":       s.server_name,
            "server_ip":         s.ip_address,
            "inbound_mb_month":  inbound,
            "outbound_mb_month": outbound,
            "note": "Estimated \u2014 upload extended utilisation data for precise figures.",
        })
    return rows


# Function: _cidr_to_network
def _cidr_to_network(cidr: str) -> str:
    """Convert interface address like '192.168.1.5/24' to network '192.168.1.0/24'."""
    try:
        import ipaddress
        return str(ipaddress.ip_network(cidr, strict=False))
    except Exception:
        return cidr


# Function: _build_network_topology
def _build_network_topology(servers: list[DiscoveredServer]) -> dict:
    """Aggregate L2/L3 topology: subnets, interface inventory, ARP table, routing."""
    subnet_map: dict[str, dict] = {}
    all_ifaces: list[dict] = []
    all_arp: list[dict] = []
    all_routes: list[dict] = []
    seen_arp_macs: set = set()

    for s in servers:
        for iface in s.interfaces:
            raw_subnet = iface.subnet or ""
            net_key = _cidr_to_network(raw_subnet) if "/" in raw_subnet else (raw_subnet or "unknown")
            if net_key not in subnet_map:
                subnet_map[net_key] = {
                    "subnet": net_key,
                    "gateway": getattr(iface, "gateway", "") or "",
                    "host_count": 0,
                    "hosts": [],
                }
            entry = subnet_map[net_key]
            entry["host_count"] += 1
            entry["hosts"].append({
                "server_name": s.server_name,
                "ip": iface.ip_address,
                "mac": iface.mac_address or "",
            })
            gw = getattr(iface, "gateway", "") or ""
            if gw and not entry["gateway"]:
                entry["gateway"] = gw

            all_ifaces.append({
                "server": s.server_name,
                "interface": iface.interface_name,
                "ip": iface.ip_address,
                "mac": iface.mac_address or "",
                "subnet": iface.subnet or "",
                "gateway": getattr(iface, "gateway", "") or "",
                "vlan": getattr(iface, "vlan_id", "") or "",
                "type": iface.ip_type or "private",
                "bandwidth_mbps": iface.bandwidth_mbps or 0,
                "duplex": getattr(iface, "duplex", "") or "",
                "link_state": getattr(iface, "link_state", "") or "",
                "mtu": getattr(iface, "mtu", 0) or 0,
            })

        for nb in getattr(s, "arp_neighbors", []):
            mac = nb.get("mac", "")
            if mac and mac not in seen_arp_macs and mac != "00:00:00:00:00:00":
                seen_arp_macs.add(mac)
                all_arp.append({
                    "ip": nb.get("ip", ""),
                    "mac": mac,
                    "seen_from": s.server_name,
                    "interface": nb.get("interface", ""),
                    "type": nb.get("type", ""),
                })

        for r in getattr(s, "routes", []):
            all_routes.append({
                "server": s.server_name,
                "destination": r.get("destination", ""),
                "gateway": r.get("gateway", ""),
                "interface": r.get("interface", ""),
                "metric": r.get("metric", ""),
            })

    return {
        "subnets": list(subnet_map.values()),
        "total_subnets": len(subnet_map),
        "interfaces": all_ifaces,
        "arp_table": all_arp[:200],
        "routes": all_routes[:200],
        "network_utilization": _build_network_utilization(servers),
    }

# ── Serialise DiscoveredServer to plain dict ─────────────────────────────────

# Function: _server_to_dict
def _server_to_dict(s: DiscoveredServer) -> dict:
    return {
        # ── Identity ──────────────────────────────────────────────────────
        "server_id":        s.server_id,
        "server_name":      s.server_name,
        "ip_address":       s.ip_address,   # kept for frontend compat
        "server_ip":        s.ip_address,
        "hostname":         s.hostname,
        "cloud_provider":   s.cloud_provider,
        "region":           s.region,
        "resource_group":   s.resource_group,
        "environment":      getattr(s, "environment", ""),
        "business_owner":   getattr(s, "business_owner", ""),
        "platform_host":    getattr(s, "platform_host", ""),
        # ── Compute ───────────────────────────────────────────────────────
        "architecture":              s.architecture,  # kept for frontend compat
        "architecture_type":         s.architecture,
        "server_type":               s.server_type,
        "cpu_cores":                 s.cpu_cores,
        "ram_gb":                    s.ram_gb,        # kept for frontend compat
        "memory_gb":                 s.ram_gb,
        "boot_type":                 s.boot_type,
        "instance_type":             s.instance_type,
        "compute_hardware_arch":     getattr(s, "compute_hardware_arch", ""),
        "virtualization_state":      getattr(s, "virtualization_state", ""),
        "virtualization_attributes": getattr(s, "virtualization_attributes", {}),
        "install_type":              getattr(s, "install_type", ""),
        # ── OS ────────────────────────────────────────────────────────────
        "os_name":              s.os_name,           # kept for frontend compat
        "operating_system":     s.os_name,
        "os_family":            s.os_family,
        "os_version":           s.os_version,
        "os_end_of_support":    s.os_end_of_support,
        "os_extended_support":  s.os_extended_support,
        # ── Storage ───────────────────────────────────────────────────────
        "total_storage_gb":       s.total_storage_gb,
        "internal_storage_gb":   getattr(s, "internal_storage_gb", s.total_storage_gb),
        "external_storage_gb":   getattr(s, "external_storage_gb", 0.0),
        "storage_type":          getattr(s, "storage_type", ""),
        "db_storage_gb":         getattr(s, "db_storage_gb", 0.0),
        "flash_storage_used":    getattr(s, "flash_storage_used", False),
        "disks": [                                   # kept for frontend compat
            {"mount_point": d.mount_point, "size_gb": d.size_gb,
             "used_gb": d.used_gb, "disk_type": d.disk_type, "iops": d.iops}
            for d in s.disks
        ],
        "storage_decomposition": [
            {"mount_point": d.mount_point, "size_gb": d.size_gb,
             "used_gb": d.used_gb, "disk_type": d.disk_type, "iops": d.iops}
            for d in s.disks
        ],
        # ── DB engine ─────────────────────────────────────────────────────
        "db_engine": getattr(s, "db_engine", ""),
        # ── Network ───────────────────────────────────────────────────────
        "interfaces": [
            {"interface_name": i.interface_name, "ip_address": i.ip_address,
             "ip_type": i.ip_type, "mac_address": i.mac_address,
             "subnet": i.subnet, "bandwidth_mbps": i.bandwidth_mbps,
             "gateway": getattr(i, "gateway", ""), "vlan_id": getattr(i, "vlan_id", ""),
             "duplex": getattr(i, "duplex", "") or "",
             "link_state": getattr(i, "link_state", "") or "",
             "mtu": getattr(i, "mtu", 0) or 0,
             "interface_flags": getattr(i, "interface_flags", "") or ""}
            for i in s.interfaces
        ],
        "arp_neighbors": [
            {"ip": nb.get("ip", ""), "mac": nb.get("mac", ""),
             "interface": nb.get("interface", ""), "type": nb.get("type", "")}
            for nb in getattr(s, "arp_neighbors", [])
        ],
        "lldp_neighbors": getattr(s, "lldp_neighbors", []),
        "routes": [
            {"destination": r.get("destination", ""), "gateway": r.get("gateway", ""),
             "interface": r.get("interface", ""), "metric": r.get("metric", "")}
            for r in getattr(s, "routes", [])
        ],
        # ── Utilization ───────────────────────────────────────────────────
        "cpu_util_pct":    s.cpu_util_pct,
        "ram_util_pct":    s.ram_util_pct,
        "disk_util_pct":   s.disk_util_pct,
        "utilization_band": s.utilization_band,
        # ── Workloads ─────────────────────────────────────────────────────
        "workloads": [
            {"name": w.name, "version": w.version, "component_type": w.component_type,
             "port": w.port, "status": w.status, "location": getattr(w, "location", "")}
            for w in s.workloads
        ],
        # ── Installed software inventory ──────────────────────────────────
        "installed_software": [
            {
                "name":              sw.name,
                "version":           sw.version,
                "vendor":            sw.vendor,
                "install_date":      sw.install_date,
                "category":          sw.category,
                "license_type":      sw.license_type,
                "eos_date":          sw.eos_date,
                "is_eos":            sw.is_eos,
                "days_to_eos":       sw.days_to_eos,
                "arch":              getattr(sw, "arch", ""),
                "install_location":  getattr(sw, "install_location", ""),
                "source":            getattr(sw, "source", ""),
                "validity_status": (
                    "expired" if sw.is_eos else
                    "expiring_soon" if (sw.eos_date and sw.days_to_eos <= 180) else
                    "current"
                ),
            }
            for sw in getattr(s, "installed_software", [])
        ],
        # ── Migration ─────────────────────────────────────────────────────
        "migration_strategy": s.migration_strategy,
        "cloud_ready":        s.cloud_ready,
        # ── Rationalization assessment ────────────────────────────────────
        "application_stability":           getattr(s, "application_stability", ""),
        "cpu_requirement":                 getattr(s, "cpu_requirement", ""),
        "memory_requirement":              getattr(s, "memory_requirement", ""),
        "mainframe_dependency":            getattr(s, "mainframe_dependency", "No"),
        "desktop_dependency":              getattr(s, "desktop_dependency", "No"),
        "app_os_cloud_suitability":        getattr(s, "app_os_cloud_suitability", ""),
        "db_cloud_readiness":              getattr(s, "db_cloud_readiness", ""),
        "middleware_cloud_readiness":      getattr(s, "middleware_cloud_readiness", ""),
        "app_hardware_dependency":         getattr(s, "app_hardware_dependency", ""),
        "app_cots_vs_non_cots":            getattr(s, "app_cots_vs_non_cots", ""),
        "cloud_suitability":               getattr(s, "cloud_suitability", ""),
        "volume_external_dependencies":    getattr(s, "volume_external_dependencies", ""),
        "app_load_predictability":         getattr(s, "app_load_predictability", ""),
        "financially_optimizable":         getattr(s, "financially_optimizable", ""),
        "distributed_architecture":        getattr(s, "distributed_architecture", ""),
        "latency_requirements":            getattr(s, "latency_requirements", ""),
        "ubiquitous_access":               getattr(s, "ubiquitous_access", ""),
        "no_production_environments":      getattr(s, "no_production_environments", 1),
        "no_non_production_environments":  getattr(s, "no_non_production_environments", 0),
        "ha_dr_requirements":              getattr(s, "ha_dr_requirements", ""),
        "rto_requirements":                getattr(s, "rto_requirements", ""),
        "rpo_requirements":                getattr(s, "rpo_requirements", ""),
        "deployment_geography":            getattr(s, "deployment_geography", ""),
        # ── L2/L3 topology ────────────────────────────────────────────────
        "arp_neighbors": getattr(s, "arp_neighbors", []),
        "routes":        getattr(s, "routes", []),
    }
