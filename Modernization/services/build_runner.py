# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: services/build_runner.py
# Date: 2026-07-19
# ---------------------------------------------------------------------------
"""
services/build_runner.py
Phase 2 of the code-generation pipeline: a real, whole-project compiler
build for generated C#/Java/TypeScript projects, feeding structured
per-file errors back into the REPAIR_PROMPT retry loop (see modernizer.py's
generate_from_prompt).

This is a materially different concern from services/validators.py's
per-file syntax checks: validators.py checks one file in isolation with no
dependency resolution (so it must filter out "cannot find symbol"-style
noise); this module builds the ENTIRE generated project with real package
restore (NuGet / Maven Central / npm), so a "member not found" or
"cannot find module" error here is genuine signal, not noise.

Requires .NET 8 SDK (`dotnet`), Maven (`mvn`), and Node/npm on PATH. Missing
tools degrade to checker="skipped" — this module never crashes the calling
job over a missing toolchain, matching the graceful-degradation pattern in
validators.py.
"""
from __future__ import annotations

import re
import json
import os
import importlib.util
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from services.native_toolchain import native_include_args
from services.tool_discovery import executable_environment, find_executable

_DOTNET_PATH = shutil.which("dotnet")
_MVN_PATH = shutil.which("mvn") or shutil.which("mvn.cmd")
_NPM_PATH = shutil.which("npm") or shutil.which("npm.cmd")
_NPX_PATH = shutil.which("npx") or shutil.which("npx.cmd")

_BUILD_TIMEOUT = 180  # seconds — dotnet build / mvn compile
_NPM_INSTALL_TIMEOUT = 180  # seconds — real package-tree fetch
_NPM_BUILD_TIMEOUT = 420  # seconds — cold Angular/Vite/React production builds on Windows
_TOOLCHAIN_CRASH_RETRIES = 2  # extra attempts after a detected transient npm/node crash
_TOOLCHAIN_CRASH_BACKOFF = 5  # seconds between retries — lets transient memory pressure clear
# Signatures of npm/node crashing itself before it ever reaches user code — a
# host-level allocator/memory-pressure blip (observed in production under a
# constrained Windows service account), not a defect in the generated
# package.json/source. Treated as retryable; anything else (missing package,
# bad script, real TS/compile errors) is left alone and reported immediately.
_TRANSIENT_TOOLCHAIN_SIGNATURES = (
    "virtualalloc failed",
    "low_level_alloc",
    "fatal error: javascript heap out of memory",
    "fatal error in v8",
    "enomem",
    "cannot allocate memory",
    "econnreset",
    "eai_again",
    "socket hang up",
    "network timeout",
)
_TSC_VALIDATOR = Path(__file__).resolve().parent.parent / "tools" / "ts-validate" / "node_modules" / "typescript" / "lib" / "tsc.js"
_BUILD_KEY = "<build>"
_DEPENDENCY_COMPATIBILITY_KEY = "<dependency-compatibility>"
_INSTALL_KEY = "<install>"
_PACKAGE_JSON = "package.json"
_CLANG = "clang"
_CLANG_CPP = "clang++"
_MISSING_MANIFEST = "missing-manifest"
_MISSING_TOOLCHAIN = "missing-toolchain"
_NPM_TSC = "npm-tsc"
_MAVEN_REPOSITORY = Path(
    os.getenv("MODERNIZATION_MAVEN_REPOSITORY")
    or (Path(tempfile.gettempdir()) / "modernization_maven_repository")
)

_TOOLCHAIN_REQUIREMENTS = (
    ("COBOL", ("cobol",), (("cobc",),)),
    ("C++", ("c++", "cpp"), ((_CLANG_CPP, "g++"),)),
    ("C", ("c17 native", "language:c"), ((_CLANG, "gcc"),)),
    ("Go", ("golang", "go gin", "go rest", "language:go"), (("go",), ("gofmt",))),
    ("PHP", ("php", "laravel"), (("php",),)),
    ("Ruby", ("ruby", "rails"), (("ruby",),)),
    ("Node.js", ("node.js", "express", "react", "typescript", "javascript"), (("node",), ("npm",))),
)
_TYPESCRIPT_SIGNALS = ("typescript", "javascript", "react", "angular", "vue", "node.js")
_SQL_SIGNALS = ("sql", "postgres", "oracle", "db2", "mysql", "mssql")

SOURCE_BUILD_LANGUAGES = frozenset({
    "python", "javascript", "c", "cpp", "cobol", "php", "ruby", "go",
})
EXTENDED_BUILD_LANGUAGES = frozenset({
    "rust", "swift", "kotlin", "shell", "r", "scala", "clojure",
    "haskell", "lisp", "elixir", "dart", "julia", "hcl", "protobuf",
    "fortran", "ada", "pascal", "erlang", "ocaml", "prolog", "abap",
    "pli", "rpg", "jcl", "mumps", "natural", "progress4gl", "apex",
    "jenkinsfile",
})
ARTIFACT_BUILD_LANGUAGES = frozenset({
    "yaml", "json", "toml", "xml", "graphql", "dockerfile",
    "cloudformation", "kubernetes", "helm", "ansible",
    "github_actions", "markdown", "sql",
})
PROJECT_BUILD_LANGUAGES = frozenset({
    "csharp", "java", "typescript",
}) | SOURCE_BUILD_LANGUAGES | EXTENDED_BUILD_LANGUAGES | ARTIFACT_BUILD_LANGUAGES
PRODUCTION_PROJECT_BUILD_LANGUAGES = frozenset({
    "csharp", "java", "typescript", "javascript", "python", "go",
    "kotlin", "rust", "php", "dart", "swift", "scala", "clojure", "shell",
    "r", "julia", "haskell", "lisp", "rpg", "c", "cpp", "cobol", "ruby",
    "elixir", "erlang", "jenkinsfile",
}) | ARTIFACT_BUILD_LANGUAGES


# Function: _refresh_windows_path
def _refresh_windows_path() -> None:
    """Merge current registry PATH values into long-running service processes."""
    if os.name != "nt":
        return
    try:
        import winreg
        locations = (
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
            (winreg.HKEY_CURRENT_USER, r"Environment"),
        )
        values = [os.environ.get("PATH", "")]
        for hive, key_name in locations:
            with winreg.OpenKey(hive, key_name) as key:
                value, _ = winreg.QueryValueEx(key, "Path")
                values.append(os.path.expandvars(str(value)))
        entries = []
        seen = set()
        for value in values:
            for entry in value.split(os.pathsep):
                normalized = entry.strip().rstrip("\\").casefold()
                if normalized and normalized not in seen:
                    seen.add(normalized)
                    entries.append(entry.strip())
        # Prefer known MSYS2 bins when present so service restarts are not required
        # after manual runtime installs done outside of machine/user PATH updates.
        for candidate in (r"C:\msys64\ucrt64\bin", r"C:\msys64\usr\bin"):
            if os.path.isdir(candidate):
                normalized = candidate.rstrip("\\").casefold()
                if normalized not in seen:
                    seen.add(normalized)
                    entries.insert(0, candidate)
        os.environ["PATH"] = os.pathsep.join(entries)
    except (OSError, ValueError):
        pass


# Function: _refresh_tool_paths
def _refresh_tool_paths() -> None:
    """Refresh cached executable paths after long-running services update PATH."""
    global _DOTNET_PATH, _MVN_PATH, _NPM_PATH, _NPX_PATH
    _refresh_windows_path()
    _DOTNET_PATH = shutil.which("dotnet")
    _MVN_PATH = _which("mvn")
    _NPM_PATH = shutil.which("npm") or shutil.which("npm.cmd")
    _NPX_PATH = shutil.which("npx") or shutil.which("npx.cmd")


