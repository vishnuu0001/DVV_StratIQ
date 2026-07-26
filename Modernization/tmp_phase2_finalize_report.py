from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from api.server import target_stacks
from services.build_runner import toolchain_status


def main() -> None:
    ts = datetime.now(timezone.utc).isoformat()
    status = toolchain_status()
    missing = [item.get("id") for item in status.get("catalog", []) if not item.get("installed")]

    stacks = asyncio.run(target_stacks())
    stack_list = stacks.get("stacks", [])
    unavailable = [s for s in stack_list if not s.get("available")]

    report = {
        "generated_at": ts,
        "all_stacks_available": len(unavailable) == 0,
        "missing_toolchains": missing,
        "stack_summary": {
            "total_stacks": len(stack_list),
            "available_stacks": len(stack_list) - len(unavailable),
            "unavailable_stacks": len(unavailable),
            "unavailable_stack_ids": [s.get("id") for s in unavailable],
        },
    }

    Path("toolchain_phase2_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Modernization Stack Availability Report",
        "",
        f"Generated: {ts}",
        "",
        "## Overall",
        f"- all_stacks_available: {report['all_stacks_available']}",
        f"- total_stacks: {report['stack_summary']['total_stacks']}",
        f"- available_stacks: {report['stack_summary']['available_stacks']}",
        f"- unavailable_stacks: {report['stack_summary']['unavailable_stacks']}",
        "",
        "## Toolchains",
        f"- missing_after: {', '.join(missing) if missing else 'none'}",
        "",
        "## Unavailable Stack IDs",
    ]
    if report["stack_summary"]["unavailable_stack_ids"]:
        lines.extend([f"- {item}" for item in report["stack_summary"]["unavailable_stack_ids"]])
    else:
        lines.append("- none")

    Path("ALL_STACKS_AVAILABILITY_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Wrote toolchain_phase2_report.json")
    print("Wrote ALL_STACKS_AVAILABILITY_REPORT.md")


if __name__ == "__main__":
    main()
