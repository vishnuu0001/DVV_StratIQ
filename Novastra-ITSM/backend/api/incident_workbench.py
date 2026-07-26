# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Incident workbench API.
# Date: 2025-08-08
# ---------------------------------------------------------------------------
"""
Incident workbench API.
Provides the feature tabs used by the modernized ticket analysis workspace.
"""
from __future__ import annotations

import asyncio
import math
import logging
import re
import time
import uuid
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from functools import lru_cache
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

import backend.config as cfg
from backend.api.auth import get_current_user
from backend.models.schemas import IncidentFeatureRequest, IncidentFeatureResponse, SimilarIncident, SourceDoc
from backend.llm.router import assert_ollama_gpu_available, get_llm
from backend.rag.vectorstore import keyword_search, regex_signal_search, similarity_search

router = APIRouter(prefix="/api/incident-workbench", tags=["Incident Workbench"])
logger = logging.getLogger(__name__)

_FEATURE_CACHE_TTL_SEC = 180
_FEATURE_CACHE: dict[str, tuple[float, dict]] = {}
_FEATURE_JOBS: dict[str, dict] = {}
_FEATURE_JOB_TTL_SEC = 900
_FEATURE_JOB_MAX_CONCURRENCY = max(2, min(8, (os.cpu_count() or 4)))
_FEATURE_JOB_SEMAPHORE = asyncio.Semaphore(_FEATURE_JOB_MAX_CONCURRENCY)
_FEATURE_EXECUTOR = ThreadPoolExecutor(max_workers=max(2, min(6, (os.cpu_count() or 4))))


# Function: _get_feature_llm
@lru_cache(maxsize=2)
def _get_feature_llm(provider: str):
    """Return a lower-latency LLM profile for analysis tabs."""
    if provider != "ollama":
        return get_llm(provider)

    from langchain_ollama import ChatOllama
    assert_ollama_gpu_available(cfg.OLLAMA_ANALYSIS_MODEL)

    return ChatOllama(
        model=cfg.OLLAMA_ANALYSIS_MODEL,
        base_url=cfg.OLLAMA_BASE_URL,
        temperature=0.0,
        num_predict=cfg.OLLAMA_ANALYSIS_NUM_PREDICT,
        num_gpu=cfg.OLLAMA_NUM_GPU,
        num_ctx=cfg.OLLAMA_ANALYSIS_NUM_CTX,
        repeat_penalty=1.12,
        top_k=12,
        top_p=0.9,
        timeout=cfg.OLLAMA_ANALYSIS_TIMEOUT_SECONDS,
        keep_alive=cfg.OLLAMA_KEEP_ALIVE,
    )

_FEATURE_PROMPTS = {
    "classify_incident": (
        "You are an ITSM classification analyst. Classify this incident using the retrieved knowledge base records.\n\n"
        "Return these sections:\n"
        "- Category / Subcategory: from category/subcategory fields of the most similar matched incidents. Note confidence if partial.\n"
        "- Severity Rationale: based on priority, impact, urgency from this incident and comparable retrieved tickets.\n"
        "- Recommended Assignment Group: from assignment_group of the most relevant matched incident.\n"
        "- Recommended Resolution Actions: resolution steps / close_notes from the top matched incidents relevant to this issue.\n\n"
        "RULES: Use ONLY data from CONTEXT. Always classify — mark 'Low confidence' if evidence is weak. "
        "Cite INC ticket IDs shown in [brackets] in CONTEXT (e.g. INC0073861). Never use [1], [2] style references."
    ),
    "anomaly_analysis": (
        "You are an IT anomaly detection analyst. Identify anomalies in this incident compared to retrieved knowledge base records.\n\n"
        "Return these sections:\n"
        "- Unusual Signals: fields or descriptions that deviate from patterns in retrieved similar incidents.\n"
        "- Missing or Inconsistent Data: empty, contradictory, or atypical fields compared to matched tickets.\n"
        "- Deviation Summary: why this incident deviates — cite INC ticket IDs from CONTEXT.\n"
        "- Recommended Next Checks: concrete actions based on retrieved resolution patterns.\n\n"
        "RULES: Only flag anomalies evident in CONTEXT. Cite INC IDs shown in [brackets] (e.g. INC0073861). "
        "If no anomalies found, state that clearly with supporting evidence."
    ),
    "event_correlation": (
        "You are an IT event correlation analyst. Identify correlations using retrieved knowledge base records.\n\n"
        "Return these sections:\n"
        "- Related Incidents: actual INC ticket IDs from [brackets] in CONTEXT (e.g. INC0073861, INC0010397).\n"
        "- Shared Indicators: specific fields / error codes / descriptions common across correlated incidents.\n"
        "- Correlation Confidence: High / Medium / Low — based on number of shared indicators.\n"
        "- Recommended Actions: concrete next steps based on how similar incidents were resolved.\n\n"
        "RULES: Only cite INC IDs shown in [brackets] in CONTEXT. Never fabricate incident IDs. "
        "If no correlated incidents found, state that explicitly."
    ),
    "incident_summarize": (
        "You are an L2 support engineer preparing a handoff summary. Use the incident details and retrieved context.\n\n"
        "Return these bullet points:\n"
        "- Problem: what was reported — use exact words from short_description and description.\n"
        "- Impact: stated impact / urgency from the incident fields.\n"
        "- Probable Cause: only if explicitly stated in the incident or retrieved matching tickets. Otherwise: 'Unknown — investigation required.'\n"
        "- Next Action: recommended step based on resolutions of matched historical incidents — cite INC IDs.\n"
        "- Escalation Criteria: conditions for escalation from retrieved context.\n\n"
        "RULES: Cite INC ticket IDs shown in [brackets] in CONTEXT (e.g. INC0073861). Do not invent causes or actions not in CONTEXT."
    ),
    "similar_incidents": (
        "You are a knowledge base analyst. List incidents similar to the one provided, using retrieved records.\n\n"
        "For each similar incident in CONTEXT return:\n"
        "- Incident Number: ACTUAL INC ID from [brackets] in CONTEXT (e.g. INC0073861)\n"
        "- Symptom Match: specific matching fields or descriptions.\n"
        "- Root Cause Pattern: from resolution/close_notes of the retrieved record — only if documented.\n"
        "- Prior Fix Applied: exact resolution steps from the retrieved record.\n\n"
        "RULES: Only use INC IDs from [brackets] in CONTEXT. Reproduce resolution steps exactly — do not paraphrase. "
        "List up to 5 similar incidents; note if fewer than 3 exist."
    ),
    "remediation_playbook": (
        "You are a senior support engineer generating a remediation playbook. "
        "Use ONLY resolution steps from retrieved knowledge base records.\n\n"
        "Return:\n"
        "1. Prerequisites: tools, access, conditions from retrieved records.\n"
        "2. Ordered Remediation Steps: exact steps from Resolution/Fix sections — cite INC IDs.\n"
        "3. Validation Checks: how to confirm the fix worked, from retrieved context.\n"
        "4. Rollback Plan: only if documented in retrieved incidents.\n"
        "5. Post-Fix Monitoring: follow-up actions from retrieved close_notes.\n\n"
        "RULES: Cite INC IDs from [brackets] in CONTEXT (e.g. INC0073861). Do not generate hypothetical steps. "
        "If no resolution found, respond: 'No verified remediation found in the knowledge base for this incident pattern.'"
    ),
    "script_generator": (
        "You are a DevOps automation engineer. Generate a script using ONLY resolution steps from retrieved knowledge base records.\n\n"
        "Return:\n"
        "- Script Language: PowerShell and/or Bash — based on what retrieved records reference.\n"
        "- Prerequisites: variables and environment requirements from retrieved resolution steps.\n"
        "- Script Body: each step as an executable command from retrieved remediation text.\n"
        "- Inline Comments: explain each command using language from the retrieved resolution.\n\n"
        "RULES: Only generate commands for actions in CONTEXT. "
        "Mark gaps with: # TODO: manual step required — not documented in knowledge base. "
        "If no scriptable steps found: 'No scriptable resolution found in the knowledge base for this incident pattern.'"
    ),
}

