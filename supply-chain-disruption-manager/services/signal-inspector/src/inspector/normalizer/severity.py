# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Stage 4: Severity evaluation from YAML rules.
# Date: 2026-04-04
# ---------------------------------------------------------------------------
"""Stage 4: Severity evaluation from YAML rules."""

from __future__ import annotations

import operator
from pathlib import Path
from typing import Any

import structlog
import yaml

from inspector.config import get_settings
from inspector.envelope import SeverityLevel

logger = structlog.get_logger(__name__)

# Type alias for a parsed severity rule
_Condition = dict[str, Any]
_Rule = dict[str, Any]

_rules_cache: list[_Rule] | None = None


# Function: _load_rules
def _load_rules() -> list[_Rule]:
    global _rules_cache
    if _rules_cache is not None:
        return _rules_cache

    settings = get_settings()
    severity_path: Path = settings.config_dir / "severity.yaml"

    with severity_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    _rules_cache = data.get("rules", [])
    logger.info("severity.rules_loaded", count=len(_rules_cache))
    return _rules_cache


_THRESHOLD_OPS = {
    "gte": operator.ge,
    "lte": operator.le,
    "gt": operator.gt,
    "lt": operator.lt,
    "eq": operator.eq,
    "neq": operator.ne,
}


# Function: _check_threshold_ops
def _check_threshold_ops(ops: dict[str, Any], value: Any) -> bool:
    for op, threshold in ops.items():
        try:
            v = float(value)
            t = float(threshold)
        except (TypeError, ValueError):
            return False
        func = _THRESHOLD_OPS.get(op)
        if func is not None and not func(v, t):
            return False
    return True


# Function: _field_condition_matches
def _field_condition_matches(field: str, ops: Any, payload: dict[str, Any]) -> bool:
    value = payload.get(field)
    if value is None:
        return False
    if not isinstance(ops, dict):
        # Exact equality shorthand
        return value == ops
    return _check_threshold_ops(ops, value)


# Function: _evaluate_condition
def _evaluate_condition(condition: _Condition, payload: dict[str, Any]) -> bool:
    """Evaluate a 'when' condition dict against the payload.

    Supported operators: gte, lte, gt, lt, eq, neq.
    All checks in the condition dict must pass (AND semantics).
    """
    for field, ops in condition.items():
        if not _field_condition_matches(field, ops, payload):
            return False
    return True


# Function: evaluate_severity
def evaluate_severity(event_type: str, payload: dict[str, Any]) -> SeverityLevel:
    """Return the first matching severity for the given event_type and payload.

    Falls back to "info" if no rule matches.
    """
    rules = _load_rules()

    for rule in rules:
        if rule.get("event_type") != event_type:
            continue

        conditions: list[_Condition] = rule.get("conditions", [])
        for cond in conditions:
            if "default" in cond:
                return cond["default"]  # type: ignore[return-value]
            when = cond.get("when", {})
            if _evaluate_condition(when, payload):
                return cond["severity"]  # type: ignore[return-value]

        # Rule found but no condition matched — return info
        break

    return "info"


# Function: reload_rules
def reload_rules() -> None:
    """Force reload of severity rules from disk (useful for testing)."""
    global _rules_cache
    _rules_cache = None
    _load_rules()
