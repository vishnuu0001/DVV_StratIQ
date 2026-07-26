# CodeAnalysis

**Automated deep analysis of source code portfolios from GitHub.**  
Supports Java · .NET (C#/VB/F#) · Python · Mainframe (COBOL/JCL/ASM/PL-I/REXX)

---

## Features

| Metric | Description |
|---|---|
| **Software Health** | Composite of Resiliency, Agility, and Elegance (0–100) |
| **Technical Debt** | COCOMO II–inspired remediation effort in person-months + USD cost |
| **Cloud Maturity Index** | Readiness for cloud deployment (0–100) across 6 dimensions |
| **Open Source Safety** | Vulnerability scan, license compliance, and dependency freshness |
| **Business Impact Index** | Criticality score based on users, revenue, release cadence, and age |

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/your-org/CodeAnalysis.git
cd CodeAnalysis

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and set your GITHUB_TOKEN
```

A GitHub **Personal Access Token** with `read:repo` scope is recommended to:
- Access private repositories
- Avoid the unauthenticated rate limit (60 req/hr)

### 3. Analyse a Single Repository

```bash
# From a GitHub URL
python main.py analyse --repo https://github.com/pallets/flask

# From an owner/repo slug
python main.py analyse --repo pallets/flask

# From a local directory (no GitHub fetch)
python main.py analyse --local ./my-project

# With business context overrides
python main.py analyse --repo myorg/myapp --users 200000 --revenue 5000000
```

Reports are written to `output_reports/` by default:
- `<repo>_<timestamp>_report.html` – interactive dashboard
- `<repo>_<timestamp>_report.json` – machine-readable full data

### 4. Portfolio Scan (Organisation)

```bash
python main.py portfolio --org my-github-org --limit 30
```

Analyses up to 30 non-fork repositories and renders a portfolio table plus
individual HTML/JSON reports for each repo.

---

## CLI Reference

```
python main.py --help
python main.py analyse --help
python main.py portfolio --help
```

### `analyse` options

| Option | Default | Description |
|---|---|---|
| `--repo / -r` | — | GitHub URL or `owner/repo` slug |
| `--local / -l` | — | Path to local repository |
| `--users / -u` | 100 | Estimated user count (Business Impact) |
| `--revenue / -$` | 0 | Annual revenue impact in USD |
| `--output / -o` | `output_reports/` | Report output directory |
| `--format / -f` | `both` | `html`, `json`, or `both` |
| `--verbose / -v` | false | Enable debug logging |

---

## Project Structure

```
CodeAnalysis/
├── main.py                   ← CLI entry point
├── requirements.txt
├── .env.example
│
├── config/
│   └── settings.py           ← All tunable constants & thresholds
│
├── core/
│   ├── github_fetcher.py     ← GitHub API + git clone/pull
│   └── analyzer.py           ← Central orchestrator
│
├── analyzers/
│   ├── base_analyzer.py      ← Abstract base class + shared helpers
│   ├── python_analyzer.py    ← Python  (ast + radon + bandit)
│   ├── java_analyzer.py      ← Java    (regex + heuristics)
│   ├── dotnet_analyzer.py    ← C#/VB/F# (regex + heuristics)
│   └── mainframe_analyzer.py ← COBOL/JCL/ASM/PL-I/REXX
│
├── metrics/
│   ├── software_health.py    ← Resiliency / Agility / Elegance → Health
│   ├── technical_debt.py     ← COCOMO II debt estimation
│   ├── cloud_maturity.py     ← 6-dimension cloud readiness (0–100)
│   ├── open_source_safety.py ← pip-audit + PyPI/Maven metadata
│   └── business_impact.py    ← Business criticality index
│
├── reports/
│   ├── html_reporter.py      ← Self-contained HTML dashboard (Jinja2)
│   └── json_reporter.py      ← Structured JSON output
│
├── cloned_repos/             ← Auto-created; holds cloned repositories
└── output_reports/           ← Auto-created; holds generated reports
```

---

## Metrics Deep-Dive

### Software Health

```
Health = 0.40 × Resiliency + 0.35 × Agility + 0.25 × Elegance
```

| Sub-score | What is measured |
|---|---|
| **Resiliency** | Absence of patterns that compromise reliability/security (deep nesting, high cyclomatic complexity, empty catches, TODO density) |
| **Agility** | Ease of change (long-method ratio, comment coverage, bad-practice count) |
| **Elegance** | Simplicity (magic-number density, avg file size, complexity score) |

**Risk labels:** EXCELLENT (≥90) · GOOD (≥75) · FAIR (≥60) · POOR (≥40) · CRITICAL (<40)

### Technical Debt

Based on **COCOMO II** with effort multipliers derived from code complexity and reliability level:

```
Effort (PM) = 2.94 × KSLOC^0.91 × EM_complexity × EM_reliability
Debt (PM)   = Effort × debt_fraction(health_score)
Cost (USD)  = Debt × $8,000/month
```

### Cloud Maturity Index

| Dimension | Weight | Signal sources |
|---|---|---|
| Stateless Design | 20% | Absence of local file I/O, in-process session patterns |
| Containerization | 20% | Dockerfile, docker-compose, GitHub topics |
| API Surface | 15% | REST annotations, OpenAPI specs |
| Config Externalisation | 15% | `os.environ`, `Environment.GetEnvironmentVariable`, no hardcoded DSNs |
| Logging & Observability | 15% | Structured logging libraries, health-check endpoints |
| CI/CD Artifacts | 15% | GitHub Actions, Jenkinsfile, Azure Pipelines, CircleCI |

### Open Source Safety

1. **Security** (50%) – pip-audit CVE scan for Python dependencies
2. **Licensing** (30%) – checks against allowed SPDX license list
3. **Freshness** (20%) – flags packages with no release in 3+ years

### Business Impact

```
Impact = 0.25×UserVolume + 0.20×ReleaseFreq + 0.20×Revenue
       + 0.15×AgeRisk   + 0.10×Operational  + 0.10×Integration
```

---

## Configuration (`config/settings.py`)

Key tunable constants:

| Constant | Default | Description |
|---|---|---|
| `HEALTH_WEIGHTS` | resiliency=0.40, agility=0.35, elegance=0.25 | Health sub-score weights |
| `COCOMO_A` | 2.94 | COCOMO II calibration constant |
| `COCOMO_B` | 0.91 | Scale-factor exponent |
| `AVG_SALARY_MONTH` | 8000 | USD per FTE per month |
| `CLOUD_WEIGHTS` | (see file) | Cloud dimension weights |
| `MAX_DEPENDENCY_AGE_YEARS` | 3 | Flag stale dependencies older than N years |
| `ALLOWED_LICENSES` | MIT, Apache-2.0, BSD-*, … | Compliant SPDX license identifiers |

---

## Extending

### Add a new language

1. Create `analyzers/myLang_analyzer.py` extending `BaseAnalyzer`
2. Set `EXTENSIONS` to the relevant file suffixes
3. Implement `language_name()`, `_analyse_file()`, `_extract_dependencies()`
4. Register the class in `core/analyzer.py`  `_ANALYZERS` dict
5. Add the extension set to `config/settings.py`  `LANGUAGE_EXTENSIONS`

### Add a new metric

1. Create `metrics/my_metric.py` with a `@dataclass` result and a calculator class
2. Instantiate and call it in `core/analyzer.py`  `CodeAnalyzer.run()`
3. Add the result field to `AnalysisResult`
4. Render it in `reports/html_reporter.py` and `reports/json_reporter.py`

---

## License

MIT
