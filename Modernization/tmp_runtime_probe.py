import asyncio
import json
from api.server import target_stacks
from services.build_runner import toolchain_status


def main() -> None:
    status = toolchain_status()
    catalog = status.get("catalog", [])
    summary = {
        "installed": [item["id"] for item in catalog if item.get("installed")],
        "missing": [item["id"] for item in catalog if not item.get("installed")],
        "installable_missing": [item["id"] for item in catalog if (not item.get("installed")) and item.get("installable")],
    }
    stacks = asyncio.run(target_stacks())
    stack_summary = {
        "total_stacks": len(stacks.get("stacks", [])),
        "supported_languages": len(stacks.get("supported_languages", [])),
        "externally_gated_languages": len(stacks.get("externally_gated_languages", [])),
        "supported_artifacts": len(stacks.get("supported_artifacts", [])),
        "externally_gated_artifacts": len(stacks.get("externally_gated_artifacts", [])),
    }
    payload = {"toolchains": summary, "stack_summary": stack_summary}
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