# Function: _which
def _which(command: str) -> Optional[str]:
    """Resolve a command, including per-user WinGet packages hidden by stale machine PATH entries."""
    command_key = (command or "").strip().casefold()
    resolved = find_executable(command)
    if resolved:
        return resolved

    # Service/watchdog processes often start with stale PATH values. For core
    # Java toolchains, probe known install locations dynamically instead of
    # requiring an explicit PATH entry.
    if os.name == "nt" and command_key in {"java", "java.exe", "javac", "javac.exe"}:
        java_home = _preferred_java_home()
        if java_home:
            binary = "javac.exe" if "javac" in command_key else "java.exe"
            candidate = java_home / "bin" / binary
            if candidate.is_file():
                return str(candidate)

    if os.name == "nt" and command_key in {"mvn", "mvn.cmd", "mvn.exe"}:
        maven_home = os.getenv("MAVEN_HOME")
        if maven_home:
            for binary in ("mvn.cmd", "mvn.exe", "mvn.bat"):
                candidate = Path(maven_home) / "bin" / binary
                if candidate.is_file():
                    return str(candidate)
        tools_root = Path(r"C:\Tools")
        if tools_root.is_dir():
            for candidate in sorted(tools_root.glob("apache-maven-*/bin/mvn.cmd"), reverse=True):
                if candidate.is_file():
                    return str(candidate)

    if os.name == "nt" and command_key in {"gradle", "gradle.bat", "gradle.cmd", "gradle.exe"}:
        gradle_home = os.getenv("GRADLE_HOME")
        if gradle_home:
            for binary in ("gradle.bat", "gradle.cmd", "gradle.exe"):
                candidate = Path(gradle_home) / "bin" / binary
                if candidate.is_file():
                    return str(candidate)

        for root in (Path(r"C:\Gradle"), Path(r"C:\ProgramData\chocolatey\lib")):
            if root.is_dir():
                for candidate in sorted(root.glob("**/gradle*.bat"), reverse=True):
                    if candidate.is_file():
                        return str(candidate)

    if os.name == "nt" and command_key in {"flutter", "flutter.bat", "flutter.cmd", "flutter.exe"}:
        user_home = Path(os.path.expanduser("~"))
        puro_candidates = (
            user_home / ".puro" / "envs" / "stable" / "flutter" / "bin" / "flutter.bat",
            user_home / ".puro" / "shared" / "flutter" / "bin" / "flutter.bat",
        )
        for candidate in puro_candidates:
            if candidate.is_file():
                return str(candidate)

    if os.name == "nt" and command.lower() == "php":
        local_app_data = os.getenv("LOCALAPPDATA")
        if local_app_data:
            packages = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
            for candidate in sorted(packages.glob("PHP.PHP.8.3_*/*php.exe"), reverse=True):
                if candidate.is_file():
                    return str(candidate)
    return None


# Function: _command_usable
def _command_usable(command: str) -> bool:
    """Return true only when an executable can actually start successfully."""
    command_key = command.casefold()
    path = _which(command)
    if not path:
        return False

    # Some MSYS2 tools are shell launchers (not Win32 PE executables) and can
    # only be reliably probed via bash -lc from Windows service processes.
    def _msys_bash_probe() -> bool:
        if os.name != "nt" or "msys64" not in path.casefold() or command_key not in {"go", "rscript"}:
            return False
        bash = _which("bash") or r"C:\msys64\usr\bin\bash.exe"
        if not os.path.isfile(bash):
            return False
        probe = {
            "go": "/ucrt64/bin/go version",
            "rscript": "/ucrt64/bin/Rscript --version",
        }[command_key]
        msys_env = os.environ.copy()
        msys_env.setdefault("MSYSTEM", "UCRT64")
        msys_env.setdefault("CHERE_INVOKING", "1")
        try:
            retry = subprocess.run(
                [bash, "-lc", probe],
                capture_output=True,
                text=True,
                timeout=30,
                env=msys_env,
            )
            return retry.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False

    arguments = {
        "go": ["version"],
        "gofmt": ["-h"],
        "php": ["-v"],
        "ruby": ["--version"],
        "cobc": ["--version"],
        "mvn": ["-version"],
        "npm": ["--version"],
        "node": ["--version"],
        "javac": ["-version"],
        "kotlinc": ["-version"],
        "scalac": ["-version"],
        "gradle": ["--version"],
        "sbt": ["--version"],
        "composer": ["--version"],
        "bundle": ["--version"],
        "flutter": ["--version"],
        "cabal": ["--version"],
        "stack": ["--version"],
        "erl": ["-noshell", "-eval", "halt()."],
        "erlc": ["-version"],
        "elixirc": ["--version"],
        "mix": ["--version"],
        "fpc": ["-h"],
        "erlc": ["-v"],
        "rscript": ["--version"],
    }.get(command_key, ["--version"])
    try:
        # Some SDK launchers (notably Flutter and first-run JVM tools) need
        # longer than a trivial compiler probe, and Swift needs its runtime
        # directory when discovered outside the process PATH.
        proc = subprocess.run(
            [path, *arguments],
            capture_output=True,
            text=True,
            timeout=30,
            env=executable_environment(path),
        )
        if command_key == "gofmt":
            return proc.returncode in {0, 2}
        if proc.returncode == 0:
            return True
        return _msys_bash_probe()
    except (OSError, subprocess.SubprocessError):
        return _msys_bash_probe()


@dataclass
class BuildResult:
    passed: bool
    checker: str                        # "dotnet" | "maven" | "npm-tsc" | "skipped"
    errors_by_file: Dict[str, List[str]] = field(default_factory=dict)
    raw_output: str = ""


# Function: installed_dotnet_majors
def installed_dotnet_majors() -> List[int]:
    """Return installed SDK major versions; an empty list means unavailable."""
    if not _DOTNET_PATH:
        return []
    try:
        proc = subprocess.run([_DOTNET_PATH, "--list-sdks"], capture_output=True, text=True, timeout=15)
        return sorted({int(match.group(1)) for match in re.finditer(r"(?m)^(\d+)\.", proc.stdout)})
    except (OSError, subprocess.SubprocessError, ValueError):
        return []


# Function: installed_java_majors
def installed_java_majors() -> List[int]:
    homes = list(Path(r"C:\Program Files\Eclipse Adoptium").glob("jdk-*")) if os.name == "nt" else []
    versions = {int(match.group(1)) for home in homes if (match := re.search(r"jdk-(\d+)", home.name, re.I))}
    java = shutil.which("java")
    if java:
        try:
            proc = subprocess.run([java, "-version"], capture_output=True, text=True, timeout=10)
            match = re.search(r'version "(?:1\.)?(\d+)', proc.stderr + proc.stdout)
            if match:
                versions.add(int(match.group(1)))
        except (OSError, subprocess.SubprocessError):
            pass
    return sorted(versions)


# Function: _preferred_java_home
def _preferred_java_home() -> Optional[Path]:
    if os.name != "nt":
        return Path(os.environ["JAVA_HOME"]) if os.environ.get("JAVA_HOME") else None
    candidates = []
    for home in Path(r"C:\Program Files\Eclipse Adoptium").glob("jdk-*"):
        match = re.search(r"jdk-(\d+)", home.name, re.I)
        if match and (home / "bin" / "java.exe").exists():
            candidates.append((int(match.group(1)), home))
    return max(candidates, default=(0, None), key=lambda item: item[0])[1]


# Function: toolchain_compatibility_error
def toolchain_compatibility_error(stack_description: str) -> Optional[str]:
    """Fail before generation when the requested .NET target cannot be built here."""
    _refresh_tool_paths()
    text = (stack_description or "").lower()
    checks = (
        _dotnet_compatibility_error(stack_description),
        _java_compatibility_error(stack_description, text),
        _required_toolchain_error(text),
        _parser_compatibility_error(text),
    )
    return next((error for error in checks if error), None)


# Function: _dotnet_compatibility_error
def _dotnet_compatibility_error(stack_description: str) -> Optional[str]:
    match = re.search(r"(?:\.net|dotnet|net)\s*(\d+)", stack_description or "", re.IGNORECASE)
    if not match:
        return None
    requested = int(match.group(1))
    installed = installed_dotnet_majors()
    if requested in installed:
        return None
    available = ", ".join(f".NET {version}" for version in installed) or "none"
    return (
        f"Target .NET {requested} cannot be validated on this build host. Installed SDKs: {available}. "
        f"Install the .NET {requested} SDK or revise and approve the plan for an installed target before transformation."
    )


# Function: _java_compatibility_error
def _java_compatibility_error(stack_description: str, normalized: str) -> Optional[str]:
    match = re.search(r"java\s*(\d+)", stack_description or "", re.IGNORECASE)
    installed = installed_java_majors()
    if match and int(match.group(1)) not in installed:
        available = ", ".join(f"Java {version}" for version in installed) or "none"
        return f"Target Java {match.group(1)} cannot be validated on this build host. Installed JDKs: {available}."
    if "java" not in normalized:
        return None
    missing: List[str] = []
    if not _command_usable("javac"):
        missing.append("javac")
    if not (_command_usable("mvn") or _command_usable("gradle")):
        missing.append("mvn/gradle")
    return _missing_prerequisites_error("Java", missing)


# Function: _missing_prerequisites_error
def _missing_prerequisites_error(label: str, missing: List[str]) -> Optional[str]:
    if not missing:
        return None
    return f"Target {label} cannot be strictly validated on this build host. Missing prerequisite(s): {', '.join(missing)}."


# Function: _required_toolchain_error
def _required_toolchain_error(normalized: str) -> Optional[str]:
    for label, signals, command_groups in _TOOLCHAIN_REQUIREMENTS:
        if not any(signal in normalized for signal in signals):
            continue
        missing = [
            "/".join(group)
            for group in command_groups
            if not any(_command_usable(command) for command in group)
        ]
        error = _missing_prerequisites_error(label, missing)
        if error:
            return error
    return None


