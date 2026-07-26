# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §5 Agent 1 ambiguity scoring rubric — 'implement as a deterministic post-processor,
# Date: 2026-03-24
# ---------------------------------------------------------------------------
"""§5 Agent 1 ambiguity scoring rubric — 'implement as a deterministic post-processor,
NOT as an LLM judgement — LLM scores are not reproducible and clients will challenge
them.' Every rule here is regex/heuristic, verbatim weights from the spec."""
from __future__ import annotations

import re
from dataclasses import dataclass

_VAGUE_TERM_RE = re.compile(
    r"\b(fast|quick|efficient|user-friendly|robust|appropriate|adequate|"
    r"sufficient|reasonable|as needed|etc\.?|and/or|minimal|optimal|"
    r"seamless|intuitive|state-of-the-art|flexible|easy)\b",
    re.IGNORECASE,
)
_PASSIVE_VOICE_RE = re.compile(r"\b(is|are|was|were|be|been|being)\s+\w+(ed|en)\b(?!\s+by\b)", re.IGNORECASE)
_COMPARATIVE_RE = re.compile(r"\b(faster|quicker|slower|more|less|better|worse|higher|lower|greater|smaller)\b", re.IGNORECASE)
_NUMERIC_TARGET_RE = re.compile(r"\d")
_UNTESTABLE_VERB_RE = re.compile(r"\b(support|handle|manage|process|enable|facilitate|deal with)\b", re.IGNORECASE)


@dataclass
class AmbiguityFlag:
    code: str
    span: str
    explanation: str
    suggestion: str


# (code, weight, explanation, suggestion)
_RULES = [
    ("VAGUE_TERM", 0.15, "Contains a subjective/unquantified adjective that different readers will interpret differently.",
     "Replace with a measurable target (e.g. 'within 2 seconds' instead of 'fast')."),
    ("PASSIVE_VOICE", 0.10, "Passive voice hides who/what performs the action, which EARS requires to be explicit.",
     "Rewrite in active voice naming the system as the actor."),
    ("NO_ACTOR", 0.20, "No <system> noun could be resolved for this requirement.",
     "Name the specific system/component responsible for this behaviour."),
    ("UNQUANTIFIED", 0.20, "Contains a comparative with no numeric target.",
     "Add a specific number, percentage, or threshold."),
    ("COMPOUND", 0.15, "The response clause contains 'and'/'or', so this requirement is not atomic.",
     "Split into separate requirements, one per response."),
    ("UNTESTABLE", 0.25, "Uses a vague verb ('support'/'handle'/'manage'/'process') with no observable, measurable outcome.",
     "State the specific, observable system behaviour and its measurable result."),
    ("DANGLING_REF", 0.15, "References a term that appears unresolved or unspecified in the source material.",
     "Confirm and name the specific document/system/term, or remove the reference."),
    ("NON_CONFORMANT", 0.30, "Does not fit any of the six EARS patterns.",
     "Rewrite using one of: Ubiquitous / Event-driven / State-driven / Optional feature / Unwanted behaviour / Complex."),
]
_WEIGHTS = {code: weight for code, weight, _, _ in _RULES}
_EXPLANATIONS = {code: (explanation, suggestion) for code, _, explanation, suggestion in _RULES}


# Levels that describe external facts/dependencies rather than system behaviour — they
# can never legitimately have a <system> actor or fit an EARS pattern, so holding them to
# NO_ACTOR/NON_CONFORMANT would flag every single one by construction, not because it's
# actually ambiguous. See §"8. Assumptions & Dependencies" in the BRD section map, which
# already renders these as plain prose bullets rather than EARS-style requirement rows.
_NON_EARS_LEVELS = {"ASSUMPTION", "CONSTRAINT"}


# Function: score_requirement
def score_requirement(
    statement: str, ears_parts: dict, ears_pattern: str | None, level: str | None = None,
) -> tuple[float, list[AmbiguityFlag]]:
    """Returns (ambiguity_score in [0,1], fired flags). Mirrors AMBIGUITY_RULES in
    Requirements.MD §5 exactly — do not turn this into an LLM call (see docstring)."""
    flags: list[AmbiguityFlag] = []
    response_clause = str((ears_parts or {}).get("system_response") or statement)
    is_non_ears_level = level in _NON_EARS_LEVELS

    if match := _VAGUE_TERM_RE.search(statement):
        flags.append(_flag("VAGUE_TERM", match.group(0)))

    if match := _PASSIVE_VOICE_RE.search(statement):
        flags.append(_flag("PASSIVE_VOICE", match.group(0)))

    if not is_non_ears_level and not (ears_parts or {}).get("system_name"):
        flags.append(_flag("NO_ACTOR", statement[:60]))

    if (match := _COMPARATIVE_RE.search(statement)) and not _NUMERIC_TARGET_RE.search(statement):
        flags.append(_flag("UNQUANTIFIED", match.group(0)))

    if re.search(r"\b(and|or)\b", response_clause, re.IGNORECASE):
        flags.append(_flag("COMPOUND", response_clause[:60]))

    if (match := _UNTESTABLE_VERB_RE.search(response_clause)) and not _NUMERIC_TARGET_RE.search(response_clause) and '"' not in response_clause:
        flags.append(_flag("UNTESTABLE", match.group(0)))

    if re.search(r"\b(TBD|TBC|unspecified|\[.*?\])\b", statement, re.IGNORECASE):
        flags.append(_flag("DANGLING_REF", statement[:60]))

    valid_patterns = {"UBIQUITOUS", "EVENT_DRIVEN", "STATE_DRIVEN", "OPTIONAL_FEATURE", "UNWANTED_BEHAVIOUR", "COMPLEX"}
    if not is_non_ears_level and ears_pattern not in valid_patterns:
        flags.append(_flag("NON_CONFORMANT", statement[:60]))

    score = min(1.0, sum(_WEIGHTS[f.code] for f in flags))
    return score, flags


# Function: _flag
def _flag(code: str, span: str) -> AmbiguityFlag:
    explanation, suggestion = _EXPLANATIONS[code]
    return AmbiguityFlag(code=code, span=span, explanation=explanation, suggestion=suggestion)
