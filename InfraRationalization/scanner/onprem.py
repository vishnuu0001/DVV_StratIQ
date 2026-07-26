# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: scanner/onprem.py
# Date: 2025-12-06
# ---------------------------------------------------------------------------
"""
scanner/onprem.py
On-premises network scanner.

Discovery strategy (best-effort, graceful fallback at each level):
  1. nmap  — host discovery + port scan in the CIDR
  2. SSH   — paramiko (Linux/Unix): uname, lscpu, free, df, /etc/os-release,
              systemctl list-units, netstat, dmidecode, lsblk
  3. WinRM — pywinrm (Windows): WMI queries for OS, CPU, RAM, disk, services
  4. SNMP  — pysnmp fallback for network-only devices (switches/routers)
  5. Banner grab — extract OS hints from SSH/HTTP banners when creds absent

All levels are optional — missing binaries/creds reduce fidelity, never crash.
"""
from __future__ import annotations

import ipaddress
import logging
import os
import re
import shutil
import socket
import subprocess
import threading
from typing import Callable

from .models import (
    DiscoveredServer,
    DiskInfo,
    InstalledSoftware,
    NetworkInterface,
    ScanTarget,
    WorkloadComponent,
)

log = logging.getLogger(__name__)

# ─── Well-known service map (port → workload type + name hint) ─────────────────
_PORT_SERVICES: dict[int, tuple[str, str]] = {
    22:   ("ssh",    "SSH"),
    80:   ("web",    "HTTP"),
    443:  ("web",    "HTTPS"),
    3306: ("db",     "MySQL"),
    5432: ("db",     "PostgreSQL"),
    1433: ("db",     "MSSQL"),
    1521: ("db",     "Oracle DB"),
    5984: ("db",     "CouchDB"),
    27017:("db",     "MongoDB"),
    6379: ("cache",  "Redis"),
    11211:("cache",  "Memcached"),
    9200: ("search", "Elasticsearch"),
    8080: ("app",    "HTTP-Alt"),
    8443: ("app",    "HTTPS-Alt"),
    8009: ("app",    "ApacheTomcat-AJP"),
    8005: ("app",    "ApacheTomcat-Control"),
    9090: ("app",    "AppServer"),
    4848: ("app",    "GlassFish"),
    7001: ("app",    "WebLogic"),
    9001: ("app",    "JBoss"),
    25:   ("mail",   "SMTP"),
    143:  ("mail",   "IMAP"),
    110:  ("mail",   "POP3"),
    389:  ("ldap",   "LDAP"),
    636:  ("ldap",   "LDAPS"),
    2181: ("queue",  "ZooKeeper"),
    9092: ("queue",  "Kafka"),
    5672: ("queue",  "RabbitMQ"),
    61616:("queue",  "ActiveMQ"),
    3389: ("rdp",    "RDP"),
    5900: ("vnc",    "VNC"),
    161:  ("snmp",   "SNMP"),
}

# Common TCP ports to scan
_COMMON_PORTS = ",".join(str(p) for p in sorted(_PORT_SERVICES.keys()))


# ─── nmap helpers ──────────────────────────────────────────────────────────────

# Function: _nmap_available
def _nmap_available() -> bool:
    return shutil.which("nmap") is not None


# Function: _nmap_scan
def _nmap_scan(cidr: str, timeout: int = 120) -> list[dict]:
    """
    Returns list of dicts: {ip, hostname, state, open_ports: [int]}
    Uses nmap host discovery + port scan.  Falls back to socket ping sweep.
    """
    if not _nmap_available():
        log.warning("nmap not found — using socket sweep fallback")
        return _socket_sweep(cidr)

    cmd = [
        "nmap", "-sV", "--open", "-T4", "-O", "--osscan-guess",
        f"-p{_COMMON_PORTS}",
        "--host-timeout", f"{timeout}s",
        "-oX", "-",            # XML output on stdout
        cidr,
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout + 30
        )
        return _parse_nmap_xml(result.stdout)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
        log.warning("nmap scan failed: %s", exc)
        return _socket_sweep(cidr)


# Function: _parse_nmap_xml
def _parse_nmap_ports(host_block: str) -> tuple:
    open_ports: list[int] = []
    service_hints: dict[int, str] = {}
    for port_m in re.finditer(
        r'<port protocol="tcp" portid="(\d+)">(.*?)</port>', host_block, re.DOTALL
    ):
        port_num = int(port_m.group(1))
        port_block = port_m.group(2)
        state_m = re.search(r'<state state="(\w+)"', port_block)
        if not state_m or state_m.group(1) != "open":
            continue
        open_ports.append(port_num)
        svc_m = re.search(
            r'<service[^>]+(?:name="([^"]*)")?[^>]*(?:product="([^"]*)")?[^>]*(?:version="([^"]*)")?',
            port_block,
        )
        if svc_m:
            svc_parts = [p for p in svc_m.groups() if p]
            service_hints[port_num] = " ".join(svc_parts)
    return open_ports, service_hints


# Function: _parse_nmap_host_block
def _parse_nmap_host_block(host_block: str) -> dict:
    # Status
    status_m = re.search(r'<status state="(\w+)"', host_block)
    if not status_m or status_m.group(1) != "up":
        return None
    # IP
    addr_m = re.search(r'<address addr="([\d.]+)" addrtype="ipv4"', host_block)
    if not addr_m:
        return None
    ip = addr_m.group(1)
    # Hostname
    hn_m = re.search(r'<hostname name="([^"]+)"', host_block)
    hostname = hn_m.group(1) if hn_m else ""
    # Open ports + service banners
    open_ports, service_hints = _parse_nmap_ports(host_block)

    _mac_m = re.search(r'<address addr="([0-9a-fA-F:]+)"\s+addrtype="mac"', host_block)
    _os_m  = re.search(r'<osmatch name="([^"]+)"\s+accuracy="(\d+)"', host_block)
    return {
        "ip": ip,
        "hostname": hostname,
        "state": "up",
        "open_ports": open_ports,
        "service_hints": service_hints,
        "mac": _mac_m.group(1).lower() if _mac_m else "",
        "os_guess": _os_m.group(1) if _os_m and int(_os_m.group(2)) >= 70 else "",
    }


# Function: _parse_nmap_xml
def _parse_nmap_xml(xml: str) -> list[dict]:
    """Parse nmap XML output — lightweight without lxml dependency."""
    hosts = []
    # Match each <host> block
    for host_block in re.findall(r"<host\b[^>]*>(.*?)</host>", xml, re.DOTALL):
        host = _parse_nmap_host_block(host_block)
        if host:
            hosts.append(host)
    return hosts


# Function: _socket_sweep
def _socket_probe_host(ip_str: str, results: list, lock) -> None:
    open_ports: list[int] = []
    for port in [22, 80, 443, 3306, 5432, 1433, 3389, 8080, 8443, 5900]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            if s.connect_ex((ip_str, port)) == 0:
                open_ports.append(port)
            s.close()
        except OSError:
            pass
    if not open_ports:
        return
    try:
        hn = socket.gethostbyaddr(ip_str)[0]
    except socket.herror:
        hn = ""
    with lock:
        results.append({
            "ip": ip_str,
            "hostname": hn,
            "state": "up",
            "open_ports": open_ports,
            "service_hints": {},
        })


# Function: _socket_sweep
def _socket_sweep(cidr: str) -> list[dict]:
    """Fallback: parallel TCP connect on common ports."""
    try:
        network = ipaddress.ip_network(cidr, strict=False)
    except ValueError:
        return []

    results: list[dict] = []
    lock = threading.Lock()

    threads = [threading.Thread(target=_socket_probe_host, args=(str(ip), results, lock), daemon=True)
               for ip in network.hosts()]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)
    return results


# ─── Level-0: ARP sweep (MAC without credentials) ─────────────────────────────

# Function: _arp_sweep_nmap
def _arp_sweep_nmap(cidr: str, timeout: int = 30) -> dict[str, str]:
    """
    Fast ARP-ping sweep with nmap (-PR -sn).
    Returns {ip: mac_address} for every host on the same L2 segment.
    nmap can resolve MACs via ARP even without Npcap on Windows (ICMP fallback).
    """
    mac_map: dict[str, str] = {}
    if not _nmap_available():
        return mac_map
    try:
        result = subprocess.run(
            ["nmap", "-PR", "-sn", "-T4", "--max-retries", "2",
             "--host-timeout", f"{timeout}s", "-oX", "-", cidr],
            capture_output=True, text=True, timeout=timeout + 15,
        )
        for block in re.findall(r"<host\b[^>]*>(.*?)</host>", result.stdout, re.DOTALL):
            ip_m  = re.search(r'<address addr="([\d.]+)"\s+addrtype="ipv4"', block)
            mac_m = re.search(r'<address addr="([0-9a-fA-F:]+)"\s+addrtype="mac"', block)
            if ip_m and mac_m:
                mac_map[ip_m.group(1)] = mac_m.group(1).lower()
    except Exception as exc:
        log.debug("ARP sweep failed: %s", exc)
    return mac_map


# Function: _powershell_arp_neighbors
def _powershell_arp_neighbors() -> dict[str, str]:
    """
    Windows-only: run Get-NetNeighbor for the complete ARP/NDP table.
    More comprehensive than `arp -a` (includes stale entries, all interfaces).
    Returns {ip: mac}.
    """
    import platform
    if platform.system() != "Windows":
        return {}
    mac_map: dict[str, str] = {}
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command",
             "Get-NetNeighbor -AddressFamily IPv4 "
             "| Where-Object {$_.State -ne 'Unreachable' -and $_.LinkLayerAddress -notmatch '^0{12}$'} "
             "| Select-Object IPAddress,LinkLayerAddress "
             "| ConvertTo-Json -Compress"],
            capture_output=True, text=True, timeout=15, check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            import json as _json
            rows = _json.loads(result.stdout.strip())
            if isinstance(rows, dict):
                rows = [rows]
            for row in rows:
                ip  = (row.get("IPAddress") or "").strip()
                mac = (row.get("LinkLayerAddress") or "").replace("-", ":").lower().strip()
                if (ip and mac
                        and mac not in ("ff:ff:ff:ff:ff:ff", "00:00:00:00:00:00")
                        and not ip.startswith("127.")
                        and not ip.endswith(".255")):
                    mac_map[ip] = mac
    except Exception as exc:
        log.debug("PowerShell Get-NetNeighbor failed: %s", exc)
    return mac_map


# ─── Level-0: SNMP enrichment (MAC / speed / VLAN without credentials) ────────

_SNMP_COMMUNITIES = ["public", "private", "community", "snmpd", "admin", "cisco"]

# IF-MIB column numbers (1.3.6.1.2.1.2.2.1.<col>.<ifIndex>)
_IF_COL_DESCR       = "2"   # ifDescr
_IF_COL_TYPE        = "3"   # ifType  (6=ethernetCsmacd, 24=softwareLoopback)
_IF_COL_MTU         = "4"   # ifMtu
_IF_COL_SPEED       = "5"   # ifSpeed (bps, capped at 4 Gbps – use ifHighSpeed for 10G+)
_IF_COL_PHYS        = "6"   # ifPhysAddress (MAC)
_IF_COL_ADMIN       = "7"   # ifAdminStatus (1=up)
_IF_COL_OPER        = "8"   # ifOperStatus  (1=up)
_IF_COL_HIGHSPEED   = "15"  # ifHighSpeed in Mbps (RFC 2863)


# Function: _snmpwalk_subprocess
def _snmpwalk_subprocess(
    ip: str, oid: str, community: str = "public", timeout: int = 3
) -> list[tuple[str, str]]:
    """
    Try `snmpwalk` (net-snmp) via subprocess.
    Returns list of (oid_string, value_string) pairs.
    """
    if not shutil.which("snmpwalk"):
        return []
    try:
        result = subprocess.run(
            ["snmpwalk", "-v2c", "-c", community, "-t", str(timeout),
             "-r", "1", "-Oqn", ip, oid],
            capture_output=True, text=True, timeout=timeout + 3,
        )
        rows: list[tuple[str, str]] = []
        for line in result.stdout.splitlines():
            if " " in line:
                oid_part, _, val_part = line.partition(" ")
                rows.append((oid_part.strip(), val_part.strip()))
        return rows
    except Exception:
        return []


# Function: _snmpget_pysnmp
def _snmpget_pysnmp(
    ip: str, oids: list[str], community: str = "public", timeout: int = 3
) -> dict[str, str]:
    """
    Try pysnmp (sync hlapi) for SNMP GET of multiple scalar OIDs.
    Returns {oid: value_str}.
    """
    try:
        from pysnmp.hlapi import (  # type: ignore
            SnmpEngine, CommunityData, UdpTransportTarget,
            ContextData, ObjectType, ObjectIdentity, getCmd,
        )
    except ImportError:
        return {}
    result_map: dict[str, str] = {}
    try:
        engine = SnmpEngine()
        gen = getCmd(
            engine,
            CommunityData(community, mpModel=1),  # nosec B508
            UdpTransportTarget((ip, 161), timeout=timeout, retries=1),
            ContextData(),
            *[ObjectType(ObjectIdentity(oid)) for oid in oids],
        )
        error_indication, error_status, _, var_binds = next(gen)
        if not error_indication and not error_status:
            for vb in var_binds:
                result_map[str(vb[0])] = str(vb[1])
    except Exception:
        pass
    return result_map


# Function: _snmpwalk_pysnmp
def _snmpwalk_pysnmp(
    ip: str, base_oid: str, community: str = "public", timeout: int = 4
) -> list[tuple[str, str]]:
    """
    Try pysnmp (sync hlapi) for SNMP WALK.
    Returns list of (oid_string, value_string) pairs.
    """
    try:
        from pysnmp.hlapi import (  # type: ignore
            SnmpEngine, CommunityData, UdpTransportTarget,
            ContextData, ObjectType, ObjectIdentity, nextCmd,
        )
    except ImportError:
        return []
    rows: list[tuple[str, str]] = []
    try:
        engine = SnmpEngine()
        for error_indication, error_status, _, var_binds in nextCmd(
            engine,
            CommunityData(community, mpModel=1),  # nosec B508
            UdpTransportTarget((ip, 161), timeout=timeout, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity(base_oid)),
            lexicographicMode=False,
        ):
            if error_indication or error_status:
                break
            for vb in var_binds:
                rows.append((str(vb[0]), str(vb[1])))
    except Exception:
        pass
    return rows


# Function: _snmp_walk
def _snmp_walk(
    ip: str, oid: str, community: str = "public", timeout: int = 4
) -> list[tuple[str, str]]:
    """Dispatcher: try snmpwalk subprocess then pysnmp fallback."""
    rows = _snmpwalk_subprocess(ip, oid, community, timeout)
    if not rows:
        rows = _snmpwalk_pysnmp(ip, oid, community, timeout)
    return rows


# Function: _snmp_available
def _snmp_available() -> bool:
    """True if any SNMP backend is usable."""
    if shutil.which("snmpwalk"):
        return True
    try:
        import pysnmp  # noqa: F401
        return True
    except ImportError:
        return False


# Function: _snmp_clean_val
def _snmp_clean_val(raw: str) -> str:
    """Strip pysnmp/snmpwalk type prefixes like 'STRING: ', 'INTEGER: ', 'Gauge32: '."""
    return re.sub(r"^[A-Z][A-Za-z0-9]+:\s*", "", raw).strip('"').strip()


# Function: _snmp_parse_mac
def _snmp_parse_mac(raw: str) -> str:
    """Parse MAC from 'Hex-STRING: aa bb cc dd ee ff' or 'aa:bb:cc:dd:ee:ff'."""
    raw = _snmp_clean_val(raw)
    # Normalize hex spaces/dashes to colons
    normalized = re.sub(r"[\s\-]", ":", raw.strip())
    if re.fullmatch(r"([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}", normalized):
        return normalized.lower()
    # Try extracting hex bytes
    parts = re.findall(r"[0-9a-fA-F]{2}", raw)
    if len(parts) == 6:
        return ":".join(parts).lower()
    return ""


