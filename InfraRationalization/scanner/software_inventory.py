#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Cross-platform installed software inventory collector.
# Date: 2026-05-14
# ---------------------------------------------------------------------------
"""
Cross-platform installed software inventory collector.

Can be run standalone on a local machine OR imported by onprem.py to execute
commands over SSH/WinRM on remote servers.

What it collects:
- Windows  : Installed software from Uninstall registry keys (HKLM + HKCU, x64 + x86)
- Linux    : Installed packages via dpkg-query (Debian/Ubuntu)
- Linux    : Installed packages via rpm (RHEL/CentOS/Fedora/SUSE)
- Linux    : Installed Flatpak applications
- Linux    : Installed Snap applications

Output formats (standalone mode):
- JSON
- CSV

Usage (standalone):
    python software_inventory.py [--json out.json] [--csv out.csv]

Import API (used by onprem.py):
    from scanner.software_inventory import (
        parse_dpkg_output,
        parse_rpm_output,
        parse_flatpak_output,
        parse_snap_output,
        parse_windows_registry_json,
        dedupe_software_records,
    )
"""

from __future__ import annotations

import argparse
import csv
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

if platform.system() == "Windows":
    try:
        import winreg  # type: ignore
    except ImportError:
        winreg = None  # type: ignore


# ─── Shared record schema ──────────────────────────────────────────────────────
# Each record is a plain dict with consistent keys so callers can normalise
# into InstalledSoftware dataclass objects easily.
RECORD_KEYS = (
    "os", "source", "name", "version", "publisher",
    "arch", "install_date", "install_location",
    "uninstall_string", "quiet_uninstall_string",
)


# Function: _blank_record
def _blank_record(**kwargs: Any) -> dict[str, Any]:
    rec: dict[str, Any] = {k: None for k in RECORD_KEYS}
    rec.update(kwargs)
    return rec


# ─── Deduplication ────────────────────────────────────────────────────────────