# Function: _parser_compatibility_error
def _parser_compatibility_error(normalized: str) -> Optional[str]:
    if any(signal in normalized for signal in _TYPESCRIPT_SIGNALS) and not _TSC_VALIDATOR.is_file():
        return "Target TypeScript/JavaScript cannot be strictly validated: the vendored TypeScript compiler is missing."
    if any(signal in normalized for signal in _SQL_SIGNALS) and importlib.util.find_spec("sqlglot") is None:
        return "Target SQL cannot be strictly validated: the sqlglot parser is missing from the backend environment."
    return None


# Function: toolchain_status
def toolchain_status() -> dict:
    """Serializable readiness inventory used before planning and generation."""
    _refresh_tool_paths()
    dotnet = installed_dotnet_majors()
    java = installed_java_majors()
    tools = {
        "dotnet": {"ready": bool(dotnet), "versions": [str(v) for v in dotnet], "supports": [f"net{v}.0" for v in dotnet]},
        "node": {"ready": _command_usable("node"), "path": shutil.which("node")},
        "npm": {"ready": bool(_command_usable("npm") and _NPX_PATH), "path": _NPM_PATH},
        "java": {"ready": bool(java and _command_usable("javac")), "versions": [str(v) for v in java], "path": str(_preferred_java_home() or shutil.which("java") or "")},
        "maven": {"ready": _command_usable("mvn"), "path": _MVN_PATH},
        "python": {"ready": bool(shutil.which("python")), "path": shutil.which("python")},
        "go": {"ready": bool(_command_usable("go") and _command_usable("gofmt")), "path": _which("go")},
        "php": {"ready": _command_usable("php"), "path": _which("php")},
        "ruby": {"ready": _command_usable("ruby"), "path": _which("ruby")},
        "bundler": {"ready": _command_usable("bundle"), "path": _which("bundle")},
        "c": {"ready": bool(_command_usable(_CLANG) or _command_usable("gcc")), "path": shutil.which(_CLANG) or shutil.which("gcc")},
        "cpp": {"ready": bool(_command_usable(_CLANG_CPP) or _command_usable("g++")), "path": shutil.which(_CLANG_CPP) or shutil.which("g++")},
        "cobol": {"ready": _command_usable("cobc"), "path": shutil.which("cobc")},
        "typescript_validator": {"ready": bool(_command_usable("node") and _TSC_VALIDATOR.is_file()), "path": str(_TSC_VALIDATOR)},
        "sql_parser": {"ready": importlib.util.find_spec("sqlglot") is not None, "path": "python:sqlglot"},
        # db2_sql_parser was checked by _stack_readiness() in api/server.py but never
        # defined here, unconditionally gating db2_sql/cobol_db2 regardless of what
        # was actually installed. sqlfluff (already a pinned dependency) ships a
        # native "db2" dialect - that's the real parser validators.py._validate_sql
        # already prefers for DB2 SQL, this just makes readiness match reality.
        "db2_sql_parser": {"ready": importlib.util.find_spec("sqlfluff") is not None, "path": "python:sqlfluff"},
        "yaml_parser": {"ready": importlib.util.find_spec("yaml") is not None, "path": "python:yaml"},
        "json_parser": {"ready": True, "path": "python:json"},
        "xml_parser": {"ready": True, "path": "python:xml.etree.ElementTree"},
        "toml_parser": {"ready": importlib.util.find_spec("tomllib") is not None, "path": "python:tomllib"},
        "graphql_parser": {"ready": importlib.util.find_spec("graphql") is not None, "path": "python:graphql"},
        "terraform": {"ready": importlib.util.find_spec("hcl2") is not None, "path": "python:hcl2"},
        "protobuf": {"ready": _command_usable("protoc"), "path": shutil.which("protoc")},
        "shell": {"ready": _command_usable("bash"), "path": _which("bash")},
        # No external grammar for Jenkinsfile (Groovy-based pipeline DSL) exists as a
        # dependency here; validated via a structural check (see validators.py), same
        # honesty tier as the heuristic-validated legacy languages below - always
        # "ready" since it has no external tool to be missing.
        "jenkinsfile": {"ready": True, "path": "heuristic:jenkinsfile"},
        # ── Additional language toolchains (validators.py._EXTERNAL_VALIDATORS
        # already has real compiler invocations wired for all of these - they were
        # gated purely because no readiness key existed here, same bug as db2_sql_parser
        # above, not because the check itself was ever missing. ──
        "rust": {"ready": _command_usable("rustc"), "path": _which("rustc")},
        "swift": {"ready": _command_usable("swiftc"), "path": _which("swiftc")},
        "kotlin": {"ready": _command_usable("kotlinc"), "path": _which("kotlinc")},
        "gradle": {"ready": _command_usable("gradle"), "path": _which("gradle")},
        "r": {"ready": _command_usable("Rscript"), "path": _which("Rscript")},
        "scala": {"ready": _command_usable("scalac"), "path": _which("scalac")},
        "sbt": {"ready": _command_usable("sbt"), "path": _which("sbt")},
        # Stack-managed GHC installations intentionally need not expose ghc on
        # the service PATH; Stack is itself a complete compiler/build route.
        "haskell": {
            "ready": _command_usable("ghc") or _command_usable("stack"),
            "path": _which("ghc") or _which("stack"),
        },
        "cabal": {"ready": _command_usable("cabal"), "path": _which("cabal")},
        "stack": {"ready": _command_usable("stack"), "path": _which("stack")},
        "elixir": {"ready": _command_usable("elixirc"), "path": _which("elixirc")},
        "mix": {"ready": _command_usable("mix"), "path": _which("mix")},
        "dart": {"ready": _command_usable("dart"), "path": _which("dart")},
        "flutter": {"ready": _command_usable("flutter"), "path": _which("flutter")},
        "julia": {"ready": _command_usable("julia"), "path": _which("julia")},
        "fortran": {"ready": bool(_command_usable("flang-new") or _command_usable("gfortran")),
                    "path": shutil.which("flang-new") or shutil.which("gfortran")},
        "ada": {"ready": _command_usable("gnatmake"), "path": shutil.which("gnatmake")},
        "pascal": {"ready": _command_usable("fpc"), "path": shutil.which("fpc")},
        "erlang": {
            "ready": _command_usable("erlc") and _command_usable("erl"),
            "path": _which("erlc"),
        },
        # DkML's ocamlc on this box has a Visual Studio version incompatibility
        # ("has a version 18.0 not supported by DkML") unrelated to anything
        # changed here - genuinely not ready, not another instance of the wiring bug.
        "ocaml": {"ready": _command_usable("ocamlc"), "path": shutil.which("ocamlc"),
                  "note": "Installed but currently broken: DkML/Visual Studio version mismatch."},
        "prolog": {"ready": _command_usable("swipl"), "path": shutil.which("swipl")},
        "lisp": {"ready": _command_usable("sbcl"), "path": _which("sbcl")},
        # No entry in _EXTERNAL_VALIDATORS (dispatches straight to the tree-sitter
        # grammar instead, already real syntax validation) - "ready" here reflects
        # the standalone `clojure` CLI actually being usable, not a validation gap.
        "clojure": {"ready": _command_usable("clojure"), "path": _which("clojure")},
        "composer": {"ready": _command_usable("composer"), "path": _which("composer")},
        # No open-source equivalent exists for these 8 - see validators.py's
        # _UNAVAILABLE_VENDOR_TOOLCHAINS - covered instead by heuristic structural
        # validators below (key names match _STACK_LANGUAGE_TOOL in api/server.py
        # exactly), always "ready" since there is no external tool to be missing.
        "abap": {"ready": True, "path": "heuristic:abap"},
        "rpg": {"ready": True, "path": "heuristic:rpg"},
        "jcl": {"ready": True, "path": "heuristic:jcl"},
        "mumps": {"ready": True, "path": "heuristic:mumps"},
        "natural": {"ready": True, "path": "heuristic:natural"},
        "progress4gl": {"ready": True, "path": "heuristic:progress4gl"},
        "apex": {"ready": True, "path": "heuristic:apex"},
        "pli": {"ready": True, "path": "heuristic:pli"},
        "git": {"ready": bool(shutil.which("git")), "path": shutil.which("git"),
                "note": "Optional import/export integration; governed snapshots remain authoritative."},
        "docker": {"ready": bool(shutil.which("docker")), "path": shutil.which("docker"),
                   "note": "Optional; native SDK builds remain available when Docker is stopped."},
    }
    tools["rust_package_manager"] = {
        "ready": _command_usable("cargo"), "path": _which("cargo"),
    }
    tools["swift_package_manager"] = {
        "ready": _command_usable("swift"), "path": _which("swift"),
    }
    tools["jvm_build"] = {
        "ready": tools["gradle"]["ready"] or tools["maven"]["ready"],
        "path": tools["gradle"]["path"] or tools["maven"]["path"],
    }
    tools["haskell_build"] = {
        "ready": tools["cabal"]["ready"] or tools["stack"]["ready"],
        "path": tools["cabal"]["path"] or tools["stack"]["path"],
    }
    catalog = [
        {"id": "dotnet8", "name": ".NET SDK 8", "installed": 8 in dotnet, "installable": os.name == "nt"},
        {"id": "dotnet10", "name": ".NET SDK 10", "installed": 10 in dotnet, "installable": os.name == "nt"},
        {"id": "java17", "name": "Java JDK 17", "installed": 17 in java, "installable": os.name == "nt"},
        {"id": "java21", "name": "Java JDK 21", "installed": 21 in java, "installable": os.name == "nt"},
        {"id": "node", "name": "Node.js LTS and npm", "installed": tools["npm"]["ready"], "installable": os.name == "nt"},
        {"id": "maven", "name": "Apache Maven", "installed": tools["maven"]["ready"], "installable": False},
        {"id": "gradle", "name": "Gradle", "installed": tools["gradle"]["ready"], "installable": False},
        {"id": "python312", "name": "Python 3.12", "installed": tools["python"]["ready"], "installable": os.name == "nt"},
        {"id": "go", "name": "Go SDK", "installed": tools["go"]["ready"], "installable": os.name == "nt"},
        {"id": "php", "name": "PHP 8.3", "installed": tools["php"]["ready"], "installable": os.name == "nt"},
        {"id": "ruby", "name": "Ruby with DevKit", "installed": tools["ruby"]["ready"], "installable": os.name == "nt"},
        {"id": "llvm", "name": "LLVM C/C++ compiler", "installed": tools["c"]["ready"] and tools["cpp"]["ready"], "installable": os.name == "nt"},
        {"id": "cobol", "name": "GnuCOBOL", "installed": tools["cobol"]["ready"], "installable": False},
        {"id": "protoc", "name": "Protocol Buffers compiler", "installed": tools["protobuf"]["ready"], "installable": os.name == "nt"},
        {"id": "bash", "name": "Bash (Git for Windows)", "installed": tools["shell"]["ready"], "installable": os.name == "nt"},
        {"id": "rust", "name": "Rust (rustc)", "installed": tools["rust"]["ready"], "installable": os.name == "nt"},
        {"id": "swift", "name": "Swift toolchain", "installed": tools["swift"]["ready"], "installable": os.name == "nt"},
        {"id": "kotlin", "name": "Kotlin compiler", "installed": tools["kotlin"]["ready"], "installable": os.name == "nt"},
        {"id": "r", "name": "R", "installed": tools["r"]["ready"], "installable": os.name == "nt"},
        {"id": "scala", "name": "Scala compiler", "installed": tools["scala"]["ready"], "installable": os.name == "nt"},
        {"id": "haskell", "name": "Haskell (GHC via GHCup)", "installed": tools["haskell"]["ready"], "installable": os.name == "nt"},
        {"id": "elixir", "name": "Elixir", "installed": tools["elixir"]["ready"], "installable": os.name == "nt"},
        {"id": "dart", "name": "Dart SDK", "installed": tools["dart"]["ready"], "installable": os.name == "nt"},
        {"id": "flutter", "name": "Flutter SDK", "installed": tools["flutter"]["ready"], "installable": os.name == "nt"},
        {"id": "julia", "name": "Julia", "installed": tools["julia"]["ready"], "installable": os.name == "nt"},
        {"id": "fortran", "name": "Fortran (gfortran/flang)", "installed": tools["fortran"]["ready"], "installable": os.name == "nt"},
        {"id": "ada", "name": "Ada (GNAT)", "installed": tools["ada"]["ready"], "installable": os.name == "nt"},
        {"id": "pascal", "name": "Free Pascal", "installed": tools["pascal"]["ready"], "installable": os.name == "nt"},
        {"id": "erlang", "name": "Erlang/OTP", "installed": tools["erlang"]["ready"], "installable": os.name == "nt"},
        {"id": "ocaml", "name": "OCaml", "installed": tools["ocaml"]["ready"], "installable": os.name == "nt"},
        {"id": "prolog", "name": "SWI-Prolog", "installed": tools["prolog"]["ready"], "installable": os.name == "nt"},
        {"id": "lisp", "name": "Common Lisp (SBCL)", "installed": tools["lisp"]["ready"], "installable": os.name == "nt"},
        {"id": "clojure", "name": "Clojure CLI", "installed": tools["clojure"]["ready"], "installable": os.name == "nt"},
        {"id": "git", "name": "Git and GitHub-compatible CLI workflow", "installed": tools["git"]["ready"], "installable": os.name == "nt"},
    ]
    required = (
        "dotnet", "node", "npm", "java", "jvm_build", "python", "go", "php",
        "ruby", "c", "cpp", "cobol", "typescript_validator", "sql_parser",
        "db2_sql_parser", "yaml_parser", "json_parser", "xml_parser",
        "toml_parser", "graphql_parser", "terraform", "protobuf", "shell",
        "jenkinsfile", "rust", "swift", "kotlin", "r", "scala", "haskell",
        "elixir", "dart", "julia", "fortran", "ada", "pascal", "erlang",
        "ocaml", "prolog", "lisp", "clojure", "abap", "rpg", "jcl", "mumps",
        "natural", "progress4gl", "apex", "pli",
    )
    return {"ready": all(tools[name]["ready"] for name in required),
            "tools": tools, "catalog": catalog}


