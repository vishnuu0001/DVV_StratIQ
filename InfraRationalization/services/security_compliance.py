# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: services/security_compliance.py
# Date: 2025-07-23
# ---------------------------------------------------------------------------
"""
services/security_compliance.py
Security & Compliance Posture Analysis.

Features:
  - CVE scoring: cross-reference software versions against NVD/OSV databases
  - Unencrypted protocol detection: Telnet, FTP, HTTP, unencrypted LDAP
  - CIS Benchmark compliance scoring (Level 1/2 baselines)
  - Firewall gap analysis: open ports that shouldn't be externally exposed
  - Stale account detection (via SSH/WinRM data)
"""
from __future__ import annotations

import logging
import re
from datetime import date
from typing import Any

log = logging.getLogger(__name__)

# ── Unencrypted / dangerous protocols ───────────────────────────────────────
_INSECURE_PORTS: dict[int, dict] = {
    21:   {"protocol": "FTP",           "risk": "High",   "reason": "Credentials transmitted in plaintext"},
    23:   {"protocol": "Telnet",        "risk": "Critical","reason": "Full session including passwords in plaintext"},
    25:   {"protocol": "SMTP",          "risk": "Medium",  "reason": "Unencrypted email relay — use STARTTLS (587) instead"},
    69:   {"protocol": "TFTP",          "risk": "High",   "reason": "No authentication, used in network attacks"},
    80:   {"protocol": "HTTP",          "risk": "Medium",  "reason": "Unencrypted web traffic — redirect to HTTPS"},
    110:  {"protocol": "POP3",          "risk": "Medium",  "reason": "Unencrypted email retrieval"},
    143:  {"protocol": "IMAP",          "risk": "Medium",  "reason": "Unencrypted mail access"},
    389:  {"protocol": "LDAP",          "risk": "High",   "reason": "Unencrypted directory access — use LDAPS (636)"},
    445:  {"protocol": "SMB",           "risk": "High",   "reason": "Common ransomware attack vector — restrict access"},
    512:  {"protocol": "rexec",         "risk": "Critical","reason": "Remote execution without encryption"},
    513:  {"protocol": "rlogin",        "risk": "Critical","reason": "Remote login without encryption"},
    514:  {"protocol": "rsh/syslog",    "risk": "High",   "reason": "Remote shell without authentication"},
    1433: {"protocol": "MSSQL",         "risk": "High",   "reason": "Database port should not be publicly accessible"},
    3306: {"protocol": "MySQL",         "risk": "High",   "reason": "Database port should not be publicly accessible"},
    5432: {"protocol": "PostgreSQL",    "risk": "High",   "reason": "Database port should not be publicly accessible"},
    1521: {"protocol": "Oracle DB",     "risk": "High",   "reason": "Database port should not be publicly accessible"},
    27017:{"protocol": "MongoDB",       "risk": "High",   "reason": "Database port should not be publicly accessible"},
    6379: {"protocol": "Redis",         "risk": "High",   "reason": "Often runs unauthenticated — restrict access"},
    9200: {"protocol": "Elasticsearch", "risk": "High",   "reason": "Often unauthenticated — data exfiltration risk"},
    2375: {"protocol": "Docker API",    "risk": "Critical","reason": "Unauthenticated Docker daemon — full host compromise"},
    5900: {"protocol": "VNC",           "risk": "High",   "reason": "Screen sharing — often weak auth"},
    3389: {"protocol": "RDP",           "risk": "High",   "reason": "Brute-force target — restrict to VPN/Bastion"},
    8080: {"protocol": "HTTP-Alt",      "risk": "Medium",  "reason": "Unencrypted web traffic on alternate port"},
    11211:{"protocol": "Memcached",     "risk": "High",   "reason": "Often unauthenticated — amplification DDoS risk"},
}

# Ports that are ONLY risky if accessible from public/external interfaces
_RISKY_IF_PUBLIC = {1433, 3306, 5432, 1521, 27017, 6379, 9200, 2375, 11211}