# Function: _snmp_process_iface
def _snmp_iface_speed_mbps(speed_raw: str, hi_speed: str) -> int:
    try:
        hi = int(hi_speed)
        sp = int(speed_raw)
        return hi if hi > 0 else (sp // 1_000_000 if sp > 0 else 0)
    except (ValueError, TypeError):
        return 0


# Function: _snmp_iface_mtu
def _snmp_iface_mtu(mtu_raw: str) -> int:
    try:
        return int(mtu_raw)
    except (ValueError, TypeError):
        return 0


# Function: _snmp_iface_link_state
def _snmp_iface_link_state(oper_raw: str) -> str:
    if oper_raw in ("1", "up", "integer: 1"):
        return "up"
    if oper_raw in ("2", "integer: 2"):
        return "down"
    return "unknown"


# Function: _snmp_iface_subnet
def _snmp_iface_subnet(ip_for_if: str, mask: str) -> str:
    if not (ip_for_if and mask):
        return ""
    try:
        return str(ipaddress.IPv4Network(f"{ip_for_if}/{mask}", strict=False))
    except Exception:
        return f"{ip_for_if}/{mask}"


# Function: _snmp_find_existing_iface
def _snmp_find_existing_iface(server: DiscoveredServer, ip_for_if: str, iface_name: str):
    if ip_for_if:
        existing = next(
            (i for i in server.interfaces if i.ip_address == ip_for_if), None
        )
        if existing:
            return existing
    if iface_name:
        return next(
            (i for i in server.interfaces
             if i.interface_name.lower() == iface_name.lower()),
            None,
        )
    return None


# Function: _snmp_update_existing_iface
def _snmp_update_existing_iface(existing, mac_norm: str, speed_mbps: int,
                                 mtu: int, link_state: str, ip_for_if: str, subnet_cidr: str) -> None:
    if mac_norm and not existing.mac_address:
        existing.mac_address = mac_norm
    if speed_mbps and not existing.bandwidth_mbps:
        existing.bandwidth_mbps = speed_mbps
    if mtu and not existing.mtu:
        existing.mtu = mtu
    if link_state != "unknown" and not existing.link_state:
        existing.link_state = link_state
    if ip_for_if and not existing.ip_address:
        existing.ip_address = ip_for_if
        existing.ip_type = (
            "public" if not _is_private(ip_for_if) else "private"
        )
    if subnet_cidr and not existing.subnet:
        existing.subnet = subnet_cidr


# Function: _snmp_append_new_iface
def _snmp_append_new_iface(server: DiscoveredServer, iface_name: str, idx: str, ip_for_if: str,
                            mac_norm: str, subnet_cidr: str, speed_mbps: int, mtu: int, link_state: str) -> None:
    if ip_for_if and not ip_for_if.startswith("127."):
        server.interfaces.append(NetworkInterface(
            interface_name=iface_name or f"if{idx}",
            ip_address=ip_for_if,
            ip_type="public" if not _is_private(ip_for_if) else "private",
            mac_address=mac_norm,
            subnet=subnet_cidr,
            bandwidth_mbps=speed_mbps,
            mtu=mtu,
            link_state=link_state,
        ))
    elif mac_norm and not any(
        i.mac_address == mac_norm for i in server.interfaces
    ):
        server.interfaces.append(NetworkInterface(
            interface_name=iface_name or f"if{idx}",
            mac_address=mac_norm,
            bandwidth_mbps=speed_mbps,
            mtu=mtu,
            link_state=link_state,
        ))


# Function: _snmp_process_iface
def _snmp_process_iface(
    server: DiscoveredServer,
    idx: str,
    fields: dict[str, str],
    ip_to_idx: dict[str, str],
    ip_to_mask: dict[str, str],
) -> None:
    iface_name = _snmp_clean_val(fields.get(_IF_COL_DESCR, ""))
    if_type    = _snmp_clean_val(fields.get(_IF_COL_TYPE, ""))
    mac_raw    = fields.get(_IF_COL_PHYS, "")
    speed_raw  = _snmp_clean_val(fields.get(_IF_COL_SPEED, "0"))
    hi_speed   = _snmp_clean_val(fields.get(_IF_COL_HIGHSPEED, "0"))
    oper_raw   = _snmp_clean_val(fields.get(_IF_COL_OPER, ""))
    mtu_raw    = _snmp_clean_val(fields.get(_IF_COL_MTU, "0"))

    if if_type in ("24", "softwareLoopback") or "loop" in iface_name.lower():
        return
    if not iface_name or iface_name.lower() in ("lo", "null0"):
        return

    mac_norm = _snmp_parse_mac(mac_raw)
    if mac_norm in ("ff:ff:ff:ff:ff:ff", "00:00:00:00:00:00"):
        mac_norm = ""

    speed_mbps = _snmp_iface_speed_mbps(speed_raw, hi_speed)
    mtu = _snmp_iface_mtu(mtu_raw)
    link_state = _snmp_iface_link_state(oper_raw)

    ip_for_if = next((a for a, i in ip_to_idx.items() if i == idx), "")
    mask      = ip_to_mask.get(ip_for_if, "")
    subnet_cidr = _snmp_iface_subnet(ip_for_if, mask)

    existing = _snmp_find_existing_iface(server, ip_for_if, iface_name)

    if existing:
        _snmp_update_existing_iface(existing, mac_norm, speed_mbps, mtu, link_state, ip_for_if, subnet_cidr)
        return

    _snmp_append_new_iface(server, iface_name, idx, ip_for_if, mac_norm, subnet_cidr, speed_mbps, mtu, link_state)


# Function: _snmp_enrich
def _snmp_apply_sys_info(server: DiscoveredServer, ip: str, community: str, sys_desc_rows: list) -> None:
    sys_desc = _snmp_clean_val(sys_desc_rows[0][1]) if sys_desc_rows else ""
    if sys_desc and not server.os_name:
        server.os_name = sys_desc[:100]
        lower = sys_desc.lower()
        if "windows" in lower:
            server.os_family = "windows"
        elif "linux" in lower or "unix" in lower:
            server.os_family = "linux"

    sys_name_rows = _snmp_walk(ip, "1.3.6.1.2.1.1.5.0", community, timeout=2)
    if sys_name_rows and not server.hostname:
        server.hostname = _snmp_clean_val(sys_name_rows[0][1])
        if not server.server_name or server.server_name == ip:
            server.server_name = server.hostname


# Function: _snmp_build_if_table
def _snmp_build_if_table(if_rows: list) -> dict:
    # Build table[ifIndex][column] = value
    if_table: dict[str, dict[str, str]] = {}
    for oid_str, val in if_rows:
        m = re.search(r"\.(\d+)\.(\d+)$", oid_str)
        if not m:
            continue
        col, idx = m.group(1), m.group(2)
        if idx not in if_table:
            if_table[idx] = {}
        if_table[idx][col] = val
    return if_table


# Function: _snmp_build_ip_maps
def _snmp_build_ip_maps(ip_rows: list) -> tuple:
    ip_to_idx: dict[str, str] = {}   # ip_addr → ifIndex
    ip_to_mask: dict[str, str] = {}  # ip_addr → netmask
    for oid_str, val in ip_rows:
        # .1.3.6.1.2.1.4.20.1.<col>.<a>.<b>.<c>.<d>
        m = re.search(r"\.(\d+)\.((?:\d+\.){3}\d+)$", oid_str)
        if not m:
            continue
        col, ip_addr = m.group(1), m.group(2)
        clean = _snmp_clean_val(val)
        if col == "2":
            ip_to_idx[ip_addr] = clean
        elif col == "3":
            ip_to_mask[ip_addr] = clean
    return ip_to_idx, ip_to_mask


# Function: _snmp_enrich
def _snmp_enrich(server: DiscoveredServer) -> None:
    """
    Deep-scan a host via SNMP (no credentials needed).
    Populates: mac_address, bandwidth_mbps, link_state, mtu on interfaces;
               os_name/hostname from sysDescr/sysName.
    Tries communities: public, private, community, …
    """
    if not _snmp_available():
        return

    ip = server.ip_address

    for community in _SNMP_COMMUNITIES:
        # Quick liveness check — sysDescr scalar OID
        test = _snmp_walk(ip, "1.3.6.1.2.1.1.1.0", community, timeout=2)
        if not test:
            continue  # community doesn't work

        # ── System description / hostname ──────────────────────────────────
        _snmp_apply_sys_info(server, ip, community, test)

        # ── IF-MIB: full interface table ───────────────────────────────────
        if_rows = _snmp_walk(ip, "1.3.6.1.2.1.2.2", community, timeout=5)
        if not if_rows:
            break  # community works but no IF-MIB — rare

        if_table = _snmp_build_if_table(if_rows)

        # ── IP-MIB: map IP addresses to ifIndex ───────────────────────────
        ip_rows = _snmp_walk(ip, "1.3.6.1.2.1.4.20", community, timeout=5)
        ip_to_idx, ip_to_mask = _snmp_build_ip_maps(ip_rows)

        # ── Build per-interface data ───────────────────────────────────────
        for idx, fields in if_table.items():
            _snmp_process_iface(server, idx, fields, ip_to_idx, ip_to_mask)

        break  # Successfully used this community — stop trying others


# ─── SSH discovery ─────────────────────────────────────────────────────────────

# Function: _ssh_available
def _ssh_available() -> bool:
    try:
        import paramiko  # noqa: F401
        return True
    except ImportError:
        return False


# Function: _ssh_run
def _ssh_run(client, cmd: str) -> str:
    try:
        _, stdout, _ = client.exec_command(cmd, timeout=15)  # nosec B601
        return stdout.read().decode("utf-8", errors="replace").strip()
    except Exception:
        return ""


# Function: _parse_key_value
def _parse_key_value(text: str, sep: str = "=") -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        if sep in line:
            k, _, v = line.partition(sep)
            result[k.strip()] = v.strip().strip('"')
    return result


# Function: _gather_raw_interface_data
def _sysclass_parse_line(line: str):
    parts = line.split("|")
    if len(parts) < 7:
        return None
    if_name, mac, spd, st, dup, mtu_s, flags_hex = parts[:7]
    if not if_name or if_name in ("lo", "docker0"):
        return None
    speed_mbps = 0
    try:
        v = int(spd)
        if v > 0:
            speed_mbps = v
    except (ValueError, TypeError):
        pass
    try:
        mtu = int(mtu_s)
    except (ValueError, TypeError):
        mtu = 0
    iface_flags_str = ""
    try:
        fl = int(flags_hex, 16)
        flag_bits = {
            0x1: "UP", 0x2: "BROADCAST", 0x8: "LOOPBACK",
            0x10: "POINTTOPOINT", 0x40: "RUNNING", 0x100: "PROMISC",
            0x1000: "MULTICAST",
        }
        iface_flags_str = ",".join(
            name for bit, name in sorted(flag_bits.items()) if fl & bit
        )
    except (ValueError, TypeError):
        pass
    return if_name, {
        "mac":        mac.strip().lower() if mac.strip() != "00:00:00:00:00:00" else "",
        "speed_mbps": speed_mbps,
        "state":      st.strip().lower(),
        "duplex":     dup.strip().lower(),
        "mtu":        mtu,
        "flags":      iface_flags_str,
    }


# Function: _gather_sysclass_data
def _gather_sysclass_data(client) -> dict:
    sysclass_out = _ssh_run(
        client,
        "for iface in $(ls /sys/class/net/ 2>/dev/null); do "
        "  spd=$(cat /sys/class/net/$iface/speed 2>/dev/null); "
        "  mac=$(cat /sys/class/net/$iface/address 2>/dev/null); "
        "  st=$(cat /sys/class/net/$iface/operstate 2>/dev/null); "
        "  dup=$(cat /sys/class/net/$iface/duplex 2>/dev/null); "
        "  mtu=$(cat /sys/class/net/$iface/mtu 2>/dev/null); "
        "  flags=$(cat /sys/class/net/$iface/flags 2>/dev/null); "
        "  echo \"$iface|$mac|$spd|$st|$dup|$mtu|$flags\"; "
        "done 2>/dev/null",
    )
    sysclass: dict[str, dict] = {}
    for line in sysclass_out.splitlines():
        parsed = _sysclass_parse_line(line)
        if parsed:
            if_name, data = parsed
            sysclass[if_name] = data
    return sysclass


# Function: _gather_link_json
def _gather_link_json(client) -> dict:
    ip_json_out = _ssh_run(client, "ip -j -d link show 2>/dev/null")
    link_json: dict[str, dict] = {}
    try:
        import json as _json
        link_list = _json.loads(ip_json_out)
        for lnk in link_list:
            name = lnk.get("ifname", "")
            if not name or name == "lo":
                continue
            link_json[name] = lnk
    except Exception:
        pass
    return link_json


# Function: _gather_ip_by_iface
def _gather_ip_by_iface(client) -> dict:
    ip_out = _ssh_run(client, "ip -o addr show 2>/dev/null || ifconfig -a 2>/dev/null")
    ip_by_iface: dict[str, list[tuple[str, str]]] = {}
    for m in re.finditer(r"(\S+)\s+inet\s+([\d.]+)/(\d+)", ip_out):
        name, addr, pfx = m.group(1), m.group(2), m.group(3)
        if addr.startswith("127.") or name == "lo":
            continue
        ip_by_iface.setdefault(name, []).append((addr, pfx))
    return ip_by_iface


# Function: _ethtool_parse_output
def _ethtool_parse_output(et_out: str) -> dict:
    et: dict[str, str] = {}
    for line in et_out.splitlines():
        line = line.strip()
        if "Speed:" in line:
            sm = re.search(r"(\d+)\s*(Mb/s|Gb/s|Kb/s)", line, re.IGNORECASE)
            if sm:
                val = int(sm.group(1))
                unit = sm.group(2).lower()
                mbps = val * 1000 if "gb" in unit else (val // 1000 if "kb" in unit else val)
                et["speed_mbps"] = str(mbps)
        elif "Duplex:" in line:
            et["duplex"] = line.split(":")[-1].strip().lower()
        elif "Link detected:" in line:
            et["link_detected"] = line.split(":")[-1].strip().lower()
    return et


# Function: _gather_ethtool_data
def _gather_ethtool_data(client, sysclass: dict) -> dict:
    ethtool_data: dict[str, dict] = {}
    for if_name in list(sysclass.keys()):
        et_out = _ssh_run(client, f"ethtool {if_name} 2>/dev/null")
        if not et_out:
            continue
        et = _ethtool_parse_output(et_out)
        if et:
            ethtool_data[if_name] = et
    return ethtool_data


# Function: _gather_raw_interface_data
def _gather_raw_interface_data(client) -> tuple:
    """Steps 1-4: Collect /sys/class/net, ip link JSON, ip addr, and ethtool data."""
    sysclass = _gather_sysclass_data(client)
    link_json = _gather_link_json(client)
    ip_by_iface = _gather_ip_by_iface(client)
    ethtool_data = _gather_ethtool_data(client, sysclass)
    return sysclass, link_json, ip_by_iface, ethtool_data


# Function: _gather_vlan_and_routing
def _gather_vlan_and_routing(client) -> tuple:
    """Steps 5-7: Collect bridge VLANs, VLAN config, and default gateway."""
    bridge_vlan_out = _ssh_run(client, "bridge vlan show 2>/dev/null")
    bridge_vlans: dict[str, list[str]] = {}
    current_bridge_if = ""
    for line in bridge_vlan_out.splitlines():
        if not line.startswith(" ") and not line.startswith("\t"):
            current_bridge_if = line.split()[0] if line.split() else ""
        else:
            vm = re.search(r"\b(\d{1,4})\b", line)
            if vm and current_bridge_if:
                bridge_vlans.setdefault(current_bridge_if, []).append(vm.group(1))

    vlan_out = _ssh_run(client, "cat /proc/net/vlan/config 2>/dev/null")
    vlan_map = _parse_vlan_info(vlan_out)

    gw_out = _ssh_run(client, "ip route show default 2>/dev/null")
    gw_m = re.search(r"default\s+via\s+([\d.]+)", gw_out)
    default_gw = gw_m.group(1) if gw_m else ""

    return bridge_vlans, vlan_map, default_gw


# Function: _gather_lldp_arp_routes
def _gather_lldp_arp_routes(client, server: DiscoveredServer) -> None:
    """Steps 8-10: Populate server LLDP neighbors, ARP table, and routing table."""
    lldp_raw = _ssh_run(client, "lldpctl -f json 2>/dev/null || lldpcli show neighbors details -f json 2>/dev/null")
    lldp_neighbors = _parse_lldpctl_json(lldp_raw)
    if lldp_neighbors:
        server.lldp_neighbors = lldp_neighbors

    arp_out = _ssh_run(client, "ip neigh show 2>/dev/null || arp -n 2>/dev/null")
    server.arp_neighbors = _parse_arp_table(arp_out, server.ip_address)

    route_raw = _ssh_run(client, "ip route show 2>/dev/null")
    server.routes = _parse_ip_routes(route_raw)


# Function: _assemble_iface_objects
def _iface_mac(sc: dict, lj: dict) -> str:
    mac = (lj.get("address") or "").lower() or sc.get("mac", "")
    if mac in ("00:00:00:00:00:00", "ff:ff:ff:ff:ff:ff"):
        return ""
    return mac


# Function: _iface_speed
def _iface_speed(sc: dict, et: dict) -> int:
    speed_mbps = int(et.get("speed_mbps", "0") or 0)
    if speed_mbps:
        return speed_mbps
    return sc.get("speed_mbps", 0)


# Function: _iface_link_state
def _iface_link_state(sc: dict, et: dict) -> str:
    link_state = sc.get("state", "")
    if et.get("link_detected") == "no":
        return "down"
    if et.get("link_detected") == "yes" and not link_state:
        return "up"
    return link_state


# Function: _iface_mtu
def _iface_mtu(sc: dict, lj: dict) -> int:
    mtu = sc.get("mtu", 0)
    if mtu:
        return mtu
    try:
        return int(lj.get("mtu", 0))
    except Exception:
        return mtu


# Function: _iface_vlan_id
def _iface_vlan_id(if_name: str, lj: dict, bridge_vlans: dict, vlan_map: dict) -> str:
    vlan_id = vlan_map.get(if_name, "")
    if vlan_id:
        return vlan_id
    li = lj.get("linkinfo", {})
    if isinstance(li, dict) and li.get("info_kind") == "vlan":
        vlan_id = str(li.get("info_data", {}).get("id", ""))
    if not vlan_id and if_name in bridge_vlans:
        vlan_id = bridge_vlans[if_name][0]
    return vlan_id


# Function: _assemble_iface_fields
def _assemble_iface_fields(if_name: str, sc: dict, lj: dict, et: dict, bridge_vlans: dict, vlan_map: dict) -> dict:
    return {
        "mac": _iface_mac(sc, lj),
        "speed_mbps": _iface_speed(sc, et),
        "duplex": et.get("duplex") or sc.get("duplex", ""),
        "link_state": _iface_link_state(sc, et),
        "mtu": _iface_mtu(sc, lj),
        "iface_flags": sc.get("flags", ""),
        "vlan_id": _iface_vlan_id(if_name, lj, bridge_vlans, vlan_map),
    }


# Function: _assemble_iface_with_ips
def _assemble_iface_with_ips(if_name: str, ips: list, fields: dict, default_gw: str) -> list:
    result = []
    for ip_addr, prefix in ips:
        try:
            net_str = str(ipaddress.ip_interface(f"{ip_addr}/{prefix}").network)
        except Exception:
            net_str = f"{ip_addr}/{prefix}"
        result.append(NetworkInterface(
            interface_name=if_name,
            ip_address=ip_addr,
            ip_type="public" if not _is_private(ip_addr) else "private",
            mac_address=fields["mac"],
            subnet=net_str,
            gateway=default_gw,
            bandwidth_mbps=fields["speed_mbps"],
            vlan_id=fields["vlan_id"],
            duplex=fields["duplex"],
            link_state=fields["link_state"],
            mtu=fields["mtu"],
            interface_flags=fields["iface_flags"],
        ))
    return result


# Function: _assemble_iface_objects
def _assemble_iface_objects(
    sysclass: dict, link_json: dict, ip_by_iface: dict,
    ethtool_data: dict, bridge_vlans: dict, vlan_map: dict, default_gw: str,
) -> list:
    """Build NetworkInterface objects from collected raw interface data."""
    all_iface_names: set[str] = set(sysclass) | set(ip_by_iface) | set(link_json)
    all_iface_names.discard("lo")

    new_interfaces: list[NetworkInterface] = []
    for if_name in sorted(all_iface_names):
        sc  = sysclass.get(if_name, {})
        lj  = link_json.get(if_name, {})
        et  = ethtool_data.get(if_name, {})
        ips = ip_by_iface.get(if_name, [])

        fields = _assemble_iface_fields(if_name, sc, lj, et, bridge_vlans, vlan_map)

        if ips:
            new_interfaces.extend(_assemble_iface_with_ips(if_name, ips, fields, default_gw))
        elif fields["mac"]:
            new_interfaces.append(NetworkInterface(
                interface_name=if_name,
                mac_address=fields["mac"],
                bandwidth_mbps=fields["speed_mbps"],
                vlan_id=fields["vlan_id"],
                duplex=fields["duplex"],
                link_state=fields["link_state"],
                mtu=fields["mtu"],
                interface_flags=fields["iface_flags"],
            ))

    return new_interfaces


# Function: _ssh_gather_network_data
def _ssh_gather_network_data(client, server: DiscoveredServer) -> None:
    """Gather full L2/L3 network data over SSH (Steps 1-10) and populate server.interfaces,
    server.lldp_neighbors, server.arp_neighbors, and server.routes."""
    sysclass, link_json, ip_by_iface, ethtool_data = _gather_raw_interface_data(client)
    bridge_vlans, vlan_map, default_gw = _gather_vlan_and_routing(client)
    _gather_lldp_arp_routes(client, server)
    new_interfaces = _assemble_iface_objects(
        sysclass, link_json, ip_by_iface, ethtool_data, bridge_vlans, vlan_map, default_gw,
    )
    if new_interfaces:
        server.interfaces = new_interfaces


# Function: _ssh_classify_storage
def _lsblk_parse_size(size_str: str) -> float:
    size_str = size_str.upper()
    try:
        if size_str.endswith("G"):
            return float(size_str[:-1])
        if size_str.endswith("T"):
            return float(size_str[:-1]) * 1024
        if size_str.endswith("M"):
            return float(size_str[:-1]) / 1024
        return 0.0
    except ValueError:
        return 0.0


# Function: _lsblk_classify_type
def _lsblk_classify_type(name: str, tran: str, rota: bool) -> str:
    if "nvme" in tran or "nvme" in name.lower():
        return "NVMe"
    if not rota:
        return "SSD"
    return "HDD"


# Function: _ssh_classify_storage
def _ssh_classify_storage(client, server: DiscoveredServer) -> None:
    """Classify storage as internal/external and detect SSD/NVMe/HDD via lsblk."""
    lsblk_full = _ssh_run(client, "lsblk -d -o NAME,SIZE,TYPE,ROTA,RM,TRAN 2>/dev/null")
    internal_gb = 0.0
    external_gb = 0.0
    flash_used = False
    storage_types: set[str] = set()
    for line in lsblk_full.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 4:
            continue
        size = _lsblk_parse_size(parts[1])
        removable = parts[4] == "1" if len(parts) > 4 else False
        tran = parts[5].lower() if len(parts) > 5 else ""
        rota = parts[3] == "1"

        stype = _lsblk_classify_type(parts[0], tran, rota)
        storage_types.add(stype)
        if stype in ("NVMe", "SSD"):
            flash_used = True

        if removable:
            external_gb += size
        else:
            internal_gb += size
    server.internal_storage_gb = round(internal_gb, 1)
    server.external_storage_gb = round(external_gb, 1)
    server.flash_storage_used   = flash_used
    if storage_types:
        server.storage_type = " / ".join(sorted(storage_types))


# Function: _ssh_collect_os_cpu_ram
def _ssh_collect_os_cpu_ram(client, server: DiscoveredServer) -> None:
    os_rel = _parse_key_value(_ssh_run(client, "cat /etc/os-release 2>/dev/null || cat /etc/lsb-release 2>/dev/null"), "=")
    if not os_rel:
        uname_raw = _ssh_run(client, "uname -srm")
        server.os_name = uname_raw
        server.os_family = "linux"
    else:
        server.os_name = os_rel.get("PRETTY_NAME") or os_rel.get("DISTRIB_DESCRIPTION", "Linux")
        server.os_family = "linux"
        server.os_version = os_rel.get("VERSION_ID", "")

    cpu_info = _ssh_run(client, "nproc 2>/dev/null || grep -c ^processor /proc/cpuinfo 2>/dev/null")
    if cpu_info.isdigit():
        server.cpu_cores = int(cpu_info)
    arch_out = _ssh_run(client, "uname -m")
    server.architecture = "64 bit" if "64" in arch_out else "32 bit"
    instance_type_out = _ssh_run(
        client,
        "curl -sf --max-time 2 http://169.254.169.254/latest/meta-data/instance-type 2>/dev/null "
        "|| curl -sf --max-time 2 -H 'Metadata:true' http://169.254.169.254/metadata/instance?api-version=2021-02-01 2>/dev/null "
        "| python3 -c \"import sys,json; d=json.load(sys.stdin); print(d.get('compute',{}).get('vmSize',''))\" 2>/dev/null"
    )
    if instance_type_out and len(instance_type_out) < 60:
        server.instance_type = instance_type_out

    meminfo = _ssh_run(client, "grep MemTotal /proc/meminfo")
    m = re.search(r"(\d+)", meminfo)
    if m:
        server.ram_gb = round(int(m.group(1)) / 1024 / 1024, 1)


# Function: _ssh_collect_disk_and_util
def _ssh_collect_disk_and_util(client, server: DiscoveredServer) -> None:
    df_out = _ssh_run(client, "df -BG --output=target,size,used,pcent,fstype 2>/dev/null | tail -n +2")
    lsblk_out = _ssh_run(client, "lsblk -d -o NAME,SIZE,TYPE,ROTA 2>/dev/null")
    server.disks = _parse_disks_linux(df_out, lsblk_out)
    server.total_storage_gb = sum(d.size_gb for d in server.disks)

    cpu_idle = _ssh_run(client, "vmstat 1 2 2>/dev/null | tail -1 | awk '{print $15}'")
    try:
        server.cpu_util_pct = round(100.0 - float(cpu_idle), 1)
    except ValueError:
        pass
    mem_avail = _ssh_run(client, "grep MemAvailable /proc/meminfo")
    m2 = re.search(r"(\d+)", mem_avail)
    if m2 and server.ram_gb > 0:
        avail_gb = int(m2.group(1)) / 1024 / 1024
        server.ram_util_pct = round(100.0 * (1 - avail_gb / server.ram_gb), 1)


# Function: _ssh_detect_virt
def _ssh_detect_virt(client, server: DiscoveredServer) -> None:
    dmi = _ssh_run(client, "sudo dmidecode -t system 2>/dev/null || cat /sys/class/dmi/id/sys_vendor 2>/dev/null")
    dmi_lower = dmi.lower()
    hypervisor = ""
    if "vmware" in dmi_lower:
        server.server_type = "Virtual"
        server.virtualization_state = "Virtualized"
        hypervisor = "VMware"
    elif "virtualbox" in dmi_lower:
        server.server_type = "Virtual"
        server.virtualization_state = "Virtualized"
        hypervisor = "VirtualBox"
    elif "kvm" in dmi_lower or "qemu" in dmi_lower:
        server.server_type = "Virtual"
        server.virtualization_state = "Virtualized"
        hypervisor = "KVM/QEMU"
    elif "xen" in dmi_lower:
        server.server_type = "Virtual"
        server.virtualization_state = "Virtualized"
        hypervisor = "Xen"
    elif "microsoft" in dmi_lower:
        server.server_type = "Virtual"
        server.virtualization_state = "Virtualized"
        hypervisor = "Hyper-V"
    else:
        server.server_type = "Physical"
        server.virtualization_state = "Physical"

    cgroup = _ssh_run(client, "cat /proc/1/cgroup 2>/dev/null | head -5")
    if "docker" in cgroup or "kubepods" in cgroup or "lxc" in cgroup:
        server.virtualization_state = "Container"
        hypervisor = "Container"

    server.virtualization_attributes = {
        "hypervisor": hypervisor,
        "dmi_hint":   dmi[:120].strip() if dmi else "",
    }


# Function: _ssh_collect_arch_install_boot
def _ssh_collect_arch_install_boot(client, server: DiscoveredServer) -> None:
    uname_machine = _ssh_run(client, "uname -m")
    if "x86_64" in uname_machine or "amd64" in uname_machine:
        server.compute_hardware_arch = "x86_64"
    elif "aarch64" in uname_machine or "arm64" in uname_machine:
        server.compute_hardware_arch = "ARM64"
    elif "ppc" in uname_machine:
        server.compute_hardware_arch = "POWER"
    elif "s390" in uname_machine:
        server.compute_hardware_arch = "IBM Z (Mainframe)"
        server.mainframe_dependency = "Yes"
    else:
        server.compute_hardware_arch = uname_machine or "x86_64"

    snap_count = _ssh_run(client, "snap list 2>/dev/null | wc -l")
    has_docker  = _ssh_run(client, "which docker 2>/dev/null")
    has_k8s     = _ssh_run(client, "which kubectl 2>/dev/null")
    if has_docker or has_k8s:
        server.install_type = "Container"
    elif snap_count.isdigit() and int(snap_count) > 2:
        server.install_type = "Cloud-Native"
    else:
        server.install_type = "Custom"

    db_engines = [
        f"{w.name} {w.version}".strip()
        for w in server.workloads if w.component_type == "db"
    ]
    if db_engines:
        server.db_engine = ", ".join(db_engines)
        server.db_storage_gb = round(server.total_storage_gb * 0.4, 1)

    boot_mode = _ssh_run(client, "[ -d /sys/firmware/efi ] && echo UEFI || echo BIOS")
    server.boot_type = "UEFI" if "UEFI" in boot_mode else "BIOS"


# Function: _ssh_enrich
def _ssh_enrich(server: DiscoveredServer, target: ScanTarget) -> None:
    """Connect over SSH and enrich the DiscoveredServer in-place."""
    if not _ssh_available():
        log.debug("paramiko not installed — skipping SSH enrichment")
        return

    import paramiko

    client = paramiko.SSHClient()
    insecure_ssh = os.getenv("ALLOW_INSECURE_SSH_HOSTKEY", "false").lower() in {"1", "true", "yes"}
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy() if insecure_ssh else paramiko.RejectPolicy())
    connect_kwargs: dict = {"hostname": server.ip_address, "timeout": 10}

    if target.ssh_key_path:
        try:
            connect_kwargs["pkey"] = paramiko.RSAKey.from_private_key_file(
                target.ssh_key_path
            )
        except Exception:
            pass
    if target.ssh_username:
        connect_kwargs["username"] = target.ssh_username
    if target.ssh_password:
        connect_kwargs["password"] = target.ssh_password

    try:
        client.connect(**connect_kwargs)
    except Exception as exc:
        log.debug("SSH connect to %s failed: %s", server.ip_address, exc)
        return

    try:
        _ssh_collect_os_cpu_ram(client, server)
        _ssh_collect_disk_and_util(client, server)

        # ── Network interfaces — deep L2/L3 gather ────────────────────────
        _ssh_gather_network_data(client, server)

        # ── Workloads ──
        server.workloads = _discover_workloads_ssh(client)

        # ── Installed software inventory ──
        server.installed_software = _collect_installed_software_ssh(client)

        _ssh_detect_virt(client, server)
        _ssh_collect_arch_install_boot(client, server)

        # ── Extended storage classification ──
        _ssh_classify_storage(client, server)

        # ── If package manager returned nothing, supplement from workloads ──
        if not server.installed_software:
            server.installed_software = _infer_software_from_workloads(server)

    finally:
        client.close()


# Function: _parse_disks_linux
def _parse_disks_linux(df_out: str, lsblk_out: str) -> list[DiskInfo]:
    disks: list[DiskInfo] = []
    # Rotation map from lsblk: 0=SSD, 1=HDD
    rotation: dict[str, bool] = {}
    for line in lsblk_out.splitlines():
        parts = line.split()
        if len(parts) >= 4:
            rotation[parts[0]] = parts[3] == "1"
    for line in df_out.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        try:
            size_gb = float(parts[1].rstrip("G"))
            used_gb = float(parts[2].rstrip("G"))
        except ValueError:
            continue
        rota = next((v for k, v in rotation.items() if k in parts[0]), None)
        disk_type = "HDD" if rota else "SSD" if rota is False else "unknown"
        disks.append(DiskInfo(
            mount_point=parts[0],
            size_gb=size_gb,
            used_gb=used_gb,
            disk_type=disk_type,
        ))
    return disks


# Function: _parse_interfaces_linux
def _parse_interfaces_linux(ip_out: str) -> list[NetworkInterface]:
    ifaces: list[NetworkInterface] = []
    seen: set[str] = set()
    for m in re.finditer(r"(\w+)\s+inet\s+([\d.]+)/(\d+)", ip_out):
        iface_name, ip, prefix = m.group(1), m.group(2), m.group(3)
        if ip.startswith("127.") or iface_name == "lo":
            continue
        if ip in seen:
            continue
        seen.add(ip)
        ip_type = "public" if not _is_private(ip) else "private"
        ifaces.append(NetworkInterface(
            interface_name=iface_name,
            ip_address=ip,
            ip_type=ip_type,
            subnet=f"{ip}/{prefix}",
        ))
    return ifaces


# Function: _is_private
def _is_private(ip: str) -> bool:
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return True


# Function: _discover_workloads_ssh
def _discover_workloads_ssh(client) -> list[WorkloadComponent]:
    """Detect running workloads via process list + service detection."""
    workloads: list[WorkloadComponent] = []
    ps_out = _ssh_run(client, "ps aux 2>/dev/null || ps -ef 2>/dev/null")
    ss_out = _ssh_run(client, "ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null")

    _check_pattern(workloads, ps_out, "mysqld", "MySQL", "db", _get_version_from_ssh(client, "mysql --version 2>/dev/null"))
    _check_pattern(workloads, ps_out, "postgres", "PostgreSQL", "db", _get_version_from_ssh(client, "psql --version 2>/dev/null"))
    _check_pattern(workloads, ps_out, "mongod", "MongoDB", "db", _get_version_from_ssh(client, "mongod --version 2>/dev/null | head -1"))
    _check_pattern(workloads, ps_out, "oracle", "Oracle DB", "db", "")
    _check_pattern(workloads, ps_out, "nginx", "nginx", "web", _get_version_from_ssh(client, "nginx -v 2>&1 | head -1"))
    _check_pattern(workloads, ps_out, "apache2|httpd", "Apache HTTPD", "web", _get_version_from_ssh(client, "apache2 -v 2>/dev/null || httpd -v 2>/dev/null | head -1"))
    _check_pattern(workloads, ps_out, "catalina|tomcat", "ApacheTomcat", "app", "")
    _check_pattern(workloads, ps_out, "node ", "Node.js", "app", _get_version_from_ssh(client, "node --version 2>/dev/null"))
    _check_pattern(workloads, ps_out, "java ", "Java App", "app", _get_version_from_ssh(client, "java -version 2>&1 | head -1"))
    _check_pattern(workloads, ps_out, "redis-server", "Redis", "cache", _get_version_from_ssh(client, "redis-server --version 2>/dev/null"))
    _check_pattern(workloads, ps_out, "memcached", "Memcached", "cache", "")
    _check_pattern(workloads, ps_out, "rabbitmq", "RabbitMQ", "queue", "")
    _check_pattern(workloads, ps_out, "kafka", "Kafka", "queue", "")
    return workloads


# Function: _get_version_from_ssh
def _get_version_from_ssh(client, cmd: str) -> str:
    raw = _ssh_run(client, cmd)
    m = re.search(r"[\d]+\.[\d.]+", raw)
    return m.group(0) if m else ""


# Function: _check_pattern
def _check_pattern(workloads: list, text: str, pattern: str, name: str, wtype: str, version: str) -> None:
    if re.search(pattern, text, re.IGNORECASE):
        workloads.append(WorkloadComponent(name=name, version=version, component_type=wtype))


# Function: _is_local_ip
def _is_local_ip(ip: str) -> bool:
    """Return True when *ip* belongs to the machine running the scanner."""
    import socket
    if not ip:
        return False
    # Direct loopback check
    if ip in ("127.0.0.1", "::1", "localhost"):
        return True
    try:
        local_hostname = socket.gethostname()
        local_ips: set[str] = set()
        try:
            local_ips.update(socket.gethostbyname_ex(local_hostname)[2])
        except Exception:
            pass
        # getaddrinfo gives all addresses including IPv6
        try:
            for af, _st, _proto, _can, sa in socket.getaddrinfo(local_hostname, None):
                local_ips.add(sa[0])
        except Exception:
            pass
        return ip in local_ips
    except Exception:
        return False


# Function: _collect_local_machine_software
def _local_sw_record_to_software(rec: dict, _SOFTWARE_EOS: dict, _date):
    name = (rec.get("name") or "").strip()
    if not name:
        return None
    version = (rec.get("version") or "").strip()
    vendor = (rec.get("publisher") or "").strip()
    arch = (rec.get("arch") or "").strip() or ""
    install_location = (rec.get("install_location") or "").strip() or ""
    source = (rec.get("source") or "").strip()
    raw_date = rec.get("install_date") or ""
    install_date = str(raw_date) if raw_date else ""

    cat, lic = _classify_software(name.lower())
    eos = _lookup_eos_date(name, version, _SOFTWARE_EOS)
    is_eos, days = False, 0
    if eos:
        try:
            eos_d = _date.fromisoformat(eos)
            today = _date.today()
            is_eos = eos_d < today
            days = (eos_d - today).days
        except ValueError:
            pass

    return InstalledSoftware(
        name=name, version=version, vendor=vendor,
        install_date=install_date,
        category=cat, license_type=lic,
        eos_date=eos, is_eos=is_eos, days_to_eos=days,
        arch=arch, install_location=install_location, source=source,
    )


# Function: _collect_local_machine_software
def _collect_local_machine_software(ip: str) -> list[InstalledSoftware]:
    """
    When *ip* is the local machine, collect the real installed software inventory
    using the software_inventory utility (no credentials required).
    Returns a list of InstalledSoftware objects, or [] if not local / not applicable.
    """
    if not _is_local_ip(ip):
        return []

    try:
        from scanner.software_inventory import collect_inventory, dedupe_software_records  # type: ignore
        from scanner.report_builder import _SOFTWARE_EOS  # type: ignore
    except Exception:
        return []

    from datetime import date as _date

    try:
        records = collect_inventory()
        records = dedupe_software_records(records)
    except Exception as exc:
        log.debug("Local software inventory collection failed: %s", exc)
        return []

    software: list[InstalledSoftware] = []
    for rec in records:
        sw = _local_sw_record_to_software(rec, _SOFTWARE_EOS, _date)
        if sw:
            software.append(sw)

    log.info("Local machine software inventory: %d packages collected", len(software))
    return software


# Function: _infer_software_from_workloads
def _os_vendor_for(os_lower: str) -> str:
    if "windows" in os_lower:
        return "Microsoft"
    if "red hat" in os_lower:
        return "Red Hat"
    if "ubuntu" in os_lower:
        return "Canonical"
    if "debian" in os_lower:
        return "Debian"
    if "centos" in os_lower:
        return "CentOS Project"
    return "Linux"


# Function: _workload_vendor_license
def _workload_vendor_license(wl_lower: str, default_lic: str, wl_vendor_map: dict) -> tuple:
    for key, (vnd, lic_override) in wl_vendor_map.items():
        if key in wl_lower:
            return vnd, lic_override
    return "", default_lic


# Function: _infer_add_sw
def _infer_add_sw(name: str, version: str, vendor: str, cat: str, lic: str,
                   software: list, seen: set, _SOFTWARE_EOS: dict, _date) -> None:
    key = name.lower()
    if key in seen:
        return
    seen.add(key)
    eos = _lookup_eos_date(name, version, _SOFTWARE_EOS)
    is_eos_flag, days = False, 0
    if eos:
        try:
            eos_d = _date.fromisoformat(eos)
            today = _date.today()
            is_eos_flag = eos_d < today
            days = (eos_d - today).days
        except ValueError:
            pass
    software.append(InstalledSoftware(
        name=name, version=version, vendor=vendor,
        category=cat, license_type=lic,
        eos_date=eos, is_eos=is_eos_flag, days_to_eos=days,
    ))


# Function: _infer_software_from_workloads
def _infer_software_from_workloads(server: "DiscoveredServer") -> list[InstalledSoftware]:
    """
    Generate InstalledSoftware entries from already-detected workloads and OS data.
    Used as a fallback when deep scan credentials are unavailable so the software
    inventory section always has meaningful data even for credential-less scans.
    """
    from datetime import date as _date
    try:
        from scanner.report_builder import _SOFTWARE_EOS  # type: ignore
    except Exception:
        _SOFTWARE_EOS = {}

    software: list[InstalledSoftware] = []
    seen: set[str] = set()

    # ── OS entry ──────────────────────────────────────────────────────────
    if server.os_name:
        os_lower = server.os_name.lower()
        cat2 = "os"
        lic2 = "commercial" if "windows" in os_lower else "open_source"
        vendor2 = _os_vendor_for(os_lower)
        _infer_add_sw(server.os_name, server.os_version or "", vendor2, cat2, lic2,
                      software, seen, _SOFTWARE_EOS, _date)

    # ── Workload entries ──────────────────────────────────────────────────
    _WL_VENDOR_MAP: dict[str, tuple[str, str]] = {
        # workload_name_pattern → (vendor, license_type)
        "mysql":       ("Oracle Corporation", "commercial"),
        "mariadb":     ("MariaDB Corporation", "open_source"),
        "postgresql":  ("PostgreSQL Global Development Group", "open_source"),
        "mongodb":     ("MongoDB Inc.", "commercial"),
        "redis":       ("Redis Labs", "open_source"),
        "memcached":   ("Memcached Contributors", "open_source"),
        "mssql":       ("Microsoft Corporation", "commercial"),
        "oracle":      ("Oracle Corporation", "commercial"),
        "nginx":       ("NGINX Inc.", "open_source"),
        "apache":      ("Apache Software Foundation", "open_source"),
        "httpd":       ("Apache Software Foundation", "open_source"),
        "iis":         ("Microsoft Corporation", "commercial"),
        "tomcat":      ("Apache Software Foundation", "open_source"),
        "apachetomcat": ("Apache Software Foundation", "open_source"),
        "jboss":       ("Red Hat Inc.", "open_source"),
        "rabbitmq":    ("Pivotal Software", "open_source"),
        "kafka":       ("Apache Software Foundation", "open_source"),
        "elasticsearch": ("Elastic N.V.", "commercial"),
        "opensearch":  ("Amazon Web Services", "open_source"),
        "node":        ("OpenJS Foundation", "open_source"),
        "java":        ("Oracle Corporation", "open_source"),
        "docker":      ("Docker Inc.", "open_source"),
    }
    for wl in server.workloads:
        if not wl.name:
            continue
        wl_lower = wl.name.lower().replace(" ", "")
        cat3, lic3 = _classify_software(wl_lower)
        vendor3, lic3 = _workload_vendor_license(wl_lower, lic3, _WL_VENDOR_MAP)
        _infer_add_sw(wl.name, wl.version or "", vendor3, cat3, lic3,
                      software, seen, _SOFTWARE_EOS, _date)

    return software



_SOFT_CATEGORY: list[tuple[str, str]] = [
    # (keyword, category)
    ("kernel", "os"), ("libc", "os"), ("glibc", "os"), ("systemd", "os"),
    ("bash", "os"), ("coreutils", "os"), ("grub", "os"),
    ("python", "runtime"), ("java", "runtime"), ("jdk", "runtime"), ("jre", "runtime"),
    ("node", "runtime"), ("ruby", "runtime"), ("perl", "runtime"),
    ("php", "runtime"), ("golang", "runtime"), ("dotnet", "runtime"),
    ("mysql", "db"), ("postgresql", "db"), ("mongodb", "db"), ("redis", "db"),
    ("mssql", "db"), ("oracle", "db"), ("sqlite", "db"), ("mariadb", "db"),
    ("cassandra", "db"), ("elasticsearch", "db"), ("opensearch", "db"),
    ("nginx", "middleware"), ("apache", "middleware"), ("iis", "middleware"),
    ("tomcat", "middleware"), ("jetty", "middleware"), ("rabbitmq", "middleware"),
    ("kafka", "middleware"), ("activemq", "middleware"), ("haproxy", "middleware"),
    ("varnish", "middleware"), ("keycloak", "middleware"),
    ("openssl", "security"), ("openssh", "security"), ("fail2ban", "security"),
    ("iptables", "security"), ("ufw", "security"), ("nftables", "security"),
    ("crowdstrike", "security"), ("clamav", "security"), ("auditd", "security"),
    ("docker", "utility"), ("kubectl", "utility"), ("git", "utility"),
    ("curl", "utility"), ("wget", "utility"), ("vim", "utility"), ("nano", "utility"),
    ("htop", "utility"), ("rsync", "utility"), ("tar", "utility"),
]

_SOFT_OPEN_SOURCE: set[str] = {
    "bash", "curl", "git", "nginx", "apache", "mysql", "postgresql", "mongodb",
    "redis", "rabbitmq", "kafka", "docker", "kubernetes", "python", "node", "ruby",
    "perl", "php", "golang", "openssh", "openssl", "vim", "nano", "rsync",
    "htop", "tar", "coreutils", "systemd", "grub", "clamav", "fail2ban",
    "iptables", "ufw", "nftables", "mariadb", "cassandra", "elasticsearch",
    "opensearch", "haproxy", "varnish", "keycloak", "activemq", "sqlite",
    "jetty", "tomcat", "jdk", "jre", "java",
}

_SOFT_COMMERCIAL: set[str] = {
    "oracle", "mssql", "iis", "windows", "crowdstrike",
    "vmware", "cisco", "checkpoint", "symantec", "mcafee",
}


# Function: _classify_software
def _classify_software(name_lower: str) -> tuple[str, str]:
    """Return (category, license_type) for a software name."""
    category = "other"
    for kw, cat in _SOFT_CATEGORY:
        if kw in name_lower:
            category = cat
            break

    if any(kw in name_lower for kw in _SOFT_COMMERCIAL):
        license_type = "commercial"
    elif any(kw in name_lower for kw in _SOFT_OPEN_SOURCE):
        license_type = "open_source"
    else:
        license_type = "unknown"

    return category, license_type


# ─── SSH installed software discovery ─────────────────────────────────────────

# Function: _lookup_eos_date
def _eos_lookup_by_version(name_l: str, ver_clean: str, eos_table: dict) -> str:
    ver_parts = re.split(r"[\.\-]", ver_clean)
    major = ver_parts[0] if ver_parts else ""
    minor = ver_parts[1] if len(ver_parts) > 1 else ""

    candidates = []
    if major and minor:
        candidates.append(f"{name_l}-{major}.{minor}")  # 2. name-MAJOR.MINOR
    if major:
        candidates.append(f"{name_l}-{major}")  # 3. name-MAJOR
    if major and minor:
        candidates.append(f"{name_l}{major}.{minor}")  # 4. nameMAJOR.MINOR
    if major:
        candidates.append(f"{name_l}{major}")  # 5. nameMAJOR

    for key in candidates:
        hit = eos_table.get(key, "")
        if hit:
            return hit
    return ""


# Function: _eos_lookup_by_scan
def _eos_lookup_by_scan(name_l: str, eos_table: dict) -> str:
    # Table-scan for closest prefix match (slowest, last resort)
    # Match e.g. "tomcat" package → "tomcat9" table entry or "libmysqlclient" → "mysql-server"
    for key, eos_date in eos_table.items():
        if (key in name_l or name_l.startswith(key.rstrip("0123456789.-"))):
            if len(key) >= 4:     # avoid spurious single-char matches
                return eos_date
    return ""


# Function: _lookup_eos_date
def _lookup_eos_date(name: str, version: str, eos_table: dict) -> str:
    """
    Version-aware EOS date lookup. Tries multiple matching strategies:
      1. Exact package name  (e.g. "openssl3.0")
      2. name-MAJOR.MINOR   (e.g. "mysql-server" + "8.0.35" → "mysql-server-8.0")
      3. name-MAJOR         (e.g. "nodejs" + "18.20.1"  → "nodejs-18")
      4. nameMAJOR.MINOR    (e.g. "python" + "3.11.2"   → "python3.11")
      5. Prefix/suffix scan in the full EOS table for partial matches
    Returns the ISO date string or "" if not found.
    """
    if not eos_table:
        return ""
    name_l = name.lower().strip()
    ver_clean = re.sub(r"[~+].*$", "", (version or "")).strip()   # strip epoch/distro suffixes

    # 1. Exact name
    hit = eos_table.get(name_l, "")
    if hit:
        return hit

    if ver_clean:
        hit = _eos_lookup_by_version(name_l, ver_clean, eos_table)
        if hit:
            return hit

    return _eos_lookup_by_scan(name_l, eos_table)


# Function: _parse_pkg_line_to_software
def _parse_pkg_line_to_software(
    name: str, version: str, vendor: str, _SOFTWARE_EOS: dict,
    install_date: str = "",
    arch: str = "",
    install_location: str = "",
    source: str = "",
) -> "InstalledSoftware":
    """Build an InstalledSoftware object from raw package fields."""
    from datetime import date as _date
    name_lower = name.lower()
    cat, lic = _classify_software(name_lower)
    eos = _lookup_eos_date(name, version, _SOFTWARE_EOS)
    is_eos = False
    days = 0
    if eos:
        try:
            eos_d = _date.fromisoformat(eos)
            today = _date.today()
            is_eos = eos_d < today
            days = (eos_d - today).days
        except ValueError:
            pass
    return InstalledSoftware(
        name=name, version=version, vendor=vendor,
        install_date=install_date,
        category=cat, license_type=lic,
        eos_date=eos, is_eos=is_eos, days_to_eos=days,
        arch=arch, install_location=install_location, source=source,
    )


# Function: _ssh_mk_software
def _ssh_mk_software(name: str, version: str, vendor: str, cat: str, lic: str, _SOFTWARE_EOS: dict) -> "InstalledSoftware":
    from datetime import date as _d
    eos = _lookup_eos_date(name, version, _SOFTWARE_EOS)
    is_eos_f, days = False, 0
    if eos:
        try:
            eos_d = _d.fromisoformat(eos)
            today = _d.today()
            is_eos_f = eos_d < today
            days = (eos_d - today).days
        except ValueError:
            pass
    return InstalledSoftware(name=name, version=version, vendor=vendor,
                             category=cat, license_type=lic,
                             eos_date=eos, is_eos=is_eos_f, days_to_eos=days)


# Function: _collect_installed_software_ssh
def _ssh_parse_manual_pkg_line(line: str, date_fmt: str):
    """Fallback tab-split parser shared by the dpkg/rpm manual paths."""
    parts = line.split("\t")
    if len(parts) < 2:
        return None
    name = parts[0].strip()
    version = parts[1].strip() if len(parts) > 1 else ""
    vendor = parts[2].strip() if len(parts) > 2 else ""
    arch = parts[3].strip() if len(parts) > 3 else ""
    raw_date = parts[4].strip() if len(parts) > 4 else ""
    install_date = ""
    if raw_date:
        try:
            from datetime import datetime as _dt
            install_date = _dt.strptime(raw_date, date_fmt).strftime("%Y-%m-%d")
        except Exception:
            if re.match(r"\d{4}-\d{2}-\d{2}", raw_date):
                install_date = raw_date[:10]
    if not name:
        return None
    return name, version, vendor, arch, install_date


# Function: _ssh_add_pkg_record
def _ssh_add_pkg_record(rec: dict, _SOFTWARE_EOS: dict, _add, source: str) -> None:
    if not rec.get("name"):
        return
    _add(_parse_pkg_line_to_software(
        rec["name"], rec.get("version") or "",
        rec.get("publisher") or "", _SOFTWARE_EOS,
        install_date=rec.get("install_date") or "",
        arch=rec.get("arch") or "",
        source=source,
    ))


# Function: _ssh_add_manual_pkg_line
def _ssh_add_manual_pkg_line(line: str, date_fmt: str, _SOFTWARE_EOS: dict, _add, source: str) -> None:
    parsed = _ssh_parse_manual_pkg_line(line, date_fmt)
    if not parsed:
        return
    name, version, vendor, arch, install_date = parsed
    _add(_parse_pkg_line_to_software(name, version, vendor, _SOFTWARE_EOS,
                                     install_date=install_date, arch=arch, source=source))


# Function: _ssh_collect_dpkg
def _ssh_collect_dpkg(client, _SOFTWARE_EOS: dict, _add, parse_dpkg_output) -> bool:
    """Try dpkg (Debian/Ubuntu) — tab-separated, includes architecture. Returns True if dpkg was present."""
    dpkg_out = _ssh_run(
        client,
        # Use tab separator and binary:Package (handles multi-arch pkg names)
        r"dpkg-query -W -f='${binary:Package}\t${Version}\t${Maintainer}\t${Architecture}\t${db:Status-Date}\n'"
        " 2>/dev/null | head -2000"
    )
    if not dpkg_out.strip():
        return False

    if parse_dpkg_output:
        for rec in parse_dpkg_output(dpkg_out):
            _ssh_add_pkg_record(rec, _SOFTWARE_EOS, _add, "dpkg")
    else:
        # Fallback: tab-split manually
        for line in dpkg_out.splitlines():
            _ssh_add_manual_pkg_line(line, "%a %b %d %H:%M:%S %Y", _SOFTWARE_EOS, _add, "dpkg")
    return True


# Function: _ssh_collect_rpm
def _ssh_collect_rpm(client, _SOFTWARE_EOS: dict, _add, parse_rpm_output) -> bool:
    """Try rpm (RHEL/CentOS/Fedora) — tab-separated, includes architecture. Returns True if rpm was present."""
    rpm_out = _ssh_run(
        client,
        r"rpm -qa --queryformat='%{NAME}\t%{VERSION}-%{RELEASE}\t%{VENDOR}\t%{ARCH}\t%{INSTALLTIME:date}\n'"
        " 2>/dev/null | head -2000"
    )
    if not rpm_out.strip():
        return False

    if parse_rpm_output:
        for rec in parse_rpm_output(rpm_out):
            _ssh_add_pkg_record(rec, _SOFTWARE_EOS, _add, "rpm")
    else:
        for line in rpm_out.splitlines():
            _ssh_add_manual_pkg_line(line, "%a %d %b %Y %H:%M:%S %Z", _SOFTWARE_EOS, _add, "rpm")
    return True


# Function: _ssh_collect_snap
def _ssh_collect_snap(client, _add) -> None:
    """Fallback: collect snap packages when neither dpkg nor rpm is present."""
    snap_out = _ssh_run(client, "snap list 2>/dev/null | tail -n +2 | head -100")
    if not snap_out.strip():
        return
    for line in snap_out.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        name = parts[0]
        version = parts[1]
        cat, lic = _classify_software(name.lower())
        _add(InstalledSoftware(
            name=name, version=version, vendor="Canonical Snap",
            category=cat, license_type=lic, source="snap",
        ))


# Function: _collect_installed_software_ssh
def _collect_installed_software_ssh(client) -> list[InstalledSoftware]:
    """
    Collect installed packages via dpkg/rpm over SSH.
    Also detects pip, npm, gem packages, Java/Node versions, and /opt applications.
    """
    from datetime import date as _date

    # Import EOS table lazily to avoid circular imports (report_builder defines it)
    try:
        from scanner.report_builder import _SOFTWARE_EOS  # type: ignore
    except Exception:
        _SOFTWARE_EOS = {}

    software: list[InstalledSoftware] = []
    seen_keys: set[tuple] = set()   # dedup by (source, name, version, arch)

    # Function: _add
    def _add(sw: InstalledSoftware) -> None:
        key = (sw.source, sw.name.lower(), sw.version, sw.arch)
        if key not in seen_keys:
            seen_keys.add(key)
            software.append(sw)

    # Import parser helpers from the software_inventory utility module
    try:
        from scanner.software_inventory import (
            parse_dpkg_output, parse_rpm_output,
            parse_flatpak_output, parse_snap_output,
            _parse_date as _sw_parse_date,
        )  # type: ignore
    except Exception:
        parse_dpkg_output = parse_rpm_output = parse_flatpak_output = parse_snap_output = None  # type: ignore
        _sw_parse_date = None  # type: ignore

    if _ssh_collect_dpkg(client, _SOFTWARE_EOS, _add, parse_dpkg_output):
        # After dpkg, also collect additional runtime detections + flatpak
        _collect_extra_runtime_info_ssh(client, _SOFTWARE_EOS, _add)
        _collect_flatpak_apps_ssh(client, _SOFTWARE_EOS, _add)
        return software

    if _ssh_collect_rpm(client, _SOFTWARE_EOS, _add, parse_rpm_output):
        _collect_extra_runtime_info_ssh(client, _SOFTWARE_EOS, _add)
        _collect_flatpak_apps_ssh(client, _SOFTWARE_EOS, _add)
        return software

    # ── Fallback: collect whatever is detectable ───────────────────────────
    _ssh_collect_snap(client, _add)

    _collect_extra_runtime_info_ssh(client, _SOFTWARE_EOS, _add)
    _collect_flatpak_apps_ssh(client, _SOFTWARE_EOS, _add)
    return software


# Function: _collect_flatpak_apps_ssh
def _flatpak_parse_line(line: str):
    line = line.strip()
    if not line:
        return None
    parts = line.split("\t") if "\t" in line else line.split(None, 3)
    if len(parts) < 3:
        return None
    app_id = parts[0].strip()
    name = parts[1].strip() if len(parts) > 1 else app_id
    version = parts[2].strip() if len(parts) > 2 else ""
    installation = parts[3].strip() if len(parts) > 3 else ""
    return {
        "name": name or app_id, "version": version,
        "publisher": None,
        "source": f"flatpak:{installation}" if installation else "flatpak",
    }


# Function: _flatpak_parse_manual
def _flatpak_parse_manual(flatpak_out: str) -> list:
    recs = []
    lines = flatpak_out.splitlines()
    start = 1 if (lines and "Application" in lines[0]) else 0
    for line in lines[start:]:
        rec = _flatpak_parse_line(line)
        if rec:
            recs.append(rec)
    return recs


# Function: _flatpak_rec_to_software
def _flatpak_rec_to_software(rec: dict, _SOFTWARE_EOS: dict, _date):
    name = (rec.get("name") or "").strip()
    if not name:
        return None
    version = (rec.get("version") or "").strip()
    source = rec.get("source") or "flatpak"
    cat, lic = _classify_software(name.lower())
    eos = _lookup_eos_date(name, version, _SOFTWARE_EOS)
    is_eos, days = False, 0
    if eos:
        try:
            eos_d = _date.fromisoformat(eos)
            today = _date.today()
            is_eos = eos_d < today
            days = (eos_d - today).days
        except ValueError:
            pass
    return InstalledSoftware(
        name=name, version=version,
        vendor=(rec.get("publisher") or ""),
        category=cat, license_type=lic,
        eos_date=eos, is_eos=is_eos, days_to_eos=days,
        source=source,
    )


# Function: _collect_flatpak_apps_ssh
def _collect_flatpak_apps_ssh(client, _SOFTWARE_EOS: dict, _add) -> None:
    """Collect Flatpak applications from the remote host over SSH."""
    from datetime import date as _date

    flatpak_out = _ssh_run(
        client,
        "flatpak list --app --columns=application,name,version,installation 2>/dev/null"
    )
    if not flatpak_out.strip():
        return

    try:
        from scanner.software_inventory import parse_flatpak_output  # type: ignore
        recs = parse_flatpak_output(flatpak_out)
    except Exception:
        recs = _flatpak_parse_manual(flatpak_out)

    for rec in recs:
        sw = _flatpak_rec_to_software(rec, _SOFTWARE_EOS, _date)
        if sw:
            _add(sw)


# Function: _collect_extra_runtime_info_ssh
def _rt_detect_java(client, _mk, _add) -> None:
    java_ver = _ssh_run(client, "java -version 2>&1 | head -1")
    if not java_ver:
        return
    m = re.search(r'(\d+(?:\.\d+)*)', java_ver)
    if not m:
        return
    ver = m.group(1)
    is_openjdk = "openjdk" in java_ver.lower()
    vendor = "OpenJDK" if is_openjdk else "Oracle"
    _add(_mk("java", ver, vendor, "runtime", "open_source" if is_openjdk else "commercial"))


# Function: _rt_detect_node
def _rt_detect_node(client, _mk, _add) -> None:
    node_ver = _ssh_run(client, "node --version 2>/dev/null || nodejs --version 2>/dev/null")
    if not node_ver.strip():
        return
    ver = node_ver.strip().lstrip("v")
    _add(_mk("nodejs", ver, "OpenJS Foundation", "runtime", "open_source"))


# Function: _rt_detect_python
def _rt_detect_python(client, _mk, _add) -> None:
    py_ver = _ssh_run(client, "python3 --version 2>/dev/null || python --version 2>/dev/null")
    if not py_ver.strip():
        return
    m = re.search(r"(\d+\.\d+\.\d+)", py_ver)
    if m:
        _add(_mk("python3", m.group(1), "Python Software Foundation", "runtime", "open_source"))


# Function: _rt_detect_ruby
def _rt_detect_ruby(client, _mk, _add) -> None:
    ruby_ver = _ssh_run(client, "ruby --version 2>/dev/null")
    if not ruby_ver.strip():
        return
    m = re.search(r"(\d+\.\d+\.\d+)", ruby_ver)
    if m:
        _add(_mk("ruby", m.group(1), "Ruby Core Team", "runtime", "open_source"))


# Function: _rt_detect_php
def _rt_detect_php(client, _mk, _add) -> None:
    php_ver = _ssh_run(client, "php --version 2>/dev/null | head -1")
    if not php_ver.strip():
        return
    m = re.search(r"(\d+\.\d+\.\d+)", php_ver)
    if m:
        _add(_mk("php", m.group(1), "PHP Group", "runtime", "open_source"))


# Function: _rt_detect_go
def _rt_detect_go(client, _mk, _add) -> None:
    go_ver = _ssh_run(client, "go version 2>/dev/null")
    if not go_ver.strip():
        return
    m = re.search(r"go(\d+\.\d+(?:\.\d+)?)", go_ver)
    if m:
        _add(_mk("golang", m.group(1), "Google", "runtime", "open_source"))


# Function: _rt_detect_docker_version
def _rt_detect_docker_version(client, _mk, _add) -> None:
    docker_ver = _ssh_run(client, "docker --version 2>/dev/null")
    if not docker_ver.strip():
        return
    m = re.search(r"(\d+\.\d+\.\d+)", docker_ver)
    if m:
        _add(_mk("docker-ce", m.group(1), "Docker Inc.", "utility", "open_source"))


# Function: _rt_detect_tomcat
def _rt_detect_tomcat(client, _mk, _add) -> None:
    # ── Tomcat detection from common paths ────────────────────────────────
    tomcat_ver = _ssh_run(
        client,
        "find /opt /usr/share /usr/local -maxdepth 3 -name 'catalina.sh' 2>/dev/null | head -3"
    )
    if not tomcat_ver.strip():
        return
    # Try to get version from catalina.sh or RELEASE-NOTES
    ver_raw = _ssh_run(
        client,
        "cat $(find /opt /usr/share /usr/local -maxdepth 4 -name 'RELEASE-NOTES' 2>/dev/null | head -1) 2>/dev/null | grep -i 'version' | head -1"
    )
    m = re.search(r"(\d+\.\d+(?:\.\d+)?)", ver_raw or "")
    ver = m.group(1) if m else ""
    _add(_mk("tomcat", ver, "Apache Software Foundation", "middleware", "open_source"))


# Function: _rt_detect_nginx
def _rt_detect_nginx(client, _mk, _add) -> None:
    nginx_ver = _ssh_run(client, "nginx -v 2>&1 | head -1")
    if "nginx" not in nginx_ver.lower():
        return
    m = re.search(r"(\d+\.\d+\.\d+)", nginx_ver)
    _add(_mk("nginx", m.group(1) if m else "", "NGINX, Inc.", "middleware", "open_source"))


# Function: _rt_detect_apache
def _rt_detect_apache(client, _mk, _add) -> None:
    apache_ver = _ssh_run(client, "apache2 -v 2>/dev/null || httpd -v 2>/dev/null | head -1")
    if "apache" not in apache_ver.lower() and "httpd" not in apache_ver.lower():
        return
    m = re.search(r"(\d+\.\d+\.\d+)", apache_ver)
    _add(_mk("apache2", m.group(1) if m else "", "Apache Software Foundation", "middleware", "open_source"))


# Function: _rt_detect_pip_packages
def _rt_detect_pip_packages(client, _add) -> None:
    # ── pip top-level packages (only prominent ones to avoid bloat) ───────
    pip_out = _ssh_run(
        client,
        "pip3 list --format=columns 2>/dev/null | tail -n +3 | head -100 || "
        "pip list --format=columns 2>/dev/null | tail -n +3 | head -100"
    )
    if not pip_out.strip():
        return
    _NOTABLE_PIP = {
        "django", "flask", "fastapi", "uvicorn", "gunicorn", "celery",
        "sqlalchemy", "alembic", "redis", "pymongo", "psycopg2", "boto3",
        "requests", "aiohttp", "pydantic", "cryptography", "paramiko",
        "ansible", "kubernetes", "docker", "tensorflow", "torch", "numpy",
        "pandas", "scipy", "scikit-learn", "pillow", "pytest",
    }
    for line in pip_out.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        pkg_name = parts[0].lower()
        if pkg_name in _NOTABLE_PIP:
            ver = parts[1]
            cat, lic = _classify_software(pkg_name)
            _add(InstalledSoftware(name=parts[0], version=ver,
                                   vendor="PyPI", category=cat, license_type=lic))


# Function: _rt_detect_npm_packages
def _rt_detect_npm_packages(client, _add) -> None:
    # ── npm global packages ───────────────────────────────────────────────
    npm_out = _ssh_run(client, "npm list -g --depth=0 2>/dev/null | tail -n +2 | head -50")
    if not npm_out.strip():
        return
    for line in npm_out.splitlines():
        m = re.search(r"[`├└─]+ (\S+)@(\S+)", line)
        if not m:
            continue
        pkg_name, ver = m.group(1), m.group(2)
        if pkg_name in ("npm", "node"):
            continue
        cat, lic = _classify_software(pkg_name.lower())
        _add(InstalledSoftware(name=pkg_name, version=ver,
                               vendor="npm", category=cat, license_type=lic))


# Function: _collect_extra_runtime_info_ssh
def _collect_extra_runtime_info_ssh(client, _SOFTWARE_EOS: dict, _add) -> None:
    """
    Supplement package-manager data with runtime-specific version detection:
    pip packages, npm global packages, Java/Node/Ruby/Go/PHP executables,
    and manual application directories.
    """
    from datetime import date as _date

    # Function: _mk
    def _mk(name: str, version: str, vendor: str, cat: str, lic: str) -> InstalledSoftware:
        eos = _lookup_eos_date(name, version, _SOFTWARE_EOS)
        is_eos, days = False, 0
        if eos:
            try:
                eos_d = _date.fromisoformat(eos)
                today = _date.today()
                is_eos = eos_d < today
                days = (eos_d - today).days
            except ValueError:
                pass
        return InstalledSoftware(name=name, version=version, vendor=vendor,
                                 category=cat, license_type=lic,
                                 eos_date=eos, is_eos=is_eos, days_to_eos=days)

    _rt_detect_java(client, _mk, _add)
    _rt_detect_node(client, _mk, _add)
    _rt_detect_python(client, _mk, _add)
    _rt_detect_ruby(client, _mk, _add)
    _rt_detect_php(client, _mk, _add)
    _rt_detect_go(client, _mk, _add)
    _rt_detect_docker_version(client, _mk, _add)
    _rt_detect_tomcat(client, _mk, _add)
    _rt_detect_nginx(client, _mk, _add)
    _rt_detect_apache(client, _mk, _add)
    _rt_detect_pip_packages(client, _add)
    _rt_detect_npm_packages(client, _add)

    # ── Systemd service scanning — detect ALL installed application services ──
    _collect_systemd_services_ssh(client, _SOFTWARE_EOS, _add)

    # ── Running process application detection ─────────────────────────────
    _collect_process_applications_ssh(client, _SOFTWARE_EOS, _add)

    # ── /opt, /usr/local, /srv directory scanning ─────────────────────────
    _collect_opt_applications_ssh(client, _SOFTWARE_EOS, _add)

    # ── Docker containers / images ────────────────────────────────────────
    _collect_docker_applications_ssh(client, _SOFTWARE_EOS, _add)


# Function: _collect_systemd_services_ssh
def _systemd_json_entry_to_service(entry: dict):
    unit = entry.get("unit", "")
    state = entry.get("active", "")
    desc = entry.get("description", "")
    if unit and unit.endswith(".service"):
        return (unit[:-8], state, desc)
    return None


# Function: _systemd_text_line_to_service
def _systemd_text_line_to_service(line: str):
    parts = line.split()
    if not parts:
        return None
    unit = parts[0]
    if unit.endswith(".service"):
        unit = unit[:-8]
    state = parts[1] if len(parts) > 1 else ""
    desc = " ".join(parts[3:]) if len(parts) > 3 else ""
    return (unit, state, desc)


# Function: _systemd_parse_services
def _systemd_parse_services(svc_out: str, svc_desc_out: str) -> list:
    # Parse JSON output (systemd >= 230)
    services: list[tuple[str, str, str]] = []  # (unit, active_state, description)
    try:
        import json as _json
        if svc_desc_out.strip().startswith("["):
            for entry in _json.loads(svc_desc_out):
                svc = _systemd_json_entry_to_service(entry)
                if svc:
                    services.append(svc)
    except Exception:
        # Fallback: parse text output
        for line in svc_out.splitlines():
            svc = _systemd_text_line_to_service(line)
            if svc:
                services.append(svc)
    return services


# Function: _systemd_service_license
def _systemd_service_license(vendor: str) -> str:
    if vendor in (
        "Oracle Corporation", "MongoDB Inc.", "Elastic N.V.", "CrowdStrike",
        "Splunk Inc.", "IBM", "JFrog", "SonarSource",
    ):
        return "commercial"
    return "open_source"


# Function: _systemd_map_service_to_app
def _systemd_map_service_to_app(unit_lower: str, desc: str, svc_app_map: dict, _mk_sw, _add) -> None:
    for key, (app_name, cat, vendor) in svc_app_map.items():
        if key in unit_lower:
            lic = _systemd_service_license(vendor)
            # Try to extract version from unit description
            ver_m = re.search(r"(\d+\.\d+(?:\.\d+)?)", desc or "")
            ver = ver_m.group(1) if ver_m else ""
            _add(_mk_sw(app_name, ver, vendor, cat, lic))
            break


# Function: _collect_systemd_services_ssh
def _collect_systemd_services_ssh(client, _SOFTWARE_EOS: dict, _add) -> None:
    """
    Scan all installed systemd service units (not just running ones).
    This catches applications that are installed but possibly stopped.
    """
    from datetime import date as _date

    # List all enabled/installed services with their description
    svc_out = _ssh_run(
        client,
        "systemctl list-units --type=service --all --no-legend --no-pager 2>/dev/null | "
        "awk '{print $1, $2, $3, substr($0, index($0,$4))}' | head -200 ; "
        "systemctl list-unit-files --type=service --no-legend --no-pager 2>/dev/null | head -200"
    )

    # Also get service descriptions for better names
    svc_desc_out = _ssh_run(
        client,
        "systemctl list-units --type=service --all --no-legend --no-pager "
        "--output=json 2>/dev/null | head -c 32768"
    )

    services = _systemd_parse_services(svc_out, svc_desc_out)

    # Map service names to known application types
    _SVC_APP_MAP: dict[str, tuple[str, str, str]] = {
        # service_keyword → (display_name, category, vendor)
        "mysql": ("MySQL Server", "db", "Oracle Corporation"),
        "mysqld": ("MySQL Server", "db", "Oracle Corporation"),
        "mariadb": ("MariaDB Server", "db", "MariaDB Corporation"),
        "postgresql": ("PostgreSQL Server", "db", "PostgreSQL Global Development Group"),
        "mongod": ("MongoDB Server", "db", "MongoDB Inc."),
        "redis": ("Redis Server", "db", "Redis Labs"),
        "redis-server": ("Redis Server", "db", "Redis Labs"),
        "memcached": ("Memcached", "db", "Memcached Contributors"),
        "cassandra": ("Apache Cassandra", "db", "Apache Software Foundation"),
        "elasticsearch": ("Elasticsearch", "db", "Elastic N.V."),
        "opensearch": ("OpenSearch", "db", "Amazon Web Services"),
        "influxdb": ("InfluxDB", "db", "InfluxData"),
        "couchdb": ("CouchDB", "db", "Apache Software Foundation"),
        "neo4j": ("Neo4j", "db", "Neo4j Inc."),
        "nginx": ("nginx", "middleware", "NGINX Inc."),
        "apache2": ("Apache HTTP Server", "middleware", "Apache Software Foundation"),
        "httpd": ("Apache HTTP Server", "middleware", "Apache Software Foundation"),
        "lighttpd": ("Lighttpd", "middleware", "Lighttpd Project"),
        "haproxy": ("HAProxy", "middleware", "HAProxy Technologies"),
        "varnish": ("Varnish Cache", "middleware", "Varnish Software"),
        "traefik": ("Traefik", "middleware", "Containous"),
        "rabbitmq": ("RabbitMQ", "middleware", "Pivotal Software"),
        "kafka": ("Apache Kafka", "middleware", "Apache Software Foundation"),
        "activemq": ("Apache ActiveMQ", "middleware", "Apache Software Foundation"),
        "zookeeper": ("Apache ZooKeeper", "middleware", "Apache Software Foundation"),
        "keycloak": ("Keycloak", "security", "Red Hat Inc."),
        "vault": ("HashiCorp Vault", "security", "HashiCorp"),
        "consul": ("HashiCorp Consul", "middleware", "HashiCorp"),
        "jenkins": ("Jenkins", "utility", "Jenkins Project"),
        "gitlab": ("GitLab", "utility", "GitLab Inc."),
        "gitea": ("Gitea", "utility", "Gitea Project"),
        "nexus": ("Sonatype Nexus", "utility", "Sonatype"),
        "artifactory": ("JFrog Artifactory", "utility", "JFrog"),
        "sonarqube": ("SonarQube", "utility", "SonarSource"),
        "grafana": ("Grafana", "utility", "Grafana Labs"),
        "prometheus": ("Prometheus", "utility", "CNCF"),
        "node_exporter": ("Prometheus Node Exporter", "utility", "CNCF"),
        "alertmanager": ("Prometheus Alertmanager", "utility", "CNCF"),
        "kibana": ("Kibana", "utility", "Elastic N.V."),
        "logstash": ("Logstash", "utility", "Elastic N.V."),
        "filebeat": ("Filebeat", "utility", "Elastic N.V."),
        "tomcat": ("Apache Tomcat", "middleware", "Apache Software Foundation"),
        "wildfly": ("WildFly (JBoss)", "middleware", "Red Hat Inc."),
        "glassfish": ("GlassFish", "middleware", "Oracle Corporation"),
        "payara": ("Payara Server", "middleware", "Payara Services"),
        "docker": ("Docker Engine", "utility", "Docker Inc."),
        "containerd": ("containerd", "utility", "CNCF"),
        "kubelet": ("Kubernetes Node Agent", "utility", "CNCF"),
        "kube-apiserver": ("Kubernetes API Server", "utility", "CNCF"),
        "etcd": ("etcd", "utility", "CNCF"),
        "ceph": ("Ceph Storage", "utility", "Red Hat Inc."),
        "glusterfs": ("GlusterFS", "utility", "Red Hat Inc."),
        "nfs": ("NFS Server", "utility", ""),
        "samba": ("Samba", "utility", "Samba Team"),
        "vsftpd": ("vsftpd", "utility", ""),
        "postfix": ("Postfix Mail Server", "utility", ""),
        "sendmail": ("Sendmail", "utility", ""),
        "dovecot": ("Dovecot IMAP Server", "utility", ""),
        "exim": ("Exim Mail Server", "utility", ""),
        "bind9": ("BIND DNS Server", "utility", "ISC"),
        "named": ("BIND DNS Server", "utility", "ISC"),
        "dnsmasq": ("dnsmasq", "utility", ""),
        "fail2ban": ("Fail2ban", "security", ""),
        "auditd": ("Audit Daemon", "security", ""),
        "crowdstrike": ("CrowdStrike Falcon", "security", "CrowdStrike"),
        "qualys": ("Qualys Agent", "security", "Qualys"),
        "splunk": ("Splunk", "utility", "Splunk Inc."),
        "newrelic": ("New Relic Agent", "utility", "New Relic"),
        "datadog": ("Datadog Agent", "utility", "Datadog"),
        "zabbix": ("Zabbix Agent", "utility", "Zabbix LLC"),
        "nagios": ("Nagios", "utility", "Nagios Enterprises"),
        "snmpd": ("SNMP Daemon", "utility", ""),
        "puppet": ("Puppet Agent", "utility", "Puppet Inc."),
        "chef": ("Chef Client", "utility", "Progress Chef"),
        "ansible": ("Ansible", "utility", "Red Hat Inc."),
        "salt": ("Salt Minion", "utility", "SaltStack"),
        "unattended-upgrade": ("Unattended Upgrades", "utility", ""),
        "cron": ("Cron Daemon", "utility", ""),
        "atd": ("at Scheduler", "utility", ""),
        "sshd": ("OpenSSH Server", "security", "OpenSSH"),
        "ufw": ("UFW Firewall", "security", "Canonical"),
        "iptables": ("iptables Firewall", "security", ""),
        "firewalld": ("firewalld", "security", "Red Hat Inc."),
        "rsyslog": ("rsyslog", "utility", ""),
        "journald": ("systemd-journald", "utility", ""),
        "ntpd": ("NTP Daemon", "utility", ""),
        "chrony": ("Chrony NTP", "utility", ""),
        "cockpit": ("Cockpit Web Console", "utility", "Red Hat Inc."),
        "webmin": ("Webmin", "utility", "Webmin Project"),
        "tomee": ("Apache TomEE", "middleware", "Apache Software Foundation"),
        "liberty": ("IBM Liberty", "middleware", "IBM"),
        "was": ("IBM WebSphere", "middleware", "IBM"),
        "wls": ("Oracle WebLogic", "middleware", "Oracle Corporation"),
    }

    # Function: _mk_sw
    def _mk_sw(name: str, version: str, vendor: str, cat: str, lic: str) -> InstalledSoftware:
        return _ssh_mk_software(name, version, vendor, cat, lic, _SOFTWARE_EOS)

    for unit, state, desc in services:
        unit_lower = unit.lower()
        _systemd_map_service_to_app(unit_lower, desc, _SVC_APP_MAP, _mk_sw, _add)


# Function: _collect_process_applications_ssh
def _proc_pattern_scan(ps_out: str, proc_patterns: list, _SOFTWARE_EOS: dict, _add) -> None:
    for pattern, app_name, cat, vendor, lic in proc_patterns:
        if re.search(pattern, ps_out, re.IGNORECASE):
            _add(_ssh_mk_software(app_name, "", vendor, cat, lic, _SOFTWARE_EOS))


# Function: _ports_scan
def _ports_scan(ss_out: str, port_app_map: dict, _SOFTWARE_EOS: dict, _add) -> None:
    seen_ports: set[int] = set()
    for line in ss_out.splitlines():
        port_m = re.search(r":(\d{2,5})(?:\s|$)", line)
        if not port_m:
            continue
        port = int(port_m.group(1))
        if port in seen_ports or port > 65535 or port < 1:
            continue
        seen_ports.add(port)
        if port in port_app_map:
            app_name, cat, vendor, lic = port_app_map[port]
            _add(_ssh_mk_software(app_name, "", vendor, cat, lic, _SOFTWARE_EOS))


# Function: _collect_process_applications_ssh
def _collect_process_applications_ssh(client, _SOFTWARE_EOS: dict, _add) -> None:
    """
    Identify applications from running processes with full command paths.
    Detects things not visible via dpkg/rpm (custom builds, .jar files, etc.).
    """
    # Get process list with full command and binary paths
    ps_out = _ssh_run(
        client,
        "ps -eo pid,comm,args --no-header 2>/dev/null | head -300 || "
        "ps aux 2>/dev/null | head -300"
    )

    # Known process patterns → (display_name, version_cmd, category, vendor, license)
    _PROC_PATTERNS: list[tuple[str, str, str, str, str]] = [
        # (process_regex, display_name, category, vendor, license)
        (r"\bjava\b.*-jar\s+(\S+\.jar)", "Java Application", "app", "Various", "unknown"),
        (r"\bpython[23]?\b.*\s+([\w/.\-]+\.py)", "Python Application", "app", "Various", "unknown"),
        (r"\bgunicorn\b", "Gunicorn WSGI Server", "middleware", "Benoit Chesneau", "open_source"),
        (r"\buwsgi\b", "uWSGI", "middleware", "uWSGI Project", "open_source"),
        (r"\buvicorn\b", "Uvicorn ASGI Server", "middleware", "Encode", "open_source"),
        (r"\bcelery\b", "Celery Worker", "middleware", "Celery Project", "open_source"),
        (r"\bflask\b", "Flask App Server", "app", "Pallets", "open_source"),
        (r"\bdjango\b", "Django App Server", "app", "Django Project", "open_source"),
        (r"\bkafka\.Kafka\b", "Apache Kafka Broker", "middleware", "Apache", "open_source"),
        (r"\bZookeeper\b", "Apache ZooKeeper", "middleware", "Apache", "open_source"),
        (r"\bcom\.atlassian\b", "Atlassian Application", "utility", "Atlassian", "commercial"),
        (r"\bcom\.sonarqube\b", "SonarQube", "utility", "SonarSource", "commercial"),
        (r"\bjenkins\b", "Jenkins Server", "utility", "Jenkins Project", "open_source"),
        (r"\bnexus\b", "Sonatype Nexus", "utility", "Sonatype", "commercial"),
        (r"\bgrafana-server\b", "Grafana", "utility", "Grafana Labs", "open_source"),
        (r"\bprometheus\b", "Prometheus", "utility", "CNCF", "open_source"),
        (r"\bnode_exporter\b", "Prometheus Node Exporter", "utility", "CNCF", "open_source"),
        (r"\bvault\b", "HashiCorp Vault", "security", "HashiCorp", "commercial"),
        (r"\bconsul\b", "HashiCorp Consul", "middleware", "HashiCorp", "commercial"),
        (r"\bterraform\b", "HashiCorp Terraform", "utility", "HashiCorp", "commercial"),
        (r"\bpuppetd?\b", "Puppet Agent", "utility", "Puppet Inc.", "commercial"),
        (r"\bansible\b", "Ansible", "utility", "Red Hat Inc.", "open_source"),
        (r"\bsplunkd\b", "Splunk Daemon", "utility", "Splunk Inc.", "commercial"),
        (r"\bnewrelic\b", "New Relic Agent", "utility", "New Relic", "commercial"),
        (r"\bdatadogagent\b", "Datadog Agent", "utility", "Datadog", "commercial"),
        (r"\bvmtoolsd\b", "VMware Tools", "utility", "VMware", "commercial"),
        (r"\bpgbouncer\b", "PgBouncer", "db", "pgBouncer Project", "open_source"),
        (r"\bproxysql\b", "ProxySQL", "db", "ProxySQL", "open_source"),
        (r"\bmysqlrouter\b", "MySQL Router", "db", "Oracle Corporation", "commercial"),
        (r"\bfluentd\b", "Fluentd", "utility", "CNCF", "open_source"),
        (r"\bfilebeat\b", "Filebeat", "utility", "Elastic N.V.", "commercial"),
        (r"\bmetricbeat\b", "Metricbeat", "utility", "Elastic N.V.", "commercial"),
        (r"\btelegraf\b", "Telegraf", "utility", "InfluxData", "open_source"),
        (r"\bminecraft\b", "Minecraft Server", "app", "Microsoft", "commercial"),
        (r"\bfabric8\b", "Fabric8", "utility", "Fabric8", "open_source"),
    ]

    _proc_pattern_scan(ps_out, _PROC_PATTERNS, _SOFTWARE_EOS, _add)

    # ── Detect listening ports and map to applications ─────────────────────
    ss_out = _ssh_run(
        client,
        "ss -tlnp 2>/dev/null | grep LISTEN | awk '{print $4, $6}' | head -50 || "
        "netstat -tlnp 2>/dev/null | grep LISTEN | head -50"
    )
    _PORT_APP_MAP: dict[int, tuple[str, str, str, str]] = {
        # port → (app_name, category, vendor, license)
        3306: ("MySQL Server", "db", "Oracle Corporation", "commercial"),
        3307: ("MySQL Server (Alt)", "db", "Oracle Corporation", "commercial"),
        5432: ("PostgreSQL Server", "db", "PostgreSQL Global Development Group", "open_source"),
        5433: ("PostgreSQL Server (Alt)", "db", "PostgreSQL Global Development Group", "open_source"),
        27017: ("MongoDB Server", "db", "MongoDB Inc.", "commercial"),
        27018: ("MongoDB Shard", "db", "MongoDB Inc.", "commercial"),
        6379: ("Redis Server", "db", "Redis Labs", "open_source"),
        6380: ("Redis Server (TLS)", "db", "Redis Labs", "open_source"),
        11211: ("Memcached", "db", "Memcached Contributors", "open_source"),
        9200: ("Elasticsearch HTTP", "db", "Elastic N.V.", "commercial"),
        9300: ("Elasticsearch Transport", "db", "Elastic N.V.", "commercial"),
        9042: ("Apache Cassandra", "db", "Apache Software Foundation", "open_source"),
        8086: ("InfluxDB", "db", "InfluxData", "open_source"),
        5672: ("RabbitMQ AMQP", "middleware", "Pivotal Software", "open_source"),
        15672: ("RabbitMQ Management", "middleware", "Pivotal Software", "open_source"),
        9092: ("Apache Kafka", "middleware", "Apache Software Foundation", "open_source"),
        2181: ("Apache ZooKeeper", "middleware", "Apache Software Foundation", "open_source"),
        8080: ("HTTP Application Server", "middleware", "", "unknown"),
        8443: ("HTTPS Application Server", "middleware", "", "unknown"),
        8005: ("Apache Tomcat Control", "middleware", "Apache Software Foundation", "open_source"),
        8009: ("Apache Tomcat AJP", "middleware", "Apache Software Foundation", "open_source"),
        8161: ("Apache ActiveMQ", "middleware", "Apache Software Foundation", "open_source"),
        61616: ("Apache ActiveMQ STOMP", "middleware", "Apache Software Foundation", "open_source"),
        4848: ("GlassFish Admin", "middleware", "Oracle Corporation", "open_source"),
        7001: ("Oracle WebLogic", "middleware", "Oracle Corporation", "commercial"),
        9990: ("WildFly Admin", "middleware", "Red Hat Inc.", "open_source"),
        8983: ("Apache Solr", "db", "Apache Software Foundation", "open_source"),
        2375: ("Docker API (insecure)", "utility", "Docker Inc.", "open_source"),
        2376: ("Docker API (TLS)", "utility", "Docker Inc.", "open_source"),
        6443: ("Kubernetes API Server", "utility", "CNCF", "open_source"),
        2379: ("etcd Client", "utility", "CNCF", "open_source"),
        2380: ("etcd Peer", "utility", "CNCF", "open_source"),
        8500: ("HashiCorp Consul", "middleware", "HashiCorp", "commercial"),
        8200: ("HashiCorp Vault", "security", "HashiCorp", "commercial"),
        9090: ("Prometheus", "utility", "CNCF", "open_source"),
        9091: ("Prometheus Pushgateway", "utility", "CNCF", "open_source"),
        9093: ("Prometheus Alertmanager", "utility", "CNCF", "open_source"),
        3000: ("Grafana", "utility", "Grafana Labs", "open_source"),
        5601: ("Kibana", "utility", "Elastic N.V.", "commercial"),
        514: ("syslog", "utility", "", "open_source"),
        8081: ("Sonatype Nexus", "utility", "Sonatype", "commercial"),
        9000: ("SonarQube", "utility", "SonarSource", "commercial"),
        8888: ("Jupyter Notebook", "utility", "Project Jupyter", "open_source"),
        8888+1: ("JupyterHub", "utility", "Project Jupyter", "open_source"),
        5000: ("Docker Registry / Flask App", "app", "", "unknown"),
        5044: ("Logstash Beats", "utility", "Elastic N.V.", "commercial"),
        8125: ("StatsD", "utility", "", "open_source"),
        4369: ("Erlang Port Mapper (EPMD)", "utility", "", "open_source"),
        25672: ("RabbitMQ Erlang Distribution", "middleware", "Pivotal Software", "open_source"),
        1433: ("Microsoft SQL Server", "db", "Microsoft Corporation", "commercial"),
        1521: ("Oracle Database", "db", "Oracle Corporation", "commercial"),
        50000: ("IBM DB2", "db", "IBM", "commercial"),
        9600: ("Logstash Monitoring", "utility", "Elastic N.V.", "commercial"),
        7474: ("Neo4j HTTP", "db", "Neo4j Inc.", "commercial"),
        7687: ("Neo4j Bolt", "db", "Neo4j Inc.", "commercial"),
        5984: ("CouchDB", "db", "Apache Software Foundation", "open_source"),
        28017: ("MongoDB Web Interface", "db", "MongoDB Inc.", "commercial"),
        8161: ("Apache ActiveMQ Console", "middleware", "Apache Software Foundation", "open_source"),
        10050: ("Zabbix Agent", "utility", "Zabbix LLC", "open_source"),
        10051: ("Zabbix Server", "utility", "Zabbix LLC", "open_source"),
        162: ("SNMP Trap", "utility", "", "open_source"),
        4730: ("Gearman Job Server", "middleware", "", "open_source"),
        11300: ("Beanstalkd", "middleware", "", "open_source"),
        6432: ("PgBouncer", "db", "pgBouncer Project", "open_source"),
        6033: ("ProxySQL", "db", "ProxySQL", "open_source"),
    }
    _ports_scan(ss_out, _PORT_APP_MAP, _SOFTWARE_EOS, _add)


# Function: _collect_opt_applications_ssh
def _opt_dir_to_app(dir_name: str, dir_app_map: dict, _SOFTWARE_EOS: dict, _add) -> None:
    # Extract version from directory name (e.g. "apache-tomcat-9.0.70")
    ver_m = re.search(r"(\d+\.\d+(?:\.\d+)?)", dir_name)
    ver = ver_m.group(1) if ver_m else ""
    # Remove version suffix from dir name for matching
    base_name = re.sub(r"[-_]\d+.*$", "", dir_name)
    for key, (app_name, cat, vendor, lic) in dir_app_map.items():
        if key in base_name or key in dir_name:
            _add(_ssh_mk_software(app_name, ver, vendor, cat, lic, _SOFTWARE_EOS))
            break


# Function: _collect_opt_applications_ssh
def _collect_opt_applications_ssh(client, _SOFTWARE_EOS: dict, _add) -> None:
    """
    Scan common application directories (/opt, /usr/local, /srv, /app, /data)
    to find manually installed applications not tracked by package managers.
    """
    # List first-level directories under common application install paths
    dirs_out = _ssh_run(
        client,
        "ls -1d /opt/*/ /usr/local/*/  /srv/*/ /app/*/ /apps/*/ /data/*/ "
        "/home/*/app/ /var/lib/tomcat*/ /var/lib/jenkins/ /var/lib/grafana/ "
        "/var/lib/prometheus/ /var/lib/elasticsearch/ /var/lib/mongodb/ "
        "2>/dev/null | sort -u | head -80"
    )

    # Map directory name patterns to applications
    _DIR_APP_MAP: dict[str, tuple[str, str, str, str]] = {
        "tomcat": ("Apache Tomcat", "middleware", "Apache Software Foundation", "open_source"),
        "apache-tomcat": ("Apache Tomcat", "middleware", "Apache Software Foundation", "open_source"),
        "catalina": ("Apache Tomcat", "middleware", "Apache Software Foundation", "open_source"),
        "nginx": ("nginx", "middleware", "NGINX Inc.", "open_source"),
        "apache": ("Apache HTTP Server", "middleware", "Apache Software Foundation", "open_source"),
        "httpd": ("Apache HTTP Server", "middleware", "Apache Software Foundation", "open_source"),
        "jdk": ("Java Development Kit", "runtime", "Oracle Corporation", "commercial"),
        "jre": ("Java Runtime Environment", "runtime", "Oracle Corporation", "commercial"),
        "java": ("Java Runtime", "runtime", "Various", "open_source"),
        "openjdk": ("OpenJDK", "runtime", "OpenJDK", "open_source"),
        "node": ("Node.js", "runtime", "OpenJS Foundation", "open_source"),
        "nodejs": ("Node.js", "runtime", "OpenJS Foundation", "open_source"),
        "python": ("Python", "runtime", "Python Software Foundation", "open_source"),
        "ruby": ("Ruby", "runtime", "Ruby Core Team", "open_source"),
        "php": ("PHP", "runtime", "PHP Group", "open_source"),
        "go": ("Go", "runtime", "Google", "open_source"),
        "golang": ("Go", "runtime", "Google", "open_source"),
        "mysql": ("MySQL", "db", "Oracle Corporation", "commercial"),
        "mariadb": ("MariaDB", "db", "MariaDB Corporation", "open_source"),
        "postgresql": ("PostgreSQL", "db", "PostgreSQL Global Development Group", "open_source"),
        "mongodb": ("MongoDB", "db", "MongoDB Inc.", "commercial"),
        "redis": ("Redis", "db", "Redis Labs", "open_source"),
        "elasticsearch": ("Elasticsearch", "db", "Elastic N.V.", "commercial"),
        "opensearch": ("OpenSearch", "db", "Amazon Web Services", "open_source"),
        "solr": ("Apache Solr", "db", "Apache Software Foundation", "open_source"),
        "cassandra": ("Apache Cassandra", "db", "Apache Software Foundation", "open_source"),
        "kafka": ("Apache Kafka", "middleware", "Apache Software Foundation", "open_source"),
        "zookeeper": ("Apache ZooKeeper", "middleware", "Apache Software Foundation", "open_source"),
        "rabbitmq": ("RabbitMQ", "middleware", "Pivotal Software", "open_source"),
        "activemq": ("Apache ActiveMQ", "middleware", "Apache Software Foundation", "open_source"),
        "wildfly": ("WildFly", "middleware", "Red Hat Inc.", "open_source"),
        "jboss": ("JBoss", "middleware", "Red Hat Inc.", "open_source"),
        "glassfish": ("GlassFish", "middleware", "Oracle Corporation", "open_source"),
        "payara": ("Payara Server", "middleware", "Payara Services", "open_source"),
        "keycloak": ("Keycloak", "security", "Red Hat Inc.", "open_source"),
        "jenkins": ("Jenkins", "utility", "Jenkins Project", "open_source"),
        "gitlab": ("GitLab", "utility", "GitLab Inc.", "commercial"),
        "gitea": ("Gitea", "utility", "Gitea Project", "open_source"),
        "nexus": ("Sonatype Nexus", "utility", "Sonatype", "commercial"),
        "artifactory": ("JFrog Artifactory", "utility", "JFrog", "commercial"),
        "sonarqube": ("SonarQube", "utility", "SonarSource", "commercial"),
        "grafana": ("Grafana", "utility", "Grafana Labs", "open_source"),
        "prometheus": ("Prometheus", "utility", "CNCF", "open_source"),
        "kibana": ("Kibana", "utility", "Elastic N.V.", "commercial"),
        "logstash": ("Logstash", "utility", "Elastic N.V.", "commercial"),
        "splunk": ("Splunk", "utility", "Splunk Inc.", "commercial"),
        "vault": ("HashiCorp Vault", "security", "HashiCorp", "commercial"),
        "consul": ("HashiCorp Consul", "middleware", "HashiCorp", "commercial"),
        "zabbix": ("Zabbix", "utility", "Zabbix LLC", "open_source"),
        "nagios": ("Nagios", "utility", "Nagios Enterprises", "commercial"),
        "icinga": ("Icinga", "utility", "Icinga GmbH", "open_source"),
        "haproxy": ("HAProxy", "middleware", "HAProxy Technologies", "open_source"),
        "traefik": ("Traefik", "middleware", "Containous", "open_source"),
        "minio": ("MinIO Object Storage", "utility", "MinIO Inc.", "open_source"),
        "harbor": ("Harbor Registry", "utility", "CNCF", "open_source"),
        "airflow": ("Apache Airflow", "utility", "Apache Software Foundation", "open_source"),
        "spark": ("Apache Spark", "utility", "Apache Software Foundation", "open_source"),
        "hadoop": ("Apache Hadoop", "utility", "Apache Software Foundation", "open_source"),
        "hbase": ("Apache HBase", "db", "Apache Software Foundation", "open_source"),
        "hive": ("Apache Hive", "db", "Apache Software Foundation", "open_source"),
        "flink": ("Apache Flink", "utility", "Apache Software Foundation", "open_source"),
        "nifi": ("Apache NiFi", "middleware", "Apache Software Foundation", "open_source"),
        "pulsar": ("Apache Pulsar", "middleware", "Apache Software Foundation", "open_source"),
    }

    for line in dirs_out.splitlines():
        dir_name = line.strip().rstrip("/").split("/")[-1].lower()
        if not dir_name:
            continue
        _opt_dir_to_app(dir_name, _DIR_APP_MAP, _SOFTWARE_EOS, _add)


# Function: _collect_docker_applications_ssh
def _docker_process_container_line(line: str, seen_images: set, _SOFTWARE_EOS: dict, _add) -> None:
    parts = line.split("|")
    if not parts or not parts[0]:
        return
    image = parts[0].strip()
    if image in seen_images:
        return
    seen_images.add(image)

    # Parse image name and tag for version
    img_parts = image.split(":")
    img_name = img_parts[0].split("/")[-1]   # strip registry/namespace
    img_tag = img_parts[1] if len(img_parts) > 1 else ""

    ver = img_tag if img_tag and img_tag not in ("latest", "stable", "lts") else ""
    cat, lic = _classify_software(img_name.lower())
    display_name = f"{img_name} (Docker)"
    _add(_ssh_mk_software(display_name, ver, "Docker Hub / Registry", cat, lic, _SOFTWARE_EOS))


# Function: _docker_process_image_line
def _docker_process_image_line(line: str, seen_images: set, _add) -> None:
    parts = line.split("|")
    if not parts or not parts[0]:
        return
    image = parts[0].strip()
    tag = parts[1].strip() if len(parts) > 1 else ""
    full = f"{image}:{tag}"
    if full in seen_images or image in ("<none>", ""):
        return
    seen_images.add(full)
    img_name = image.split("/")[-1]
    ver = tag if tag and tag not in ("latest", "stable", "lts") else ""
    cat, lic = _classify_software(img_name.lower())
    display_name = f"{img_name} (Docker Image)"
    _add(InstalledSoftware(name=display_name, version=ver, vendor="Docker Hub / Registry",
                           category=cat, license_type=lic))


# Function: _collect_docker_applications_ssh
def _collect_docker_applications_ssh(client, _SOFTWARE_EOS: dict, _add) -> None:
    """
    Collect Docker containers and images as installed applications.
    """
    # Check if Docker is available
    docker_check = _ssh_run(client, "which docker 2>/dev/null && docker info --format '{{.ServerVersion}}' 2>/dev/null")
    if not docker_check.strip():
        return

    # List running containers
    containers_out = _ssh_run(
        client,
        "docker ps --format '{{.Image}}|{{.Names}}|{{.Status}}' 2>/dev/null | head -50"
    )

    # List all images
    images_out = _ssh_run(
        client,
        "docker images --format '{{.Repository}}|{{.Tag}}|{{.Size}}' 2>/dev/null | head -100"
    )

    seen_images: set[str] = set()

    # Process running containers (most important — these are running apps)
    for line in containers_out.splitlines():
        _docker_process_container_line(line, seen_images, _SOFTWARE_EOS, _add)

    # Also list local images (may be installed but not yet running)
    for line in images_out.splitlines():
        _docker_process_image_line(line, seen_images, _add)




# ─── WinRM software discovery ─────────────────────────────────────────────────

# Function: _winrm_json_items
def _winrm_json_items(raw: str) -> list:
    """Parse a WinRM ConvertTo-Json response into a normalized list of dicts."""
    import json as _json

    if not raw or raw == "null":
        return []
    items = _json.loads(raw)
    if isinstance(items, dict):
        items = [items]
    return items or []


# Function: _winrm_parse_registry_item
def _winrm_parse_registry_item(item: dict, arch_label: str, _add) -> None:
    name = (item.get("DisplayName") or "").strip()
    version = (item.get("DisplayVersion") or "").strip()
    vendor = (item.get("Publisher") or "").strip()
    raw_date = str(item.get("InstallDate") or "").strip()
    install_location = (item.get("InstallLocation") or "").strip()
    # InstallDate format: "20240115" → "2024-01-15"
    install_date = ""
    if raw_date and re.match(r"^\d{8}$", raw_date):
        install_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
    elif raw_date and re.match(r"\d{4}-\d{2}-\d{2}", raw_date):
        install_date = raw_date[:10]
    _add(name, version, vendor,
         install_date=install_date,
         arch=arch_label,
         install_location=install_location,
         source="registry_uninstall")


# Function: _winrm_sw_registry
def _winrm_sw_registry(s, _add) -> None:
    _reg_hive_queries = [
        (r"HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*", "x64_or_native"),
        (r"HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*", "x86"),
        (r"HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*", "x64_or_native"),
    ]
    for reg_path, arch_label in _reg_hive_queries:
        try:
            reg_result = s.run_ps(
                f"$p = '{reg_path}';"
                "$apps = Get-ItemProperty $p -ErrorAction SilentlyContinue |"
                "  Where-Object { $_.DisplayName -and $_.DisplayName -notmatch '^\\s*$' } |"
                "  Select-Object DisplayName, DisplayVersion, Publisher, InstallDate,"
                "                InstallLocation, UninstallString, QuietUninstallString;"
                "$apps | ConvertTo-Json -Depth 2"
            )
            if reg_result.status_code == 0 and reg_result.std_out:
                raw = reg_result.std_out.decode("utf-8", errors="replace").strip()
                for item in _winrm_json_items(raw):
                    _winrm_parse_registry_item(item, arch_label, _add)
        except Exception as exc:
            log.debug("WinRM registry query for %s failed: %s", reg_path, exc)


# Function: _winrm_sw_get_package
def _winrm_sw_get_package(s, _add) -> None:
    try:
        pkg_result = s.run_ps(
            "Get-Package -ErrorAction SilentlyContinue |"
            " Select-Object Name, Version, ProviderName |"
            " ConvertTo-Json -Depth 2"
        )
        if pkg_result.status_code == 0 and pkg_result.std_out:
            raw = pkg_result.std_out.decode("utf-8", errors="replace").strip()
            for item in _winrm_json_items(raw):
                name = (item.get("Name") or "").strip()
                version = (item.get("Version") or "").strip()
                vendor = (item.get("ProviderName") or "").strip()
                _add(name, version, vendor, source="get_package")
    except Exception as exc:
        log.debug("WinRM Get-Package failed: %s", exc)


# Function: _winrm_map_service_to_app
def _winrm_map_service_to_app(svc_name: str, disp_name: str, svc_map: dict, _add) -> None:
    for key, (app_name, cat, vendor) in svc_map.items():
        if key in svc_name:
            m = re.search(r"(\d{4}|\d+\.\d+)", disp_name)
            ver = m.group(1) if m else ""
            _add(app_name, ver, vendor, source="windows_service")
            break


# Function: _winrm_sw_services
def _winrm_sw_services(s, _add) -> None:
    try:
        svc_result = s.run_ps(
            "Get-Service | Select-Object Name, DisplayName, Status |"
            " ConvertTo-Json -Depth 1"
        )
        if svc_result.status_code == 0 and svc_result.std_out:
            raw = svc_result.std_out.decode("utf-8", errors="replace").strip()
            svc_items = _winrm_json_items(raw)
            # Comprehensive service → application mapping
            _WIN_SVC_MAP: dict[str, tuple[str, str, str]] = {
                # service_key → (app_name, category, vendor)
                "mssqlserver": ("Microsoft SQL Server", "db", "Microsoft Corporation"),
                "mssql$": ("Microsoft SQL Server", "db", "Microsoft Corporation"),
                "sqlbrowser": ("SQL Server Browser", "db", "Microsoft Corporation"),
                "sqlagent": ("SQL Server Agent", "db", "Microsoft Corporation"),
                "sqlserveragent": ("SQL Server Agent", "db", "Microsoft Corporation"),
                "mysql": ("MySQL Server", "db", "Oracle Corporation"),
                "mysql57": ("MySQL Server 5.7", "db", "Oracle Corporation"),
                "mysql80": ("MySQL Server 8.0", "db", "Oracle Corporation"),
                "postgresql": ("PostgreSQL Server", "db", "PostgreSQL Global Development Group"),
                "pgsql": ("PostgreSQL Server", "db", "PostgreSQL Global Development Group"),
                "mongodb": ("MongoDB Server", "db", "MongoDB Inc."),
                "w3svc": ("IIS Web Server", "middleware", "Microsoft Corporation"),
                "was": ("IIS Windows Process Activation", "middleware", "Microsoft Corporation"),
                "iisadmin": ("IIS Admin Service", "middleware", "Microsoft Corporation"),
                "tomcat": ("Apache Tomcat", "middleware", "Apache Software Foundation"),
                "catalina": ("Apache Tomcat", "middleware", "Apache Software Foundation"),
                "redis": ("Redis Cache Server", "db", "Redis Labs"),
                "redis-server": ("Redis Cache Server", "db", "Redis Labs"),
                "rabbitmq": ("RabbitMQ", "middleware", "Pivotal Software"),
                "elasticsearch-service": ("Elasticsearch", "db", "Elastic N.V."),
                "elasticsearch": ("Elasticsearch", "db", "Elastic N.V."),
                "kibana": ("Kibana", "utility", "Elastic N.V."),
                "logstash": ("Logstash", "utility", "Elastic N.V."),
                "jenkins": ("Jenkins", "utility", "Jenkins Project"),
                "sonarqube": ("SonarQube", "utility", "SonarSource"),
                "sonar": ("SonarQube", "utility", "SonarSource"),
                "nexusrepo": ("Sonatype Nexus", "utility", "Sonatype"),
                "grafana": ("Grafana", "utility", "Grafana Labs"),
                "prometheus": ("Prometheus", "utility", "CNCF"),
                "vault": ("HashiCorp Vault", "security", "HashiCorp"),
                "consul": ("HashiCorp Consul", "middleware", "HashiCorp"),
                "docker": ("Docker Desktop / Engine", "utility", "Docker Inc."),
                "com.docker": ("Docker", "utility", "Docker Inc."),
                "dockerdesktop": ("Docker Desktop", "utility", "Docker Inc."),
                "splunkd": ("Splunk", "utility", "Splunk Inc."),
                "splunkforwarder": ("Splunk Universal Forwarder", "utility", "Splunk Inc."),
                "datadogagent": ("Datadog Agent", "utility", "Datadog"),
                "newrelic": ("New Relic .NET Agent", "utility", "New Relic"),
                "zabbix": ("Zabbix Agent", "utility", "Zabbix LLC"),
                "nsclient": ("NSClient++ (Nagios)", "utility", "NSClient"),
                "puppet": ("Puppet Agent", "utility", "Puppet Inc."),
                "chef": ("Chef Client", "utility", "Progress Chef"),
                "saltminion": ("Salt Minion", "utility", "SaltStack"),
                "crowdstrike": ("CrowdStrike Falcon", "security", "CrowdStrike"),
                "qualysagent": ("Qualys Cloud Agent", "security", "Qualys"),
                "taniumclient": ("Tanium Client", "security", "Tanium"),
                "carbonblack": ("Carbon Black", "security", "VMware Carbon Black"),
                "cylance": ("Cylance PROTECT", "security", "Cylance"),
                "mcafee": ("McAfee / Trellix", "security", "Trellix"),
                "symantec": ("Symantec Endpoint", "security", "Symantec"),
                "defender": ("Microsoft Defender", "security", "Microsoft Corporation"),
                "sense": ("Microsoft Defender ATP Sense", "security", "Microsoft Corporation"),
                "msiserver": ("Windows Installer", "utility", "Microsoft Corporation"),
                "winrm": ("Windows Remote Management", "utility", "Microsoft Corporation"),
                "wsman": ("WS-Management", "utility", "Microsoft Corporation"),
                "bits": ("Background Intelligent Transfer Service", "utility", "Microsoft Corporation"),
                "wuauserv": ("Windows Update", "utility", "Microsoft Corporation"),
                "termservice": ("Remote Desktop Services", "utility", "Microsoft Corporation"),
                "rdserver": ("Remote Desktop Session Host", "utility", "Microsoft Corporation"),
                "dhcp": ("DHCP Server", "utility", "Microsoft Corporation"),
                "dns": ("DNS Server", "utility", "Microsoft Corporation"),
                "adws": ("Active Directory Web Services", "utility", "Microsoft Corporation"),
                "ntds": ("Active Directory Domain Services", "utility", "Microsoft Corporation"),
                "netlogon": ("Netlogon", "utility", "Microsoft Corporation"),
                "iis": ("Internet Information Services", "middleware", "Microsoft Corporation"),
                "aspnet": ("ASP.NET", "runtime", "Microsoft Corporation"),
                "dotnet": (".NET Runtime", "runtime", "Microsoft Corporation"),
                "dotnetclr": (".NET CLR", "runtime", "Microsoft Corporation"),
                "oracleservice": ("Oracle Database", "db", "Oracle Corporation"),
                "oraclevss": ("Oracle VSS Writer", "db", "Oracle Corporation"),
                "ibmdb2": ("IBM DB2", "db", "IBM"),
                "postgresql": ("PostgreSQL", "db", "PostgreSQL Global Development Group"),
                "activerecord": ("ActiveRecord App", "app", "Various"),
                "wsusservice": ("Windows Server Update Services", "utility", "Microsoft Corporation"),
                "sccm": ("Microsoft SCCM / Endpoint Config Manager", "utility", "Microsoft Corporation"),
                "ccmexec": ("Microsoft SCCM Client", "utility", "Microsoft Corporation"),
                "kafka": ("Apache Kafka", "middleware", "Apache Software Foundation"),
                "zookeeper": ("Apache ZooKeeper", "middleware", "Apache Software Foundation"),
                "activemq": ("Apache ActiveMQ", "middleware", "Apache Software Foundation"),
                "nats": ("NATS Server", "middleware", "Synadia"),
                "ftp": ("IIS FTP Service", "utility", "Microsoft Corporation"),
                "smtp": ("SMTP Service", "utility", "Microsoft Corporation"),
                "pop3svc": ("POP3 Service", "utility", "Microsoft Corporation"),
                "imap4svc": ("IMAP4 Service", "utility", "Microsoft Corporation"),
            }
            for svc in svc_items:
                svc_name = (svc.get("Name") or "").lower()
                disp_name = (svc.get("DisplayName") or "").strip()
                _winrm_map_service_to_app(svc_name, disp_name, _WIN_SVC_MAP, _add)
    except Exception as exc:
        log.debug("WinRM service scan failed: %s", exc)


# Function: _winrm_sw_features
def _winrm_map_feature_to_app(name_raw: str, feat_map: dict, _add) -> None:
    for key, (app_name, cat, vendor) in feat_map.items():
        if key in name_raw:
            _add(app_name, "", vendor, source="windows_feature")
            break


# Function: _winrm_sw_features
def _winrm_sw_features(s, _add) -> None:
    try:
        feat_result = s.run_ps(
            "try {"
            "  Import-Module ServerManager -ErrorAction Stop;"
            "  Get-WindowsFeature | Where-Object { $_.Installed -eq $true } |"
            "  Select-Object Name, DisplayName |"
            "  ConvertTo-Json -Depth 1"
            "} catch {"
            "  # Non-server: list Windows optional features"
            "  Get-WindowsOptionalFeature -Online -ErrorAction SilentlyContinue |"
            "  Where-Object { $_.State -eq 'Enabled' } |"
            "  Select-Object FeatureName |"
            "  ConvertTo-Json -Depth 1"
            "}"
        )
        if feat_result.status_code == 0 and feat_result.std_out:
            raw = feat_result.std_out.decode("utf-8", errors="replace").strip()
            feat_items = _winrm_json_items(raw)
            if feat_items:
                _FEAT_MAP: dict[str, tuple[str, str, str]] = {
                    "web-server": ("IIS Web Server", "middleware", "Microsoft Corporation"),
                    "web-webserver": ("IIS Web Server", "middleware", "Microsoft Corporation"),
                    "web-asp": ("ASP on IIS", "runtime", "Microsoft Corporation"),
                    "web-asp-net": ("ASP.NET on IIS", "runtime", "Microsoft Corporation"),
                    "web-asp-net45": ("ASP.NET 4.5 on IIS", "runtime", "Microsoft Corporation"),
                    "web-ftp-server": ("IIS FTP Server", "utility", "Microsoft Corporation"),
                    "web-websockets": ("IIS WebSocket Protocol", "middleware", "Microsoft Corporation"),
                    "net-framework": (".NET Framework", "runtime", "Microsoft Corporation"),
                    "net-framework-45": (".NET Framework 4.5", "runtime", "Microsoft Corporation"),
                    "net-framework-core": (".NET Framework Core", "runtime", "Microsoft Corporation"),
                    "rds-rd-server": ("Remote Desktop Session Host", "utility", "Microsoft Corporation"),
                    "rds-gateway": ("Remote Desktop Gateway", "utility", "Microsoft Corporation"),
                    "rds-connection-broker": ("Remote Desktop Connection Broker", "utility", "Microsoft Corporation"),
                    "ad-domain-services": ("Active Directory Domain Services", "utility", "Microsoft Corporation"),
                    "dns": ("DNS Server", "utility", "Microsoft Corporation"),
                    "dhcp": ("DHCP Server", "utility", "Microsoft Corporation"),
                    "file-services": ("File Services", "utility", "Microsoft Corporation"),
                    "fs-fileserver": ("File Server", "utility", "Microsoft Corporation"),
                    "fs-dfs": ("Distributed File System", "utility", "Microsoft Corporation"),
                    "print-services": ("Print Services", "utility", "Microsoft Corporation"),
                    "msmq": ("Message Queuing (MSMQ)", "middleware", "Microsoft Corporation"),
                    "windows-server-backup": ("Windows Server Backup", "utility", "Microsoft Corporation"),
                    "failover-clustering": ("Failover Clustering", "utility", "Microsoft Corporation"),
                    "hyper-v": ("Hyper-V", "utility", "Microsoft Corporation"),
                    "containers": ("Windows Containers", "utility", "Microsoft Corporation"),
                    "powershell-v2": ("PowerShell 2.0 Engine", "runtime", "Microsoft Corporation"),
                    "telnet-client": ("Telnet Client", "utility", "Microsoft Corporation"),
                    "smtp-server": ("SMTP Server", "utility", "Microsoft Corporation"),
                }
                for feat in feat_items:
                    name_raw = (feat.get("Name") or feat.get("FeatureName") or "").lower()
                    disp = (feat.get("DisplayName") or "").strip()
                    _winrm_map_feature_to_app(name_raw, _FEAT_MAP, _add)
    except Exception as exc:
        log.debug("WinRM Windows features scan failed: %s", exc)


# Function: _winrm_sw_iis_sites
def _winrm_sw_iis_sites(s, _add) -> None:
    try:
        iis_result = s.run_ps(
            "Import-Module WebAdministration -ErrorAction SilentlyContinue;"
            "Get-Website -ErrorAction SilentlyContinue |"
            " Select-Object Name, State, PhysicalPath, @{n='Binding';e={($_.Bindings.Collection | ForEach-Object { $_.bindingInformation }) -join ','}} |"
            " ConvertTo-Json -Depth 2"
        )
        if iis_result.status_code == 0 and iis_result.std_out:
            raw = iis_result.std_out.decode("utf-8", errors="replace").strip()
            for site in _winrm_json_items(raw):
                site_name = (site.get("Name") or "").strip()
                if site_name:
                    _add(f"IIS Site: {site_name}", "", "Microsoft Corporation", source="iis_site")
    except Exception as exc:
        log.debug("WinRM IIS sites scan failed: %s", exc)


# Function: _winrm_sw_chocolatey
def _winrm_sw_chocolatey(s, _add) -> None:
    try:
        choco_result = s.run_ps(
            "if (Get-Command choco -ErrorAction SilentlyContinue) {"
            "  choco list --local-only --limit-output 2>$null | ForEach-Object {"
            "    $p = $_ -split '\\|'; if ($p.Count -ge 2) {"
            "      [PSCustomObject]@{Name=$p[0]; Version=$p[1]}"
            "    }"
            "  } | ConvertTo-Json -Depth 1"
            "}"
        )
        if choco_result.status_code == 0 and choco_result.std_out:
            raw = choco_result.std_out.decode("utf-8", errors="replace").strip()
            for item in _winrm_json_items(raw):
                name = (item.get("Name") or "").strip()
                version = (item.get("Version") or "").strip()
                if name:
                    _add(name, version, "Chocolatey", source="chocolatey")
    except Exception as exc:
        log.debug("WinRM Chocolatey scan failed: %s", exc)


# Function: _winrm_sw_winget
def _winrm_sw_winget(s, _add) -> None:
    try:
        winget_result = s.run_ps(
            "if (Get-Command winget -ErrorAction SilentlyContinue) {"
            "  winget list --accept-source-agreements 2>$null |"
            "  Select-Object -Skip 2 |"
            "  ConvertFrom-Csv -Delimiter '`t' -Header Name,Id,Version,Available,Source |"
            "  Where-Object { $_.Name } |"
            "  Select-Object Name,Version,Source |"
            "  ConvertTo-Json -Depth 1"
            "}"
        )
        if winget_result.status_code == 0 and winget_result.std_out:
            raw = winget_result.std_out.decode("utf-8", errors="replace").strip()
            for item in _winrm_json_items(raw):
                name = (item.get("Name") or "").strip()
                version = (item.get("Version") or "").strip()
                if name:
                    _add(name, version, "winget", source="winget")
    except Exception as exc:
        log.debug("WinRM winget scan failed: %s", exc)


# Function: _winrm_sw_dotnet
def _winrm_sw_dotnet(s, _add) -> None:
    try:
        dotnet_result = s.run_ps(
            "& dotnet --list-runtimes 2>$null | ForEach-Object {"
            "  if ($_ -match '(\\S+)\\s+(\\d+\\.\\d+\\.\\d+)') {"
            "    [PSCustomObject]@{Name=$Matches[1]; Version=$Matches[2]}"
            "  }"
            "} | ConvertTo-Json -Depth 1"
        )
        if dotnet_result.status_code == 0 and dotnet_result.std_out:
            raw = dotnet_result.std_out.decode("utf-8", errors="replace").strip()
            for item in _winrm_json_items(raw):
                name = (item.get("Name") or "").strip()
                ver = (item.get("Version") or "").strip()
                if name:
                    _add(f".NET Runtime ({name})", ver, "Microsoft Corporation", source="dotnet_runtime")
    except Exception as exc:
        log.debug("WinRM .NET runtimes scan failed: %s", exc)


# Function: _winrm_add_java_item
def _winrm_add_java_item(item: dict, _add) -> None:
    vendor_raw = (item.get("Vendor") or "Java").strip()
    ver = (item.get("Version") or "").strip()
    vendor_map = {
        "Java Runtime Environment": "Oracle Corporation",
        "Java Development Kit": "Oracle Corporation",
        "JRE": "Oracle Corporation",
        "JDK": "Oracle Corporation",
        "Eclipse Adoptium": "Eclipse Adoptium (Temurin)",
        "Eclipse Foundation": "Eclipse Foundation",
        "Semeru": "IBM Semeru",
    }
    vendor = vendor_map.get(vendor_raw, vendor_raw)
    if ver:
        _add(f"Java ({vendor_raw})", ver, vendor, source="java_registry")


# Function: _winrm_sw_java
def _winrm_sw_java(s, _add) -> None:
    try:
        java_result = s.run_ps(
            "$javaPaths = @();"
            "# Check registry for JDK/JRE"
            "('HKLM:\\SOFTWARE\\JavaSoft\\Java Runtime Environment',"
            " 'HKLM:\\SOFTWARE\\JavaSoft\\Java Development Kit',"
            " 'HKLM:\\SOFTWARE\\JavaSoft\\JRE',"
            " 'HKLM:\\SOFTWARE\\JavaSoft\\JDK',"
            " 'HKLM:\\SOFTWARE\\Eclipse Adoptium\\JRE',"
            " 'HKLM:\\SOFTWARE\\Eclipse Adoptium\\JDK',"
            " 'HKLM:\\SOFTWARE\\Eclipse Foundation\\JDK',"
            " 'HKLM:\\SOFTWARE\\Semeru\\JRE',"
            " 'HKLM:\\SOFTWARE\\Semeru\\JDK') | ForEach-Object {"
            "  if (Test-Path $_) {"
            "    Get-ChildItem $_ | ForEach-Object {"
            "      [PSCustomObject]@{Vendor=(Split-Path $_.PSParentPath -Leaf); Version=$_.PSChildName}"
            "    }"
            "  }"
            "} | ConvertTo-Json -Depth 2"
        )
        if java_result.status_code == 0 and java_result.std_out:
            raw = java_result.std_out.decode("utf-8", errors="replace").strip()
            for item in _winrm_json_items(raw):
                _winrm_add_java_item(item, _add)
    except Exception as exc:
        log.debug("WinRM Java scan failed: %s", exc)


# Function: _collect_installed_software_winrm
def _collect_installed_software_winrm(s) -> list[InstalledSoftware]:
    """
    Collect installed software via WinRM.
    Uses Windows Registry (fast) as primary source,
    with Get-Package and Win32_Product as fallbacks.
    """
    from datetime import date as _date

    try:
        from scanner.report_builder import _SOFTWARE_EOS  # type: ignore
    except Exception:
        _SOFTWARE_EOS = {}

    software: list[InstalledSoftware] = []
    seen_keys: set[tuple] = set()

    # Function: _add
    def _add(name: str, version: str, vendor: str, install_date: str = "",
             arch: str = "", install_location: str = "", source: str = "registry_uninstall") -> None:
        key = (source, name.lower(), version, arch)
        if key in seen_keys or not name.strip():
            return
        seen_keys.add(key)
        software.append(_parse_pkg_line_to_software(
            name, version, vendor, _SOFTWARE_EOS,
            install_date=install_date, arch=arch,
            install_location=install_location, source=source,
        ))

    # ── Primary: Registry-based enumeration (HKLM x64, HKLM x86, HKCU) ───
    _winrm_sw_registry(s, _add)

    # ── Supplement with Get-Package (Chocolatey, MSI, etc.) ───────────────
    if len(software) < 10:    # registry returned nothing, try alternative
        _winrm_sw_get_package(s, _add)

    # ── Comprehensive Windows service scan (all services, not just running) ─
    _winrm_sw_services(s, _add)

    # ── Windows Features / Roles (IIS, .NET, RSAT, etc.) ─────────────────
    _winrm_sw_features(s, _add)

    # ── IIS website enumeration ───────────────────────────────────────────
    _winrm_sw_iis_sites(s, _add)

    # ── Chocolatey packages ───────────────────────────────────────────────
    _winrm_sw_chocolatey(s, _add)

    # ── winget packages ───────────────────────────────────────────────────
    _winrm_sw_winget(s, _add)

    # ── Detect .NET runtimes installed ────────────────────────────────────
    _winrm_sw_dotnet(s, _add)

    # ── Detect Java installations (JDK/JRE) ───────────────────────────────
    _winrm_sw_java(s, _add)

    return software


# ─── WinRM discovery ───────────────────────────────────────────────────────────

# Function: _winrm_available
def _winrm_available() -> bool:
    try:
        import winrm  # noqa: F401
        return True
    except ImportError:
        return False


# Function: _winrm_parse_network_interfaces
def _winrm_net_normalize_raw(nd: dict) -> tuple:
    adapters_raw = nd.get("adapters") or []
    configs_raw  = nd.get("configs") or []
    assoc_raw    = nd.get("assoc") or []
    vlans_raw    = nd.get("vlans") or []
    physical_raw = nd.get("physical") or []

    if isinstance(adapters_raw, dict):
        adapters_raw = [adapters_raw]
    if isinstance(configs_raw, dict):
        configs_raw = [configs_raw]
    if isinstance(assoc_raw, dict):
        assoc_raw = [assoc_raw]
    if isinstance(vlans_raw, dict):
        vlans_raw = [vlans_raw]
    if isinstance(physical_raw, dict):
        physical_raw = [physical_raw]
    return adapters_raw, configs_raw, assoc_raw, vlans_raw, physical_raw


# Function: _winrm_net_wmi_maps
def _winrm_net_wmi_maps(physical_raw: list) -> tuple:
    _wmi_speed: dict[str, int] = {}
    _wmi_mac: dict[str, str] = {}
    for p in physical_raw:
        conn = p.get("NetConnectionID") or p.get("Name") or ""
        spd_raw = p.get("Speed")
        if conn and spd_raw:
            try:
                _wmi_speed[conn] = int(spd_raw)
            except (ValueError, TypeError):
                pass
        mac_r = (p.get("MACAddress") or "").replace("-", ":").lower().strip()
        if conn and mac_r and mac_r not in ("ff:ff:ff:ff:ff:ff", "00:00:00:00:00:00"):
            _wmi_mac[conn] = mac_r
    return _wmi_speed, _wmi_mac


# Function: _winrm_net_vlan_map
def _winrm_net_vlan_map(vlans_raw: list) -> dict:
    _vlan_by_name: dict[str, str] = {}
    for v in vlans_raw:
        vn = v.get("Name", "")
        vv = v.get("RegistryValue")
        if vn and vv is not None:
            _vlan_by_name[vn] = str(vv[0] if isinstance(vv, list) else vv)
    return _vlan_by_name


# Function: _winrm_extract_gateway_ip
def _winrm_extract_gateway_ip(gw_obj) -> str:
    if not gw_obj:
        return ""
    if isinstance(gw_obj, list):
        gw_obj = gw_obj[0] if gw_obj else {}
    if isinstance(gw_obj, dict):
        return gw_obj.get("NextHop") or ""
    return str(gw_obj)


# Function: _winrm_net_gateway_map
def _winrm_net_gateway_map(configs_raw: list) -> dict:
    _gw_by_alias: dict[str, str] = {}
    for c in configs_raw:
        alias = c.get("InterfaceAlias", "")
        gw_ip = _winrm_extract_gateway_ip(c.get("IPv4DefaultGateway"))
        if gw_ip:
            _gw_by_alias[alias] = gw_ip
    return _gw_by_alias


# Function: _winrm_net_prefix_map
def _winrm_net_prefix_map(assoc_raw: list) -> dict:
    _prefix_by_alias: dict[str, int] = {}
    for a in assoc_raw:
        alias = a.get("InterfaceAlias", "")
        pfx = a.get("PrefixLength", 24)
        if alias:
            _prefix_by_alias[alias] = int(pfx)
    return _prefix_by_alias


# Function: _winrm_net_duplex_str
def _winrm_net_duplex_str(a_duplex) -> str:
    if a_duplex is True or a_duplex == "True":
        return "full"
    if a_duplex is False or a_duplex == "False":
        return "half"
    return ""


# Function: _winrm_net_link_state
def _winrm_net_link_state(a_mcs: str, a_status: str) -> str:
    if "connected" in a_mcs:
        return "up"
    if "disconnected" in a_mcs or "notpresent" in a_mcs:
        return "down"
    if a_status == "up":
        return "up"
    if a_status in ("disconnected", "notpresent"):
        return "down"
    return ""


# Function: _winrm_ip4_from_assoc
def _winrm_ip4_from_assoc(a_name: str, assoc_raw: list) -> str:
    for a in assoc_raw:
        if a.get("InterfaceAlias") == a_name:
            return a.get("IPAddress", "") or ""
    return ""


# Function: _winrm_ip4_from_config
def _winrm_ip4_from_config(a_name: str, configs_raw: list) -> str:
    for c in configs_raw:
        if c.get("InterfaceAlias") != a_name:
            continue
        ip4_obj = c.get("IPv4Address")
        if not ip4_obj:
            return ""
        if isinstance(ip4_obj, list):
            ip4_obj = ip4_obj[0] if ip4_obj else {}
        if isinstance(ip4_obj, dict):
            return ip4_obj.get("IPAddress") or ""
        return str(ip4_obj)
    return ""


# Function: _winrm_net_find_ip4
def _winrm_net_find_ip4(a_name: str, assoc_raw: list, configs_raw: list) -> str:
    ip4 = _winrm_ip4_from_assoc(a_name, assoc_raw)
    if ip4:
        return ip4
    return _winrm_ip4_from_config(a_name, configs_raw)


# Function: _winrm_net_speed_mbps
def _winrm_net_speed_mbps(a_speed, a_name: str, wmi_speed: dict) -> int:
    speed_mbps = 0
    if isinstance(a_speed, str):
        sp_m = re.search(r'([\d.]+)\s*(Gbps|Mbps|bps)', a_speed, re.IGNORECASE)
        if sp_m:
            val = float(sp_m.group(1))
            unit = sp_m.group(2).lower()
            if "gbps" in unit:
                speed_mbps = int(val * 1000)
            elif "mbps" in unit:
                speed_mbps = int(val)
    elif isinstance(a_speed, (int, float)):
        speed_mbps = int(a_speed // 1_000_000) if a_speed > 10_000 else int(a_speed)
    if not speed_mbps and a_name in wmi_speed:
        speed_mbps = wmi_speed[a_name] // 1_000_000
    return speed_mbps


# Function: _winrm_process_adapter
def _winrm_process_adapter(server: DiscoveredServer, adap: dict, assoc_raw: list, configs_raw: list,
                            wmi_speed: dict, wmi_mac: dict, vlan_by_name: dict,
                            gw_by_alias: dict, prefix_by_alias: dict) -> None:
    a_name     = adap.get("Name", "")
    a_mac_raw  = adap.get("MacAddress", "") or wmi_mac.get(a_name, "")
    a_speed    = adap.get("LinkSpeed") or ""
    a_status   = (adap.get("Status") or "").lower()
    a_duplex   = adap.get("FullDuplex")
    a_mcs      = (adap.get("MediaConnectionState") or "").lower()

    if a_status not in ("up", "disconnected", "notpresent", "2", ""):
        pass
    mac_norm = a_mac_raw.replace("-", ":").lower().strip()

    duplex_str = _winrm_net_duplex_str(a_duplex)
    link_state_str = _winrm_net_link_state(a_mcs, a_status)
    ip4 = _winrm_net_find_ip4(a_name, assoc_raw, configs_raw)
    speed_mbps = _winrm_net_speed_mbps(a_speed, a_name, wmi_speed)

    if not ip4:
        if mac_norm and mac_norm not in ("ff:ff:ff:ff:ff:ff", "00:00:00:00:00:00"):
            server.interfaces.append(NetworkInterface(
                interface_name=a_name,
                ip_address="",
                ip_type="private",
                mac_address=mac_norm,
                bandwidth_mbps=speed_mbps,
                vlan_id=vlan_by_name.get(a_name, ""),
                duplex=duplex_str,
                link_state=link_state_str,
            ))
        return

    if ip4.startswith("127.") or ip4.startswith("169.254."):
        return

    prefix = prefix_by_alias.get(a_name, 24)
    gw     = gw_by_alias.get(a_name, "")
    try:
        import ipaddress as _ipa2
        net_str = str(_ipa2.ip_interface(f"{ip4}/{prefix}").network)
    except Exception:
        net_str = f"{ip4}/{prefix}"

    server.interfaces.append(NetworkInterface(
        interface_name=a_name,
        ip_address=ip4,
        ip_type="public" if not _is_private(ip4) else "private",
        mac_address=mac_norm,
        subnet=net_str,
        gateway=gw,
        bandwidth_mbps=speed_mbps,
        vlan_id=vlan_by_name.get(a_name, ""),
        duplex=duplex_str,
        link_state=link_state_str,
    ))


# Function: _winrm_parse_network_interfaces
def _winrm_parse_network_interfaces(server: DiscoveredServer, s) -> None:
    """Parse Windows network adapters, IPs, VLANs, speed, and duplex via WinRM."""
    try:
        net_r = s.run_ps(
            "$adapters = Get-NetAdapter | Select-Object Name,MacAddress,LinkSpeed,MediaType,Status,Virtual,InterfaceIndex,FullDuplex,MediaConnectionState; "
            "$configs  = Get-NetIPConfiguration | Select-Object InterfaceAlias,InterfaceIndex,IPv4Address,IPv4DefaultGateway,DNSServer; "
            "$assoc    = Get-NetIPAddress -AddressFamily IPv4 | Select-Object InterfaceAlias,InterfaceIndex,IPAddress,PrefixLength; "
            "$vlans    = Get-NetAdapterAdvancedProperty -RegistryKeyword 'VlanID' -ErrorAction SilentlyContinue "
            "            | Select-Object Name,RegistryValue; "
            "$physical = Get-WmiObject Win32_NetworkAdapter -ErrorAction SilentlyContinue "
            "            | Where-Object {$_.PhysicalAdapter -eq $true} "
            "            | Select-Object Name,Speed,MACAddress,NetConnectionID,NetEnabled; "
            "$result   = @{adapters=$adapters; configs=$configs; assoc=$assoc; vlans=$vlans; physical=$physical}; "
            "ConvertTo-Json -Depth 5 $result"
        )
        if net_r.status_code == 0 and net_r.std_out:
            import json as _json
            try:
                nd = _json.loads(net_r.std_out.decode("utf-8", errors="replace"))
                adapters_raw, configs_raw, assoc_raw, vlans_raw, physical_raw = _winrm_net_normalize_raw(nd)

                wmi_speed, wmi_mac = _winrm_net_wmi_maps(physical_raw)
                vlan_by_name = _winrm_net_vlan_map(vlans_raw)
                gw_by_alias = _winrm_net_gateway_map(configs_raw)
                prefix_by_alias = _winrm_net_prefix_map(assoc_raw)

                server.interfaces = []
                for adap in adapters_raw:
                    _winrm_process_adapter(server, adap, assoc_raw, configs_raw,
                                           wmi_speed, wmi_mac, vlan_by_name,
                                           gw_by_alias, prefix_by_alias)
            except Exception as _ne:
                log.debug("WinRM network parse error: %s", _ne)
    except Exception as _ne:
        log.debug("WinRM Get-NetAdapter failed: %s", _ne)


# Function: _winrm_parse_routing_table
def _winrm_parse_routing_table(server: DiscoveredServer, s) -> None:
    """Populate server.routes from Get-NetRoute via WinRM."""
    try:
        route_r = s.run_ps(
            "Get-NetRoute -AddressFamily IPv4 | Where-Object {$_.DestinationPrefix -ne '127.0.0.0/8' -and $_.DestinationPrefix -ne '127.0.0.1/32'} "
            "| Select-Object DestinationPrefix,NextHop,RouteMetric,InterfaceAlias | ConvertTo-Json"
        )
        if route_r.status_code == 0 and route_r.std_out:
            import json as _json
            try:
                routes_raw = _json.loads(route_r.std_out.decode("utf-8", errors="replace"))
                if isinstance(routes_raw, dict):
                    routes_raw = [routes_raw]
                server.routes = [
                    {
                        "destination": r.get("DestinationPrefix", ""),
                        "gateway": r.get("NextHop", "") or "",
                        "interface": r.get("InterfaceAlias", "") or "",
                        "metric": r.get("RouteMetric", ""),
                    }
                    for r in (routes_raw or [])
                    if r.get("DestinationPrefix")
                ][:50]
            except Exception:
                pass
    except Exception:
        pass


# Function: _winrm_parse_arp_table
def _winrm_arp_entry(entry: dict, seen_macs_arp: set):
    ip  = entry.get("IPAddress", "") or ""
    mac = (entry.get("LinkLayerAddress") or "").replace("-", ":").lower()
    if not ip or not mac:
        return None
    if ip.startswith("127.") or ip.endswith(".255"):
        return None
    if mac in ("ff:ff:ff:ff:ff:ff", "00:00:00:00:00:00"):
        return None
    if mac in seen_macs_arp:
        return None
    seen_macs_arp.add(mac)
    return {
        "ip": ip,
        "mac": mac,
        "interface": entry.get("InterfaceAlias", "") or "",
        "type": entry.get("State", "") or "",
    }


# Function: _winrm_parse_arp_table
def _winrm_parse_arp_table(server: DiscoveredServer, s) -> None:
    """Populate server.arp_neighbors from Get-NetNeighbor via WinRM."""
    try:
        arp_r = s.run_ps(
            "Get-NetNeighbor -AddressFamily IPv4 | Where-Object {$_.State -ne 'Unreachable' -and $_.LinkLayerAddress -ne '00-00-00-00-00-00'} "
            "| Select-Object IPAddress,LinkLayerAddress,State,InterfaceAlias | ConvertTo-Json"
        )
        if arp_r.status_code == 0 and arp_r.std_out:
            import json as _json
            try:
                arp_raw = _json.loads(arp_r.std_out.decode("utf-8", errors="replace"))
                if isinstance(arp_raw, dict):
                    arp_raw = [arp_raw]
                seen_macs_arp: set[str] = set()
                server.arp_neighbors = []
                for entry in (arp_raw or []):
                    parsed = _winrm_arp_entry(entry, seen_macs_arp)
                    if parsed:
                        server.arp_neighbors.append(parsed)
            except Exception:
                pass
    except Exception:
        pass


# Function: _winrm_enrich
def _winrm_fetch_os_info(server: DiscoveredServer, s) -> None:
    os_result = s.run_ps(
        "Get-WmiObject -Class Win32_OperatingSystem | "
        "Select-Object -Property Caption,Version,OSArchitecture,TotalVisibleMemorySize | "
        "ConvertTo-Json"
    )
    if os_result.status_code != 0:
        return
    import json
    data = json.loads(os_result.std_out.decode())
    server.os_name = data.get("Caption", "Windows")
    server.os_family = "windows"
    server.os_version = data.get("Version", "")
    server.architecture = "64 bit" if "64" in str(data.get("OSArchitecture", "")) else "32 bit"
    mem_kb = data.get("TotalVisibleMemorySize", 0)
    server.ram_gb = round(mem_kb / 1024 / 1024, 1) if mem_kb else 0.0


# Function: _winrm_fetch_cpu
def _winrm_fetch_cpu(server: DiscoveredServer, s) -> None:
    cpu_r = s.run_ps(
        "Get-WmiObject Win32_ComputerSystem | Select-Object -ExpandProperty NumberOfLogicalProcessors"
    )
    if cpu_r.status_code != 0:
        return
    try:
        server.cpu_cores = int(cpu_r.std_out.decode().strip())
    except ValueError:
        pass


# Function: _winrm_fetch_disks
def _winrm_fetch_disks(server: DiscoveredServer, s) -> None:
    disk_r = s.run_ps(
        "Get-WmiObject Win32_LogicalDisk | Where-Object {$_.DriveType -eq 3} | "
        "Select-Object DeviceID,Size,FreeSpace | ConvertTo-Json"
    )
    if disk_r.status_code != 0:
        return
    import json
    disks_raw = json.loads(disk_r.std_out.decode())
    if isinstance(disks_raw, dict):
        disks_raw = [disks_raw]
    for dr in disks_raw:
        size_gb = round(int(dr.get("Size", 0)) / 1e9, 1)
        used_gb = round((int(dr.get("Size", 0)) - int(dr.get("FreeSpace", 0))) / 1e9, 1)
        server.disks.append(DiskInfo(
            mount_point=str(dr.get("DeviceID", "")),
            size_gb=size_gb,
            used_gb=used_gb,
            disk_type="HDD",
        ))
    server.total_storage_gb = sum(d.size_gb for d in server.disks)


# Function: _winrm_fetch_services_workloads
def _winrm_fetch_services_workloads(server: DiscoveredServer, s) -> None:
    svc_r = s.run_ps(
        "Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object -ExpandProperty Name | ConvertTo-Json"
    )
    if svc_r.status_code != 0:
        return
    import json
    svc_names = json.loads(svc_r.std_out.decode())
    wl_map = {
        "MSSQLSERVER": ("MSSQL", "db"), "mysql": ("MySQL", "db"),
        "PostgreSQL": ("PostgreSQL", "db"), "W3SVC": ("IIS", "web"),
        "Tomcat": ("ApacheTomcat", "app"),
        "redis": ("Redis", "cache"),
    }
    for svc_name in svc_names:
        for key, (name, wtype) in wl_map.items():
            if key.lower() in svc_name.lower():
                server.workloads.append(WorkloadComponent(name=name, component_type=wtype))


# Function: _winrm_set_static_attrs
def _winrm_set_static_attrs(server: DiscoveredServer) -> None:
    server.server_type = "Virtual"
    server.virtualization_state = "Virtualized"
    server.virtualization_attributes = {"hypervisor": "Hyper-V or VMware", "dmi_hint": "WinRM detected"}
    server.compute_hardware_arch = "x86_64"
    server.boot_type = "BIOS"
    server.os_family = "windows"
    server.install_type = "OEM"


# Function: _winrm_finalize_db_and_software
def _winrm_finalize_db_and_software(server: DiscoveredServer, s) -> None:
    # DB engine from running services
    db_engines = [
        f"{w.name} {w.version}".strip()
        for w in server.workloads if w.component_type == "db"
    ]
    if db_engines:
        server.db_engine = ", ".join(db_engines)
        server.db_storage_gb = round(server.total_storage_gb * 0.4, 1)

    server.internal_storage_gb = server.total_storage_gb
    server.storage_type = "HDD"

    # ── Installed software inventory ──
    server.installed_software = _collect_installed_software_winrm(s)
    # Supplement with workload inference if WinRM software collection is sparse
    if len(server.installed_software) < 3:
        inferred = _infer_software_from_workloads(server)
        existing_names = {sw.name.lower() for sw in server.installed_software}
        server.installed_software += [
            sw for sw in inferred if sw.name.lower() not in existing_names
        ]


# Function: _winrm_enrich
def _winrm_enrich(server: DiscoveredServer, target: ScanTarget) -> None:
    if not _winrm_available():
        log.debug("pywinrm not installed — skipping WinRM enrichment")
        return
    try:
        import winrm
        s = winrm.Session(
            target=server.ip_address,
            auth=(target.winrm_username, target.winrm_password),
            transport="ntlm",
        )
        _winrm_fetch_os_info(server, s)
        _winrm_fetch_cpu(server, s)
        _winrm_fetch_disks(server, s)
        _winrm_fetch_services_workloads(server, s)
        _winrm_set_static_attrs(server)

        # ── Network Interfaces — MAC, VLAN, subnet, gateway, speed, duplex (L2 + L3) ──
        _winrm_parse_network_interfaces(server, s)

        # ── L3 Routing table ──────────────────────────────────────────────────
        _winrm_parse_routing_table(server, s)

        # ── L2 ARP / Neighbor table ───────────────────────────────────────────
        _winrm_parse_arp_table(server, s)

        _winrm_finalize_db_and_software(server, s)
    except Exception as exc:
        log.debug("WinRM enrichment failed for %s: %s", server.ip_address, exc)


# ─── Main entry point ──────────────────────────────────────────────────────────

# Function: _phase0_arp_sweep
def _phase0_arp_sweep(cidr: str, cb: Callable[[int, str], None]) -> dict[str, str]:
    """Pre-scan MAC harvest (no auth, very fast)."""
    cb(3, "Phase 0: ARP sweep — bulk MAC discovery")

    # a) Platform ARP cache (built from prior traffic, instant)
    local_arp = _collect_local_arp()

    # b) PowerShell Get-NetNeighbor (Windows — more complete than arp -a)
    ps_arp = _powershell_arp_neighbors()
    local_arp.update(ps_arp)

    # c) Dedicated nmap ARP ping sweep — resolves MACs for all L2-reachable hosts
    cb(5, "Phase 0: nmap ARP sweep for MAC addresses")
    arp_mac_map = _arp_sweep_nmap(cidr, timeout=20)
    local_arp.update(arp_mac_map)
    if arp_mac_map:
        cb(8, f"Phase 0: Collected {len(arp_mac_map)} MACs via ARP sweep")

    return local_arp


# Function: _build_workload_hints
def _build_workload_hints(host: dict, server: DiscoveredServer) -> None:
    """Add workload hints from port scan."""
    for port in host.get("open_ports", []):
        if port in _PORT_SERVICES:
            wl_type, wl_name = _PORT_SERVICES[port]
            if wl_type not in ("ssh", "rdp", "snmp", "vnc"):
                server.workloads.append(WorkloadComponent(
                    name=wl_name,
                    component_type=wl_type,
                    port=port,
                ))


# Function: _deep_scan_host
def _deep_scan_host(server: DiscoveredServer, host: dict, target: ScanTarget) -> None:
    """Deep scan: SSH/WinRM for CPU/RAM/disk/network/workload details."""
    if not target.deep_scan:
        return
    has_ssh = 22 in host.get("open_ports", [])
    has_rdp = 3389 in host.get("open_ports", [])

    if has_ssh and target.ssh_username:
        _ssh_enrich(server, target)
    elif has_rdp and target.winrm_username:
        _winrm_enrich(server, target)


# Function: _scan_single_host
def _scan_single_host(
    host: dict,
    target: ScanTarget,
    local_arp: dict[str, str],
    local_gateway: str,
    scan_network: str,
    local_ips: set[str],
) -> DiscoveredServer:
    ip = host["ip"]

    server = DiscoveredServer(
        server_id=ip.replace(".", "-"),
        server_name=host.get("hostname") or ip,
        ip_address=ip,
        hostname=host.get("hostname", ""),
        cloud_provider="onprem",
        region="OnPrem",
    )

    _build_workload_hints(host, server)

    # Primary interface — MAC from: nmap ARP XML → ARP pre-pass → local ARP cache
    mac = host.get("mac", "") or local_arp.get(ip, "")
    server.interfaces.append(NetworkInterface(
        interface_name="eth0",
        ip_address=ip,
        ip_type="public" if not _is_private(ip) else "private",
        mac_address=mac,
        subnet=scan_network,
        gateway=local_gateway,
    ))

    # OS detection from nmap data (SSH/WinRM will overwrite with accurate info)
    _guess_os_from_ports(server, host)

    # Hardware enrichment without credentials:
    if ip in local_ips:
        _enrich_local_host(server)
    elif server.os_family == "windows":
        _wmic_remote_enrich(server)

    _deep_scan_host(server, host, target)

    # ── Local machine software inventory (no credentials needed) ─────
    # When the target is the local machine and no credential-based scan
    # ran (or it returned nothing), collect directly via the local OS APIs.
    if not server.installed_software:
        local_sw = _collect_local_machine_software(server.ip_address)
        if local_sw:
            server.installed_software = local_sw

    _classify_utilization(server)
    _assess_cloud_rationalization(server)

    # ── Ensure software inventory is never empty ────────────────────
    # When deep scan couldn't collect packages (no credentials or no SSH/WinRM),
    # infer software entries from detected workloads and OS so the dashboard
    # always shows at least the known running applications.
    if not server.installed_software:
        server.installed_software = _infer_software_from_workloads(server)

    return server


# Function: _phase3_snmp_enrich
def _phase3_snmp_enrich(servers: list[DiscoveredServer], cb: Callable[[int, str], None]) -> None:
    """SNMP enrichment — fill gaps for hosts missing MAC/speed."""
    needs_snmp = [
        s for s in servers
        if not all(i.mac_address for i in s.interfaces if i.ip_address)
        or not any(i.bandwidth_mbps for i in s.interfaces)
    ]
    if not (needs_snmp and _snmp_available()):
        return
    cb(90, f"Phase 3: SNMP enrichment for {len(needs_snmp)} host(s)")
    for srv in needs_snmp:
        try:
            _snmp_enrich(srv)
        except Exception as exc:
            log.debug("SNMP enrich %s failed: %s", srv.ip_address, exc)


# Function: _backfill_mac_addresses
def _backfill_mac_addresses(servers: list[DiscoveredServer], local_arp: dict[str, str]) -> None:
    """Back-fill any still-empty MACs from our ARP map (last resort)."""
    for srv in servers:
        mac_fallback = local_arp.get(srv.ip_address, "")
        for iface in srv.interfaces:
            if not iface.mac_address and mac_fallback:
                iface.mac_address = mac_fallback


# Function: scan_onprem
def scan_onprem(
    target: ScanTarget,
    progress_cb: Callable[[int, str], None] | None = None,
) -> list[DiscoveredServer]:
    """
    Full on-premises scan.  Returns list of DiscoveredServer.
    progress_cb(pct, message) is called with updates.

    Deep-scan strategy ("hacking mode"):
      Phase 0: ARP sweep + local ARP cache + Get-NetNeighbor  → MAC map for all hosts
      Phase 1: nmap host+port+OS discovery (enhanced with SNMP/banner scripts)
      Phase 2: Per-host SSH / WinRM deep enrichment (CPU/RAM/network/workloads)
      Phase 3: SNMP enrichment for any host still missing MAC/speed
    """
    # Function: _cb
    def _cb(pct: int, msg: str) -> None:
        log.info("[onprem %d%%] %s", pct, msg)
        if progress_cb:
            progress_cb(pct, msg)

    cidr = target.network_range or "192.168.1.0/24"
    _cb(2, f"Starting deep host discovery on {cidr}")

    # ── Phase 0: Pre-scan MAC harvest (no auth, very fast) ────────────────────
    local_arp = _phase0_arp_sweep(cidr, _cb)

    local_gateway = _get_local_gateway()
    local_ips = _get_local_ips()
    try:
        scan_network = str(ipaddress.ip_network(cidr, strict=False))
    except Exception:
        scan_network = ""

    # ── Phase 1: nmap host + port + OS discovery ──────────────────────────────
    _cb(10, f"Phase 1: nmap host discovery on {cidr}")
    raw_hosts = _nmap_scan(cidr, timeout=target.timeout_seconds)
    _cb(30, f"Phase 1 complete: {len(raw_hosts)} live hosts found")

    servers: list[DiscoveredServer] = []
    total = max(len(raw_hosts), 1)

    # ── Phase 2: Per-host enrichment ──────────────────────────────────────────
    for idx, host in enumerate(raw_hosts):
        ip = host["ip"]
        _cb(30 + int(55 * idx / total), f"Phase 2: Scanning {ip}")
        server = _scan_single_host(host, target, local_arp, local_gateway, scan_network, local_ips)
        servers.append(server)

    _cb(88, "Phase 2 complete")

    # ── Phase 3: SNMP enrichment — fill gaps for hosts missing MAC/speed ──────
    _phase3_snmp_enrich(servers, _cb)

    # Back-fill any still-empty MACs from our ARP map (last resort)
    _backfill_mac_addresses(servers, local_arp)

    _cb(95, "Finalizing results")
    return servers


# ─── Cloud rationalization assessment ────────────────────────────────────────

# Function: _assess_cpu_requirement
def _assess_cpu_requirement(server: DiscoveredServer) -> None:
    if server.cpu_cores and server.cpu_cores >= 32:
        server.cpu_requirement = "High-Performance"
    elif server.cpu_cores and server.cpu_cores >= 16:
        server.cpu_requirement = "Standard-High"
    else:
        server.cpu_requirement = "Standard"


# Function: _assess_memory_requirement
def _assess_memory_requirement(server: DiscoveredServer) -> None:
    if server.ram_gb and server.ram_gb >= 256:
        server.memory_requirement = "High-Memory"
    elif server.ram_gb and server.ram_gb >= 64:
        server.memory_requirement = "Standard-High"
    else:
        server.memory_requirement = "Standard"


# Function: _assess_virtualization_suitability
def _assess_virtualization_suitability(server: DiscoveredServer) -> None:
    if server.virtualization_state in ("Virtualized", "Container"):
        server.cloud_suitability = "High"
    elif server.virtualization_state == "Physical":
        server.cloud_suitability = "Medium"
    else:
        server.cloud_suitability = "Medium"


# Function: _assess_mainframe_dependency
def _assess_mainframe_dependency(server: DiscoveredServer) -> None:
    if "mainframe" in (server.compute_hardware_arch or "").lower() or \
       "z (mainframe)" in (server.compute_hardware_arch or "").lower():
        server.mainframe_dependency = "Yes"
        server.cloud_suitability = "Low"
    else:
        server.mainframe_dependency = server.mainframe_dependency or "No"


# Function: _assess_os_cloud_suitability
def _assess_os_cloud_suitability(server: DiscoveredServer) -> None:
    os_lower = (server.os_name or "").lower()
    if any(k in os_lower for k in ["ubuntu 20", "ubuntu 22", "ubuntu 24",
                                    "rhel 8", "rhel 9", "debian 11",
                                    "windows server 2019", "windows server 2022"]):
        server.app_os_cloud_suitability = "Ready"
    elif any(k in os_lower for k in ["ubuntu 16", "ubuntu 18", "centos 6", "centos 7",
                                      "rhel 6", "rhel 7",
                                      "windows server 2008", "windows server 2012"]):
        server.app_os_cloud_suitability = "Needs Remediation"
    else:
        server.app_os_cloud_suitability = "Review Required"


# Function: _assess_db_cloud_readiness
def _assess_db_cloud_readiness(server: DiscoveredServer) -> None:
    db_lower = (server.db_engine or "").lower()
    if any(k in db_lower for k in ["mysql 8", "postgresql 14", "postgresql 15",
                                    "postgresql 16", "mongodb", "redis"]):
        server.db_cloud_readiness = "Ready"
    elif db_lower:
        server.db_cloud_readiness = "Needs Migration"
    else:
        server.db_cloud_readiness = "N/A"


# Function: _assess_middleware_cloud_readiness
def _assess_middleware_cloud_readiness(server: DiscoveredServer) -> None:
    mw = [w for w in server.workloads
          if w.component_type in ("app", "queue", "cache", "web")]
    if mw:
        server.middleware_cloud_readiness = "Review Required"
    else:
        server.middleware_cloud_readiness = "N/A"


# Function: _assess_hardware_dependency
def _assess_hardware_dependency(server: DiscoveredServer) -> None:
    if server.flash_storage_used:
        server.app_hardware_dependency = "Flash Storage"
    else:
        server.app_hardware_dependency = "None"


# Function: _assess_cots_status
def _assess_cots_status(server: DiscoveredServer) -> None:
    """COTS vs Non-COTS — heuristic from known software."""
    cots_names = {"mysql", "mssql", "oracle", "postgresql", "redis",
                  "nginx", "apache", "iis", "tomcat", "rabbitmq", "kafka"}
    has_cots = any(
        any(c in (w.name or "").lower() for c in cots_names)
        for w in server.workloads
    )
    server.app_cots_vs_non_cots = "COTS" if has_cots else "Unknown"


# Function: _assess_external_dependencies
def _assess_external_dependencies(server: DiscoveredServer) -> None:
    """External dependencies (ports open)."""
    open_port_count = sum(len(getattr(iface, "port", 0) or []) for iface in server.interfaces)
    total_workloads = len(server.workloads)
    if total_workloads <= 2:
        server.volume_external_dependencies = "Low"
    elif total_workloads <= 5:
        server.volume_external_dependencies = "Medium"
    else:
        server.volume_external_dependencies = "High"


# Function: _assess_load_predictability
def _assess_load_predictability(server: DiscoveredServer) -> None:
    """Load predictability from utilization."""
    band = server.utilization_band or "unknown"
    if band == "underutilized":
        server.app_load_predictability = "Predictable"
        server.financially_optimizable = "Yes"
    elif band == "moderate":
        server.app_load_predictability = "Predictable"
        server.financially_optimizable = "Partial"
    else:
        server.app_load_predictability = "Unpredictable"
        server.financially_optimizable = "No"


# Function: _assess_distributed_architecture
def _assess_distributed_architecture(server: DiscoveredServer) -> None:
    """Distributed architecture — heuristic: multiple interfaces or cluster hint."""
    if len(server.interfaces) > 2:
        server.distributed_architecture = "Yes"
    elif len(server.workloads) > 4:
        server.distributed_architecture = "Partial"
    else:
        server.distributed_architecture = "No"


# Function: _apply_manual_input_defaults
def _apply_manual_input_defaults(server: DiscoveredServer) -> None:
    """Defaults for fields that need manual input."""
    server.latency_requirements             = server.latency_requirements or "Standard"
    server.ubiquitous_access                = server.ubiquitous_access or "No"
    server.no_production_environments       = server.no_production_environments or 1
    server.no_non_production_environments   = server.no_non_production_environments or 1
    server.ha_dr_requirements               = server.ha_dr_requirements or "Active-Passive"
    server.rto_requirements                 = server.rto_requirements or "<4h"
    server.rpo_requirements                 = server.rpo_requirements or "<1h"
    server.deployment_geography             = server.deployment_geography or "Single-Region"
    server.application_stability            = server.application_stability or "Stable"
    server.environment                      = server.environment or "Production"


# Function: _assess_migration_strategy
def _assess_migration_strategy(server: DiscoveredServer) -> None:
    """Migration strategy — derived from cloud_suitability + utilization."""
    if server.migration_strategy:
        return
    cs    = server.cloud_suitability or ""
    band  = server.utilization_band or "unknown"
    ms    = server.mainframe_dependency or "No"
    if ms == "Yes":
        server.migration_strategy = "decommission"
    elif cs == "High":
        server.migration_strategy = "lift_and_shift" if band == "underutilized" else "smart_shift"
    elif cs == "Medium":
        server.migration_strategy = "smart_shift_effort"
    else:
        server.migration_strategy = "smart_shift_effort"


# Function: _assess_cloud_rationalization
def _assess_cloud_rationalization(server: DiscoveredServer) -> None:
    """
    Derive the cloud/rationalization assessment fields from scanner-collected
    hardware & OS data.  These are heuristic defaults — users can override via
    the API / UI.
    """
    _assess_cpu_requirement(server)
    _assess_memory_requirement(server)
    _assess_virtualization_suitability(server)
    _assess_mainframe_dependency(server)

    server.desktop_dependency = "No"

    _assess_os_cloud_suitability(server)
    _assess_db_cloud_readiness(server)
    _assess_middleware_cloud_readiness(server)
    _assess_hardware_dependency(server)
    _assess_cots_status(server)
    _assess_external_dependencies(server)
    _assess_load_predictability(server)
    _assess_distributed_architecture(server)
    _apply_manual_input_defaults(server)
    _assess_migration_strategy(server)


# ─── L2/L3 deep-scan helpers ──────────────────────────────────────────────────

# Function: _collect_local_arp
def _collect_local_arp() -> dict[str, str]:
    """
    Read local ARP/neighbor cache — OS-agnostic.
    Sources tried: `arp -a` (all), `ip neigh show` (Linux).
    Returns {ip: mac_address}.
    """
    arp_map: dict[str, str] = {}
    mac_re = re.compile(r'\b((?:[0-9a-fA-F]{2}[:\-]){5}[0-9a-fA-F]{2})\b')
    ip_re  = re.compile(r'\b((?:\d{1,3}\.){3}\d{1,3})\b')

    # Function: _parse_lines
    def _parse_lines(text: str) -> None:
        for line in text.splitlines():
            ip_m  = ip_re.search(line)
            mac_m = mac_re.search(line)
            if ip_m and mac_m:
                ip  = ip_m.group(1)
                mac = mac_m.group(1).replace("-", ":").lower()
                if (mac not in ("ff:ff:ff:ff:ff:ff", "00:00:00:00:00:00")
                        and not ip.startswith("127.")
                        and not ip.endswith(".255")):
                    arp_map[ip] = mac

    # arp -a (Windows + Linux)
    try:
        r = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=10, check=False)
        _parse_lines(r.stdout)
    except Exception:
        pass

    # ip neigh show (Linux — includes STALE entries that arp -a sometimes misses)
    try:
        r = subprocess.run(
            ["ip", "neigh", "show"],
            capture_output=True, text=True, timeout=5, check=False,
        )
        if r.returncode == 0:
            _parse_lines(r.stdout)
    except Exception:
        pass

    return arp_map


# Function: _get_local_gateway
def _get_local_gateway() -> str:
    """Get the default gateway from the local machine's routing table."""
    # Linux: ip route show default
    try:
        result = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True, text=True, timeout=5, check=False
        )
        m = re.search(r'default\s+via\s+([\d.]+)', result.stdout)
        if m:
            return m.group(1)
    except Exception:
        pass
    # Windows: route print -4 — look for 0.0.0.0 network entry
    try:
        result = subprocess.run(
            ["route", "print", "-4"],
            capture_output=True, text=True, timeout=5, check=False
        )
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[0] == '0.0.0.0' and parts[1] == '0.0.0.0':  # nosec B104
                gw = parts[2]
                if re.match(r'[\d.]+', gw) and gw != '0.0.0.0':  # nosec B104
                    return gw
    except Exception:
        pass
    return ""