# Function: _materialize
def _materialize(output: Dict[str, str], tmp_dir: Path) -> None:
    for rel_path, content in output.items():
        if not isinstance(content, str):
            continue
        file_path = tmp_dir / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            file_path.write_text(content, encoding="utf-8")
        except OSError:
            continue  # a single unwritable file (bad path chars, etc.) shouldn't abort the whole build


_WIN_DRIVE_WITH_LEADING_SLASH = re.compile(r"^/([A-Za-z]:)")


# Function: _rel_to_output_key
def _rel_to_output_key(reported_path: str, base_dir: Path, tmp_dir: Path) -> str:
    """Normalize a compiler-reported path (absolute or cwd-relative, native
    separators) back to the forward-slash-relative form used as keys in the
    `output` dict, so build errors can be attached to the right file.
    Maven-on-Windows reports absolute paths as "/C:/Users/..." (a leading
    slash before the drive letter) rather than "C:/Users/..." — strip that
    or Path() treats the whole thing as relative and relative_to() below
    always fails, silently degrading every Java error to a raw absolute path."""
    reported_path = _WIN_DRIVE_WITH_LEADING_SLASH.sub(r"\1", reported_path)
    p = Path(reported_path)
    p = p if p.is_absolute() else (base_dir / p)
    try:
        rel = p.resolve().relative_to(tmp_dir.resolve())
    except (ValueError, OSError):
        rel = Path(reported_path)
    return str(rel).replace("\\", "/")


# Function: _find_one
def _find_one(tmp_dir: Path, pattern: str) -> Optional[Path]:
    ignored = {"node_modules", "bin", "obj", ".git", "dist", "target"}
    matches = [path for path in tmp_dir.rglob(pattern) if not ignored.intersection(path.relative_to(tmp_dir).parts)]
    matches.sort(key=lambda path: (len(path.relative_to(tmp_dir).parts), path.as_posix()))
    return matches[0] if matches else None


# ─── C# / .NET ──────────────────────────────────────────────────────────────

# Function: _parse_parenthesized_diagnostic
def _parse_parenthesized_diagnostic(line: str, code_prefix: str) -> Optional[tuple[str, str, str, str]]:
    """Parse path(line,col): error CODE: message without backtracking."""
    location, separator, detail = line.partition("): error ")
    if not separator:
        return None
    file_path, open_paren, coordinates = location.rpartition("(")
    if not open_paren:
        return None
    line_no, comma, column = coordinates.partition(",")
    code, colon, message = detail.partition(":")
    if not (comma and colon and line_no.isdigit() and column.isdigit() and code.startswith(code_prefix)):
        return None
    cleaned_message = message.strip()
    if code_prefix == "CS" and cleaned_message.endswith("]") and " [" in cleaned_message:
        cleaned_message = cleaned_message.rsplit(" [", 1)[0]
    return file_path, line_no, code, cleaned_message


