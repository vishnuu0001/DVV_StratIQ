# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Agent query API — handles support agent chat with RAG-grounded responses.
# Date: 2025-07-14
# ---------------------------------------------------------------------------
"""
Agent query API — handles support agent chat with RAG-grounded responses.
"""
import asyncio
import json
import logging
import random
import re
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from langchain_core.documents import Document

import backend.config as cfg
from backend.llm.router import get_llm
from backend.models.schemas import (
    QueryRequest,
    QueryResponse,
    SyntheticTicketRequest,
    SyntheticTicketResponse,
)
from backend.rag.document_loader import load_image_bytes
from backend.rag.pipeline import query_rag
from backend.rag.vectorstore import get_vectorstore, keyword_search, similarity_search

router = APIRouter(prefix="/api/agent", tags=["Agent"])
logger = logging.getLogger(__name__)

_QUERY_CACHE_TTL_SEC = 180
_QUERY_CACHE: dict[str, tuple[float, dict]] = {}
_QUERY_JOBS: dict[str, dict] = {}
_QUERY_JOB_TTL_SEC = 900
_QUERY_EXECUTOR = ThreadPoolExecutor(max_workers=4)


# Function: _compact_history
def _compact_history(history: list) -> str:
    compact: list[str] = []
    for item in (history or [])[-4:]:
        role = str(item.get("role", "")) if isinstance(item, dict) else ""
        content = str(item.get("content", "")) if isinstance(item, dict) else ""
        compact.append(f"{role}:{' '.join(content.split())[:180]}")
    return "||".join(compact)


# Function: _query_cache_key
def _query_cache_key(question: str, provider: str, history: list) -> str:
    q = " ".join((question or "").split())[:1500]
    h = _compact_history(history)
    return f"v3|{provider}|{q}|{h}"


# Function: _cache_get
def _cache_get(key: str) -> Optional[dict]:
    item = _QUERY_CACHE.get(key)
    if not item:
        return None
    expires_at, payload = item
    if expires_at < time.time():
        _QUERY_CACHE.pop(key, None)
        return None
    return payload


# Function: _cache_put
def _cache_put(key: str, payload: dict) -> None:
    _QUERY_CACHE[key] = (time.time() + _QUERY_CACHE_TTL_SEC, payload)


# Function: _cleanup_query_jobs
def _cleanup_query_jobs() -> None:
    now = time.time()
    stale = [jid for jid, meta in _QUERY_JOBS.items() if float(meta.get("expires_at", 0)) < now]
    for jid in stale:
        _QUERY_JOBS.pop(jid, None)


# Function: _fast_grounded_fallback
def _fast_grounded_fallback(question: str, provider: str) -> tuple[str, list, bool]:
    """Synchronous regex + keyword search fallback for when the full RAG pipeline times out.

    Runs within ~2 s and returns matched incident snippets from the vector DB
    so the user sees real evidence rather than a static error message.
    """
    fast_answer = ""
    fallback_sources: list[dict] = []
    fallback_context_used = False
    try:
        from backend.rag.vectorstore import keyword_search, regex_signal_search
        from backend.rag.pipeline import (
            _extract_ticket_signals_regex,
            _enrich_query_with_signals,
            _prepare_retrieval_query,
            _build_no_verified_resolution_answer,
            _build_sources,
            _extract_solution_text,
            _format_context,
            _get_top_solution,
            _rag_direct_answer,
            NO_CONTEXT_RESPONSE,
        )

        retrieval_query = _prepare_retrieval_query(question)
        signals = _extract_ticket_signals_regex(question)
        enriched = _enrich_query_with_signals(retrieval_query, signals)

        fast_chunks: list = []
        seen_texts: set[str] = set()
        for doc, score in keyword_search(enriched, provider, k=6):
            if doc.page_content not in seen_texts:
                fast_chunks.append((doc, score))
                seen_texts.add(doc.page_content)
        for doc, score in regex_signal_search(enriched, provider, k=6):
            if doc.page_content not in seen_texts:
                fast_chunks.append((doc, score))
                seen_texts.add(doc.page_content)

        if fast_chunks:
            fallback_sources = _build_sources(fast_chunks)
            fallback_context_used = True
            # Try direct regex solution extraction first (no LLM needed)
            top_solution = _get_top_solution(fast_chunks)
            if top_solution:
                fast_answer = top_solution
            else:
                # Build a grounded pattern-based answer from matched incidents
                fast_answer = _build_no_verified_resolution_answer(fast_chunks, question=question)
    except Exception as _fb_exc:
        logger.warning("Fast grounded fallback search failed: %s", _fb_exc)

    if not fast_answer:
        fast_answer = (
            "Request took too long to complete with full analysis. "
            "Returning fast grounded fallback from indexed incidents. "
            "Refine with one discriminator (error code, stack token, or transaction code) for a precise answer."
        )

    return fast_answer, fallback_sources, fallback_context_used


# Function: _handle_query_job_timeout
def _handle_query_job_timeout(rag_future, job_id: str, cache_key: str, question: str, provider: str, started_at: float) -> None:
    try:
        rag_future.cancel()
    except Exception:
        pass

    fast_answer, fallback_sources, fallback_context_used = _fast_grounded_fallback(question, provider)

    payload = {
        "answer": fast_answer,
        "sources": fallback_sources,
        "confidence": 0.38 if fallback_context_used else 0.20,
        "context_used": fallback_context_used,
        "mode": "chat",
        "session_id": str(uuid.uuid4()),
    }
    _QUERY_JOBS[job_id].update({"status": "done", "result": payload})
    _cache_put(cache_key, payload)
    logger.warning("query_job timeout job_id=%s provider=%s elapsed_ms=%.1f grounded=%s", job_id, provider, (time.perf_counter() - started_at) * 1000, fallback_context_used)


# Function: _run_query_job
async def _run_query_job(job_id: str, cache_key: str, question: str, provider: str, history: list) -> None:
    started_at = time.perf_counter()
    try:
        timeout_sec = min(120, max(30, int(getattr(cfg, "QUERY_JOB_TIMEOUT_SECONDS", 60) or 60)))
        rag_future = _QUERY_EXECUTOR.submit(
            query_rag,
            question=question,
            llm_provider=provider,
            chat_history=history,
        )
        result = await asyncio.wait_for(asyncio.wrap_future(rag_future), timeout=timeout_sec)
        payload = {
            "answer": result["answer"],
            "sources": result["sources"],
            "confidence": result["confidence"],
            "context_used": result["context_used"],
            "mode": "chat",
            "session_id": str(uuid.uuid4()),
        }
        _cache_put(cache_key, payload)
        _QUERY_JOBS[job_id].update({"status": "done", "result": payload})
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        logger.info(
            "query_job done job_id=%s provider=%s elapsed_ms=%.1f context_used=%s sources=%d confidence=%.4f",
            job_id,
            provider,
            elapsed_ms,
            bool(result.get("context_used", False)),
            len(result.get("sources", [])),
            float(result.get("confidence", 0.0)),
        )
    except asyncio.TimeoutError:
        _handle_query_job_timeout(rag_future, job_id, cache_key, question, provider, started_at)
    except Exception as exc:
        _QUERY_JOBS[job_id].update({"status": "error", "detail": str(exc)})
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        logger.exception("query_job failed job_id=%s provider=%s elapsed_ms=%.1f", job_id, provider, elapsed_ms)


