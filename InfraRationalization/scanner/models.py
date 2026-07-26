# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: scanner/models.py
# Date: 2025-12-30
# ---------------------------------------------------------------------------
"""
scanner/models.py
Shared dataclasses that every provider populates.
The ScanJob is what goes into the report_builder and then gets persisted.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ─── Per-server model ──────────────────────────────────────────────────────────

@dataclass
class DiskInfo:
    mount_point: str = ""
    size_gb: float = 0.0
    used_gb: float = 0.0
    disk_type: str = "unknown"        # SSD / HDD / NVMe / network
    iops: int = 0


@dataclass
class NetworkInterface:
    interface_name: str = ""
    ip_address: str = ""
    ip_type: str = "private"          # private / public / elastic / ISP
    mac_address: str = ""
    subnet: str = ""
    bandwidth_mbps: int = 0
    gateway: str = ""                 # default gateway via this interface
    vlan_id: str = ""                 # 802.1Q VLAN tag (if detected)
    duplex: str = ""                  # full / half / unknown
    link_state: str = ""              # up / down / unknown
    mtu: int = 0                      # MTU bytes (e.g. 1500)
    interface_flags: str = ""         # BROADCAST,MULTICAST,UP,RUNNING …


@dataclass
class WorkloadComponent:
    name: str = ""                    # e.g. MySQL, ApacheTomcat, nginx, PostgreSQL
    version: str = ""
    component_type: str = ""          # db / web / app / cache / queue / ldap / mail
    port: int = 0
    status: str = "running"
    location: str = ""                # filesystem path or install dir (e.g. /usr/sbin, C:\App)


@dataclass
class InstalledSoftware:
    """Represents a software package/application installed on a server."""
    name: str = ""
    version: str = ""
    vendor: str = ""
    install_date: str = ""            # ISO date or empty
    category: str = "other"           # os / runtime / middleware / db / security / utility / other
    license_type: str = "unknown"     # commercial / open_source / unknown
    eos_date: str = ""                # ISO end-of-support date or empty
    is_eos: bool = False              # True if today > eos_date
    days_to_eos: int = 0              # negative = already expired
    arch: str = ""                    # x64_or_native / x86 / amd64 / arm64 / noarch / etc.
    install_location: str = ""        # filesystem install path (if available)
    source: str = ""                  # dpkg / rpm / flatpak / registry_uninstall / winget / choco / inferred


@dataclass
class DiscoveredServer:
    # Identity
    server_id: str = ""
    server_name: str = ""
    ip_address: str = ""
    hostname: str = ""
    cloud_provider: str = ""          # onprem / aws / azure / gcp
    region: str = ""
    resource_group: str = ""          # Azure RG / AWS VPC / GCP project

    # Compute
    cpu_cores: int = 0
    ram_gb: float = 0.0
    architecture: str = "64 bit"
    server_type: str = "Virtual"      # Physical / Virtual
    boot_type: str = "BIOS"           # BIOS / UEFI
    instance_type: str = ""           # e.g. t3.medium, Standard_D2s_v3

    # OS
    os_name: str = ""                 # e.g. Ubuntu 24.04 LTS
    os_family: str = ""               # linux / windows
    os_version: str = ""
    os_end_of_support: str = ""       # ISO date or empty
    os_extended_support: str = ""
    os_migration_advisory: str = ""

    # Storage
    disks: list[DiskInfo] = field(default_factory=list)
    total_storage_gb: float = 0.0

    # Network
    interfaces: list[NetworkInterface] = field(default_factory=list)

    # Utilization (0..100 percentages; -1 = unknown)
    cpu_util_pct: float = -1.0
    ram_util_pct: float = -1.0
    disk_util_pct: float = -1.0
    utilization_band: str = "unknown"   # underutilized / moderate / utilized

    # Workloads running on this server
    workloads: list[WorkloadComponent] = field(default_factory=list)

    # Full installed software inventory (populated by deep scan)
    installed_software: list[InstalledSoftware] = field(default_factory=list)

    # Cloud migration fields (populated by report_builder)
    migration_strategy: str = ""        # lift_and_shift / smart_shift / paas_shift
    cloud_ready: bool = True

    # ── Environment / ownership ────────────────────────────────────────────
    environment: str = ""               # Production / Development / Test / Staging / DR
    business_owner: str = ""            # team or person responsible
    platform_host: str = ""             # data-centre name / cloud account / colo

    # ── Extra compute metadata ─────────────────────────────────────────────
    compute_hardware_arch: str = ""     # x86_64 / ARM64 / SPARC / POWER
    virtualization_state: str = ""      # Virtualized / Physical / Container / Bare-Metal
    virtualization_attributes: dict[str, Any] = field(default_factory=dict)
                                        # {hypervisor, version, cluster, datacenter}
    install_type: str = ""              # OEM / Custom / Cloud-Native / Container / Manual

    # ── Extended storage ──────────────────────────────────────────────────
    external_storage_gb: float = 0.0
    storage_type: str = ""              # SSD / HDD / Mixed / NVMe / SAN / NAS
    db_storage_gb: float = 0.0
    flash_storage_used: bool = False

    # ── DB engine ─────────────────────────────────────────────────────────
    db_engine: str = ""                 # e.g. "MySQL 8.0, PostgreSQL 14"

    # ── Rationalization assessment (may be filled post-scan or by LLM) ────
    application_stability: str = ""            # Stable / Unstable / End-of-Life
    cpu_requirement: str = ""                  # Standard / High-Performance / GPU
    memory_requirement: str = ""               # Standard / High-Memory
    mainframe_dependency: str = "No"           # Yes / No / Partial
    desktop_dependency: str = "No"             # Yes / No
    app_os_cloud_suitability: str = ""         # Ready / Needs Remediation / Not Suitable
    db_cloud_readiness: str = ""               # Ready / Needs Migration / Incompatible
    middleware_cloud_readiness: str = ""       # Ready / Needs Refactor / Incompatible
    app_hardware_dependency: str = ""          # None / GPU / FPGA / HSM / Dongle
    app_cots_vs_non_cots: str = ""             # COTS / Non-COTS / Mixed
    cloud_suitability: str = ""                # High / Medium / Low / Not Suitable
    volume_external_dependencies: str = ""     # Low / Medium / High
    app_load_predictability: str = ""          # Predictable / Unpredictable / Elastic
    financially_optimizable: str = ""          # Yes / No / Partial
    distributed_architecture: str = ""         # Yes / No / Partial
    latency_requirements: str = ""             # Low / Standard / Strict (<10ms) / Ultra (<1ms)
    ubiquitous_access: str = ""                # Yes / No
    no_production_environments: int = 1
    no_non_production_environments: int = 0
    ha_dr_requirements: str = ""               # Active-Active / Active-Passive / Cold-Standby / None
    rto_requirements: str = ""                 # e.g. <1h / <4h / <24h / Best-Effort
    rpo_requirements: str = ""                 # e.g. <15min / <1h / <24h
    deployment_geography: str = ""             # Single-Region / Multi-Region / Global

    # ── Licensing ─────────────────────────────────────────────────────────
    license_type: str = ""             # None / Windows-Std / Windows-DC / RHEL / SUSE / BYOL
    os_license_count: int = 0          # Number of OS licenses required (1 per Windows/RHEL VM)
    db_license_count: int = 0          # Number of commercial DB licenses (MSSQL / Oracle)

    # ── Network utilisation ───────────────────────────────────────────────
    network_data_in_mb_month: float = 0.0   # Inbound MB/month (collected from scan or estimated)
    network_data_out_mb_month: float = 0.0  # Outbound MB/month

    # ── Power & sustainability (filled by report_builder) ─────────────────
    power_consumption_kw_month: float = 0.0  # Baseline power kWh/month

    # Raw provider metadata
    raw_metadata: dict[str, Any] = field(default_factory=dict)

    # L2/L3 topology (populated by deep scan)
    arp_neighbors: list = field(default_factory=list)  # [{ip, mac, interface}]
    routes: list = field(default_factory=list)          # [{destination, gateway, interface}]
    lldp_neighbors: list = field(default_factory=list)  # [{chassis_id, port_id, system_name, ip}]


# ─── Scan job (aggregation of all discovered servers) ─────────────────────────

@dataclass
class ScanTarget:
    provider: str = "onprem"            # onprem / aws / azure / gcp
    # OnPrem
    network_range: str = ""             # e.g. 192.168.1.0/24
    ssh_username: str = ""
    ssh_password: str = ""
    ssh_key_path: str = ""
    winrm_username: str = ""
    winrm_password: str = ""
    # AWS
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_regions: list[str] = field(default_factory=list)
    # Azure
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    azure_client_secret: str = ""
    azure_subscription_id: str = ""
    azure_regions: list[str] = field(default_factory=list)
    # GCP
    gcp_project_id: str = ""
    gcp_service_account_json: str = ""  # JSON key string
    gcp_regions: list[str] = field(default_factory=list)
    # Scan options
    deep_scan: bool = True              # attempt SSH/WMI/SDK for full details
    port_scan: bool = True              # nmap port scan
    timeout_seconds: int = 120


@dataclass
class ScanJob:
    scan_id: str = ""
    report_name: str = ""
    target: ScanTarget = field(default_factory=ScanTarget)
    status: str = "pending"             # pending / running / completed / failed
    progress: int = 0                   # 0..100
    progress_message: str = ""
    error: str = ""
    servers: list[DiscoveredServer] = field(default_factory=list)
    created_at: str = ""
    completed_at: str = ""
