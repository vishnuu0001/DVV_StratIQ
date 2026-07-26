# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Central configuration for the Novastra-ITSM Support Agent.
# Date: 2026-01-20
# ---------------------------------------------------------------------------
"""
Central configuration for the Novastra-ITSM Support Agent.
All settings are driven from environment variables with safe defaults.
"""
import os
from pathlib import Path
from urllib.parse import unquote
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(dotenv_path=BASE_DIR / ".env")


# Function: _require_env
def _require_env(name: str) -> str:
    """Read a required secret from the environment. No hardcoded fallback —
    a missing value fails startup loudly instead of silently running with a
    weak, source-controlled default."""
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"{name} is not set. Add it to backend/.env before starting the service "
            "(see CLAUDE.md 'Shared Secrets' — this value must match every other "
            "Strat-Aqorynth backend, and the watchdog already injects it in production)."
        )
    return value

# ── LLM Settings ─────────────────────────────────────────────
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")          # "ollama" | "openai"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")  # GPU-capable; run: ollama pull qwen3.5:9b
OLLAMA_ANALYSIS_MODEL = os.getenv("OLLAMA_ANALYSIS_MODEL", OLLAMA_MODEL)
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
OLLAMA_NUM_GPU = int(os.getenv("OLLAMA_NUM_GPU", "-1"))
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "6144"))
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "1024"))
OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))
OLLAMA_KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "15m")
OLLAMA_REQUIRE_GPU = os.getenv("OLLAMA_REQUIRE_GPU", "true").lower() in {"1", "true", "yes"}
OLLAMA_ANALYSIS_NUM_PREDICT = int(os.getenv("OLLAMA_ANALYSIS_NUM_PREDICT", "768"))
OLLAMA_ANALYSIS_NUM_CTX = int(os.getenv("OLLAMA_ANALYSIS_NUM_CTX", "3072"))
OLLAMA_ANALYSIS_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_ANALYSIS_TIMEOUT_SECONDS", "90"))
OLLAMA_EMBED_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_EMBED_TIMEOUT_SECONDS", "12"))
OLLAMA_EMBED_BATCH_SIZE = int(os.getenv("OLLAMA_EMBED_BATCH_SIZE", "150"))  # max texts per embed_documents() call
OLLAMA_SIGNAL_EXTRACTION_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_SIGNAL_EXTRACTION_TIMEOUT_SECONDS", "4"))
QUERY_JOB_TIMEOUT_SECONDS = int(os.getenv("QUERY_JOB_TIMEOUT_SECONDS", "90"))
FEATURE_JOB_TIMEOUT_SECONDS = int(os.getenv("FEATURE_JOB_TIMEOUT_SECONDS", "90"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ── Auth / JWT ──────────────────────────────────────────────
JWT_SECRET = _require_env("JWT_SECRET")
# Portal SSO tokens are issued by AppRationalization and may use a different
# secret from Novastra's own sessions. AUTH_TOKEN_SECRET is retained as a
# compatibility alias for existing deployments.
PORTAL_AUTH_TOKEN_SECRET = (
    os.getenv("PORTAL_AUTH_TOKEN_SECRET")
    or os.getenv("AUTH_TOKEN_SECRET")
    or JWT_SECRET
)
JWT_EXPIRE_SECONDS = int(os.getenv("JWT_EXPIRE_SECONDS", "86400"))  # 24 hours
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8086")

# ── OAuth Providers (optional) ────────────────────────────────
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

# ── RAG / Vector Store (PostgreSQL + pgvector + LanceDB) ──────────────
VECTOR_COLLECTION = os.getenv("VECTOR_COLLECTION", "kg_support")
VECTOR_TABLE = os.getenv("VECTOR_TABLE", "vector_chunks")
VECTOR_BACKEND = os.getenv("VECTOR_BACKEND", "lancedb").strip().lower()  # postgres | qdrant | lancedb | hybrid
MODERN_PIPELINE_ENABLED = os.getenv("MODERN_PIPELINE_ENABLED", "true").lower() in {"1", "true", "yes"}
MODERN_PIPELINE_STRICT = os.getenv("MODERN_PIPELINE_STRICT", "false").lower() in {"1", "true", "yes"}
SYNC_REQUIRE_DUAL_WRITE = os.getenv("SYNC_REQUIRE_DUAL_WRITE", "true").lower() in {"1", "true", "yes"}

# ── Qdrant Configuration (Legacy - kept for backward compatibility) ──────
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "novastra_itsm_incidents")
QDRANT_TIMEOUT_SECONDS = int(os.getenv("QDRANT_TIMEOUT_SECONDS", "15"))
QDRANT_PREFER_GRPC = os.getenv("QDRANT_PREFER_GRPC", "false").lower() in {"1", "true", "yes"}
QDRANT_RECREATE_COLLECTION = os.getenv("QDRANT_RECREATE_COLLECTION", "false").lower() in {"1", "true", "yes"}

# ── LanceDB Configuration (Local GPU-accelerated vector store) ──────────
LANCEDB_PATH = os.getenv("LANCEDB_PATH", str(BASE_DIR / "vectorstore" / "lancedb"))
LANCEDB_TABLE = os.getenv("LANCEDB_TABLE", "incidents_vectors")
LANCEDB_METRIC = os.getenv("LANCEDB_METRIC", "cosine")  # cosine, euclidean, dot

# ── GPU/Embedding Configuration ────────────────────────────────────────
GPU_ENABLED = os.getenv("GPU_ENABLED", "true").lower() in {"1", "true", "yes"}
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")  # local GPU model
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cuda")  # cuda, cpu
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
# Larger chunks keep incident description + solution in the same chunk where possible.
# High overlap ensures solution text is never lost at a chunk boundary.
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "400"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "20"))    # wider recall net before reranking
# MIN_RELEVANCE_SCORE is intentionally low so the cross-encoder reranker (not cosine
# similarity) acts as the quality gate.  Cosine sim varies with embedding model and
# query phrasing; blocking at 0.45 discards many genuinely relevant chunks.
MIN_RELEVANCE_SCORE = float(os.getenv("MIN_RELEVANCE_SCORE", "0.20"))
STRICT_MIN_TOP_SCORE = float(os.getenv("STRICT_MIN_TOP_SCORE", "0.12"))
STRICT_MIN_AVG_SCORE = float(os.getenv("STRICT_MIN_AVG_SCORE", "0.06"))
RAG_MAX_QUERY_ANGLES = int(os.getenv("RAG_MAX_QUERY_ANGLES", "2"))
RAG_ENABLE_REGEX_LAYER = os.getenv("RAG_ENABLE_REGEX_LAYER", "true").lower() in {"1", "true", "yes"}
RAG_DIRECT_EXTRACTIVE_MODE = os.getenv("RAG_DIRECT_EXTRACTIVE_MODE", "true").lower() in {"1", "true", "yes"}
RAG_ENABLE_AUGMENT_LAYER = os.getenv("RAG_ENABLE_AUGMENT_LAYER", "false").lower() in {"1", "true", "yes"}
RAG_ENABLE_RERANK = os.getenv("RAG_ENABLE_RERANK", "true").lower() in {"1", "true", "yes"}

