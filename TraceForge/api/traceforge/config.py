# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Central configuration for TraceForge. All settings are environment-driven with safe local defaults.
# Date: 2025-12-13
# ---------------------------------------------------------------------------
"""Central configuration for TraceForge. All settings are environment-driven with safe local defaults."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent  # .../TraceForge/api
MODULE_ROOT = BASE_DIR.parent  # .../TraceForge

load_dotenv(dotenv_path=BASE_DIR / ".env")


# Function: _bool
def _bool(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes"}


# ── Auth (shared Strat-Aqorynth token format — see auth.py) ───────────
AUTH_TOKEN_SECRET = os.getenv("AUTH_TOKEN_SECRET") or os.getenv("JWT_SECRET") or "change_me_jwt_secret_in_production"
AUTH_REQUIRED = _bool("AUTH_REQUIRED", "true")
ALLOW_LOCAL_AUTH_BYPASS = _bool("ALLOW_LOCAL_AUTH_BYPASS", "false")
TRACEFORGE_APP = "TRACEFORGE"

# ── CORS ────────────────────────────────────────────────────────
CORS_ORIGINS = [
    "http://localhost", "http://127.0.0.1",
    "http://localhost:8090", "http://127.0.0.1:8090",
    "http://localhost:5186", "http://127.0.0.1:5186",
    *[o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()],
]

# ── Database (local Postgres 16 + pgvector) ─────────────────────
# No hardcoded password fallback — required, fails startup loudly if unset.
# TRACEFORGE_DATABASE_URL allows credential rotation without mutating shared
# DATABASE_URL values used by other local tools.
DATABASE_URL = os.getenv("TRACEFORGE_DATABASE_URL") or os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Add it to api/.env before starting the service, "
        "e.g. postgresql+asyncpg://tf_admin:<password>@localhost:5432/traceforge"
    )

# ── Redis / Arq job queue (Memurai, Windows-native Redis-compatible) ─
# localhost resolves to ::1 first on this box and Memurai isn't listening on IPv6 —
# use the literal IPv4 address to avoid a multi-second connect timeout.
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/3")

# ── LLM (Ollama only — no Anthropic/Azure OpenAI in this deployment) ─
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
# qwen2.5-coder:14b (~10GB) does not fit this box's 8GB vGPU (NVIDIA A10-8Q) and always
# partially CPU-offloads (~48/52 CPU/GPU split observed) — qwen3.5:9b (~6.6GB)
# runs fully in VRAM, meaningfully faster for the extractor/BRD-author agent loop.
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
OLLAMA_EMBED_DIM = int(os.getenv("OLLAMA_EMBED_DIM", "768"))  # nomic-embed-text output size
OLLAMA_EMBED_BATCH_SIZE = int(os.getenv("OLLAMA_EMBED_BATCH_SIZE", "16"))
OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "300"))
# num_ctx covers prompt + completion together. Sized above the worst case for extraction:
# a 4-chunk batch (~2.4k tokens) + EXTRACT_RAG_TOP_K RAG-augmented chunks (~1.8k) + system
# prompt (~0.8k) + EXTRACT_MAX_TOKENS(6000) output could reach ~11k once RAG retrieval was
# added to the extractor — 8192 silently truncated that combination.
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "12288"))

# ── Agent behaviour (spec §5 "Universal rules for all agents") ──
AGENT_TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.2"))
# Measured empirically against a real dense BRD/contract doc: an 8-chunk batch wanted
# 10,000+ output tokens (hit the cap, truncated mid-JSON, batch silently produced zero
# requirements) — this source material is denser than the original 20-chunk/8000-token
# assumption planned for. A 4-chunk batch completed cleanly at ~5,500 tokens with 6000
# as the cap (24 valid requirements, no truncation) — sized with headroom above that.
AGENT_MAX_TOKENS = int(os.getenv("AGENT_MAX_TOKENS", "7000"))
AGENT_BATCH_SIZE_CHUNKS = int(os.getenv("AGENT_BATCH_SIZE_CHUNKS", "4"))
# Token-aware cap for extractor batches. Large documents often contain dense chunks,
# so the extractor now splits by both chunk count and an approximate input-token budget
# to keep malformed-tail failures from recurring on oversized prompts.
EXTRACT_BATCH_TARGET_TOKENS = int(os.getenv("EXTRACT_BATCH_TARGET_TOKENS", "1600"))
AGENT_WORKER_CONCURRENCY = int(os.getenv("AGENT_WORKER_CONCURRENCY", "1"))
AGENT_JOB_TIMEOUT_SECONDS = int(os.getenv("AGENT_JOB_TIMEOUT_SECONDS", "14400"))
AMBIGUITY_THRESHOLD_DEFAULT = float(os.getenv("AMBIGUITY_THRESHOLD_DEFAULT", "0.4"))
# §5 Agent 1 conflict-detection pass: caps total cross-document candidate pairs
# judged by the LLM per Extract run, so a large project (hundreds of requirements)
# can't turn one Extract run into thousands of serialized LLM calls.
CONFLICT_DETECTION_MAX_PAIRS = int(os.getenv("CONFLICT_DETECTION_MAX_PAIRS", "200"))
# §6.3: 'All prompts and completions optionally persisted (config flag PERSIST_LLM_IO)
# for audit; redact PII before persisting.' Off by default — persisting full prompt/
# completion text is an audit feature a deployment opts into, not a default behaviour.
PERSIST_LLM_IO = _bool("PERSIST_LLM_IO", "false")
# Fast mode keeps the expensive LLM focused on source understanding and document
# synthesis. Repetitive per-requirement test scaffolding and per-framework script
# boilerplate are generated deterministically from approved traceability data.
PERFORMANCE_MODE = os.getenv("TRACEFORGE_PERFORMANCE_MODE", "fast").strip().lower()
FAST_PIPELINE = PERFORMANCE_MODE in {"fast", "optimized", "performance"}
# 6000 still truncated 2/5 batches mid-JSON in a live run (dense RAG-augmented batches
# legitimately want more) — OLLAMA_NUM_CTX(12288) now has headroom above it, so raised.
EXTRACT_MAX_TOKENS = int(os.getenv("EXTRACT_MAX_TOKENS", "7500"))
# 6 was sized without accounting for the 8GB shared GPU also needing to keep the embed
# model resident for hybrid_search's own embedding call every batch — halved to keep the
# combined prompt comfortably inside OLLAMA_NUM_CTX while still adding cross-document context.
EXTRACT_RAG_TOP_K = int(os.getenv("EXTRACT_RAG_TOP_K", "3"))
TEST_PLAN_MAX_TOKENS = int(os.getenv("TEST_PLAN_MAX_TOKENS", "1200"))
TEST_CASE_MAX_TOKENS = int(os.getenv("TEST_CASE_MAX_TOKENS", "6000"))
TEST_CASE_OUTLINE_MAX_TOKENS = int(os.getenv("TEST_CASE_OUTLINE_MAX_TOKENS", "1800"))
TEST_DESIGN_CONCURRENCY = max(1, int(os.getenv("TEST_DESIGN_CONCURRENCY", "2")))
DOC_BUNDLE_MAX_TOKENS = int(os.getenv("DOC_BUNDLE_MAX_TOKENS", "3200"))
SCRIPT_MAX_TOKENS = int(os.getenv("SCRIPT_MAX_TOKENS", "2500"))
SCRIPT_PLAN_MAX_TOKENS = int(os.getenv("SCRIPT_PLAN_MAX_TOKENS", "1000"))

# ── Storage (local disk — no Azure Blob Storage in this deployment) ─
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", str(MODULE_ROOT / "data" / "blobs")))
SANDBOX_DIR = Path(os.getenv("SANDBOX_DIR", str(MODULE_ROOT / "data" / "sandbox")))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

# ── Chunking ──────────────────────────────────────────────────
CHUNK_TARGET_TOKENS = int(os.getenv("CHUNK_TARGET_TOKENS", "600"))
CHUNK_OVERLAP_TOKENS = int(os.getenv("CHUNK_OVERLAP_TOKENS", "80"))
