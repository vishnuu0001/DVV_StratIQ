# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Safe executable discovery for service processes with stale Windows PATHs.
# Date: 2025-09-20
# ---------------------------------------------------------------------------
"""Safe executable discovery for service processes with stale Windows PATHs."""
from __future__ import annotations

import os
import shutil
import glob
from pathlib import Path
from typing import Dict, Optional


_WINDOWS_TOOL_PATTERNS = {
    "go": (r"C:\msys64\ucrt64\bin\go.exe",),
    "gofmt": (r"C:\msys64\ucrt64\bin\gofmt.exe",),
    "rustc": (r"C:\Program Files\Rust stable MSVC *\bin\rustc.exe",),
    "cargo": (r"C:\Program Files\Rust stable MSVC *\bin\cargo.exe",),
    "gradle": (r"C:\msys64\ucrt64\bin\gradle.bat", r"C:\Tools\gradle-*\bin\gradle.bat"),
    "sbt": (r"C:\msys64\ucrt64\bin\sbt.bat", r"C:\Program Files\sbt\bin\sbt.bat", r"C:\Program Files (x86)\sbt\bin\sbt.bat"),
    "composer": (
        r"C:\msys64\ucrt64\bin\composer.bat",
        r"C:\Tools\Composer\composer.bat",
        r"C:\ProgramData\ComposerSetup\bin\composer.bat",
    ),
    "flutter": (
        r"C:\msys64\ucrt64\bin\flutter.bat",
        r"C:\src\flutter\bin\flutter.bat",
        r"%LOCALAPPDATA%\Programs\Flutter\bin\flutter.bat",
    ),
    "cabal": (r"%APPDATA%\cabal\bin\cabal.exe", r"C:\ghcup\bin\cabal.exe"),
    "stack": (r"%APPDATA%\local\bin\stack.exe", r"C:\ghcup\bin\stack.exe"),
    "bundle": (r"C:\Ruby*\bin\bundle.cmd", r"C:\Ruby*\bin\bundle.bat"),
    "swiftc": (r"%LOCALAPPDATA%\Programs\Swift\Toolchains\*\usr\bin\swiftc.exe",),
    "swift": (r"%LOCALAPPDATA%\Programs\Swift\Toolchains\*\usr\bin\swift.exe",),
    "rscript": (r"C:\Program Files\R\R-*\bin\Rscript.exe", r"C:\msys64\ucrt64\bin\Rscript.exe"),
    "erlc": (r"C:\Program Files\Erlang OTP\bin\erlc.exe",),
    "erl": (r"C:\Program Files\Erlang OTP\bin\erl.exe",),
    "swipl": (r"C:\Program Files\swipl\bin\swipl.exe",),
    "julia": (r"%LOCALAPPDATA%\Programs\Julia-*\bin\julia.exe",),
    "dart": (
        r"C:\msys64\ucrt64\bin\dart.exe",
        r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Google.DartSDK_*\dart-sdk\bin\dart.exe",
    ),
    "terraform": (r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Hashicorp.Terraform_*\terraform.exe",),
    "fpc": (r"C:\FPC\*\bin\*\fpc.exe",),
    "scalac": (r"C:\msys64\ucrt64\bin\scalac.bat", r"C:\Program Files (x86)\scala\bin\scalac.bat"),
    "sbcl": (r"C:\Program Files\Steel Bank Common Lisp\sbcl.exe",),
    "gfortran": (r"C:\Ruby33-x64\msys64\ucrt64\bin\gfortran.exe",),
    "gnatmake": (r"C:\Ruby33-x64\msys64\ucrt64\bin\gnatmake.exe",),
    "protoc": (
        r"C:\msys64\ucrt64\bin\protoc.exe",
        r"C:\Ruby33-x64\msys64\ucrt64\bin\protoc.exe",
        r"C:\Tools\protobuf\bin\protoc.exe",
        r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Google.Protobuf_*\bin\protoc.exe",
    ),
    "cobc": (r"C:\Ruby33-x64\msys64\ucrt64\bin\cobc.exe",),
    "bash": (r"C:\Program Files\Git\bin\bash.exe",),
    "kotlinc": (
        r"C:\msys64\ucrt64\bin\kotlinc.bat",
        r"C:\Tools\Kotlin-*\kotlinc\bin\kotlinc.bat",
        r"C:\Tools\Kotlin-*\bin\kotlinc.bat",
    ),
    "php": (
        r"C:\msys64\ucrt64\bin\php.exe",
        r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\PHP.PHP.8.3_*\php.exe",
        r"C:\Users\*\AppData\Local\Microsoft\WinGet\Packages\PHP.PHP.8.3_*\php.exe",
        r"C:\php\php.exe",
        r"C:\Program Files\PHP\php.exe",
        r"C:\xampp\php\php.exe",
    ),
    "clojure": (
        r"C:\Program Files\Clojure\clojure.exe",
        r"C:\Program Files\Clojure\clojure.cmd",
        r"C:\Program Files\Clojure\bin\clojure.bat",
    ),
    "elixirc": (r"C:\Tools\Elixir-*-otp-*\bin\elixirc.bat",),
    "elixir": (r"C:\Tools\Elixir-*-otp-*\bin\elixir.bat",),
    "mix": (r"C:\Tools\Elixir-*-otp-*\bin\mix.bat",),
}

_ERLANG_TOOLS = {"elixir.bat", "elixirc.bat", "mix.bat"}
_JAVA_TOOLS = {
    "gradle", "gradle.bat", "sbt", "sbt.bat", "kotlinc", "kotlinc.bat",
    "scalac", "scalac.bat",
}


def _prepend_path(environment: Dict[str, str], directory: str) -> None:
    environment["PATH"] = directory + os.pathsep + environment.get("PATH", "")


def _configure_swift(environment: Dict[str, str], _executable: Path) -> None:
    runtime_pattern = os.path.expandvars(
        r"%LOCALAPPDATA%\Programs\Swift\Runtimes\*\usr\bin",
    )
    runtimes = sorted(glob.glob(runtime_pattern), reverse=True)
    if runtimes:
        _prepend_path(environment, runtimes[0])


def _configure_erlang(environment: Dict[str, str], _executable: Path) -> None:
    _prepend_path(environment, r"C:\Program Files\Erlang OTP\bin")


def _configure_cobol(environment: Dict[str, str], executable: Path) -> None:
    executable_dir = executable.parent
    config_dir = executable_dir.parent / "share" / "gnucobol" / "config"
    if config_dir.is_dir():
        environment["COB_CONFIG_DIR"] = str(config_dir)
    _prepend_path(environment, str(executable_dir))


def _configure_msys_tool(
    environment: Dict[str, str], executable: Path, variable: str, relative_home: Path,
) -> None:
    if "msys64" not in str(executable).casefold():
        return
    home = executable.parent.parent / relative_home
    if home.is_dir():
        environment[variable] = str(home)
    _prepend_path(environment, str(executable.parent))


def _configure_go(environment: Dict[str, str], executable: Path) -> None:
    _configure_msys_tool(environment, executable, "GOROOT", Path("lib") / "go")


def _configure_r(environment: Dict[str, str], executable: Path) -> None:
    _configure_msys_tool(environment, executable, "R_HOME", Path("lib") / "R")


def _discover_java_home() -> str:
    for candidate in sorted(Path(r"C:\Program Files\Eclipse Adoptium").glob("jdk-*"), reverse=True):
        if (candidate / "bin" / "java.exe").is_file():
            return str(candidate)
    return ""


def _configure_java(environment: Dict[str, str], _executable: Path) -> None:
    java_home = environment.get("JAVA_HOME", "").strip() or _discover_java_home()
    if not java_home:
        return
    environment["JAVA_HOME"] = java_home
    java_bin = str(Path(java_home) / "bin")
    if java_bin not in environment.get("PATH", ""):
        _prepend_path(environment, java_bin)


_ENVIRONMENT_HANDLERS = {
    "swiftc.exe": _configure_swift,
    "cobc.exe": _configure_cobol,
    "go.exe": _configure_go,
    "rscript.exe": _configure_r,
    **dict.fromkeys(_ERLANG_TOOLS, _configure_erlang),
    **dict.fromkeys(_JAVA_TOOLS, _configure_java),
}


# Function: find_executable
def find_executable(command: str) -> Optional[str]:
    """Find a tool without executing it or searching untrusted project paths."""
    if os.name == "nt":
        patterns = _WINDOWS_TOOL_PATTERNS.get(command.casefold(), ())
        for pattern in patterns:
            try:
                matches = [Path(match) for match in sorted(
                    glob.glob(os.path.expandvars(pattern)), reverse=True,
                )]
            except OSError:
                continue
            for candidate in matches:
                if candidate.is_file():
                    return str(candidate)
    return shutil.which(command) or shutil.which(f"{command}.cmd")


# Function: executable_environment
def executable_environment(executable: str) -> Dict[str, str]:
    """Return the minimal environment additions required by an installed tool."""
    environment = os.environ.copy()
    if os.name != "nt":
        return environment
    executable_path = Path(executable)
    handler = _ENVIRONMENT_HANDLERS.get(executable_path.name.casefold())
    if handler:
        handler(environment, executable_path)
    return environment
