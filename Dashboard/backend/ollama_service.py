# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Ollama LLM service for AI-powered ITSM insights generation.
# Date: 2025-11-18
# ---------------------------------------------------------------------------
"""
Ollama LLM service for AI-powered ITSM insights generation.

Uses the local Ollama API (GPU-accelerated) to generate contextual leadership
insights from KPI data. Falls back to rule-based kpis.generate_leadership_insights()
if Ollama is unavailable or misconfigured.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------

_INSIGHT_PROMPT = """\
You are an expert ITSM analyst preparing an executive management dashboard report.
Analyze the ITSM KPI data below and generate concise, data-driven leadership insights.

KPI DATA:
{kpi_json}

INSTRUCTIONS:
- Return ONLY a valid JSON object — no markdown fences, no explanation text.
- The JSON must have exactly 4 keys: "executive", "incidents", "changes", "service_requests"
- Each key maps to a list of 3–5 insight objects: {{"text": "...", "level": "..."}}
- "level" must be one of: "good", "warn", "critical", "info"
- Level logic:
    good     = healthy (SLA ≥ 95%, MTTR < 24h, emergency changes < 5%, backlog < 20%)
    warn     = needs attention (SLA 85–95%, MTTR 24–72h, emergency 5–15%, backlog 20–40%)
    critical = urgent action (SLA < 85%, MTTR > 72h, emergency > 15%, backlog > 40%)
    info     = neutral context or factual statement
- Be specific: include actual metric values in the text.
- executive insights should give a C-suite summary of overall health.
- incidents insights should focus on MTTR, SLA, hotspots.
- changes insights should focus on emergency %, success rate, cycle time.
- service_requests insights should focus on backlog, closure time, top categories.
"""


_AUTOMATION_PREDICTION_PROMPT = """\
You are an enterprise automation architect.
Given ITSM issue categories, predict automation opportunity and practical rollout guidance.

INPUT CANDIDATES (JSON):
{candidate_json}

INSTRUCTIONS:
- Return ONLY valid JSON, no markdown.
- JSON schema:
    {{
        "predictions": [
            {{
                "candidate_id": integer,
                "category": "...",
                "work_type": "Incident|Change|ServiceRequest",
                "llm_opportunity_score": 0-100,
                "llm_confidence": 0-100,
                "llm_automation_type": "Runbook|Workflow|RPA|AIOps|Self-Service|Script|Monitoring|Hybrid",
                "llm_risk_level": "Low|Medium|High",
                "llm_rationale": "short rationale with data references",
                "llm_next_step": "single actionable next step"
            }}
        ]
    }}
- Use category and work-type context; consider volume, repetition, cycle time, and priority.
- Preserve candidate_id exactly from input rows.
- Scores must be numeric.
- Keep rationale concise (max 220 chars).
"""


_AUTOMATION_SINGLE_PREDICTION_PROMPT = """\
You are an enterprise automation architect.
Predict automation opportunity for the single input row.

INPUT (JSON):
{candidate_json}

