# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §4a static validation — real subprocess-based `tsc --noEmit`, no OS Job Object
# Date: 2026-05-02
# ---------------------------------------------------------------------------
"""§4a static validation — real subprocess-based `tsc --noEmit`, no OS Job Object
sandbox this pass (that was a separate, already-agreed scope cut about infra
provisioning — see PROGRESS.md; `deploy/sandbox/Provision-Sandbox.ps1` is the
ready-to-run hardening path once it's actually needed).

`npm install` never runs at validation time (spec §4a) — the toolchain
(typescript/eslint/@playwright/test/selenium-webdriver) is pre-installed once into
TraceForge/toolchain/node_modules, and each validation run gets a fresh scratch
directory with a Windows junction pointing at that node_modules so TypeScript's normal
directory-walk-up module resolution finds it without copying or reinstalling.
"""
from __future__ import annotations

import asyncio
import shutil
import subprocess
import uuid
from pathlib import Path

from traceforge.config import SANDBOX_DIR

_TOOLCHAIN_DIR = Path(__file__).resolve().parents[4] / "toolchain"
_TOOLCHAIN_NODE_MODULES = _TOOLCHAIN_DIR / "node_modules"
_TSC = _TOOLCHAIN_NODE_MODULES / ".bin" / "tsc.cmd"
_VALIDATION_TIMEOUT_SECONDS = 60


# Function: _ensure_junction
def _ensure_junction(scratch_dir: Path) -> None:
    target = scratch_dir / "node_modules"
    if target.exists():
        return
    subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(target), str(_TOOLCHAIN_NODE_MODULES)],
        capture_output=True, check=True,
    )


# Function: _cleanup
def _cleanup(scratch_dir: Path) -> None:
    node_modules = scratch_dir / "node_modules"
    if node_modules.exists():
        node_modules.unlink() if node_modules.is_symlink() else subprocess.run(["cmd", "/c", "rmdir", str(node_modules)], capture_output=True)
    shutil.rmtree(scratch_dir, ignore_errors=True)


# Function: validate_typescript
async def validate_typescript(code: str, run_id: str | None = None) -> tuple[bool | None, str]:
    """Returns (compiles, output). compiles=None means the toolchain wasn't available
    (never crashes the caller — a validation-infra problem must not block a pipeline run)."""
    if not _TSC.exists():
        return None, "TypeScript toolchain not installed at TraceForge/toolchain — run `npm install` there once."

    scratch_dir = SANDBOX_DIR / (run_id or uuid.uuid4().hex)
    scratch_dir.mkdir(parents=True, exist_ok=True)
    script_path = scratch_dir / "script.spec.ts"
    script_path.write_text(code, encoding="utf-8")

    try:
        _ensure_junction(scratch_dir)
        try:
            proc = await asyncio.to_thread(
                subprocess.run,
                [
                    str(_TSC), "--noEmit", "--target", "ES2020", "--module", "esnext",
                    "--moduleResolution", "bundler", "--esModuleInterop", "--skipLibCheck",
                    "script.spec.ts",
                ],
                cwd=str(scratch_dir), capture_output=True, timeout=_VALIDATION_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            return False, f"tsc timed out after {_VALIDATION_TIMEOUT_SECONDS}s"
        output = (proc.stdout.decode(errors="replace") + proc.stderr.decode(errors="replace")).strip()
        return proc.returncode == 0, output or "OK"
    finally:
        _cleanup(scratch_dir)
