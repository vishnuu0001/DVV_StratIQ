# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: db/models.py
# Date: 2026-05-01
# ---------------------------------------------------------------------------
"""
db/models.py
SQLAlchemy ORM models for InfraRationalization.

Tables
------
infra_scans   — one row per scan run (header / metadata)
infra_servers — one row per discovered server (many per scan)
"""
from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


# ─── Scan header ──────────────────────────────────────────────────────────────

class InfraScan(Base):
    __tablename__ = "infra_scans"

    scan_id         = Column(String(64),  primary_key=True)
    report_name     = Column(String(255), nullable=False, default="")
    provider        = Column(String(32),  nullable=False, default="onprem")
    status          = Column(String(32),  nullable=False, default="pending")
    created_at      = Column(DateTime,    server_default=func.now(), nullable=False)
    completed_at    = Column(DateTime,    nullable=True)
    total_servers   = Column(Integer,     nullable=False, default=0)
    error_message   = Column(Text,        nullable=True)

    # Aggregated report sections (stored as JSON text)
    report_json     = Column(Text, nullable=True)

    servers = relationship(
        "InfraServer",
        back_populates="scan",
        cascade="all, delete-orphan",
    )

    # Function: to_dict
    def to_dict(self) -> dict:
        return {
            "scan_id":       self.scan_id,
            "report_name":   self.report_name,
            "provider":      self.provider,
            "status":        self.status,
            "created_at":    self.created_at.isoformat() if self.created_at else None,
            "completed_at":  self.completed_at.isoformat() if self.completed_at else None,
            "total_servers": self.total_servers,
            "error_message": self.error_message,
        }


# ─── Per-server detail ────────────────────────────────────────────────────────