# ── Knowledge Data ────────────────────────────────────────────
DATA_DIR = os.getenv("DATA_DIR", str(BASE_DIR / "data"))

# ── ServiceNow ───────────────────────────────────────────────
# Function: _env_clean
def _env_clean(name: str, default: str = "") -> str:
	value = os.getenv(name, default)
	if value is None:
		return default
	# Handle copied values that include quotes or URL-encoded chars (for example %2B).
	cleaned = value.strip().strip('"').strip("'")
	return unquote(cleaned)


SERVICENOW_BASE_URL = _env_clean("SERVICENOW_BASE_URL", "").rstrip("/")
SERVICENOW_USERNAME = _env_clean("SERVICENOW_USERNAME", "")
SERVICENOW_PASSWORD = _env_clean("SERVICENOW_PASSWORD", "")
SERVICENOW_VERIFY_SSL = _env_clean("SERVICENOW_VERIFY_SSL", "true").lower() not in {"0", "false", "no"}
SERVICENOW_TIMEOUT_SECONDS = int(_env_clean("SERVICENOW_TIMEOUT_SECONDS", "20") or "20")

# ── Email intake (Omnichannel "Email" channel) ─────────────────
# IMAP mailbox polled for inbound support requests; each new message becomes a
# real Omnichannel ticket the same way a "Simulate Intake" click does. Disabled
# unless host/username/password are all set, same convention as ServiceNow above.
EMAIL_IMAP_ENABLED = _env_clean("EMAIL_IMAP_ENABLED", "true").lower() not in {"0", "false", "no"}
EMAIL_IMAP_HOST = _env_clean("EMAIL_IMAP_HOST", "imap.titan.email")
EMAIL_IMAP_PORT = int(_env_clean("EMAIL_IMAP_PORT", "993") or "993")
EMAIL_IMAP_USERNAME = _env_clean("EMAIL_IMAP_USERNAME", "")
EMAIL_IMAP_PASSWORD = _env_clean("EMAIL_IMAP_PASSWORD", "")
EMAIL_IMAP_FOLDER = _env_clean("EMAIL_IMAP_FOLDER", "INBOX")
EMAIL_IMAP_USE_SSL = _env_clean("EMAIL_IMAP_USE_SSL", "true").lower() not in {"0", "false", "no"}
EMAIL_IMAP_POLL_SECONDS = int(_env_clean("EMAIL_IMAP_POLL_SECONDS", "60") or "60")
# Sender filtering — this mailbox isn't a dedicated support address, so without a
# filter every receipt/newsletter/security-notice sitting unread in it becomes a
# ServiceNow incident too. Comma-separated addresses or "@domain" suffixes.
# ALLOWED (if non-empty): only these senders can create tickets, everything else
# is skipped. BLOCKED: senders skipped in addition to the allowlist check.
EMAIL_IMAP_ALLOWED_SENDERS = [s.strip().lower() for s in _env_clean("EMAIL_IMAP_ALLOWED_SENDERS", "").split(",") if s.strip()]
EMAIL_IMAP_BLOCKED_SENDERS = [s.strip().lower() for s in _env_clean("EMAIL_IMAP_BLOCKED_SENDERS", "").split(",") if s.strip()]
# Baseline heuristic filter for bulk/automated mail (no-reply, notifications,
# newsletters, ...) — active by default regardless of the lists above, since no
# one submits a real support request from a no-reply address. Set to false to
# capture every unread message verbatim (e.g. for a real dedicated support inbox).
EMAIL_IMAP_FILTER_AUTOMATED_SENDERS = _env_clean("EMAIL_IMAP_FILTER_AUTOMATED_SENDERS", "true").lower() not in {"0", "false", "no"}

