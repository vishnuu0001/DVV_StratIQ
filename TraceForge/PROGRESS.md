# TraceForge — Build Progress

Full spec: `Requirements.MD`. This file tracks what's actually built vs. what's still spec-only, so nobody has to diff the code against the spec to find out.

**Status: full SDLC factory built and verified end-to-end** — ingestion through ServiceNow/JIRA/GitHub connectors, all five agents (Requirement Extractor, BRD/FSD/Solution-Doc Author, Test Designer, Script Generator, Doc Renderer), hybrid retrieval, suspect-link propagation, and the complete gated pipeline (Gate 1–4). This supersedes the earlier "Phase 0 + Phase 1 only" build — that version was explicitly rejected as too narrow a slice of the spec; everything below is the real implementation, not a stub returning 501.

## Governed workspace expansion (2026-07-23)

The UI is now grouped by lifecycle activity: Discovery, Requirements,
Specifications, Verification, Traceability, Governance, and Settings. Existing
bookmarks redirect to the new routes.

- Requirement Quality & Conflicts performs deterministic evidence, ambiguity,
  acceptance-criteria, exact-duplicate, and opposing-polarity checks.
- Specifications generate four separately versioned deliverables: BRD, SRS/FRS,
  Functional Design, and Architecture/Solution Design. Generated narrative
  carries source labels, and regeneration increments artifact versions.
- Baselines are immutable, content-addressed snapshots of requirements, tests,
  scripts, and artifacts. Baseline creation is audited.
- Reviews & Approvals consolidates every gate and advances the governed pipeline
  after approval.
- Template upload supports project DOCX/DOTX templates and XLSX RTM templates,
  with type and size validation.
- Integrations persist only non-secret endpoint/project mappings. Credential-like
  keys are rejected; connector credentials remain request-scoped.
- Project Settings validates governed ambiguity thresholds and coverage policy.
- The production frontend is split into cacheable vendor/editor/diagram chunks.

This expansion does not claim capabilities that are still listed under
"What's still out of scope" below, including test execution, full product-line
variant management, or regulated electronic signatures.

## Deployment reality (read this before touching config)

The spec assumes Anthropic Claude, Azure Key Vault, Entra ID, Managed Identity, and Azure Blob Storage. **None of that is used.** This deployment is Azure VMs running native processes, matching every other module in this repo:

- **LLM**: Ollama only (`qwen3.5:9b` for generation, `nomic-embed-text` for embeddings). `traceforge/llm/provider.py` defines an `LLMProvider` ABC so a second provider is a config change, but only `OllamaProvider` exists.
- **Auth**: the shared `v1.{payload}.{sig}` HMAC token every module uses, not Entra ID/OIDC. `traceforge/auth.py` is a straight port of `SSDLC_Process_Assessment/backend/app/auth.py`.
- **Database**: local PostgreSQL 16 + pgvector (database `traceforge`, role `tf_admin`/`tf_secret`), not Azure Database for PostgreSQL Flexible Server.
- **Job queue**: the existing local Memurai instance (`redis://127.0.0.1:6379/3`), not Azure Cache for Redis. **Use the literal `127.0.0.1`, not `localhost`** — `localhost` resolves to `::1` first on this box and Memurai isn't listening on IPv6.
- **Storage**: local disk (`TraceForge/data/blobs/`), not Azure Blob Storage.
- **Secrets**: `.env` files and the watchdog script's inline `Env` blocks, not Key Vault.
- **Hosting**: the same IIS URL-Rewrite reverse-proxy pattern every other module uses. The Arq worker runs as its own watchdog-managed process (`TraceForge-Worker`) — critically, **not** inside the IIS/uvicorn process, so an app-pool recycle can't lose a running agent job.
- **Frontend**: served via an IIS Virtual Directory (`/tf` → `TraceForge/ui/dist`).

## What works end-to-end

**Connectors** (`traceforge/connectors/`)
- `servicenow.py` — table API fetch (`incident`/`sc_req_item`/`sc_task`/`change_request`/`kb_knowledge`/`cmdb_ci`), HDBSCAN clustering of incidents by category/subcategory/app + semantic similarity, synthesized `INCIDENT PATTERN:` chunks feed Test Designer's negative-case evidence. `sys_attachment` handling is not implemented (documented gap).
- `jira.py` — JQL search + read, `create_issue_from_requirement` and `comment_on_issue` write-back. Verified via mocked-HTTP unit tests (no live JIRA instance available this pass).
- `github.py` — clone + tree-sitter parse for legacy-code ingestion, `open_pr_with_scripts` write-back (branch, commit, PR via PyGithub). Verified via mocked unit tests (no live repo available this pass).