Return ONLY valid JSON (no markdown) with this schema:
{{
    "candidate_id": integer,
    "category": "...",
    "work_type": "Incident|Change|ServiceRequest",
    "llm_opportunity_score": 0-100,
    "llm_confidence": 0-100,
    "llm_automation_type": "Runbook|Workflow|RPA|AIOps|Self-Service|Script|Monitoring|Hybrid",
    "llm_risk_level": "Low|Medium|High",
    "llm_rationale": "max 220 chars",
    "llm_next_step": "single actionable step"
}}
"""


_PREFERRED_OLLAMA_MODELS = [
    "qwen3.5:9b",
    "qwen2.5:7b",
    "mistral:latest",
    "llama3.1:8b",
    "llama2:latest",
]

# Ollama options tuned for NVIDIA A10-8Q (7 GB VRAM).
# num_ctx=2048  — sufficient for all prompts; halves KV-cache vs the 4096 default.
# num_batch=512 — large prefill batch exploits A10 tensor-core throughput.
# num_gpu=99    — load all layers onto GPU (model fits comfortably at Q4_K_M).
_OLLAMA_GPU_OPTIONS_BASE = {
    "num_ctx": 2048,
    "num_batch": 512,
    "num_gpu": 99,
}


# Function: _build_kpi_summary
def _build_kpi_summary(
    summary: Dict[str, Any],
    incident_data: Dict[str, Any],
    change_data: Dict[str, Any],
    sr_data: Dict[str, Any],
    hotspots: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Build a compact KPI dict for the LLM prompt."""
    return {
        "total_tickets": summary.get("total_tickets", 0),
        "sla_compliance_pct": round(summary.get("sla_compliance_pct", 0), 1),
        "avg_mttr_hours": round(summary.get("avg_mttr_hours", 0), 1),
        "emergency_change_pct": round(summary.get("emergency_change_pct", 0), 1),
        "incident_total": incident_data.get("summary", {}).get("total_incidents", 0),
        "incident_sla_pct": round(incident_data.get("summary", {}).get("incident_sla_pct", 0), 1),
        "incident_avg_mttr_hours": round(incident_data.get("cycle_time", {}).get("avg", 0), 1),
        "incident_p90_mttr_hours": round(incident_data.get("cycle_time", {}).get("p90", 0), 1),
        "top_hotspot_app": hotspots[0].get("application", "N/A") if hotspots else "N/A",
        "top_hotspot_count": hotspots[0].get("count", 0) if hotspots else 0,
        "top_hotspot_pct": round(hotspots[0].get("pct_of_total", 0), 1) if hotspots else 0,
        "change_emergency_pct": round(change_data.get("risk", {}).get("emergency_pct", 0), 1),
        "change_success_pct": round(change_data.get("risk", {}).get("implementation_success_pct", 0), 1),
        "change_avg_impl_hours": round(change_data.get("risk", {}).get("avg_impl_hours", 0), 1),
        "change_by_type": change_data.get("risk", {}).get("by_type", {}),
        "sr_total": sr_data.get("summary", {}).get("total", 0),
        "sr_backlog": sr_data.get("summary", {}).get("backlog_count", 0),
        "sr_avg_closure_hours": round(sr_data.get("summary", {}).get("avg_closure_hours", 0), 1),
        "sr_top_category": (
            sr_data.get("summary", {}).get("top_categories", [{}])[0].get("category", "N/A")
            if sr_data.get("summary", {}).get("top_categories") else "N/A"
        ),
    }


# Function: _extract_json_object
def _extract_json_object(text: str) -> Dict[str, Any]:
    text = (text or "").strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
        raise


# Function: _normalize_work_type
def _normalize_work_type(work_type: str) -> str:
    wt = re.sub(r"[^a-z]", "", str(work_type or "").lower())
    if wt in {"servicerequest", "servicecatalog", "request"}:
        return "servicerequest"
    if wt in {"incident", "incidents"}:
        return "incident"
    if wt in {"change", "changes", "changerequest"}:
        return "change"
    return wt or "unknown"


# Function: build_automation_key
def build_automation_key(category: str, work_type: str) -> str:
    cat = re.sub(r"\s+", " ", str(category or "unknown").strip().lower())
    return f"{cat}::{_normalize_work_type(work_type)}"


# Function: build_automation_id_key
def build_automation_id_key(candidate_id: Any) -> str:
    return f"id::{int(candidate_id)}"


# Function: _coerce_predictions
def _coerce_predictions(parsed: Any) -> List[Dict[str, Any]]:
    if isinstance(parsed, dict):
        preds = parsed.get("predictions", None)
        if isinstance(preds, list):
            return [p for p in preds if isinstance(p, dict)]
        if all(k in parsed for k in ("llm_opportunity_score", "category", "work_type")):
            return [parsed]
        return []
    if isinstance(parsed, list):
        return [p for p in parsed if isinstance(p, dict)]
    return []