_DISALLOWED_GENERIC_PHRASES = (
    "i can't assist with this request",
    "i cannot assist with this request",
    "general information",
    "in general",
    "typically",
    "usually",
    "often",
)

_ERR_CODE_RE = re.compile(r"\b(?:ORA-\d{3,6}|SQL\d{3,6}[A-Z]?|[A-Z]{2,6}\d{3,6}[A-Z]?|0x[0-9A-Fa-f]{6,})\b")
_STACK_TOKEN_RE = re.compile(r"\b(?:[A-Za-z_][A-Za-z0-9_]*Exception|[A-Za-z_][A-Za-z0-9_]*Error)\b")
_TXN_CODE_RE = re.compile(r"\b(?:/N)?[A-Z]{2,5}\d{2,4}\b", re.IGNORECASE)
_JOBKEY_RE = re.compile(r"\bJobkey\s*\d{4,}/\d+\b", re.IGNORECASE)
_RCS_RE = re.compile(r"\bRCS\s*['\"]?[A-Z0-9_#\-]{2,32}['\"]?\b", re.IGNORECASE)
_IFACE_RE = re.compile(r"\b(?:SI|IF|API|EAI)_[A-Za-z0-9_]{4,}\b", re.IGNORECASE)
_CHANNEL_RE = re.compile(r"\b(?:JDBC|RFC|IDOC|SOAP|REST|HTTP|HTTPS)_[A-Z0-9_]{3,}\b", re.IGNORECASE)
_PATH_RE = re.compile(r"(?:[A-Za-z]:\\[^\s'\"]{6,260}|/(?:[A-Za-z0-9_.-]+/){1,8}[A-Za-z0-9_.-]{2,120})")
_GUID_RE = re.compile(r"\b(?:Message\s+GUID|Transaction\s+ID)\s*:\s*([A-Za-z0-9\-]{10,64})\b", re.IGNORECASE)
_METHOD_RE = re.compile(r"\b(?:at\s+)?[A-Za-z_][A-Za-z0-9_.$]{3,}\([^\)]{0,120}\)")
_SYMBOLIC_TOKEN_RE = re.compile(r"\b[A-Za-z0-9_./:\-#\\]{5,120}\b")
_DEEP_SIGNAL_PATTERNS = (
    (_ERR_CODE_RE, 100),
    (_STACK_TOKEN_RE, 95),
    (_TXN_CODE_RE, 90),
    (_JOBKEY_RE, 92),
    (_RCS_RE, 88),
    (_IFACE_RE, 90),
    (_CHANNEL_RE, 86),
    (_PATH_RE, 94),
    (_GUID_RE, 96),
    (_METHOD_RE, 89),
)
_FEATURE_STOPWORDS = {
    "incident", "number", "short", "description", "priority", "category", "additional", "context",
    "reported", "issue", "problem", "users", "user", "service", "system", "workflow", "ticket",
    "from", "with", "this", "that", "into", "using", "none", "n/a", "production",
}

_INCIDENT_ID_RE = re.compile(r"\bINC\d{4,}\b", re.IGNORECASE)
_SHORT_DESC_RE = re.compile(r"(?im)short\s*description\s*[:\-]\s*([^\n]{10,220})")
_DESC_RE = re.compile(r"(?im)description\s*[:\-]\s*([^\n]{10,220})")
_RESOLUTION_SNIPPET_RE = re.compile(
    r"(?is)(?:solution|resolution|fix|workaround|action\s+taken|corrective\s+action|close_notes)\s*[:\-\.]\s*(.+?)(?=\n\s*(?:issue|problem|root\s*cause|solution|resolution|fix|workaround|close_code|$)|\Z)"
)


# Function: _extract_classification_signals
def _tally_regex_matches(pattern: "re.Pattern", content: str, weight: float, tally: dict[str, float]) -> None:
    for m in pattern.findall(content):
        v = m.strip()
        if v and v.lower() not in ("", "n/a", "none", "null"):
            tally[v] += weight


# Function: _extract_classification_signals
def _extract_classification_signals(results: list) -> dict:
    """Extract category, subcategory, and assignment_group tallies from matched chunks."""
    categories: dict[str, float] = defaultdict(float)
    subcats: dict[str, float] = defaultdict(float)
    groups: dict[str, float] = defaultdict(float)
    _cat_re = re.compile(r"(?im)^category\s*[:\-]\s*([^\n]{2,60})")
    _sub_re = re.compile(r"(?im)^subcategory\s*[:\-]\s*([^\n]{2,60})")
    _grp_re = re.compile(r"(?im)^assignment\s*group\s*[:\-]\s*([^\n]{2,80})")
    for doc, score in results:
        content = doc.page_content or ""
        w = max(0.05, float(score))
        _tally_regex_matches(_cat_re, content, w, categories)
        _tally_regex_matches(_sub_re, content, w, subcats)
        _tally_regex_matches(_grp_re, content, w, groups)
    return {
        "category": max(categories, key=categories.__getitem__) if categories else None,
        "subcategory": max(subcats, key=subcats.__getitem__) if subcats else None,
        "assignment_group": max(groups, key=groups.__getitem__) if groups else None,
    }


# Function: _dedupe_results
def _dedupe_results(primary: list, secondary: list, limit: int = 10) -> list:
    merged = sorted((primary or []) + (secondary or []), key=lambda x: float(x[1]), reverse=True)
    deduped: list = []
    seen: set[str] = set()
    for doc, score in merged:
        key = f"{doc.metadata.get('source', 'unknown')}::{(doc.page_content or '')[:180]}"
        if key in seen:
            continue
        seen.add(key)
        deduped.append((doc, float(score)))
        if len(deduped) >= limit:
            break
    return deduped


# Function: _extract_incidents_from_text
def _extract_incidents_from_text(text: str, limit: int = 6) -> list[str]:
    found = [m.upper() for m in re.findall(r"\bINC\d+\b", text or "", flags=re.IGNORECASE)]
    uniq: list[str] = []
    seen: set[str] = set()
    for inc in found:
        if inc in seen:
            continue
        seen.add(inc)
        uniq.append(inc)
        if len(uniq) >= limit:
            break
    return uniq


# Function: _extract_candidate_incident_id
def _extract_candidate_incident_id(doc, content: str) -> str:
    candidate = str(doc.metadata.get("incident_number", "") or "").strip().upper()
    if candidate and _INCIDENT_ID_RE.fullmatch(candidate):
        return candidate

    ticket_id = str(doc.metadata.get("ticket_id", "") or "").strip().upper()
    if ticket_id and _INCIDENT_ID_RE.fullmatch(ticket_id):
        return ticket_id

    source = str(doc.metadata.get("source", "") or "")
    source_match = _INCIDENT_ID_RE.search(source)
    if source_match:
        return source_match.group(0).upper()

    text_match = _INCIDENT_ID_RE.search(content or "")
    if text_match:
        return text_match.group(0).upper()

    return ""


