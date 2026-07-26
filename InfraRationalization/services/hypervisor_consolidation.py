# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: services/hypervisor_consolidation.py
# Date: 2025-09-27
# ---------------------------------------------------------------------------
"""
services/hypervisor_consolidation.py
Hypervisor & Virtualization Consolidation Analysis.

Features:
  - VMware vSphere/ESXi discovery via vCenter API
  - VM-to-host ratio analysis
  - Consolidation calculator: estimate physical hosts that can be eliminated
  - VM sprawl detection: powered-off VMs > 90 days
"""
from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date, datetime
from typing import Any

log = logging.getLogger(__name__)

# Physical host sizing assumptions (for consolidation calculator)
_TARGET_HOST_CPU_CORES  = 32   # typical modern dual-socket host
_TARGET_HOST_RAM_GB     = 256  # typical modern host RAM
_VM_CPU_OVERCOMMIT      = 4    # 4:1 vCPU:pCPU overcommit ratio
_VM_RAM_OVERCOMMIT      = 1.2  # 20% memory overcommit
_MIN_VM_PER_HOST        = 4    # minimum viable density
_MAX_VM_PER_HOST        = 40   # practical max for manageability


# Function: _server_id
def _server_id(srv: dict) -> str:
    return (srv.get("server_ip") or srv.get("ip_address") or srv.get("ip") or
            srv.get("server_name") or srv.get("name") or "unknown")


# Function: _server_name
def _server_name(srv: dict) -> str:
    return srv.get("server_name") or srv.get("name") or _server_id(srv)


# Function: _is_virtual
def _is_virtual(srv: dict) -> bool:
    return (srv.get("server_type") or srv.get("virtualization_state") or "").lower() in (
        "virtual", "virtualized", "vm", "container"
    )


# Function: _is_physical
def _is_physical(srv: dict) -> bool:
    return (srv.get("server_type") or "").lower() == "physical"


# Function: _get_hypervisor
def _get_hypervisor(srv: dict) -> str:
    """Extract hypervisor type from virtualization attributes."""
    va = srv.get("virtualization_attributes") or {}
    if isinstance(va, dict):
        return va.get("hypervisor") or ""
    return ""


# Function: _is_stopped_vm
def _is_stopped_vm(srv: dict) -> bool:
    """Check if VM is stopped/powered-off."""
    raw = srv.get("raw_metadata") or {}
    state = (
        raw.get("aws_state") or
        raw.get("power_state") or
        raw.get("vm_power_state") or
        ""
    ).lower()
    return state in ("stopped", "deallocated", "powered off", "suspended", "off")


# Function: _days_since_created
def _days_since_created(srv: dict) -> int | None:
    """Estimate days since VM was created (rough heuristic from metadata)."""
    raw = srv.get("raw_metadata") or {}
    created_str = raw.get("created_at") or raw.get("creation_time") or ""
    if not created_str:
        return None
    try:
        created = datetime.fromisoformat(str(created_str)[:19])
        return (datetime.utcnow() - created).days
    except Exception:
        return None


# Function: _cluster_group
def _cluster_group(srv: dict) -> str:
    """Get cluster/datacenter name for grouping."""
    va = srv.get("virtualization_attributes") or {}
    if isinstance(va, dict):
        return va.get("cluster") or va.get("datacenter") or va.get("host") or "default_cluster"
    return "default_cluster"