# Function: get_available_ollama_models
def get_available_ollama_models(
    base_url: str = "http://localhost:11434",
    timeout: float = 10.0,
) -> List[str]:
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(f"{base_url}/api/tags")
            resp.raise_for_status()
            payload = resp.json() if isinstance(resp.json(), dict) else {}
            models = payload.get("models", [])
            names = [str(m.get("name", "")).strip() for m in models if isinstance(m, dict)]
            return [n for n in names if n]
    except Exception:
        return []


# Function: resolve_ollama_model
def resolve_ollama_model(
    configured_model: str,
    base_url: str = "http://localhost:11434",
    timeout: float = 10.0,
) -> str:
    """Choose an installed model, preferring configured model then known 7-8B defaults."""
    installed = get_available_ollama_models(base_url=base_url, timeout=timeout)
    if not installed:
        return configured_model

    configured = str(configured_model or "").strip()
    if configured in installed:
        return configured

    cfg_base = configured.split(":")[0].lower() if configured else ""
    if cfg_base:
        for model_name in installed:
            if model_name.split(":")[0].lower() == cfg_base:
                return model_name

    for preferred in _PREFERRED_OLLAMA_MODELS:
        if preferred in installed:
            return preferred

    return installed[0]


# Function: _normalise_insight_items
def _normalise_insight_items(parsed: Dict[str, Any], expected: set) -> Dict[str, List[Dict[str, str]]]:
    valid_levels = {"good", "warn", "critical", "info"}
    clean: Dict[str, List[Dict[str, str]]] = {}
    for key in expected:
        items = []
        for item in parsed.get(key, []):
            if isinstance(item, dict) and "text" in item:
                items.append({
                    "text": str(item["text"]),
                    "level": item.get("level", "info") if item.get("level") in valid_levels else "info",
                })
        clean[key] = items
    return clean


# Function: generate_insights_ollama
def generate_insights_ollama(
    summary: Dict[str, Any],
    incident_data: Dict[str, Any],
    change_data: Dict[str, Any],
    sr_data: Dict[str, Any],
    hotspots: List[Dict[str, Any]],
    base_url: str = "http://localhost:11434",
    model: str = "llama3.1:8b",
    timeout: float = 45.0,
    model_name: str = None,  # pre-resolved model — skips resolve_ollama_model() HTTP call
) -> Dict[str, List[Dict[str, str]]]:
    """
    Generate leadership insights using Ollama LLM (GPU).
    Falls back to rule-based kpis.generate_leadership_insights on any error.
    """
    from kpis import generate_leadership_insights  # local import to avoid circular

    selected_model = model_name if model_name else resolve_ollama_model(model, base_url=base_url, timeout=min(timeout, 10.0))
    kpi_dict = _build_kpi_summary(summary, incident_data, change_data, sr_data, hotspots)
    # Compact JSON reduces prompt token count by ~30% vs indent=2
    prompt = _INSIGHT_PROMPT.format(kpi_json=json.dumps(kpi_dict))

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(
                f"{base_url}/api/generate",
                json={
                    "model": selected_model,
                    "prompt": prompt,
                    "stream": False,
                    "keep_alive": "30m",
                    "format": "json",
                    "options": {
                        **_OLLAMA_GPU_OPTIONS_BASE,
                        "temperature": 0.2,
                        "num_predict": 380,  # 16 short insight strings fit easily in 380 tokens
                    },
                },
            )
            resp.raise_for_status()

        response_text = resp.json().get("response", "")
        parsed = _extract_json_object(response_text)

        expected = {"executive", "incidents", "changes", "service_requests"}
        if not expected.issubset(parsed.keys()):
            raise ValueError(f"LLM response missing keys: {expected - set(parsed.keys())}")

        # Validate and normalise each item
        clean = _normalise_insight_items(parsed, expected)

        logger.info("Ollama (%s) generated %d insight categories", selected_model, len(clean))
        return clean

    except httpx.ConnectError:
        logger.warning("Ollama not reachable at %s — using rule-based insights", base_url)
    except httpx.TimeoutException:
        logger.warning("Ollama request timed out after %.0fs — using rule-based insights", timeout)
    except (json.JSONDecodeError, ValueError, KeyError) as exc:
        logger.warning("Ollama response invalid (%s) — using rule-based insights", exc)
    except Exception as exc:
        logger.warning("Ollama error (%s) — using rule-based insights", exc)

    # Fallback
    return generate_leadership_insights(summary, incident_data, change_data, sr_data, hotspots)


