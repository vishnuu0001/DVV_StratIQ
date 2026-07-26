# TraceForge Performance Architecture

## Production profile (2026-07-14)

The production host has one 12 GB GPU and runs Ollama with `qwen3.5:9b` at an
8,192-token context. GPU generation is therefore serialized. The observed 19-chunk
project contained 8,421 source tokens and produced 47 persisted requirements.

The original project-scale path was slow primarily because it multiplied GPU calls:

- EXTRACT requested up to 7,000 output tokens per four-chunk batch and exposed no
  activity until the entire JSON response completed.
- TEST_DESIGN performed one or more LLM calls plus an embedding/reranking pass for
  every approved requirement.
- SCRIPT_GEN performed a separate LLM call for each applicable test framework and
  test case.
- BRD performed ten sequential prose-generation calls across BRD, FSD, and Solution
  Documentation.
- UI pages polled runs every three seconds even while the pipeline was idle.

Historic production metering showed individual 14B test-design calls taking 30–217
seconds. At project scale, per-item calls made the downstream pipeline an hours-long
workflow even before script generation.

## Optimized mode

`TRACEFORGE_PERFORMANCE_MODE=fast` is the production default.

- Source understanding remains AI-driven, streamed, citation-validated, and
  resumable from the last committed chunk.
- Extraction output is constrained to concise requirements and a 4,500-token cap.
- Streaming response chunks are persisted as live progress.
- Test Plan, positive/negative baseline cases, document connective text, and test
  framework scaffolding are generated deterministically from approved requirements.
- Review gates remain unchanged; deterministic outputs are DRAFT until approved.
- Script locators remain explicit `TODO_LOCATOR` gaps when no DOM/HAR is available.
- Database N+1 queries and per-item commits were replaced with bulk loading and
  bounded commits.
- Idle UI polling backs off to 30 seconds.
- Runs have a first-class Stop action backed by ARQ cancellation.

The regression benchmark generates a five-requirement Test Plan, ten test cases,
twenty Playwright/Selenium scripts, and a BRD in under five seconds per stage on the
production database, with no LLM call in those repetitive stages.

Set `TRACEFORGE_PERFORMANCE_MODE=quality` to restore LLM-authored per-item test cases,
scripts, and document prose when turnaround time is secondary to generative detail.