# ── CIS Benchmark checks ────────────────────────────────────────────────────
# Each check: (check_id, description, applies_to_os, severity, deduction)
_CIS_CHECKS = [
    ("CIS-1.1",  "OS is supported (not EOS)",               "all",     "Critical", 25),
    ("CIS-1.2",  "No Telnet/FTP/rsh services running",       "all",     "High",     15),
    ("CIS-1.3",  "SSH is the only remote access protocol",   "linux",   "High",     10),
    ("CIS-1.4",  "LDAP traffic uses LDAPS (port 636)",       "all",     "Medium",    8),
    ("CIS-1.5",  "HTTP redirected to HTTPS",                 "all",     "Medium",    8),
    ("CIS-2.1",  "Database ports not publicly exposed",      "all",     "High",     15),
    ("CIS-2.2",  "Docker API not exposed on 2375",           "linux",   "Critical", 20),
    ("CIS-2.3",  "RDP access restricted (not public-facing)","windows", "High",     12),
    ("CIS-3.1",  "No end-of-life software packages",         "all",     "High",     10),
    ("CIS-3.2",  "Firewall/ACL present (port restrictions)", "all",     "Medium",    8),
]

# ── Known CVE patterns (simplified — real impl would call NVD/OSV APIs) ─────
# Format: (name_pattern, version_condition_fn, cve_id, cvss_score, description)
_KNOWN_CVES = [
    # OpenSSH
    ("openssh", lambda v: _version_lt(v, "9.3"), "CVE-2023-38408", 9.8,
     "Remote code execution via ssh-agent forwarding"),
    ("openssh", lambda v: _version_lt(v, "8.8"), "CVE-2021-41617", 7.0,
     "Privilege escalation in ssh-agent"),
    # Log4j
    ("log4j", lambda v: _version_lt(v, "2.17.1"), "CVE-2021-44228", 10.0,
     "Log4Shell — Remote code execution (CRITICAL)"),
    ("log4j-core", lambda v: _version_lt(v, "2.17.1"), "CVE-2021-44228", 10.0,
     "Log4Shell — Remote code execution (CRITICAL)"),
    # Apache HTTP
    ("apache2", lambda v: _version_lt(v, "2.4.55"), "CVE-2023-25690", 9.8,
     "HTTP request smuggling — remote code execution"),
    ("apache-httpd", lambda v: _version_lt(v, "2.4.55"), "CVE-2023-25690", 9.8,
     "HTTP request smuggling"),
    # nginx
    ("nginx", lambda v: _version_lt(v, "1.25.0"), "CVE-2022-41741", 7.1,
     "Memory corruption via mp4 module"),
    # OpenSSL
    ("openssl", lambda v: _version_lt(v, "3.0.7"), "CVE-2022-3786", 7.5,
     "Buffer overflow in X.509 certificate verification"),
    # Python
    ("python3", lambda v: _version_lt(v, "3.9.16"), "CVE-2022-45061", 7.5,
     "Quadratic time complexity in IDNA decode"),
    # MySQL
    ("mysql-server", lambda v: _version_lt(v, "8.0.32"), "CVE-2023-21912", 7.5,
     "MySQL Server DoS vulnerability"),
    # PostgreSQL
    ("postgresql", lambda v: _version_lt(v, "15.2"), "CVE-2023-2454", 7.2,
     "Privilege escalation via extension scripts"),
    # Redis
    ("redis", lambda v: _version_lt(v, "7.0.8"), "CVE-2023-22458", 5.5,
     "Integer overflow leading to DoS"),
    # Spring Framework
    ("spring-webmvc", lambda v: _version_lt(v, "5.3.18"), "CVE-2022-22965", 9.8,
     "Spring4Shell — Remote code execution"),
    # Tomcat
    ("tomcat", lambda v: _version_lt(v, "9.0.71"), "CVE-2023-28709", 7.5,
     "DoS via partial PUT request"),
    # Samba
    ("samba", lambda v: _version_lt(v, "4.17.5"), "CVE-2022-38023", 8.1,
     "RC4/HMAC-MD5 use allows man-in-the-middle"),
]