# Function: _resolve_provider
def _resolve_provider(request_provider: Optional[str]) -> str:
    """Use request-level override if present, else fall back to global config."""
    if request_provider:
        return request_provider.value if hasattr(request_provider, "value") else request_provider
    return cfg.LLM_PROVIDER


# Function: _run_rag
async def _run_rag(question: str, provider: str, history: list) -> dict:
    """Run the blocking query_rag call in a thread so the event loop stays free."""
    loop = asyncio.get_running_loop()
    fn = partial(query_rag, question=question, llm_provider=provider, chat_history=history)
    return await loop.run_in_executor(None, fn)


_SIMULATION_SEED_QUERIES = [
    "database connection timeout and transaction failure in production",
    "vpn access denied after certificate change and user login failure",
    "sap interface job failure with jobkey reprocessed and cancelled state",
    "high CPU and memory alert causing application node failure",
    "service outage after recent deployment with hard error details",
    "api authentication token expired and users cannot access portal",
    "file transfer failure due to permission issue and IOException",
    "network latency spike causing timeout in transaction processing",
    "batch job failed and next run not started due to cancelled state",
    "exception stack trace and error code from incident work notes",
]

_GENERIC_TICKET_PHRASES = (
    "operational issue impacting normal",
    "normal ticket workflows",
    "normal workflow processes",
    "production-like enterprise environment",
    "recurring operational issue",
)

_NON_DIAGNOSTIC_PHRASES = (
    "attachment added",
    "related alert",
    "state is now closed",
    "ticket needs to be transferred",
    "the above issue being handled with this incident",
    "waiting for caller",
    "no further action required",
    "automatically closed",
    "no response from the caller",
    "task is created by system administrator",
    "alert rule",
    "incident can be resolved",
    "we are resolving this child incident",
    "resolving this child incident",
)

_SPECIFICITY_PATTERNS: list[tuple[re.Pattern[str], int]] = [
    (re.compile(r"\bINC\d{6,8}\b", re.IGNORECASE), 2),
    (re.compile(r"\bJobkey\s*\d{4,}/\d+\b", re.IGNORECASE), 5),
    (re.compile(r"\bRCS\s*['\"]?[A-Z0-9_#\-]{2,20}", re.IGNORECASE), 3),
    (re.compile(r"\b(?:ORA|SQL|HTTP|SAP)[-_ ]?\d{2,6}\b", re.IGNORECASE), 3),
    (re.compile(r"\b(?:Exception|IOException|NullPointerException|TimeoutException)\b", re.IGNORECASE), 4),
    (re.compile(r"\b(?:failed|error|denied|timeout|cancelled|canceled|reprocessed|next run)\b", re.IGNORECASE), 2),
    (re.compile(r"[A-Za-z]:\\[^\s]{8,}"), 3),
    (re.compile(r"\b[A-Z0-9_]{4,}\|ERROR_LABEL=", re.IGNORECASE), 4),
]

_TECH_TOKEN_RE = re.compile(
    r"(\bINC\d{6,8}\b"
    r"|\bJobkey\s*\d{4,}/\d+\b"
    r"|\bRCS\s*['\"]?[A-Z0-9_#\-]{2,20}['\"]?(?:\s+via\s+[A-Z0-9_#\-]{2,20})?\b"
    r"|[A-Za-z]:\\[^\s\"']+"
    r"|\b[A-Z_]{2,}=[^|\s]+"
    r"|\b[A-Z]{2,}\d{2,}\b"
    r"|\B/[A-Z0-9_./-]{3,}\b)"
)

_TEXT_TYPO_FIXES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bIO Erro\b", re.IGNORECASE), "IO Error"),
    (re.compile(r"\bsucessfully\b", re.IGNORECASE), "successfully"),
    (re.compile(r"\boccured\b", re.IGNORECASE), "occurred"),
    (re.compile(r"\brecieve\b", re.IGNORECASE), "receive"),
    (re.compile(r"\bseperate\b", re.IGNORECASE), "separate"),
]

_POLL_MAX_LEN = {
    "Incident Number": 16,
    "Short Description": 160,
    "Description": 520,
    "Priority": 8,
    "Category": 48,
    "Symptoms": 260,
    "Environment": 260,
    "Recent Change": 200,
    "Suggested Resolution": 320,
}

_POLL_ERR_CODE_RE = re.compile(r"\b(?:ORA-\d{3,6}|SQL\d{3,6}[A-Z]?|[A-Z]{2,6}\d{3,6}[A-Z]?|0x[0-9A-Fa-f]{6,})\b")
_POLL_STACK_TOKEN_RE = re.compile(r"\b(?:[A-Za-z_][A-Za-z0-9_]*Exception|[A-Za-z_][A-Za-z0-9_]*Error)\b")
_POLL_TX_API_RE = re.compile(r"\b(?:/N)?[A-Z]{2,5}\d{2,4}\b|\b(?:API|IF|SI|EAI)_[A-Za-z0-9_]{4,}\b", re.IGNORECASE)
_POLL_AFFECTED_SERVICE_RE = re.compile(r"\b(?:CI|Service|Component|Name|Package)\s*[:=]\s*([A-Za-z0-9_./-]{4,120})\b", re.IGNORECASE)
_POLL_TIMESTAMP_RE = re.compile(
    r"\b(?:\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(?::\d{2})?|\d{2}[./-]\d{2}[./-]\d{4}(?:\s+\d{2}:\d{2}(?::\d{2})?)?)\b"
)
_POLL_MSG_ID_RE = re.compile(r"(?i)\b(?:application\s+message\s+ids?|message\s+ids?)\s*:\s*([0-9]{8,20})")
_POLL_NAME_TOKEN_RE = re.compile(r"\b(?:EAI|API|IF|SI)_[A-Za-z0-9_]{6,}\b", re.IGNORECASE)