# Function: _get_local_ips
def _get_local_ips() -> set[str]:
    """Return all IPv4 addresses assigned to this scanning machine."""
    ips: set[str] = set()
    try:
        ips.update(socket.gethostbyname_ex(socket.gethostname())[2])
    except Exception:
        pass
    try:
        import psutil
        for addrs in psutil.net_if_addrs().values():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ips.add(addr.address)
    except Exception:
        pass
    ips.discard("127.0.0.1")
    ips.discard("0.0.0.0")  # nosec B104
    return ips


# Function: _iface_ip_and_mac
def _iface_ip_and_mac(addrs) -> tuple[str, str]:
    import psutil
    ip4 = mac = ""
    for a in addrs:
        if a.family == socket.AF_INET:
            ip4 = a.address
        elif hasattr(psutil, "AF_LINK") and a.family == psutil.AF_LINK:
            mac = a.address
        elif a.family.value == 17 if hasattr(a.family, "value") else a.family == 17:
            mac = a.address
    return ip4, mac


# Function: _update_existing_interface
def _update_existing_interface(existing, mac: str, speed: int) -> None:
    if mac and not existing.mac_address:
        existing.mac_address = mac.lower()
    if speed and not existing.bandwidth_mbps:
        existing.bandwidth_mbps = speed


