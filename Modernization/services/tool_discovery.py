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
    "protoc": (r"C:\Ruby33-x64\msys64\ucrt64\bin\protoc.exe",),
    "cobc": (r"C:\Ruby33-x64\msys64\ucrt64\bin\cobc.exe",),
    "bash": (r"C:\Program Files\Git\bin\bash.exe",),
    "kotlinc": (
        r"C:\msys64\ucrt64\bin\kotlinc.bat",
        r"C:\Tools\Kotlin-*\kotlinc\bin\kotlinc.bat",
        r"C:\Tools\Kotlin-*\bin\kotlinc.bat",
    ),
    "php": (r"C:\msys64\ucrt64\bin\php.exe",),
    "clojure": (
        r"C:\Program Files\Clojure\clojure.exe",
        r"C:\Program Files\Clojure\clojure.cmd",
        r"C:\Program Files\Clojure\bin\clojure.bat",
    ),
    "elixirc": (r"C:\Tools\Elixir-*-otp-*\bin\elixirc.bat",),
    "elixir": (r"C:\Tools\Elixir-*-otp-*\bin\elixir.bat",),
    "mix": (r"C:\Tools\Elixir-*-otp-*\bin\mix.bat",),
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
    if os.name == "nt" and Path(executable).name.casefold() == "swiftc.exe":
        runtime_pattern = os.path.expandvars(
            r"%LOCALAPPDATA%\Programs\Swift\Runtimes\*\usr\bin",
        )
        runtimes = sorted(glob.glob(runtime_pattern), reverse=True)
        if runtimes:
            environment["PATH"] = runtimes[0] + os.pathsep + environment.get("PATH", "")
    if os.name == "nt" and Path(executable).name.casefold() in {
        "elixir.bat", "elixirc.bat", "mix.bat",
    }:
        environment["PATH"] = (
            r"C:\Program Files\Erlang OTP\bin" + os.pathsep
            + environment.get("PATH", "")
        )
    if os.name == "nt" and Path(executable).name.casefold() == "cobc.exe":
        executable_dir = Path(executable).parent
        config_dir = executable_dir.parent / "share" / "gnucobol" / "config"
        if config_dir.is_dir():
            environment["COB_CONFIG_DIR"] = str(config_dir)
        environment["PATH"] = str(executable_dir) + os.pathsep + environment.get("PATH", "")
    if os.name == "nt" and Path(executable).name.casefold() == "go.exe":
        executable_path = Path(executable)
        if "msys64" in str(executable_path).casefold():
            goroot = executable_path.parent.parent / "lib" / "go"
            if goroot.is_dir():
                environment["GOROOT"] = str(goroot)
            environment["PATH"] = str(executable_path.parent) + os.pathsep + environment.get("PATH", "")
    if os.name == "nt" and Path(executable).name.casefold() == "rscript.exe":
        executable_path = Path(executable)
        if "msys64" in str(executable_path).casefold():
            r_home = executable_path.parent.parent / "lib" / "R"
            if r_home.is_dir():
                environment["R_HOME"] = str(r_home)
            environment["PATH"] = str(executable_path.parent) + os.pathsep + environment.get("PATH", "")
    if os.name == "nt" and Path(executable).name.casefold() in {
        "gradle", "gradle.bat", "sbt", "sbt.bat", "kotlinc", "kotlinc.bat", "scalac", "scalac.bat",
    }:
        java_home = environment.get("JAVA_HOME", "").strip()
        if not java_home:
            for candidate in sorted(Path(r"C:\Program Files\Eclipse Adoptium").glob("jdk-*"), reverse=True):
                if (candidate / "bin" / "java.exe").is_file():
                    java_home = str(candidate)
                    break
        if java_home:
            environment["JAVA_HOME"] = java_home
            java_bin = str(Path(java_home) / "bin")
            if java_bin not in environment.get("PATH", ""):
                environment["PATH"] = java_bin + os.pathsep + environment.get("PATH", "")
    return environment
