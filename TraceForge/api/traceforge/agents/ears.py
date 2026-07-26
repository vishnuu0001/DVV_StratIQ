# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §5 Agent 1 — the six EARS patterns, verbatim from Requirements.MD, used both in the
# Date: 2025-08-31
# ---------------------------------------------------------------------------
"""§5 Agent 1 — the six EARS patterns, verbatim from Requirements.MD, used both in the
extractor's system prompt and as the valid-pattern set the ambiguity scorer checks against."""
from __future__ import annotations

EARS_PATTERNS: dict[str, str] = {
    "UBIQUITOUS": "The <system> shall <response>.",
    "EVENT_DRIVEN": "When <trigger>, the <system> shall <response>.",
    "STATE_DRIVEN": "While <state>, the <system> shall <response>.",
    "OPTIONAL_FEATURE": "Where <feature is included>, the <system> shall <response>.",
    "UNWANTED_BEHAVIOUR": "If <unwanted condition>, then the <system> shall <response>.",
    "COMPLEX": "Combination of the above (e.g. 'While <state>, when <trigger>, the <system> shall <response>.')",
}

EARS_REFERENCE = "\n".join(f"- {name}: {template}" for name, template in EARS_PATTERNS.items())