# Function: _merge_local_interface
def _merge_local_interface(server: DiscoveredServer, if_name: str, addrs, net_stats) -> None:
    ip4, mac = _iface_ip_and_mac(addrs)
    if not ip4 or ip4.startswith("127."):
        return
    stat = net_stats.get(if_name)
    speed = stat.speed if (stat and stat.isup) else 0
    existing = next((i for i in server.interfaces if i.ip_address == ip4), None)
    if existing:
        _update_existing_interface(existing, mac, speed)
        return
    server.interfaces.append(NetworkInterface(
        interface_name=if_name,
        ip_address=ip4,
        ip_type="public" if not _is_private(ip4) else "private",
        mac_address=mac.lower() if mac else "",
        bandwidth_mbps=speed,
    ))


# Function: _enrich_local_interfaces
def _enrich_local_interfaces(server: DiscoveredServer) -> None:
    """Network interfaces — MAC + speed via psutil (L2 enrichment)."""
    import psutil
    try:
        net_addrs = psutil.net_if_addrs()
        net_stats = psutil.net_if_stats()
        for if_name, addrs in net_addrs.items():
            _merge_local_interface(server, if_name, addrs, net_stats)
    except Exception as _ne:
        log.debug("psutil network iface enrichment failed: %s", _ne)