# Function: _poll_timestamp_window
def _poll_timestamp_window(timestamps: list) -> str:
    if len(timestamps) >= 2:
        return f"{timestamps[0]} to {timestamps[1]}"
    if len(timestamps) == 1:
        return timestamps[0]
    return "Not explicit in indexed snippets"


# Function: _poll_match_or_fallback
def _poll_match_or_fallback(match, group, fallback_match, fallback_group: int = 0) -> str:
    if match:
        return match.group(group).strip()
    if fallback_match:
        return fallback_match.group(fallback_group).strip()
    return "N/A"


# Function: _poll_stack_token
def _poll_stack_token(stack, blob: str) -> str:
    if stack:
        return stack.group(0).strip()
    return "Error Text" if "error text" in blob.lower() else "N/A"


# Function: _extract_poll_diagnostic_details
def _extract_poll_diagnostic_details(text: str) -> dict[str, str]:
    blob = " ".join((text or "").split())
    if not blob:
        return {
            "exact_error_code": "N/A",
            "failing_transaction_or_api": "N/A",
            "stack_trace_token": "N/A",
            "affected_ci_or_service": "N/A",
            "timestamp_window": "N/A",
        }

    err = _POLL_ERR_CODE_RE.search(blob)
    stack = _POLL_STACK_TOKEN_RE.search(blob)
    tx = _POLL_TX_API_RE.search(blob)
    svc = _POLL_AFFECTED_SERVICE_RE.search(blob)
    msgid = _POLL_MSG_ID_RE.search(blob)
    name_token = _POLL_NAME_TOKEN_RE.search(blob)
    timestamps = _POLL_TIMESTAMP_RE.findall(blob)

    return {
        "exact_error_code": _poll_match_or_fallback(err, 0, msgid, 1),
        "failing_transaction_or_api": _poll_match_or_fallback(tx, 0, name_token, 0),
        "stack_trace_token": _poll_stack_token(stack, blob),
        "affected_ci_or_service": _poll_match_or_fallback(svc, 1, name_token, 0),
        "timestamp_window": _poll_timestamp_window(timestamps),
    }


# Function: _inject_poll_diagnostic_details
def _inject_poll_diagnostic_details(text: str, details: dict[str, str]) -> str:
    sections = _extract_ticket_sections(text)
    if any(h not in sections for h in _POLL_FIELD_HEADERS):
        return text

    exact_error = _cap_text_clean(str(details.get("exact_error_code", "N/A") or "N/A"), 48)
    tx_api = _cap_text_clean(str(details.get("failing_transaction_or_api", "N/A") or "N/A"), 96)
    stack_token = _cap_text_clean(str(details.get("stack_trace_token", "N/A") or "N/A"), 48)
    affected = _cap_text_clean(str(details.get("affected_ci_or_service", "N/A") or "N/A"), 96)
    ts_window = _cap_text_clean(str(details.get("timestamp_window", "N/A") or "N/A"), 64)

    anchor_line = (
        "Diagnostic anchors: "
        f"exact error code={exact_error}; "
        f"failing transaction/API name={tx_api}; "
        f"stack trace token={stack_token}; "
        f"affected CI/service={affected}; "
        f"timestamp window={ts_window}."
    )

    base_desc = re.sub(r"(?i)(?:\bDescription\s*:\s*)+", "", sections["Description"]).strip()
    base_desc = _cap_text_clean(base_desc, 260)

    sections["Description"] = _cap_text_clean(
        f"{base_desc} {anchor_line}",
        _POLL_MAX_LEN["Description"],
    )

    return _render_ticket_text(
        incident_number=sections["Incident Number"],
        short_desc=sections["Short Description"],
        description=sections["Description"],
        priority=sections["Priority"],
        category=sections["Category"],
        symptoms=sections["Symptoms"],
        environment=sections["Environment"],
        recent_change=sections["Recent Change"],
        suggestion=sections["Suggested Resolution"],
    )


# Function: _llm_content_to_text
def _llm_content_to_text(content: object) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                txt = item.get("text")
                if isinstance(txt, str):
                    parts.append(txt)
        return "\n".join(p.strip() for p in parts if p and p.strip())
    return str(content).strip()


# Function: _normalize_text_preserving_identifiers
def _normalize_text_preserving_identifiers(text: str) -> str:
    compact = " ".join((text or "").split())
    if not compact:
        return ""

    placeholders: dict[str, str] = {}

    # Function: _protect
    def _protect(match: re.Match[str]) -> str:
        key = f"__TECH_{len(placeholders)}__"
        placeholders[key] = match.group(0)
        return key

    protected = _TECH_TOKEN_RE.sub(_protect, compact)
    normalized = protected
    for pattern, replacement in _TEXT_TYPO_FIXES:
        normalized = pattern.sub(replacement, normalized)
    normalized = re.sub(r"\s{2,}", " ", normalized).strip()

    for key, original in placeholders.items():
        normalized = normalized.replace(key, original)

    return normalized


# Function: _normalize_synthetic_ticket_fields
def _normalize_synthetic_ticket_fields(text: str) -> str:
    sections = _extract_ticket_sections(text)
    if any(header not in sections for header in _POLL_FIELD_HEADERS):
        return text

    normalized: dict[str, str] = {}
    for header in _POLL_FIELD_HEADERS:
        value = sections.get(header, "")
        if header in {"Short Description", "Description", "Symptoms", "Environment", "Recent Change", "Suggested Resolution"}:
            value = _normalize_text_preserving_identifiers(value)
        elif header == "Category":
            value = _normalize_text_preserving_identifiers(value).lower()
        elif header == "Priority":
            value = value.upper()
        elif header == "Incident Number":
            value = value.upper()

        value = " ".join(value.split()).strip()
        max_len = _POLL_MAX_LEN.get(header)
        if max_len:
            value = _cap_text_clean(value, max_len)
        normalized[header] = value

    return _render_ticket_text(
        incident_number=normalized["Incident Number"],
        short_desc=normalized["Short Description"],
        description=normalized["Description"],
        priority=normalized["Priority"],
        category=normalized["Category"],
        symptoms=normalized["Symptoms"],
        environment=normalized["Environment"],
        recent_change=normalized["Recent Change"],
        suggestion=normalized["Suggested Resolution"],
    )


# Function: _specificity_score
def _specificity_score(text: str) -> int:
    compact = " ".join((text or "").split())
    if not compact:
        return 0

    score = 0
    for pattern, weight in _SPECIFICITY_PATTERNS:
        score += len(pattern.findall(compact)) * weight

    lower = compact.lower()
    if any(p in lower for p in _GENERIC_TICKET_PHRASES):
        score -= 4

    return max(score, 0)