# Function: dedupe_software_records
def dedupe_software_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove duplicate records using a (os, source, name, version, publisher, arch,
    install_location) composite key.  First occurrence wins."""
    seen: set[tuple] = set()
    unique: list[dict[str, Any]] = []
    for r in records:
        key = (
            r.get("os"),
            r.get("source"),
            (r.get("name") or "").lower().strip(),
            (r.get("version") or "").strip(),
            (r.get("publisher") or "").strip(),
            r.get("arch"),
            r.get("install_location"),
        )
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


# ─── Linux parsers (operate on already-collected command output strings) ──────

# Function: parse_dpkg_output
def parse_dpkg_output(output: str) -> list[dict[str, Any]]:
    """
    Parse output of:
        dpkg-query -W -f='${binary:Package}\\t${Version}\\t${Maintainer}\\t${Architecture}\\t${db:Status-Date}\\n'
    Returns list of record dicts.
    """
    records: list[dict[str, Any]] = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        name    = parts[0].strip()
        version = parts[1].strip() if len(parts) > 1 else ""
        vendor  = parts[2].strip() if len(parts) > 2 else ""
        arch    = parts[3].strip() if len(parts) > 3 else ""
        raw_date = parts[4].strip() if len(parts) > 4 else ""
        if not name:
            continue
        install_date = _parse_date(raw_date)
        records.append(_blank_record(
            os="Linux", source="dpkg",
            name=name, version=version,
            publisher=vendor, arch=arch,
            install_date=install_date or None,
        ))
    return records


# Function: parse_rpm_output
def parse_rpm_output(output: str) -> list[dict[str, Any]]:
    """
    Parse output of:
        rpm -qa --qf '%{NAME}\\t%{VERSION}-%{RELEASE}\\t%{VENDOR}\\t%{ARCH}\\t%{INSTALLTIME:date}\\n'
    Returns list of record dicts.
    """
    records: list[dict[str, Any]] = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        name    = parts[0].strip()
        version = parts[1].strip() if len(parts) > 1 else ""
        vendor  = parts[2].strip() if len(parts) > 2 else ""
        arch    = parts[3].strip() if len(parts) > 3 else ""
        raw_date = parts[4].strip() if len(parts) > 4 else ""
        if not name:
            continue
        install_date = _parse_date(raw_date)
        records.append(_blank_record(
            os="Linux", source="rpm",
            name=name, version=version,
            publisher=vendor, arch=arch,
            install_date=install_date or None,
        ))
    return records


# Function: parse_flatpak_output
def parse_flatpak_output(output: str) -> list[dict[str, Any]]:
    """
    Parse output of:
        flatpak list --app --columns=application,name,version,installation
    Returns list of record dicts.
    """
    records: list[dict[str, Any]] = []
    lines = output.splitlines()
    if not lines:
        return records
    # Skip header line if present (first line often starts with "Application ID")
    start = 1 if (lines and "Application" in lines[0]) else 0
    for line in lines[start:]:
        line = line.strip()
        if not line:
            continue
        # Try tab-separated first, then whitespace
        parts = line.split("\t") if "\t" in line else line.split(None, 3)
        if len(parts) < 3:
            continue
        app_id      = parts[0].strip()
        name        = parts[1].strip() if len(parts) > 1 else app_id
        version     = parts[2].strip() if len(parts) > 2 else ""
        installation = parts[3].strip() if len(parts) > 3 else ""
        records.append(_blank_record(
            os="Linux",
            source=f"flatpak:{installation}" if installation else "flatpak",
            name=name or app_id,
            version=version,
        ))
    return records


# Function: parse_snap_output
def parse_snap_output(output: str) -> list[dict[str, Any]]:
    """
    Parse output of:
        snap list
    Returns list of record dicts.
    """
    records: list[dict[str, Any]] = []
    lines = output.splitlines()
    # Skip header line
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        name    = parts[0]
        version = parts[1]
        records.append(_blank_record(
            os="Linux", source="snap",
            name=name, version=version,
            publisher="Canonical Snap",
        ))
    return records


# ─── Windows parser (operates on JSON from WinRM PowerShell output) ───────────

# Function: parse_windows_registry_json
def parse_windows_registry_json(
    json_text: str,
    arch_label: str = "x64_or_native",
    hive: str = "HKLM",
) -> list[dict[str, Any]]:
    """
    Parse JSON output from the PowerShell registry query:
        Get-ItemProperty HKLM:\\...\\Uninstall\\* |
          Select-Object DisplayName, DisplayVersion, Publisher, InstallDate,
                        InstallLocation, UninstallString, QuietUninstallString |
          ConvertTo-Json

    arch_label: "x64_or_native" for the main Uninstall hive, "x86" for WOW6432Node.
    hive:       "HKLM" or "HKCU".
    """
    records: list[dict[str, Any]] = []
    try:
        items = json.loads(json_text)
    except Exception:
        return records
    if isinstance(items, dict):
        items = [items]
    for item in (items or []):
        name = (item.get("DisplayName") or "").strip()
        if not name:
            continue
        raw_date = str(item.get("InstallDate") or "").strip()
        install_date = None
        if raw_date:
            import re
            if re.match(r"^\d{8}$", raw_date):
                install_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
            elif re.match(r"\d{4}-\d{2}-\d{2}", raw_date):
                install_date = raw_date[:10]
        records.append(_blank_record(
            os="Windows",
            source="registry_uninstall",
            name=name,
            version=(item.get("DisplayVersion") or "").strip() or None,
            publisher=(item.get("Publisher") or "").strip() or None,
            arch=arch_label,
            install_date=install_date,
            install_location=(item.get("InstallLocation") or "").strip() or None,
            uninstall_string=(item.get("UninstallString") or "").strip() or None,
            quiet_uninstall_string=(item.get("QuietUninstallString") or "").strip() or None,
        ))
    return records


# ─── Date normalisation helper ────────────────────────────────────────────────

# Function: _parse_date
def _parse_date(raw: str) -> str:
    """Convert various date strings to ISO YYYY-MM-DD or return empty string."""
    if not raw:
        return ""
    import re
    # Already ISO
    if re.match(r"\d{4}-\d{2}-\d{2}", raw):
        return raw[:10]
    from datetime import datetime
    for fmt in (
        "%a %b %d %H:%M:%S %Y",   # dpkg: "Mon Jan 01 00:00:00 2024"
        "%a %d %b %Y %H:%M:%S %Z",  # rpm:  "Mon 01 Jan 2024 12:00:00 UTC"
        "%a %d %b %Y %H:%M:%S",
        "%Y%m%d",                    # Windows YYYYMMDD
    ):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


# ─── Local collection (standalone mode) ───────────────────────────────────────

# Function: _run_command
def _run_command(cmd: list[str]) -> str:
    """Run a subprocess command and return stdout, empty string on failure."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, check=True,
            encoding="utf-8", errors="replace",
        )
        return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError, PermissionError):
        return ""