**Parsing** (`traceforge/parsing/`) — `docx.py`, `pdf.py` (pymupdf + pytesseract OCR fallback), `xlsx.py` (openpyxl), `code.py` (tree-sitter-languages, per-language chunk-node tables, `tree-sitter` pinned to 0.21.3 for compatibility). `pptx`/`bpmn`/image parsing remain stubbed — narrower, higher-effort, not part of the requested scope.

**Agent 1 — Requirement Extractor** (`agents/extractor.py`) — sweeps every indexed chunk in document order, EARS-formatted output, P1 citation enforcement both at the API layer and via a Postgres `DEFERRABLE` constraint trigger (`trg_requirement_has_citation`).

**Agents 2 — BRD/FSD/Solution Doc Authors** (`agents/doc_author.py`, `agents/docx_render.py`) — all three generated together under one Gate 2 from the same approved-requirement set, same GENERATED/REQ_TABLE/GLOSSARY/RTM_SUMMARY section-mode split, shared `.docx` rendering engine (client-template `{{SECTION:key}}` placeholder mode + a built-in default style). `Artifact.requirement_ids` + `stale` columns back suspect-propagation.

**Agent 3 — Test Designer** (`agents/test_designer.py`, `agents/coverage_policy.py`) — one project-level `TestPlan` (scope/strategy/environments/entry-exit criteria, P1-cited) plus per-requirement `TestCase`s with incident-evidence injection via hybrid retrieval and an auto-reprompt-once-on-coverage-gap loop. **Fixed 2026-07-12**: the reprompt loop was deleting the final attempt's test cases even when coverage gaps remained after the retry, silently leaving some requirements with zero test cases despite the run reporting a nonzero count for them — spec says accept the last attempt, not discard it. Now fixed and reverified (all 6 DEMO-1 requirements have real, persisted coverage).

**Agent 4 — Script Generator** (`agents/script_gen/`) — deterministic TypeScript codegen per `TestCase.steps`, separate Playwright and Selenium emitters (not one framework-agnostic script), `TODO_LOCATOR()` markers + `compiles=false` whenever no UI artifact exists to ground real selectors against (never hallucinates a selector). Real `tsc --noEmit` validation via a pre-installed `TraceForge/toolchain/node_modules` (Windows directory junction, no `npm install` at validation time). Test execution is out of scope by design — scripts are generated, never run.

**Agent 5 — Doc Renderer** (`agents/renderer/`) — `rtm_xlsx.py` produces all 6 sheets (RTM/TestCases/Scripts/Coverage Summary/Gaps/Audit) with every derived column a live formula (`TEXTJOIN`/`COUNTIF`/`COUNTIFS`/nested `IF`/`FILTER`), never a hardcoded value. `evidence_pack.py` builds the full ZIP (documents, RTM, scripts by tool, source index, audit trail, sha256 manifest).