# Function: _run_dotnet_build
def _run_dotnet_build(tmp_dir: Path) -> BuildResult:
    if not _DOTNET_PATH:
        return BuildResult(False, _MISSING_TOOLCHAIN, {_BUILD_KEY: ["dotnet not found on PATH"]})

    sln = _find_one(tmp_dir, "*.sln")
    target = sln if sln else _find_one(tmp_dir, "*.csproj")
    if not target:
        return BuildResult(False, _MISSING_MANIFEST, {_BUILD_KEY: ["Generated .NET output has no .sln or .csproj"]})

    try:
        proc = subprocess.run(
            [_DOTNET_PATH, "build", str(target), "--nologo", "-v", "quiet"],
            capture_output=True, text=True, timeout=_BUILD_TIMEOUT, cwd=str(target.parent),
        )
    except subprocess.TimeoutExpired as exc:
        return BuildResult(False, "dotnet", {_BUILD_KEY: [f"dotnet build timed out after {_BUILD_TIMEOUT}s"]}, str(exc))

    combined = proc.stdout + "\n" + proc.stderr
    if proc.returncode == 0:
        return BuildResult(True, "dotnet", raw_output=combined)

    errors_by_file: Dict[str, List[str]] = {}
    for line in combined.splitlines():
        parsed = _parse_parenthesized_diagnostic(line.strip(), "CS")
        if not parsed:
            continue
        file_path, _lineno, code, message = parsed
        key = _rel_to_output_key(file_path, target.parent, tmp_dir)
        errors_by_file.setdefault(key, []).append(f"{code}: {message}")

    if not errors_by_file:
        # Build failed (non-zero exit) but no per-file line matched — e.g. a
        # restore failure. Attach the raw tail so the repair loop has SOMETHING.
        errors_by_file[_BUILD_KEY] = [combined.strip()[-1500:] or "dotnet build failed with no parseable output"]

    for key, messages in list(errors_by_file.items()):
        errors_by_file[key] = list(dict.fromkeys(messages))
    return BuildResult(False, "dotnet", errors_by_file, combined)


# ─── Java / Maven ───────────────────────────────────────────────────────────

# Function: _parse_maven_diagnostic
def _parse_maven_diagnostic(line: str) -> Optional[tuple[str, str]]:
    """Parse Maven's [ERROR] path.java:[line,col] message format."""
    prefix = "[ERROR] "
    if not line.startswith(prefix):
        return None
    location, separator, message = line[len(prefix):].partition("] ")
    file_path, marker, coordinates = location.rpartition(":[")
    if not (separator and marker and file_path.endswith(".java")):
        return None
    line_no, comma, column = coordinates.partition(",")
    if not (comma and line_no.isdigit() and column.isdigit()):
        return None
    return file_path, message.strip()


# Function: _parse_maven_project_diagnostic
def _parse_maven_project_diagnostic(line: str) -> Optional[tuple[str, str]]:
    """Attach a missing-reactor-module error to its parent POM."""
    match = re.search(
        r"Child module\s+(.+?)\s+of\s+(.+?pom\.xml)\s+does not exist",
        line,
        re.IGNORECASE,
    )
    if not match:
        return None
    return (
        match.group(2).strip(),
        f"Declared Maven child module does not exist: {match.group(1).strip()}",
    )


# Function: _run_maven_build
def _run_maven_build(tmp_dir: Path) -> BuildResult:
    if not _MVN_PATH:
        return BuildResult(False, _MISSING_TOOLCHAIN, {_BUILD_KEY: ["mvn not found on PATH"]})

    pom = _find_one(tmp_dir, "pom.xml")
    if not pom:
        return BuildResult(False, _MISSING_MANIFEST, {_BUILD_KEY: ["Generated Java output has no pom.xml"]})

    try:
        _MAVEN_REPOSITORY.mkdir(parents=True, exist_ok=True)
        build_env = os.environ.copy()
        java_home = _preferred_java_home()
        if java_home:
            build_env["JAVA_HOME"] = str(java_home)
            build_env["PATH"] = str(java_home / "bin") + os.pathsep + build_env.get("PATH", "")
        proc = subprocess.run(
            [
                _MVN_PATH,
                "-B",
                "-q",
                f"-Dmaven.repo.local={_MAVEN_REPOSITORY}",
                "verify",
            ],
            capture_output=True, text=True, timeout=_BUILD_TIMEOUT, cwd=str(pom.parent), env=build_env,
        )
    except subprocess.TimeoutExpired as exc:
        return BuildResult(False, "maven", {_BUILD_KEY: [f"mvn verify timed out after {_BUILD_TIMEOUT}s"]}, str(exc))

    combined = proc.stdout + "\n" + proc.stderr
    if proc.returncode == 0:
        return BuildResult(True, "maven", raw_output=combined)

    errors_by_file: Dict[str, List[str]] = {}
    last_java_key: Optional[str] = None
    for line in combined.splitlines():
        stripped = line.strip()
        parsed = _parse_maven_diagnostic(stripped)
        project_parsed = _parse_maven_project_diagnostic(stripped)
        if parsed:
            file_path, message = parsed
        elif project_parsed:
            file_path, message = project_parsed
        else:
            detail_match = re.match(
                r"\[ERROR]\s+(symbol|location):\s*(.+)",
                stripped,
                re.IGNORECASE,
            )
            if detail_match and last_java_key and errors_by_file.get(last_java_key):
                errors_by_file[last_java_key][-1] += (
                    f" — {detail_match.group(1).lower()}: {detail_match.group(2).strip()}"
                )
            continue
        key = _rel_to_output_key(file_path, pom.parent, tmp_dir)
        errors_by_file.setdefault(key, []).append(message)
        last_java_key = key if parsed else None

    if not errors_by_file:
        errors_by_file[_BUILD_KEY] = [combined.strip()[-1500:] or "mvn verify failed with no parseable output"]

    return BuildResult(False, "maven", errors_by_file, combined)


# Function: _run_java_project_build
def _run_java_project_build(tmp_dir: Path) -> BuildResult:
    """Run a real Java project build based on whichever build manifest exists.

    Dynamic route selection avoids hard-coding Maven-only readiness for stacks
    whose generated projects can be Gradle-based (for example Quarkus/Micronaut
    variants), while keeping strict compile validation fail-closed.
    """
    pom = _find_one(tmp_dir, "pom.xml")
    gradle = _find_one(tmp_dir, "build.gradle") or _find_one(tmp_dir, "build.gradle.kts")

    if pom:
        return _run_maven_build(tmp_dir)
    if gradle:
        return _run_manifest_build(tmp_dir, "gradle", ["test", "--no-daemon"])

    if _command_usable("mvn"):
        return BuildResult(False, _MISSING_MANIFEST, {_BUILD_KEY: ["Generated Java output has no pom.xml/build.gradle/build.gradle.kts"]})
    if _command_usable("gradle"):
        return BuildResult(False, _MISSING_MANIFEST, {_BUILD_KEY: ["Generated Java output has no build.gradle/build.gradle.kts/pom.xml"]})
    return BuildResult(False, _MISSING_TOOLCHAIN, {_BUILD_KEY: ["Neither mvn nor gradle is available on PATH"]})


# ─── TypeScript / npm ───────────────────────────────────────────────────────

# Function: _parse_angular_diagnostic
def _parse_angular_diagnostic(line: str) -> Optional[tuple[str, str, str]]:
    """Parse Angular path:line:col - error TS/NGxxxx: message output."""
    normalized = line.removeprefix("Error: ")
    location, separator, detail = normalized.partition(" - error ")
    if not separator:
        return None
    file_path, colon, column = location.rpartition(":")
    file_path, line_colon, line_no = file_path.rpartition(":")
    code, message_colon, message = detail.partition(":")
    if not (
        colon and line_colon and message_colon
        and line_no.isdigit() and column.isdigit()
        and file_path.endswith((".ts", ".tsx"))
        and code.startswith(("TS", "NG"))
    ):
        return None
    return file_path, code, message.strip()


# Function: _parse_typescript_diagnostic
def _parse_typescript_diagnostic(line: str) -> Optional[tuple[str, str, str]]:
    parsed = _parse_parenthesized_diagnostic(line, "TS")
    if parsed:
        file_path, _line_no, code, message = parsed
        return file_path, code, message
    return _parse_angular_diagnostic(line)