# ── App ───────────────────────────────────────────────────────
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost,http://localhost:3000,http://localhost:5173,http://localhost:5177").split(",")
ADMIN_SECRET = _require_env("ADMIN_SECRET")
CHAT_HISTORY_RETENTION_DAYS = int(os.getenv("CHAT_HISTORY_RETENTION_DAYS", "5"))

# ── Storage / Postgres ──────────────────────────────────────
# Example DSN shape: postgresql://<user>:<password>@localhost:5432/postgres?connect_timeout=10&sslmode=prefer
DB_BACKEND = os.getenv("DB_BACKEND", "postgres").strip().lower()
# No hardcoded fallback DSN/password — required whenever DB_BACKEND is postgres.
POSTGRES_DSN = _require_env("POSTGRES_DSN") if DB_BACKEND in {"postgres", "postgresql"} else os.getenv("POSTGRES_DSN", "")
POSTGRES_POOL_MIN_SIZE = int(os.getenv("POSTGRES_POOL_MIN_SIZE", "2"))
POSTGRES_POOL_MAX_SIZE = int(os.getenv("POSTGRES_POOL_MAX_SIZE", "16"))
POSTGRES_POOL_TIMEOUT_SECONDS = float(os.getenv("POSTGRES_POOL_TIMEOUT_SECONDS", "10"))