# Function: _extract_resolution_from_text
def _extract_resolution_from_text(content: str) -> str:
    match = _RESOLUTION_SNIPPET_RE.search(content or "")
    if not match:
        return ""
    return " ".join(str(match.group(1) or "").split()).strip()[:240]


# Function: _extract_root_cause_from_text
def _extract_root_cause_from_text(content: str) -> str:
    m = re.search(r"(?is)root\s*cause\s*[:\-\.]\s*(.+?)(?=\n\s*(?:solution|resolution|fix|workaround|action\s+taken|close_notes|$)|\Z)", content or "")
    if not m:
        return ""
    return " ".join(str(m.group(1) or "").split()).strip()[:220]


# Function: _expand_signal_variants
def _add_signal_token(token: str, out: list[str], seen: set[str]) -> None:
    t = str(token or "").strip()
    if not t:
        return
    key = t.lower()
    if key in seen:
        return
    seen.add(key)
    out.append(t)


# Function: _add_signal_parts
def _add_signal_parts(parts, out: list[str], seen: set[str]) -> None:
    for part in parts:
        p = str(part).strip()
        if len(p) >= 4 and p.lower() not in _FEATURE_STOPWORDS:
            _add_signal_token(p, out, seen)


# Function: _expand_signal_variants
def _expand_signal_variants(signals: list[str], limit: int = 24) -> list[str]:
    """Expand technical signals into searchable variants for deeper recall."""
    out: list[str] = []
    seen: set[str] = set()

    for sig in signals:
        s = str(sig or "").strip()
        if not s:
            continue
        _add_signal_token(s, out, seen)

        # Split composite tokens: EAI_BASF_BYC_MidPlatform2Cobalt_OrdersCreate_001
        _add_signal_parts(re.split(r"[_:/.\\\-]+", s), out, seen)

        # Split camel case chunks for broader nearest-neighbour retrieval.
        _add_signal_parts(re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|\d+", s), out, seen)

        if len(out) >= limit:
            break

    return out[:limit]


# Function: _run_deep_search_hunt
def _run_deep_search_hunt(incident_blob: str, provider: str, max_results: int = 32) -> list:
    """Execute expanded multi-query deep search for regex/keyword/vector evidence."""
    incident_ids = _extract_incidents_from_text(incident_blob, limit=4)
    deep_signals = _extract_deep_signals(incident_blob, limit=20)
    variants = _expand_signal_variants(deep_signals, limit=24)

    query_set: list[str] = []
    query_set.append(_build_enriched_feature_query(incident_blob))
    query_set.extend(incident_ids)
    query_set.extend(variants[:12])
    if variants:
        query_set.append(" ".join(variants[:4]))
    if len(variants) >= 8:
        query_set.append(" ".join(variants[4:8]))

    merged: list = []
    for query in query_set[:10]:
        q = str(query or "").strip()
        if not q:
            continue
        try:
            sem_k = 8 if len(q) < 12 else 12
            kw_k = 10
            rx_k = 14
            with ThreadPoolExecutor(max_workers=3) as pool:
                f_sem = pool.submit(similarity_search, q, provider, sem_k)
                f_kw = pool.submit(keyword_search, q, provider, kw_k)
                f_rx = pool.submit(regex_signal_search, q, provider, rx_k)
                sem = f_sem.result()
                kw = f_kw.result()
                rx = f_rx.result()
            merged = _dedupe_results(merged, _dedupe_results(_dedupe_results(sem, kw, limit=max_results), rx, limit=max_results), limit=max_results)
        except Exception as exc:
            logger.warning("Deep hunt query failed for '%s': %s", q[:80], exc)

    return _rank_results_by_evidence(merged, incident_blob, limit=max_results)


# Function: _score_result_evidence
def _score_result_evidence(doc, score, all_terms: set[str], query_incidents: set[str]):
    content = str(doc.page_content or "")
    if not content.strip():
        return None

    overlap = _overlap_score(content, all_terms)
    technical_hits = 0
    technical_hits += 1 if _ERR_CODE_RE.search(content) else 0
    technical_hits += 1 if _STACK_TOKEN_RE.search(content) else 0
    technical_hits += 1 if _TXN_CODE_RE.search(content) else 0
    technical_hits += 1 if _extract_resolution_from_text(content) else 0
    candidate_incident = _extract_candidate_incident_id(doc, content)
    has_incident_id = bool(candidate_incident)
    same_incident_bonus = 0.12 if candidate_incident and candidate_incident in query_incidents else 0.0

    technical_score = min(1.0, technical_hits / 3.0)
    id_bonus = 0.08 if has_incident_id else 0.0
    evidence = (max(0.0, float(score)) * 0.52) + (overlap * 0.34) + (technical_score * 0.14) + id_bonus + same_incident_bonus

    if evidence < 0.13 and float(score) < 0.19 and overlap < 0.06 and technical_hits == 0 and not has_incident_id:
        return None

    return evidence, (doc, float(score))


# Function: _rank_results_by_evidence
def _rank_results_by_evidence(results: list, incident_blob: str, limit: int = 10) -> list:
    if not results:
        return []

    query_terms = _query_terms(incident_blob)
    signal_terms = {
        token.lower()
        for token in _extract_deep_signals(incident_blob, limit=30)
        if isinstance(token, str) and token.strip()
    }
    all_terms = set(query_terms) | signal_terms

    query_incidents = set(_extract_incidents_from_text(incident_blob, limit=8))
    ranked: list[tuple[float, tuple]] = []
    for doc, score in results:
        scored = _score_result_evidence(doc, score, all_terms, query_incidents)
        if scored is not None:
            ranked.append(scored)

    ranked.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in ranked[:limit]]


# Function: _build_similar_incident_evidence_entry
def _build_similar_incident_evidence_entry(doc, content: str, query_incidents: set[str], seen: set[str]):
    inc = _extract_candidate_incident_id(doc, content)
    if not inc or inc in seen:
        return None
    if query_incidents and inc in query_incidents:
        # Skip the current ticket when looking for similar historical incidents.
        return None

    symptom = ""
    m_short = _SHORT_DESC_RE.search(content)
    m_desc = _DESC_RE.search(content)
    if m_short:
        symptom = " ".join((m_short.group(1) or "").split()).strip()[:180]
    elif m_desc:
        symptom = " ".join((m_desc.group(1) or "").split()).strip()[:180]
    if not symptom:
        symptom = " ".join(content.split())[:180]

    root_cause = _extract_root_cause_from_text(content) or "Not explicitly documented in retrieved history."
    prior_fix = _extract_resolution_from_text(content) or "Resolution text not explicitly documented for this match."

    entry_lines = [
        f"- Incident Number: {inc}",
        f"- Symptom Match: {symptom}",
        f"- Root Cause Pattern: {root_cause}",
        f"- Prior Fix Applied: {prior_fix}",
    ]
    return inc, entry_lines


# Function: _build_similar_incidents_evidence_lines
def _build_similar_incidents_evidence_lines(results: list, incident_blob: str, limit: int = 3) -> list[str]:
    query_incidents = set(_extract_incidents_from_text(incident_blob, limit=6))
    lines: list[str] = []
    added = 0
    seen: set[str] = set()

    for doc, _score in results:
        content = str(doc.page_content or "")
        if not content.strip():
            continue
        entry = _build_similar_incident_evidence_entry(doc, content, query_incidents, seen)
        if entry is None:
            continue
        inc, entry_lines = entry
        lines.extend(entry_lines)
        seen.add(inc)
        added += 1
        if added >= limit:
            break
        lines.append("")

    return lines