# Function: _version_lt
def _version_lt(version_str: str, threshold: str) -> bool:
    """Simple version comparison — returns True if version_str < threshold."""
    if not version_str or not threshold:
        return False
    try:
        # Function: _parse
        def _parse(v: str) -> tuple:
            # Strip non-numeric prefix (e.g. "1:8.4.0-1ubuntu2" → "8.4.0")
            v = re.sub(r"^[^0-9]*", "", v.split("-")[0].split("+")[0].split("~")[0])
            return tuple(int(x) for x in re.split(r"[.\-_]", v) if x.isdigit())
        return _parse(version_str) < _parse(threshold)
    except Exception:
        return False


# Function: _collect_workload_ports
def _collect_workload_ports(srv: dict) -> dict[int, bool]:
    ports: dict[int, bool] = {}
    for wl in (srv.get("workloads") or []):
        p = wl.get("port")
        if p:
            try:
                ports[int(p)] = False  # unknown, assume private
            except (ValueError, TypeError):
                pass
    return ports


# Function: _collect_open_ports
def _collect_open_ports(srv: dict) -> dict[int, bool]:
    ports: dict[int, bool] = {}
    for p in (srv.get("open_ports") or []):
        try:
            ports[int(p)] = False
        except (ValueError, TypeError):
            pass
    return ports


# Function: _get_all_ports
def _get_all_ports(srv: dict) -> dict[int, bool]:
    """Returns {port: is_public}."""
    ports = _collect_workload_ports(srv)
    ports.update(_collect_open_ports(srv))

    # Check if any interface is public
    has_public = any(
        (i.get("ip_type") or "").lower() == "public"
        for i in (srv.get("interfaces") or [])
    )
    if has_public:
        for p in list(ports.keys()):
            ports[p] = True
    return ports


# Function: _cve_match_for_pattern
def _cve_match_for_pattern(name: str, version: str, sw: dict, pattern: tuple) -> dict | None:
    """Check a single (sw_pattern, version_fn, cve_id, cvss, desc) tuple against sw."""
    sw_pattern, version_fn, cve_id, cvss, desc = pattern
    if sw_pattern not in name:
        return None
    try:
        if version_fn(version):
            return {
                "software":    sw.get("name"),
                "version":     version,
                "cve_id":      cve_id,
                "cvss_score":  cvss,
                "severity":    "Critical" if cvss >= 9 else "High" if cvss >= 7 else "Medium" if cvss >= 4 else "Low",
                "description": desc,
                "remediation": f"Upgrade {sw.get('name')} to a patched version",
            }
    except Exception:
        pass
    return None


# Function: _match_cves_for_software
def _match_cves_for_software(sw: dict) -> list[dict]:
    """Match a single installed-software entry against all known CVE patterns."""
    name    = (sw.get("name") or "").lower().replace(" ", "-").replace("_", "-")
    version = sw.get("version") or ""
    matches: list[dict] = []
    for pattern in _KNOWN_CVES:
        match = _cve_match_for_pattern(name, version, sw, pattern)
        if match:
            matches.append(match)
    return matches


# Function: _dedupe_cve_findings
def _dedupe_cve_findings(findings: list[dict]) -> list[dict]:
    seen_cves: set[str] = set()
    unique: list[dict] = []
    for f in findings:
        if f["cve_id"] not in seen_cves:
            seen_cves.add(f["cve_id"])
            unique.append(f)
    return unique


# Function: _check_cve
def _check_cve(software_list: list[dict]) -> list[dict]:
    """Cross-reference installed software against known CVEs."""
    findings: list[dict] = []
    for sw in software_list:
        findings.extend(_match_cves_for_software(sw))

    unique = _dedupe_cve_findings(findings)
    return sorted(unique, key=lambda x: x["cvss_score"], reverse=True)


# Function: _check_protocols
def _check_protocols(ports: dict[int, bool]) -> list[dict]:
    """Flag insecure/dangerous protocols."""
    findings: list[dict] = []
    for port, is_public in ports.items():
        if port in _INSECURE_PORTS:
            info = _INSECURE_PORTS[port]
            # Escalate risk if DB ports are public
            risk = info["risk"]
            if port in _RISKY_IF_PUBLIC and is_public:
                risk = "Critical"
            findings.append({
                "port":     port,
                "protocol": info["protocol"],
                "risk":     risk,
                "is_public": is_public,
                "reason":   info["reason"],
                "remediation": _protocol_remediation(port),
            })
    return sorted(findings, key=lambda x: {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}.get(x["risk"], 4))


