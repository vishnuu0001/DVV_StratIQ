# Infrastructure Requirements — Modernization Module (Standalone On-Premises Deployment)


---

## 1. Minimum vs Recommended Hardware

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | Intel Core i7 (8-core, 2.5 GHz+) | Intel Core i9 / Xeon (16-core, 3.0 GHz+) |
| **RAM** | 32 GB DDR4 | 96 GB DDR4/DDR5 |
| **GPU** | NVIDIA RTX 3060 (12 GB VRAM) | NVIDIA RTX 4070 SUPER (12 GB VRAM) or RTX 4090 (24 GB VRAM) |
| **GPU VRAM** | 8 GB (runs `qwen2.5-coder:7b` fully in VRAM) | 24 GB (runs `qwen3-coder:30b` natively) |
| **System Disk (OS + App)** | 200 GB SSD | 500 GB NVMe SSD |
| **Data / Model Disk** | 200 GB (Ollama models) | 500 GB NVMe SSD (models + cache) |
| **Network** | 100 Mbps (internal) | 1 Gbps (for initial model downloads) |

> **Why high RAM?** Models like `qwen3-coder:30b` require VRAM + CPU RAM offloading. With 12 GB GPU VRAM, the remaining model layers load into system RAM. 96 GB ensures smooth offloading with headroom.

---

## 2. Operating System

| Requirement | Specification |
|-------------|---------------|
| **OS** | Windows Server 2019 / 2022 (recommended) or Ubuntu 22.04 LTS |
| **Architecture** | x86-64 (64-bit) only |
| **IIS** | IIS 10.0+ with URL Rewrite Module 2.1 (Windows) |
| **PowerShell** | PowerShell 5.1+ (for watchdog service) |
| **GPU Drivers** | NVIDIA Driver 525+ (CUDA 12.x compatible) |
| **CUDA Toolkit** | CUDA 12.1+ (required by Ollama for GPU inference) |
| **cuDNN** | 8.9+ (required for optimal inference throughput) |

---

## 3. Software Runtime Stack

### 3.1 Python Backend

| Package | Version | Purpose |
|---------|---------|---------|
| Python | 3.11 or 3.12 | Runtime |
| FastAPI | 0.111.0 | REST API framework |
| Uvicorn | 0.29.0 | ASGI server |
| httpx | 0.27.0 | Async HTTP client (Ollama calls) |
| pymupdf | ≥ 1.24.0 | PDF document parsing |
| python-docx | ≥ 1.1.0 | Word document parsing |
| python-multipart | ≥ 0.0.9 | File upload handling |
| pyyaml | 6.0.1 | YAML config parsing |
| python-dotenv | 1.0.1 | Environment variable management |

**Estimated Python venv disk usage**: ~150–250 MB

### 3.2 Node.js / Frontend Build

| Component | Version | Purpose |
|-----------|---------|---------|
| Node.js | 20 LTS (or 22 LTS) | Frontend build runtime |
| npm | 10+ | Package manager |
| Vite | 5.4.11 | Build bundler |
| React | 18.3.1 | UI framework |

**Frontend `node_modules` disk usage**: ~800 MB–1 GB (only needed at build time)  
**Production build output (`dist/`)**: ~2–5 MB (served as static files)

### 3.3 Code-Generation Validation — Phase 1: per-file syntax checking

Every LLM-generated file is syntax-validated before being returned as final output (`services/validators.py`), with a bounded retry-and-fix loop on failure. This is per-file syntax-level validation only — no cross-file dependency resolution — so it stays useful even when Phase 2 (below) can't run.