# Function: _query_terms
def _query_terms(text: str) -> set[str]:
    tokens = set(re.findall(r"[a-z0-9_\-]{4,}", (text or "").lower()))
    return {t for t in tokens if t not in _FEATURE_STOPWORDS and not t.startswith("inc")}


# Function: _extract_deep_signals
def _collect_symbolic_tokens(blob: str) -> list[tuple[str, int]]:
    # Include wider symbolic technical tokens (for stack fragments, adapter IDs, labels, etc.).
    found: list[tuple[str, int]] = []
    for token in _SYMBOLIC_TOKEN_RE.findall(blob):
        t = str(token).strip()
        if len(t) < 6:
            continue
        has_alpha = any(ch.isalpha() for ch in t)
        has_digit_or_symbol = any(ch.isdigit() for ch in t) or any(ch in "._:/-#\\" for ch in t)
        if has_alpha and has_digit_or_symbol:
            found.append((t, 60))
    return found


# Function: _dedupe_ranked_tokens
def _dedupe_ranked_tokens(ranked: list[tuple[str, int]], limit: int) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for token, _weight in ranked:
        key = token.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(token)
        if len(out) >= limit:
            break
    return out


# Function: _extract_deep_signals
def _extract_deep_signals(text: str, limit: int = 30) -> list[str]:
    """Extract high-value discriminator tokens from incident text, including wide/symbolic forms."""
    blob = " ".join((text or "").split())
    if not blob:
        return []

    candidates: list[tuple[str, int]] = []
    for pattern, weight in _DEEP_SIGNAL_PATTERNS:
        for token in pattern.findall(blob):
            candidates.append((str(token).strip(), weight))

    candidates.extend(_collect_symbolic_tokens(blob))

    ranked = sorted(candidates, key=lambda item: item[1], reverse=True)
    return _dedupe_ranked_tokens(ranked, limit)


# Function: _build_enriched_feature_query
def _build_enriched_feature_query(incident_blob: str) -> str:
    base = " ".join((incident_blob or "").split())
    signals = _extract_deep_signals(incident_blob, limit=24)
    if not signals:
        return base[:2200]
    enriched = " ".join([base, *signals])
    return enriched[:2600]


# Function: _overlap_score
def _overlap_score(text: str, terms: set[str]) -> float:
    if not text or not terms:
        return 0.0
    low = text.lower()
    hits = sum(1 for t in terms if t in low)
    return hits / max(1, len(terms))


# Function: _extract_pattern_signals
def _extract_pattern_signals(results: list, terms: set[str], limit: int = 2) -> list[str]:
    candidates: list[tuple[float, str]] = []
    seen: set[str] = set()
    for doc, score in results:
        content = doc.page_content or ""
        m = re.search(r"(?im)short\s*description\s*[:\-]\s*([^\n]{10,220})", content)
        if not m:
            m = re.search(r"(?im)description\s*[:\-]\s*([^\n]{10,220})", content)
        if not m:
            continue
        hint = " ".join(m.group(1).split()).strip()
        if not hint:
            continue
        key = hint.lower()
        if key in seen:
            continue
        seen.add(key)
        weight = (max(0.05, float(score)) * 0.75) + (_overlap_score(hint, terms) * 0.25)
        candidates.append((weight, hint))
    candidates.sort(key=lambda x: x[0], reverse=True)
    return [hint for _, hint in candidates[:limit]]


# Function: _extract_resolution_actions
def _extract_resolution_actions(results: list, terms: set[str], limit: int = 3) -> list[str]:
    rx = re.compile(
        r"(?is)(?:solution|resolution|fix|workaround|action\s+taken|corrective\s+action|close_notes)\s*[:\-\.]\s*(.+?)(?=\n\s*(?:issue|problem|root\s*cause|solution|resolution|fix|workaround|close_code|$)|\Z)"
    )
    candidates: list[tuple[float, str]] = []
    seen: set[str] = set()
    for doc, score in results:
        content = doc.page_content or ""
        matched = [m.group(1) for m in rx.finditer(content)]
        for raw in matched:
            action = " ".join(str(raw).split()).strip('"').strip()
            if len(action) < 12:
                continue
            key = action.lower()
            if key in seen:
                continue
            seen.add(key)
            weight = (max(0.05, float(score)) * 0.75) + (_overlap_score(action, terms) * 0.25)
            candidates.append((weight, action[:220]))
    candidates.sort(key=lambda x: x[0], reverse=True)
    return [action for _, action in candidates[:limit]]


# Function: _predict_discriminator
def _top_discriminator_token(results: list, pattern: "re.Pattern", max_len: int = 40) -> Optional[str]:
    weights: dict[str, float] = defaultdict(float)
    for doc, score in results:
        text = doc.page_content or ""
        for raw in pattern.findall(text):
            token = str(raw).strip().upper()
            if not token or len(token) > max_len or token.startswith("INC"):
                continue
            if token in {"P1", "P2", "P3", "P4", "N/A", "HTTP", "HTTPS", "ERROR"}:
                continue
            weights[token] += max(0.05, float(score))
    if not weights:
        return None
    return max(weights.items(), key=lambda x: x[1])[0]


# Function: _predict_discriminator
def _predict_discriminator(results: list) -> dict[str, str]:
    out: dict[str, str] = {}
    err = _top_discriminator_token(results, _ERR_CODE_RE)
    stk = _top_discriminator_token(results, _STACK_TOKEN_RE)
    txn = _top_discriminator_token(results, _TXN_CODE_RE)
    if err:
        out["error_code"] = err
    if stk:
        out["stack_token"] = stk
    if txn:
        out["transaction_code"] = txn
    return out


# Function: _predict_discriminator_from_text
def _predict_discriminator_from_text(text: str) -> dict[str, str]:
    out: dict[str, str] = {}

    err = _ERR_CODE_RE.search(text or "")
    if err:
        out["error_code"] = err.group(0).strip().upper()

    stk = _STACK_TOKEN_RE.search(text or "")
    if stk:
        out["stack_token"] = stk.group(0).strip()

    txn = _TXN_CODE_RE.search(text or "")
    if txn:
        token = txn.group(0).strip().upper()
        if token not in {"HTTP", "HTTPS", "ERROR", "INFO", "WARN"}:
            out["transaction_code"] = token

    return out


# Function: _format_feature_context
def _format_feature_context(results: list, max_chunks: int = 6, max_chars: int = 1000) -> str:
    blocks: list[str] = []
    for idx, (doc, score) in enumerate(results[:max_chunks], start=1):
        src = str(doc.metadata.get("source", "unknown"))
        # Extract incident ticket ID for better citation
        incident_id = str(doc.metadata.get("incident_number", "")).strip().upper()
        if not incident_id or incident_id == "UNKNOWN":
            # Fallback to ticket_id from Qdrant payload
            incident_id = str(doc.metadata.get("ticket_id", "")).strip().upper()
        
        # Use incident ticket ID as reference if available, otherwise use index
        ref_label = incident_id if incident_id and incident_id != "UNKNOWN" else f"{idx}"
        
        content = " ".join((doc.page_content or "").split())
        blocks.append(f"[{ref_label}] Source: {src} (relevance: {float(score):.4f})\\n{content[:max_chars]}")
    return "\n\n---\n\n".join(blocks)


# Function: _feature_cache_key
def _feature_cache_key(feature: str, incident_blob: str, provider: str) -> str:
    compact = " ".join((incident_blob or "").split())[:1500]
    return f"{provider}|{feature}|{compact}"