# Function: _enrich_local_routes
def _enrich_local_routes(server: DiscoveredServer, system: str) -> None:
    """L3 routing table (local machine)."""
    try:
        if system == "Windows":
            _r = subprocess.run(
                ["route", "print", "-4"],
                capture_output=True, text=True, timeout=8, check=False,
            )
            server.routes = _parse_ip_routes_windows(_r.stdout)
        else:
            _r = subprocess.run(
                ["ip", "route", "show"],
                capture_output=True, text=True, timeout=5, check=False,
            )
            server.routes = _parse_ip_routes(_r.stdout)
    except Exception:
        pass


# Function: _enrich_local_arp
def _enrich_local_arp(server: DiscoveredServer, system: str) -> None:
    """L2 ARP / neighbor table (local machine)."""
    try:
        if system == "Windows":
            _a = subprocess.run(
                ["arp", "-a"],
                capture_output=True, text=True, timeout=8, check=False,
            )
            server.arp_neighbors = _parse_arp_table_windows(_a.stdout, server.ip_address)
        else:
            _a = subprocess.run(
                ["ip", "neigh", "show"],
                capture_output=True, text=True, timeout=5, check=False,
            )
            server.arp_neighbors = _parse_arp_table(_a.stdout, server.ip_address)
    except Exception:
        pass