# Function: _run_npm_tsc_build
def _load_package_data(package_path: Path) -> dict:
    try:
        return json.loads(package_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


# Function: _is_transient_toolchain_crash
def _is_transient_toolchain_crash(proc: "subprocess.CompletedProcess[str]") -> bool:
    """True when npm/node crashed itself (allocator/host memory pressure)
    rather than reporting a real problem with the generated project. These
    crashes are non-deterministic — the exact same package.json succeeds on
    the very next attempt once transient pressure clears — so failing the
    whole build (and the release quality gate) on the first occurrence
    reports a false "generated code is broken" verdict."""
    if proc.returncode == 0:
        return False
    combined = f"{proc.stdout or ''}\n{proc.stderr or ''}".casefold()
    return any(signature in combined for signature in _TRANSIENT_TOOLCHAIN_SIGNATURES)


# Function: _run_npm_subprocess_with_retry
def _run_npm_subprocess_with_retry(
    command: list, project_dir: Path, timeout: int, timeout_key: str, timeout_message: str,
) -> "subprocess.CompletedProcess[str] | BuildResult":
    """Run an npm/npx subprocess, retrying only on a detected transient
    toolchain crash (see _is_transient_toolchain_crash) — never on a normal
    non-zero exit from a real dependency/compile problem."""
    attempt = 0
    last_proc: Optional["subprocess.CompletedProcess[str]"] = None
    while attempt <= _TOOLCHAIN_CRASH_RETRIES:
        attempt += 1
        try:
            proc = subprocess.run(
                command, capture_output=True, text=True, timeout=timeout, cwd=str(project_dir),
            )
        except subprocess.TimeoutExpired as exc:
            return BuildResult(False, _NPM_TSC, {timeout_key: [timeout_message]}, str(exc))
        if not _is_transient_toolchain_crash(proc) or attempt > _TOOLCHAIN_CRASH_RETRIES:
            return proc
        last_proc = proc
        time.sleep(_TOOLCHAIN_CRASH_BACKOFF)
    return last_proc


# Function: _npm_install
def _npm_install(project_dir: Path) -> "subprocess.CompletedProcess[str] | BuildResult":
    return _run_npm_subprocess_with_retry(
        [_NPM_PATH, "install", "--no-fund", "--no-audit"], project_dir, _NPM_INSTALL_TIMEOUT,
        _INSTALL_KEY, f"npm install timed out after {_NPM_INSTALL_TIMEOUT}s",
    )


# Function: _npm_compile
def _npm_compile(project_dir: Path, build_script: str) -> "subprocess.CompletedProcess[str] | BuildResult":
    command = [_NPM_PATH, "run", "build"] if build_script else [_NPX_PATH, "tsc", "--noEmit"]
    return _run_npm_subprocess_with_retry(
        command, project_dir, _NPM_BUILD_TIMEOUT,
        _BUILD_KEY, f"frontend build timed out after {_NPM_BUILD_TIMEOUT}s",
    )


# Function: _typescript_errors
def _typescript_errors(output: str, project_dir: Path, tmp_dir: Path) -> Dict[str, List[str]]:
    errors: Dict[str, List[str]] = {}
    for line in output.splitlines():
        parsed = _parse_typescript_diagnostic(line.strip())
        if not parsed:
            continue
        file_path, code, message = parsed
        key = _rel_to_output_key(file_path, project_dir, tmp_dir)
        if "/node_modules/" in f"/{key}":
            key = _DEPENDENCY_COMPATIBILITY_KEY
        errors.setdefault(key, []).append(f"{code}: {message}")
    return {key: list(dict.fromkeys(messages))[:20] for key, messages in errors.items()}


# Function: _vite_manifest_errors
def _vite_manifest_errors(output: str, package_path: Path, tmp_dir: Path) -> Dict[str, List[str]]:
    """Map missing packages to package.json and local imports to their importer."""
    errors: Dict[str, List[str]] = {}
    detailed = re.compile(
        r"""(?:failed to resolve import|could not resolve)\s+["']([^"']+)["']\s+from\s+["']([^"']+)["']""",
        re.IGNORECASE,
    )
    seen = set()
    for match in detailed.finditer(output):
        specifier, importer = match.groups()
        seen.add(specifier)
        is_local = specifier.startswith((".", "/", "@/", "src/", "~/"))
        target = importer if is_local else str(package_path)
        key = _rel_to_output_key(target, package_path.parent, tmp_dir)
        category = "Local frontend import" if is_local else "Frontend dependency"
        errors.setdefault(key, []).append(f"{category} is not resolvable: {specifier}")
    for pattern in (
        r"""failed to resolve import\s+["']([^"']+)["']""",
        r"""could not resolve\s+["']([^"']+)["']""",
    ):
        for match in re.finditer(pattern, output, re.IGNORECASE):
            specifier = match.group(1)
            if specifier in seen or specifier.startswith((".", "/", "@/", "src/", "~/")):
                continue
            key = _rel_to_output_key(str(package_path), package_path.parent, tmp_dir)
            errors.setdefault(key, []).append(
                f"Frontend dependency is imported but not resolvable: {specifier}"
            )
    return {
        key: list(dict.fromkeys(messages))[:20]
        for key, messages in errors.items()
    }


# Function: _run_npm_tsc_build
def _run_npm_tsc_build(
    tmp_dir: Path,
    package_path: Optional[Path] = None,
    manifest_diagnostics: bool = False,
) -> BuildResult:
    if not (_NPM_PATH and _NPX_PATH):
        return BuildResult(False, _MISSING_TOOLCHAIN, {_BUILD_KEY: ["npm/npx not found on PATH"]})

    pkg = package_path or _find_one(tmp_dir, _PACKAGE_JSON)
    if not pkg:
        return BuildResult(
            False, _MISSING_MANIFEST,
            {_BUILD_KEY: [f"Generated Node/TypeScript output has no {_PACKAGE_JSON}"]},
        )
    project_dir = pkg.parent
    package_data = _load_package_data(pkg)
    install = _npm_install(project_dir)
    if isinstance(install, BuildResult):
        return install
    if install.returncode != 0:
        combined = install.stdout + "\n" + install.stderr
        return BuildResult(False, _NPM_TSC, {_INSTALL_KEY: [combined.strip()[-1500:]]}, combined)

    build_script = (package_data.get("scripts") or {}).get("build")
    proc = _npm_compile(project_dir, build_script)
    if isinstance(proc, BuildResult):
        return proc

    combined = install.stdout + proc.stdout + "\n" + proc.stderr
    checker = "npm-build" if build_script else _NPM_TSC
    if proc.returncode == 0:
        return BuildResult(True, checker, raw_output=combined)

    # Unlike validators.py's per-file check (which filters TSxxxx >= 2000 as
    # dependency-resolution noise since no node_modules exist there), a real
    # `npm install` just ran here — TS2xxx type/module-resolution errors are
    # genuine signal now, not noise. Keep every error-level diagnostic.
    errors_by_file = _typescript_errors(proc.stdout + "\n" + proc.stderr, project_dir, tmp_dir)
    if not errors_by_file and manifest_diagnostics:
        errors_by_file = _vite_manifest_errors(
            proc.stdout + "\n" + proc.stderr, pkg, tmp_dir,
        )
    if not errors_by_file:
        errors_by_file[_BUILD_KEY] = [combined.strip()[-1500:] or "tsc failed with no parseable output"]
    return BuildResult(False, checker, errors_by_file, combined)


# Function: _run_all_npm_builds
def _run_all_npm_builds(tmp_dir: Path) -> BuildResult:
    """Restore and compile every generated Node workspace independently."""
    packages = sorted(
        path for path in tmp_dir.rglob(_PACKAGE_JSON)
        if "node_modules" not in path.parts
    )
    if not packages:
        return BuildResult(False, _MISSING_MANIFEST, {_BUILD_KEY: ["Generated output has no package.json"]})
    result: Optional[BuildResult] = None
    for package in packages:
        current = _run_npm_tsc_build(tmp_dir, package)
        result = current if result is None else _combine_build_results(result, current)
    return result or BuildResult(False, _MISSING_MANIFEST)


# Function: _run_c_family_build
def _run_c_family_build(tmp_dir: Path, language: str) -> BuildResult:
    """Real project build for C/C++: compile every source file to an object
    file, then link them together. A per-file -fsyntax-only pass (the old
    route, still used by validators.py's Phase-1 per-file check) treats every
    translation unit in isolation and can never catch cross-file link errors -
    an undefined reference to a sibling file's function, or the same symbol
    defined twice. Linking is the only way to catch those, so this is what
    makes c/cpp genuinely "project ready" rather than single-file-only."""
    files = _source_files(tmp_dir, language)
    if not files:
        return BuildResult(True, f"{language}-build", raw_output="no source files to build")

    executable = _source_check_executable(language, "")
    if not executable:
        return BuildResult(
            False, _MISSING_TOOLCHAIN,
            {_BUILD_KEY: [f"Required {'C' if language == 'c' else 'C++'} compiler is not installed"]},
        )

    output_parts: List[str] = []
    objects: List[Path] = []
    standard_flag = "-std=c17" if language == "c" else "-std=c++23"
    for source in files:
        obj_path = source.with_suffix(".o")
        try:
            proc = subprocess.run(
                [executable, standard_flag, "-c", *native_include_args(), str(source), "-o", str(obj_path)],
                cwd=str(tmp_dir), capture_output=True, text=True, timeout=_BUILD_TIMEOUT,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return BuildResult(False, f"{language}-build", {_BUILD_KEY: [str(exc)]})
        combined = (proc.stdout + "\n" + proc.stderr).strip()
        output_parts.append(combined)
        if proc.returncode != 0:
            rel = source.relative_to(tmp_dir).as_posix()
            return BuildResult(
                False, f"{language}-build",
                {_BUILD_KEY: [combined[-3000:] or f"Compilation failed for {rel}"]},
                "\n".join(output_parts),
            )
        objects.append(obj_path)

    # Decide executable vs. shared-library link mode from the source itself rather
    # than pattern-matching linker error text after the fact: lld-link (Windows)
    # and GNU ld report a missing entry point completely differently ("subsystem
    # must be defined" vs. "undefined reference to `main'"), so guessing from the
    # error message is fragile across linkers/versions. A library with no `main`
    # is valid, not a defect - detect that case up front instead.
    combined_source = "\n".join(
        source.read_text(encoding="utf-8", errors="ignore") for source in files
    )
    has_entry_point = bool(re.search(r"\b(?:int|void)\s+main\s*\(|\bwWinMain\b|\bWinMain\b", combined_source))
    if has_entry_point:
        link_flags: List[str] = []
        link_output = tmp_dir / ("__modernization_link_check.exe" if os.name == "nt" else "__modernization_link_check")
    else:
        link_flags = ["-shared"]
        link_output = tmp_dir / ("__modernization_link_check.dll" if os.name == "nt" else "__modernization_link_check.so")
    try:
        link_proc = subprocess.run(
            [executable, standard_flag, *link_flags, *[str(o) for o in objects], "-o", str(link_output)],
            cwd=str(tmp_dir), capture_output=True, text=True, timeout=_BUILD_TIMEOUT,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return BuildResult(False, f"{language}-build", {_BUILD_KEY: [str(exc)]}, "\n".join(output_parts))
    link_combined = (link_proc.stdout + "\n" + link_proc.stderr).strip()
    output_parts.append(link_combined)
    if link_proc.returncode != 0:
        return BuildResult(
            False, f"{language}-build",
            {_BUILD_KEY: [link_combined[-3000:] or "Link failed"]},
            "\n".join(output_parts),
        )
    return BuildResult(True, f"{language}-build", raw_output="\n".join(output_parts))


# ─── Public API ─────────────────────────────────────────────────────────────

# Function: run_build
def run_build(output: Dict[str, str], language: str, tmp_dir: Path) -> BuildResult:
    """Materialize `output` under tmp_dir and run a real build for the given
    language. Returns checker="skipped" for languages with no real build
    concept (python/sql — already covered by validators.py's syntax checks)
    or when the required toolchain isn't installed. Never raises."""
    tmp_dir.mkdir(parents=True, exist_ok=True)
    _refresh_tool_paths()

    try:
        _materialize(output, tmp_dir)
        if language == "csharp":
            primary = _run_dotnet_build(tmp_dir)
            frontend = _run_npm_tsc_build(tmp_dir) if _find_one(tmp_dir, _PACKAGE_JSON) else None
            return _combine_build_results(primary, frontend)
        if language == "java":
            primary = _run_java_project_build(tmp_dir)
            frontend = (
                _run_npm_tsc_build(tmp_dir, manifest_diagnostics=True)
                if _find_one(tmp_dir, _PACKAGE_JSON) else None
            )
            return _combine_build_results(primary, frontend)
        if language == "typescript":
            return _run_all_npm_builds(tmp_dir)
        if language == "javascript":
            return _run_npm_tsc_build(tmp_dir) if _find_one(tmp_dir, _PACKAGE_JSON) else _run_source_checks(tmp_dir, language)
        if language in {"c", "cpp"}:
            return _run_c_family_build(tmp_dir, language)
        if language in {"python", "cobol", "php", "ruby", "go"}:
            if language == "php" and _find_one(tmp_dir, "composer.json"):
                primary = _run_manifest_build(
                    tmp_dir, "composer", ["install", "--no-interaction", "--prefer-dist"], ["test"],
                )
                frontend = _run_npm_tsc_build(tmp_dir) if _find_one(tmp_dir, _PACKAGE_JSON) else None
                return _combine_build_results(primary, frontend)
            if language == "ruby" and _find_one(tmp_dir, "Gemfile"):
                primary = _run_manifest_build(
                    tmp_dir, "bundle", ["install"], ["exec", "rails", "runner", "puts :ok"],
                )
                frontend = _run_npm_tsc_build(tmp_dir) if _find_one(tmp_dir, _PACKAGE_JSON) else None
                return _combine_build_results(primary, frontend)
            if language == "cobol":
                return _run_cobol_project_build(tmp_dir)
            return _run_source_checks(tmp_dir, language)
        if language == "rust":
            primary = _run_manifest_build(tmp_dir, "cargo", ["test", "--all-targets"])
            frontend = _run_npm_tsc_build(tmp_dir) if _find_one(tmp_dir, _PACKAGE_JSON) else None
            return _combine_build_results(primary, frontend)
        if language == "kotlin":
            return _run_manifest_build(tmp_dir, "gradle", ["test", "--no-daemon"])
        if language == "swift":
            return _run_manifest_build(tmp_dir, "swift", ["build"])
        if language == "scala":
            return _run_manifest_build(tmp_dir, "sbt", ["-batch", "test"])
        if language == "clojure":
            # The official Windows CLI is optional: Maven plus the Clojure
            # compiler plugin provides a reproducible JVM compilation route.
            return _run_maven_build(tmp_dir)
        if language == "dart":
            pubspec = _find_one(tmp_dir, "pubspec.yaml")
            is_flutter = bool(pubspec and re.search(r"(?m)^\s*flutter\s*:", pubspec.read_text(encoding="utf-8")))
            if is_flutter:
                primary = _run_manifest_build(tmp_dir, "flutter", ["test"])
                dotnet = _run_dotnet_build(tmp_dir) if _find_one(tmp_dir, "*.csproj") else None
                return _combine_build_results(primary, dotnet)
            return _run_manifest_build(tmp_dir, "dart", ["pub", "get"], ["test"])
        if language == "elixir":
            return _run_manifest_build(tmp_dir, "mix", ["deps.get"], ["test"])
        if language == "erlang":
            return _run_erlang_otp_build(tmp_dir)
        if language == "r":
            return _run_manifest_build(tmp_dir, "Rscript", ["-e", "parse(file='app.R')"])
        if language == "julia":
            return _run_manifest_build(
                tmp_dir, "julia", ["--project=.", "-e", "using Pkg; Pkg.instantiate(); Pkg.test()"],
            )
        if language == "haskell":
            command = "stack" if _which("stack") else "cabal"
            return _run_manifest_build(
                tmp_dir, command, ["build", "--test"] if command == "stack" else ["build", "all"],
            )
        if language == "lisp":
            return _run_manifest_build(tmp_dir, "sbcl", ["--non-interactive", "--load", "main.lisp"])
        if language == "shell":
            return _run_manifest_build(tmp_dir, "bash", ["smoke.sh"])
        return BuildResult(
            False, "unsupported-build-route",
            {_BUILD_KEY: [f"No strict project validation route is registered for language={language!r}"]},
        )
    except Exception as exc:  # belt-and-suspenders — report infrastructure failure honestly
        return BuildResult(
            False, "build-runner-error",
            {_BUILD_KEY: [f"Build validation could not complete: {exc}"]},
            raw_output=f"build_runner internal error: {exc}",
        )


_MANIFESTS_BY_TOOL = {
    "cargo": "Cargo.toml", "gradle": "build.gradle.kts", "swift": "Package.swift",
    "sbt": "build.sbt", "clojure": "deps.edn", "flutter": "pubspec.yaml",
    "Rscript": "DESCRIPTION", "julia": "Project.toml", "stack": "stack.yaml",
    "cabal": "*.cabal", "sbcl": "*.asd", "composer": "composer.json",
    "bash": "tests/smoke.sh",
    "bundle": "Gemfile",
    "dart": "pubspec.yaml", "mix": "mix.exs",
}


# Function: _run_manifest_build
def _run_manifest_build(
    tmp_dir: Path, tool: str, args: List[str], after: Optional[List[str]] = None,
) -> BuildResult:
    """Run a framework/package-manager build from the manifest-owning directory."""
    executable = _which(tool)
    if not executable:
        return BuildResult(False, _MISSING_TOOLCHAIN, {_BUILD_KEY: [f"{tool} not found on PATH"]})
    manifest = _find_one(tmp_dir, _MANIFESTS_BY_TOOL[tool])
    if not manifest:
        expected = _MANIFESTS_BY_TOOL[tool]
        return BuildResult(False, _MISSING_MANIFEST, {_BUILD_KEY: [f"Generated output has no {expected}"]})
    outputs: List[str] = []
    for command_args in (args, after):
        if not command_args:
            continue
        try:
            proc = subprocess.run(
                [executable, *command_args], cwd=str(manifest.parent),
                capture_output=True, text=True, timeout=_BUILD_TIMEOUT,
                env=executable_environment(executable),
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return BuildResult(False, f"{tool}-build", {_BUILD_KEY: [str(exc)]}, "\n".join(outputs))
        combined = (proc.stdout + "\n" + proc.stderr).strip()
        outputs.append(combined)
        if proc.returncode:
            return BuildResult(
                False, f"{tool}-build",
                {_BUILD_KEY: [combined[-3000:] or f"{tool} build failed"]},
                "\n".join(outputs),
            )
    return BuildResult(True, f"{tool}-build", raw_output="\n".join(outputs))


# Function: _run_cobol_project_build
def _run_cobol_project_build(tmp_dir: Path) -> BuildResult:
    """Compile and link every generated COBOL program independently."""
    executable = _which("cobc")
    if not executable:
        return BuildResult(False, _MISSING_TOOLCHAIN, {_BUILD_KEY: ["cobc not found on PATH"]})
    sources = sorted({*tmp_dir.rglob("*.cob"), *tmp_dir.rglob("*.cbl")})
    if not sources:
        return BuildResult(False, "missing-source", {_BUILD_KEY: ["Generated output contains no COBOL source files"]})
    outputs = []
    for index, source in enumerate(sources):
        output = tmp_dir / f"cobol-program-{index}.exe"
        try:
            proc = subprocess.run(
                [executable, "-x", "-std=ibm", str(source), "-o", str(output)],
                cwd=str(source.parent), capture_output=True, text=True, timeout=_BUILD_TIMEOUT,
                env=executable_environment(executable),
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return BuildResult(False, "cobol-build", {_BUILD_KEY: [str(exc)]}, "\n".join(outputs))
        combined = (proc.stdout + "\n" + proc.stderr).strip()
        outputs.append(combined)
        if proc.returncode:
            return BuildResult(False, "cobol-build", {
                source.relative_to(tmp_dir).as_posix(): [combined[-3000:] or "COBOL build failed"],
            }, "\n".join(outputs))
    return BuildResult(True, "cobol-build", raw_output="\n".join(outputs))


# Function: _run_erlang_otp_build
def _run_erlang_otp_build(tmp_dir: Path) -> BuildResult:
    """Compile a complete OTP application and execute generated EUnit tests."""
    erlc, erl = _which("erlc"), _which("erl")
    if not (erlc and erl):
        return BuildResult(False, _MISSING_TOOLCHAIN, {_BUILD_KEY: ["erlc/erl not installed"]})
    sources = sorted(tmp_dir.rglob("*.erl"))
    if not sources:
        return BuildResult(False, "missing-source", {_BUILD_KEY: ["Generated output contains no Erlang source"]})
    ebin = tmp_dir / "__erlang_ebin"
    ebin.mkdir(exist_ok=True)
    environment = executable_environment(erlc)
    compile_proc = subprocess.run(
        [erlc, "-Werror", "-o", str(ebin), *map(str, sources)],
        cwd=str(tmp_dir), capture_output=True, text=True,
        timeout=_BUILD_TIMEOUT, env=environment,
    )
    compile_output = compile_proc.stdout + "\n" + compile_proc.stderr
    if compile_proc.returncode:
        return BuildResult(False, "erlang-build", {_BUILD_KEY: [compile_output[-3000:]]}, compile_output)
    tests = [source.stem for source in sources if source.stem.endswith("_tests")]
    if not tests:
        return BuildResult(True, "erlang-build", raw_output=compile_output)
    expression = f"case eunit:test([{','.join(tests)}], [verbose]) of ok -> halt(0); _ -> halt(1) end."
    test_proc = subprocess.run(
        [erl, "-noshell", "-pa", str(ebin), "-eval", expression],
        cwd=str(tmp_dir), capture_output=True, text=True,
        timeout=_BUILD_TIMEOUT, env=executable_environment(erl),
    )
    output = compile_output + test_proc.stdout + "\n" + test_proc.stderr
    return BuildResult(
        test_proc.returncode == 0, "erlang-build",
        {} if test_proc.returncode == 0 else {_BUILD_KEY: [output[-3000:]]},
        output,
    )


_SOURCE_CHECK_SPECS = {
    "python": ("python", ["-m", "compileall", "-q", "."]),
    "go": ("go", ["test", "./..."]),
    "php": ("php", None), "ruby": ("ruby", None),
    "cobol": ("cobc", None), "c": (_CLANG, None),
    "cpp": (_CLANG_CPP, None), "javascript": ("node", None),
}
_SOURCE_EXTENSIONS = {
    "php": ("*.php",), "ruby": ("*.rb",),
    "cobol": ("*.cob", "*.cbl", "*.cpy"),
    "c": ("*.c",), "cpp": ("*.cpp", "*.cc", "*.cxx"),
    "javascript": ("*.js", "*.jsx", "*.mjs", "*.cjs"),
}


# Function: _source_check_executable
def _source_check_executable(language: str, command: str) -> Optional[str]:
    if language == "php":
        return _which(command)
    if language == "c":
        return shutil.which(_CLANG) or shutil.which("gcc")
    if language == "cpp":
        return shutil.which(_CLANG_CPP) or shutil.which("g++")
    return shutil.which(command)


# Function: _source_files
def _source_files(tmp_dir: Path, language: str) -> List[Path]:
    return sorted({
        path
        for pattern in _SOURCE_EXTENSIONS[language]
        for path in tmp_dir.rglob(pattern)
    })


# Function: _source_commands
def _source_commands(
    executable: str, language: str, fixed_args: Optional[List[str]], files: List[Path],
) -> List[List[str]]:
    if fixed_args is not None:
        return [[executable, *fixed_args]]
    paths = [str(path) for path in files]
    if language in {"c", "cpp"}:
        return [[executable, "-fsyntax-only", *paths]]
    flags = {"cobol": "-fsyntax-only", "php": "-l", "ruby": "-c"}
    flag = flags.get(language, "--check")
    return [[executable, flag, path] for path in paths]


# Function: _execute_source_commands
def _execute_source_commands(
    commands: List[List[str]], tmp_dir: Path, language: str,
) -> BuildResult:
    output_parts = []
    for command in commands:
        proc = subprocess.run(
            command, cwd=str(tmp_dir), capture_output=True,
            text=True, timeout=_BUILD_TIMEOUT,
        )
        combined = (proc.stdout + "\n" + proc.stderr).strip()
        output_parts.append(combined)
        if proc.returncode != 0:
            return BuildResult(
                False, f"{language}-build",
                {_BUILD_KEY: [combined[-3000:] or "Build failed"]},
                "\n".join(output_parts),
            )
    return BuildResult(True, f"{language}-build", raw_output="\n".join(output_parts))


# Function: _python_test_commands
def _python_test_commands(executable: str, tmp_dir: Path) -> Optional[List[List[str]]]:
    test_files = list(tmp_dir.rglob("test*.py"))
    if not test_files:
        return None
    test_roots = sorted({path.parent.relative_to(tmp_dir) for path in test_files})
    discovery_script = (
        "import os,sys,unittest;"
        "os.chdir(sys.argv[1]);sys.path.insert(0,os.getcwd());"
        "suite=unittest.defaultTestLoader.discover(sys.argv[2],pattern='test*.py');"
        "result=unittest.TextTestRunner(verbosity=1).run(suite);"
        "raise SystemExit(0 if result.wasSuccessful() and result.testsRun else 1)"
    )
    commands = []
    for test_root in test_roots:
        parts = test_root.parts
        project_root = parts[0] if len(parts) > 1 else "."
        start_directory = str(Path(*parts[1:])) if len(parts) > 1 else str(test_root)
        commands.append([
            executable, "-c", discovery_script, project_root, start_directory,
        ])
    return commands


# Function: _run_source_checks
def _run_source_checks(tmp_dir: Path, language: str) -> BuildResult:
    """Run a native whole-output syntax/build check for non-MSBuild/Maven stacks."""
    command, fixed_args = _SOURCE_CHECK_SPECS[language]
    executable = _source_check_executable(language, command)
    if not executable:
        return BuildResult(
            False, _MISSING_TOOLCHAIN,
            {_BUILD_KEY: [f"Required {language} build tool is not installed"]},
        )
    files = [] if fixed_args is not None else _source_files(tmp_dir, language)
    if fixed_args is None and not files:
        return BuildResult(
            False, "missing-source",
            {_BUILD_KEY: [f"Generated output contains no {language} source files"]},
        )
    commands = _source_commands(executable, language, fixed_args, files)
    if language == "python":
        test_commands = _python_test_commands(executable, tmp_dir)
        if test_commands is None:
            return BuildResult(
                False, "missing-tests",
                {_BUILD_KEY: ["Python project validation requires generated unittest test files"]},
            )
        commands.extend(test_commands)
    return _execute_source_commands(commands, tmp_dir, language)


# Function: _combine_build_results
def _combine_build_results(primary: BuildResult, frontend: Optional[BuildResult]) -> BuildResult:
    """Fail a full-stack build when either backend or frontend fails."""
    if frontend is None:
        return primary
    errors = {**primary.errors_by_file}
    for path, messages in frontend.errors_by_file.items():
        errors.setdefault(path, []).extend(messages)
    for path, messages in list(errors.items()):
        errors[path] = list(dict.fromkeys(messages))
    effective = [result for result in (primary, frontend) if result.checker != "skipped"]
    if not effective:
        return BuildResult(True, "skipped", raw_output=primary.raw_output + "\n" + frontend.raw_output)
    return BuildResult(all(result.passed for result in effective), "+".join(result.checker for result in effective),
                       errors, primary.raw_output + "\n" + frontend.raw_output)
