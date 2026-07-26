# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: RAG pipeline — retrieves context and generates grounded answers.
# Date: 2025-10-20
# ---------------------------------------------------------------------------
"""
RAG pipeline — retrieves context and generates grounded answers.
Anti-hallucination enforced via:
  1. Relevance-score gate (MIN_RELEVANCE_SCORE)
  2. Layer 0: exact metadata lookup (INC number / SolManID / delivery number)
  3. Layer 1: vector similarity search (semantic embeddings)
  4. Layer 2: keyword / SAP-entity text-match search (BM25-style fallback)
  5. Layer 3: solution-chunk sibling augmentation
  6. FlashrankRerank cross-encoder — reorders all candidates by true relevance
  7. Context window cap — only TOP_CONTEXT_CHUNKS sent to LLM
  8. Regex-first extraction — solution text extracted verbatim before LLM call
  9. Direct-answer short-circuit — LLM formats, not discovers, the answer
 10. Rule-based answer validation — blocks responses that cite IDs/numbers not
     found verbatim in the retrieved context (hallucination guard)
 11. Temperature = 0
"""
import logging
import hashlib
import json
import re
import time
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FutureTimeout
from typing import Any, Dict, List, Optional

import backend.config as cfg
from langchain_core.documents import Document

from backend.rag.vectorstore import (
    similarity_search,
    fetch_solution_chunks,
    keyword_search,
    metadata_search,
    regex_signal_search,
)

logger = logging.getLogger(__name__)

_ML_SIGNAL_CACHE_TTL_SEC = 300
_ML_SIGNAL_CACHE: dict[str, tuple[float, dict]] = {}
_ML_SIGNAL_TIMEOUT_SEC = int(getattr(cfg, "OLLAMA_SIGNAL_EXTRACTION_TIMEOUT_SECONDS", 4))
_ML_SIGNAL_MIN_QUERY_CHARS = 220
_ML_SIGNAL_EXECUTOR = ThreadPoolExecutor(max_workers=max(2, min(4, (os.cpu_count() or 4))))

# ── SAP entity extraction from user query ────────────────────────────────
_Q_INC_RE      = re.compile(r'\b(INC\d+)\b', re.IGNORECASE)
_Q_SOLMAN_RE   = re.compile(r'\b(7\d{9})\b')               # 10-digit, starts with 7
_Q_DELIVERY_RE = re.compile(r'\b(1\d{8,11})\b')             # 9-12 digit SAP doc numbers


# Function: _extract_query_entities
def _extract_query_entities(query: str) -> dict:
    """
    Extract structured SAP identifiers from the user's query for Layer 0
    (exact metadata lookup).  Returns a dict consumed by metadata_search().
    """
    entities: dict = {}

    incs = list(dict.fromkeys(m.upper() for m in _Q_INC_RE.findall(query)))
    if incs:
        entities["inc_numbers"] = incs

    solman = list(dict.fromkeys(_Q_SOLMAN_RE.findall(query)))
    if solman:
        entities["solman_ids"] = solman

    deliveries = list(dict.fromkeys(_Q_DELIVERY_RE.findall(query)))
    if deliveries:
        entities["delivery_numbers"] = deliveries

    return entities


# ── Multi-query expansion ─────────────────────────────────────────────────
_TICKET_FIELD_PATTERNS = {
    "short_desc": re.compile(r"Short Description\s*:\s*(.+?)(?=\n|$)", re.IGNORECASE),
    "description": re.compile(r"(?<!\bShort )Description\s*:\s*(.+?)(?=\n(?:Priority|Category|Symptoms)|$)", re.IGNORECASE | re.DOTALL),
    "symptoms": re.compile(r"Symptoms?\s*:\s*(.+?)(?=\n|$)", re.IGNORECASE),
    "category": re.compile(r"Category\s*:\s*(.+?)(?=\n|$)", re.IGNORECASE),
}

_RETRIEVAL_LABEL_PATTERNS = [
    re.compile(
        r"Incident Number\s*:\s*(.+?)(?=(?:\n|\r|\b(?:Incident Number|Short Description|Description|Priority|Category|Symptoms|Environment|Recent Change|Suggested Resolution)\b\s*:|$))",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"Short Description\s*:\s*(.+?)(?=(?:\n|\r|\b(?:Incident Number|Short Description|Description|Priority|Category|Symptoms|Environment|Recent Change|Suggested Resolution)\b\s*:|$))",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"Description\s*:\s*(.+?)(?=(?:\n|\r|\b(?:Incident Number|Short Description|Description|Priority|Category|Symptoms|Environment|Recent Change|Suggested Resolution)\b\s*:|$))",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"Symptoms\s*:\s*(.+?)(?=(?:\n|\r|\b(?:Incident Number|Short Description|Description|Priority|Category|Symptoms|Environment|Recent Change|Suggested Resolution)\b\s*:|$))",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"Category\s*:\s*(.+?)(?=(?:\n|\r|\b(?:Incident Number|Short Description|Description|Priority|Category|Symptoms|Environment|Recent Change|Suggested Resolution)\b\s*:|$))",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"Priority\s*:\s*(.+?)(?=(?:\n|\r|\b(?:Incident Number|Short Description|Description|Priority|Category|Symptoms|Environment|Recent Change|Suggested Resolution)\b\s*:|$))",
        re.IGNORECASE | re.DOTALL,
    ),
]


# Function: _expand_queries
def _expand_queries(question: str) -> list[str]:
    """
    Decompose a structured incident ticket into focused sub-queries.

    A full ticket blob has a diluted embedding because the vector averages over
    all fields.  Extracting high-signal fields (short description, symptoms,
    category) and querying them separately dramatically improves recall.
    """
    base = _prepare_retrieval_query(question)
    queries: list[str] = [base]
    query_lowers = {base.lower()}

    for field, pat in _TICKET_FIELD_PATTERNS.items():
        m = pat.search(question)
        if not m:
            continue
        val = " ".join(m.group(1).strip().split())
        # Skip very short or duplicate values
        lowered = val.lower()
        if len(val) < 12 or lowered in query_lowers:
            continue
        if field in ("short_desc", "symptoms"):
            queries.append(val)
            query_lowers.add(lowered)
        elif field == "description":
            # Take first 200 chars of description
            desc = val[:200]
            queries.append(desc)
            query_lowers.add(desc.lower())

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for q in queries:
        if q.lower() not in seen:
            seen.add(q.lower())
            unique.append(q)
    return unique[:4]  # max 4 query angles to bound latency


# Function: _prepare_retrieval_query
def _prepare_retrieval_query(question: str) -> str:
    """
    Normalize long incident-template inputs into a retrieval-friendly query.

    Poll Tickets can produce large structured blobs. Using the full blob as a
    semantic query dilutes relevance; this function keeps the high-signal fields
    (short description, description, symptoms, codes, IDs) for retrieval.
    """
    q = (question or "").strip()
    if not q:
        return q

    # Fast path: short user query is already fine.
    if len(q) <= 360:
        return q

    parts: List[str] = []
    for pattern in _RETRIEVAL_LABEL_PATTERNS:
        m = pattern.search(q)
        if m:
            val = " ".join(m.group(1).strip().split())
            if val:
                parts.append(val)

    # Preserve quoted signatures and path-like fragments (high match value).
    for quoted in re.findall(r'"([^"]{6,180})"', q):
        parts.append(quoted.strip())

    # Keep mixed alpha-numeric error signatures.
    for token in re.findall(r"\b(?=[A-Za-z0-9]{6,24}\b)(?=[A-Za-z0-9]*[A-Za-z])(?=[A-Za-z0-9]*\d)[A-Za-z0-9_\-]+\b", q):
        parts.append(token)

    compact = " ".join(dict.fromkeys(p for p in parts if p))
    if not compact:
        compact = " ".join(q.split())

    return compact[:900]


# Function: _extract_ticket_signals_regex
def _extract_ticket_signals_regex(question: Optional[str]) -> Dict[str, List[str]]:
    q = question or ""
    if not q:
        return {"error_codes": [], "stack_tokens": [], "transaction_codes": [], "operational_tokens": [], "context_tokens": [], "keywords": []}

    error_codes = list(dict.fromkeys(_PRED_ERR_CODE_RE.findall(q.upper())))
    stack_tokens = list(
        dict.fromkeys(
            re.findall(r"\b(?:[A-Za-z_][A-Za-z0-9_]*Exception|[A-Za-z_][A-Za-z0-9_]*Error)\b", q)
        )
    )
    transaction_codes = list(dict.fromkeys(m.upper() for m in _PRED_TCODE_RE.findall(q)))
    operational_tokens = list(
        dict.fromkeys(
            [
                *[m.strip() for m in _PRED_JOBKEY_RE.findall(q)],
                *[m.strip() for m in _PRED_RCS_RE.findall(q)],
                *[m.strip() for m in _PRED_JOBNAME_RE.findall(q)],
            ]
        )
    )
    for marker in ("cancelled state", "canceled state", "reprocessed", "next run", "job has been reprocessed"):
        if marker in q.lower():
            operational_tokens.append(marker)
    operational_tokens = list(dict.fromkeys(operational_tokens))[:6]

    context_tokens = list(
        dict.fromkeys(
            [
                *[m.strip() for m in _PRED_COMPONENT_RE.findall(q)],
                *[m.strip() for m in _PRED_CHANNEL_RE.findall(q)],
                *[m.strip() for m in _PRED_INTERFACE_RE.findall(q)],
                *[m.strip() for m in _PRED_MESSAGE_GUID_RE.findall(q)],
                *[m.strip() for m in _PRED_TRANSACTION_ID_RE.findall(q)],
                *[m.strip() for m in _PRED_FLOW_NAME_RE.findall(q)],
            ]
        )
    )
    q_lower = q.lower()
    for marker in (
        "unable to establish connection",
        "returns: io error",
        "driver returns",
        "configuration scenario",
        "delivering to channel",
        "technical details",
        "failed message detected",
        "integrated gateway",
        "sap-system",
        "idocs got failed",
        "integration flow name",
        "message guid",
        "transaction id",
    ):
        if marker in q_lower:
            context_tokens.append(marker)
    context_tokens = list(dict.fromkeys(context_tokens))[:8]

    keywords = [
        t
        for t in re.findall(r"[A-Za-z0-9_\-]{4,}", q)
        if t.lower() not in _QUERY_STOPWORDS and not t.upper().startswith("INC")
    ]
    keywords = list(dict.fromkeys(keywords))[:8]

    return {
        "error_codes": error_codes[:5],
        "stack_tokens": stack_tokens[:5],
        "transaction_codes": transaction_codes[:5],
        "operational_tokens": operational_tokens,
        "context_tokens": context_tokens,
        "keywords": keywords,
    }