# Function: _cache_get
def _cache_get(key: str) -> Optional[dict]:
    entry = _FEATURE_CACHE.get(key)
    if not entry:
        return None
    expires_at, payload = entry
    if expires_at < time.time():
        _FEATURE_CACHE.pop(key, None)
        return None
    return payload


# Function: _cache_put
def _cache_put(key: str, payload: dict) -> None:
    _FEATURE_CACHE[key] = (time.time() + _FEATURE_CACHE_TTL_SEC, payload)


# Function: _cleanup_feature_jobs
def _cleanup_feature_jobs() -> None:
    now = time.time()
    stale = [jid for jid, meta in _FEATURE_JOBS.items() if float(meta.get("expires_at", 0)) < now]
    for jid in stale:
        _FEATURE_JOBS.pop(jid, None)


# Function: _extract_similar_incidents_from_results
def _extract_similar_incidents_from_results(results: list) -> list[SimilarIncident]:
    incidents: list[SimilarIncident] = []
    seen: set[str] = set()
    inc_re = re.compile(r"\bINC\d+\b", re.IGNORECASE)

    for doc, score in (results or []):
        content = str(doc.page_content or "")
        from_text = inc_re.findall(content)
        candidate = _extract_candidate_incident_id(doc, content) or (from_text[0].upper() if from_text else "")
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        summary = content.replace("\n", " ").strip()
        incidents.append(
            SimilarIncident(
                incident_number=candidate,
                summary=summary[:240],
                source=str(doc.metadata.get("source", "unknown")),
                relevance=float(score),
            )
        )
        if len(incidents) >= 5:
            break

    return incidents


# Function: _analyze_weak_evidence_with_llm
def _analyze_weak_evidence_with_llm(feature: str, context_text: str, incident_blob: str, results: list, provider: str) -> Optional[str]:
    """When VectorDB evidence is weak, invoke Ollama LLM to extract grounded predictions from weak matches."""
    if not incident_blob.strip():
        return None
    llm = _get_feature_llm(provider)
    feature_prompt = _FEATURE_PROMPTS.get(feature, '')
    grounded_context = context_text.strip() or "No high-confidence vector matches. Use incident text and extracted deep technical signals only."
    deep_signals = _extract_deep_signals(incident_blob, limit=24)
    deep_signal_text = ", ".join(deep_signals) if deep_signals else "None"
    weak_evidence_prompt = (
        f"{feature_prompt}\n\n"
        "WEAK EVIDENCE MODE:\n"
        "Evidence is limited, but analyze what exists and extract grounded feature-specific predictions.\n"
        "Rules:\n"
        "1. Cite ACTUAL INCIDENT TICKET IDs from CONTEXT (e.g., INC0073861).\n"
        "2. Extract concrete technical details: error codes, resolution patterns, category hints.\n"
        "3. Do NOT refuse or use generic phrases like 'cannot be determined'.\n"
        "4. Generate feature-specific output even if weak: classify incidents, find similar patterns, extract steps.\n"
        "5. Clearly mark uncertain claims as 'preliminary' or 'based on limited evidence'.\n"
        "6. Keep output under 7 bullet points, each under 28 words.\n"
        f"\nIncident details:\n{incident_blob}\n\n"
        f"Deep signals (regex extracted): {deep_signal_text}\n\n"
        f"CONTEXT (weak evidence):\n{grounded_context}"
    )
    try:
        response = llm.invoke([
            ("system", "You are a grounded IT analysis assistant. Extract whatever insights you can from weak evidence without refusing."),
            ("human", weak_evidence_prompt)
        ])
        answer = (response.content if hasattr(response, "content") else str(response)).strip()
        if answer and len(answer) > 20:
            return answer
    except Exception as exc:
        logger.warning("Weak evidence LLM analysis failed: %s", exc)
    return None


# Function: _fallback_similar_incidents
def _fallback_similar_incidents(results: list, incident_blob: str, similar_context: list, pred_parts: list[str]) -> str:
    evidence_lines = _build_similar_incidents_evidence_lines(results, incident_blob, limit=3)
    if evidence_lines:
        if pred_parts:
            evidence_lines.append("")
            evidence_lines.append(f"- Predicted Discriminator: {', '.join(pred_parts)}")
        return "\n".join(evidence_lines)
    if similar_context:
        lines = []
        for idx, item in enumerate(similar_context[:3], start=1):
            lines.append(f"- Incident Number: {item.incident_number}")
            lines.append(f"- Symptom Match: {item.summary[:180]}")
            lines.append("- Root Cause Pattern: Not explicitly documented in matched resolution text.")
            lines.append("- Prior Fix Applied: Refer to resolution notes from this matched incident in vector evidence.")
            if idx < min(3, len(similar_context)):
                lines.append("")
        if pred_parts:
            lines.append("")
            lines.append(f"- Predicted Discriminator: {', '.join(pred_parts)}")
        return "\n".join(lines)
    deep = _extract_deep_signals(incident_blob, limit=6)
    deep_text = " | ".join(deep) if deep else "No high-confidence discriminator extracted from incident text."
    return (
        "- Deep Search Result: No verified similar historical incident could be extracted from vector evidence after regex, keyword, and semantic passes.\n"
        f"- Deep Regex Signals Used: {deep_text}\n"
        "- Action: Re-sync KB and ensure historical close_notes/resolution fields are indexed for this integration pattern."
        + (f"\n- Predicted Discriminator: {', '.join(pred_parts)}" if pred_parts else "")
    )


# Function: _fallback_incident_summarize
def _fallback_incident_summarize(patterns: list[str], actions: list[str], rel: str, pattern_text: str, pred_parts: list[str]) -> str:
    top_pattern = patterns[0] if patterns else "Symptom not specific enough for deterministic historical alignment."
    next_action = actions[0] if actions else "Collect one discriminator and rerun retrieval against vector evidence."
    return (
        f"- Problem: {top_pattern}"
        f"\n- Impact: Potential recurrence risk inferred from related incidents.{rel}"
        f"\n- Probable Cause: Unknown — investigation required.{pattern_text}"
        f"\n- Next Action: {next_action}"
        "\n- Escalation Criteria: Escalate if issue repeats after applying validated historical recommendation."
        + (f"\n- Predicted Discriminator: {', '.join(pred_parts)}" if pred_parts else "")
    )


# Function: _fallback_classify_incident
def _fallback_classify_incident(results: list, actions: list[str], related: list[str]) -> str:
    cls = _extract_classification_signals(results)
    cat_line = f"- Category / Subcategory: {cls['category'] or 'Unknown'} / {cls['subcategory'] or 'Unknown'} (Low confidence — partial match)"
    grp_line = f"- Recommended Assignment Group: {cls['assignment_group'] or 'Unknown — not determinable from current matches'}"
    sev_line = "- Severity Rationale: Priority and impact could not be derived conclusively; treat as medium until confirmed."
    action_line = f"- Recommended Resolution Actions: {' | '.join(actions) if actions else 'No resolution steps recovered from matched incidents. Collect a discriminator (exact error code, stack trace, or transaction code) and re-run.'}"
    inc_line = f"- Evidence Incidents: {', '.join(related) if related else 'None directly matched'}"
    return f"{cat_line}\n{grp_line}\n{sev_line}\n{action_line}\n{inc_line}"