# Function: _local_enrich_network
def _local_enrich_network(server: DiscoveredServer, system: str) -> None:
    """Populate server interfaces, routes and ARP from psutil + local CLI commands."""
    _enrich_local_interfaces(server)
    _enrich_local_routes(server, system)
    _enrich_local_arp(server, system)


# Function: _detect_local_os_name
def _detect_local_os_name(server: DiscoveredServer, system: str) -> None:
    """Accurate OS name from local system."""
    import platform
    if system == "Windows":
        server.os_family = "windows"
        try:
            import winreg
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
            ) as k:
                product = winreg.QueryValueEx(k, "ProductName")[0]
                build = winreg.QueryValueEx(k, "CurrentBuildNumber")[0]
                server.os_name = f"{product} (Build {build})"
        except Exception:
            ver = platform.win32_ver()
            server.os_name = f"Windows {ver[0]} {ver[1]}".strip()
    else:
        server.os_family = "linux"
        try:
            kv: dict[str, str] = {}
            with open("/etc/os-release") as _f:
                for _line in _f:
                    if "=" in _line:
                        _k, _, _v = _line.strip().partition("=")
                        kv[_k] = _v.strip('"')
            server.os_name = kv.get("PRETTY_NAME") or platform.platform()
        except Exception:
            server.os_name = platform.platform()