# Function: _is_generic_issue_text
def _is_generic_issue_text(text: str) -> bool:
    compact = " ".join((text or "").split()).lower()
    if not compact:
        return True
    has_marker = _specificity_score(compact) >= 4
    mostly_generic = sum(1 for p in _GENERIC_TICKET_PHRASES if p in compact) >= 1
    non_diagnostic = any(p in compact for p in _NON_DIAGNOSTIC_PHRASES)
    return non_diagnostic or (mostly_generic and not has_marker)


# Function: _clean_issue_phrase
def _clean_issue_phrase(text: str, max_len: int) -> str:
    compact = " ".join((text or "").split())
    if not compact:
        return ""

    compact = compact.replace("\\n", " ").replace("\\r", " ")

    compact = re.sub(r"\s+---\s+.*$", "", compact)
    compact = re.sub(
        r"(?i)\b(Incident Number|Short Description|Description|Priority|Category|Symptoms|Environment|Recent Change|Suggested Resolution)\s*:\s*",
        "",
        compact,
    )
    compact = re.sub(r"(?i)^\s*close notes?\s*:\s*", "", compact)
    compact = re.sub(r"(?i)^\s*attachment added\s*:\s*", "", compact)
    compact = re.sub(r"(?i)^\s*in case the ticket needs to be transferred\b[^.]*\.?", "", compact)
    compact = compact.strip(" .:-;")
    if not compact:
        return ""
    return _cap_text_clean(compact, max_len)


# Function: _best_issue_signature
def _best_issue_signature(text: str) -> str:
    compact = " ".join((text or "").split())
    if not compact:
        return ""

    candidates: list[tuple[int, str]] = []
    for segment in re.split(r"(?<=[.!?])\s+|\s+---\s+", compact):
        phrase = _clean_issue_phrase(segment, 160)
        if not phrase or len(phrase) < 20:
            continue
        low = phrase.lower()
        if any(bad in low for bad in ("subject:", "dear ", "http://", "https://", "[pattern", "source=", "type=", "relevance=")):
            continue
        if any(bad in low for bad in _NON_DIAGNOSTIC_PHRASES):
            continue
        score = _specificity_score(phrase)
        if score >= 4:
            candidates.append((score, phrase))

    if not candidates:
        return ""
    candidates.sort(key=lambda item: (item[0], len(item[1])), reverse=True)
    return candidates[0][1]


# Function: _fallback_issue_from_context
def _fallback_issue_from_context(text: str, max_len: int = 220) -> str:
    compact = " ".join((text or "").split())
    if not compact:
        return ""

    segments = re.split(r"(?<=[.!?])\s+|\s+---\s+", compact)
    soft_candidates: list[str] = []
    for segment in segments:
        phrase = _clean_issue_phrase(segment, max_len)
        if not phrase or len(phrase) < 18:
            continue
        low = phrase.lower()
        if any(bad in low for bad in ("subject:", "dear ", "http://", "https://", "[pattern", "source=", "type=", "relevance=")):
            continue
        if any(bad in low for bad in _NON_DIAGNOSTIC_PHRASES):
            continue
        if _specificity_score(phrase) >= 3:
            return phrase
        soft_candidates.append(phrase)

    return soft_candidates[0] if soft_candidates else ""


# Function: _pick_sentence
def _pick_sentence(text: str, keywords: list[str], fallback: str) -> str:
    lines = re.split(r"(?<=[.!?])\s+", " ".join(text.split()))
    candidates: list[tuple[int, str]] = []
    for line in lines:
        lline = line.lower()
        # Skip noisy fragments that frequently appear in raw ServiceNow chunks.
        if any(bad in lline for bad in ("[pattern", "source=", "type=", "relevance=", "subject:", "dear ", "http://", "https://", "incident number:", "short description:", "close notes:", "in case the ticket needs to be transferred")):
            continue
        if any(k in lline for k in keywords) and len(line.strip()) >= 18:
            cleaned = line.strip()
            candidates.append((_specificity_score(cleaned), cleaned))
    if candidates:
        candidates.sort(key=lambda item: (item[0], len(item[1])), reverse=True)
        return _cap_text_clean(candidates[0][1], 220)
    return fallback


# Function: _cap_text_clean
def _cap_text_clean(text: str, max_len: int) -> str:
    compact = " ".join((text or "").split()).strip(" .")
    if not compact:
        return ""
    if len(compact) <= max_len:
        return compact

    boundary = compact.rfind(" ", 0, max_len + 1)
    if boundary < int(max_len * 0.6):
        boundary = max_len
    return compact[:boundary].rstrip(" .,:;-")


# Function: _merge_ticket_hint_parts
def _merge_ticket_hint_parts(job_match, state_match, rcs_match) -> str:
    parts = []
    if job_match:
        parts.append(job_match.group(1).strip())
    if state_match:
        parts.append(state_match.group(1).strip())
    if rcs_match:
        rcs_token = rcs_match.group(1).strip()
        if not any(rcs_token.lower() in part.lower() for part in parts):
            parts.append(rcs_token)
    return ". ".join(dict.fromkeys(part for part in parts if part))


# Function: _build_ticket_identifier_phrase
def _build_ticket_identifier_phrase(job_identifier_match, rcs_match) -> str:
    identifier_parts = []
    if job_identifier_match:
        identifier_parts.append(job_identifier_match.group(1).strip())
    if rcs_match:
        rcs_token = rcs_match.group(1).strip()
        if not any(rcs_token.lower() in part.lower() for part in identifier_parts):
            identifier_parts.append(rcs_token)
    return " ".join(identifier_parts).strip()


