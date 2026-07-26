from __future__ import annotations

import asyncio
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from api.server import _TOOLCHAIN_PACKAGES, target_stacks
from services.build_runner import toolchain_status


def _winget_has_package(package_id: str) -> bool:
    cmd = ["winget", "list", "--id", package_id, "--exact", "--accept-source-agreements"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return False
    combined = (proc.stdout + "\n" + proc.stderr).lower()
    return package_id.lower() in combined


def _run_install(package_id: str) -> tuple[bool, str]:
    cmd = [
        "winget",
        "install",
        "--id",
        package_id,
        "--exact",
        "--silent",
        "--disable-interactivity",
        "--accept-package-agreements",
        "--accept-source-agreements",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired as exc:
        out = ((exc.stdout or "") + "\n" + (exc.stderr or "")).strip()
        return False, ("winget install timed out after 180s\n" + out)[-4000:]
    output = (proc.stdout + "\n" + proc.stderr).strip()
    if proc.returncode == 0:
        return True, output[-4000:]
    return False, output[-4000:]


def _stack_summary() -> dict:
    stacks = asyncio.run(target_stacks())
    stack_list = stacks.get("stacks", [])
    unavailable = [s for s in stack_list if not s.get("available")]
    return {
        "total_stacks": len(stack_list),
        "available_stacks": len(stack_list) - len(unavailable),
        "unavailable_stacks": len(unavailable),
        "supported_languages": stacks.get("supported_languages", []),
        "externally_gated_languages": stacks.get("externally_gated_languages", []),
        "supported_artifacts": stacks.get("supported_artifacts", []),
        "externally_gated_artifacts": stacks.get("externally_gated_artifacts", []),
        "unavailable_stack_ids": [s.get("id") for s in unavailable],
    }


def main() -> None:
    started_at = datetime.now(timezone.utc)
    before = toolchain_status()
    catalog_before = before.get("catalog", [])
    missing = [item for item in catalog_before if not item.get("installed")]

    install_attempts = []
    for item in missing:
        tool_id = item.get("id")
        package_id = _TOOLCHAIN_PACKAGES.get(tool_id)
        if not package_id:
            install_attempts.append({
                "tool_id": tool_id,
                "package_id": None,
                "installed": False,
                "status": "skipped-no-winget-mapping",
                "output": "No package mapping exists in api.server::_TOOLCHAIN_PACKAGES",
            })
            continue
        if _winget_has_package(package_id):
            install_attempts.append({
                "tool_id": tool_id,
                "package_id": package_id,
                "installed": True,
                "status": "already-present",
                "output": "Package already present according to winget list.",
            })
            continue
        print(f"Installing {tool_id} via {package_id}...", flush=True)
        ok, output = _run_install(package_id)
        install_attempts.append({
            "tool_id": tool_id,
            "package_id": package_id,
            "installed": ok,
            "status": "installed" if ok else "failed",
            "output": output,
        })

    after = toolchain_status()
    catalog_after = after.get("catalog", [])
    after_missing = [item.get("id") for item in catalog_after if not item.get("installed")]
    stack = _stack_summary()

    report = {
        "started_at": started_at.isoformat(),
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "missing_before": [item.get("id") for item in missing],
        "install_attempts": install_attempts,
        "missing_after": after_missing,
        "all_stacks_available": stack["unavailable_stacks"] == 0,
        "stack_summary": stack,
    }

    out_json = Path("toolchain_phase2_report.json")
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    out_md = Path("ALL_STACKS_AVAILABILITY_REPORT.md")
    lines = []
    lines.append("# Modernization Stack Availability Report")
    lines.append("")
    lines.append(f"Generated: {report['finished_at']}")
    lines.append("")
    lines.append("## Overall")
    lines.append(f"- all_stacks_available: {report['all_stacks_available']}")
    lines.append(f"- total_stacks: {stack['total_stacks']}")
    lines.append(f"- available_stacks: {stack['available_stacks']}")
    lines.append(f"- unavailable_stacks: {stack['unavailable_stacks']}")
    lines.append("")
    lines.append("## Toolchains")
    lines.append(f"- missing_before: {', '.join(report['missing_before']) if report['missing_before'] else 'none'}")
    lines.append(f"- missing_after: {', '.join(report['missing_after']) if report['missing_after'] else 'none'}")
    lines.append("")
    lines.append("## Installation Attempts")
    if install_attempts:
        for attempt in install_attempts:
            lines.append(f"- {attempt['tool_id']}: {attempt['status']}" + (f" ({attempt['package_id']})" if attempt['package_id'] else ""))
    else:
        lines.append("- No missing toolchains required installation.")
    lines.append("")
    lines.append("## Unavailable Stack IDs")
    if stack["unavailable_stack_ids"]:
        for stack_id in stack["unavailable_stack_ids"]:
            lines.append(f"- {stack_id}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Supported Languages")
    for language in stack["supported_languages"]:
        lines.append(f"- {language}")
    lines.append("")
    lines.append("## Externally Gated Languages")
    if stack["externally_gated_languages"]:
        for language in stack["externally_gated_languages"]:
            lines.append(f"- {language}")
    else:
        lines.append("- none")

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