# Function: _collect_local_disks
def _collect_local_disks(server: DiscoveredServer) -> None:
    """Disks — skip virtual/system-only partitions."""
    import psutil
    server.disks = []
    seen_mounts: set[str] = set()
    _skip_fstypes = {"cdfs", "squashfs", "tmpfs", "devtmpfs", "sysfs", "proc", ""}
    for part in psutil.disk_partitions(all=False):
        mp = part.mountpoint
        if mp in seen_mounts:
            continue
        seen_mounts.add(mp)
        if part.fstype.lower() in _skip_fstypes:
            continue
        try:
            usage = psutil.disk_usage(mp)
            if usage.total < 200 * 1024 * 1024:   # skip < 200 MB
                continue
            server.disks.append(DiskInfo(
                mount_point=mp,
                size_gb=round(usage.total / (1024 ** 3), 1),
                used_gb=round(usage.used / (1024 ** 3), 1),
                disk_type="SSD",
            ))
        except (PermissionError, OSError):
            pass
    server.total_storage_gb = round(sum(d.size_gb for d in server.disks), 1)
    if server.total_storage_gb > 0:
        used_total = sum(d.used_gb for d in server.disks)
        server.disk_util_pct = round(100.0 * used_total / server.total_storage_gb, 1)


# Function: _detect_local_server_type
def _detect_local_server_type(server: DiscoveredServer, system: str) -> None:
    """Server type: detect VM via wmic model (fast, < 1 s)."""
    try:
        if system == "Windows":
            _vm_r = subprocess.run(
                ["wmic", "computersystem", "get", "Model", "/format:list"],
                capture_output=True, text=True, timeout=5, check=False
            )
        else:
            _vm_r = subprocess.run(
                ["cat", "/sys/class/dmi/id/product_name"],
                capture_output=True, text=True, timeout=5, check=False
            )
        _hint = _vm_r.stdout.lower()
        _vm_kw = ("vmware", "virtualbox", "kvm", "xen", "virtual machine",
                  "hyper-v", "qemu", "bochs", "innotek")
        server.server_type = "Virtual" if any(kw in _hint for kw in _vm_kw) else "Physical"
    except Exception:
        server.server_type = "Physical"


