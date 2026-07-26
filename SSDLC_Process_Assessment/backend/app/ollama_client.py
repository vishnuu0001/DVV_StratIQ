# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — backend/app (ollama_client.py)
# Date: 2026-04-23
# ---------------------------------------------------------------------------
from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx

DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
DEFAULT_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "90"))


# Function: ollama_settings
def ollama_settings() -> dict[str, Any]:
    return {
        "base_url": DEFAULT_BASE_URL,
        "default_model": DEFAULT_MODEL,
        "num_gpu": os.getenv("OLLAMA_NUM_GPU", "-1"),
    }


# Function: list_models
def list_models() -> dict[str, Any]:
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{DEFAULT_BASE_URL.rstrip('/')}/api/tags")
            response.raise_for_status()
        payload = response.json()
        return {"available": True, "models": payload.get("models", [])}
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "models": [], "error": str(exc)}


MATURITY_ORDER = ["Early", "Emerging", "Mature", "Fully Mature"]


# Function: _progression_block
def _progression_block(options: dict[str, Any], selected: str | None) -> str:
    if not selected or selected not in MATURITY_ORDER:
        return ""
    current_idx = MATURITY_ORDER.index(selected)
    if current_idx >= len(MATURITY_ORDER) - 1:
        return ""
    lines = []
    for level in MATURITY_ORDER[current_idx + 1 :]:
        desc = (options.get(level) or {}).get("description", "")
        if desc:
            lines.append(f"  {level}: {desc}")
    return ("\nMaturity progression to Fully Mature:\n" + "\n".join(lines) + "\n") if lines else ""


SYSTEM_COMBINED = (
    "You are an SSDLC security expert performing a maturity gap assessment. "
    "When given an assessment context, respond with EXACTLY this format and nothing else:\n"
    "WEIGHT: [integer 1-10]\n"
    "ACTIONS:\n"
    "1. [first corrective action]\n"
    "2. [second corrective action]\n"
    "3. [third corrective action]\n"
    "4. [optional fourth action]\n\n"
    "Weight scoring: Security/Compliance/Audit/Vendor dimension=base 10, "
    "Architecture/DevSecOps/Operational=base 7, Governance/Ownership=base 6, all others=base 5. "
    "Multiply by maturity factor: Early×0.50, Emerging×0.65, Mature×0.82, Fully Mature×1.00. "
    "Round to nearest integer, minimum 1, maximum 10. "
    "Actions must advance the control toward Fully Mature with specific tools, processes, roles, or measurable outcomes. "
    "Do not add any text outside this format."
)

_WEIGHT_RE = re.compile(r"WEIGHT\s*:\s*(\d+)", re.IGNORECASE)
_ACTIONS_RE = re.compile(r"ACTIONS\s*:\s*\n(.*)", re.IGNORECASE | re.DOTALL)


# Function: build_combined_prompt
def build_combined_prompt(row: dict[str, Any]) -> str:
    options = {option["key"]: option for option in row.get("maturityOptions", [])}
    selected = row.get("selectedLevelKey")
    current_state_text = (row.get("currentState") or "").strip()
    evidence = (row.get("evidence") or "").strip() or "No evidence yet."
    score = row.get("score") or ""
    progression = _progression_block(options, selected)
    return (
        f"Application: {row.get('applicationName') or 'Unknown'}\n"
        f"Dimension: {row.get('dimension')}\n"
        f"Phase: {row.get('phase')}\n"
        f"Question: {row.get('question')}\n"
        f"Current State: {current_state_text or 'Not specified'}\n"
        f"Maturity Level: {selected} ({score}/4)\n"
        f"Description: {options.get(selected, {}).get('description', 'N/A')}\n"
        f"Evidence: {evidence}\n"
        f"{progression}"
        f"\nAssess the WEIGHT (1-10) for this control and list corrective ACTIONS "
        f"to advance from {selected} to Fully Mature."
    )


# Function: _parse_combined_response
def _parse_combined_response(text: str) -> tuple[int | None, str]:
    weight: int | None = None
    weight_match = _WEIGHT_RE.search(text)
    if weight_match:
        try:
            weight = max(1, min(10, int(weight_match.group(1))))
        except ValueError:
            weight = None

    actions_match = _ACTIONS_RE.search(text)
    if actions_match:
        recommendation = actions_match.group(1).strip()
    else:
        recommendation = _WEIGHT_RE.sub("", text).strip()

    return weight, recommendation