# Function: _consolidation_calculator
def _consolidation_calculator(vms: list[dict]) -> dict:
    """
    Given a list of VMs, calculate how many physical hosts are needed
    at target density vs current state.
    """
    total_vcpu = sum(max(1, s.get("cpu_cores") or 1) for s in vms)
    total_vram = sum(max(0.5, s.get("ram_gb") or s.get("memory_gb") or 0.5) for s in vms)

    # Current: assume each VM is on its own host (worst case sprawl)
    current_hosts = len(vms)

    # Target: pack onto consolidated hosts
    hosts_by_cpu = -(-total_vcpu // (_TARGET_HOST_CPU_CORES * _VM_CPU_OVERCOMMIT))
    hosts_by_ram = -(-total_vram // (_TARGET_HOST_RAM_GB * _VM_RAM_OVERCOMMIT))
    hosts_needed = max(2, max(hosts_by_cpu, hosts_by_ram))  # min 2 for HA
    hosts_to_eliminate = max(0, current_hosts - hosts_needed)

    # Cost estimate: $5000/mo per physical host (hardware lease + power + management)
    cost_savings_per_month = hosts_to_eliminate * 5000
    vms_per_host = round(len(vms) / hosts_needed, 1) if hosts_needed > 0 else 0

    return {
        "vm_count":              len(vms),
        "total_vcpu":            total_vcpu,
        "total_vram_gb":         round(total_vram, 1),
        "current_estimated_hosts": current_hosts,
        "recommended_hosts":     hosts_needed,
        "hosts_to_eliminate":    hosts_to_eliminate,
        "vms_per_host_target":   vms_per_host,
        "estimated_monthly_savings_usd": cost_savings_per_month,
        "estimated_annual_savings_usd":  cost_savings_per_month * 12,
    }


# Function: scan_vsphere
def scan_vsphere(vcenter_host: str, username: str, password: str,
                 verify_ssl: bool = False) -> list[dict]:
    """
    Connect to vCenter via pyVmomi and enumerate VMs/hosts/clusters.
    Returns list of server dicts compatible with DiscoveredServer schema.
    """
    try:
        from pyVim.connect import SmartConnectNoSSL, SmartConnect, Disconnect
        from pyVmomi import vim  # type: ignore
        import atexit
    except ImportError:
        log.warning("pyVmomi not installed — vSphere scan unavailable. Run: pip install pyvmomi")
        return []

    servers: list[dict] = []
    try:
        if verify_ssl:
            si = SmartConnect(host=vcenter_host, user=username, pwd=password)
        else:
            si = SmartConnectNoSSL(host=vcenter_host, user=username, pwd=password)
        atexit.register(Disconnect, si)

        content    = si.RetrieveContent()
        container  = content.rootFolder
        view_type  = [vim.VirtualMachine]
        recursive  = True
        container_view = content.viewManager.CreateContainerView(container, view_type, recursive)
        vms = container_view.view

        for vm in vms:
            summary  = vm.summary
            config   = summary.config
            runtime  = summary.runtime
            guest    = summary.guest

            power_state = str(runtime.powerState)
            host_name   = vm.runtime.host.name if vm.runtime.host else ""

            cpu_cores = config.numCpu if config else 0
            ram_mb    = config.memorySizeMB if config else 0
            ram_gb    = round(ram_mb / 1024, 2)
            os_name   = config.guestFullName if config else ""
            vm_name   = config.name if config else vm.name

            # Disks
            disks = []
            total_gb = 0.0
            if hasattr(vm, "config") and vm.config:
                for dev in (vm.config.hardware.device or []):
                    if hasattr(dev, "capacityInKB"):
                        gb = round(dev.capacityInKB / (1024 * 1024), 2)
                        disks.append({
                            "mount_point": getattr(dev, "deviceInfo", {}).label if hasattr(dev, "deviceInfo") else "disk",
                            "size_gb": gb,
                            "disk_type": "SSD" if "ssd" in str(getattr(dev, "backing", "")).lower() else "HDD",
                        })
                        total_gb += gb

            ip = ""
            if guest and guest.ipAddress:
                ip = guest.ipAddress

            servers.append({
                "server_name":        vm_name,
                "ip_address":         ip,
                "hostname":           vm_name,
                "cloud_provider":     "onprem",
                "server_type":        "Virtual",
                "virtualization_state": "Virtualized",
                "cpu_cores":          cpu_cores,
                "ram_gb":             ram_gb,
                "os_name":            os_name,
                "disks":              disks,
                "total_storage_gb":   round(total_gb, 2),
                "raw_metadata": {
                    "vm_power_state": power_state,
                    "hypervisor_host": host_name,
                    "tools_status": str(getattr(guest, "toolsStatus", "")),
                    "vcenter_host": vcenter_host,
                },
                "virtualization_attributes": {
                    "hypervisor": "VMware ESXi",
                    "host": host_name,
                },
            })

        container_view.Destroy()
        log.info("vSphere scan complete: %d VMs discovered", len(servers))
    except Exception as exc:
        log.warning("vSphere scan failed: %s", exc)

    return servers


# Function: analyze_hypervisor_consolidation
def analyze_hypervisor_consolidation(report: dict) -> dict:
    """
    Main entry point. Analyzes scan report for virtualization consolidation opportunities.
    """
    servers = report.get("servers") or []
    if not servers:
        return {"error": "No servers in report", "clusters": [], "summary": {}}

    # Separate VMs from physical hosts
    vms       = [s for s in servers if _is_virtual(s)]
    physicals = [s for s in servers if _is_physical(s)]

    if not vms:
        return {
            "clusters":   [],
            "vm_sprawl":  [],
            "summary": {
                "total_servers":   len(servers),
                "virtual_count":   0,
                "physical_count":  len(physicals),
                "message":         "No virtual machines detected in scan",
            }
        }

    # Group VMs by cluster
    cluster_vms: dict[str, list[dict]] = defaultdict(list)
    for vm in vms:
        cluster = _cluster_group(vm)
        cluster_vms[cluster].append(vm)

    # Analyze each cluster
    cluster_results: list[dict] = []
    for cluster_name, c_vms in cluster_vms.items():
        consolidation = _consolidation_calculator(c_vms)

        # Hypervisor breakdown
        hypervisor_types: dict[str, int] = defaultdict(int)
        for vm in c_vms:
            hv = _get_hypervisor(vm) or "Unknown"
            hypervisor_types[hv] += 1

        cluster_results.append({
            "cluster_name":    cluster_name,
            "vm_count":        len(c_vms),
            "hypervisor_types": dict(hypervisor_types),
            "consolidation":   consolidation,
        })

    # VM Sprawl: stopped/powered-off VMs
    vm_sprawl: list[dict] = []
    for vm in vms:
        if _is_stopped_vm(vm):
            days = _days_since_created(vm)
            vm_sprawl.append({
                "server_name": _server_name(vm),
                "server_ip":   vm.get("ip_address") or vm.get("ip") or "",
                "power_state": (vm.get("raw_metadata") or {}).get("vm_power_state") or "stopped",
                "days_since_created": days,
                "is_sprawl":   days is None or days > 90,
                "recommendation": "Decommission if unused for 90+ days",
            })

    # Over-committed hosts (from physical servers with VM role)
    over_committed: list[dict] = []
    for phys in physicals:
        vm_count_on_host = sum(
            1 for vm in vms
            if (_cluster_group(vm) == _cluster_group(phys) or
                (vm.get("virtualization_attributes") or {}).get("host") == _server_name(phys))
        )
        if vm_count_on_host > _MAX_VM_PER_HOST:
            over_committed.append({
                "host_name":    _server_name(phys),
                "vm_count":     vm_count_on_host,
                "threshold":    _MAX_VM_PER_HOST,
                "recommendation": f"Host has {vm_count_on_host} VMs — consider adding capacity or redistributing",
            })

    # Totals
    total_consolidation = _consolidation_calculator(vms)

    return {
        "clusters":          cluster_results,
        "vm_sprawl":         vm_sprawl,
        "over_committed_hosts": over_committed,
        "global_consolidation": total_consolidation,
        "summary": {
            "total_servers":              len(servers),
            "virtual_count":              len(vms),
            "physical_count":             len(physicals),
            "stopped_vm_count":           len(vm_sprawl),
            "sprawl_vm_count":            sum(1 for v in vm_sprawl if v["is_sprawl"]),
            "cluster_count":              len(cluster_results),
            "total_hosts_to_eliminate":   total_consolidation["hosts_to_eliminate"],
            "estimated_monthly_savings_usd": total_consolidation["estimated_monthly_savings_usd"],
            "vm_to_physical_ratio":       round(len(vms) / max(1, len(physicals)), 1),
        },
    }