# Function: _collect_local_psutil_metrics
def _collect_local_psutil_metrics(server: DiscoveredServer, system: str) -> None:
    import psutil

    # CPU
    server.cpu_cores = psutil.cpu_count(logical=True) or 1
    server.cpu_util_pct = round(psutil.cpu_percent(interval=0.5), 1)

    # RAM
    mem = psutil.virtual_memory()
    server.ram_gb = round(mem.total / (1024 ** 3), 1)
    server.ram_util_pct = round(mem.percent, 1)

    _collect_local_disks(server)

    # Network interfaces, routing, and ARP
    _local_enrich_network(server, system)

    _detect_local_server_type(server, system)


# Function: _enrich_local_host
def _enrich_local_host(server: DiscoveredServer) -> None:
    """Populate the local scanning host with accurate hardware data via psutil.
    Falls back to wmic CLI on Windows if psutil is unavailable.
    """
    import platform
    system = platform.system()

    _detect_local_os_name(server, system)

    try:
        _collect_local_psutil_metrics(server, system)
    except ImportError:
        _enrich_local_host_wmic(server)
    except Exception as exc:
        log.debug("psutil local enrichment failed: %s", exc)


# Function: _wmic_local_cpu
def _wmic_local_cpu(server: DiscoveredServer) -> None:
    r = subprocess.run(
        ["wmic", "cpu", "get", "NumberOfLogicalProcessors", "/format:list"],
        capture_output=True, text=True, timeout=10, check=False
    )
    m = re.search(r"NumberOfLogicalProcessors=(\d+)", r.stdout)
    if m:
        server.cpu_cores = int(m.group(1))


# Function: _wmic_local_ram
def _wmic_local_ram(server: DiscoveredServer) -> None:
    r = subprocess.run(
        ["wmic", "os", "get",
         "TotalVisibleMemorySize,FreePhysicalMemory", "/format:list"],
        capture_output=True, text=True, timeout=10, check=False
    )
    total_m = re.search(r"TotalVisibleMemorySize=(\d+)", r.stdout)
    free_m = re.search(r"FreePhysicalMemory=(\d+)", r.stdout)
    if total_m:
        total_kb = int(total_m.group(1))
        server.ram_gb = round(total_kb / 1024 / 1024, 1)
        if free_m:
            free_kb = int(free_m.group(1))
            server.ram_util_pct = round(100.0 * (1 - free_kb / total_kb), 1)


# Function: _wmic_local_disks
def _wmic_local_disks(server: DiscoveredServer) -> None:
    r = subprocess.run(
        ["wmic", "logicaldisk", "get",
         "Caption,Size,FreeSpace", "/format:csv"],
        capture_output=True, text=True, timeout=10, check=False
    )
    server.disks = []
    for line in r.stdout.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 4 or parts[1] == "Caption" or not parts[3]:
            continue
        try:
            size_gb = round(int(parts[3]) / 1e9, 1)
            free_gb = round(int(parts[2]) / 1e9, 1) if parts[2] else 0.0
            if size_gb > 0:
                server.disks.append(DiskInfo(
                    mount_point=parts[1],
                    size_gb=size_gb,
                    used_gb=round(size_gb - free_gb, 1),
                    disk_type="HDD",
                ))
        except (ValueError, IndexError):
            pass
    server.total_storage_gb = round(sum(d.size_gb for d in server.disks), 1)


# Function: _enrich_local_host_wmic
def _enrich_local_host_wmic(server: DiscoveredServer) -> None:
    """Fallback: use wmic CLI to enrich local host on Windows (when psutil absent)."""
    import platform
    if platform.system() != "Windows":
        return
    try:
        _wmic_local_cpu(server)
        _wmic_local_ram(server)
        _wmic_local_disks(server)
        server.server_type = "Physical"
    except Exception as exc:
        log.debug("wmic local enrichment failed: %s", exc)


# Function: _wmic_remote_enrich
def _wmic_remote_enrich(server: DiscoveredServer) -> None:
    """Attempt a no-auth WMI query against a remote Windows host via wmic CLI.
    Only succeeds when both machines share the same Windows workgroup / domain
    and the target allows DCOM pass-through authentication.
    """
    import platform
    if platform.system() != "Windows":
        return
    ip = server.ip_address
    try:
        r = subprocess.run(
            ["wmic", f"/node:{ip}", "cpu",
             "get", "NumberOfLogicalProcessors", "/format:list"],
            capture_output=True, text=True, timeout=15, check=False
        )
        m = re.search(r"NumberOfLogicalProcessors=(\d+)", r.stdout)
        if m:
            server.cpu_cores = int(m.group(1))

        r = subprocess.run(
            ["wmic", f"/node:{ip}", "os",
             "get", "TotalVisibleMemorySize,FreePhysicalMemory", "/format:list"],
            capture_output=True, text=True, timeout=15, check=False
        )
        total_m = re.search(r"TotalVisibleMemorySize=(\d+)", r.stdout)
        free_m = re.search(r"FreePhysicalMemory=(\d+)", r.stdout)
        if total_m:
            total_kb = int(total_m.group(1))
            server.ram_gb = round(total_kb / 1024 / 1024, 1)
            if free_m:
                free_kb = int(free_m.group(1))
                server.ram_util_pct = round(100.0 * (1 - free_kb / total_kb), 1)

        if server.cpu_cores or server.ram_gb:
            log.debug("wmic-remote enriched %s: cpu=%d ram=%.1fGB",
                      ip, server.cpu_cores, server.ram_gb)
    except Exception as exc:
        log.debug("wmic remote enrich for %s: %s", ip, exc)


# Function: _parse_mac_from_iplink
def _parse_mac_from_iplink(ip_link_out: str) -> dict[str, str]:
    """Extract {interface_name: mac_address} from `ip link show` output."""
    macs: dict[str, str] = {}
    current: str = ""
    for line in ip_link_out.splitlines():
        m = re.match(r'\d+:\s+([\w@.]+):', line)
        if m:
            current = m.group(1).split('@')[0]
        if current:
            mac_m = re.search(r'link/ether\s+((?:[\da-fA-F]{2}:){5}[\da-fA-F]{2})', line)
            if mac_m:
                macs[current] = mac_m.group(1).lower()
                current = ""
    return macs


# Function: _lldp_mgmt_ip
def _lldp_mgmt_ip(chassis: dict) -> str:
    """Extract IP from chassis mgmt-ip."""
    mgmt = chassis.get("mgmt-ip", [])
    if isinstance(mgmt, list) and mgmt:
        return mgmt[0].get("value", "") if isinstance(mgmt[0], dict) else str(mgmt[0])
    if isinstance(mgmt, dict):
        return mgmt.get("value", "")
    return ""


# Function: _lldp_neighbor_entry
def _lldp_neighbor_entry(neighbor: dict) -> dict:
    chassis = neighbor.get("chassis", {})
    if isinstance(chassis, dict):
        chassis = list(chassis.values())[0] if chassis else {}
    port = neighbor.get("port", {})
    ttl = neighbor.get("ttl", {}).get("ttl", "") if isinstance(neighbor.get("ttl"), dict) else ""

    return {
        "chassis_id":   chassis.get("id", {}).get("value", ""),
        "system_name":  chassis.get("name", {}).get("value", "") if isinstance(chassis.get("name"), dict) else str(chassis.get("name", "")),
        "port_id":      port.get("id", {}).get("value", "") if isinstance(port.get("id"), dict) else str(port.get("id", "")),
        "port_descr":   port.get("descr", {}).get("value", "") if isinstance(port.get("descr"), dict) else str(port.get("descr", "")),
        "ip_address":   _lldp_mgmt_ip(chassis),
        "ttl":          str(ttl),
    }


# Function: _lldp_interface_neighbors
def _lldp_interface_neighbors(iface: dict) -> list[dict]:
    port_list = iface.get("port", [])
    if isinstance(port_list, dict):
        port_list = [port_list]
    return [_lldp_neighbor_entry(neighbor) for neighbor in port_list]


# Function: _parse_lldpctl_json
def _parse_lldpctl_json(lldp_raw: str) -> list[dict]:
    """
    Parse `lldpctl -f json` output into a list of neighbor dicts.
    Each entry: {chassis_id, port_id, system_name, ip_address, ttl}.
    """
    if not lldp_raw or not lldp_raw.strip().startswith("{"):
        return []
    neighbors: list[dict] = []
    try:
        import json as _json
        data = _json.loads(lldp_raw)
        lldp_root = data.get("lldp", data)
        interfaces = lldp_root.get("interface", [])
        if isinstance(interfaces, dict):
            interfaces = list(interfaces.values())
        for iface in interfaces:
            neighbors.extend(_lldp_interface_neighbors(iface))
    except Exception as exc:
        log.debug("LLDP JSON parse error: %s", exc)
    return neighbors


# Function: _parse_vlan_info
def _parse_vlan_info(vlan_out: str) -> dict[str, str]:
    """Extract {interface: vlan_id} from /proc/net/vlan/config."""
    vlan_map: dict[str, str] = {}
    for line in vlan_out.splitlines():
        m = re.match(r'(\S+)\s*\|\s*(\d+)', line)
        if m:
            vlan_map[m.group(1)] = m.group(2)
    return vlan_map


# Function: _parse_ip_routes
def _parse_ip_routes(route_out: str) -> list[dict]:
    """Parse `ip route show` into structured route list."""
    routes: list[dict] = []
    for line in route_out.splitlines():
        parts = line.split()
        if not parts:
            continue
        dest = parts[0]
        gw = dev = ""
        try:
            if "via" in parts:
                gw = parts[parts.index("via") + 1]
            if "dev" in parts:
                dev = parts[parts.index("dev") + 1]
        except IndexError:
            pass
        routes.append({"destination": dest, "gateway": gw, "interface": dev})
    return routes[:50]


# Function: _parse_arp_table
def _parse_arp_table(arp_out: str, self_ip: str = "") -> list[dict]:
    """Parse ARP/ip-neigh output into [{ip, mac, interface}] list."""
    neighbors: list[dict] = []
    seen_macs: set = set()
    for line in arp_out.splitlines():
        ip_m = re.match(r'([\d.]+)', line)
        if not ip_m:
            continue
        ip = ip_m.group(1)
        if ip == self_ip or ip.startswith("127."):
            continue
        mac_m = re.search(r'((?:[\da-fA-F]{2}:){5}[\da-fA-F]{2})', line)
        if not mac_m:
            continue
        mac = mac_m.group(1).lower()
        if mac in seen_macs or mac == "00:00:00:00:00:00":
            continue
        seen_macs.add(mac)
        dev_m = re.search(r'dev\s+(\w+)', line)
        neighbors.append({
            "ip": ip,
            "mac": mac,
            "interface": dev_m.group(1) if dev_m else "",
        })
    return neighbors[:50]


# Function: _windows_route_entry
def _windows_route_entry(s: str) -> dict | None:
    """Match a single `route print -4` line: Network Dest  Netmask  Gateway  Interface  Metric."""
    m = re.match(r'([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)', s)
    if not m:
        return None
    dest, mask, gw, iface_ip, metric = m.groups()
    if dest == "127.0.0.0" or dest == "127.0.0.1":
        return None
    # Convert netmask to prefix
    try:
        import ipaddress as _ipa
        net = _ipa.IPv4Network(f"{dest}/{mask}", strict=False)
        destination = str(net)
    except Exception:
        destination = dest
    return {
        "destination": destination,
        "gateway": gw if gw != "On-link" and gw != "0.0.0.0" else "",  # nosec B104
        "interface": iface_ip,
        "metric": metric,
    }


# Function: _parse_ip_routes_windows
def _parse_ip_routes_windows(route_out: str) -> list[dict]:
    """Parse `route print -4` (Windows) output into structured route list."""
    routes: list[dict] = []
    in_ipv4 = False
    for line in route_out.splitlines():
        s = line.strip()
        if "IPv4 Route Table" in s or "IPv4-Routentabelle" in s:
            in_ipv4 = True
            continue
        if in_ipv4 and s.startswith("="):
            continue
        if in_ipv4 and not s:
            continue
        entry = _windows_route_entry(s)
        if entry:
            routes.append(entry)
    return routes[:50]


# Function: _parse_arp_table_windows
def _parse_arp_table_windows(arp_out: str, self_ip: str = "") -> list[dict]:
    """Parse `arp -a` (Windows) output into [{ip, mac, interface}] list."""
    neighbors: list[dict] = []
    seen_macs: set = set()
    current_iface = ""
    for line in arp_out.splitlines():
        s = line.strip()
        # Interface line: "Interface: 192.168.0.105 --- 0x..."
        iface_m = re.match(r'Interface:\s+([\d.]+)', s)
        if iface_m:
            current_iface = iface_m.group(1)
            continue
        # ARP entry: "  192.168.0.1    aa-bb-cc-dd-ee-ff    dynamic"
        m = re.match(r'([\d.]+)\s+((?:[0-9a-fA-F]{2}[:\-]){5}[0-9a-fA-F]{2})\s+(\w+)', s)
        if m:
            ip, mac_raw, kind = m.groups()
            mac = mac_raw.replace('-', ':').lower()
            if ip == self_ip or ip.startswith("127.") or ip.endswith(".255"):
                continue
            if mac in ('ff:ff:ff:ff:ff:ff', '00:00:00:00:00:00'):
                continue
            if mac in seen_macs:
                continue
            seen_macs.add(mac)
            neighbors.append({
                "ip": ip,
                "mac": mac,
                "interface": current_iface,
                "type": kind,
            })
    return neighbors[:50]


# Function: _distro_label_from_hints
def _distro_label_from_hints(hints: str, hostname: str) -> str | None:
    """Linux distro hints from service version banners (e.g. OpenSSH 8.x Ubuntu)."""
    distro_map = [
        ("ubuntu",       "Ubuntu Linux"),
        ("debian",       "Debian Linux"),
        ("centos",       "CentOS Linux"),
        ("red hat",      "RHEL"),
        ("fedora",       "Fedora Linux"),
        ("alpine",       "Alpine Linux"),
        ("raspbian",     "Raspbian Linux"),
    ]
    for keyword, label in distro_map:
        if keyword in hints or keyword in hostname:
            return label
    return None


# Function: _guess_os_from_ports
def _guess_os_from_ports(server: DiscoveredServer, host: dict) -> None:
    """Heuristic OS detection from nmap port/banner data when no credentials available."""
    ports = set(host.get("open_ports", []))
    service_vals = list(host.get("service_hints", {}).values())
    hints = " ".join(service_vals).lower()
    hostname = (host.get("hostname", "") or "").lower()
    ip = server.ip_address

    # Use nmap OS guess if was extracted
    os_guess = host.get("os_guess", "")
    if os_guess:
        server.os_name = os_guess
        server.os_family = "windows" if "windows" in os_guess.lower() else "linux"
        return

    # Windows: RDP, SMB, or Windows-identifying banners
    if (3389 in ports or 445 in ports
            or "microsoft" in hints or "windows" in hints
            or "microsoft-ds" in hints):
        server.os_name = "Windows Server"
        server.os_family = "windows"
        return

    distro_label = _distro_label_from_hints(hints, hostname)
    if distro_label:
        server.os_name = distro_label
        server.os_family = "linux"
        return

    # SSH open → almost certainly Linux/Unix
    if 22 in ports:
        server.os_name = "Linux"
        server.os_family = "linux"
        return

    # Network device heuristics: gateway IP (.1 / .254) or only HTTP/HTTPS open
    last_octet = ip.split('.')[-1] if ip else ""
    if last_octet in ('1', '254') and 22 not in ports and 3389 not in ports:
        server.os_name = "Network Device (Router/Firewall)"
        server.server_type = "Network"
        return

    # Web server without SSH/RDP → embedded Linux or appliance
    if 80 in ports or 443 in ports or 8080 in ports:
        server.os_name = "Linux/Embedded"
        server.os_family = "linux"


# Function: _classify_utilization
def _classify_utilization(server: DiscoveredServer) -> None:
    """Set utilization_band based on CPU + RAM utilization metrics."""
    if server.cpu_util_pct < 0 and server.ram_util_pct < 0:
        server.utilization_band = "unknown"
        return
    avg = 0.0
    count = 0
    if server.cpu_util_pct >= 0:
        avg += server.cpu_util_pct
        count += 1
    if server.ram_util_pct >= 0:
        avg += server.ram_util_pct
        count += 1
    avg = avg / count if count else 0
    if avg < 30:
        server.utilization_band = "underutilized"
    elif avg < 65:
        server.utilization_band = "moderate"
    else:
        server.utilization_band = "utilized"