# Function: _extract_operational_ticket_hints
def _extract_operational_ticket_hints(text: str) -> dict[str, str]:
    compact = " ".join((text or "").split())
    if not compact:
        return {"short_desc": "", "symptoms": "", "description": ""}

    job_identifier_match = re.search(
        r"\b([A-Z0-9_/#-]{4,}\s*'[^'\n]{2,20}'\s*Jobkey\s*\d{4,}/\d+\b)",
        compact,
        flags=re.IGNORECASE,
    )
    rcs_match = re.search(
        r"\b(RCS\s*['\"]?[A-Z0-9_#\-]{2,20}['\"]?(?:\s+via\s+[A-Z0-9_#\-]{2,20})?)\b",
        compact,
        flags=re.IGNORECASE,
    )
    job_match = re.search(
        r"\b([A-Z0-9_/#-]{6,}\s*'[^'\n]{2,20}'\s*Jobkey\s*\d{4,}/\d+[^.\n]{0,120})",
        compact,
        flags=re.IGNORECASE,
    )
    state_match = re.search(
        r"\b([^.!?\n]{0,80}(?:cancelled state|canceled state|reprocessed|next run finished successfully|next run[^.!?\n]{0,60})[^.!?\n]{0,120})",
        compact,
        flags=re.IGNORECASE,
    )

    merged = _merge_ticket_hint_parts(job_match, state_match, rcs_match)
    if not merged:
        return {"short_desc": "", "symptoms": "", "description": ""}

    identifier_phrase = _build_ticket_identifier_phrase(job_identifier_match, rcs_match)
    state_phrase = state_match.group(1).strip() if state_match else ""
    if identifier_phrase and state_phrase:
        short_desc_seed = f"{identifier_phrase}; {state_phrase}"
    else:
        short_desc_seed = identifier_phrase or merged

    return {
        "short_desc": _cap_text_clean(short_desc_seed, 160),
        "symptoms": _cap_text_clean(merged, 260),
        "description": _cap_text_clean(merged, 420),
    }


# Function: _extract_priority
def _extract_priority(text: str) -> str:
    up = text.upper()
    for value in ("P1", "P2", "P3", "P4"):
        if value in up:
            return value
    if "CRITICAL" in up:
        return "P1"
    if "HIGH" in up:
        return "P2"
    if "MEDIUM" in up:
        return "P3"
    return "P3"


# Function: _extract_category
def _extract_category(text: str) -> str:
    category_map = {
        "database": ["sql", "oracle", "db", "database"],
        "network": ["latency", "packet", "network", "vpn", "dns"],
        "authentication": ["login", "auth", "token", "password", "access denied"],
        "application": ["app", "application", "service", "api", "portal"],
        "infrastructure": ["cpu", "memory", "disk", "server", "node", "vm"],
        "integration": ["interface", "etl", "job", "queue", "batch", "sync"],
    }
    lower = text.lower()
    for cat, keys in category_map.items():
        if any(k in lower for k in keys):
            return cat
    return "application"


# Function: _token_set
def _token_set(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]{4,}", text.lower())}


# Function: _grounding_ratio
def _grounding_ratio(candidate: str, context: str) -> float:
    cand = _token_set(candidate)
    if not cand:
        return 0.0
    ctx = _token_set(context)
    if not ctx:
        return 0.0
    return len(cand & ctx) / len(cand)


# ── Strip ServiceNow/HTML noise from chunk content ───────────────────────
_SN_CODE_BLOCK_RE  = re.compile(r'\[code\].*?\[/code\]', re.IGNORECASE | re.DOTALL)
_HTML_TAG_RE        = re.compile(r'<[^>]+>')
_SN_JSON_BLOB_RE    = re.compile(r'\[Source Row JSON\]\s*\{.*?\}(?=\s|$)', re.DOTALL)
_SN_JSON_LINE_RE    = re.compile(r'\[Source Row JSON\]\s*[^\n]*')
_SN_ORIG_INC_RE     = re.compile(r'\[Original Incident Number:[^\]]*\]')
_SN_PATTERN_LBL_RE  = re.compile(r'\[Pattern \d+[^\]]*\]')
_SN_WORKNOTE_TS_RE  = re.compile(r'\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2}\s*-\s*[^\n]+')
_POLL_FIELD_HEADERS = [
    "Incident Number",
    "Short Description",
    "Description",
    "Priority",
    "Category",
    "Symptoms",
    "Environment",
    "Recent Change",
    "Suggested Resolution",
]


# Function: _clean_chunk_for_ticket
def _clean_chunk_for_ticket(raw: str) -> str:
    """Remove ServiceNow markup/JSON blobs/HTML from chunk text used as ticket seed."""
    s = raw
    s = _SN_CODE_BLOCK_RE.sub('', s)         # [code]...[/code]
    s = _HTML_TAG_RE.sub('', s)              # <a href=...>, <u>, etc.
    s = _SN_JSON_BLOB_RE.sub('', s)          # [Source Row JSON] {...}
    s = _SN_JSON_LINE_RE.sub('', s)          # any remaining [Source Row JSON] line
    s = _SN_ORIG_INC_RE.sub('', s)           # [Original Incident Number: ...]
    s = _SN_PATTERN_LBL_RE.sub('', s)        # [Pattern N | ...]
    s = _SN_WORKNOTE_TS_RE.sub('', s)        # timestamp lines in work_notes
    # Collapse excess whitespace
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip()