# Function: _fallback_anomaly_analysis
def _fallback_anomaly_analysis(patterns: list[str], actions: list[str], rel: str, pred_parts: list[str]) -> str:
    return (
        "- Unusual Signals: Verified exact anomaly signature is not fully established from matched incidents."
        f"\n- Missing or Inconsistent Data: A discriminator is required to separate close incident patterns.{rel}"
        f"\n- Deviation Summary: {patterns[0] if patterns else 'No dominant deviation marker extracted from retrieved context.'}"
        f"\n- Recommended Next Checks: {' | '.join(actions) if actions else 'Collect error code or stack token and compare against related incidents.'}"
        + (f"\n- Predicted Discriminator: {', '.join(pred_parts)}" if pred_parts else "")
    )


# Function: _fallback_event_correlation
def _fallback_event_correlation(patterns: list[str], actions: list[str], related: list[str], pred_parts: list[str]) -> str:
    corr_conf = "Low" if len(related) < 3 else "Medium"
    return (
        f"- Related Incidents: {', '.join(related) if related else 'Not enough direct matches'}"
        f"\n- Shared Indicators: {' | '.join(patterns) if patterns else 'No high-confidence shared indicator extracted.'}"
        f"\n- Correlation Confidence: {corr_conf}"
        f"\n- Recommended Correlation Actions: {' | '.join(actions) if actions else 'Collect discriminator and re-run correlation on narrowed subset.'}"
        + (f"\n- Predicted Discriminator: {', '.join(pred_parts)}" if pred_parts else "")
    )


# Function: _feature_fallback
def _feature_fallback(feature: str, context_text: str, incident_blob: str, results: list) -> str:
    similar_context = _extract_similar_incidents_from_results(results)
    related = [item.incident_number for item in similar_context[:5]]
    rel = f" Related incidents in context: {', '.join(related)}." if related else ""
    terms = _query_terms(incident_blob)
    patterns = _extract_pattern_signals(results, terms, limit=2)
    actions = _extract_resolution_actions(results, terms, limit=3)
    predicted = _predict_discriminator(results)
    if not predicted:
        predicted = _predict_discriminator_from_text(incident_blob)

    pattern_text = f" Pattern signals: {' | '.join(patterns)}." if patterns else ""
    action_text = f" Historical recommendations: {' | '.join(actions)}." if actions else ""
    pred_parts: list[str] = []
    if predicted.get("error_code"):
        pred_parts.append(f"error code={predicted['error_code']}")
    if predicted.get("stack_token"):
        pred_parts.append(f"stack token={predicted['stack_token']}")
    if predicted.get("transaction_code"):
        pred_parts.append(f"transaction code={predicted['transaction_code']}")
    pred_text = f" Predicted discriminator: {', '.join(pred_parts)}." if pred_parts else ""

    if feature == "similar_incidents":
        return _fallback_similar_incidents(results, incident_blob, similar_context, pred_parts)
    if feature == "incident_summarize":
        return _fallback_incident_summarize(patterns, actions, rel, pattern_text, pred_parts)
    if feature == "classify_incident":
        return _fallback_classify_incident(results, actions, related)
    if feature == "anomaly_analysis":
        return _fallback_anomaly_analysis(patterns, actions, rel, pred_parts)
    if feature == "event_correlation":
        return _fallback_event_correlation(patterns, actions, related, pred_parts)

    return (
        "Vector-grounded feature insight is limited by weak discriminator overlap."
        f"{rel}{pattern_text}{action_text}{pred_text} Provide one discriminator (exact error code, stack trace line, or transaction code) for a tighter match."
    )


# Function: _run_feature_grounded
def _retrieve_grounded_results(incident_blob: str, provider: str, feature: str) -> list:
    enriched_query = _build_enriched_feature_query(incident_blob)

    # Run semantic, keyword, and regex-signal retrieval in parallel for broad technical recall.
    # Use a wider recall window so each tab gets deep evidence before reranking.
    with ThreadPoolExecutor(max_workers=3) as pool:
        f_sem = pool.submit(similarity_search, enriched_query, provider, 18)
        f_kw = pool.submit(keyword_search, enriched_query, provider, 14)
        f_rx = pool.submit(regex_signal_search, enriched_query, provider, 20)
        sem = f_sem.result()
        kw = f_kw.result()
        rx = f_rx.result()

    # Dedupe with higher priority to regex results (which are technically grounded)
    results = _dedupe_results(_dedupe_results(sem, kw, limit=24), rx, limit=24)
    results = _rank_results_by_evidence(results, incident_blob, limit=12)

    # Second-pass deep regex-only search on extracted discriminators when first pass misses.
    if not results:
        deep_signals = _extract_deep_signals(incident_blob, limit=18)
        if deep_signals:
            try:
                deep_query = " ".join(deep_signals)
                rx_deep = regex_signal_search(deep_query, provider, 24)
                kw_deep = keyword_search(deep_query, provider, 12)
                results = _dedupe_results(rx_deep, kw_deep, limit=24)
                results = _rank_results_by_evidence(results, incident_blob, limit=12)
            except Exception as exc:
                logger.warning("Deep regex second-pass retrieval failed: %s", exc)

    # Third-pass expanded deep hunt for low/empty evidence to improve tab predictions.
    deep_hunt_needed = (not results) or (feature == "similar_incidents" and len(_build_similar_incidents_evidence_lines(results, incident_blob, limit=1)) == 0)
    if deep_hunt_needed:
        deep_results = _run_deep_search_hunt(incident_blob, provider, max_results=32)
        if deep_results:
            results = _rank_results_by_evidence(_dedupe_results(results, deep_results, limit=32), incident_blob, limit=16)

    return results


# Function: _compute_evidence_strength
def _compute_evidence_strength(results: list, incident_blob: str) -> tuple[float, bool]:
    # Calculate evidence strength — higher weights for top score and overlap for realistic confidence
    top_score = float(results[0][1]) if results else 0.0
    avg_score = (sum(float(s) for _, s in results) / len(results)) if results else 0.0
    coverage = min(1.0, len(results) / 6.0)
    match_terms = _query_terms(incident_blob)
    overlap_strength = max((_overlap_score(doc.page_content or "", match_terms) for doc, _ in results), default=0.0)
    # Rebalanced: top_score is the strongest quality signal; coverage rewards breadth
    evidence_strength = min(1.0, (top_score * 0.48) + (avg_score * 0.20) + (coverage * 0.18) + (overlap_strength * 0.14))
    # Lowered from 0.50 to 0.38 — reduce unnecessary double-LLM calls for borderline evidence
    weak_evidence = evidence_strength < 0.38
    return evidence_strength, weak_evidence


# Function: _grounded_answer_needs_fallback
def _grounded_answer_needs_fallback(feature: str, answer: str, context_text: str) -> bool:
    answer_low = answer.lower()
    _REFUSAL_PHRASES = (
        "classification cannot be determined",
        "cannot be determined",
        "no matching patterns found",
    )
    cited_incs_in_answer = _extract_incidents_from_text(answer, limit=20) if answer else []
    ctx_low = context_text.lower()
    # Only reject generic phrases if the response contains NO grounded INC citations
    # (a response citing real incidents can still say "typically" in a grounded context)
    purely_generic = any(phrase in answer_low for phrase in _DISALLOWED_GENERIC_PHRASES) and not cited_incs_in_answer
    hard_refusal = any(phrase in answer_low for phrase in _REFUSAL_PHRASES)
    hallucinated_incs = any(inc.lower() not in ctx_low for inc in cited_incs_in_answer) if cited_incs_in_answer else False
    return not answer or (feature == "classify_incident" and hard_refusal) or purely_generic or hallucinated_incs