# Function: _parse_json_object
def _parse_json_object(text: str) -> Optional[dict]:
    raw = (text or "").strip()
    if not raw:
        return None
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        obj = json.loads(raw)
        return obj if isinstance(obj, dict) else None
    except Exception:
        pass
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        try:
            obj = json.loads(raw[start : end + 1])
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None
    return None


# Function: _extract_ticket_signals_ml
def _clean_ml_signal_list(parsed: Any, key: str, cap: int = 6) -> List[str]:
    values = parsed.get(key) if isinstance(parsed, dict) else []
    if not isinstance(values, list):
        return []
    out: List[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text:
            continue
        out.append(text)
    return list(dict.fromkeys(out))[:cap]


# Function: _has_sufficient_regex_signals
def _has_sufficient_regex_signals(base: Dict[str, List[str]]) -> bool:
    return bool(
        base.get("error_codes")
        or base.get("stack_tokens")
        or base.get("transaction_codes")
        or len(base.get("operational_tokens") or []) >= 2
        or len(base.get("context_tokens") or []) >= 2
    )


# Function: _extract_ticket_signals_ml
def _extract_ticket_signals_ml(question: Optional[str], llm_provider: str) -> Dict[str, List[str]]:
    q = (question or "").strip()
    base = _extract_ticket_signals_regex(q)
    if len(q) < _ML_SIGNAL_MIN_QUERY_CHARS:
        return base

    cache_key = hashlib.sha256(f"{llm_provider}|{q}".encode("utf-8", errors="ignore")).hexdigest()
    cached = _ML_SIGNAL_CACHE.get(cache_key)
    if cached and cached[0] >= time.time():
        return cached[1]

    if _has_sufficient_regex_signals(base):
        _ML_SIGNAL_CACHE[cache_key] = (time.time() + _ML_SIGNAL_CACHE_TTL_SEC, base)
        return base

    prompt = (
        "Extract diagnostic signals from this IT incident ticket. Return JSON only with keys: "
        "error_codes, stack_tokens, transaction_codes, keywords. "
        "Use short exact strings from input only, no invention. "
        f"Ticket:\n{q}"
    )

    try:
        from backend.llm.router import get_llm

        llm = get_llm(llm_provider)
        response = _ML_SIGNAL_EXECUTOR.submit(
            llm.invoke,
            [
                ("system", "You extract structured diagnostic signals from incident text. Return strict JSON."),
                ("human", prompt),
            ],
        ).result(timeout=max(1, min(_ML_SIGNAL_TIMEOUT_SEC, 3)))
        content = response.content if hasattr(response, "content") else str(response)
        parsed = _parse_json_object(content) or {}

        merged = {
            "error_codes": list(dict.fromkeys(base["error_codes"] + _clean_ml_signal_list(parsed, "error_codes")))[:6],
            "stack_tokens": list(dict.fromkeys(base["stack_tokens"] + _clean_ml_signal_list(parsed, "stack_tokens")))[:6],
            "transaction_codes": list(dict.fromkeys(base["transaction_codes"] + _clean_ml_signal_list(parsed, "transaction_codes")))[:6],
            "operational_tokens": base.get("operational_tokens") or [],
            "context_tokens": base.get("context_tokens") or [],
            "keywords": list(dict.fromkeys(base["keywords"] + _clean_ml_signal_list(parsed, "keywords", cap=10)))[:10],
        }
        _ML_SIGNAL_CACHE[cache_key] = (time.time() + _ML_SIGNAL_CACHE_TTL_SEC, merged)
        return merged
    except (FutureTimeout, Exception):
        _ML_SIGNAL_CACHE[cache_key] = (time.time() + _ML_SIGNAL_CACHE_TTL_SEC, base)
        return base


# Function: _enrich_query_with_signals
def _enrich_query_with_signals(base_query: str, signals: Optional[Dict[str, List[str]]]) -> str:
    if not signals:
        return base_query
    parts: List[str] = [base_query]
    for key in ("error_codes", "stack_tokens", "transaction_codes", "keywords"):
        for item in (signals.get(key) or []):
            text = str(item).strip()
            if text:
                parts.append(text)
    enriched = " ".join(dict.fromkeys(parts))
    return enriched[:1200]


# Function: _normalized_text
def _normalized_text(value: Optional[str]) -> str:
    return " ".join(str(value or "").split()).strip().lower()


# Function: _trim_chat_history_for_prompt
def _trim_chat_history_for_prompt(chat_history: Optional[List[Dict[str, str]]], question: str) -> List[Dict[str, str]]:
    turns = list(chat_history or [])
    if not turns:
        return []

    # Drop duplicated trailing human turn when clients already send `question` separately.
    nq = _normalized_text(question)
    while turns:
        last = turns[-1]
        role = str(last.get("role", "")).strip().lower() if isinstance(last, dict) else ""
        content = _normalized_text(last.get("content", "") if isinstance(last, dict) else "")
        if role == "human" and content and content == nq:
            turns.pop()
            continue
        break
    return turns


# ── Rule-based answer validation ─────────────────────────────────────────
_VALIDATE_INC_RE      = re.compile(r'\bINC\d+\b', re.IGNORECASE)
_VALIDATE_DELIVERY_RE = re.compile(
    r'(?:delivery|transfer\s+posting|new\s+delivery)\s+(\d{7,12})',
    re.IGNORECASE,
)
_VALIDATE_SOLMAN_RE   = re.compile(r'SolManID#?\s*(\d{7,13})', re.IGNORECASE)
# Strict (no IGNORECASE) so ordinary words like "step1"/"tab2" in generated prose
# don't false-positive as fabricated transaction/error codes — real SAP T-codes and
# error codes are conventionally written all-uppercase.
_VALIDATE_TCODE_RE    = re.compile(r'\b[A-Z]{2,5}\d{2,4}\b')
_VALIDATE_ERRCODE_RE  = re.compile(r'\b(?:ORA-\d{3,6}|SQL\d{3,6}[A-Z]?|0x[0-9A-Fa-f]{6,})\b')
_PRED_ERR_CODE_RE     = re.compile(r"\b(?:ORA-\d{3,6}|SQL\d{3,6}[A-Z]?|[A-Z]{2,6}\d{3,6}[A-Z]?|0x[0-9A-Fa-f]{6,})\b")
_PRED_STACK_RE        = re.compile(r"\b(?:[A-Za-z_][A-Za-z0-9_]*Exception|[A-Za-z_][A-Za-z0-9_]*Error)\b")
_PRED_TCODE_RE        = re.compile(r"\b(?:/N)?[A-Z]{2,5}\d{2,4}\b", re.IGNORECASE)
_PRED_JOBKEY_RE       = re.compile(r"\bJobkey\s*\d{4,}/\d+\b", re.IGNORECASE)
_PRED_RCS_RE          = re.compile(r"\bRCS\s*['\"]?[A-Z0-9_#\-]{2,20}['\"]?\b", re.IGNORECASE)
_PRED_JOBNAME_RE      = re.compile(r"\b[A-Z0-9_/#-]{6,}\b\s*'[^'\n]{2,20}'\s*Jobkey\s*\d{4,}/\d+", re.IGNORECASE)
_PRED_COMPONENT_RE    = re.compile(r"\b(?:[A-Za-z]+\.[A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)+|[A-Z]{2,}_[A-Za-z0-9_]{3,})\b")
_PRED_CHANNEL_RE      = re.compile(r"\b(?:JDBC|RFC|IDOC|SOAP|REST|HTTP|HTTPS)_[A-Z0-9_]{3,}\b", re.IGNORECASE)
_PRED_INTERFACE_RE    = re.compile(r"\b(?:SI|IF|API)_[A-Za-z0-9_]{4,}\b", re.IGNORECASE)
_PRED_MESSAGE_GUID_RE = re.compile(r"\bMessage\s+GUID\s*:\s*([A-Za-z0-9]{12,64})\b", re.IGNORECASE)
_PRED_TRANSACTION_ID_RE = re.compile(r"\bTransaction\s+ID\s*:\s*([A-Za-z0-9]{10,64})\b", re.IGNORECASE)
_PRED_FLOW_NAME_RE    = re.compile(r"\b(?:Affected\s+Integration\s+Flow\s+Name\s*:\s*)?([A-Z][A-Z0-9_]{10,}_v\d{3})\b", re.IGNORECASE)
_QUERY_STOPWORDS      = {
    "incident", "number", "short", "description", "priority", "category", "symptoms",
    "environment", "recent", "change", "reported", "issue", "failed", "error", "unknown",
    "users", "user", "process", "please", "provide", "based", "details", "resolved",
    "with", "from", "this", "that", "there", "their", "using", "about", "into",
    "production", "standard", "none", "reported",
}

_AUTO_CLOSURE_MARKERS = (
    "automatically closed",
    "auto closed",
    "auto-closed",
    "lack of response",
    "no response from the caller",
    "no response from caller",
    "7 calendar days",
    "permanent resolution code",
)

_LOW_SPECIFICITY_PHRASES = (
    "recurring operational issue",
    "impacting normal workflows",
    "production-like enterprise environment",
    "production-like enterprise setting",
    "recurring issues with task execution",
    "recurring issues were observed during task execution",
    "none reported",
)

_GENERIC_INCIDENT_TERMS = {
    "users", "reported", "recurring", "issues", "issue", "task", "execution", "workflow", "workflows",
    "status", "cancelled", "extended", "period", "further", "action", "production", "like", "environment",
    "enterprise", "setting", "observed", "occurred", "during", "prompting", "none", "reported", "change",
    "priority", "category", "symptoms", "description", "short", "incident", "number",
}


# Function: _top_weighted_candidate
def _top_weighted_candidate(chunks: List[tuple], pattern: re.Pattern, *, max_token_len: int = 40) -> Optional[str]:
    weights: Dict[str, float] = defaultdict(float)
    for doc, score in chunks:
        text = doc.page_content or ""
        w = max(0.05, float(score))
        for raw in pattern.findall(text):
            token = str(raw).strip().upper()
            if (
                not token
                or len(token) > max_token_len
                or token.startswith("INC")
                or token in {"P1", "P2", "P3", "P4", "N/A"}
            ):
                continue
            weights[token] += w
    if not weights:
        return None
    return max(weights.items(), key=lambda kv: kv[1])[0]


# Function: _predict_discriminator_from_history
def _predict_discriminator_from_history(chunks: List[tuple]) -> Dict[str, str]:
    err = _top_weighted_candidate(chunks, _PRED_ERR_CODE_RE)
    stack = _top_weighted_candidate(chunks, _PRED_STACK_RE)
    tcode = _top_weighted_candidate(chunks, _PRED_TCODE_RE)

    # Avoid returning very generic transaction-like tokens.
    if tcode and tcode in {"HTTP", "HTTPS", "ERROR"}:
        tcode = None

    result: Dict[str, str] = {}
    if err:
        result["error_code"] = err
    if stack:
        result["stack_token"] = stack
    if tcode:
        result["transaction_code"] = tcode
    return result


# Function: _query_terms
def _query_terms(question: Optional[str]) -> set[str]:
    if not question:
        return set()
    compact = _prepare_retrieval_query(question)
    tokens = set(re.findall(r"[a-z0-9_\-]{4,}", compact.lower()))
    return {t for t in tokens if t not in _QUERY_STOPWORDS and not t.startswith("inc")}


# Function: _focus_terms
def _focus_terms(question: Optional[str]) -> set[str]:
    """Extract higher-signal terms from structured ticket fields for relevance filtering."""
    q = question or ""
    if not q:
        return set()
    fields = [
        r"Short\s+Description\s*:\s*(.+?)(?=\n|$)",
        r"Symptoms?\s*:\s*(.+?)(?=\n|$)",
        r"Description\s*:\s*(.+?)(?=\n(?:Priority|Category|Environment|Recent\s+Change)\s*:|$)",
    ]
    parts: List[str] = []
    for pat in fields:
        m = re.search(pat, q, flags=re.IGNORECASE | re.DOTALL)
        if m:
            parts.append(" ".join(m.group(1).split()))
    if not parts:
        return _query_terms(q)
    text = " ".join(parts).lower()
    toks = set(re.findall(r"[a-z0-9_\-]{4,}", text))
    return {t for t in toks if t not in _QUERY_STOPWORDS and not t.startswith("inc")}


# Function: _detects_repeated_ticket_text
def _detects_repeated_ticket_text(question: Optional[str]) -> bool:
    # Repeated text blocks across short-description/description/symptoms are typically low-signal.
    short_m = re.search(r"(?im)^\s*Short\s+Description\s*:\s*(.+)$", question or "")
    desc_m = re.search(r"(?im)^\s*Description\s*:\s*(.+)$", question or "")
    sym_m = re.search(r"(?im)^\s*Symptoms\s*:\s*(.+)$", question or "")
    if not (short_m and desc_m and sym_m):
        return False
    s = " ".join(short_m.group(1).split()).lower()
    d = " ".join(desc_m.group(1).split()).lower()
    y = " ".join(sym_m.group(1).split()).lower()
    return bool(s and s in d and s in y)


# Function: _count_low_specificity_indicators
def _count_low_specificity_indicators(
    focus: set[str], phrase_hits: int, specificity_ratio: float, repeats_same_text: bool
) -> int:
    low_indicators = 0
    if len(focus) <= 8:
        low_indicators += 1
    if phrase_hits >= 1:
        low_indicators += 1
    if specificity_ratio < 0.35:
        low_indicators += 1
    if repeats_same_text:
        low_indicators += 1
    return low_indicators


# Function: _is_low_specificity_ticket
def _is_low_specificity_ticket(question: Optional[str]) -> bool:
    q = (question or "").lower()
    if not q:
        return True

    signals = _extract_ticket_signals_regex(question)
    if _has_sufficient_regex_signals(signals):
        return False

    focus = _focus_terms(question)
    phrase_hits = sum(1 for p in _LOW_SPECIFICITY_PHRASES if p in q)
    if not focus:
        return True

    non_generic = {t for t in focus if t not in _GENERIC_INCIDENT_TERMS}
    specificity_ratio = len(non_generic) / max(1, len(focus))
    context_strength = len(signals.get("context_tokens") or [])
    has_failure_lexeme = any(t in q for t in ("failed", "error", "timeout", "unable", "cannot", "denied", "stuck", "cancelled", "canceled"))
    repeats_same_text = _detects_repeated_ticket_text(question)

    # Technical interface/channel/driver clues should bypass low-specificity fallback.
    if context_strength >= 1 and len(focus) >= 7 and specificity_ratio >= 0.35 and not repeats_same_text:
        return False
    if context_strength >= 1 and has_failure_lexeme:
        return False

    low_indicators = _count_low_specificity_indicators(focus, phrase_hits, specificity_ratio, repeats_same_text)

    # Very broad incident text with multiple low-signal indicators should not trigger confident matching.
    return low_indicators >= 2


# Function: _prediction_context_profile
def _prediction_context_profile(question: Optional[str]) -> str:
    """Classify incident context for stable, scenario-aware prediction behavior."""
    if _is_auto_closure_lifecycle_case(question):
        return "lifecycle"
    if _has_hard_signals(question):
        return "diagnostic"
    if _is_low_specificity_ticket(question):
        return "low_specificity"
    return "contextual"


# Function: _has_hard_signals
def _has_hard_signals(question: Optional[str]) -> bool:
    q = (question or "").lower()
    s = _extract_ticket_signals_regex(question)
    return bool(
        s.get("error_codes")
        or s.get("stack_tokens")
        or s.get("transaction_codes")
        or len(s.get("operational_tokens") or []) >= 2
        or len(s.get("context_tokens") or []) >= 2
        or (len(s.get("context_tokens") or []) >= 1 and any(t in q for t in ("failed", "error", "timeout", "unable", "cannot", "denied", "stuck", "cancelled", "canceled")))
    )


# Function: _find_signal_snippet_in_doc
def _find_signal_snippet_in_doc(doc, score, tokens: List[str], seen: set[str]) -> Optional[str]:
    source = str(doc.metadata.get("source", "unknown"))
    content = " ".join((doc.page_content or "").split())
    if not content:
        return None
    for sent in re.split(r"(?<=[.!?])\s+", content):
        low = sent.lower()
        if not any(t in low for t in tokens):
            continue
        clean = _sanitize_hint_text(sent)
        if len(clean) < 24:
            continue
        key = clean.lower()
        if key in seen:
            continue
        seen.add(key)
        return f"[{source} @ {float(score):.4f}] {clean[:210]}"
    return None


# Function: _extract_signal_evidence
def _extract_signal_evidence(chunks: List[tuple], question: Optional[str], limit: int = 2) -> List[str]:
    signals = _extract_ticket_signals_regex(question)
    token_pool: List[str] = []
    token_pool.extend(signals.get("error_codes") or [])
    token_pool.extend(signals.get("stack_tokens") or [])
    token_pool.extend(signals.get("transaction_codes") or [])
    token_pool.extend(signals.get("context_tokens") or [])
    token_pool.extend(["cannot access the file", "being used by another process", "ioexception"])
    tokens = [t.lower() for t in token_pool if t]

    snippets: List[str] = []
    seen: set[str] = set()
    for doc, score in chunks:
        snippet = _find_signal_snippet_in_doc(doc, score, tokens, seen)
        if snippet:
            snippets.append(snippet)
        if len(snippets) >= limit:
            break
    return snippets


# Function: _diagnostic_scenario
def _diagnostic_scenario(question: Optional[str], signals: Dict[str, List[str]]) -> str:
    q = (question or "").lower()
    context = " ".join(signals.get("context_tokens") or []).lower()
    stack = " ".join(signals.get("stack_tokens") or []).lower()
    errors = " ".join(signals.get("error_codes") or []).lower()

    if any(token in q for token in ("cannot access the file", "being used by another process")) or "ioexception" in stack:
        return "file_lock"
    if "timeout" in q or "timeoutexception" in stack or "sockettimeoutexception" in stack:
        return "timeout"
    if any(token in q for token in ("oracle.jdbc.oracledriver", "unable to establish connection", "registered driver", "jdbc_rcv_", "driver returns: io error")):
        return "jdbc_connection"
    if any(token in q for token in ("integration flow name", "message guid", "transaction id", "integrated gateway")):
        return "integration_flow"
    if any(token in context for token in ("eai_", "message guid", "transaction id")):
        return "integration_flow"
    if any(token in q for token in ("jobkey", "cancelled state", "reprocessed", "next run")):
        return "job_execution"
    if errors or signals.get("transaction_codes"):
        return "application_failure"
    return "generic_diagnostic"


# Function: _diagnostic_summary
def _diagnostic_summary(scenario: str) -> str:
    mapping = {
        "file_lock": "Pattern-matched prediction from indexed incidents indicates a file/resource lock contention scenario.",
        "timeout": "Pattern-matched prediction from indexed incidents indicates a timeout or downstream connectivity degradation scenario.",
        "jdbc_connection": "Pattern-matched prediction from indexed incidents indicates a JDBC/driver connectivity or datasource registration scenario.",
        "integration_flow": "Pattern-matched prediction from indexed incidents indicates an SAP integration-flow processing scenario requiring flow-level trace validation.",
        "job_execution": "Pattern-matched prediction from indexed incidents indicates a batch/job execution failure scenario.",
        "application_failure": "Pattern-matched prediction from indexed incidents indicates an application-level processing failure scenario.",
        "generic_diagnostic": "Pattern-matched prediction from indexed incidents indicates a diagnostic scenario with concrete technical discriminators.",
    }
    return mapping.get(scenario, mapping["generic_diagnostic"])


# Function: _diagnostic_next_checks
def _diagnostic_next_checks(scenario: str, signals: Dict[str, List[str]]) -> str:
    context_tokens = signals.get("context_tokens") or []
    tx_tokens = signals.get("transaction_codes") or []
    lead_ctx = context_tokens[0] if context_tokens else "the failing component"
    lead_tx = tx_tokens[0] if tx_tokens else "the affected flow"

    if scenario == "file_lock":
        return (
            "Recommended next checks: identify the locking process/handle for the target file path, "
            "serialize concurrent writes for the same artifact, and retry after lock release."
        )
    if scenario == "timeout":
        return (
            "Recommended next checks: validate downstream endpoint latency and retry behavior, inspect timeout thresholds and network path stability, "
            "and capture the first failing timeout stack frame or adapter log entry."
        )
    if scenario == "jdbc_connection":
        return (
            f"Recommended next checks: validate datasource and driver registration for {lead_ctx}, confirm JDBC channel connectivity and credentials, "
            "and inspect adapter logs for connection initialization failures."
        )
    if scenario == "integration_flow":
        return (
            f"Recommended next checks: trace {lead_ctx} in the integration monitor using the Message GUID/Transaction ID, inspect adapter/channel logs for {lead_tx}, "
            "and validate the downstream endpoint or payload mapping step that first failed."
        )
    if scenario == "job_execution":
        return (
            "Recommended next checks: inspect the failed job step and scheduler history, confirm dependent task state and reprocessing outcome, "
            "and capture the first technical error emitted by the failing program or interface."
        )
    return (
        "Recommended next checks: capture the first failing technical event in logs, match it against retrieved incidents, "
        "and validate the leading remediation candidate in a controlled run before production use."
    )


# Function: _is_auto_closure_lifecycle_case
def _is_auto_closure_lifecycle_case(question: Optional[str]) -> bool:
    q = (question or "").lower()
    if not q:
        return False
    marker_hits = sum(1 for m in _AUTO_CLOSURE_MARKERS if m in q)
    has_auto_close = ("automatically closed" in q) or ("auto closed" in q) or ("auto-closed" in q)
    has_caller_timeout = ("caller" in q and "response" in q) or ("7 calendar days" in q)
    return marker_hits >= 2 or (has_auto_close and has_caller_timeout)


# Function: _sanitize_hint_text
def _sanitize_hint_text(text: str) -> str:
    cleaned = text or ""
    # Remove host/user-like noisy suffixes commonly seen in SN logs.
    cleaned = re.sub(r"\b[a-z][a-z0-9._-]{2,}@[a-z0-9._-]{4,}\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b[a-z]{2,8}\d{4,}\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip(" -|;,")
    return cleaned


# Function: _overlap_score
def _overlap_score(text: str, terms: set[str]) -> float:
    if not text:
        return 0.0
    if not terms:
        return 0.0
    low = text.lower()
    hits = sum(1 for t in terms if t in low)
    return hits / max(1, len(terms))


# Function: _extract_action_line_candidates
def _extract_action_line_candidates(content: str, action_line_re: "re.Pattern") -> List[str]:
    candidates = [m.group(1) for m in action_line_re.finditer(content)]
    # Fallback: capture imperative/action sentences if explicit labels are missing.
    if not candidates:
        for sentence in re.split(r"(?<=[.!?])\s+", " ".join(content.split())):
            low = sentence.lower()
            if any(k in low for k in ("restart", "reboot", "retry", "rerun", "clear", "validate", "check", "restore", "backup", "job", "service")):
                candidates.append(sentence)
    return candidates


# Function: _score_recommendation_candidate
def _score_recommendation_candidate(
    raw: str, score, terms: set[str], noisy_field_blob: "re.Pattern", seen: set[str]
) -> Optional[tuple[float, str]]:
    hint = _sanitize_hint_text(" ".join(str(raw).split()))
    if len(hint) < 15 or len(hint) > 180:
        return None
    # Skip full ticket field dumps accidentally captured as "recommendations".
    if len(noisy_field_blob.findall(hint)) >= 2:
        return None
    if hint.lower().startswith(("incident number:", "short description:", "description:")):
        return None
    hint = re.sub(r"\.{2,}", ".", hint).strip(" |;,-")
    key = hint.lower()
    if key in seen:
        return None
    seen.add(key)

    rel = max(0.05, float(score))
    ov = _overlap_score(hint, terms)
    total = (rel * 0.75) + (ov * 0.25)
    return total, hint[:220]


# Function: _extract_recommendation_candidates
def _extract_recommendation_candidates(chunks: List[tuple], question: Optional[str], limit: int = 3) -> List[str]:
    terms = _query_terms(question)
    noisy_field_blob = re.compile(
        r"(?i)(incident\s*number\s*:|short\s*description\s*:|description\s*:|priority\s*:|category\s*:|state\s*:|assignment\s*group\s*:|opened\s*at\s*:|resolved\s*at\s*:|closed\s*at\s*:)")
    action_line_re = re.compile(
        r"(?is)(?:solution|resolution|fix|workaround|action\s+taken|corrective\s+action|close_notes)\s*[:\-\.]\s*(.+?)(?=\n\s*(?:issue|problem|root\s*cause|solution|resolution|fix|workaround|close_code|$)|\Z)"
    )
    scored: List[tuple[float, str]] = []
    seen: set[str] = set()

    for doc, score in chunks:
        content = doc.page_content or ""
        candidates = _extract_action_line_candidates(content, action_line_re)

        for raw in candidates:
            result = _score_recommendation_candidate(raw, score, terms, noisy_field_blob, seen)
            if result is not None:
                scored.append(result)

    scored.sort(key=lambda x: x[0], reverse=True)
    return [hint for _, hint in scored[:limit]]


# Function: _validate_answer
_DISALLOWED_ANSWER_PATTERNS = (
    "i can't assist with this request",
    "i cannot assist with this request",
    "the provided context does not contain any relevant information",
    "however, based on the retrieved incidents",
    "however, i can list related incident numbers and descriptions",
    "related incident numbers and descriptions",
    "i can provide some general information",
    "general information related to",
    "unable to find any incidents that match your specific issue",
    "there are several related incidents with similar descriptions",
    "no verified resolution is available for the provided incident number",
    "providing resolution based on",
    "based on sap best practices",
    "based on general best practices",
    "combined with knowledge base insights",
)
_GENERIC_ANSWER_PHRASES = ("in general", "typically", "usually", "often")


# Function: _fallback_or_no_context
def _fallback_or_no_context(chunks: List[tuple], question: Optional[str]) -> str:
    return _build_no_verified_resolution_answer(chunks, question=question) if chunks else NO_CONTEXT_RESPONSE


# Function: _check_blocklisted_answer_text
def _check_blocklisted_answer_text(answer_low: str, chunks: List[tuple], question: Optional[str]) -> Optional[str]:
    # Block refusal-style or generic detours that are not actionable grounded answers.
    # These responses can appear with some model backends despite strict prompts.
    if any(p in answer_low for p in _DISALLOWED_ANSWER_PATTERNS):
        return _fallback_or_no_context(chunks, question)

    # Enforce no-generalization policy from SEARCH_PROMPT at runtime.
    if any(p in answer_low for p in _GENERIC_ANSWER_PHRASES):
        return _fallback_or_no_context(chunks, question)

    # Normalize legacy generic fallback templates and prevent speculative suffixes.
    # Always remap to the grounded fallback style used by this pipeline.
    if (
        "knowledge base does not contain a verified resolution" in answer_low
        or ("i don't have enough information" in answer_low and "knowledge base" in answer_low)
        or "no verified remediation steps were found" in answer_low
    ):
        return _fallback_or_no_context(chunks, question)

    return None


# Function: _check_answer_incident_numbers
def _check_answer_incident_numbers(
    answer_text: str, context_text: str, question: Optional[str], chunks: List[tuple]
) -> Optional[str]:
    # Check INC numbers
    question_incidents = {inc.upper() for inc in _VALIDATE_INC_RE.findall(question or "")}
    for inc in _VALIDATE_INC_RE.findall(answer_text):
        if inc.upper() in question_incidents:
            continue
        if not re.search(re.escape(inc), context_text, re.IGNORECASE):
            logger.warning(
                "Validation FAIL: INC '%s' in answer not found in retrieved context — "
                "blocking response to prevent hallucination.", inc,
            )
            return _fallback_or_no_context(chunks, question)
    return None


# Check explicitly labelled delivery numbers, SolManID numbers, transaction codes
# (e.g. SE93, VA01), and error codes (ORA-xxxx, SQLxxx, 0x...). These are the specific
# technical details the SEARCH_PROMPT's old "best practices" fallback used to invent
# wholesale — the LLM can produce a confident, well-structured answer citing a
# real-looking T-code that never appeared anywhere in the retrieved incidents. Block
# it the same way fabricated INC/delivery/SolManID numbers are blocked.
_LITERAL_CODE_CHECKS = (
    (_VALIDATE_DELIVERY_RE, "Validation FAIL: delivery '%s' in answer not in context."),
    (_VALIDATE_SOLMAN_RE, "Validation FAIL: SolManID '%s' in answer not in context."),
    (
        _VALIDATE_TCODE_RE,
        "Validation FAIL: transaction code '%s' in answer not found in retrieved context — "
        "blocking response to prevent hallucination.",
    ),
    (
        _VALIDATE_ERRCODE_RE,
        "Validation FAIL: error code '%s' in answer not found in retrieved context — "
        "blocking response to prevent hallucination.",
    ),
)


# Function: _check_answer_literal_codes
def _check_answer_literal_codes(
    answer_text: str, context_text: str, question: Optional[str], chunks: List[tuple]
) -> Optional[str]:
    for pattern, log_msg in _LITERAL_CODE_CHECKS:
        for num in pattern.findall(answer_text):
            if num not in context_text:
                logger.warning(log_msg, num)
                return _fallback_or_no_context(chunks, question)
    return None


# Function: _check_ungrounded_answer
def _check_ungrounded_answer(
    answer_text: str, answer_low: str, chunks: List[tuple], question: Optional[str]
) -> Optional[str]:
    # If we have context but the model produced an ungrounded free-form answer
    # without any incident/source anchors, force deterministic fallback.
    has_inc_anchor = bool(_VALIDATE_INC_RE.search(answer_text))
    has_source_anchor = bool(re.search(r"\bsource\b", answer_text, re.IGNORECASE))
    known_sources = [str(doc.metadata.get("source", "")).strip() for doc, _ in chunks]
    has_known_source_name = any(src and src.lower() in answer_low for src in known_sources)
    if chunks and not (has_inc_anchor or has_source_anchor or has_known_source_name):
        return _build_no_verified_resolution_answer(chunks, question=question)
    return None


# Function: _validate_answer
def _validate_answer(answer: str, chunks: List[tuple], question: Optional[str] = None) -> str:
    """
    Rule-based post-generation validation.

    Checks that EVERY specific identifier cited in the LLM's answer — INC
    numbers, labelled delivery numbers, and SolManIDs — exists verbatim in
    the retrieved context chunks.  If any identifier fails this check, the
    answer is discarded and the safe fallback message is returned.

    This is the final anti-hallucination layer: even if the LLM generates a
    plausible-sounding answer containing fabricated IDs, this guard catches it
    before it reaches the user.
    """
    answer_text = (answer or "").strip()
    answer_low = answer_text.lower()

    blocked = _check_blocklisted_answer_text(answer_low, chunks, question)
    if blocked is not None:
        return blocked

    context_text = " ".join(doc.page_content for doc, _ in chunks)

    inc_fail = _check_answer_incident_numbers(answer_text, context_text, question, chunks)
    if inc_fail is not None:
        return inc_fail

    code_fail = _check_answer_literal_codes(answer_text, context_text, question, chunks)
    if code_fail is not None:
        return code_fail

    ungrounded = _check_ungrounded_answer(answer_text, answer_low, chunks, question)
    if ungrounded is not None:
        return ungrounded

    return answer_text


# ── How many chunks the LLM actually sees after reranking ────────────────
# 8 high-quality chunks gives the LLM enough indexed evidence for workbench
# features (correlation, similar incidents) while avoiding context overflow.
TOP_CONTEXT_CHUNKS = 6

# ── Reranker (lazy-loaded once) ───────────────────────────────────────────
_reranker = None

# Function: _get_reranker
def _get_reranker():
    global _reranker
    if _reranker is None:
        try:
            import os, tempfile
            from flashrank import Ranker
            _cache = os.path.join(tempfile.gettempdir(), "flashrank")
            _reranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir=_cache)
            logger.info("FlashrankRerank loaded: ms-marco-MiniLM-L-12-v2")
        except Exception as exc:
            logger.warning("Could not load flashrank reranker (%s) — skipping rerank step.", exc)
            _reranker = False   # False = tried and failed, don't retry
    return _reranker if _reranker is not False else None


# Function: _rerank
def _rerank(query: str, chunks: List[tuple]) -> List[tuple]:
    """
    Re-order chunks using a cross-encoder (ms-marco-MiniLM-L-12-v2).
    Falls back to original order if flashrank is unavailable.
    Returns at most TOP_CONTEXT_CHUNKS items.
    """
    ranker = _get_reranker()
    if not ranker or not chunks:
        return chunks[:TOP_CONTEXT_CHUNKS]

    try:
        from flashrank import RerankRequest
        passages = [
            {"id": i, "text": doc.page_content}
            for i, (doc, _) in enumerate(chunks)
        ]
        req = RerankRequest(query=query, passages=passages)
        results = ranker.rerank(req)
        # results are sorted by score descending; map back to (doc, score) tuples
        reranked = [
            (chunks[r["id"]][0], float(r.get("score", 0.0)))
            for r in results[:TOP_CONTEXT_CHUNKS]
        ]
        logger.debug("Reranker: top result score=%.4f  text=%.80s",
                     reranked[0][1] if reranked else 0,
                     reranked[0][0].page_content if reranked else "")
        return reranked
    except Exception as exc:
        logger.warning("Reranking failed (%s) — using unsorted top-%d.", exc, TOP_CONTEXT_CHUNKS)
        return chunks[:TOP_CONTEXT_CHUNKS]


# ── Regex to detect and highlight solution sections ───────────────────────
_SOLUTION_LABEL_RE = re.compile(
    r'(?m)^([ \t]*)'
    r'(Solution|Resolution|Fix|Workaround|Action\s+Taken|Corrective\s+Action)'
    r'([ \t]*[:\-\.][ \t]*)',
    re.IGNORECASE,
)

# Function: _annotate_solutions
def _annotate_solutions(text: str) -> str:
    return _SOLUTION_LABEL_RE.sub(
        lambda m: f"{m.group(1)}>>> [SOLUTION] {m.group(2).upper()}{m.group(3)}",
        text,
    )


# ── Regex to extract raw solution body text ───────────────────────────────
# Handles both:
#   - DOCX / XLSX flat format:  "Resolution: ..."  or "Solution: ..."
#   - MD flat format after _load_md conversion: "\nResolution: ..."
#   - ServiceNow JSONL flat format: "close_notes": "..." or close_notes: ...
_SOLUTION_BODY_RE = re.compile(
    r'(?:Solution|Resolution|Fix|Workaround|Action\s+Taken|Corrective\s+Action'
    r'|close_notes|close_code)'
    r'(?:"?\s*[:\-\.]\s*"?|\s*":\s*")'
    r'(.+?)(?=\n[ \t]*(?:Issue|Problem|Root\s*Cause|Solution|Resolution|Fix|'
    r'Workaround|Keywords|INC\d+|close_notes|close_code|$)|\Z)',
    re.IGNORECASE | re.DOTALL,
)

# Separate lightweight regex for close_notes/close_code JSON field extraction
# (used as a secondary pass when the main regex misses flat JSONL content).
_CLOSE_NOTES_RE = re.compile(
    r'"close_notes"\s*:\s*"([^"]{10,})"',
    re.IGNORECASE,
)
_CLOSE_CODE_RE = re.compile(
    r'"close_code"\s*:\s*"([^"]{3,})"',
    re.IGNORECASE,
)

# Function: _extract_solution_text
def _extract_solution_body_matches(content: str, src: str, seen: set) -> List[str]:
    extractions: List[str] = []
    for match in _SOLUTION_BODY_RE.finditer(content):
        body = match.group(1).strip().strip('"').strip()
        if body and body not in seen and len(body) >= 10:
            seen.add(body)
            extractions.append(f"• [{src}] {body}")
    return extractions


# Function: _extract_close_notes_matches
def _extract_close_notes_matches(content: str, src: str, seen: set) -> List[str]:
    extractions: List[str] = []
    for match in _CLOSE_NOTES_RE.finditer(content):
        body = match.group(1).strip()
        if body and body not in seen and len(body) >= 10:
            # Skip auto-close boilerplate
            if "automatically closed" not in body.lower():
                seen.add(body)
                extractions.append(f"• [{src}] (close notes) {body}")
    return extractions


# Function: _extract_solution_text
def _extract_solution_text(chunks: List[tuple]) -> str:
    extractions: List[str] = []
    seen: set = set()
    for doc, _ in chunks:
        content = doc.page_content or ""
        src = doc.metadata.get("source", "unknown")

        # Primary: labelled Solution/Resolution/Workaround/close_notes sections
        extractions.extend(_extract_solution_body_matches(content, src, seen))

        # Secondary: bare JSON "close_notes":"..." fields (flat JSONL from ServiceNow)
        extractions.extend(_extract_close_notes_matches(content, src, seen))

    if not extractions:
        return ""
    return "=== EXTRACTED SOLUTIONS (use verbatim) ===\n" + "\n".join(extractions)


# Function: _get_top_solution
def _get_top_solution(chunks: List[tuple]) -> Optional[str]:
    """
    Return the solution text from the #1 ranked chunk if it has an explicit
    Solution/Resolution label — used for the direct-answer short-circuit.
    """
    if not chunks:
        return None
    top_doc = chunks[0][0]
    content = top_doc.page_content or ""
    match = _SOLUTION_BODY_RE.search(content)
    if match:
        body = match.group(1).strip().strip('"').strip()
        if body and len(body) >= 10:
            return body
    # Also check close_notes
    cn_match = _CLOSE_NOTES_RE.search(content)
    if cn_match:
        body = cn_match.group(1).strip()
        if body and len(body) >= 10 and "automatically closed" not in body.lower():
            return body
    return None


# ── System prompts ────────────────────────────────────────────────────────

# Used when the top-ranked chunk has a clear solution (direct-answer mode).
DIRECT_ANSWER_PROMPT = """You are a precise IT Support assistant specialised in SAP and enterprise systems.

The following solution has been retrieved verbatim from the knowledge base:

**Root Cause / Issue:**
{root_cause}

**Solution from Knowledge Base:**
{direct_answer}

**Source Document:** {source}

CRITICAL RULES — you MUST follow these without exception:
1. Present ONLY the information given above. Do NOT add steps, transaction codes, system names, or advice that does not appear in the solution text.
2. You may rephrase for clarity, but every technical detail (codes, system names, document numbers, steps) must be copied verbatim from the solution.
3. Do NOT infer, assume, or speculate about any detail not explicitly stated above.
4. If the solution references a specific action, present it exactly as written.

RESPONSE FORMAT — structure your response exactly in the following order:

First, write a single-line preamble: "Direct match found - {source}: <one-sentence summary of the matched issue and its resolution>."

Then produce these sections:

📋 DIAGNOSIS

List the root causes as concise bullet points drawn from the retrieved solution.

✅ RECOMMENDED RESOLUTION STEPS

Number each major step with a bold title. Under each step, indent the sub-actions as plain lines (one action per line). Include every transaction code, navigation path, tab name, and field name exactly as stated in the solution — do not paraphrase technical specifics.

⚠️ IMPORTANT NOTES

List important warnings, precautions, or prerequisites as bullet points. Only include items present in the solution text.

📞 ESCALATION PATH

If the solution mentions escalation targets or conditions, list them here. Otherwise write: "Follow standard escalation procedures if the above steps do not resolve the issue."

📊 CONFIDENCE LEVEL

Write: "High: Direct match found in knowledge base. Source: {source}."

🔧 IMMEDIATE NEXT STEPS

List any follow-up verification steps or additional information that would help confirm the fix is complete.
"""

# Used when no single clear solution is found — LLM must synthesise from context.
SEARCH_PROMPT = """You are a precise IT Support assistant specialised in enterprise IT service management, SAP, and ITSM.

The CONTEXT below contains knowledge base articles and past incident resolutions retrieved from a trusted internal ServiceNow database. Answer the user's question using ONLY information from this context.

CRITICAL GROUNDING RULES — you MUST follow these without exception:
1. ONLY use facts, steps, transaction codes, system names, and document numbers that appear explicitly in the CONTEXT.
2. Do NOT invent, infer, or assume any detail not present verbatim in the CONTEXT.
3. Do NOT combine information from multiple incidents unless the CONTEXT explicitly links them.
4. If the CONTEXT contains a Resolution or Solution section, reproduce its steps accurately — do not paraphrase technical actions.
5. If the CONTEXT has related incidents but no explicit verified resolution, do NOT say "no incidents found". Instead, list the related incident number(s), short description(s), and clearly state that no verified resolution is available.
6. If the CONTEXT does not contain enough information to provide a verified fix, state that in the CONFIDENCE LEVEL section. Then list related incidents and ask for one concrete discriminator (exact error code, stack trace line, or transaction code). Exception: for administrative lifecycle auto-closure scenarios, do not request technical discriminators.
7. Do NOT use phrases like "typically", "usually", "in general", or "often" — all claims must be grounded in the specific context provided.
8. Always cite the source incident number(s) or document name(s).
9. If multiple retrieved incidents are relevant, list each one separately with its INC number — do not merge their resolutions.
10. Never answer with refusal-style wording such as "I can't assist with this request" or generic detours like "general information".
11. Never substitute a real resolution with generic SAP/ITSM "best practices" advice. If the CONTEXT does not contain a verified fix for the specific issue asked about, say so plainly (see rule 5) — do not invent transaction codes, report names, or steps that are not present in the CONTEXT just to appear helpful.

RESPONSE FORMAT — structure your response exactly in the following order:

First, write a preamble (one or two lines):
- If the CONTEXT contains a related or partial match, write: "Partial match found - <INC number>: <one-sentence description of what actually matched, using only facts stated in the CONTEXT>."
- Then on the next line state plainly whether a verified resolution exists: "No verified resolution found in the retrieved incidents for <specific issue>." or "Direct match found for <specific issue>." Do NOT write anything resembling "providing resolution based on best practices" — if there is no verified resolution, the DIAGNOSIS and RESOLUTION STEPS sections below must say so rather than filling in generic advice.

Then produce these sections:

📋 DIAGNOSIS

List the root causes of the issue as concise bullet points. Derive only from the CONTEXT; if the CONTEXT is insufficient, state plainly that the root cause is not established by the retrieved evidence — do not offer a speculative root cause.

✅ RECOMMENDED RESOLUTION STEPS

If the CONTEXT contains verified resolution steps, number each major step with a bold title; under each step, indent the sub-actions as plain lines (one action per line), including every transaction code, navigation path, tab name, and field name exactly as present in the CONTEXT. If the CONTEXT does NOT contain verified resolution steps for this specific issue, write only: "No verified resolution steps are available in the retrieved incidents." Do not fill this section with generic transaction codes or reports not present in the CONTEXT.

⚠️ IMPORTANT NOTES

List important warnings, precautions, authorization requirements, and sequencing constraints as bullet points — only if present in the CONTEXT.

📞 ESCALATION PATH

Describe when to escalate, to which team, and any relevant OSS note searches or table-level checks, only if present in the CONTEXT. Otherwise write: "Follow standard escalation procedures for unresolved incidents."

📊 CONFIDENCE LEVEL

State the confidence level: High, Medium, or Low. Explain: what was matched in the CONTEXT, what was not matched, and if no verified resolution exists, say so explicitly rather than describing the answer as based on best practices.

🔧 IMMEDIATE NEXT STEPS

List the specific details the user should provide (asset number, company code, error message, depreciation area, etc.) to enable more targeted guidance.

CONTEXT:
{context}
"""

NO_CONTEXT_RESPONSE = (
    "Verified fix could not be established from matched incidents. "
    "Provide one concrete discriminator (exact error code, stack trace line, or transaction code) to refine the match."
)


# Function: _format_context
def _format_context(results: List[tuple]) -> str:
    if not results:
        return ""
    parts = []
    for i, (doc, score) in enumerate(results, 1):
        src = doc.metadata.get("source", "unknown")
        # Keep prompt compact to reduce LLM latency for chat answers.
        compact = (doc.page_content or "")[:900]
        annotated = _annotate_solutions(compact)
        parts.append(f"[{i}] Source: {src} (relevance: {score:.4f})\n{annotated}")
    return "\n\n---\n\n".join(parts)


# Function: _build_sources
def _build_sources(results: List[tuple]) -> List[Dict[str, Any]]:
    seen = set()
    sources = []
    for doc, score in results:
        src = doc.metadata.get("source", "unknown")
        if src not in seen:
            seen.add(src)
            sources.append({
                "source": src,
                "type": doc.metadata.get("type", "unknown"),
                "relevance": round(score, 4),
            })
    return sources


# Function: _extract_related_incidents
def _collect_related_incidents_from_doc(
    doc, q_terms: set[str], signal_tokens: set[str], seen: set[str], related: List[str], limit: int
) -> bool:
    """Process one chunk; returns True if the caller should stop (limit reached)."""
    content = doc.page_content or ""
    if _overlap_score(content, q_terms) < 0.14:
        return False
    if signal_tokens:
        up = content.upper()
        if not any(sig in up for sig in signal_tokens):
            return False
    for inc in _VALIDATE_INC_RE.findall(doc.page_content or ""):
        inc_u = inc.upper()
        if inc_u not in seen:
            seen.add(inc_u)
            related.append(inc_u)
            if len(related) >= limit:
                return True
    return False


# Function: _extract_related_incidents
def _extract_related_incidents(chunks: List[tuple], limit: int = 3, question: Optional[str] = None) -> List[str]:
    if _is_low_specificity_ticket(question):
        return []

    related: List[str] = []
    seen: set[str] = set()
    q_terms = _focus_terms(question)
    if len(q_terms) < 2:
        return []

    ticket_signals = _extract_ticket_signals_regex(question)
    signal_tokens = {
        *(s.upper() for s in (ticket_signals.get("error_codes") or [])),
        *(s.upper() for s in (ticket_signals.get("stack_tokens") or [])),
        *(s.upper() for s in (ticket_signals.get("transaction_codes") or [])),
    }

    for doc, _ in chunks:
        if _collect_related_incidents_from_doc(doc, q_terms, signal_tokens, seen, related, limit):
            break
    return related


# Function: _build_no_verified_resolution_answer
def _no_resolution_low_specificity(question: Optional[str]) -> str:
    inc_match = _VALIDATE_INC_RE.search(question or "")
    inc_text = f" for {inc_match.group(0).upper()}" if inc_match else ""
    return (
        "No high-specificity diagnostic signals were found in the provided ticket"
        f"{inc_text}. "
        "The text is currently too broad to produce a verified, incident-specific fix from indexed history. "
        "Provide at least two of these for accurate prediction: exact error code, failing transaction/API name, stack trace token, affected CI/service, and timestamp window."
    )


# Function: _no_resolution_lifecycle
def _no_resolution_lifecycle(question: Optional[str]) -> str:
    inc_match = _VALIDATE_INC_RE.search(question or "")
    inc_text = f" for {inc_match.group(0).upper()}" if inc_match else ""
    return (
        "This incident appears to be a workflow/lifecycle auto-closure event, not an unresolved technical failure"
        f"{inc_text}. "
        "Based on the provided details, it was auto-closed after a caller non-response confirmation window. "
        "No additional technical fix is indicated by matched evidence. "
        "Recommended next checks: validate auto-closure policy timing and notification audit trail; reopen the incident if impact persists and capture fresh symptom evidence."
    )


# Function: _no_resolution_diagnostic
def _no_resolution_diagnostic(chunks: List[tuple], question: Optional[str]) -> str:
    signals = _extract_ticket_signals_regex(question)
    evidence = _extract_signal_evidence(chunks, question=question, limit=2)
    action_hints = _extract_recommendation_candidates(chunks, question=question, limit=3)
    scenario = _diagnostic_scenario(question, signals)

    sig_parts: List[str] = []
    if signals.get("error_codes"):
        sig_parts.append("error=" + ", ".join(signals["error_codes"][:2]))
    if signals.get("stack_tokens"):
        sig_parts.append("stack=" + ", ".join(signals["stack_tokens"][:2]))
    if signals.get("transaction_codes"):
        sig_parts.append("tx=" + ", ".join(signals["transaction_codes"][:2]))
    if signals.get("context_tokens"):
        sig_parts.append("ctx=" + ", ".join(signals["context_tokens"][:2]))
    sig_text = " Extracted ticket signals: " + " | ".join(sig_parts) + "." if sig_parts else ""

    evidence_text = ""
    if evidence:
        evidence_text = " Indexed evidence match: " + " | ".join(evidence) + "."

    action_text = ""
    if action_hints:
        action_text = " Recommended remediation candidates from matched incidents (validate before production use): " + " | ".join(action_hints) + "."
    else:
        action_text = " " + _diagnostic_next_checks(scenario, signals)

    return (
        _diagnostic_summary(scenario)
        + f"{sig_text}{evidence_text}{action_text} "
        + "If unresolved, capture the first failing runtime correlation id, stack frame, or adapter log entry for narrower ranking."
    )


# Function: _extract_pattern_hints_from_chunks
def _extract_pattern_hints_from_chunks(chunks: List[tuple], q_terms: set[str], limit: int = 2) -> List[str]:
    pattern_candidates: List[tuple[float, str]] = []
    seen_hints: set[str] = set()
    for doc, score in chunks:
        content = doc.page_content or ""
        m = re.search(r"(?im)short\s*description\s*[:\-]\s*([^\n]{10,220})", content)
        if not m:
            m = re.search(r"(?im)description\s*[:\-]\s*([^\n]{10,220})", content)
        if not m:
            continue
        hint = _sanitize_hint_text(" ".join(m.group(1).split()).strip())
        if hint and hint.lower() not in seen_hints:
            seen_hints.add(hint.lower())
            total = (max(0.05, float(score)) * 0.8) + (_overlap_score(hint, q_terms) * 0.2)
            pattern_candidates.append((total, hint))

    pattern_candidates.sort(key=lambda x: x[0], reverse=True)
    return [hint for _, hint in pattern_candidates[:limit]]


# Function: _format_predicted_discriminator_text
def _format_predicted_discriminator_text(predicted: Dict[str, str]) -> str:
    if not predicted:
        return ""
    predicted_parts: List[str] = []
    if predicted.get("error_code"):
        predicted_parts.append(f"error code={predicted['error_code']}")
    if predicted.get("stack_token"):
        predicted_parts.append(f"stack token={predicted['stack_token']}")
    if predicted.get("transaction_code"):
        predicted_parts.append(f"transaction code={predicted['transaction_code']}")
    if not predicted_parts:
        return ""
    return " Predicted discriminator from historical pattern: " + ", ".join(predicted_parts) + "."


# Function: _format_ticket_signals_text
def _format_ticket_signals_text(ticket_signals: Dict[str, List[str]]) -> str:
    ticket_parts: List[str] = []
    if ticket_signals.get("error_codes"):
        ticket_parts.append("error codes=" + ", ".join(ticket_signals["error_codes"][:3]))
    if ticket_signals.get("stack_tokens"):
        ticket_parts.append("stack tokens=" + ", ".join(ticket_signals["stack_tokens"][:3]))
    if ticket_signals.get("transaction_codes"):
        ticket_parts.append("transaction codes=" + ", ".join(ticket_signals["transaction_codes"][:2]))
    if not ticket_parts:
        return ""
    return " Extracted from ticket details: " + " | ".join(ticket_parts) + "."


# Function: _format_recommendation_text
def _format_recommendation_text(predicted: Dict[str, str], action_hints: List[str], ticket_signals: Dict[str, List[str]]) -> str:
    rec_steps: List[str] = []
    if predicted.get("error_code"):
        rec_steps.append(f"search logs for {predicted['error_code']}")
    if predicted.get("stack_token"):
        rec_steps.append(f"capture first stack frame containing {predicted['stack_token']}")
    if predicted.get("transaction_code"):
        rec_steps.append(f"reproduce flow in transaction {predicted['transaction_code']} and capture failing step")
    if rec_steps:
        return " Recommended next checks: " + " | ".join(rec_steps) + "."
    if action_hints:
        return " Recommended next checks: validate the first historical candidate in a controlled run, then compare outcome against related incidents."
    if ticket_signals.get("keywords"):
        return " Recommended next checks: compare the ticket keywords against source incidents with matching symptom phrases before applying any historical fix."
    return ""


# Function: _no_resolution_default
def _no_resolution_default(chunks: List[tuple], question: Optional[str]) -> str:
    if not chunks:
        return (
            "Verified exact fix could not be established from matched incidents. "
            "Provide one discriminator (exact error code, stack trace line, or transaction code) for a tighter match."
        )

    related = _extract_related_incidents(chunks, limit=4, question=question)
    rel_text = f" Related incidents in context: {', '.join(related)}." if related else ""
    predicted = _predict_discriminator_from_history(chunks)
    ticket_signals = _extract_ticket_signals_regex(question)
    q_terms = _query_terms(question)

    pattern_hints = _extract_pattern_hints_from_chunks(chunks, q_terms, limit=2)
    action_hints = _extract_recommendation_candidates(chunks, question=question, limit=3)

    pattern_text = ""
    if pattern_hints:
        pattern_text = " Historical pattern signals: " + " | ".join(pattern_hints) + "."

    action_text = ""
    if action_hints:
        action_text = (
            " Historical resolution candidates from matched incidents (verify before applying): "
            + " | ".join(action_hints)
            + "."
        )

    predicted_text = _format_predicted_discriminator_text(predicted)
    extracted_ticket_text = _format_ticket_signals_text(ticket_signals)
    recommendation_text = _format_recommendation_text(predicted, action_hints, ticket_signals)

    return (
        "Verified exact fix could not be established from matched incidents."
        f"{rel_text}{pattern_text}{action_text}{predicted_text}{extracted_ticket_text}{recommendation_text} "
        "If issue persists, provide one additional discriminator not already in the ticket for a tighter match."
    )


# Function: _build_no_verified_resolution_answer
def _build_no_verified_resolution_answer(chunks: List[tuple], question: Optional[str] = None) -> str:
    profile = _prediction_context_profile(question)

    if profile == "low_specificity":
        return _no_resolution_low_specificity(question)

    if profile == "lifecycle":
        return _no_resolution_lifecycle(question)

    if profile == "diagnostic":
        return _no_resolution_diagnostic(chunks, question)

    return _no_resolution_default(chunks, question)


# Function: _is_no_resolution_answer
def _is_no_resolution_answer(answer: str) -> bool:
    low = (answer or "").strip().lower()
    if not low:
        return True
    markers = (
        "no verified remediation steps were found",
        "knowledge base does not contain a verified resolution",
        "i don't have enough information in the knowledge base",
        "verified fix could not be established from matched incidents",
        "verified exact fix could not be established from matched incidents",
        "no high-specificity diagnostic signals were found in the provided ticket",
        "pattern-matched prediction from indexed incidents indicates a file/resource lock contention scenario",
        "unable to find any incidents that match your specific issue",
        "there are several related incidents with similar descriptions",
        "no verified resolution is available for the provided incident number",
        "no verified resolution found in the retrieved incidents",
        "no verified resolution steps are available in the retrieved incidents",
    )
    return any(m in low for m in markers)


# Function: _confidence_for_answer
def _confidence_for_answer(answer: str, top_score: float, has_context: bool) -> float:
    """
    Calibrate confidence score.

    For resolved answers  → top reranker score (reflects true match quality).
    For no-resolution answers → scaled score capped at 0.65 (the system DID find
    relevant context; it just lacks an explicit verified fix step, which is an
    answer-quality issue, not a retrieval-quality issue).
    """
    if not has_context:
        return 0.0

    if _is_no_resolution_answer(answer):
        if "no high-specificity diagnostic signals were found" in (answer or "").lower():
            return round(min(0.25, max(0.05, top_score * 0.35)), 4)
        if "pattern-matched prediction from indexed incidents indicates" in (answer or "").lower():
            return round(min(0.58, max(0.20, top_score * 0.60)), 4)
        # Map reranker score 0-1 → confidence 10-65%.
        # A top_score of 0.7 now yields ~0.50 instead of the old 0.29 cap.
        return round(min(0.45, max(0.08, top_score * 0.52)), 4)

    return round(min(0.99, top_score), 4)


# Function: _retrieve_parallel
def _dedupe_and_enrich_expanded_queries(
    expanded_queries: list[str],
    query_signals: Optional[Dict[str, List[str]]],
    retrieval_base_query: str,
) -> tuple[list[str], Optional[str]]:
    # _expand_queries can emit near-duplicates; keep first occurrence only.
    deduped_queries: list[str] = []
    seen_queries: set[str] = set()
    for query in expanded_queries:
        key = (query or "").strip().lower()
        if not key or key in seen_queries:
            continue
        seen_queries.add(key)
        deduped_queries.append(query)
    expanded_queries = deduped_queries
    expanded_query_lowers = {q.lower() for q in expanded_queries}
    boosted = None
    if query_signals:
        boosted = _enrich_query_with_signals(retrieval_base_query, query_signals)
        if boosted and boosted.lower() not in expanded_query_lowers:
            expanded_queries.append(boosted)
            expanded_query_lowers.add(boosted.lower())
    return expanded_queries, boosted


# Function: _try_fast_keyword_path
def _try_fast_keyword_path(
    question: str,
    query_entities: dict,
    query_signals: Optional[Dict[str, List[str]]],
    boosted: Optional[str],
    retrieval_base_query: str,
    llm_provider: str,
) -> Optional[list]:
    # Fast path for short free-text Send queries: keyword/regex first.
    # This avoids waiting on semantic embedding when a grounded lexical match already exists.
    short_query = len((question or "").strip()) <= 180
    if not (short_query and not query_entities):
        return None

    results: list = []
    existing_texts: set = set()
    keyword_query = boosted if query_signals else retrieval_base_query
    try:
        for kw_doc, kw_score in keyword_search(keyword_query, llm_provider):
            if kw_doc.page_content not in existing_texts:
                results.append((kw_doc, kw_score))
                existing_texts.add(kw_doc.page_content)

        if bool(getattr(cfg, "RAG_ENABLE_REGEX_LAYER", True)):
            for rx_doc, rx_score in regex_signal_search(keyword_query, llm_provider, 8):
                if rx_doc.page_content not in existing_texts:
                    results.append((rx_doc, rx_score))
                    existing_texts.add(rx_doc.page_content)

        if results:
            return results
    except Exception:
        # Fall through to semantic path if fast path errors.
        pass
    return None


# Function: _merge_into_results
def _merge_into_results(pairs, results: list, existing_texts: set) -> None:
    for doc, score in pairs:
        if doc.page_content not in existing_texts:
            results.append((doc, score))
            existing_texts.add(doc.page_content)


# Function: _run_full_parallel_retrieval
def _run_full_parallel_retrieval(
    query_entities: dict,
    expanded_queries: list[str],
    query_signals: Optional[Dict[str, List[str]]],
    boosted: Optional[str],
    retrieval_base_query: str,
    llm_provider: str,
) -> list:
    results: list = []
    existing_texts: set = set()

    with ThreadPoolExecutor(max_workers=min(4, 2 + len(expanded_queries))) as pool:
        # Layer 0: exact metadata lookup (INC number / SolManID)
        future_meta = (
            pool.submit(metadata_search, query_entities, llm_provider)
            if query_entities else None
        )
        # Layer 1: vector similarity — one future per expanded query angle
        futures_sem = [pool.submit(similarity_search, q, llm_provider) for q in expanded_queries]
        # Layer 2: keyword / SAP-entity search on base query
        keyword_query = boosted if query_signals else retrieval_base_query
        future_kw = pool.submit(keyword_search, keyword_query, llm_provider)
        future_rx = pool.submit(regex_signal_search, keyword_query, llm_provider, 8)

        if future_meta is not None:
            meta_results = future_meta.result()
            if meta_results:
                logger.info(
                    "Layer 0 metadata search: %d exact-match results for entities %s",
                    len(meta_results), query_entities,
                )
            _merge_into_results(meta_results, results, existing_texts)

        for future_sem in futures_sem:
            _merge_into_results(future_sem.result(), results, existing_texts)

        _merge_into_results(future_kw.result(), results, existing_texts)
        _merge_into_results(future_rx.result(), results, existing_texts)

    return results


# Function: _retrieve_parallel
def _retrieve_parallel(
    question: str,
    query_entities: dict,
    llm_provider: str,
    query_signals: Optional[Dict[str, List[str]]] = None,
) -> list:
    """Layers 0-2: parallel metadata + multi-angle vector + keyword retrieval. Returns deduplicated list."""
    # Expand the query into multiple focused sub-queries for better recall.
    # Each angle gets its own similarity_search call; results are merged and deduped.
    retrieval_base_query = _prepare_retrieval_query(question)
    expanded_queries = _expand_queries(question)
    expanded_queries, boosted = _dedupe_and_enrich_expanded_queries(
        expanded_queries, query_signals, retrieval_base_query
    )
    # Keep latency predictable for short prompts: fewer semantic query angles.
    if len(question or "") < 260:
        expanded_queries = expanded_queries[:3]
    logger.info("Query expansion: %d angles → %s", len(expanded_queries),
                [q[:60] for q in expanded_queries])

    fast_results = _try_fast_keyword_path(
        question, query_entities, query_signals, boosted, retrieval_base_query, llm_provider
    )
    if fast_results:
        return fast_results

    return _run_full_parallel_retrieval(
        query_entities, expanded_queries, query_signals, boosted, retrieval_base_query, llm_provider
    )


# Function: _augment_solution_chunks
def _augment_solution_chunks(results: list, llm_provider: str) -> list:
    """Layer 3: add sibling solution chunks from already-matched sources."""
    existing_texts: set = {doc.page_content for doc, _ in results}
    matched_sources = list({doc.metadata.get("source", "") for doc, _ in results[:8]})
    for sdoc in fetch_solution_chunks(matched_sources, provider=llm_provider):
        if sdoc.page_content not in existing_texts:
            results.append((sdoc, 0.9))
            existing_texts.add(sdoc.page_content)
    return results


# Function: _rag_direct_answer
def _rag_direct_answer(
    question: str,
    top_solution: str,
    top_doc: Any,
    reranked: list,
    llm_provider: str,
) -> Dict[str, Any]:
    """Layer 5a: direct-answer short-circuit when top chunk has an explicit solution."""
    from backend.llm.router import get_llm

    issue_match = re.search(
        r'(?:Issue|Problem|Description)\s*[:\-\.]\s*(.+?)(?=\n(?:Solution|Resolution|Analysis|$)|\Z)',
        top_doc.page_content,
        re.IGNORECASE | re.DOTALL,
    )
    root_cause  = issue_match.group(1).strip() if issue_match else "See document for details."
    source_name = top_doc.metadata.get("source", "knowledge base")

    prompt_text = DIRECT_ANSWER_PROMPT.format(
        direct_answer=top_solution, root_cause=root_cause, source=source_name,
    )
    logger.info("Direct-answer short-circuit activated — source: %s", source_name)
    llm      = get_llm(llm_provider)
    response = llm.invoke([("system", prompt_text), ("human", question)])
    answer   = _validate_answer(
        response.content if hasattr(response, "content") else str(response),
        reranked,
        question,
    )
    if answer == NO_CONTEXT_RESPONSE:
        return {
            "answer": answer,
            "sources": [],
            "confidence": 0.0,
            "context_used": False,
        }
    top_score = reranked[0][1] if reranked else 0.0
    return {
        "answer": answer,
        "sources": _build_sources(reranked),
        "confidence": _confidence_for_answer(answer, top_score, has_context=True),
        "context_used": True,
    }


# Function: _rag_full_context_search
def _rag_full_context_search(
    question: str,
    reranked: list,
    chat_history: Optional[List[Dict[str, str]]],
    llm_provider: str,
) -> Dict[str, Any]:
    """Layer 5b: full context search when no direct solution is found."""
    from backend.llm.router import get_llm

    regex_block   = _extract_solution_text(reranked)
    chunk_context = _format_context(reranked)
    context_text  = (regex_block + "\n\n" + chunk_context) if regex_block else chunk_context

    top_score = reranked[0][1] if reranked else 0.0
    avg_score = (sum(float(s) for _, s in reranked) / len(reranked)) if reranked else 0.0

    # Only skip LLM when evidence is truly absent or extremely weak.
    if (not regex_block) and (top_score < 0.18 or avg_score < 0.08):
        fallback_answer = _build_no_verified_resolution_answer(reranked, question=question)
        return {
            "answer": fallback_answer,
            "sources": _build_sources(reranked),
            "confidence": _confidence_for_answer(fallback_answer, top_score, has_context=bool(reranked)),
            "context_used": bool(reranked),
        }

    # Only short-circuit to extractive fallback when there are truly no relevant chunks.
    if not reranked or (not regex_block and top_score < 0.10):
        fallback_answer = _build_no_verified_resolution_answer(reranked, question=question)
        return {
            "answer": fallback_answer,
            "sources": _build_sources(reranked),
            "confidence": _confidence_for_answer(fallback_answer, top_score, has_context=bool(reranked)),
            "context_used": bool(reranked),
        }

    messages: List[Any] = [("system", SEARCH_PROMPT.format(context=context_text))]
    trimmed_history = _trim_chat_history_for_prompt(chat_history, question)
    if trimmed_history:
        for turn in trimmed_history[-6:]:
            messages.append((turn["role"], turn["content"]))
    messages.append(("human", question))

    llm      = get_llm(llm_provider)
    response = llm.invoke(messages)
    answer   = _validate_answer(
        response.content if hasattr(response, "content") else str(response),
        reranked,
        question,
    )
    if answer == NO_CONTEXT_RESPONSE:
        fallback_answer = _build_no_verified_resolution_answer(reranked, question=question)
        return {
            "answer": fallback_answer,
            "sources": _build_sources(reranked),
            "confidence": _confidence_for_answer(fallback_answer, top_score, has_context=bool(reranked)),
            "context_used": bool(reranked),
        }
    return {
        "answer": answer,
        "sources": _build_sources(reranked),
        "confidence": _confidence_for_answer(answer, top_score, has_context=True),
        "context_used": True,
    }


# Function: query_rag
def _bound_and_rerank_results(results: list, enriched_query: str) -> tuple[list, list]:
    # Bound reranker cost: cross-encoder is the slowest step in the Send path.
    # Keep only strongest candidates before reranking.
    if len(results) > 36:
        results = sorted(results, key=lambda item: float(item[1]), reverse=True)[:36]

    sorted_results = sorted(results, key=lambda item: float(item[1]), reverse=True)
    top_raw = float(sorted_results[0][1]) if sorted_results else 0.0
    fast_semantic_mode = top_raw >= 0.72 and len(sorted_results) <= 12

    if bool(getattr(cfg, "RAG_ENABLE_RERANK", True)) and not fast_semantic_mode:
        reranked = _rerank(enriched_query, sorted_results)
    else:
        reranked = sorted_results[:TOP_CONTEXT_CHUNKS]
    return results, reranked


# Function: _strict_evidence_gate_response
def _strict_evidence_gate_response(
    reranked: list, question: Optional[str], top_score: float, avg_score: float
) -> Optional[Dict[str, Any]]:
    # Strict evidence gate: if retrieval quality is weak, return safe fallback.
    if top_score >= cfg.STRICT_MIN_TOP_SCORE and avg_score >= cfg.STRICT_MIN_AVG_SCORE:
        return None
    logger.warning(
        "Strict gate blocked answer: top_score=%.4f avg_score=%.4f thresholds=(%.2f, %.2f)",
        top_score,
        avg_score,
        cfg.STRICT_MIN_TOP_SCORE,
        cfg.STRICT_MIN_AVG_SCORE,
    )
    fallback_answer = _build_no_verified_resolution_answer(reranked, question=question)
    return {
        "answer": fallback_answer,
        "sources": _build_sources(reranked),
        "confidence": _confidence_for_answer(fallback_answer, top_score, has_context=bool(reranked)),
        "context_used": bool(reranked),
    }


# Function: _weak_evidence_fallback_response
def _weak_evidence_fallback_response(
    reranked: list, question: Optional[str], top_score: float, avg_score: float
) -> Optional[Dict[str, Any]]:
    # Lowered threshold: only short-circuit to extractive fallback when evidence is very weak
    # (below 0.28/0.12). For mid-confidence results, always invoke Ollama GPU LLM to refine.
    if not (top_score < 0.28 and avg_score < 0.12):
        return None
    fallback_answer = _build_no_verified_resolution_answer(reranked, question=question)
    return {
        "answer": fallback_answer,
        "sources": _build_sources(reranked),
        "confidence": _confidence_for_answer(fallback_answer, top_score, has_context=bool(reranked)),
        "context_used": bool(reranked),
    }


# Function: query_rag
def query_rag(
    question: str,
    llm_provider: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """
    Full RAG pipeline — 4 retrieval layers + rerank + extract + validate:

      Layer 0: Exact metadata lookup   — INC / SolManID / delivery number
      Layer 1: Vector similarity       — semantic embedding search
      Layer 2: Keyword / SAP-entity    — BM25-style text-match search
      Layer 3: Solution-chunk sibling  — fetch missing resolution chunks
      → FlashrankRerank → top-N
      → Regex-first extraction         — solution text before LLM sees it
      → Direct-answer short-circuit    — LLM formats, not discovers
      → Rule-based answer validation   — block hallucinated IDs
    """
    t0 = time.perf_counter()

    retrieval_query = _prepare_retrieval_query(question)
    query_signals = _extract_ticket_signals_ml(question, llm_provider)
    enriched_query = _enrich_query_with_signals(retrieval_query, query_signals)
    query_entities = _extract_query_entities(enriched_query)
    t_signals = time.perf_counter()

    results = _retrieve_parallel(retrieval_query, query_entities, llm_provider, query_signals=query_signals)
    t_retrieve = time.perf_counter()

    if not results:
        return {"answer": NO_CONTEXT_RESPONSE, "sources": [], "confidence": 0.0, "context_used": False}

    if bool(getattr(cfg, "RAG_ENABLE_AUGMENT_LAYER", False)):
        results = _augment_solution_chunks(results, llm_provider)
    t_augment = time.perf_counter()

    results, reranked = _bound_and_rerank_results(results, enriched_query)
    t_rerank = time.perf_counter()
    logger.info("Retrieval: %d candidates → reranked to %d chunks for LLM", len(results), len(reranked))
    logger.info(
        "RAG stage timings (ms): signals=%.1f retrieve=%.1f augment=%.1f rerank=%.1f total_pre_llm=%.1f",
        (t_signals - t0) * 1000,
        (t_retrieve - t_signals) * 1000,
        (t_augment - t_retrieve) * 1000,
        (t_rerank - t_augment) * 1000,
        (t_rerank - t0) * 1000,
    )

    top_score = reranked[0][1] if reranked else 0.0
    avg_score = (sum(score for _, score in reranked) / len(reranked)) if reranked else 0.0

    gate_response = _strict_evidence_gate_response(reranked, question, top_score, avg_score)
    if gate_response is not None:
        return gate_response

    top_solution = _get_top_solution(reranked)
    top_doc      = reranked[0][0] if reranked else None

    if top_solution and top_doc:
        return _rag_direct_answer(question, top_solution, top_doc, reranked, llm_provider)

    weak_response = _weak_evidence_fallback_response(reranked, question, top_score, avg_score)
    if weak_response is not None:
        return weak_response

    # Always invoke the full Ollama LLM context search when chunks are available.
    # RAG_DIRECT_EXTRACTIVE_MODE is checked inside _rag_full_context_search only as an
    # optimisation hint; if no explicit solution label is found, LLM synthesis runs anyway.
    return _rag_full_context_search(question, reranked, chat_history, llm_provider)


