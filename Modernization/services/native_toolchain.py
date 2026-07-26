# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Shared native compiler configuration for generated C and C++ sources.
# Date: 2025-08-29
# ---------------------------------------------------------------------------
"""Shared native compiler configuration for generated C and C++ sources."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List


_INCLUDE_PATH_ENV = "MODERNIZATION_NATIVE_INCLUDE_PATHS"
_WINDOWS_INCLUDE_ROOTS = (
    Path(r"C:\Ruby33-x64\msys64\ucrt64\include"),
    Path(r"C:\msys64\ucrt64\include"),
)


# Function: _configured_include_roots
def _configured_include_roots() -> Iterable[Path]:
    configured = os.environ.get(_INCLUDE_PATH_ENV, "")
    for value in configured.split(os.pathsep):
        if value.strip():
            yield Path(value.strip())
    if os.name == "nt":
        yield from _WINDOWS_INCLUDE_ROOTS


# Function: native_include_args
def native_include_args() -> List[str]:
    """Return trusted dependency include roots after the compiler system paths.

    ``-idirafter`` is deliberate: generated code must continue to use the
    compiler's own C runtime headers, while optional SDK headers such as
    sqlite3.h can be resolved from an installed MSYS2 development package.
    """
    arguments: List[str] = []
    seen = set()
    for root in _configured_include_roots():
        resolved = root.resolve()
        key = os.path.normcase(str(resolved))
        if key in seen or not resolved.is_dir():
            continue
        seen.add(key)
        arguments.extend(("-idirafter", str(resolved)))
    return arguments