# Function: _chunk
def _chunk(items: List[Dict[str, Any]], size: int) -> List[List[Dict[str, Any]]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


# Function: _processor_for_model_item
def _processor_for_model_item(item: Any, target: str) -> Optional[str]:
    """Return the processor string for a single /api/ps model entry, or None if it doesn't match/apply."""
    if not isinstance(item, dict):
        return None
    name = str(item.get("name", "")).lower()
    if target and target not in name:
        return None

    processor = (
        item.get("processor")
        or item.get("compute")
        or item.get("inference")
        or item.get("details", {}).get("processor")
        or item.get("details", {}).get("inference")
    )
    if processor:
        return str(processor)

    # Ollama /api/ps may omit processor string; infer from VRAM footprint.
    try:
        size_vram = int(item.get("size_vram", 0) or 0)
        if size_vram > 0:
            return "gpu"
    except Exception:
        pass
    return None


# Function: get_ollama_model_processor
def get_ollama_model_processor(
    base_url: str = "http://localhost:11434",
    model: str = "llama3.1:8b",
    timeout: float = 15.0,
) -> str:
    """
    Return the runtime processor for a loaded Ollama model (e.g., GPU/CPU).
    Returns "unknown" when processor metadata is unavailable.
    """
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(f"{base_url}/api/ps")
            resp.raise_for_status()
            payload = resp.json() if isinstance(resp.json(), dict) else {}
            models = payload.get("models", [])
            target = model.split(":")[0].lower()

            for item in models:
                processor = _processor_for_model_item(item, target)
                if processor:
                    return processor
            return "unknown"
    except Exception:
        return "unknown"


# Function: _build_automation_payload_rows
def _build_automation_payload_rows(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "candidate_id": i,
            "category": c.get("category", "Unknown"),
            "work_type": c.get("work_type", "Unknown"),
            "ticket_count": c.get("ticket_count", c.get("volume", 0)),
            "repetition_score": c.get("repetition_score", 0),
            "avg_cycle_time_hours": c.get("avg_cycle_time_hours", c.get("avg_cycle_time", 0)),
            "priority": c.get("priority", "Monitor"),
            "total_score": c.get("total_score", 0),
        }
        for i, c in enumerate(candidates)
    ]