# Function: _resolve_grounded_answer
def _resolve_grounded_answer(
    feature: str,
    answer: str,
    context_text: str,
    incident_blob: str,
    results: list,
    provider: str,
    weak_evidence: bool,
) -> tuple[str, bool]:
    if not _grounded_answer_needs_fallback(feature, answer, context_text):
        return answer, False
    if weak_evidence:
        weak_answer = _analyze_weak_evidence_with_llm(feature, context_text, incident_blob, results, provider)
        if weak_answer:
            return weak_answer, False
    return _feature_fallback(feature, context_text, incident_blob, results), True


# Function: _compute_grounded_confidence
def _compute_grounded_confidence(evidence_strength: float, fallback_used: bool, feature: str) -> float:
    # Rebalanced confidence — evidence_strength is now a more realistic signal
    # Fallback path: scale from 0.32 to 0.62; LLM path: scale from 0.52 to 0.92
    tuned_tabs = {"anomaly_analysis", "event_correlation", "incident_summarize", "similar_incidents", "classify_incident"}
    if fallback_used and feature in tuned_tabs:
        return round(min(0.62, max(0.32, evidence_strength * 0.88)), 4)
    return round(min(0.92, max(0.52, evidence_strength * 0.85 + 0.18)), 4)


# Function: _run_feature_grounded
def _run_feature_grounded(feature: str, incident_blob: str, provider: str) -> dict:
    cache_key = _feature_cache_key(feature, incident_blob, provider)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    results = _retrieve_grounded_results(incident_blob, provider, feature)

    if not results:
        weak_answer = _analyze_weak_evidence_with_llm(feature, "", incident_blob, [], provider)
        payload = {
            "answer": weak_answer or _feature_fallback(feature, "", incident_blob, []),
            "sources": [],
            "confidence": 0.0,
            "context_used": False,
            "fallback_used": True,
            "similar_incidents": [],
        }
        _cache_put(cache_key, payload)
        return payload

    context_text = _format_feature_context(results, max_chunks=8, max_chars=1000)
    prompt = (
        f"{_FEATURE_PROMPTS[feature]}\n\n"
        "GROUNDING RULES:\n"
        "1. Every claim must be grounded in CONTEXT below.\n"
        "2. Cite ACTUAL INC ticket IDs shown in [brackets] in CONTEXT (e.g. INC0073861). Never use [1], [2] style.\n"
        "3. If evidence is limited, state it clearly but always produce the requested output format.\n"
        "4. Be specific and complete — include all relevant details from CONTEXT.\n\n"
        f"Incident details:\n{incident_blob}\n\n"
        f"CONTEXT:\n{context_text}"
    )

    evidence_strength, weak_evidence = _compute_evidence_strength(results, incident_blob)

    llm = _get_feature_llm(provider)
    response = llm.invoke(
        [("system", "You are a strict grounded IT analysis assistant."), ("human", prompt)]
    )
    answer = (response.content if hasattr(response, "content") else str(response)).strip()

    answer, fallback_used = _resolve_grounded_answer(
        feature, answer, context_text, incident_blob, results, provider, weak_evidence
    )

    confidence = _compute_grounded_confidence(evidence_strength, fallback_used, feature)
    sources = [
        {
            "source": str(doc.metadata.get("source", "unknown")),
            "type": str(doc.metadata.get("type", "unknown")),
            "relevance": float(score),
        }
        for doc, score in results
    ]

    payload = {
        "answer": answer,
        "sources": sources,
        "confidence": confidence,
        "context_used": True,
        "fallback_used": fallback_used,
        "similar_incidents": _extract_similar_incidents_from_results(results),
    }
    _cache_put(cache_key, payload)
    return payload


# Function: _build_fast_grounded_timeout_payload
def _build_fast_grounded_timeout_payload(request: IncidentFeatureRequest, provider: str) -> dict:
    """Return a fast grounded fallback with evidence when full feature analysis times out."""
    incident_blob = _incident_text(request)
    enriched_query = _build_enriched_feature_query(incident_blob)
    try:
        with ThreadPoolExecutor(max_workers=3) as pool:
            f_sem = pool.submit(similarity_search, enriched_query, provider, 10)
            f_kw = pool.submit(keyword_search, enriched_query, provider, 8)
            f_rx = pool.submit(regex_signal_search, enriched_query, provider, 12)
            sem = f_sem.result()
            kw = f_kw.result()
            rx = f_rx.result()
        results = _dedupe_results(_dedupe_results(sem, kw, limit=14), rx, limit=14)
        results = _rank_results_by_evidence(results, incident_blob, limit=8)
    except Exception:
        results = []

    if not results:
        return {
            "feature": request.feature,
            "answer": (
                "Analysis timed out before completion and no grounded evidence could be retrieved quickly. "
                "Retry with one discriminator (exact error code, stack trace line, or transaction code)."
            ),
            "confidence": 0.18,
            "context_used": False,
            "mode": "analysis",
            "sources": [],
            "similar_incidents": [],
        }

    context_text = _format_feature_context(results, max_chunks=5, max_chars=550)
    answer = _feature_fallback(request.feature, context_text, incident_blob, results)
    sources = [
        {
            "source": str(doc.metadata.get("source", "unknown")),
            "type": str(doc.metadata.get("type", "unknown")),
            "relevance": float(score),
        }
        for doc, score in results
    ]
    return {
        "feature": request.feature,
        "answer": answer,
        "confidence": 0.44,
        "context_used": True,
        "mode": "analysis",
        "sources": sources,
        "similar_incidents": _extract_similar_incidents_from_results(results),
    }


# Function: _resolve_provider
def _resolve_provider(req_provider: Optional[str]) -> str:
    requested = req_provider.value if hasattr(req_provider, "value") else req_provider
    # Force Ollama GPU model for feature tabs to keep outputs deterministic and locally grounded.
    if requested and str(requested).strip().lower() != "ollama":
        logger.info("incident_workbench provider override: requested=%s -> using=ollama", requested)
    return "ollama"


# Function: _incident_text
def _incident_text(payload: IncidentFeatureRequest) -> str:
    incident_no = payload.incident_number or "N/A"
    return (
        f"Incident Number: {incident_no}\n"
        f"Short Description: {payload.short_description}\n"
        f"Description: {payload.description}\n"
        f"Priority: {payload.priority or 'N/A'}\n"
        f"Category: {payload.category or 'N/A'}\n"
        f"Additional Context: {payload.additional_context or 'N/A'}"
    )


# Function: _build_feature_response
def _build_feature_response(request: IncidentFeatureRequest, provider: str) -> IncidentFeatureResponse:
    incident_blob = _incident_text(request)
    prompt_prefix = _FEATURE_PROMPTS.get(request.feature)
    if not prompt_prefix:
        raise HTTPException(status_code=400, detail="Unsupported feature.")

    try:
        rag = _run_feature_grounded(request.feature, incident_blob, provider)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Feature execution failed: {exc}")

    similar: list[SimilarIncident] | None = None
    if request.feature in {"similar_incidents", "event_correlation"}:
        similar = rag.get("similar_incidents") or _extract_similar_incidents(incident_blob, provider=provider)

    answer_text = (rag.get("answer", "") or "").strip()
    if not answer_text:
        if similar:
            rel = ", ".join(item.incident_number for item in similar[:5])
            answer_text = f"Related incidents in context: {rel}."
        else:
            answer_text = (
                "Verified fix could not be established from matched incidents. "
                "Provide one discriminator (exact error code, stack trace line, or transaction code) for a tighter match."
            )

    sources = _normalize_source_docs(rag.get("sources", []))
    context_used = bool(rag.get("context_used", False) or sources)

    logger.info(
        "mode=analysis endpoint=/api/incident-workbench/run-feature feature=%s context_used=%s sources=%d confidence=%.4f",
        request.feature,
        context_used,
        len(sources),
        float(rag.get("confidence", 0.0)),
    )

    return IncidentFeatureResponse(
        feature=request.feature,
        answer=answer_text,
        confidence=float(rag.get("confidence", 0.0)),
        context_used=context_used,
        mode="analysis",
        sources=sources,
        similar_incidents=similar,
    )