# Function: _sanitize_polled_ticket_text
def _sanitize_polled_ticket_text(text: str) -> str:
    if not text:
        return ""

    cleaned = text.strip()
    cleaned = cleaned.replace("\\n", "\n").replace("\\r", "\n")
    cleaned = re.sub(
        r"^\s*here is a synthetic incident ticket that follows the provided draft and indexed pattern snippets:\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    # Strip any HTML/code tags the LLM may have copied from context.
    cleaned = _SN_CODE_BLOCK_RE.sub('', cleaned)
    cleaned = _HTML_TAG_RE.sub('', cleaned)

    # Keep only the structured block from the first required header onward.
    first_header = re.search(r"(?im)^\s*Incident Number:\s*", cleaned)
    if first_header:
        cleaned = cleaned[first_header.start():].strip()

    # Remove markdown fencing if model returns it.
    cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", cleaned)
    cleaned = re.sub(r"\s*```\s*$", "", cleaned)
    return cleaned.strip()


# Function: _remove_suggested_solution_section
def _remove_suggested_solution_section(text: str) -> str:
    """Remove Suggested Solution/Resolution section from synthetic ticket text."""
    if not text:
        return ""

    lines = str(text).splitlines()
    cleaned_lines: list[str] = []
    skipping = False

    for line in lines:
        trimmed = line.strip()
        is_header_like = bool(re.match(r"^\s*[A-Za-z][A-Za-z\s/()_-]*\s*:\s*", line))
        starts_suggestion = bool(re.match(r"^\s*Suggested\s*(Resolution|Solution)\s*:\s*", line, flags=re.IGNORECASE))

        if starts_suggestion:
            skipping = True
            continue

        if skipping:
            if not trimmed:
                continue
            if is_header_like:
                skipping = False
            else:
                continue

        cleaned_lines.append(line)

    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


# Function: _extract_ticket_sections
def _extract_ticket_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    for i, header in enumerate(_POLL_FIELD_HEADERS):
        next_headers = _POLL_FIELD_HEADERS[i + 1:]
        if next_headers:
            lookahead = "|".join(re.escape(h) for h in next_headers)
            pattern = rf"(?is){re.escape(header)}\s*:\s*(.+?)(?=\n(?:{lookahead})\s*:|$)"
        else:
            pattern = rf"(?is){re.escape(header)}\s*:\s*(.+)$"
        m = re.search(pattern, text)
        if m:
            sections[header] = " ".join(m.group(1).split()).strip()
    return sections


_SYNTHETIC_TICKET_FORBIDDEN = (
    "[pattern", "source=", "type=", "relevance=", "subject:", "dear ",
    "http://", "https://", "<a ", "</a>", "[code]", "[/code]",
)

_SYNTHETIC_TICKET_MAX_LEN = {
    "Incident Number": 16,
    "Short Description": 160,
    "Description": 520,
    "Priority": 8,
    "Category": 48,
    "Symptoms": 260,
    "Environment": 260,
    "Recent Change": 200,
    "Suggested Resolution": 320,
}


# Function: _is_section_value_valid
def _is_section_value_valid(header: str, value: str) -> bool:
    if not value:
        return False
    low = value.lower()
    if len(value) > _SYNTHETIC_TICKET_MAX_LEN[header]:
        return False
    if any(tok in low for tok in _SYNTHETIC_TICKET_FORBIDDEN):
        return False
    # Prevent field bleeding where one section contains another header.
    for other in _POLL_FIELD_HEADERS:
        if other != header and f"{other.lower()}:" in low:
            return False
    return True


# Function: _is_valid_synthetic_ticket
def _is_valid_synthetic_ticket(text: str) -> bool:
    sections = _extract_ticket_sections(text)
    if any(h not in sections for h in _POLL_FIELD_HEADERS):
        return False

    inc = sections["Incident Number"].upper()
    if not re.fullmatch(r"INC\d{7,8}", inc):
        return False
    if sections["Priority"].upper() not in {"P1", "P2", "P3", "P4"}:
        return False

    return all(_is_section_value_valid(header, value) for header, value in sections.items())


# Function: _render_ticket_text
def _render_ticket_text(incident_number: str, short_desc: str, description: str, priority: str, category: str, symptoms: str, environment: str, recent_change: str, suggestion: str) -> str:
    return (
        f"Incident Number: {incident_number}\n"
        f"Short Description: {short_desc}\n"
        f"Description: {description}\n"
        f"Priority: {priority}\n"
        f"Category: {category}\n"
        f"Symptoms: {symptoms}\n"
        f"Environment: {environment}\n"
        f"Recent Change: {recent_change}\n"
        f"Suggested Resolution: {suggestion}"
    )


# Function: _is_strong_seed_doc
def _is_strong_seed_doc(doc: Document) -> bool:
    content = _clean_chunk_for_ticket(doc.page_content or "")
    if not content:
        return False
    low = content.lower()
    if any(p in low for p in _NON_DIAGNOSTIC_PHRASES):
        return False
    return _specificity_score(content) >= 3


# Function: _search_seeds_for_match
def _search_seeds_for_match(search_fn, terms, provider: str) -> list[tuple[Document, float]]:
    """Try each seed term in turn, returning the first term's strong (or any) hits."""
    for term in terms:
        results = search_fn(term, provider=provider, k=12)
        strong = [(doc, score) for doc, score in results if _is_strong_seed_doc(doc)]
        if strong:
            return strong
        if results:
            return results
    return []


# Function: _sample_from_vectorstore
def _sample_from_vectorstore(provider: str) -> list[tuple[Document, float]]:
    """Last fallback: sample directly from the indexed collection if chunks exist."""
    vs = get_vectorstore(provider)
    try:
        if vs._collection.count() <= 0:
            return []
        raw = vs._collection.get(include=["documents", "metadatas"], limit=200)
    except Exception:
        return []

    docs = raw.get("documents", [])
    metas = raw.get("metadatas", [])
    if not docs:
        return []

    combined = list(zip(docs, metas))
    random.shuffle(combined)
    sampled: list[tuple[Document, float]] = []
    for content, meta in combined:
        if not content:
            continue
        sampled.append((Document(page_content=content, metadata=meta or {}), 0.55))
        if len(sampled) >= 12:
            break
    return sampled


# Function: _retrieve_poll_seed_matches
def _retrieve_poll_seed_matches(provider: str) -> list[tuple[Document, float]]:
    # 1) Try semantic retrieval across multiple seed intents.
    shuffled_seeds = list(_SIMULATION_SEED_QUERIES)
    random.shuffle(shuffled_seeds)
    matches = _search_seeds_for_match(similarity_search, shuffled_seeds, provider)
    if matches:
        return matches

    # 2) Fallback to keyword retrieval to tolerate embedding/query mismatch.
    keyword_terms = ("error", "failed", "exception", "timeout", "jobkey", "cancelled", "servicenow", "incident")
    matches = _search_seeds_for_match(keyword_search, keyword_terms, provider)
    if matches:
        return matches

    # 3) Last fallback: sample directly from indexed collection if chunks exist.
    return _sample_from_vectorstore(provider)


# Function: _rank_and_sample_seed_matches
def _rank_and_sample_seed_matches(matches: list[tuple[Document, float]]) -> list[tuple[Document, float]]:
    source_counts: dict[str, int] = {}
    for doc, _ in matches:
        source_name = doc.metadata.get("source", "")
        source_counts[source_name] = source_counts.get(source_name, 0) + 1

    ranked_matches: list[tuple[float, Document, float]] = []
    for doc, score in matches:
        raw_content = doc.page_content or ""
        clean = _clean_chunk_for_ticket(raw_content)
        snippet = " ".join(clean.split())[:700]
        if not snippet:
            continue
        source_name = doc.metadata.get("source", "")
        specificity = float(_specificity_score(snippet))
        source_bonus = float(source_counts.get(source_name, 0)) * 0.35
        relevance = float(score)
        total = relevance + source_bonus + (specificity / 25.0)
        ranked_matches.append((total, doc, score))

    if ranked_matches:
        ranked_matches.sort(key=lambda item: item[0], reverse=True)
        return [(doc, score) for _, doc, score in ranked_matches[:3]]
    return matches[:3]


# Function: _build_seed_context_and_sources
def _build_seed_context_and_sources(sampled: list[tuple[Document, float]]) -> tuple[str, list[dict]]:
    context_parts = []
    sources = []
    for idx, (doc, score) in enumerate(sampled, start=1):
        source_name = doc.metadata.get("source", "unknown")
        doc_type = doc.metadata.get("type", "unknown")
        raw_content = doc.page_content or ""
        clean = _clean_chunk_for_ticket(raw_content)
        snippet = " ".join(clean.split())[:650]
        if snippet:
            context_parts.append(snippet)
        sources.append({
            "source": source_name,
            "type": doc_type,
            "relevance": float(score),
        })
    return "\n\n---\n\n".join(context_parts), sources


# Function: _derive_synthetic_short_desc
def _derive_synthetic_short_desc(operational_hints: dict, issue_signature: str, symptoms: str, context_fallback: str, required_details: dict) -> str:
    short_desc = _clean_issue_phrase(operational_hints["short_desc"], 160) or _clean_issue_phrase(issue_signature, 160) or _clean_issue_phrase(symptoms, 160) or _clean_issue_phrase(context_fallback, 160)
    if _is_generic_issue_text(short_desc):
        short_desc = _clean_issue_phrase(issue_signature, 160) or _clean_issue_phrase(context_fallback, 160) or _clean_issue_phrase(symptoms, 160)
    if _is_generic_issue_text(short_desc):
        tx_seed = required_details.get("failing_transaction_or_api", "N/A")
        err_seed = required_details.get("exact_error_code", "N/A")
        if tx_seed and tx_seed != "N/A":
            short_desc = _cap_text_clean(f"Failure in {tx_seed}", 160)
        elif err_seed and err_seed != "N/A":
            short_desc = _cap_text_clean(f"Processing failure with error {err_seed}", 160)
    if not short_desc:
        short_desc = "Synthetic incident generated from indexed support patterns"
    return short_desc


# Function: _synthetic_ticket_needs_fallback
def _synthetic_ticket_needs_fallback(content: str, context_blob: str, grounded_seed_ticket: str, short_desc: str, description: str, required_headers: list) -> bool:
    has_format = all(h in content for h in required_headers)
    grounding = _grounding_ratio(content, f"{context_blob}\n{grounded_seed_ticket}")
    generated_sections = _extract_ticket_sections(content)
    generated_short_desc = generated_sections.get("Short Description", "")
    generated_description = generated_sections.get("Description", "")
    generated_specificity = _specificity_score(f"{generated_short_desc}. {generated_description}")
    seed_specificity = _specificity_score(f"{short_desc}. {description}")
    is_generic_short = _is_generic_issue_text(generated_short_desc)
    is_generic = is_generic_short and _is_generic_issue_text(generated_description)

    return (
        not has_format
        or grounding < 0.58
        or not _is_valid_synthetic_ticket(content)
        or is_generic_short
        or is_generic
        or generated_specificity < max(4, int(seed_specificity * 0.55))
    )


# Function: _build_synthetic_ticket
def _build_synthetic_ticket(provider: str) -> dict:
    matches = _retrieve_poll_seed_matches(provider)
    if not matches:
        raise ValueError("No indexed data found. Run one-time sync or indexing before polling tickets.")

    sampled = _rank_and_sample_seed_matches(matches)
    context_blob, sources = _build_seed_context_and_sources(sampled)
    required_details = _extract_poll_diagnostic_details(context_blob)
    operational_hints = _extract_operational_ticket_hints(context_blob)
    issue_signature = _best_issue_signature(context_blob)
    context_fallback = _fallback_issue_from_context(context_blob, 220)
    symptoms = _pick_sentence(
        context_blob,
        ["error", "failed", "timeout", "denied", "unable", "unavailable", "exception", "cancelled", "canceled", "reprocessed", "next run", "jobkey"],
        context_fallback or "Synthetic issue extracted from indexed incident evidence.",
    )
    suggestion = _pick_sentence(
        context_blob,
        ["workaround", "resolved", "resolution", "fixed", "mitigation", "retry", "restart"],
        "Apply a validated workaround from similar indexed incidents and monitor stability.",
    )
    environment = _pick_sentence(
        context_blob,
        ["production", "prod", "uat", "staging", "server", "node", "cluster"],
        "Issue observed in a production-like enterprise environment.",
    )
    recent_change = _pick_sentence(
        context_blob,
        ["deploy", "release", "change", "patch", "upgrade", "migration"],
        "None reported",
    )
    priority = _extract_priority(context_blob)
    category = _extract_category(context_blob)
    incident_number = f"INC{random.randint(1000000, 9999999)}"

    short_desc = _derive_synthetic_short_desc(operational_hints, issue_signature, symptoms, context_fallback, required_details)
    symptoms = _clean_issue_phrase(operational_hints["symptoms"], 260) or _clean_issue_phrase(symptoms, 260)
    description = _clean_issue_phrase(operational_hints["description"], 420) or _clean_issue_phrase(f"{issue_signature}. {symptoms} {environment}", 420) or _clean_issue_phrase(f"{context_fallback}. {symptoms}", 420)
    if _is_generic_issue_text(description):
        description = _clean_issue_phrase(f"{issue_signature}. {symptoms}", 420)

    grounded_seed_ticket = _render_ticket_text(
        incident_number=incident_number,
        short_desc=short_desc,
        description=description,
        priority=priority,
        category=category,
        symptoms=symptoms,
        environment=environment,
        recent_change=recent_change,
        suggestion=suggestion,
    )
    grounded_seed_ticket = _inject_poll_diagnostic_details(grounded_seed_ticket, required_details)
    grounded_seed_ticket = _normalize_synthetic_ticket_fields(grounded_seed_ticket)

    prompt = (
        "You are generating a synthetic incident ticket for simulation.\n"
        "Strict grounding rules:\n"
        "1) Use ONLY facts and terminology present in the provided snippets and draft.\n"
        "2) Do NOT invent new product names, error codes, root causes, or environment details.\n"
        "3) Keep it synthetic but faithful to indexed patterns.\n"
        "4) Keep same output headings and plain text format.\n\n"
        "5) Ensure these are explicitly present in the ticket details: exact error code, failing transaction/API name, stack trace token, affected CI/service, and timestamp window.\n\n"
        "Output format (exact headings):\n"
        "Incident Number: INC########\n"
        "Short Description: <single line>\n"
        "Description: <2-4 sentences>\n"
        "Priority: <P1|P2|P3|P4>\n"
        "Category: <one concise category>\n"
        "Symptoms: <one sentence>\n"
        "Environment: <one sentence>\n"
        "Recent Change: <one sentence or 'None reported'>\n"
        "Suggested Resolution: <one sentence>\n\n"
        "Grounded draft (must remain semantically consistent):\n"
        f"{grounded_seed_ticket}\n\n"
        "Indexed snippets:\n"
        + context_blob
    )

    llm = get_llm(provider)
    response = llm.invoke(prompt)
    content = _llm_content_to_text(getattr(response, "content", response)).strip()
    content = _sanitize_polled_ticket_text(content)
    if not content:
        raise ValueError("Synthetic ticket generation returned an empty response.")

    required_headers = [
        "Incident Number:",
        "Short Description:",
        "Description:",
        "Priority:",
        "Category:",
        "Symptoms:",
        "Environment:",
        "Recent Change:",
        "Suggested Resolution:",
    ]
    if _synthetic_ticket_needs_fallback(content, context_blob, grounded_seed_ticket, short_desc, description, required_headers):
        # Hard fallback to extractive grounded draft to avoid hallucinations.
        content = grounded_seed_ticket

    content = _normalize_synthetic_ticket_fields(content)
    content = _inject_poll_diagnostic_details(content, required_details)
    content = _normalize_synthetic_ticket_fields(content)

    # Enforce consistent client-facing format across apps.
    # Validation still runs against the complete synthetic structure above.
    content = _remove_suggested_solution_section(content)

    return {
        "ticket_text": content,
        "sources": sources,
        "model_provider": provider,
    }


# Function: query_agent
@router.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """
    Primary RAG-powered Q&A endpoint for support agents.
    Returns a grounded answer with source citations and a confidence score.
    """
    provider = _resolve_provider(request.llm_provider)
    history = [{"role": m.role, "content": m.content} for m in (request.chat_history or [])]
    cache_key = _query_cache_key(request.question, provider, history)
    cached = _cache_get(cache_key)
    if cached is not None:
        return QueryResponse(**cached)

    try:
        result = await _run_rag(request.question, provider, history)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"LLM error: {exc}")

    logger.info(
        "mode=chat endpoint=/api/agent/query provider=%s context_used=%s sources=%d confidence=%.4f",
        provider,
        bool(result.get("context_used", False)),
        len(result.get("sources", [])),
        float(result.get("confidence", 0.0)),
    )

    payload = {
        "answer": result["answer"],
        "sources": result["sources"],
        "confidence": result["confidence"],
        "context_used": result["context_used"],
        "mode": "chat",
        "session_id": str(uuid.uuid4()),
    }
    _cache_put(cache_key, payload)

    return QueryResponse(
        **payload,
    )