**Hybrid retrieval** (`indexing/retriever.py`) — pgvector cosine + Postgres `ts_rank_cd` BM25, fused via Reciprocal Rank Fusion (k=60), reranked with a local CPU cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`, `sentence-transformers`). Runs off the event loop via `asyncio.to_thread` and is pinned to CPU explicitly — this box's GPU is a shared vGPU slice (A10-8Q) that Ollama already keeps busy, and letting the reranker auto-detect a device caused multi-minute stalls under contention.

**Suspect-link propagation** (`orchestration/suspect.py`) — editing an approved Requirement flips its downstream `TestCase`/`TestScript` rows to `SUSPECT` and referencing Artifacts to `stale=True`, never deletes. `get_requirement_impact` gives a read-only preview for the UI banner. Covered by `tests/test_suspect_propagation.py`.

**Gate state machine** (`orchestration/gates.py`) — EXTRACT → BRD (fans out to BRD+FSD+SolutionDoc) → TEST_DESIGN → SCRIPT_GEN → RENDER, each gated. Approving a gate cascades DRAFT/IN_REVIEW items of the relevant kind to APPROVED (honoring per-item REJECT overrides) — without this, nothing downstream could ever find an approved row to work from.

**Frontend** — Overview (React Flow pipeline DAG, gates as diamonds, blocking gate visually prominent), Sources (upload + ServiceNow/JIRA/GitHub connector forms), Requirements, Documents (BRD/FSD/SolutionDoc together), Test Cases (Test Plan summary + per-requirement grouping + coverage badges), Scripts (Monaco split-view, compile-status banner, `TODO_LOCATOR` markers visible), Traceability (live RTM-mirroring grid), Artifacts, Audit. Verified via a real headless-Chromium walkthrough of all 9 pages against a fully-populated DEMO-1 project — zero console errors, zero failed requests.

## What's still out of scope (unchanged, agreed up front)

- **Executing** generated tests — TraceForge generates, never runs them.
- Full OS-level Job Object sandbox for script validation — `deploy/sandbox/Provision-Sandbox.ps1` is a ready-to-run artifact, not yet executed; validation runs via plain `subprocess`/`asyncio.create_subprocess_exec` + timeout instead.
- Azure Key Vault / Entra ID / Managed Identity / Blob Storage — not used, per this deployment's constraints.
- `pptx`/`vsdx`-bpmn/image parsers — narrower, higher-effort, not part of the requested scope.
- RBAC / Entra ID groups → roles, PII redaction, cost-budget hard-stops (spec's Phase 4).
- Azure DevOps pipeline — this repo deploys via the watchdog script + manual `npm run build`.
- Dedup / conflict detection on re-running Extract against the same corpus (creates duplicates rather than merging by embedding similarity).

## Bugs found and fixed during end-to-end verification (2026-07-12)

Full pipeline verification (Extract → BRD/FSD/SolutionDoc → Test Design → Script Gen → Render, all four gates) surfaced four real bugs that unit tests alone didn't catch, because each only manifests when actual runs execute against a live Postgres/Redis/Ollama stack:

1. **Stale `ck_kind` CHECK constraints** — migration `9ccc5f1342c6` (full_sdlc) added `FSD_DOCX`/`SOLUTION_DOC_DOCX`/`TEST_PLAN_DOCX` to the `ArtifactKind` Python enum and `SELENIUM_TS` to `ScriptTarget`, but never updated the corresponding Postgres CHECK constraints on `artifact.kind`, `template.kind`, and `test_script.target` — they still enforced the pre-migration value lists. Every FSD/SolutionDoc/TestPlan insert failed with `CheckViolationError`. Fixed in migration `1c09d22c8873`.
2. **Poisoned-session failure handlers** — `workers/tasks.py`'s per-stage exception handlers tried to write `status="FAILED"` using the same session whose transaction had just aborted from the exception above, which itself raised `PendingRollbackError` — silently swallowed by arq, leaving the `PipelineRun` stuck at `RUNNING` forever with no error surfaced anywhere. This is what looked like an indefinite hang. Fixed by rolling back before writing the failure status in all four handlers.
3. **Reranker event-loop stall** — `CrossEncoder` auto-detected a device and the first call's model load/inference ran synchronously on the event loop; combined with this box's shared vGPU slice already busy running Ollama, `hybrid_search` calls stalled for 18+ minutes. Fixed by forcing `device="cpu"` explicitly and wrapping the call in `asyncio.to_thread`.
4. **Coverage-gap reprompt loop discarded the final attempt** — `_generate_test_cases_for_requirement`'s "reprompt once, then accept" loop unconditionally deleted a requirement's test cases whenever `check_coverage` still found gaps, including on the *last* allowed attempt — so any requirement that still had a coverage gap after its retry ended up with **zero** persisted test cases, even though the run's stats reported a nonzero count for it. Fixed by only deleting-and-retrying when another attempt remains.

All four were caught by actually running the full pipeline against `DEMO-1` end-to-end rather than trusting unit tests or a single stage in isolation — the coverage-gap bug in particular only showed up as a discrepancy between the API's reported `test_cases_created` count and the actual row count in Postgres, and only for a requirement whose LLM output happened to lack a negative case on both attempts.

## Known rough edges

- `qwen3.5:9b` fits fully in the 12 GB GPU. Agent jobs are serialized and have a four-hour timeout so large project-wide runs can complete without GPU contention or stale retries.
- Re-running Extract against the same source documents creates new duplicate requirements each time (dedup not implemented).
- Live JIRA/GitHub round-trips are unverified — only mocked-HTTP unit tests, since no live credentials were available this pass.

## Running it locally

```powershell
# Backend
cd TraceForge/api
.venv\Scripts\python.exe -m uvicorn traceforge.main:app --host 0.0.0.0 --port 8095 --log-level info

# Worker (separate process — required for any pipeline run to actually execute)
.venv\Scripts\python.exe -m arq traceforge.workers.arq_worker.WorkerSettings

# Tests
.venv\Scripts\python.exe -m pytest tests/ -v

# Frontend dev server
cd TraceForge/ui
npm run dev   # http://localhost:5186/tf/
```

In production both backend processes are watchdog-managed (`TraceForge-API`, `TraceForge-Worker` in `watchdog_all_backends.ps1`) and the frontend is the built `TraceForge/ui/dist` served via the `/tf` IIS virtual directory — `npm run build` after any frontend change, no separate deploy step needed.