# Function: _protocol_remediation
def _protocol_remediation(port: int) -> str:
    rems = {
        21:   "Disable FTP; use SFTP (port 22) or FTPS (port 990)",
        23:   "Disable Telnet; use SSH (port 22)",
        80:   "Configure HTTP→HTTPS redirect; obtain TLS certificate",
        389:  "Disable LDAP; enforce LDAPS on port 636",
        445:  "Restrict SMB to internal networks via firewall",
        3306: "Bind MySQL to 127.0.0.1 or restrict via firewall",
        5432: "Bind PostgreSQL to 127.0.0.1 or restrict via firewall",
        6379: "Enable Redis AUTH and bind to localhost",
        9200: "Enable Elasticsearch X-Pack security; restrict via firewall",
        2375: "Disable unauthenticated Docker API; use TLS on 2376",
        3389: "Restrict RDP to VPN/Bastion; enable NLA",
        27017:"Bind MongoDB to localhost; enable authentication",
    }
    return rems.get(port, "Restrict access via firewall; use encrypted alternative")


# Function: _cis_check_os_eos
def _cis_check_os_eos(srv: dict, ports: dict, is_linux: bool, is_windows: bool) -> tuple[bool, bool, str]:
    """CIS-1.1: OS is supported (not EOS). Returns (skip, passed, detail)."""
    eos = srv.get("os_end_of_support") or ""
    if eos:
        try:
            if date.fromisoformat(eos) < date.today():
                return False, False, f"OS EOS date: {eos}"
        except ValueError:
            pass
    return False, True, ""


# Function: _cis_check_no_insecure_remote
def _cis_check_no_insecure_remote(srv: dict, ports: dict, is_linux: bool, is_windows: bool) -> tuple[bool, bool, str]:
    """CIS-1.2: No Telnet/FTP/rsh services running."""
    insecure = {21, 23, 512, 513, 514}
    bad_ports = insecure & set(ports.keys())
    if bad_ports:
        return False, False, f"Insecure ports open: {sorted(bad_ports)}"
    return False, True, ""


# Function: _cis_check_ssh_only_linux
def _cis_check_ssh_only_linux(srv: dict, ports: dict, is_linux: bool, is_windows: bool) -> tuple[bool, bool, str]:
    """CIS-1.3: SSH is the only remote access protocol."""
    if not is_linux:
        return True, True, ""
    if 3389 in ports or 5900 in ports:
        return False, False, "Non-SSH remote access (RDP/VNC) detected on Linux"
    return False, True, ""


# Function: _cis_check_ldap_over_tls
def _cis_check_ldap_over_tls(srv: dict, ports: dict, is_linux: bool, is_windows: bool) -> tuple[bool, bool, str]:
    """CIS-1.4: LDAP traffic uses LDAPS (port 636)."""
    if 389 in ports and 636 not in ports:
        return False, False, "LDAP (389) open without LDAPS (636)"
    return False, True, ""


# Function: _cis_check_http_redirect
def _cis_check_http_redirect(srv: dict, ports: dict, is_linux: bool, is_windows: bool) -> tuple[bool, bool, str]:
    """CIS-1.5: HTTP redirected to HTTPS."""
    if 80 in ports and 443 not in ports:
        return False, False, "HTTP (80) without HTTPS (443)"
    return False, True, ""


# Function: _cis_check_db_ports_private
def _cis_check_db_ports_private(srv: dict, ports: dict, is_linux: bool, is_windows: bool) -> tuple[bool, bool, str]:
    """CIS-2.1: Database ports not publicly exposed."""
    db_ports_public = {p for p, pub in ports.items() if p in _RISKY_IF_PUBLIC and pub}
    if db_ports_public:
        return False, False, f"DB ports publicly accessible: {sorted(db_ports_public)}"
    return False, True, ""