# Function: query_agent_async
@router.post("/query-async")
async def query_agent_async(request: QueryRequest):
    """Submit chat prediction as an async job and return a job id immediately."""
    provider = _resolve_provider(request.llm_provider)
    history = [{"role": m.role, "content": m.content} for m in (request.chat_history or [])]
    cache_key = _query_cache_key(request.question, provider, history)
    cached = _cache_get(cache_key)
    if cached is not None:
        return {"status": "done", "job_id": None, "result": cached}

    _cleanup_query_jobs()
    job_id = str(uuid.uuid4())
    _QUERY_JOBS[job_id] = {
        "status": "pending",
        "result": None,
        "detail": None,
        "created_at": time.time(),
        "expires_at": time.time() + _QUERY_JOB_TTL_SEC,
    }
    asyncio.create_task(_run_query_job(job_id, cache_key, request.question, provider, history))
    return {"status": "pending", "job_id": job_id}


# Function: query_agent_job_status
@router.get("/query-job/{job_id}")
async def query_agent_job_status(job_id: str):
    """Poll async chat prediction job status."""
    _cleanup_query_jobs()
    job = _QUERY_JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Query job not found or expired")
    created_at = float(job.get("created_at", time.time()))
    elapsed = max(0.0, time.time() - created_at)
    retry_after_ms = 0
    if job.get("status", "pending") == "pending":
        if elapsed < 3:
            retry_after_ms = 220
        elif elapsed < 15:
            retry_after_ms = 400
        elif elapsed < 45:
            retry_after_ms = 700
        else:
            retry_after_ms = 1100

    return {
        "status": job.get("status", "pending"),
        "result": job.get("result"),
        "detail": job.get("detail"),
        "retry_after_ms": retry_after_ms,
    }


