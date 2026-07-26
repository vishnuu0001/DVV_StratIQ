# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §6.3: 'redact PII before persisting (run a Presidio pass ... and store an
#   entity map, not raw values, for anything classified as PII).' Used only by
#   llm/metering.py's PERSIST_LLM_IO path — the source corpus itself (chunk.text) is
#   never touched here, since P1 citations must remain byte-for-byte verbatim against
#   the original document.
# Date: 2026-07-24
# ---------------------------------------------------------------------------
"""Presidio needs a spaCy NLP model that isn't guaranteed to be installed on every box
this runs on (it's a separate `python -m spacy download <model>` step, not something
`pip install` pulls in). Degrades the same way indexing/retriever.py's cross-encoder
reranker does: lazy-load the engines once, and if that fails for any reason, fail
CLOSED — return None so the caller skips persistence entirely rather than ever writing
an unredacted prompt/completion to the audit trail."""
from __future__ import annotations

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# A representative subset of Presidio's built-in recognizers — the entity types most
# likely to appear in client SOWs/incident text/BRDs (names, contact details, financial
# and government identifiers). Not exhaustive; Presidio's full default recognizer set
# can be enabled by dropping the `entities=` filter below if a deployment wants it.
_ENTITIES = [
    "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "IBAN_CODE",
    "US_SSN", "US_BANK_NUMBER", "IP_ADDRESS", "LOCATION",
]


# Function: _get_engines
@lru_cache(maxsize=1)
def _get_engines():
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    return AnalyzerEngine(), AnonymizerEngine()


# Function: redact_pii
def redact_pii(text: str) -> tuple[str, dict] | None:
    """Returns (redacted_text, entity_map) where entity_map is {entity_type: [values]}
    for every PII span Presidio found (the *values*, not their positions — this is an
    audit record of what was present, not a reversible mapping). Returns None if
    redaction isn't available or fails; callers MUST treat None as 'do not persist',
    never as 'persist the original text unredacted'."""
    if not text:
        return "", {}
    try:
        analyzer, anonymizer = _get_engines()
    except Exception:  # noqa: BLE001 — presidio/spaCy model not installed on this box
        logger.warning("PII redaction unavailable (presidio/spaCy model not installed) — skipping LLM I/O persistence.")
        return None

    try:
        findings = analyzer.analyze(text=text, entities=_ENTITIES, language="en")
        if not findings:
            return text, {}
        entity_map: dict[str, list[str]] = {}
        for finding in findings:
            entity_map.setdefault(finding.entity_type, []).append(text[finding.start:finding.end])
        anonymized = anonymizer.anonymize(text=text, analyzer_results=findings)
        return anonymized.text, entity_map
    except Exception:  # noqa: BLE001 — a redaction failure must never fall back to raw text
        logger.exception("PII redaction failed — skipping LLM I/O persistence.")
        return None
