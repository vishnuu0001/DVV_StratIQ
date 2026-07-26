# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: scanner/orchestrator.py
# Date: 2025-09-15
# ---------------------------------------------------------------------------
"""
scanner/orchestrator.py
Central scan dispatcher. Manages ScanJob lifecycle, launches provider-specific
scanners in background threads, and aggregates results into a report.

Usage:
    from scanner.orchestrator import Orchestrator
    orch = Orchestrator(reports_dir="reports/")
    scan_id = orch.start_scan(target, report_name="My Scan")
    status  = orch.get_status(scan_id)
    report  = orch.get_report(scan_id)
"""
from __future__ import annotations

import json
import logging
import os
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Generator

from .models import ScanJob, ScanTarget
from .report_builder import build_report

log = logging.getLogger(__name__)


# Function: _persist_to_db
def _persist_to_db(scan_id: str, report_name: str, provider: str,
                   status: str, servers: list, report: dict,
                   error: str, created_at: str, completed_at: str) -> None:
    """Persist a completed/failed scan to SQLite via SQLAlchemy. Silently skips on error."""
    try:
        import json as _json
        from datetime import datetime as _dt
        import sys, os
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from db.database import SessionLocal, init_db
        from db.models import InfraScan, InfraServer

        init_db()
        db = SessionLocal()
        try:
            # Upsert the scan header
            existing = db.get(InfraScan, scan_id)
            if existing:
                existing.status       = status
                existing.total_servers= len(servers)
                existing.report_json  = _json.dumps(report, default=str)
                existing.error_message= error or None
                if completed_at:
                    try:
                        existing.completed_at = _dt.fromisoformat(completed_at)
                    except Exception:
                        pass
            else:
                scan_row = InfraScan(
                    scan_id      = scan_id,
                    report_name  = report_name,
                    provider     = provider,
                    status       = status,
                    total_servers= len(servers),
                    report_json  = _json.dumps(report, default=str),
                    error_message= error or None,
                )
                if created_at:
                    try:
                        scan_row.created_at = _dt.fromisoformat(created_at)
                    except Exception:
                        pass
                if completed_at:
                    try:
                        scan_row.completed_at = _dt.fromisoformat(completed_at)
                    except Exception:
                        pass
                db.add(scan_row)
                db.flush()

            # Delete old server rows for this scan then re-insert
            db.query(InfraServer).filter(InfraServer.scan_id == scan_id).delete()

            for s in servers:
                row = InfraServer(
                    scan_id                        = scan_id,
                    server_ip                      = s.ip_address or "",
                    server_name                    = s.server_name or s.hostname or s.ip_address or "",
                    hostname                       = s.hostname,
                    cloud_provider                 = s.cloud_provider,
                    region                         = s.region,
                    resource_group                 = getattr(s, "resource_group", None),
                    environment                    = getattr(s, "environment", None),
                    business_owner                 = getattr(s, "business_owner", None),
                    platform_host                  = getattr(s, "platform_host", None),
                    architecture_type              = s.architecture,
                    server_type                    = s.server_type,
                    cpu_cores                      = s.cpu_cores,
                    memory_gb                      = s.ram_gb,
                    boot_type                      = s.boot_type,
                    instance_type                  = s.instance_type,
                    compute_hardware_arch          = getattr(s, "compute_hardware_arch", None),
                    virtualization_state           = getattr(s, "virtualization_state", None),
                    virtualization_attributes      = _json.dumps(getattr(s, "virtualization_attributes", {}), default=str),
                    install_type                   = getattr(s, "install_type", None),
                    operating_system               = s.os_name,
                    os_family                      = s.os_family,
                    os_version                     = s.os_version,
                    os_end_of_support              = s.os_end_of_support,
                    os_extended_support            = s.os_extended_support,
                    internal_storage_gb            = getattr(s, "internal_storage_gb", s.total_storage_gb),
                    external_storage_gb            = getattr(s, "external_storage_gb", 0.0),
                    storage_type                   = getattr(s, "storage_type", None),
                    db_storage_gb                  = getattr(s, "db_storage_gb", 0.0),
                    flash_storage_used             = getattr(s, "flash_storage_used", False),
                    storage_decomposition          = _json.dumps(
                        [{"mount_point": d.mount_point, "size_gb": d.size_gb,
                          "used_gb": d.used_gb, "disk_type": d.disk_type} for d in s.disks],
                        default=str,
                    ),
                    db_engine                      = getattr(s, "db_engine", None),
                    cpu_util_pct                   = s.cpu_util_pct if s.cpu_util_pct >= 0 else None,
                    ram_util_pct                   = s.ram_util_pct if s.ram_util_pct >= 0 else None,
                    disk_util_pct                  = s.disk_util_pct if s.disk_util_pct >= 0 else None,
                    utilization_band               = s.utilization_band,
                    migration_strategy             = s.migration_strategy,
                    cloud_ready                    = s.cloud_ready,
                    application_stability          = getattr(s, "application_stability", None),
                    cpu_requirement                = getattr(s, "cpu_requirement", None),
                    memory_requirement             = getattr(s, "memory_requirement", None),
                    mainframe_dependency           = getattr(s, "mainframe_dependency", "No"),
                    desktop_dependency             = getattr(s, "desktop_dependency", "No"),
                    app_os_cloud_suitability       = getattr(s, "app_os_cloud_suitability", None),
                    db_cloud_readiness             = getattr(s, "db_cloud_readiness", None),
                    middleware_cloud_readiness     = getattr(s, "middleware_cloud_readiness", None),
                    app_hardware_dependency        = getattr(s, "app_hardware_dependency", None),
                    app_cots_vs_non_cots           = getattr(s, "app_cots_vs_non_cots", None),
                    cloud_suitability              = getattr(s, "cloud_suitability", None),
                    volume_external_dependencies   = getattr(s, "volume_external_dependencies", None),
                    app_load_predictability        = getattr(s, "app_load_predictability", None),
                    financially_optimizable        = getattr(s, "financially_optimizable", None),
                    distributed_architecture       = getattr(s, "distributed_architecture", None),
                    latency_requirements           = getattr(s, "latency_requirements", None),
                    ubiquitous_access              = getattr(s, "ubiquitous_access", None),
                    no_production_environments     = getattr(s, "no_production_environments", 1),
                    no_non_production_environments = getattr(s, "no_non_production_environments", 0),
                    ha_dr_requirements             = getattr(s, "ha_dr_requirements", None),
                    rto_requirements               = getattr(s, "rto_requirements", None),
                    rpo_requirements               = getattr(s, "rpo_requirements", None),
                    deployment_geography           = getattr(s, "deployment_geography", None),
                    workloads_json                 = _json.dumps(
                        [{"name": w.name, "version": w.version,
                          "component_type": w.component_type, "port": w.port}
                         for w in s.workloads], default=str),
                    interfaces_json                = _json.dumps(
                        [{"interface_name": i.interface_name, "ip_address": i.ip_address,
                          "ip_type": i.ip_type, "mac_address": i.mac_address}
                         for i in s.interfaces], default=str),
                    raw_metadata_json              = _json.dumps(s.raw_metadata, default=str),
                )
                db.add(row)

            db.commit()
            log.info("Scan %s persisted to DB (%d servers)", scan_id, len(servers))
        finally:
            db.close()
    except Exception as exc:
        log.warning("DB persist failed for scan %s: %s", scan_id, exc)