| Language | Checker | Requirement |
|----------|---------|-------------|
| Python | `py_compile` (stdlib) | None — always available with the Python runtime already required above |
| Java | `javac` | JDK 17+ already on `PATH` or at a well-known install path (Eclipse Temurin/Oracle/OpenJDK). Dependency-resolution errors (`cannot find symbol`, missing Spring/Jakarta imports) are expected and filtered out — only genuine parse errors fail validation |
| TypeScript / JavaScript | `tsc --noEmit` | **One-time setup required** (see below) — without it, falls back to a weaker structural heuristic |
| C# | — (heuristic only) | No usable offline C# 9+ compiler exists for a per-file, no-classpath check (the only always-present Windows component, the legacy .NET Framework `csc.exe`, only understands C# 5 and would false-fail on records/top-level statements/file-scoped namespaces). Falls back to a structural heuristic (balanced braces, no leftover markdown fences, no placeholder text). A real C# compiler check exists at the whole-project level — see Phase 2 |
| SQL | `sqlglot` (Python package, in `requirements.txt`) | None — installed via `pip install -r requirements.txt`. Dialect (Postgres/T-SQL/Oracle/MySQL) is inferred from the target stack's `db_tech` string; DB2/UDB is validated via `sqlfluff`'s native `db2` dialect instead (also in `requirements.txt`) — `sqlglot` has no DB2 dialect and remains the fallback parser for every dialect `sqlfluff` doesn't cover |
| COBOL | `cobc` (GnuCOBOL) | Open-source, not IBM's proprietary Enterprise COBOL (a licensed z/OS-only product — not installable here). `-std=ibm -fformat=fixed` targets IBM-compatible fixed-format column conventions. Structural checks beyond compilation (PROGRAM-ID length, SELECT/FD matching, PERFORM target resolution) run on top |
| C17 / C++23 | `clang`/`clang++` (preferred) or `gcc`/`g++` | LLVM or MSYS2/MinGW toolchain on `PATH`. Phase 1 is a per-file `-fsyntax-only` pass; Phase 2 (below) does a real multi-file compile + link |

**One-time TypeScript validator setup** (not required for the module to run — only degrades TS/JS validation to the heuristic checker if skipped):
```powershell
cd Modernization\tools\ts-validate
npm init -y
npm install typescript --no-save
```
This vendors a local `typescript` package (`tools/ts-validate/node_modules/typescript/lib/tsc.js`) invoked directly via `node`, with no global `tsc` install.

### 3.4 Code-Generation Validation — Phase 2: real whole-project build + repair

For prompt-driven **multi-file "project" mode** generation targeting C#, Java, or TypeScript, `services/build_runner.py` materializes the entire generated project to disk after Phase 1 and runs a **real compiler build with full dependency resolution** (`dotnet build`, `mvn compile`, or `npm install` + `tsc --noEmit`), then feeds structured per-file build errors back to the LLM (`REPAIR_PROMPT`) for up to 3 whole-project rebuild rounds. Unlike Phase 1, this catches genuine cross-file defects — a missing member, an unresolved import, an undeclared package — because the dependencies are actually installed, not just syntax-parsed in isolation.