# Function: generate_weighted_prediction
def generate_weighted_prediction(row: dict[str, Any], requested_model: str | None = None) -> dict[str, Any]:
    """Return LLM-derived weight and recommendation. No heuristic fallback — Ollama only."""
    model = requested_model or DEFAULT_MODEL

    if not row.get("selectedLevelKey"):
        return {"weight": None, "recommendation": "", "source": None, "model": None}

    payload = {
        "model": model,
        "system": SYSTEM_COMBINED,
        "prompt": build_combined_prompt(row),
        "stream": False,
        "options": {
            "temperature": 0.15,
            "num_ctx": 2048,
            "num_predict": 500,
            "num_gpu": int(os.getenv("OLLAMA_NUM_GPU", "-1")),
        },
    }
    try:
        with httpx.Client(timeout=DEFAULT_TIMEOUT_SECONDS) as client:
            response = client.post(f"{DEFAULT_BASE_URL.rstrip('/')}/api/generate", json=payload)
            response.raise_for_status()
        text = response.json().get("response", "").strip()
        if text:
            weight, recommendation = _parse_combined_response(text)
            return {
                "weight": weight,
                "recommendation": recommendation,
                "source": "ollama",
                "model": model,
            }
    except Exception:  # noqa: BLE001
        pass

    return {"weight": None, "recommendation": "", "source": None, "model": None}


# Function: generate_recommendation
def generate_recommendation(row: dict[str, Any], requested_model: str | None = None) -> dict[str, Any]:
    """Legacy adapter used by generate_recommendations endpoint — delegates to generate_weighted_prediction."""
    result = generate_weighted_prediction(row, requested_model=requested_model)
    return {"text": result["recommendation"], "source": result["source"], "model": result["model"]}


# ── Executive Dashboard ────────────────────────────────────────────────────────

SYSTEM_EXECUTIVE = (
    "You are a Chief Information Security Officer (CISO) preparing an executive briefing on SSDLC maturity. "
    "When given assessment data, respond with EXACTLY this structure and nothing else:\n\n"
    "EXECUTIVE SUMMARY:\n[2-3 sentences on overall security posture citing actual scores and levels]\n\n"
    "KEY RISKS:\n1. [specific risk with tower/dimension reference and score]\n"
    "2. [specific risk]\n3. [specific risk]\n\n"
    "PRIORITY ACTIONS:\n1. [concrete action — owner role, 30/60/90-day timeline]\n"
    "2. [action]\n3. [action]\n\n"
    "STRATEGIC RECOMMENDATIONS:\n[2-3 sentences on roadmap to reach target maturity]\n\n"
    "Cite actual percentages and tower/dimension names. Use executive language. No markdown formatting."
)


# Function: build_executive_prompt
def build_executive_prompt(dashboard: dict[str, Any]) -> str:
    cards = dashboard.get("cards") or []
    portfolio = dashboard.get("portfolio") or {}
    dim_matrix = dashboard.get("dimensionMatrix") or []
    target = dashboard.get("targetPct", 80)

    lines = [
        f"Portfolio Score: {portfolio.get('overallScorePct', 'N/A')}%  "
        f"Level: {portfolio.get('overallLevel', 'N/A')}  "
        f"Target: {target}%  "
        f"Towers Assessed: {portfolio.get('assessedTowers', 0)}/{portfolio.get('towerCount', 0)}",
        "",
        "Tower Scores:",
    ]
    for c in cards:
        score = c.get("overallScorePct")
        lines.append(
            f"  {c.get('name', '?')}: {score}%  Level={c.get('overallLevel', '?')}  "
            f"Answered={c.get('answered', 0)}/{c.get('totalQuestions', 0)}  "
            f"Gap={c.get('gapToTarget', '?')}%  TopConcern={c.get('topConcern', '?')}"
        )

    lines += ["", "Dimension Scores (tower breakdown):"]
    for dim_row in dim_matrix:
        dim = dim_row.get("dimension", "")
        parts = []
        for t_key, t_data in (dim_row.get("towers") or {}).items():
            s = t_data.get("scorePct")
            if s is not None:
                name = next((c.get("name", t_key) for c in cards if c.get("key") == t_key), t_key)
                parts.append(f"{name}={s}%")
        if parts:
            lines.append(f"  {dim}: {', '.join(parts)}")

    return "\n".join(lines)


# Function: stream_executive_summary
def stream_executive_summary(dashboard: dict[str, Any], requested_model: str | None = None):
    """Blocking generator — yields raw text tokens from Ollama streaming API."""
    model = requested_model or DEFAULT_MODEL
    payload = {
        "model": model,
        "system": SYSTEM_EXECUTIVE,
        "prompt": build_executive_prompt(dashboard),
        "stream": True,
        "options": {
            "temperature": 0.2,
            "num_ctx": 3000,
            "num_predict": 700,
            "num_gpu": int(os.getenv("OLLAMA_NUM_GPU", "-1")),
        },
    }
    try:
        with httpx.Client(timeout=DEFAULT_TIMEOUT_SECONDS) as client:
            with client.stream("POST", f"{DEFAULT_BASE_URL.rstrip('/')}/api/generate", json=payload) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if line:
                        data = json.loads(line)
                        token = data.get("response", "")
                        if token:
                            yield token
                        if data.get("done"):
                            break
    except Exception:  # noqa: BLE001
        return