class InfraServer(Base):
    """
    Every DiscoveredServer from a scan is stored as one row.
    Includes all the Corent MaaS™ rationalization fields requested.
    """
    __tablename__ = "infra_servers"

    id      = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String(64), ForeignKey("infra_scans.scan_id", ondelete="CASCADE"),
                     nullable=False, index=True)

    # ── Identity ──────────────────────────────────────────────────────────
    server_ip          = Column(String(64),  nullable=False, default="")
    server_name        = Column(String(255), nullable=False, default="")
    hostname           = Column(String(255), nullable=True)
    cloud_provider     = Column(String(32),  nullable=True)   # onprem / aws / azure / gcp
    region             = Column(String(64),  nullable=True)
    resource_group     = Column(String(128), nullable=True)
    environment        = Column(String(64),  nullable=True)   # Production / Development / Test / Staging / DR
    business_owner     = Column(String(128), nullable=True)   # business contact / team
    platform_host      = Column(String(128), nullable=True)   # data-centre / colocation / cloud account

    # ── Compute / Hardware ────────────────────────────────────────────────
    architecture_type           = Column(String(32),  nullable=True)   # 64 bit / 32 bit
    server_type                 = Column(String(32),  nullable=True)   # Physical / Virtual
    cpu_cores                   = Column(Integer,     nullable=True)
    memory_gb                   = Column(Float,       nullable=True)
    boot_type                   = Column(String(16),  nullable=True)   # BIOS / UEFI
    instance_type               = Column(String(64),  nullable=True)   # e.g. t3.medium
    compute_hardware_arch       = Column(String(64),  nullable=True)   # x86_64 / ARM64 / SPARC
    virtualization_state        = Column(String(64),  nullable=True)   # Virtualized / Physical / Container
    virtualization_attributes   = Column(Text,        nullable=True)   # JSON: {hypervisor, version, cluster}
    install_type                = Column(String(64),  nullable=True)   # OEM / Custom / Cloud-Native / Container

    # ── OS ────────────────────────────────────────────────────────────────
    operating_system            = Column(String(128), nullable=True)
    os_family                   = Column(String(32),  nullable=True)   # linux / windows
    os_version                  = Column(String(32),  nullable=True)
    os_end_of_support           = Column(String(32),  nullable=True)   # ISO date
    os_extended_support         = Column(String(32),  nullable=True)

    # ── Storage ───────────────────────────────────────────────────────────
    internal_storage_gb         = Column(Float,   nullable=True)
    external_storage_gb         = Column(Float,   nullable=True)
    storage_type                = Column(String(32),  nullable=True)   # SSD / HDD / Mixed / NVMe
    db_storage_gb               = Column(Float,   nullable=True)
    flash_storage_used          = Column(Boolean, nullable=True)
    storage_decomposition       = Column(Text,    nullable=True)       # JSON array of disk records

    # ── DB Engine ─────────────────────────────────────────────────────────
    db_engine                   = Column(String(128), nullable=True)   # MySQL 8.0, PostgreSQL 14, …

    # ── Utilization (runtime metrics) ─────────────────────────────────────
    cpu_util_pct                = Column(Float,   nullable=True)
    ram_util_pct                = Column(Float,   nullable=True)
    disk_util_pct               = Column(Float,   nullable=True)
    utilization_band            = Column(String(32),  nullable=True)   # underutilized / moderate / utilized

    # ── Migration ─────────────────────────────────────────────────────────
    migration_strategy          = Column(String(64),  nullable=True)
    cloud_ready                 = Column(Boolean, nullable=True)

    # ── Cloud / Rationalization Assessment ───────────────────────────────
    application_stability              = Column(String(64),  nullable=True)   # Stable / Unstable / End-of-Life
    cpu_requirement                    = Column(String(64),  nullable=True)   # Standard / High-Performance / GPU
    memory_requirement                 = Column(String(64),  nullable=True)   # Standard / High-Memory / etc
    mainframe_dependency               = Column(String(16),  nullable=True)   # Yes / No / Partial
    desktop_dependency                 = Column(String(16),  nullable=True)   # Yes / No
    app_os_cloud_suitability           = Column(String(64),  nullable=True)   # Ready / Needs Remediation / Not Suitable
    db_cloud_readiness                 = Column(String(64),  nullable=True)
    middleware_cloud_readiness         = Column(String(64),  nullable=True)
    app_hardware_dependency            = Column(String(128), nullable=True)
    app_cots_vs_non_cots               = Column(String(32),  nullable=True)   # COTS / Non-COTS / Mixed
    cloud_suitability                  = Column(String(64),  nullable=True)   # High / Medium / Low / Not Suitable
    volume_external_dependencies       = Column(String(32),  nullable=True)   # Low / Medium / High
    app_load_predictability            = Column(String(32),  nullable=True)   # Predictable / Unpredictable / Elastic
    financially_optimizable            = Column(String(32),  nullable=True)   # Yes / No / Partial
    distributed_architecture           = Column(String(32),  nullable=True)   # Yes / No / Partial
    latency_requirements               = Column(String(64),  nullable=True)   # Low / Standard / Strict (<10ms / <1ms)
    ubiquitous_access                  = Column(String(32),  nullable=True)   # Yes / No
    no_production_environments         = Column(Integer,     nullable=True)
    no_non_production_environments     = Column(Integer,     nullable=True)
    ha_dr_requirements                 = Column(String(64),  nullable=True)   # Active-Active / Active-Passive / None
    rto_requirements                   = Column(String(32),  nullable=True)   # e.g. <1h / <4h / <24h
    rpo_requirements                   = Column(String(32),  nullable=True)   # e.g. <15min / <1h
    deployment_geography               = Column(String(128), nullable=True)   # Single-Region / Multi-Region / Global

    # ── Raw JSON blobs ────────────────────────────────────────────────────
    workloads_json                      = Column(Text, nullable=True)   # JSON list of WorkloadComponent dicts
    interfaces_json                     = Column(Text, nullable=True)   # JSON list of NetworkInterface dicts
    raw_metadata_json                   = Column(Text, nullable=True)   # provider raw metadata

    scan = relationship("InfraScan", back_populates="servers")

    # Function: to_dict
    def to_dict(self) -> dict:
        import json as _json

        # Function: _j
        def _j(v):
            if v is None:
                return None
            try:
                return _json.loads(v)
            except Exception:
                return v

        return {
            "id":                              self.id,
            "scan_id":                         self.scan_id,
            # Identity
            "server_ip":                       self.server_ip,
            "server_name":                     self.server_name,
            "hostname":                        self.hostname,
            "cloud_provider":                  self.cloud_provider,
            "region":                          self.region,
            "resource_group":                  self.resource_group,
            "environment":                     self.environment,
            "business_owner":                  self.business_owner,
            "platform_host":                   self.platform_host,
            # Compute
            "architecture_type":               self.architecture_type,
            "server_type":                     self.server_type,
            "cpu_cores":                       self.cpu_cores,
            "memory_gb":                       self.memory_gb,
            "boot_type":                       self.boot_type,
            "instance_type":                   self.instance_type,
            "compute_hardware_arch":           self.compute_hardware_arch,
            "virtualization_state":            self.virtualization_state,
            "virtualization_attributes":       _j(self.virtualization_attributes),
            "install_type":                    self.install_type,
            # OS
            "operating_system":                self.operating_system,
            "os_family":                       self.os_family,
            "os_version":                      self.os_version,
            "os_end_of_support":               self.os_end_of_support,
            "os_extended_support":             self.os_extended_support,
            # Storage
            "internal_storage_gb":             self.internal_storage_gb,
            "external_storage_gb":             self.external_storage_gb,
            "storage_type":                    self.storage_type,
            "db_storage_gb":                   self.db_storage_gb,
            "flash_storage_used":              self.flash_storage_used,
            "storage_decomposition":           _j(self.storage_decomposition),
            # DB
            "db_engine":                       self.db_engine,
            # Utilization
            "cpu_util_pct":                    self.cpu_util_pct,
            "ram_util_pct":                    self.ram_util_pct,
            "disk_util_pct":                   self.disk_util_pct,
            "utilization_band":                self.utilization_band,
            # Migration
            "migration_strategy":              self.migration_strategy,
            "cloud_ready":                     self.cloud_ready,
            # Rationalization
            "application_stability":           self.application_stability,
            "cpu_requirement":                 self.cpu_requirement,
            "memory_requirement":              self.memory_requirement,
            "mainframe_dependency":            self.mainframe_dependency,
            "desktop_dependency":              self.desktop_dependency,
            "app_os_cloud_suitability":        self.app_os_cloud_suitability,
            "db_cloud_readiness":              self.db_cloud_readiness,
            "middleware_cloud_readiness":      self.middleware_cloud_readiness,
            "app_hardware_dependency":         self.app_hardware_dependency,
            "app_cots_vs_non_cots":            self.app_cots_vs_non_cots,
            "cloud_suitability":               self.cloud_suitability,
            "volume_external_dependencies":    self.volume_external_dependencies,
            "app_load_predictability":         self.app_load_predictability,
            "financially_optimizable":         self.financially_optimizable,
            "distributed_architecture":        self.distributed_architecture,
            "latency_requirements":            self.latency_requirements,
            "ubiquitous_access":               self.ubiquitous_access,
            "no_production_environments":      self.no_production_environments,
            "no_non_production_environments":  self.no_non_production_environments,
            "ha_dr_requirements":              self.ha_dr_requirements,
            "rto_requirements":                self.rto_requirements,
            "rpo_requirements":                self.rpo_requirements,
            "deployment_geography":            self.deployment_geography,
            # Raw blobs
            "workloads":                       _j(self.workloads_json),
            "interfaces":                      _j(self.interfaces_json),
            "raw_metadata":                    _j(self.raw_metadata_json),
        }