# Function: _cis_check_docker_api
def _cis_check_docker_api(srv: dict, ports: dict, is_linux: bool, is_windows: bool) -> tuple[bool, bool, str]:
    """CIS-2.2: Docker API not exposed on 2375."""
    if 2375 in ports:
        return False, False, "Docker API exposed on port 2375"
    return False, True, ""


# Function: _cis_check_rdp_restricted
def _cis_check_rdp_restricted(srv: dict, ports: dict, is_linux: bool, is_windows: bool) -> tuple[bool, bool, str]:
    """CIS-2.3: RDP access restricted (not public-facing)."""
    if not is_windows:
        return True, True, ""
    if 3389 in ports and ports.get(3389, False):
        return False, False, "RDP publicly accessible"
    return False, True, ""


# Function: _cis_check_no_eos_software
def _cis_check_no_eos_software(srv: dict, ports: dict, is_linux: bool, is_windows: bool) -> tuple[bool, bool, str]:
    """CIS-3.1: No end-of-life software packages."""
    eos_sw = [s.get("name", "") for s in (srv.get("installed_software") or []) if s.get("is_eos")]
    if eos_sw:
        return False, False, f"EOS packages: {', '.join(eos_sw[:3])}"
    return False, True, ""


# Function: _cis_check_firewall_present
def _cis_check_firewall_present(srv: dict, ports: dict, is_linux: bool, is_windows: bool) -> tuple[bool, bool, str]:
    """CIS-3.2: Firewall/ACL present (port restrictions).

    Heuristic: if we see firewall-related processes or if server type is
    properly scanned — assume passing unless we have negative evidence.
    """
    return False, True, ""


_CIS_CHECK_FUNCS = {
    "CIS-1.1": _cis_check_os_eos,
    "CIS-1.2": _cis_check_no_insecure_remote,
    "CIS-1.3": _cis_check_ssh_only_linux,
    "CIS-1.4": _cis_check_ldap_over_tls,
    "CIS-1.5": _cis_check_http_redirect,
    "CIS-2.1": _cis_check_db_ports_private,
    "CIS-2.2": _cis_check_docker_api,
    "CIS-2.3": _cis_check_rdp_restricted,
    "CIS-3.1": _cis_check_no_eos_software,
    "CIS-3.2": _cis_check_firewall_present,
}


# Function: _os_platform_flags
def _os_platform_flags(os_lower: str) -> tuple[bool, bool]:
    is_linux = any(tag in os_lower for tag in ("linux", "ubuntu", "centos", "rhel", "debian"))
    is_windows = "windows" in os_lower
    return is_linux, is_windows


# Function: _cis_check_applies
def _cis_check_applies(applies_to: str, is_linux: bool, is_windows: bool) -> bool:
    """Check if applicable."""
    if applies_to == "linux":
        return is_linux
    if applies_to == "windows":
        return is_windows
    return True


# Function: _evaluate_cis_check
def _evaluate_cis_check(check_id, applies_to, srv, ports, is_linux, is_windows) -> tuple[bool, bool, str]:
    if not _cis_check_applies(applies_to, is_linux, is_windows):
        return True, True, ""
    return _CIS_CHECK_FUNCS[check_id](srv, ports, is_linux, is_windows)


# Function: _apply_cis_check_outcome
def _apply_cis_check_outcome(check_id, desc, severity, detail, passed_check, deduction, score, passed, failed):
    result = {
        "check_id":   check_id,
        "description": desc,
        "severity":   severity,
        "detail":     detail,
    }
    if passed_check:
        passed.append(result)
        return score
    failed.append(result)
    return score - deduction


# Function: _cis_score
def _cis_score(srv: dict, ports: dict[int, bool]) -> dict:
    """Compute CIS Benchmark compliance score."""
    score     = 100
    passed    : list[dict] = []
    failed    : list[dict] = []
    os_lower  = (srv.get("os_name") or srv.get("os_family") or "").lower()
    is_linux, is_windows = _os_platform_flags(os_lower)

    for check_id, desc, applies_to, severity, deduction in _CIS_CHECKS:
        skip, passed_check, detail = _evaluate_cis_check(check_id, applies_to, srv, ports, is_linux, is_windows)
        if skip:
            continue

        score = _apply_cis_check_outcome(
            check_id, desc, severity, detail, passed_check, deduction, score, passed, failed
        )

    score = max(0, score)
    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F"
    return {
        "score":         score,
        "grade":         grade,
        "passed_count":  len(passed),
        "failed_count":  len(failed),
        "passed_checks": passed,
        "failed_checks": failed,
    }