**Requires internet access at generation time** (not just at initial setup): `dotnet build` restores NuGet packages, `npm install` fetches the full frontend dependency tree, and `mvn compile` resolves Maven Central — all per job. This is a deliberate departure from the "fully air-gapped after initial setup" posture in section 6, made because this specific deployment has live outbound internet access; a genuinely air-gapped deployment would need a pre-warmed offline NuGet/npm/Maven package cache/mirror for Phase 2 to work at all, and should otherwise expect `run_build` to degrade to `checker="skipped"` (missing tool or failed restore never blocks the job — Phase 1's syntax check result still stands).

| Tool | Version installed | Install method |
|------|-------------------|-----------------|
| .NET SDK | 8.0.423 | `winget install --id Microsoft.DotNet.SDK.8 -e` |
| Maven | 3.9.9 | No official winget package — downloaded binary zip from `archive.apache.org/dist/maven/maven-3/3.9.9/binaries/apache-maven-3.9.9-bin.zip`, extracted to `C:\Tools\apache-maven-3.9.9`, `bin\` added to the machine `PATH` |
| Node/npm | already required (3.2 above) | — |

Both `dotnet` and `mvn` must resolve on `PATH` for the process the Modernization backend actually runs as (machine-level `PATH`, not a per-user or per-session addition, since the backend runs under the `Strat-Aqorynth-Master-Watchdog` scheduled task — see root `CLAUDE.md`). Verify with `dotnet --version` and `mvn --version` in a **fresh** shell after install; a shell open before the `PATH` change won't see it.

**Cost**: a real build + repair round can take 30s-3min per attempt (NuGet/npm/Maven resolution dominates), and the loop reruns the whole build after each repair round — this adds real, multi-minute latency to affected "project" mode jobs, visible to the user via the `"building"`/`"repairing"`/`"build-complete"` progress phases.

**C/C++ also get a real Phase 2 build**, distinct from the dependency-restore-driven languages above: every generated `.c`/`.cpp` file is compiled to an object file individually, then all objects are linked together (as an executable if a `main`/`WinMain` is present in the source, otherwise as a shared library) — this is what catches genuine cross-file link errors (undefined references to a sibling file's function, duplicate symbols) that a per-file `-fsyntax-only` pass structurally cannot.

#### Generated-stack prerequisite and build matrix

Catalog readiness is based on the complete framework toolchain, not merely the
language parser/compiler. Targets remain selectable when prerequisites are
missing, but the API returns `available: false` with the missing tools and
release validation fails closed.

| Generated target | Required build tools | Whole-project command |
|---|---|---|
| .NET 8 API + React/Angular/PostgreSQL/SQL Server | .NET 8 SDK, Node 20+, npm | `dotnet build`; frontend `npm install && npm run build` |
| .NET 8 microservices + Kubernetes | .NET 8 SDK, Node/npm; `kubectl` only for deployment | .NET/frontend builds; manifest parsing |
| NestJS + React / Next.js + Prisma | Node 20+, npm | `npm install && npm run build` |
| Kotlin Spring Boot / Ktor | JDK 21, Kotlin compiler, Gradle 8+ | `gradle test --no-daemon` |
| Go Gin/Fiber + React/Vue | Go 1.22+, Node/npm for SPA | `go test ./...`; frontend npm build |
| Rust Axum + React | Rust stable with Cargo; Node/npm for SPA | `cargo test --all-targets`; frontend npm build |
| Laravel + Vue | PHP 8.2+, Composer 2, Node/npm | `composer install && composer test`; frontend npm build |
| Flutter + .NET 8 API | Flutter SDK, .NET 8 SDK | `flutter test` and `dotnet build` |
| Swift + Vapor | Swift 5.10+ with Swift Package Manager | `swift build` |
| Bash automation | Bash 5+ | generated smoke script with `bash -n` |
| R + Shiny | R 4.x with Shiny and testthat | `Rscript` parse/test entry point |
| Scala + Play | JDK 17+, Scala 2.13, sbt 1.9+ | `sbt -batch test` |
| Clojure + Ring/Reitit | JDK 17+, Clojure CLI | `clojure -M:run` compile/startup check |
| Haskell + Servant | GHC, Stack or Cabal | `stack build --test` or `cabal build all` |
| Common Lisp | SBCL with ASDF | `sbcl --non-interactive --load main.lisp` |
| Julia | Julia 1.x | `Pkg.instantiate(); Pkg.test()` |
| IBM i / AS400 as modernization source | Exported RPG/RPGLE/SQLRPGLE, CL, DDS, DSPF/PRTF and copybook text | No IBM compiler required to analyze or generate Java/.NET/other targets |
| IBM i / AS400 as generated target or source-regression environment | IBM i with licensed 5770-WDS option 31 (ILE RPG), CL and Db2 for i | `CRTBNDRPG`; Db2 `RUNSQLSTM` |

Dependency resolution requires an approved registry or internal mirror/cache
(NuGet, npm, Maven/Gradle, Cargo, Composer, SwiftPM, Hackage/Stack, Julia).
Air-gapped deployments must pre-populate those caches.

### 3.4a Code-Generation Validation — Extended Language Toolchains

Beyond the languages in 3.3/3.4, the catalog (`GET /api/modernize/target-stacks`) supports a much larger set of legacy/enterprise target languages, split into two honesty tiers:

**Real compiler/runtime, installed and PATH-registered** (validators.py's `_EXTERNAL_VALIDATORS` runs the real tool per file across the whole generated project — same rigor as PHP/Ruby/COBOL in 3.3):

| Language | Tool | Install source |
|----------|------|-----------------|
| Rust | `rustc` | rustup (already present) |
| Swift | `swiftc` | Swift toolchain for Windows (already present) |
| Kotlin | `kotlinc` | Kotlin compiler distribution, `JetBrains/kotlin` GitHub releases |
| Scala | `scalac` | already present |
| Dart | `dart` | `winget install Google.DartSDK` |
| R | `Rscript` | `winget install RProject.R` |
| Julia | `julia` | `winget install Julialang.Julia` |
| Fortran | `flang-new`/`gfortran` | already present (LLVM / MSYS2) |
| Ada | `gnatmake` (GNAT) | already present (MSYS2) |
| Free Pascal | `fpc` | already present |
| Erlang | `erlc` | official installer, erlang.org |
| Elixir | `elixirc` | official installer, elixir-lang.org (requires Erlang first) |
| Common Lisp | `sbcl` | already present |
| SWI-Prolog | `swipl` | `winget install SWI-Prolog.SWI-Prolog` |
| Clojure | `clojure`/`clj` | `clojure-tools.zip` from `clojure/brew-install` GitHub releases (official installer script is interactive-only; wrapped in a thin `.cmd` invoking `java -classpath clojure-tools-VERSION.jar clojure.main` directly) |
| OCaml | `ocamlc` (DkML) | **Known broken on this box** — DkML's bundled toolchain rejects the installed Visual Studio Build Tools version ("has a version 18.0 not supported by DkML"); needs VS 2019/2022 Build Tools or a non-DkML OCaml distribution to fix |
| Haskell | `ghc` (via GHCup) | GHCup bootstrap installer, haskell.org |
| Protocol Buffers | `protoc` | already present (MSYS2) |

All of the above require adding their install directory to the **User or Machine `PATH`** — several installers on this box place binaries under `AppData\Local\Programs\...` or `C:\Tools\...` without ever registering `PATH`, so `winget list`/the installer reporting "already installed" does not mean the Modernization backend process can actually resolve the binary.

**Vendor compiler unavailable on this host — generation is supported but
release validation is externally gated.** Structural analysis can provide
diagnostics, but cannot produce a passing production-validation result without
the actual vendor compiler/platform:

| Language | Why no real compiler is possible here |
|----------|----------------------------------------|
| ABAP | Requires SAP |
| RPG generated as an IBM i target | Requires an IBM i platform with licensed 5770-WDS option 31. This is **not** required when RPG/CL/DDS are inputs being modernized to Java, .NET, Go, Python, or another non-IBM-i target. |
| JCL | Requires z/OS |
| MUMPS | No practical Windows-native open-source implementation |
| Natural | Requires Software AG's platform |
| Progress 4GL / OpenEdge ABL | Requires Progress Software's platform |
| Apex | Only executes inside a Salesforce org — cannot run standalone at all |
| PL/I | IBM's Enterprise PL/I is licensed/proprietary; the one open-source alternative (Iron Spring PL/I) is unmaintained |

### 3.4 Ollama (LLM Inference Engine)

| Component | Specification |
|-----------|--------------|
| **Ollama** | v0.3.0 or later |
| **Endpoint** | `http://localhost:11434` |
| **Protocol** | HTTP REST + streaming |
| **Model storage path** | `C:\Users\<user>\.ollama\models\` (Windows) or `/usr/share/ollama/.ollama/models/` (Linux) |

---

## 4. LLM Model Requirements

The Modernization module auto-selects the best available Ollama model in this priority order:

| Priority | Model | VRAM Required | Disk Size | Quality |
|----------|-------|--------------|-----------|---------|
| 1 (Best) | `qwen3-coder:30b` | ~17 GB (partial CPU offload) | ~19 GB | Highest |
| 2 | `qwen2.5-coder:7b` | ~4–5 GB | ~4.7 GB | Good |
| 3 | `qwen2.5-coder:32b` | ~18 GB (partial CPU offload) | ~20 GB | Highest |
| 4 | `qwen2.5-coder:3b` | ~2 GB | ~1.9 GB | Fast fallback |
| 5 | `deepseek-coder-v2:16b` | ~9–10 GB | ~9.1 GB | Good |
| 6 | `codellama:34b` | ~20 GB | ~19 GB | Moderate |
| 7 (Fallback) | `mistral:7b-instruct` | ~4 GB | ~4.1 GB | Basic |

**Recommendation for On-Prem**:  
- **8 GB VRAM GPU**: Install `qwen2.5-coder:7b` as primary model.
- **24 GB VRAM GPU**: Install `qwen3-coder:30b` for highest quality output.  
- Pull via: `ollama pull qwen2.5-coder:7b`

**LLM inference parameters (configured in code):**

| Parameter | Value |
|-----------|-------|
| Context window | 16,384 tokens (adaptive per file) |
| Max output tokens | 4,096 tokens |
| Temperature | 0.10 (deterministic code generation) |
| Model keep-alive | 10 minutes (stays hot in VRAM) |
| Request timeout | 360 seconds per file |
| Parallel workers | 5 (configurable via `MODERNIZATION_WORKERS`) |

---

## 5. Disk Storage Breakdown

| Component | Estimated Size | Notes |
|-----------|---------------|-------|
| OS (Windows Server 2022) | ~30 GB | Base OS |
| NVIDIA Drivers + CUDA | ~5–8 GB | GPU compute stack |
| Ollama binary | ~100 MB | Inference engine |
| LLM Models (1–2 models) | ~10–40 GB | Stored in Ollama model dir |
| Python `.venv` | ~250 MB | Module dependencies |
| Node `node_modules` | ~1 GB | Build-time only |
| Frontend `dist/` | ~5 MB | Served static files |
| Application code | ~20 MB | Source + assets |
| LLM cache (`%TEMP%`) | ~1–10 GB (grows) | Per-file conversion cache |
| Logs | ~500 MB | Watchdog + uvicorn logs |
| **Total (estimated)** | **~100–150 GB** | Including OS, models, app |

> **Recommended disk**: 500 GB NVMe SSD to accommodate model updates, cache growth, and large project analysis.

---

## 6. Network Requirements

| Requirement | Specification |
|-------------|--------------|
| **Internal LAN** | 100 Mbps minimum (1 Gbps recommended) |
| **Internet access (setup only)** | Required for pip install, npm install, Ollama model downloads |
| **Internet access (runtime)** | NOT required — fully air-gapped after initial setup |
| **Firewall — inbound** | TCP 8084 (backend API), TCP 8090 (IIS/Nginx, if applicable) |
| **Firewall — localhost** | TCP 11434 (Ollama, internal only — must NOT be exposed externally) |
| **Firewall — outbound** | Block 11434 from external access |

> **Security Note**: Ollama listens on `localhost:11434` by default. Ensure firewall rules prevent external access to port 11434.

---

## 7. Environment Variables (Required)

Create a `.env` file in the `Modernization/` directory:

```env
# Authentication (must match shared Strat-Aqorynth secret if integrated, or set standalone value)
AUTH_TOKEN_SECRET=<your-secure-random-string-min-32-chars>
AUTH_TOKEN_TTL_SECONDS=28800
AUTH_REQUIRED=true

# CORS — add the URL(s) where your frontend is served
CORS_ORIGINS=http://localhost:8090,http://<server-ip>:8090

# Optional: restrict file system browsing to a safe root
MODERNIZATION_FS_ROOT=C:\Projects

# Optional: tune parallel workers (default 5 each)
MODERNIZATION_WORKERS=5
MODERNIZATION_DOM_WORKERS=5

# Optional: domain cache TTL in seconds (default 86400 = 24h)
MODERNIZATION_DOM_CACHE_TTL=86400

# Backend bind settings
HOST=0.0.0.0
PORT=8084
```

---

## 8. IIS Configuration (Windows On-Prem)

| Component | Requirement |
|-----------|-------------|
| IIS Version | 10.0+ |
| URL Rewrite Module | 2.1+ (for `/api/mod/*` proxy rules) |
| ARR (Application Request Routing) | Required if using IIS as reverse proxy |
| Static file handler | For serving `frontend/dist/` |
| SPA fallback rule | Rewrite all non-API routes to `index.html` |

**URL Rewrite rule** (in `web.config`):
```xml
<rule name="Modernization API Proxy" stopProcessing="true">
  <match url="^api/mod/(.*)" />
  <action type="Rewrite" url="http://localhost:8084/api/{R:1}" />
</rule>
```

---

## 9. Service Management

| Component | Method |
|-----------|--------|
| **Backend startup** | `watchdog_backend.ps1` (PowerShell watchdog) |
| **Auto-restart on crash** | Built into watchdog script |
| **Run as service** | Register via Windows Task Scheduler (at logon, highest privilege) |
| **Ollama startup** | `ollama serve` (register as Windows Service or Task Scheduler) |
| **Log location** | `Modernization\logs\` (watchdog + stderr) |

**Start command (manual)**:
```powershell
# Start Ollama
Start-Process "ollama" -ArgumentList "serve" -NoNewWindow

# Start Modernization backend
.\Modernization\.venv\Scripts\python.exe -m uvicorn api.server:app --host 0.0.0.0 --port 8084
```

---

## 10. Capacity Planning

| Workload | Recommended Config |
|----------|--------------------|
| 1–5 concurrent users, small projects (<50 files) | 32 GB RAM, RTX 3060 (12 GB VRAM), i7 8-core |
| 5–20 concurrent users, medium projects (50–500 files) | 64 GB RAM, RTX 4070 SUPER (12 GB VRAM), i9 16-core |
| 20+ concurrent users, large projects (500+ files) | 96 GB RAM, RTX 4090 (24 GB VRAM), Xeon 16-core+ |
| Enterprise / large monolith modernization | 128 GB RAM, Dual GPU (A100/H100), multi-node |

> **Throughput note**: On the single 8 GB GPU, use one concurrent generation worker with `qwen2.5-coder:7b`; project duration depends on source size and requested output length.

---

## 11. Pre-Deployment Checklist

- [ ] NVIDIA GPU driver (525+) installed and verified (`nvidia-smi`)
- [ ] CUDA 12.x toolkit installed
- [ ] Ollama installed and `ollama serve` running on port 11434
- [ ] Preferred LLM model pulled (`ollama pull qwen2.5-coder:7b`)
- [ ] Python 3.11+ installed and `pip` accessible
- [ ] Python venv created and dependencies installed (`pip install -r requirements.txt`)
- [ ] Node.js 20 LTS installed (for frontend build only)
- [ ] Frontend built (`cd frontend && npm install && npm run build`)
- [ ] JDK 17+ installed and `javac` reachable (for Java output validation)
- [ ] One-time TS validator setup done (`cd tools\ts-validate && npm install typescript --no-save`) — see section 3.3
- [ ] .NET 8 SDK installed and `dotnet` reachable on machine `PATH` (for real C# builds, Phase 2 — see section 3.4)
- [ ] Maven installed and `mvn` reachable on machine `PATH` (for real Java builds, Phase 2 — see section 3.4)
- [ ] Outbound internet access confirmed to `api.nuget.org`, `repo.maven.apache.org`/Maven Central, and the npm registry, if Phase 2 real builds are wanted (otherwise Phase 2 gracefully degrades to Phase 1 syntax-only)
- [ ] `.env` file configured with secure `AUTH_TOKEN_SECRET`
- [ ] IIS URL Rewrite rules configured (or Nginx reverse proxy configured)
- [ ] Firewall: TCP 8084 open internally, TCP 11434 blocked externally
- [ ] Windows Task Scheduler entry created for watchdog at logon
- [ ] Disk storage: at least 150 GB free before setup

---

## 12. Summary — Minimum Viable On-Prem Deployment

| Item | Specification |
|------|--------------|
| **Server** | 1x physical or VM server |
| **CPU** | Intel i7 / Xeon, 8+ cores |
| **RAM** | 32 GB DDR4 (96 GB recommended) |
| **GPU** | NVIDIA RTX 3060 12 GB VRAM (RTX 4070 SUPER recommended) |
| **Storage** | 500 GB NVMe SSD |
| **OS** | Windows Server 2022 or Ubuntu 22.04 LTS |
| **Runtime** | Python 3.11, Node.js 20 LTS, Ollama, IIS 10 / Nginx |
| **LLM Model** | `qwen2.5-coder:7b` (8 GB deployment), `qwen3-coder:30b` (24 GB deployment) |
| **Internet** | Required at setup; air-gapped at runtime |
| **External services** | None — fully self-contained |

---