# Function: _get_windows_apps_local
def _get_windows_apps_local() -> list[dict[str, Any]]:
    """Collect installed apps from the Windows registry on the local machine."""
    if winreg is None:
        return []
    records: list[dict[str, Any]] = []

    registry_locations = [
        (winreg.HKEY_LOCAL_MACHINE,
         r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
         "x64_or_native", "HKLM"),
        (winreg.HKEY_LOCAL_MACHINE,
         r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
         "x86", "HKLM"),
        (winreg.HKEY_CURRENT_USER,
         r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
         "x64_or_native", "HKCU"),
    ]

    # Function: _read
    def _read(subkey: Any, name: str) -> Any:
        try:
            value, _ = winreg.QueryValueEx(subkey, name)
            return value
        except OSError:
            return None

    for hive, path, arch_label, hive_name in registry_locations:
        try:
            with winreg.OpenKey(hive, path) as root:
                idx = 0
                while True:
                    try:
                        child_name = winreg.EnumKey(root, idx)
                        idx += 1
                    except OSError:
                        break
                    try:
                        with winreg.OpenKey(root, child_name) as subkey:
                            display_name = _read(subkey, "DisplayName")
                            if not display_name:
                                continue
                            raw_date = str(_read(subkey, "InstallDate") or "")
                            records.append(_blank_record(
                                os="Windows",
                                source="registry_uninstall",
                                name=str(display_name).strip(),
                                version=_read(subkey, "DisplayVersion"),
                                publisher=_read(subkey, "Publisher"),
                                arch=arch_label,
                                install_date=_parse_date(raw_date) or None,
                                install_location=_read(subkey, "InstallLocation"),
                                uninstall_string=_read(subkey, "UninstallString"),
                                quiet_uninstall_string=_read(subkey, "QuietUninstallString"),
                            ))
                    except OSError:
                        continue
        except OSError:
            continue
    return records


# Function: _get_linux_dpkg_local
def _get_linux_dpkg_local() -> list[dict[str, Any]]:
    if not shutil.which("dpkg-query"):
        return []
    out = _run_command([
        "dpkg-query", "-W",
        "-f=${binary:Package}\t${Version}\t${Maintainer}\t${Architecture}\t${db:Status-Date}\n",
    ])
    return parse_dpkg_output(out)


# Function: _get_linux_rpm_local
def _get_linux_rpm_local() -> list[dict[str, Any]]:
    if not shutil.which("rpm"):
        return []
    out = _run_command([
        "rpm", "-qa", "--qf",
        r"%{NAME}\t%{VERSION}-%{RELEASE}\t%{VENDOR}\t%{ARCH}\t%{INSTALLTIME:date}\n",
    ])
    return parse_rpm_output(out)


# Function: _get_linux_flatpak_local
def _get_linux_flatpak_local() -> list[dict[str, Any]]:
    if not shutil.which("flatpak"):
        return []
    out = _run_command([
        "flatpak", "list", "--app",
        "--columns=application,name,version,installation",
    ])
    return parse_flatpak_output(out)


# Function: _get_linux_snap_local
def _get_linux_snap_local() -> list[dict[str, Any]]:
    if not shutil.which("snap"):
        return []
    out = _run_command(["snap", "list"])
    return parse_snap_output(out)


# Function: collect_inventory
def collect_inventory() -> list[dict[str, Any]]:
    """Collect full software inventory for the local machine."""
    system = platform.system()
    records: list[dict[str, Any]] = []
    if system == "Windows":
        records.extend(_get_windows_apps_local())
    elif system == "Linux":
        records.extend(_get_linux_dpkg_local())
        records.extend(_get_linux_rpm_local())
        records.extend(_get_linux_flatpak_local())
        records.extend(_get_linux_snap_local())
    else:
        raise RuntimeError(f"Unsupported OS: {system}")
    records = dedupe_software_records(records)
    records.sort(key=lambda r: ((r.get("name") or "").lower(), (r.get("source") or "")))
    return records


# ─── Output writers ───────────────────────────────────────────────────────────

# Function: write_json
def write_json(records: list[dict[str, Any]], path: Path) -> None:
    path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")


# Function: write_csv
def write_csv(records: list[dict[str, Any]], path: Path) -> None:
    if not records:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = sorted({k for r in records for k in r.keys()})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


# ─── CLI entry point ──────────────────────────────────────────────────────────

# Function: main
def main() -> int:
    parser = argparse.ArgumentParser(description="Installed software inventory collector")
    parser.add_argument("--json", default="software_inventory.json", help="JSON output path")
    parser.add_argument("--csv",  default="software_inventory.csv",  help="CSV output path")
    args = parser.parse_args()
    try:
        records = collect_inventory()
        write_json(records, Path(args.json))
        write_csv(records, Path(args.csv))
        print(f"Collected {len(records)} records")
        print(f"JSON: {args.json}")
        print(f"CSV : {args.csv}")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