# Function: _build_feature_response_with_timeout
def _build_feature_response_with_timeout(request: IncidentFeatureRequest, provider: str, timeout_sec: int) -> IncidentFeatureResponse:
    future = _FEATURE_EXECUTOR.submit(_build_feature_response, request, provider)
    try:
        return future.result(timeout=max(1, int(timeout_sec)))
    except FutureTimeout as exc:
        future.cancel()
        raise TimeoutError(f"feature timeout after {timeout_sec}s") from exc


# Function: _run_feature_job
async def _run_feature_job(job_id: str, request: IncidentFeatureRequest, provider: str) -> None:
    started_at = time.perf_counter()
    try:
        timeout_sec = min(120, max(30, int(getattr(cfg, "FEATURE_JOB_TIMEOUT_SECONDS", 60) or 60)))
        async with _FEATURE_JOB_SEMAPHORE:
            response = await asyncio.to_thread(
                _build_feature_response_with_timeout,
                request,
                provider,
                timeout_sec,
            )
        payload = response.model_dump() if hasattr(response, "model_dump") else response.dict()
        _FEATURE_JOBS[job_id].update({"status": "done", "result": payload})
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        logger.info(
            "feature_job done job_id=%s feature=%s provider=%s elapsed_ms=%.1f queue_limit=%d",
            job_id,
            request.feature,
            provider,
            elapsed_ms,
            _FEATURE_JOB_MAX_CONCURRENCY,
        )
    except asyncio.TimeoutError:
        payload = await asyncio.to_thread(_build_fast_grounded_timeout_payload, request, provider)
        _FEATURE_JOBS[job_id].update({"status": "done", "result": payload})
        logger.warning(
            "feature_job timeout job_id=%s feature=%s provider=%s elapsed_ms=%.1f context_used=%s sources=%d",
            job_id,
            request.feature,
            provider,
            (time.perf_counter() - started_at) * 1000,
            bool(payload.get("context_used", False)),
            len(payload.get("sources", [])),
        )
    except HTTPException as exc:
        _FEATURE_JOBS[job_id].update({"status": "error", "detail": str(exc.detail)})
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        logger.warning(
            "feature_job failed job_id=%s feature=%s provider=%s elapsed_ms=%.1f detail=%s",
            job_id,
            request.feature,
            provider,
            elapsed_ms,
            exc.detail,
        )
    except Exception as exc:
        _FEATURE_JOBS[job_id].update({"status": "error", "detail": str(exc)})
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        logger.exception(
            "feature_job failed job_id=%s feature=%s provider=%s elapsed_ms=%.1f",
            job_id,
            request.feature,
            provider,
            elapsed_ms,
        )


# Function: _extract_similar_incidents
def _extract_similar_incidents(question: str, provider: str) -> list[SimilarIncident]:
    results = similarity_search(question, provider=provider, k=8)
    results = _rank_results_by_evidence(results, question, limit=8)
    incidents: list[SimilarIncident] = []
    seen: set[str] = set()
    inc_re = re.compile(r"\bINC\d+\b", re.IGNORECASE)

    for doc, score in results:
        from_meta = str(doc.metadata.get("incident_number", "")).upper()
        from_text = inc_re.findall(doc.page_content)
        candidate = from_meta or (from_text[0].upper() if from_text else "")
        if not candidate:
            continue
        if candidate in seen:
            continue
        seen.add(candidate)

        summary = doc.page_content.replace("\n", " ").strip()
        incidents.append(
            SimilarIncident(
                incident_number=candidate,
                summary=summary[:240],
                source=str(doc.metadata.get("source", "unknown")),
                relevance=float(score),
            )
        )

        if len(incidents) >= 5:
            break

    return incidents


# Function: _normalize_source_docs
def _normalize_source_docs(raw_sources: list) -> list[SourceDoc]:
    sources: list[SourceDoc] = []
    for item in raw_sources or []:
        if isinstance(item, dict):
            source = str(item.get("source", "unknown"))
            source_type = str(item.get("type", "unknown"))
            relevance = item.get("relevance", 0.0)
        else:
            source = str(getattr(item, "source", "unknown"))
            source_type = str(getattr(item, "type", "unknown"))
            relevance = getattr(item, "relevance", 0.0)

        try:
            relevance_value = float(relevance)
        except (TypeError, ValueError):
            relevance_value = 0.0

        if not math.isfinite(relevance_value):
            relevance_value = 0.0

        try:
            sources.append(
                SourceDoc(source=source, type=source_type, relevance=relevance_value)
            )
        except Exception:
            # Skip malformed source entries rather than failing the entire feature response.
            continue
    return sources


# Function: run_incident_feature
@router.post("/run-feature", response_model=IncidentFeatureResponse)
async def run_incident_feature(
    request: IncidentFeatureRequest,
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Force feature tabs to Ollama for deterministic local grounding.
    provider = "ollama"
    async with _FEATURE_JOB_SEMAPHORE:
        # Unlike _run_feature_job (the async job path), this sync endpoint had no
        # bound at all — a stalled Ollama/RAG call could run past IIS/ARR's
        # 2-minute proxy timeout and surface as an opaque 502.3 Bad Gateway
        # instead of a clean error. Reuse the same bounded helper the async job
        # path already uses, safely under the 120s proxy ceiling.
        try:
            return await asyncio.to_thread(_build_feature_response_with_timeout, request, provider, 100)
        except TimeoutError as exc:
            raise HTTPException(status_code=504, detail=str(exc))


# Function: run_incident_feature_async
@router.post("/run-feature-async")
async def run_incident_feature_async(
    request: IncidentFeatureRequest,
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    provider = "ollama"
    _cleanup_feature_jobs()

    job_id = str(uuid.uuid4())
    _FEATURE_JOBS[job_id] = {
        "status": "pending",
        "result": None,
        "detail": None,
        "created_at": time.time(),
        "expires_at": time.time() + _FEATURE_JOB_TTL_SEC,
    }
    asyncio.create_task(_run_feature_job(job_id, request, provider))
    return {"status": "pending", "job_id": job_id}


# Function: run_incident_feature_job_status
@router.get("/feature-job/{job_id}")
async def run_incident_feature_job_status(job_id: str, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    _cleanup_feature_jobs()
    job = _FEATURE_JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Feature job not found or expired")

    created_at = float(job.get("created_at", time.time()))
    elapsed = max(0.0, time.time() - created_at)
    retry_after_ms = 0
    if job.get("status", "pending") == "pending":
        if elapsed < 3:
            retry_after_ms = 250
        elif elapsed < 15:
            retry_after_ms = 450
        elif elapsed < 45:
            retry_after_ms = 800
        else:
            retry_after_ms = 1200

    return {
        "status": job.get("status", "pending"),
        "result": job.get("result"),
        "detail": job.get("detail"),
        "retry_after_ms": retry_after_ms,
    }