# Function: _request_bulk_predictions
def _request_bulk_predictions(
    client: "httpx.Client", base_url: str, selected_model: str, part: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Ask Ollama to score a whole chunk of candidates in a single call."""
    try:
        prompt = _AUTOMATION_PREDICTION_PROMPT.format(candidate_json=json.dumps(part, indent=2))
        resp = client.post(
            f"{base_url}/api/generate",
            json={
                "model": selected_model,
                "prompt": prompt,
                "stream": False,
                "keep_alive": "30m",
                "format": "json",
                "options": {
                    **_OLLAMA_GPU_OPTIONS_BASE,
                    "temperature": 0.15,
                    "num_predict": 1024,
                },
            },
        )
        resp.raise_for_status()
        response_text = resp.json().get("response", "")
        parsed = _extract_json_object(response_text)
        return _coerce_predictions(parsed)
    except Exception as exc:
        logger.warning("Bulk automation enrichment parse failed; retrying single-row mode: %s", exc)
        return []


# Function: _request_single_predictions
def _request_single_predictions(
    client: "httpx.Client", base_url: str, selected_model: str, part: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Fallback: per-row strict prompt to recover from malformed bulk JSON."""
    predictions: List[Dict[str, Any]] = []
    for row in part:
        try:
            single_prompt = _AUTOMATION_SINGLE_PREDICTION_PROMPT.format(candidate_json=json.dumps(row, indent=2))
            single_resp = client.post(
                f"{base_url}/api/generate",
                json={
                    "model": selected_model,
                    "prompt": single_prompt,
                    "stream": False,
                    "keep_alive": "30m",
                    "format": "json",
                    "options": {
                        **_OLLAMA_GPU_OPTIONS_BASE,
                        "temperature": 0.15,
                        "num_predict": 256,
                    },
                },
            )
            single_resp.raise_for_status()
            single_text = single_resp.json().get("response", "")
            single_parsed = _extract_json_object(single_text)
            single_predictions = _coerce_predictions(single_parsed)
            if single_predictions:
                predictions.extend(single_predictions)
        except Exception as exc:
            logger.warning("Single-row automation enrichment parse failed: %s", exc)
    return predictions


# Function: _apply_automation_predictions
def _apply_automation_predictions(
    predictions: List[Dict[str, Any]], prediction_map: Dict[str, Dict[str, Any]]
) -> None:
    for p in predictions:
        if not isinstance(p, dict):
            continue
        candidate_id = p.get("candidate_id", None)
        category = str(p.get("category", "Unknown"))
        work_type = str(p.get("work_type", "Unknown"))
        prediction = {
            "llm_opportunity_score": float(p.get("llm_opportunity_score", 0)),
            "llm_confidence": float(p.get("llm_confidence", 0)),
            "llm_automation_type": str(p.get("llm_automation_type", "Hybrid")),
            "llm_risk_level": str(p.get("llm_risk_level", "Medium")),
            "llm_rationale": str(p.get("llm_rationale", "")),
            "llm_next_step": str(p.get("llm_next_step", "")),
            "analysis_source": "ollama",
        }
        if candidate_id is not None:
            try:
                prediction_map[build_automation_id_key(candidate_id)] = prediction
            except Exception:
                pass
        prediction_map[build_automation_key(category, work_type)] = prediction


# Function: enrich_automation_candidates_ollama
def enrich_automation_candidates_ollama(
    candidates: List[Dict[str, Any]],
    base_url: str = "http://localhost:11434",
    model: str = "llama3.1:8b",
    timeout: float = 60.0,
    chunk_size: int = 15,
    require_gpu: bool = False,
) -> Dict[str, Dict[str, Any]]:
    """
    Use Ollama to enrich automation candidates with predicted opportunity,
    confidence, risk, and recommended automation approach.

    Returns a mapping keyed by "{category}::{work_type}".
    """
    if not candidates:
        return {}

    selected_model = resolve_ollama_model(model, base_url=base_url, timeout=min(timeout, 10.0))

    # GPU preflight — check before spending time on LLM calls so we fail fast.
    if require_gpu:
        processor = get_ollama_model_processor(
            base_url=base_url, model=selected_model, timeout=min(timeout, 15.0)
        )
        if "gpu" not in processor.lower():
            logger.warning(
                "GPU required but Ollama processor is '%s' — aborting automation enrichment", processor
            )
            return {}
    prediction_map: Dict[str, Dict[str, Any]] = {}
    payload_rows = _build_automation_payload_rows(candidates)

    try:
        with httpx.Client(timeout=timeout) as client:
            for part in _chunk(payload_rows, chunk_size):
                predictions = _request_bulk_predictions(client, base_url, selected_model, part)
                if not predictions:
                    predictions = _request_single_predictions(client, base_url, selected_model, part)
                _apply_automation_predictions(predictions, prediction_map)

        logger.info("Ollama (%s) enriched %d automation candidates", selected_model, len(prediction_map))
        return prediction_map

    except httpx.ConnectError:
        logger.warning("Ollama not reachable at %s for automation enrichment", base_url)
    except httpx.TimeoutException:
        logger.warning("Ollama automation enrichment timed out after %.0fs", timeout)
    except (json.JSONDecodeError, ValueError, KeyError) as exc:
        logger.warning("Invalid Ollama automation enrichment response: %s", exc)
    except Exception as exc:
        logger.warning("Ollama automation enrichment error: %s", exc)

    return {}