# Function: query_agent_with_attachment
@router.post("/query-with-attachment", response_model=QueryResponse)
async def query_agent_with_attachment(
    question: str = Form(...),
    llm_provider: Optional[str] = Form(None),
    chat_history: Optional[str] = Form("[]"),
    attachment: UploadFile = File(...),
):
    """
    RAG query that also accepts an attached screenshot or error-log file.
    OCR/text extraction is run on the attachment; the extracted content is
    prepended to the question so the LLM can use it as additional context.
    Supports: .png, .jpg, .jpeg (OCR via pytesseract) and .txt/.log/.csv (raw text).
    """
    provider = _resolve_provider(llm_provider)
    try:
        history = json.loads(chat_history or "[]")
    except Exception:
        history = []

    # ── Extract text from attachment ──────────────────────────
    content = await attachment.read()
    filename = attachment.filename or ""
    extracted_text = ""

    fname_lower = filename.lower()
    if fname_lower.endswith((".png", ".jpg", ".jpeg")):
        docs = await asyncio.to_thread(load_image_bytes, content, filename)
        if docs:
            extracted_text = "\n".join(d.page_content for d in docs)
    else:
        # Plain text / log / CSV — decode safely
        try:
            extracted_text = content.decode("utf-8", errors="replace")
        except Exception:
            extracted_text = ""

    # ── Build augmented question ──────────────────────────────
    if extracted_text.strip():
        augmented_question = (
            f"{question}\n\n"
            f"--- Attached file: {filename} ---\n"
            f"{extracted_text[:3000]}"   # cap to avoid blowing context window
        )
    else:
        augmented_question = question

    try:
        result = await _run_rag(augmented_question, provider, history)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"LLM error: {exc}")

    logger.info(
        "mode=chat endpoint=/api/agent/query-with-attachment provider=%s context_used=%s sources=%d confidence=%.4f",
        provider,
        bool(result.get("context_used", False)),
        len(result.get("sources", [])),
        float(result.get("confidence", 0.0)),
    )

    return QueryResponse(
        answer=result["answer"],
        sources=result["sources"],
        confidence=result["confidence"],
        context_used=result["context_used"],
        mode="chat",
        session_id=str(uuid.uuid4()),
    )


# Function: poll_synthetic_ticket
@router.post("/poll-ticket", response_model=SyntheticTicketResponse)
async def poll_synthetic_ticket(request: SyntheticTicketRequest):
    """
    Generate a synthetic incident ticket prompt using indexed data patterns.
    Defaults to Ollama to support local real-time simulation workflows.
    """
    provider = _resolve_provider(request.llm_provider)
    if provider != "ollama":
        provider = "ollama"

    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(None, partial(_build_synthetic_ticket, provider))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Synthetic ticket generation failed: {exc}")

    return SyntheticTicketResponse(**result)