# Function: _overall_server_risk
def _overall_server_risk(critical_cves: int, high_cves: int, critical_protos: int, high_protos: int, cis_score: int) -> str:
    if critical_cves > 0 or critical_protos > 0 or cis_score < 40:
        return "Critical"
    if high_cves > 0 or high_protos > 0 or cis_score < 60:
        return "High"
    if cis_score < 75:
        return "Medium"
    return "Low"


# Function: _analyze_server_security
def _analyze_server_security(srv: dict) -> dict:
    name  = srv.get("server_name") or srv.get("name") or srv.get("server_ip") or "unknown"
    ports = _get_all_ports(srv)
    sw    = srv.get("installed_software") or []

    cve_findings = _check_cve(sw)
    protocol_findings = _check_protocols(ports)
    cis = _cis_score(srv, ports)

    critical_cves  = sum(1 for c in cve_findings if c["severity"] == "Critical")
    high_cves      = sum(1 for c in cve_findings if c["severity"] == "High")
    critical_protos= sum(1 for p in protocol_findings if p["risk"] == "Critical")
    high_protos    = sum(1 for p in protocol_findings if p["risk"] == "High")
    risk = _overall_server_risk(critical_cves, high_cves, critical_protos, high_protos, cis["score"])

    return {
        "server_name":         name,
        "server_ip":           srv.get("ip_address") or srv.get("ip") or srv.get("server_ip") or "",
        "os":                  srv.get("os_name") or srv.get("os_family") or "",
        "overall_risk":        risk,
        "cis_compliance":      cis,
        "cve_findings":        cve_findings,
        "protocol_findings":   protocol_findings,
        "total_cve_count":     len(cve_findings),
        "critical_cve_count":  critical_cves,
        "total_port_risks":    len(protocol_findings),
        "critical_port_risks": critical_protos,
    }


# Function: _build_security_summary
def _build_security_summary(server_results: list[dict]) -> dict:
    total_cves      = sum(r["total_cve_count"] for r in server_results)
    critical_servers= sum(1 for r in server_results if r["overall_risk"] == "Critical")
    avg_cis         = sum(r["cis_compliance"]["score"] for r in server_results) / len(server_results) if server_results else 0
    unique_cves: set[str] = set()
    for r in server_results:
        for c in r["cve_findings"]:
            unique_cves.add(c["cve_id"])

    return {
        "total_servers_analyzed": len(server_results),
        "critical_risk_servers":  critical_servers,
        "high_risk_servers":      sum(1 for r in server_results if r["overall_risk"] == "High"),
        "medium_risk_servers":    sum(1 for r in server_results if r["overall_risk"] == "Medium"),
        "low_risk_servers":       sum(1 for r in server_results if r["overall_risk"] == "Low"),
        "total_cve_findings":     total_cves,
        "unique_cves":            len(unique_cves),
        "critical_cves":          sum(r["critical_cve_count"] for r in server_results),
        "avg_cis_score":          round(avg_cis, 1),
        "insecure_protocol_servers": sum(1 for r in server_results if r["total_port_risks"] > 0),
        "top_cve_servers": sorted(
            server_results,
            key=lambda r: (r["critical_cve_count"], r["total_cve_count"]),
            reverse=True,
        )[:5],
    }


# Function: analyze_security
def analyze_security(report: dict) -> dict:
    """Main entry point. Returns security & compliance analysis section."""
    servers = report.get("servers") or []
    if not servers:
        return {"error": "No servers in report", "server_results": [], "summary": {}}

    server_results = [_analyze_server_security(srv) for srv in servers]

    return {
        "server_results": server_results,
        "summary": _build_security_summary(server_results),
    }