class Orchestrator:
    # Function: __init__
    def __init__(self, reports_dir: str = "reports") -> None:
        self._reports_dir = Path(reports_dir)
        self._reports_dir.mkdir(parents=True, exist_ok=True)
        self._jobs: dict[str, ScanJob] = {}
        self._lock = threading.Lock()

        # SSE subscribers: scan_id → list of queue-like callables
        self._subscribers: dict[str, list[Callable[[str], None]]] = {}

    # ── Public API ────────────────────────────────────────────────────────

    # Function: start_scan
    def start_scan(self, target: ScanTarget, report_name: str) -> str:
        scan_id = str(uuid.uuid4())
        job = ScanJob(
            scan_id=scan_id,
            report_name=report_name,
            target=target,
            status="pending",
        )
        with self._lock:
            self._jobs[scan_id] = job

        thread = threading.Thread(
            target=self._run_scan,
            args=(scan_id,),
            daemon=True,
            name=f"scan-{scan_id[:8]}",
        )
        thread.start()
        return scan_id

    # Function: get_status
    def get_status(self, scan_id: str) -> dict[str, Any] | None:
        job = self._jobs.get(scan_id)
        if not job:
            return None
        return {
            "scan_id": job.scan_id,
            "report_name": job.report_name,
            "status": job.status,
            "progress": job.progress,
            "progress_message": job.progress_message,
            "error": job.error,
            "server_count": len(job.servers),
            "created_at": job.created_at,
            "completed_at": job.completed_at,
        }

    # Function: list_jobs
    def list_jobs(self) -> list[dict[str, Any]]:
        return [self.get_status(jid) for jid in self._jobs]  # type: ignore[misc]

    # Function: remove_job
    def remove_job(self, scan_id: str) -> bool:
        """Remove a completed/failed job from the in-memory store. Returns True if found."""
        with self._lock:
            if scan_id in self._jobs:
                del self._jobs[scan_id]
                self._subscribers.pop(scan_id, None)
                return True
        return False

    # Function: get_report
    def get_report(self, scan_id: str) -> dict | None:
        report_path = self._reports_dir / f"{scan_id}.json"
        if report_path.exists():
            with open(report_path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        return None

    # Function: subscribe_progress
    def subscribe_progress(self, scan_id: str, callback: Callable[[str], None]) -> None:
        """Register a callback that will be called with SSE event strings."""
        with self._lock:
            self._subscribers.setdefault(scan_id, []).append(callback)

    # Function: unsubscribe_progress
    def unsubscribe_progress(self, scan_id: str, callback: Callable[[str], None]) -> None:
        with self._lock:
            subs = self._subscribers.get(scan_id, [])
            if callback in subs:
                subs.remove(callback)

    # ── Internal ─────────────────────────────────────────────────────────

    # Function: _update_job
    def _update_job(self, scan_id: str, **kwargs: Any) -> None:
        with self._lock:
            job = self._jobs.get(scan_id)
            if job:
                for k, v in kwargs.items():
                    setattr(job, k, v)

    # Function: _emit
    def _emit(self, scan_id: str, pct: int, msg: str, status: str | None = None) -> None:
        self._update_job(scan_id, progress=pct, progress_message=msg)
        payload: dict = {"progress": pct, "message": msg}
        if status:
            payload["status"] = status
        event = json.dumps(payload)
        with self._lock:
            subs = list(self._subscribers.get(scan_id, []))
        for cb in subs:
            try:
                cb(event)
            except Exception:
                pass

    # Function: _run_scan
    def _run_scan(self, scan_id: str) -> None:
        self._update_job(scan_id, status="running", progress=0, progress_message="Starting scan…")
        with self._lock:
            job = self._jobs[scan_id]
        target = job.target

        servers = []
        try:
            provider = target.provider.lower()

            # Function: cb
            def cb(pct: int, msg: str) -> None:
                self._emit(scan_id, pct, msg)

            if provider == "onprem":
                from .onprem import scan_onprem
                servers = scan_onprem(target, progress_cb=cb)

            elif provider == "aws":
                from .aws_scanner import scan_aws
                servers = scan_aws(target, progress_cb=cb)

            elif provider == "azure":
                from .azure_scanner import scan_azure
                servers = scan_azure(target, progress_cb=cb)

            elif provider == "gcp":
                from .gcp_scanner import scan_gcp
                servers = scan_gcp(target, progress_cb=cb)

            elif provider == "multi":
                # Scan all configured providers
                if target.network_range:
                    from .onprem import scan_onprem
                    self._emit(scan_id, 5, "Scanning on-premises network…")
                    servers += scan_onprem(target, progress_cb=lambda p, m: cb(5 + p // 4, m))

                if target.aws_access_key_id:
                    from .aws_scanner import scan_aws
                    self._emit(scan_id, 30, "Scanning AWS…")
                    servers += scan_aws(target, progress_cb=lambda p, m: cb(30 + p // 4, m))

                if target.azure_subscription_id:
                    from .azure_scanner import scan_azure
                    self._emit(scan_id, 55, "Scanning Azure…")
                    servers += scan_azure(target, progress_cb=lambda p, m: cb(55 + p // 4, m))

                if target.gcp_project_id:
                    from .gcp_scanner import scan_gcp
                    self._emit(scan_id, 80, "Scanning GCP…")
                    servers += scan_gcp(target, progress_cb=lambda p, m: cb(80 + p // 5, m))

                self._emit(scan_id, 96, f"All providers scanned — {len(servers)} servers found")

            else:
                raise ValueError(f"Unknown provider: {provider!r}")

            # Build report
            self._emit(scan_id, 98, "Building report…")
            with self._lock:
                job_ref = self._jobs[scan_id]
            report = build_report(
                servers=servers,
                target=target,
                report_name=job.report_name,
                scan_job=job_ref,
            )

            # Persist report to disk
            report_path = self._reports_dir / f"{scan_id}.json"
            with open(report_path, "w", encoding="utf-8") as fh:
                json.dump(report, fh, indent=2, default=str)

            with self._lock:
                j = self._jobs[scan_id]
                j.servers = servers
                j.status = "completed"
                j.progress = 100
                j.progress_message = f"Scan complete — {len(servers)} servers discovered"
                j.completed_at = datetime.utcnow().isoformat()

            # Persist to database
            _persist_to_db(
                scan_id      = scan_id,
                report_name  = job.report_name,
                provider     = target.provider,
                status       = "completed",
                servers      = servers,
                report       = report,
                error        = "",
                created_at   = job.created_at,
                completed_at = self._jobs[scan_id].completed_at,
            )

            self._emit(scan_id, 100,
                       f"Scan complete — {len(servers)} servers discovered",
                       status="completed")

        except Exception as exc:
            log.exception("Scan %s failed", scan_id)
            self._update_job(
                scan_id,
                status="failed",
                error=str(exc),
                progress_message=f"Scan failed: {exc}",
                completed_at=datetime.utcnow().isoformat(),
            )
            self._emit(scan_id, 0, f"ERROR: {exc}", status="failed")
        finally:
            # Clean up subscribers
            with self._lock:
                self._subscribers.pop(scan_id, None)
