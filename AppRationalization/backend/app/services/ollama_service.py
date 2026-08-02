# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: OllamaService — Local LLM (Ollama) integration for:
# Date: 2025-07-13
# ---------------------------------------------------------------------------
"""
OllamaService — Local LLM (Ollama) integration for:
  1. Null/missing field prediction across CORENT, CAST, and Industry data
  2. Correlation analysis & insights generation
"""

import json
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import unescape
from xml.etree import ElementTree
from typing import Any, Dict, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MARKET_SEARCH_PROVIDER = os.getenv("MARKET_SEARCH_PROVIDER", "").strip().casefold()
MARKET_SEARCH_URL = os.getenv("MARKET_SEARCH_URL", "").strip()
MARKET_SEARCH_RESPONSE_FORMAT = os.getenv("MARKET_SEARCH_RESPONSE_FORMAT", "html").strip().casefold()
MARKET_SEARCH_ENGINES = os.getenv("MARKET_SEARCH_ENGINES", "").strip()
MARKET_SEARCH_API_KEY = os.getenv("MARKET_SEARCH_API_KEY", "").strip()
MARKET_SEARCH_API_KEY_HEADER = os.getenv("MARKET_SEARCH_API_KEY_HEADER", "X-Subscription-Token").strip()
try:
    MARKET_SEARCH_TIMEOUT = max(3, int(os.getenv("MARKET_SEARCH_TIMEOUT_SECONDS", "15")))
except ValueError:
    MARKET_SEARCH_TIMEOUT = 15
try:
    MARKET_SEARCH_MAX_PRODUCTS = max(1, int(os.getenv("MARKET_SEARCH_MAX_PRODUCTS", "100")))
except ValueError:
    MARKET_SEARCH_MAX_PRODUCTS = 100
MARKET_SEARCH_REQUIRED = os.getenv("MARKET_SEARCH_REQUIRED", "true").strip().casefold() not in {"0", "false", "no"}

# GPU offloading: -1 = all layers to GPU (full CUDA mode), 0 = CPU only.
# Override via OLLAMA_NUM_GPU env var (e.g. OLLAMA_NUM_GPU=0 for CPU-only).
# RTX 4070 SUPER (12 GB VRAM) can handle qwen2.5:7b or smaller fully on-GPU.
_raw_num_gpu = os.getenv("OLLAMA_NUM_GPU", "-1")
try:
    OLLAMA_NUM_GPU: int = int(_raw_num_gpu)
except ValueError:
    OLLAMA_NUM_GPU = -1

# Index of the GPU to use (0 = first GPU).  Override via OLLAMA_MAIN_GPU.
_raw_main_gpu = os.getenv("OLLAMA_MAIN_GPU", "0")
try:
    OLLAMA_MAIN_GPU: int = int(_raw_main_gpu)
except ValueError:
    OLLAMA_MAIN_GPU = 0

# Optional hard-coded preferred model override (e.g. OLLAMA_PREFERRED_MODEL=qwen2.5:7b).
# When set, this model is tried first before the ranked list below.
OLLAMA_PREFERRED_MODEL: Optional[str] = os.getenv("OLLAMA_PREFERRED_MODEL") or None

# Ranked model list — optimised for NVIDIA GPU with 12 GB VRAM (e.g. RTX 4070 SUPER).
# Models are ordered best-quality-first within each VRAM tier.
# Best choice for RTX 4070 SUPER: qwen2.5:7b (~8.9 GB Q4_K_M) — top
# reasoning/quality while still leaving ~3 GB headroom on 12 GB VRAM.
PREFERRED_MODELS = [
    # ── Tier 1 — 12 GB VRAM sweet-spot (recommended for RTX 4070 SUPER) ──
    "qwen3.5:9b",          # Shared default; fits fully in the 12 GB RTX 4070 SUPER
    "qwen2.5:7b",           # 14B Q4_K_M ~8.9 GB — best quality for enterprise analysis
    "qwen2.5:7b-instruct",
    "mistral:7b-instruct",   # 7B Q4 ~4.1 GB — fast, strong instruction following
    "mistral:7b",
    "mistral:latest",
    "mistral",
    "llama3.1:8b",           # 8B Q4 ~4.9 GB — strong reasoning, long context
    "llama3.1:latest",
    "llama3:latest",         # 8B — already installed
    "llama3",
    "llama3:8b",
    "gemma2:9b",             # 9B Q4 ~5.5 GB — Google, excellent benchmarks
    "gemma2:latest",
    # ── Tier 2 — smaller/fast fallbacks ──
    "llama3.2:latest",       # 3B — extremely fast
    "llama3.2",
    "exaone3.5:2.4b",        # 2.4B — very fast
    "phi3:mini",
    "phi3",
    "gemma2:2b",
    "gemma2",
    "moondream:latest",      # ~1.8B — ultra fast
    "starling-lm:7b-alpha-q5_K_M",
    "qwen2.5",
    # ── Tier 3 — large models (only if 12B+ fits) ──
    "codellama:13b",         # 13B ~8.4 GB Q4
    "GLM4:latest",
    "llama2:latest",
    "gpt-oss:20b",           # 20B — requires ~12 GB+ VRAM
    "llama3:70b-instruct",
    "llama3:70b",
]

# Column groups per source (used to build context-rich prompts)
CORENT_SCHEMA_CONTEXT = (
    "architecture_type, business_owner, platform_host, server_type, server_ip, server_name, "
    "operating_system, cpu_core, memory, internal_storage, external_storage, storage_type, "
    "db_storage, db_engine, environment, install_type, virtualization_attributes, "
    "compute_server_hardware_architecture, application_stability, virtualization_state, "
    "storage_decomposition, flash_storage_used, cpu_requirement, memory_ram_requirement, "
    "mainframe_dependency, desktop_dependency, app_os_platform_cloud_suitability, "
    "database_cloud_readiness, integration_middleware_cloud_readiness, "
    "application_hardware_dependency, app_cots_vs_non_cots, cloud_suitability, "
    "volume_external_dependencies, app_load_predictability_elasticity, "
    "financially_optimizable_hardware_usage, distributed_architecture_design, "
    "latency_requirements, ubiquitous_access_requirements, no_production_environments, "
    "no_non_production_environments, ha_dr_requirements, rto_requirements, "
    "rpo_requirements, deployment_geography"
)

CAST_SCHEMA_CONTEXT = (
    "app_id, app_name, application_architecture, source_code_availability, "
    "programming_language, component_coupling, cloud_suitability, "
    "volume_external_dependencies, code_design, server_name"
)

INDUSTRY_SCHEMA_CONTEXT = (
    "app_id, app_name, business_owner, architecture_type, platform_host, "
    "application_type, install_type, capabilities"
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

# Module-level model cache — avoids a HTTP round-trip on every batch call.
# The cache is invalidated after _MODEL_CACHE_TTL seconds so new models pulled
# during a long run are picked up without restarting the server. Keyed by the
# requested `preferred` model (None = the default ranked-list behaviour) so a
# caller asking for one specific model (e.g. Wave Planning's qwen3.5:9b)
# can't clobber the cache entry other callers rely on, or vice versa.
import time as _time
_model_cache: Dict[Optional[str], str] = {}
_model_cache_ts: Dict[Optional[str], float] = {}
_MODEL_CACHE_TTL: float = 30.0   # seconds


def _plain_search_text(value: str) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>", " ", value, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(unescape(text).split())


def _market_search_subject(topic: str) -> str:
    subject = " ".join(str(topic or "").split())
    return re.sub(
        r"^(?:harmonize|rationalize|consolidate|modernize|standardize|optimize|evaluate|assess)\s+",
        "",
        subject,
        flags=re.I,
    ) or subject


def _market_topic_queries(topic: str) -> List[str]:
    """Build domain-focused discovery queries and avoid consumer-market drift."""
    subject = _market_search_subject(topic)
    queries = [f'"{subject}" software capabilities standards features']
    if "alarm management" in subject.casefold():
        queries.append(
            '"EEMUA 191" process plant alarm management software '
            'alarm rationalization monitoring operator response'
        )
    return queries


def _portfolio_evidence_defaults(
    product: Dict[str, Any],
    headers: List[str],
) -> Dict[str, str]:
    """Derive conservative values from uploaded first-party portfolio fields."""
    context = product.get("context") if isinstance(product.get("context"), dict) else {}
    context_text = " ".join(str(value or "") for value in context.values()).casefold()
    application_type = " ".join(
        str(value or "")
        for key, value in context.items()
        if "application type" in str(key).casefold()
    ).casefold()
    values: Dict[str, str] = {}
    for header in headers:
        header_key = str(header or "").casefold()
        if any(token in header_key for token in ("product type", "cots", "custom product", "available in market")):
            if "commercial of the shelf with major modifications" in application_type:
                values[header] = "Hybrid"
            elif "commercial of the shelf" in application_type or "off the shelf" in application_type:
                values[header] = "COTS"
            elif any(token in application_type for token in ("custom", "in-house", "in house", "bespoke")):
                values[header] = "Custom"
            continue

        terms = {
            token for token in re.findall(r"[a-z0-9]+", header_key)
            if len(token) >= 4 and token not in {
                "alarm", "event", "management", "system", "software", "capability",
            }
        }
        if terms and terms & set(re.findall(r"[a-z0-9]+", context_text)):
            values[header] = "Yes"
    return values


def _portfolio_grounded_capabilities(
    topic: str,
    products: List[Dict[str, Any]],
) -> List[str]:
    """Surface capabilities explicitly stated in uploaded portfolio evidence."""
    if "alarm management" not in str(topic or "").casefold():
        return []
    context_text = " ".join(
        str(value or "")
        for product in products
        for value in (product.get("context") or {}).values()
    ).casefold()
    grounded = []
    for phrase, capability in (
        ("alarm monitoring", "Alarm Monitoring"),
        ("alarm-event analysis", "Alarm Event Analysis"),
        ("alarm event analysis", "Alarm Event Analysis"),
        ("operational alert management", "Operational Alert Management"),
    ):
        if phrase in context_text and capability not in grounded:
            grounded.append(capability)
    return grounded


def _global_market_search(query: str, max_results: int = 5) -> List[str]:
    """Retrieve public-market evidence for Ollama; never invent search results."""
    if not MARKET_SEARCH_URL:
        raise RuntimeError(
            "MARKET_SEARCH_URL is not configured; set it to an approved enterprise or public search endpoint"
        )
    params = {"q": query}
    if MARKET_SEARCH_ENGINES:
        params["engines"] = MARKET_SEARCH_ENGINES
    if MARKET_SEARCH_RESPONSE_FORMAT in {"json", "rss"}:
        params["format"] = MARKET_SEARCH_RESPONSE_FORMAT
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; StratIQ-MarketResearch/1.0)",
        "Accept-Language": "en-US,en;q=0.8",
    }
    if MARKET_SEARCH_API_KEY:
        headers[MARKET_SEARCH_API_KEY_HEADER] = MARKET_SEARCH_API_KEY
    response = requests.get(
        MARKET_SEARCH_URL,
        params=params,
        headers=headers,
        timeout=MARKET_SEARCH_TIMEOUT,
    )
    response.raise_for_status()
    content_type = response.headers.get("content-type", "").casefold()
    snippets: List[str] = []
    if "xml" in content_type:
        root = ElementTree.fromstring(response.text)
        for item in root.findall(".//item"):
            title = _plain_search_text(item.findtext("title") or "")
            description = _plain_search_text(item.findtext("description") or "")
            combined = " — ".join(part for part in (title, description) if part)
            if combined:
                snippets.append(combined[:1000])
    elif "json" in content_type:
        payload = response.json()
        candidates = payload.get("results", []) if isinstance(payload, dict) else payload
        for item in candidates if isinstance(candidates, list) else []:
            if isinstance(item, dict):
                text = item.get("snippet") or item.get("description") or item.get("title")
            else:
                text = item
            cleaned = _plain_search_text(str(text or ""))
            if cleaned:
                snippets.append(cleaned[:1000])
    else:
        lowered = response.text.casefold()
        if "challenge-form" in lowered or "confirm this search was made by a human" in lowered:
            raise RuntimeError("market search provider returned an anti-bot challenge")
        bing_blocks = re.findall(
            r'<li[^>]+class="[^"]*b_algo[^"]*"[^>]*>(.*?)</li>',
            response.text,
            flags=re.I | re.S,
        )
        for block in bing_blocks:
            title_match = re.search(r"<h2[^>]*>(.*?)</h2>", block, flags=re.I | re.S)
            description_match = re.search(r"<p[^>]*>(.*?)</p>", block, flags=re.I | re.S)
            title = _plain_search_text(title_match.group(1)) if title_match else ""
            description = _plain_search_text(description_match.group(1)) if description_match else ""
            combined = " — ".join(part for part in (title, description) if part)
            if combined:
                snippets.append(combined[:1000])
        searxng_blocks = re.findall(
            r'<article[^>]+class="[^"]*\bresult\b[^"]*"[^>]*>(.*?)</article>',
            response.text,
            flags=re.I | re.S,
        )
        for block in searxng_blocks:
            title_match = re.search(r"<h3[^>]*>(.*?)</h3>", block, flags=re.I | re.S)
            description_match = re.search(
                r'<p[^>]+class="[^"]*\bcontent\b[^"]*"[^>]*>(.*?)</p>',
                block,
                flags=re.I | re.S,
            )
            title = _plain_search_text(title_match.group(1)) if title_match else ""
            description = _plain_search_text(description_match.group(1)) if description_match else ""
            combined = " — ".join(part for part in (title, description) if part)
            if combined:
                snippets.append(combined[:1000])
        blocks = re.findall(
            r'<(?:a|div)[^>]+class="[^"]*(?:result__a|result__snippet)[^"]*"[^>]*>(.*?)</(?:a|div)>',
            response.text,
            flags=re.I | re.S,
        )
        snippets.extend(_plain_search_text(block)[:1000] for block in blocks if _plain_search_text(block))
    significant = {
        token for token in re.findall(r"[a-z0-9]+", query.casefold())
        if len(token) >= 4 and token not in {
            "software", "capabilities", "capability", "features", "feature", "standards",
            "product", "products", "solutions", "solution", "available", "market",
        }
    }
    relevant = []
    for snippet in dict.fromkeys(snippets):
        snippet_tokens = set(re.findall(r"[a-z0-9]+", snippet.casefold()))
        if len(significant & snippet_tokens) >= min(2, len(significant)):
            relevant.append(snippet)
    return relevant[:max_results]


# Function: _available_model
def _available_model(timeout: int = 5, preferred: Optional[str] = None) -> Optional[str]:
    """Return an available Ollama model, optionally requiring one specific tag.

    Priority: explicit `preferred` argument (if installed) > `OLLAMA_PREFERRED_MODEL`
    env var (if installed) > ranked PREFERRED_MODELS list > first installed model.

    Result is cached per `preferred` key for ``_MODEL_CACHE_TTL`` seconds to
    avoid hammering the Ollama /api/tags endpoint inside tight batch loops.
    """
    now = _time.monotonic()
    cached = _model_cache.get(preferred)
    if cached is not None and (now - _model_cache_ts.get(preferred, 0)) < _MODEL_CACHE_TTL:
        return cached

    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=timeout)
        if resp.status_code != 200:
            return None
        installed = {m.get("name", "") for m in resp.json().get("models", [])}

        if preferred and preferred in installed:
            _model_cache[preferred] = preferred
            _model_cache_ts[preferred] = now
            return preferred

        # Honour explicit override first
        if OLLAMA_PREFERRED_MODEL and OLLAMA_PREFERRED_MODEL in installed:
            logger.debug("Ollama: using env-specified model '%s'", OLLAMA_PREFERRED_MODEL)
            _model_cache[preferred] = OLLAMA_PREFERRED_MODEL
            _model_cache_ts[preferred] = now
            return OLLAMA_PREFERRED_MODEL

        for candidate in PREFERRED_MODELS:
            if candidate in installed:
                _model_cache[preferred] = candidate
                _model_cache_ts[preferred] = now
                return candidate
        # Use first installed if none in preferred list
        if installed:
            fallback = next(iter(installed))
            _model_cache[preferred] = fallback
            _model_cache_ts[preferred] = now
            return fallback
        return None
    except Exception as exc:
        logger.warning("Ollama not reachable: %s", exc)
        return None


# Function: _generate
def _generate(
    model: str,
    prompt: str,
    timeout: int = 30,
    force_json: bool = False,
    num_predict: int = 4096,
    num_ctx: int = 8192,
    temperature: float = 0.2,
    think: Optional[bool] = None,
) -> str:
    """Call Ollama /api/generate and return the full response text.

    Parameters
    ----------
    force_json : bool
        When True, adds ``"format": "json"`` to the Ollama request so the
        inference engine hard-constrains output to valid JSON.  Use for batch
        prediction calls to prevent small-model free-text preamble.
    num_predict : int
        Maximum tokens to generate.  Default 4096 — sufficient for all structured
        JSON responses with multiple sections, lists and per-app annotations.
        Reasoning ("thinking") models spend part of this budget on an internal
        reasoning trace before the actual answer — Ollama separates that out
        of the returned `response` text automatically, but the budget must be
        large enough to cover both, or generation gets cut off before the
        answer ever starts.
    num_ctx : int
        Context window (prompt + response tokens combined).  Default 16384 — saves
        ~1GB VRAM vs 32768 on 14B models, speeds up prefill, fits comfortably on
        RTX 4070 SUPER 12GB alongside qwen2.5:7b (~8.9GB model weights).
    think : bool | None
        Explicit reasoning-mode control for models that support it (e.g.
        Qwen3-family "thinking" models). ``None`` leaves the model's own
        default behaviour; ``False`` disables the reasoning trace entirely
        (much faster); ``True`` forces it on.

    GPU notes
    ---------
    ``num_gpu`` is set to ``OLLAMA_NUM_GPU`` (default -1 = all layers on GPU).
    This forces Ollama to fully offload the model to the NVIDIA GPU via CUDA.
    Set ``OLLAMA_NUM_GPU=0`` to fall back to CPU-only inference.
    """
    payload: Dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": 0.9,
            "num_predict": num_predict,
            "num_ctx":     num_ctx,
            # ── GPU acceleration (CUDA) ──────────────────────────────────
            # -1 = offload ALL transformer layers to GPU (full CUDA mode).
            # Requires Ollama built with CUDA support and NVIDIA drivers.
            # Controlled by OLLAMA_NUM_GPU env var (override in .env).
            "num_gpu": OLLAMA_NUM_GPU,
            # Select GPU device index (0 = first GPU, e.g. RTX 4070 SUPER).
            # Controlled by OLLAMA_MAIN_GPU env var.
            "main_gpu": OLLAMA_MAIN_GPU,
        },
    }
    if force_json:
        payload["format"] = "json"
    if think is not None:
        payload["think"] = think
    resp = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json=payload,
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json().get("response", "")


# Function: _extract_json
def _extract_json(text: str) -> Dict[str, Any]:
    """
    Robustly extract the first JSON object from an LLM response.
    The model sometimes wraps JSON in markdown code fences.
    """
    text = _clean_llm_json_text(text)

    # Find the largest {...} block (greedy — handles nested JSON correctly)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Try the whole cleaned text
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return {}


# Function: _clean_llm_json_text
def _clean_llm_json_text(text: str) -> str:
    """Remove markdown fences and trim whitespace from LLM output."""
    text = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE)
    text = text.replace("```", "")
    return text.strip()


# Function: _scan_string_char
def _scan_string_char(ch: str, escape: bool) -> Tuple[bool, bool]:
    """Given a char consumed while inside a JSON string, return (still_in_string, new_escape)."""
    if escape:
        return True, False
    if ch == "\\":
        return True, True
    if ch == '"':
        return False, False
    return True, False


# Function: _extract_top_level_json_objects
def _extract_top_level_json_objects(text: str) -> List[str]:
    """
    Extract top-level JSON object snippets from arbitrary text.

    This is a best-effort fallback when array parsing fails due to
    one malformed object inside the batch payload.
    """
    objects: List[str] = []
    depth = 0
    start_idx: Optional[int] = None
    in_string = False
    escape = False

    for i, ch in enumerate(text):
        if in_string:
            in_string, escape = _scan_string_char(ch, escape)
            continue

        if ch == '"':
            in_string = True
            continue

        if ch == "{":
            if depth == 0:
                start_idx = i
            depth += 1
        elif ch == "}" and depth > 0:
            depth -= 1
            if depth == 0 and start_idx is not None:
                objects.append(text[start_idx:i + 1])
                start_idx = None

    return objects


# Function: _extract_json_array
def _extract_json_array(text: str) -> List[Dict[str, Any]]:
    """
    Robustly parse a JSON array from an LLM response.

    Strategy:
      1) Parse the matched [...] block directly.
      2) Retry after removing trailing commas before ] or }.
      3) Fallback: parse any recoverable top-level objects individually.
    """
    cleaned = _clean_llm_json_text(text)
    arr_match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    candidate = arr_match.group() if arr_match else cleaned

    # Primary parse attempt
    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
    except json.JSONDecodeError:
        pass

    # Common repair: trailing commas like {...,}
    repaired = re.sub(r",\s*([\]}])", r"\1", candidate)
    try:
        parsed = json.loads(repaired)
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
    except json.JSONDecodeError:
        pass

    # Best-effort salvage: parse each recoverable object independently
    recovered: List[Dict[str, Any]] = []
    for obj_text in _extract_top_level_json_objects(candidate):
        try:
            obj = json.loads(obj_text)
            if isinstance(obj, dict):
                recovered.append(obj)
        except json.JSONDecodeError:
            continue

    return recovered


# Function: _numeric_key_map_to_list
def _numeric_key_map_to_list(obj: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert a {"0": {...}, "1": {...}} shaped dict into [{"idx": 0, "predictions": {...}}, ...].

    Returns [] if any key/value pair doesn't fit that shape (mirrors the
    original all-or-nothing "all_numeric" gate).
    """
    items: List[Dict[str, Any]] = []
    for key, value in obj.items():
        if not isinstance(value, dict):
            return []
        try:
            idx = int(str(key))
        except ValueError:
            return []
        items.append({"idx": idx, "predictions": value})
    return items


# Function: _extract_wrapped_list
def _extract_wrapped_list(obj: Dict[str, Any]) -> List[Dict[str, Any]]:
    for key in ("results", "items", "data", "predictions", "records"):
        val = obj.get(key)
        if isinstance(val, list):
            return [item for item in val if isinstance(item, dict)]
    return []


# Function: _candidates_from_object
def _candidates_from_object(obj: Dict[str, Any], expected_count: int) -> List[Dict[str, Any]]:
    candidates = _extract_wrapped_list(obj)
    if candidates:
        return candidates

    numeric_items = _numeric_key_map_to_list(obj)
    if numeric_items:
        return numeric_items

    if "idx" in obj or "predictions" in obj:
        return [obj]
    if expected_count == 1:
        return [obj]
    return []


# Function: _extract_item_preds
def _extract_item_preds(item: Dict[str, Any]) -> Dict[str, Any]:
    preds = item.get("predictions")
    if isinstance(preds, dict):
        return preds
    return {k: v for k, v in item.items() if k not in ("idx", "known", "null_fields")}


# Function: _normalize_indexed_candidates
def _normalize_indexed_candidates(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for item in candidates:
        idx = item.get("idx")
        if not isinstance(idx, int):
            continue
        normalized.append({"idx": idx, "predictions": _extract_item_preds(item)})
    return normalized


# Function: _normalize_ordered_candidates
def _normalize_ordered_candidates(
    candidates: List[Dict[str, Any]], expected_count: int
) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for i, item in enumerate(candidates):
        if i >= expected_count:
            break
        if not isinstance(item, dict):
            continue
        normalized.append({"idx": i, "predictions": _extract_item_preds(item)})
    return normalized


# Function: _parse_batch_prediction_payload
def _parse_batch_prediction_payload(raw_text: str, expected_count: int) -> List[Dict[str, Any]]:
    """
    Parse and normalize LLM batch output into:
      [{"idx": <int>, "predictions": {...}}, ...]

    Accepts multiple JSON shapes to reduce brittle parsing failures:
      - array of {idx, predictions}
      - array of plain prediction objects (mapped by order)
      - object wrapper with list under keys like results/items/data
      - object keyed by numeric idx: {"0": {...}, "1": {...}}
      - single object {idx, predictions} or plain predictions (for 1-record batches)
    """
    cleaned = _clean_llm_json_text(raw_text)

    candidates: List[Dict[str, Any]] = _extract_json_array(cleaned)

    # If array extraction fails, try object-based shapes.
    if not candidates:
        obj = _extract_json(cleaned)
        if isinstance(obj, dict) and obj:
            candidates = _candidates_from_object(obj, expected_count)

    if not candidates:
        return []

    # If salvage returned one dict that is itself a numeric-key map,
    # normalize it before order-based handling.
    if len(candidates) == 1 and isinstance(candidates[0], dict):
        numeric_items = _numeric_key_map_to_list(candidates[0])
        if numeric_items:
            return numeric_items

    # Case 1: items already include numeric idx.
    has_explicit_idx = all(isinstance(item.get("idx"), int) for item in candidates)
    if has_explicit_idx:
        return _normalize_indexed_candidates(candidates)

    # Case 2: no idx field, map items by order.
    return _normalize_ordered_candidates(candidates, expected_count)


# ---------------------------------------------------------------------------
# Rule-based pre-fill — populate obvious fields deterministically BEFORE LLM
# to reduce the number of null fields sent to the GPU, improving throughput.
# ---------------------------------------------------------------------------

# Function: _fill_cast_application_architecture
def _fill_cast_application_architecture(lang: str, coupling: str) -> Optional[str]:
    if "cobol" in lang or "rpg" in lang or "pl/i" in lang:
        return "Batch"
    if coupling == "high":
        return "Monolithic"
    if coupling in ("low", "very low"):
        return "Microservices"
    if any(x in lang for x in ("java", "spring", "kotlin")):
        return "SOA"
    if any(x in lang for x in (".net", "c#", "vb.net")):
        return "N-Tier"
    if any(x in lang for x in ("python", "node", "ruby", "go", "rust")):
        return "Web-Based"
    return None


# Function: _fill_cast_cloud_suitability
def _fill_cast_cloud_suitability(effective_arch: str) -> Optional[str]:
    arch_lower = effective_arch.lower()
    if "microservice" in arch_lower or "web" in arch_lower or "soa" in arch_lower:
        return "High"
    if "monolith" in arch_lower or "batch" in arch_lower or "mainframe" in arch_lower:
        return "Low"
    if "n-tier" in arch_lower or "client" in arch_lower:
        return "Medium"
    return None


# Function: _heuristic_fills_cast
def _heuristic_fills_cast(record: Dict[str, Any], fills: Dict[str, Any], is_null: Any) -> None:
    arch = (record.get("application_architecture") or "").strip()
    lang = (record.get("programming_language") or "").lower()
    coupling = (record.get("component_coupling") or "").lower()

    if is_null("application_architecture"):
        filled = _fill_cast_application_architecture(lang, coupling)
        if filled:
            fills["application_architecture"] = filled

    effective_arch = fills.get("application_architecture") or arch
    if is_null("cloud_suitability") and effective_arch:
        filled = _fill_cast_cloud_suitability(effective_arch)
        if filled:
            fills["cloud_suitability"] = filled

    if is_null("source_code_availability") and record.get("repo_name"):
        fills["source_code_availability"] = "Available"


# Function: _fill_corent_cloud_suitability
def _fill_corent_cloud_suitability(arch: str, os_: str, virt: str) -> Optional[str]:
    if "microservice" in arch or "web" in arch or "soa" in arch:
        return "High"
    if "monolith" in arch or "mainframe" in arch:
        return "Low"
    if "n-tier" in arch or "client" in arch:
        return "Medium"
    if "linux" in os_ or "ubuntu" in os_ or "rhel" in os_ or "centos" in os_:
        return "High"
    if "windows" in os_:
        return "Medium"
    if "virtual" in virt or "vm" in virt:
        return "Medium"
    return None


# Function: _fill_corent_virtualization_state
def _fill_corent_virtualization_state(record: Dict[str, Any], os_: str) -> Optional[str]:
    # Both checks are independent (not mutually exclusive) in the source data;
    # if both match, "physical" wins since it is evaluated last.
    result = None
    if "vmware" in os_ or "hyper-v" in os_:
        result = "Virtualized"
    if "physical" in (record.get("server_type") or "").lower():
        result = "Physical"
    return result
    return None


# Function: _heuristic_fills_corent
def _heuristic_fills_corent(record: Dict[str, Any], fills: Dict[str, Any], is_null: Any) -> None:
    arch = (record.get("architecture_type") or "").lower()
    os_ = (record.get("operating_system") or "").lower()
    virt = (record.get("virtualization_state") or "").lower()

    if is_null("cloud_suitability"):
        filled = _fill_corent_cloud_suitability(arch, os_, virt)
        if filled:
            fills["cloud_suitability"] = filled

    if is_null("virtualization_state"):
        filled = _fill_corent_virtualization_state(record, os_)
        if filled:
            fills["virtualization_state"] = filled

    if is_null("distributed_architecture_design") and arch:
        fills["distributed_architecture_design"] = (
            "Yes" if any(x in arch for x in ("microservice", "soa", "distributed")) else "No"
        )


# Function: _heuristic_fills_industry
def _heuristic_fills_industry(record: Dict[str, Any], fills: Dict[str, Any], is_null: Any) -> None:
    app_type = (record.get("application_type") or "").lower()
    if not is_null("capabilities"):
        return
    if "erp" in app_type:
        fills["capabilities"] = "Finance, HR, Supply Chain, Procurement"
    elif "crm" in app_type:
        fills["capabilities"] = "Customer Management, Sales, Marketing"
    elif "hr" in app_type:
        fills["capabilities"] = "Human Resources, Payroll, Talent Management"
    elif "finance" in app_type or "accounting" in app_type:
        fills["capabilities"] = "Financial Reporting, Accounts Payable/Receivable, Budgeting"
    elif "itsm" in app_type or "helpdesk" in app_type:
        fills["capabilities"] = "Incident Management, Change Management, Service Desk"

# Function: apply_heuristic_fills
def apply_heuristic_fills(record: Dict[str, Any], source: str) -> Dict[str, Any]:
    """
    Populate fields that can be derived from other known fields using
    deterministic rules.  Returns a dict of {field: filled_value} for
    every field that was null and could be filled.

    Safe to call before the LLM batch — zero network latency.
    """
    fills: Dict[str, Any] = {}
    is_null = lambda f: not record.get(f) or str(record.get(f, "")).strip() == ""

    handlers = {
        "cast": _heuristic_fills_cast,
        "corent": _heuristic_fills_corent,
        "industry": _heuristic_fills_industry,
    }
    handler = handlers.get(source)
    if handler:
        handler(record, fills, is_null)

    return fills


# ---------------------------------------------------------------------------
# Distribution helpers — used by deep correlation analysis
# ---------------------------------------------------------------------------

# Function: _top_dist
def _top_dist(records: List[Dict], field: str, top: int = 8) -> Dict[str, int]:
    dist: Dict[str, int] = {}
    for r in records:
        v = r.get(field)
        if v and str(v).strip() not in ("", "None", "null", "N/A", "nan"):
            dist[str(v).strip()] = dist.get(str(v).strip(), 0) + 1
    return dict(sorted(dist.items(), key=lambda x: -x[1])[:top])


# Function: _top_dist_multi
def _top_dist_multi(records: List[Dict], *fields: str, top: int = 8) -> Dict[str, int]:
    dist: Dict[str, int] = {}
    for r in records:
        for field in fields:
            v = r.get(field)
            if v and str(v).strip() not in ("", "None", "null", "N/A", "nan"):
                key = str(v).strip()
                dist[key] = dist.get(key, 0) + 1
                break  # first non-null per record to avoid double-counting
    return dict(sorted(dist.items(), key=lambda x: -x[1])[:top])


# Function: _compute_cloud_agreement
def _compute_cloud_agreement(records: List[Dict]) -> Tuple[int, int, int]:
    agree = disagree = partial = 0
    for r in records:
        c = (r.get("cast_cloud_suitability") or "").strip().lower()
        o = (r.get("corent_cloud_suitability") or "").strip().lower()
        if c and o:
            if c == o:
                agree += 1
            elif ("high" in c and "high" in o) or ("low" in c and "low" in o):
                partial += 1
            else:
                disagree += 1
    return agree, disagree, partial


# Function: _build_portfolio_distributions
def _build_portfolio_distributions(
    consolidated_records: List[Dict[str, Any]],
    statistics: Dict[str, Any],
) -> Dict[str, Any]:
    total          = len(consolidated_records)
    cloud_dist     = _top_dist_multi(consolidated_records, "cast_cloud_suitability", "corent_cloud_suitability")
    arch_dist      = _top_dist_multi(consolidated_records, "cast_application_architecture", "corent_architecture_type", "industry_architecture_type")
    plat_dist      = _top_dist_multi(consolidated_records, "corent_platform_host", "industry_platform_host", top=6)
    lang_dist      = _top_dist(consolidated_records, "cast_programming_language", top=8)
    env_dist       = _top_dist(consolidated_records, "corent_environment", top=6)
    inst_dist      = _top_dist_multi(consolidated_records, "corent_install_type", "industry_install_type", top=6)
    os_dist        = _top_dist(consolidated_records, "corent_operating_system", top=8)
    db_engine_dist = _top_dist(consolidated_records, "corent_db_engine", top=6)
    coupling_dist  = _top_dist(consolidated_records, "cast_component_coupling", top=5)
    code_design_dist = _top_dist(consolidated_records, "cast_code_design", top=5)
    app_type_dist  = _top_dist(consolidated_records, "industry_application_type", top=6)
    ha_dr_dist     = _top_dist(consolidated_records, "corent_ha_dr_requirements", top=5)
    stability_dist = _top_dist(consolidated_records, "corent_application_stability", top=5)
    deploy_geo_dist = _top_dist(consolidated_records, "corent_deployment_geography", top=5)
    mainframe_dist = _top_dist(consolidated_records, "corent_mainframe_dependency", top=4)
    cots_dist      = _top_dist(consolidated_records, "corent_app_cots_vs_non_cots", top=4)
    src_avail_dist = _top_dist(consolidated_records, "cast_source_code_availability", top=4)

    cloud_agree, cloud_disagree, cloud_partial = _compute_cloud_agreement(consolidated_records)

    ai_fill_count = sum(1 for r in consolidated_records if r.get("ai_predicted_columns"))
    ai_field_freq: Dict[str, int] = {}
    for r in consolidated_records:
        for col in (r.get("ai_predicted_columns") or []):
            ai_field_freq[col] = ai_field_freq.get(col, 0) + 1
    top_ai_fields = dict(sorted(ai_field_freq.items(), key=lambda x: -x[1])[:10])

    return {
        "total_apps":                     total,
        "match_percentage":               statistics.get("match_percentage"),
        "corent_source_rows":             statistics.get("corent_source_rows", 0),
        "cast_source_rows":               statistics.get("cast_source_rows", 0),
        "industry_source_rows":           statistics.get("industry_source_rows", 0),
        "apps_with_ai_fill":              ai_fill_count,
        "top_ai_predicted_fields":        top_ai_fields,
        "cloud_suitability_dist":         cloud_dist,
        "corent_cloud_suitability_dist":  _top_dist(consolidated_records, "corent_cloud_suitability"),
        "cast_cloud_suitability_dist":    _top_dist(consolidated_records, "cast_cloud_suitability"),
        "cross_source_cloud_agreement":   {
            "agree": cloud_agree, "partial": cloud_partial, "disagree": cloud_disagree,
        },
        "cast_architecture_dist":         _top_dist(consolidated_records, "cast_application_architecture"),
        "corent_architecture_dist":       _top_dist(consolidated_records, "corent_architecture_type"),
        "programming_language_dist":      lang_dist,
        "component_coupling_dist":        coupling_dist,
        "code_design_dist":               code_design_dist,
        "source_code_availability_dist":  src_avail_dist,
        "platform_host_dist":             plat_dist,
        "operating_system_dist":          os_dist,
        "db_engine_dist":                 db_engine_dist,
        "environment_dist":               env_dist,
        "install_type_dist":              inst_dist,
        "deployment_geography_dist":      deploy_geo_dist,
        "application_type_dist":          app_type_dist,
        "application_stability_dist":     stability_dist,
        "ha_dr_requirements_dist":        ha_dr_dist,
        "mainframe_dependency_dist":      mainframe_dist,
        "cots_vs_non_cots_dist":          cots_dist,
    }


# ---------------------------------------------------------------------------
# Backfill helpers — used by _backfill_full_app_lists
# ---------------------------------------------------------------------------

_BACKFILL_PLACEHOLDER_IDS = {
    "...", "\u2026", "app_id", "<app_id>", "actual_app_id",
    "<actual_app_id>", "app-id", "appid", "example", "n/a",
    "sample_app_id", "your_app_id",
}


# Function: _is_placeholder_app_id
def _is_placeholder_app_id(v: str) -> bool:
    return (
        not v
        or v.lower() in _BACKFILL_PLACEHOLDER_IDS
        or v.startswith("<")
        or v.startswith("...")
    )


# Function: _pick_nonempty
def _pick_nonempty(*fields: str, record: Dict) -> str:
    for f in fields:
        v = record.get(f)
        if v and str(v).strip() not in ("", "None", "null", "N/A", "nan"):
            return str(v).strip()
    return ""


# Function: _annotation_description_parts
def _annotation_description_parts(
    arch: str, lang: str, platform: str, env: str, os_: str,
    db_eng: str, ha_dr: str, coupling: str,
) -> List[str]:
    parts = []
    if arch:
        parts.append(f"{arch} architecture")
    if lang:
        parts.append(f"built in {lang}")
    if platform:
        parts.append(f"runs on {platform}")
    if env:
        parts.append(f"{env} environment")
    if os_:
        parts.append(f"{os_} OS")
    if db_eng:
        parts.append(f"{db_eng} DB")
    if ha_dr:
        parts.append(f"{ha_dr} HA/DR")
    if coupling:
        parts.append(f"{coupling} component coupling")
    return parts


# Function: _annotation_extras
def _annotation_extras(cloud: str, src: str) -> List[str]:
    cloud_part = f"{cloud} cloud suitability" if cloud else ""
    src_part = (
        "no source code available" if src and "not" in src.lower()
        else ("source code available" if src else "")
    )
    return [x for x in (cloud_part, src_part) if x]


# Function: _rule_annotation_for_record
def _rule_annotation_for_record(r: Dict) -> str:
    app_id   = _pick_nonempty("app_id",   record=r)
    app_name = _pick_nonempty("app_name", record=r) or app_id
    arch     = _pick_nonempty("cast_application_architecture", "corent_architecture_type",
                              "industry_architecture_type", record=r)
    lang     = _pick_nonempty("cast_programming_language", record=r)
    cloud    = _pick_nonempty("cast_cloud_suitability", "corent_cloud_suitability", record=r)
    platform = _pick_nonempty("corent_platform_host", "industry_platform_host", record=r)
    env      = _pick_nonempty("corent_environment", record=r)
    os_      = _pick_nonempty("corent_operating_system", record=r)
    src      = _pick_nonempty("cast_source_code_availability", record=r)
    coupling = _pick_nonempty("cast_component_coupling", record=r)
    db_eng   = _pick_nonempty("corent_db_engine", record=r)
    ha_dr    = _pick_nonempty("corent_ha_dr_requirements", record=r)

    parts = _annotation_description_parts(arch, lang, platform, env, os_, db_eng, ha_dr, coupling)
    extras = _annotation_extras(cloud, src)

    base = f"{app_name}: " + (", ".join(parts) if parts else "infrastructure record")
    if extras:
        base += " \u2014 " + ", ".join(extras)
    return base


# Function: _rule_action_score_for_record
def _rule_action_score_for_record(r: Dict) -> Tuple[int, str, str]:
    cloud     = _pick_nonempty("cast_cloud_suitability", "corent_cloud_suitability", record=r).lower()
    src       = _pick_nonempty("cast_source_code_availability", record=r).lower()
    coupling  = _pick_nonempty("cast_component_coupling", record=r).lower()
    cots      = _pick_nonempty("corent_app_cots_vs_non_cots", record=r).lower()
    mainframe = _pick_nonempty("corent_mainframe_dependency", record=r).lower()

    score = 0
    action = "Rehost"
    rationale_parts: List[str] = []

    if "low" in cloud:
        score += 3; action = "Refactor"; rationale_parts.append("low cloud readiness")
    elif "medium" in cloud or "moderate" in cloud:
        score += 1; action = "Replatform"; rationale_parts.append("medium cloud readiness")
    elif "high" in cloud:
        action = "Rehost"; rationale_parts.append("high cloud readiness")

    if "not" in src and "available" in src:
        score += 2; action = "Replace"; rationale_parts.append("no source code")
    if "high" in coupling or "tight" in coupling:
        score += 1; rationale_parts.append("high component coupling")
    if "cots" in cots:
        action = "Replace"; rationale_parts.append("COTS application")
    if "yes" in mainframe or "dependent" in mainframe:
        score += 2; rationale_parts.append("mainframe dependency")

    rationale = "; ".join(rationale_parts) if rationale_parts else "standard assessment"
    return score, action, rationale


# ---------------------------------------------------------------------------
# Prompt-building helpers — reduce function body sizes
# ---------------------------------------------------------------------------

# Function: _build_few_shot_block
def _build_few_shot_block(sample_records: Optional[List[Dict]], null_fields: List[str]) -> str:
    if not sample_records:
        return ""
    examples = []
    for sr in sample_records[:3]:
        example_json = json.dumps(
            {k: sr.get(k) for k in null_fields if sr.get(k)}, ensure_ascii=False
        )
        examples.append(f"  Example: {example_json}")
    if not examples:
        return ""
    return (
        "\nHere are example values from similar records:\n"
        + "\n".join(examples)
        + "\n"
    )


# Function: _build_predict_missing_prompt
def _build_predict_missing_prompt(
    source: str,
    schema_hints: str,
    known_pairs: Dict[str, Any],
    null_fields: List[str],
    few_shot_block: str,
) -> str:
    return (
        f"You are an expert enterprise application portfolio analyst.\n"
        "You have been given a partially complete application record from an IT rationalization assessment.\n"
        "Your task is to intelligently predict/fill the missing (NULL) fields based on the known field values\n"
        "and your knowledge of enterprise application patterns.\n\n"
        f"Schema context ({source} table columns): {schema_hints}\n\n"
        "Known field values:\n"
        f"{json.dumps(known_pairs, indent=2, ensure_ascii=False)}\n"
        f"{few_shot_block}\n"
        "Fields that are NULL and need prediction:\n"
        f"{json.dumps(null_fields, ensure_ascii=False)}\n\n"
        "Instructions:\n"
        "- Analyze the known fields for patterns (e.g. architecture type → cloud suitability, OS → virtualization state).\n"
        "- Provide the most likely realistic enterprise values for each NULL field.\n"
        "- Return ONLY a JSON object with keys matching the NULL field names and predicted string values.\n"
        "- Do NOT include any explanation — only the JSON object.\n"
        "- If a field cannot reasonably be predicted, use null in the JSON.\n\n"
        "JSON predictions:"
    )


# Function: _build_batch_items_for_prompt
def _build_batch_items_for_prompt(
    batch: List[Dict[str, Any]],
    priority_fields: Optional[List[str]],
    skip_keys: frozenset,
) -> Tuple[List[Dict[str, Any]], Dict[int, List[str]]]:
    batch_items: List[Dict[str, Any]] = []
    idx_null_map: Dict[int, List[str]] = {}
    important = {"app_name", "app_id", "server_name", "operating_system",
                 "application_architecture", "architecture_type",
                 "programming_language", "component_coupling",
                 "platform_host", "environment", "server_type"}

    for local_idx, record in enumerate(batch):
        all_null = [
            k for k, v in record.items()
            if k not in skip_keys and (v is None or str(v).strip() == "")
        ]
        null_fields = (
            [f for f in all_null if f in priority_fields]
            if priority_fields else all_null
        )
        if not null_fields:
            continue
        known = {
            k: v for k, v in record.items()
            if k not in skip_keys
            and v is not None and str(v).strip() != ""
            and k not in ("app_id", "source_row_index")
        }
        if len(known) > 12:
            hi = {k: v for k, v in known.items() if k in important}
            lo = {k: v for k, v in known.items() if k not in important}
            known = {**hi, **dict(list(lo.items())[:max(0, 12 - len(hi))])}
        batch_items.append({"idx": local_idx, "known": known, "null_fields": null_fields})
        idx_null_map[local_idx] = null_fields

    return batch_items, idx_null_map


_BATCH_FIELD_GUIDANCE: Dict[str, str] = {
    "corent": (
        "Field prediction rules:\n"
        "- app_name: REQUIRED — derive from app_id text, server_name pattern, "
        "or business_owner. Strip prefixes like 'APP-', expand abbreviations. "
        "Never return null for app_name.\n"
        "- architecture_type: choose ONE of: Monolithic, SOA, Client-Server, "
        "Web-Based, Microservices, N-Tier, Mainframe. Infer from OS, "
        "virtualization_state, platform_host.\n"
        "- cloud_suitability: Low / Medium / High. Infer from architecture_type "
        "and operating_system.\n"
    ),
    "cast": (
        "Field prediction rules:\n"
        "- application_architecture: REQUIRED — choose ONE of: Monolithic, SOA, "
        "Microservices, Client-Server, Web-Based, N-Tier, Batch, Event-Driven. "
        "Infer from programming_language (COBOL→Batch/Monolithic, Java/Spring→SOA, "
        ".NET→N-Tier, Python/Node.js→Microservices) AND component_coupling "
        "(High coupling→Monolithic, Low coupling→Microservices/SOA).\n"
        "- app_name: expand app_id abbreviation into a readable application name.\n"
        "- cloud_suitability: infer from programming_language and component_coupling.\n"
    ),
    "industry": (
        "Field prediction rules:\n"
        "- app_name: expand app_id into a readable application name using "
        "business_owner and application_type as context.\n"
        "- capabilities: list core business functions inferred from application_type "
        "and architecture_type.\n"
    ),
}


# Function: _build_batch_prompt_and_params
def _build_batch_prompt_and_params(
    batch_items: List[Dict[str, Any]],
    schema_hints: str,
    source: str,
) -> Tuple[str, int, int]:
    field_guidance = _BATCH_FIELD_GUIDANCE.get(source, "")
    prompt = (
        f"Enterprise IT portfolio analyst. Table: {source}.\n"
        + (field_guidance if field_guidance else "")
        + "Predict null fields. Output ONLY a compact JSON array, no extra text.\n"
        'Format: [{"idx":0,"predictions":{"field":"value"}}]\n'
        f"Records:\n{json.dumps(batch_items, separators=(',',':'), ensure_ascii=False)}\n"
        "JSON:"
    )
    timeout = min(30 + 5 * len(batch_items), 240)
    num_predict = max(512, min(80 * len(batch_items), 3072))
    return prompt, timeout, num_predict


# Function: _apply_batch_prediction_results
def _apply_batch_prediction_results(
    parsed_items: List[Dict[str, Any]],
    idx_null_map: Dict[int, List[str]],
    batch_results: List[Tuple[Dict, List, Dict]],
    batch_len: int,
) -> None:
    for item in parsed_items:
        idx = item.get("idx")
        if not isinstance(idx, int) or idx >= batch_len:
            continue
        null_fields = idx_null_map.get(idx, [])
        preds = {
            k: v
            for k, v in item.get("predictions", {}).items()
            if k in null_fields and v is not None
        }
        predicted_cols = list(preds.keys())
        batch_results[idx] = (preds, predicted_cols, {col: 0.75 for col in predicted_cols})


# Function: _build_slim_sample_records
def _build_slim_sample_records(consolidated_records: List[Dict[str, Any]]) -> List[Dict]:
    _KEEP = {
        "app_id", "app_name",
        "cast_application_architecture", "cast_programming_language",
        "cast_cloud_suitability", "cast_component_coupling",
        "cast_code_design", "cast_source_code_availability",
        "corent_architecture_type", "corent_platform_host",
        "corent_cloud_suitability", "corent_operating_system",
        "corent_environment", "corent_install_type", "corent_db_engine",
        "corent_application_stability", "corent_mainframe_dependency",
        "corent_deployment_geography", "corent_ha_dr_requirements",
        "corent_app_cots_vs_non_cots",
        "industry_application_type", "industry_platform_host",
        "industry_install_type", "industry_business_owner",
        "ai_predicted_columns",
    }
    return [
        {k: v for k, v in r.items() if k in _KEEP and v not in (None, "", "None")}
        for r in consolidated_records[:15]
    ]


# Function: _build_deep_analysis_prompt
def _build_deep_analysis_prompt(stats_json: str, pred_json: str, sample_json: str) -> str:
    return (
        "You are a senior enterprise architect performing application portfolio rationalization.\n"
        "The dataset merges three sources:\n"
        "  - CORENT: infrastructure/server data (fields prefixed corent_)\n"
        "  - CAST:   code analysis data (fields prefixed cast_)\n"
        "  - Industry Template: business context data (fields prefixed industry_)\n\n"
        "CRITICAL INSTRUCTIONS:\n"
        "1. Base ALL analysis STRICTLY on the actual distributions and sample records below.\n"
        "2. Quote specific counts and percentages from the data (e.g. '47 of 195 apps').\n"
        "3. Highlight cross-source DISAGREEMENTS (e.g. CAST says High cloud-ready but CORENT says Low).\n"
        "4. Identify the most AI-predicted fields and explain what that means for data confidence.\n"
        "5. Every risk and recommendation must cite actual field values from the data.\n"
        "6. Do NOT write generic boilerplate — every sentence must be tied to the data.\n\n"
        f"=== PORTFOLIO DISTRIBUTIONS ===\n{stats_json}\n\n"
        f"=== AI PREDICTION SUMMARY ===\n{pred_json}\n\n"
        f"=== SAMPLE APP RECORDS (first 25) ===\n{sample_json}\n\n"
        "Return a single minified JSON object with EXACTLY these keys (no extras):\n"
        "{\n"
        '  "summary": "3-sentence executive summary citing exact counts, match%, cloud distribution, '
        'and key finding from cross-source comparison",\n'
        '  "cloud_readiness": "detailed paragraph citing BOTH corent_cloud_suitability_dist AND '
        'cast_cloud_suitability_dist counts, cross-source agreement stats, and top cloud blockers '
        'from architecture/coupling data",\n'
        '  "risk_observations": ["≥5 specific risks each citing actual distribution values, '
        'disagreements between CORENT and CAST, AI-filling gaps, or concerning patterns"],\n'
        '  "recommendations": ["≥5 specific actionable recommendations each tied to '
        'a distribution value or pattern, with priority ordering"],\n'
        '  "per_app_notes": {"<ACTUAL_APP_ID>": "one-line insight combining CAST arch + CORENT infra '
        '+ cloud suitability — use real app_id values from the sample records, NOT the literal string app_id"},\n'
        '  "correlation_quality": "assessment citing source row counts, match%, '
        'AI fill rate, and which fields have highest AI-prediction frequency (data gaps)",\n'
        '  "migration_roadmap": [{"phase": 1, "title": "...", "app_count": 0, '
        '"rationale": "tied to actual cloud_suitability and architecture distribution counts"}],\n'
        '  "technical_debt_summary": "paragraph citing programming_language_dist, '
        'cast_architecture_dist, component_coupling_dist, code_design_dist, '
        'and source_code_availability_dist with exact counts",\n'
        '  "modernization_priorities": [{"app_id": "...", "app_name": "...", '
        '"priority": 1, "rationale": "specific reason from actual field values", '
        '"recommended_action": "Retire|Rehost|Replatform|Refactor|Replace"}]\n'
        "}\n"
        "Return ONLY the JSON object. No markdown fences, no explanations outside JSON."
    )


# Function: _build_standardization_summary_input
def _build_standardization_summary_input(
    infra: Dict, code: Dict, tech: Dict, recs: List, roi: Dict,
) -> Dict[str, Any]:
    return {
        "total_applications":             infra.get("total_applications", 0),
        "total_servers":                  infra.get("total_servers", 0),
        "cloud_readiness_distribution":   infra.get("cloud_readiness", {}),
        "environment_distribution":       infra.get("environment_distribution", {}),
        "operating_systems":              tech.get("operating_systems", {}),
        "database_engines":               tech.get("database_engines", {}),
        "server_types":                   tech.get("server_types", {}),
        "standardization_potential":      tech.get("standardization_potential", 0),
        "architecture_distribution":      code.get("architecture_distribution", {}),
        "top_languages":                  code.get("top_languages", {}),
        "source_code_availability":       code.get("source_code_availability", "N/A"),
        "cloud_ready_apps":               code.get("cloud_ready_apps", 0),
        "rule_based_recommendations_count": len(recs),
        "estimated_savings_summary":      roi.get("roi_summary", "N/A"),
    }


# Function: _load_all_records_fallback
def _load_all_records_fallback(all_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """If all_records is empty (e.g. first-ever run), try loading from ConsolidatedApp DB."""
    if all_records:
        return all_records
    try:
        from app.models.consolidated_app import ConsolidatedApp as _CA
        db_rows = _CA.query.all()
        if db_rows:
            return [
                {k: v for k, v in r.__dict__.items() if not k.startswith("_")}
                for r in db_rows
            ]
    except Exception:
        pass
    return all_records


# Function: _backfill_per_app_notes
def _backfill_per_app_notes(analysis: Dict[str, Any], all_records: List[Dict[str, Any]]) -> None:
    cleaned_notes: Dict[str, Any] = {
        k: v for k, v in (analysis.get("per_app_notes") or {}).items()
        if not _is_placeholder_app_id(str(k))
    }
    for rec in all_records:
        aid = (rec.get("app_id") or "").strip()
        if not aid or _is_placeholder_app_id(aid) or aid in cleaned_notes:
            continue
        cleaned_notes[aid] = _rule_annotation_for_record(rec)
    analysis["per_app_notes"] = cleaned_notes


# Function: _backfill_modernization_priorities
def _backfill_modernization_priorities(analysis: Dict[str, Any], all_records: List[Dict[str, Any]]) -> None:
    llm_prio: List[Dict] = [
        p for p in (analysis.get("modernization_priorities") or [])
        if not _is_placeholder_app_id(str(p.get("app_id", "")).strip())
    ]
    covered: set = {str(p.get("app_id", "")).strip().upper() for p in llm_prio}

    extra: List[Dict] = []
    for rec in all_records:
        aid = (rec.get("app_id") or "").strip()
        if not aid or aid.upper() in covered:
            continue
        score, action, rationale = _rule_action_score_for_record(rec)
        extra.append({
            "app_id":             aid,
            "app_name":           (rec.get("app_name") or "").strip() or aid,
            "priority":           0,
            "recommended_action": action,
            "rationale":          rationale,
            "_score":             score,
        })

    extra.sort(key=lambda x: -x.pop("_score", 0))
    # Re-number all priorities so they are contiguous 1…N
    full_list = llm_prio + extra
    for idx, p in enumerate(full_list, start=1):
        p["priority"] = idx

    analysis["modernization_priorities"] = full_list


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class OllamaService:
    """Wraps all Ollama LLM calls used in the correlation pipeline."""

    # ------------------------------------------------------------------ #
    #  Health / status                                                      #
    # ------------------------------------------------------------------ #

    # Function: is_available
    @staticmethod
    def is_available() -> bool:
        """Return True if Ollama is reachable and has at least one model."""
        return _available_model() is not None

    # Function: health_info
    @staticmethod
    def health_info() -> Dict[str, Any]:
        """Return a dict with Ollama status details (for API exposure)."""
        try:
            resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if resp.status_code != 200:
                return {"available": False, "models": [], "selected_model": None}
            models = [m.get("name") for m in resp.json().get("models", [])]
            selected = _available_model()
            return {
                "available": True,
                "base_url": OLLAMA_BASE_URL,
                "models": models,
                "selected_model": selected,
            }
        except Exception as exc:
            return {"available": False, "error": str(exc), "models": [], "selected_model": None}

    # ------------------------------------------------------------------ #
    #  Null / missing value prediction                                      #
    # ------------------------------------------------------------------ #

    # Function: predict_missing_fields
    @staticmethod
    def predict_missing_fields(
        record: Dict[str, Any],
        source: str = "generic",
        sample_records: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[Dict[str, Any], List[str], Dict[str, float]]:
        """
        Use the LLM to predict null / missing field values in *record*.

        Parameters
        ----------
        record : dict
            Flat dict of fieldname → value.  None / empty string → "NULL".
        source : str
            One of "corent", "cast", "industry" — used to select schema hint.
        sample_records : list[dict] | None
            Up to 3 representative non-null records for few-shot context.

        Returns
        -------
        predictions : dict
            {field_name: predicted_value} for every field that was null.
        predicted_columns : list[str]
            Names of columns that were AI-filled.
        confidence_map : dict
            {field_name: confidence_score (0.0–1.0)}.
            Ollama doesn't expose per-token probabilities, so we use a fixed
            confidence of 0.75 for all LLM predictions (indicating "inferred,
            not measured").
        """
        model = _available_model()
        if model is None:
            return {}, [], {}

        # Identify null fields
        null_fields = [k for k, v in record.items() if v is None or str(v).strip() == ""]
        if not null_fields:
            return {}, [], {}

        known_pairs = {k: v for k, v in record.items() if v is not None and str(v).strip() != ""}

        schema_hints = {
            "corent": CORENT_SCHEMA_CONTEXT,
            "cast": CAST_SCHEMA_CONTEXT,
            "industry": INDUSTRY_SCHEMA_CONTEXT,
        }.get(source, "")

        few_shot_block = _build_few_shot_block(sample_records, null_fields)
        prompt = _build_predict_missing_prompt(source, schema_hints, known_pairs, null_fields, few_shot_block)

        try:
            raw_response = _generate(model, prompt, timeout=30, num_predict=2048)
            predictions = _extract_json(raw_response)

            predictions = {k: v for k, v in predictions.items() if k in null_fields and v is not None}
            predicted_columns = list(predictions.keys())
            confidence_map = {col: 0.75 for col in predicted_columns}

            logger.info(
                "OllamaService.predict_missing_fields [model=%s, source=%s]: "
                "predicted %d / %d null fields",
                model, source, len(predicted_columns), len(null_fields),
            )
            return predictions, predicted_columns, confidence_map

        except Exception as exc:
            logger.warning("OllamaService: prediction failed — %s", exc)
            return {}, [], {}

    # ------------------------------------------------------------------ #
    #  LLM Correlation Analysis                                            #
    # ------------------------------------------------------------------ #

    # Function: generate_correlation_analysis
    @staticmethod
    def generate_correlation_analysis(
        consolidated_records: List[Dict[str, Any]],
        statistics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Ask the LLM to analyse the consolidated dataset and return insights:
          - Overall portfolio findings
          - Cloud readiness summary
          - Risk observations
          - Top recommendations
          - Per-app brief annotations (first 20 apps max)

        Parameters
        ----------
        consolidated_records : list[dict]
            Full consolidated records (use a sample for very large datasets).
        statistics : dict
            Aggregate statistics from the correlation pipeline.

        Returns
        -------
        dict with keys: summary, cloud_readiness_insight, risk_observations,
                        recommendations, per_app_notes, model_used
        """
        model = _available_model()
        if model is None:
            return {
                "available": False,
                "summary": "Ollama LLM not available on localhost:11434. "
                           "Install Ollama and pull a model (e.g. `ollama pull llama3`).",
                "model_used": None,
            }

        # Summarise to avoid huge prompts (max 30 records for the per-app block)
        sample = consolidated_records[:30]
        sample_json = json.dumps(sample, indent=2, ensure_ascii=False, default=str)

        stats_json = json.dumps(statistics, indent=2, ensure_ascii=False, default=str)

        prompt = f"""You are a senior enterprise application portfolio strategist.
You have been provided with a consolidated data set that merges CORENT (infrastructure),
CAST (code analysis), and Industry Template data for {statistics.get('total_apps', 'N/A')} applications.

== Portfolio Statistics ==
{stats_json}

== Sample Consolidated Records (up to 30) ==
{sample_json}

Provide a comprehensive correlation analysis with the following sections.
Return your answer as a single minified JSON object with exactly these keys:
  "summary"            : 2-3 sentence executive summary of the overall portfolio
  "cloud_readiness"    : observations on cloud-readiness distribution and key blockers
  "risk_observations"  : top 3-5 risk findings (string array)
  "recommendations"    : top 5 actionable recommendations (string array)
  "per_app_notes"      : object mapping app_id → one-line annotation (first 20 apps only)
  "correlation_quality": brief assessment of data quality and match confidence

Return ONLY the JSON object. No markdown, no explanation outside the JSON."""

        try:
            raw_response = _generate(model, prompt, timeout=90, num_predict=4096)
            analysis = _extract_json(raw_response)

            # Ensure required keys exist
            defaults = {
                "summary": "",
                "cloud_readiness": "",
                "risk_observations": [],
                "recommendations": [],
                "per_app_notes": {},
                "correlation_quality": "",
            }
            for key, default in defaults.items():
                if key not in analysis:
                    analysis[key] = default

            analysis["available"] = True
            analysis["model_used"] = model
            return analysis

        except Exception as exc:
            logger.warning("OllamaService: correlation analysis failed — %s", exc)
            return {
                "available": False,
                "error": str(exc),
                "summary": "LLM analysis failed. Check Ollama logs.",
                "model_used": model,
            }

    # ------------------------------------------------------------------ #
    #  Per-app annotation (lightweight, called per record)                 #
    # ------------------------------------------------------------------ #

    # ------------------------------------------------------------------ #
    #  Model selection helper                                              #
    # ------------------------------------------------------------------ #

    # Function: get_selected_model
    @staticmethod
    def get_selected_model() -> Optional[str]:
        """Return the model that will be used for predictions (first available)."""
        return _available_model()

    # ------------------------------------------------------------------ #
    #  Technical Evaluation market enrichment                             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def market_search_status() -> Dict[str, Any]:
        return {
            "provider": MARKET_SEARCH_PROVIDER,
            "configured": bool(MARKET_SEARCH_URL),
            "response_format": MARKET_SEARCH_RESPONSE_FORMAT,
            "engines": MARKET_SEARCH_ENGINES,
            "product_queries_enabled": bool(MARKET_SEARCH_URL),
        }

    # Function: discover_market_capability_matrix
    @staticmethod
    def discover_market_capability_matrix(
        topic: str,
        products: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Discover a topic schema globally, then validate every product against it."""
        model = _available_model(preferred="qwen3.5:9b") or _available_model()
        if model is None:
            raise RuntimeError("Ollama is unavailable; dynamic capability discovery cannot run")

        topic_evidence: List[str] = []
        product_evidence: Dict[str, List[str]] = {}
        search_errors: List[str] = []
        search_subject = _market_search_subject(topic)
        queries = [
            *[("__topic__", query) for query in _market_topic_queries(topic)],
            *[
                (
                    str(product.get("id")),
                    f'"{product.get("product", "")}" "{search_subject}" capabilities features',
                )
                for product in products[:MARKET_SEARCH_MAX_PRODUCTS]
            ],
        ]
        with ThreadPoolExecutor(max_workers=min(6, len(queries))) as executor:
            futures = {executor.submit(_global_market_search, query): row_id for row_id, query in queries}
            for future in as_completed(futures):
                row_id = futures[future]
                try:
                    evidence = future.result()
                except Exception as exc:
                    search_errors.append(f"{row_id}: {exc}")
                    logger.warning("Global market search failed for %s: %s", row_id, exc)
                    continue
                if row_id == "__topic__":
                    topic_evidence.extend(evidence)
                else:
                    product_evidence[row_id] = evidence

        evidence_count = len(topic_evidence) + sum(len(items) for items in product_evidence.values())
        if MARKET_SEARCH_REQUIRED and evidence_count == 0:
            detail = search_errors[0] if search_errors else "no public results returned"
            raise RuntimeError(f"Global market search produced no evidence ({detail})")

        discovery_prompt = (
            "You are defining an evidence-grounded product comparison matrix.\n"
            "Derive the distinct, decision-relevant capabilities for the selected topic from the supplied public search evidence.\n"
            "Capabilities become spreadsheet columns, so use concise noun phrases, merge synonyms, exclude vendor names, product names,"
            " generic words such as Capability/Feature, and Product Type. Do not invent a capability unsupported by the evidence.\n"
            "Return ONLY JSON: {\"capabilities\":[\"Capability A\",\"Capability B\"]}.\n\n"
            f"TOPIC: {topic}\n"
            f"DOMAIN_CONSTRAINT: {'Industrial process-plant alarm management; exclude residential security, home automation, healthcare, and consumer alarm systems.' if 'alarm management' in search_subject.casefold() else 'Enterprise and industrial software.'}\n"
            f"PRODUCTS: {json.dumps([item.get('product') for item in products], ensure_ascii=False)}\n"
            f"TOPIC_SEARCH_EVIDENCE: {json.dumps(topic_evidence, ensure_ascii=False)}\n"
            f"PRODUCT_SEARCH_EVIDENCE_SAMPLE: {json.dumps({key: [text[:500] for text in value[:2]] for key, value in list(product_evidence.items())[:25]}, ensure_ascii=False)}\n"
        )
        raw = _generate(
            model,
            discovery_prompt,
            timeout=120,
            force_json=True,
            num_predict=1200,
            num_ctx=12288,
            temperature=0.05,
            think=False,
        )
        parsed = _extract_json(raw)
        raw_capabilities = parsed.get("capabilities", []) if isinstance(parsed, dict) else []
        capabilities: List[str] = _portfolio_grounded_capabilities(topic, products)
        seen = {name.casefold() for name in capabilities}
        for item in raw_capabilities if isinstance(raw_capabilities, list) else []:
            name = item.get("name") if isinstance(item, dict) else item
            name = " ".join(str(name or "").strip().split())[:120]
            key = name.casefold()
            if not name or key in seen or key in {"capability", "capabilities", "feature", "features", "product type"}:
                continue
            seen.add(key)
            capabilities.append(name)
        if not capabilities:
            raise RuntimeError("Ollama did not return an evidence-grounded capability schema")

        capability_terms = " ".join(f'"{name}"' for name in capabilities[:8])
        targeted_queries = [
            (
                str(product.get("id")),
                f'"{product.get("product", "")}" "{search_subject}" {capability_terms}',
            )
            for product in products[:MARKET_SEARCH_MAX_PRODUCTS]
        ]
        if targeted_queries:
            with ThreadPoolExecutor(max_workers=min(6, len(targeted_queries))) as executor:
                futures = {
                    executor.submit(_global_market_search, query): row_id
                    for row_id, query in targeted_queries
                }
                for future in as_completed(futures):
                    row_id = futures[future]
                    try:
                        targeted = future.result()
                    except Exception as exc:
                        logger.warning("Capability-specific market search failed for %s: %s", row_id, exc)
                        continue
                    product_evidence[row_id] = list(dict.fromkeys(
                        product_evidence.get(row_id, []) + targeted
                    ))[:8]

        product_type_header = "COTS / Available in Market / Custom Products"
        headers = capabilities + [product_type_header]
        enriched_products = []
        for product in products:
            row = dict(product)
            row["market_evidence"] = product_evidence.get(str(product.get("id")), [])
            enriched_products.append(row)
        values = OllamaService.generate_market_product_enrichment(
            topic,
            enriched_products,
            headers,
        )
        return {
            "capabilities": capabilities,
            "product_type_headers": [product_type_header],
            "headers": headers,
            "values": values,
            "evidence_count": len(topic_evidence) + sum(len(items) for items in product_evidence.values()),
        }

    # Function: generate_market_product_enrichment
    @staticmethod
    def generate_market_product_enrichment(
        topic: str,
        products: List[Dict[str, Any]],
        highlighted_headers: List[str],
        batch_size: int = 12,
    ) -> Dict[str, Dict[str, str]]:
        """Populate highlighted capability columns using market-style LLM inference.

        Returns a map keyed by row id (as string) to {header: value}.
        """
        if not products or not highlighted_headers:
            return {}

        default_row = {header: "Unknown" for header in highlighted_headers}
        defaults = {str(product.get("id")): dict(default_row) for product in products}

        model = _available_model(preferred="qwen3.5:9b") or _available_model()
        if model is None:
            return defaults

        results: Dict[str, Dict[str, str]] = {}
        for start in range(0, len(products), batch_size):
            batch = products[start:start + batch_size]
            payload = [
                {
                    "id": str(item.get("id")),
                    "product": str(item.get("product") or "").strip(),
                    "size": str(item.get("size") or "").strip(),
                    "context": item.get("context") or {},
                    "market_evidence": [str(text)[:500] for text in (item.get("market_evidence") or [])[:3]],
                }
                for item in batch
            ]
            prompt = (
                "You are a market intelligence analyst for industrial software and products.\n"
                "Given a category/topic and product list, perform market-level validation per capability column for each product.\n"
                "Use the supplied public market evidence first; product naming cues are not proof.\n"
                "Validate every product independently against every capability. Never copy one product's result to another.\n"
                "For capability columns, return exactly one of: Yes, No, Partial, Unknown.\n"
                "When a header refers to Product Type / COTS / Custom Products, return exactly one of: COTS, Custom, Hybrid, Unknown.\n"
                "If uncertain, return 'Unknown'.\n"
                "Return ONLY a JSON array.\n"
                "Each array element must be:\n"
                "{\"id\":\"row-id\",\"values\":{\"<header>\":\"<short value>\",...}}\n"
                "No markdown, no commentary.\n\n"
                f"TOPIC: {topic}\n"
                f"HIGHLIGHTED_HEADERS: {json.dumps(highlighted_headers, ensure_ascii=False)}\n"
                f"PRODUCT_ROWS: {json.dumps(payload, ensure_ascii=False)}\n"
            )

            try:
                raw = _generate(
                    model,
                    prompt,
                    timeout=90,
                    force_json=True,
                    num_predict=1600,
                    num_ctx=8192,
                    temperature=0.1,
                    think=False,
                )
                parsed = _extract_json_array(raw)
                if not parsed:
                    obj = _extract_json(raw)
                    if isinstance(obj, dict):
                        parsed = obj.get("results", []) if isinstance(obj.get("results"), list) else []
                for item in parsed:
                    row_id = str(item.get("id") or "").strip()
                    values = item.get("values") if isinstance(item.get("values"), dict) else {}
                    if not row_id:
                        continue
                    normalized = {}
                    for header in highlighted_headers:
                        value = values.get(header)
                        if value is None:
                            normalized[header] = "Unknown"
                        else:
                            text = str(value).strip()
                            normalized[header] = text[:500] if text else "Unknown"
                    results[row_id] = normalized
            except Exception as exc:
                logger.warning(
                    "OllamaService.generate_market_product_enrichment failed for batch start=%d: %s",
                    start,
                    exc,
                )

        final_map = dict(defaults)
        final_map.update(results)
        for product in products:
            row_id = str(product.get("id"))
            inferred = _portfolio_evidence_defaults(product, highlighted_headers)
            row_values = final_map.setdefault(row_id, dict(default_row))
            for header, value in inferred.items():
                is_product_type = any(
                    token in header.casefold()
                    for token in ("product type", "cots", "custom product", "available in market")
                )
                if is_product_type or row_values.get(header) in {None, "", "Unknown"}:
                    row_values[header] = value
        return final_map

    # ------------------------------------------------------------------ #
    #  Batch null/missing value prediction (performance-optimised)         #
    # ------------------------------------------------------------------ #

    # Priority fields per source — only these are sent to the LLM when null.
    # Less-important fields are left for heuristics or remain blank.
    # This cuts output tokens by ~60%, reducing generation time proportionally.
    _PRIORITY_NULL_FIELDS: Dict[str, List[str]] = {
        "corent": [
            "app_name", "architecture_type", "cloud_suitability", "environment",
            "virtualization_state", "distributed_architecture_design",
            "app_os_platform_cloud_suitability",
        ],
        "cast": [
            "app_name", "application_architecture", "cloud_suitability",
            "programming_language", "component_coupling",
            "source_code_availability",
        ],
        "industry": [
            "app_name", "capabilities", "architecture_type", "application_type",
            "install_type",
        ],
    }

    # Function: predict_missing_fields_batch
    @staticmethod
    def predict_missing_fields_batch(
        records: List[Dict[str, Any]],
        source: str = "generic",
        batch_size: int = 15,
    ) -> List[Tuple[Dict[str, Any], List[str], Dict[str, float]]]:
        """
        Batch variant of predict_missing_fields.

        Sends up to *batch_size* records to the LLM in a single API call,
        reducing total round-trips from N to ceil(N / batch_size).

        Returns
        -------
        List of (predictions, predicted_columns, confidence_map) in the same
        order as *records*.  Entries with no null fields return ({}, [], {}).
        """
        model = _available_model()
        if model is None:
            return [({}, [], {}) for _ in records]

        schema_hints = {
            "corent": CORENT_SCHEMA_CONTEXT,
            "cast":   CAST_SCHEMA_CONTEXT,
            "industry": INDUSTRY_SCHEMA_CONTEXT,
        }.get(source, "")

        priority_fields: Optional[List[str]] = OllamaService._PRIORITY_NULL_FIELDS.get(source)

        _skip_keys = frozenset((
            "id", "created_at", "updated_at", "template_id",
            "cast_analysis_id", "_ai_predicted", "_ai_confidence", "_ai_model",
        ))

        all_results: List[Tuple[Dict, List, Dict]] = []

        for batch_start in range(0, len(records), batch_size):
            batch = records[batch_start: batch_start + batch_size]
            batch_results: List[Tuple[Dict, List, Dict]] = [({}, [], {}) for _ in batch]

            batch_items, idx_null_map = _build_batch_items_for_prompt(
                batch, priority_fields, _skip_keys
            )

            if not batch_items:
                all_results.extend(batch_results)
                continue

            prompt, _batch_timeout, _batch_num_predict = _build_batch_prompt_and_params(
                batch_items, schema_hints, source
            )

            try:
                raw = _generate(
                    model, prompt,
                    timeout=_batch_timeout, force_json=True,
                    num_predict=_batch_num_predict, num_ctx=4096,
                )
                parsed_items = _parse_batch_prediction_payload(raw, expected_count=len(batch))
                if not parsed_items:
                    raise ValueError("Batch response did not contain a parseable JSON array")
                _apply_batch_prediction_results(parsed_items, idx_null_map, batch_results, len(batch))
            except Exception as exc:
                logger.warning(
                    "OllamaService.predict_missing_fields_batch "
                    "[source=%s, batch_start=%d]: skipping — %s",
                    source, batch_start, exc,
                )

            logger.info(
                "OllamaService batch [model=%s, source=%s, batch_start=%d]: %d predictions",
                model, source, batch_start,
                sum(len(r[1]) for r in batch_results),
            )
            all_results.extend(batch_results)

        return all_results

    # ------------------------------------------------------------------ #
    #  Deep Portfolio Correlation Analysis                                 #
    # ------------------------------------------------------------------ #

    # Function: generate_deep_correlation_analysis
    @staticmethod
    def generate_deep_correlation_analysis(
        consolidated_records: List[Dict[str, Any]],
        statistics: Dict[str, Any],
        predictions_summary: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Deep LLM analysis of the full portfolio *after* blank-value enrichment.

        Extends generate_correlation_analysis with:
          - 3-phase migration roadmap
          - Technical debt summary across the portfolio
          - Top modernisation priorities ranked by urgency

        Parameters
        ----------
        consolidated_records : list[dict]
            Enriched consolidated records (AI blank-filled).
        statistics : dict
            Aggregate stats (match_percentage, total_apps, etc.).
        predictions_summary : dict
            How many fields were AI-predicted, which model, etc.

        Returns
        -------
        dict with keys: summary, cloud_readiness, risk_observations,
                        recommendations, per_app_notes, correlation_quality,
                        migration_roadmap, technical_debt_summary,
                        modernization_priorities, model_used, available
        """
        model = _available_model()
        if model is None:
            return {
                "available": False,
                "summary": (
                    "LLM not reachable on localhost:11434. "
                    "Start Ollama and pull the model: `ollama pull mistral`"
                ),
                "model_used": None,
            }

        portfolio_distributions = _build_portfolio_distributions(consolidated_records, statistics)

        sample_slim = _build_slim_sample_records(consolidated_records)
        sample_json = json.dumps(sample_slim, ensure_ascii=False, default=str)
        stats_json  = json.dumps(portfolio_distributions, ensure_ascii=False, default=str)
        pred_json   = json.dumps(predictions_summary, ensure_ascii=False, default=str)

        prompt = _build_deep_analysis_prompt(stats_json, pred_json, sample_json)

        try:
            raw = _generate(model, prompt, timeout=180, num_predict=2048)
            analysis = _extract_json(raw)

            defaults = {
                "summary": "",
                "cloud_readiness": "",
                "risk_observations": [],
                "recommendations": [],
                "per_app_notes": {},
                "correlation_quality": "",
                "migration_roadmap": [],
                "technical_debt_summary": "",
                "modernization_priorities": [],
            }
            for key, default in defaults.items():
                if key not in analysis:
                    analysis[key] = default

            # ── Post-process: backfill per_app_notes & modernization_priorities
            # for ALL consolidated records not covered by the LLM sample ──────
            analysis = OllamaService._backfill_full_app_lists(
                analysis, consolidated_records
            )

            analysis["available"]   = True
            analysis["model_used"]  = model
            logger.info(
                "OllamaService.generate_deep_correlation_analysis [model=%s]: done", model
            )
            return analysis

        except Exception as exc:
            logger.warning("OllamaService.generate_deep_correlation_analysis failed: %s", exc)
            return {
                "available": False,
                "error": str(exc),
                "summary": "Deep LLM analysis failed. Check Ollama logs.",
                "model_used": model,
            }

    # ------------------------------------------------------------------ #
    #  Backfill all apps not covered by LLM sample                        #
    # ------------------------------------------------------------------ #

    # Function: _backfill_full_app_lists
    @staticmethod
    def _backfill_full_app_lists(
        analysis: Dict[str, Any],
        all_records: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        After the LLM returns analysis (based on a 15-record sample), add
        rule-based per_app_notes and modernization_priorities for every app
        that the LLM did not annotate.  LLM entries are kept as-is.
        """
        all_records = _load_all_records_fallback(all_records)
        _backfill_per_app_notes(analysis, all_records)
        _backfill_modernization_priorities(analysis, all_records)
        return analysis

    # ------------------------------------------------------------------ #
    #  Per-app annotation (lightweight, called per record)                 #
    # ------------------------------------------------------------------ #

    # ------------------------------------------------------------------ #
    #  Standardization & Consolidation LLM Analysis                       #
    # ------------------------------------------------------------------ #

    # Function: generate_standardization_insights
    @staticmethod
    def generate_standardization_insights(
        analysis_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        LLM-powered recommendations for the Standardization & Consolidation page.

        Receives the already-computed rule-based analysis and enriches it with
        natural-language narrative, phased roadmap, and prioritized actions.
        """
        model = _available_model()
        if model is None:
            return {
                "available": False, "model_used": None,
                "summary": "Ollama LLM not available. Start Ollama and pull a model.",
            }

        infra = analysis_data.get("infrastructure_analysis", {})
        code  = analysis_data.get("code_analysis", {})
        tech  = analysis_data.get("technology_standardization", {})
        recs  = analysis_data.get("business_value_recommendations", [])
        roi   = analysis_data.get("roi_analysis", {})

        summary_input = _build_standardization_summary_input(infra, code, tech, recs, roi)
        input_json = json.dumps(summary_input, ensure_ascii=False, default=str)

        prompt = (
            "You are a senior enterprise architect advising on application portfolio standardization.\n"
            "You have been given computed statistics from an IT rationalization assessment.\n"
            "Base ALL insights strictly on the numbers provided — cite specific counts.\n\n"
            f"=== PORTFOLIO STATISTICS ===\n{input_json}\n\n"
            "Return a single JSON object with EXACTLY these keys:\n"
            "{\n"
            '  "executive_summary": "3-4 sentence narrative citing specific counts and distributions",\n'
            '  "top_recommendations": [\n'
            '    {"priority": 1, "title": "...", "action": "...", "rationale": "citing data", "timeline": "..."},\n'
            '    {"priority": 2, "title": "...", "action": "...", "rationale": "citing data", "timeline": "..."},\n'
            '    {"priority": 3, "title": "...", "action": "...", "rationale": "citing data", "timeline": "..."},\n'
            '    {"priority": 4, "title": "...", "action": "...", "rationale": "citing data", "timeline": "..."},\n'
            '    {"priority": 5, "title": "...", "action": "...", "rationale": "citing data", "timeline": "..."}\n'
            '  ],\n'
            '  "consolidation_roadmap": [\n'
            '    {"phase": 1, "title": "...", "duration": "0-6 months", "focus": "...", "expected_outcome": "..."},\n'
            '    {"phase": 2, "title": "...", "duration": "6-12 months", "focus": "...", "expected_outcome": "..."},\n'
            '    {"phase": 3, "title": "...", "duration": "12-24 months", "focus": "...", "expected_outcome": "..."}\n'
            '  ],\n'
            '  "risk_highlights": ["risk citing data", "risk citing data", "risk citing data", "risk citing data", "risk citing data"],\n'
            '  "standardization_strategy": "2-3 sentences on the recommended technology standardization approach"\n'
            "}\n"
            "Return ONLY the JSON. No markdown fences, no text outside JSON."
        )

        try:
            raw = _generate(model, prompt, timeout=75, num_predict=800)
            result = _extract_json(raw)
            defaults: Dict[str, Any] = {
                "executive_summary": "",
                "top_recommendations": [],
                "consolidation_roadmap": [],
                "risk_highlights": [],
                "standardization_strategy": "",
            }
            for key, default in defaults.items():
                if key not in result:
                    result[key] = default
            result["available"]  = True
            result["model_used"] = model
            logger.info("OllamaService.generate_standardization_insights [model=%s]: done", model)
            return result
        except Exception as exc:
            logger.warning("OllamaService.generate_standardization_insights failed: %s", exc)
            return {"available": False, "error": str(exc), "model_used": model}

    # ------------------------------------------------------------------ #
    #  Business Capability LLM Analysis                                    #
    # ------------------------------------------------------------------ #

    # Function: generate_capability_insights
    @staticmethod
    def generate_capability_insights(
        capability_summary: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        LLM-powered recommendations for the Business Capability Mapping page.

        Receives a summarised view of capabilities and application groupings,
        returns narrative insights and consolidation recommendations.
        """
        model = _available_model()
        if model is None:
            return {
                "available": False, "model_used": None,
                "summary": "Ollama LLM not available. Start Ollama and pull a model.",
            }

        input_json = json.dumps(capability_summary, ensure_ascii=False, default=str)

        prompt = (
            "You are an enterprise business capability architect.\n"
            "Below is a summary of application-to-capability mappings from an IT rationalization study.\n"
            "Base ALL insights on the provided data — cite specific capability names and counts.\n\n"
            f"=== CAPABILITY PORTFOLIO DATA ===\n{input_json}\n\n"
            "Return a single JSON object with EXACTLY these keys:\n"
            "{\n"
            '  "portfolio_insights": "3-4 sentence narrative on the capability landscape and redundancy patterns",\n'
            '  "consolidation_targets": [\n'
            '    {"capability": "name", "apps_affected": 0, "rationale": "...", "recommended_action": "Consolidate|Retain|Eliminate"},\n'
            '    {"capability": "name", "apps_affected": 0, "rationale": "...", "recommended_action": "Consolidate|Retain|Eliminate"},\n'
            '    {"capability": "name", "apps_affected": 0, "rationale": "...", "recommended_action": "Consolidate|Retain|Eliminate"},\n'
            '    {"capability": "name", "apps_affected": 0, "rationale": "...", "recommended_action": "Consolidate|Retain|Eliminate"},\n'
            '    {"capability": "name", "apps_affected": 0, "rationale": "...", "recommended_action": "Consolidate|Retain|Eliminate"}\n'
            '  ],\n'
            '  "capability_strategy": "2-3 sentence description of the overall capability rationalization strategy",\n'
            '  "modernization_priorities": [\n'
            '    {"capability": "name", "priority": "High|Medium|Low", "action": "...", "business_impact": "..."},\n'
            '    {"capability": "name", "priority": "High|Medium|Low", "action": "...", "business_impact": "..."},\n'
            '    {"capability": "name", "priority": "High|Medium|Low", "action": "...", "business_impact": "..."}\n'
            '  ],\n'
            '  "quick_wins": ["actionable item < 3 months", "actionable item < 3 months", "actionable item < 3 months"]\n'
            "}\n"
            "Return ONLY the JSON. No markdown fences, no text outside JSON."
        )

        try:
            raw = _generate(model, prompt, timeout=75, num_predict=800)
            result = _extract_json(raw)
            defaults: Dict[str, Any] = {
                "portfolio_insights": "",
                "consolidation_targets": [],
                "capability_strategy": "",
                "modernization_priorities": [],
                "quick_wins": [],
            }
            for key, default in defaults.items():
                if key not in result:
                    result[key] = default
            result["available"]  = True
            result["model_used"] = model
            logger.info("OllamaService.generate_capability_insights [model=%s]: done", model)
            return result
        except Exception as exc:
            logger.warning("OllamaService.generate_capability_insights failed: %s", exc)
            return {"available": False, "error": str(exc), "model_used": model}

    # ------------------------------------------------------------------ #
    #  Traceability Matrix LLM Analysis                                    #
    # ------------------------------------------------------------------ #

    # Function: generate_traceability_insights
    @staticmethod
    def generate_traceability_insights(
        matrix_summary: Dict[str, Any],
        sample_entries: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        LLM-powered narrative and recommendations for the Final Traceability Matrix page.

        Receives the rule-based summary and a sample of matrix entries,
        returns executive narrative and validated prioritized actions.
        """
        model = _available_model()
        if model is None:
            return {
                "available": False, "model_used": None,
                "summary": "Ollama LLM not available. Start Ollama and pull a model.",
            }

        summary_json = json.dumps(matrix_summary, ensure_ascii=False, default=str)
        sample_json  = json.dumps(sample_entries[:20], ensure_ascii=False, default=str)

        prompt = (
            "You are an enterprise application rationalization expert.\n"
            "You have been given a Traceability Matrix mapping applications to infrastructure, repositories, and capabilities.\n"
            "Base ALL insights on the actual statistics and sample entries provided — cite specific counts.\n\n"
            f"=== MATRIX SUMMARY STATISTICS ===\n{summary_json}\n\n"
            f"=== SAMPLE MATRIX ENTRIES (up to 20) ===\n{sample_json}\n\n"
            "Return a single JSON object with EXACTLY these keys:\n"
            "{\n"
            '  "rationalization_narrative": "3-4 sentence executive narrative on the rationalization strategy citing counts",\n'
            '  "priority_actions": [\n'
            '    {"rank": 1, "action": "...", "apps_affected": "...", "rationale": "...", "timeline": "..."},\n'
            '    {"rank": 2, "action": "...", "apps_affected": "...", "rationale": "...", "timeline": "..."},\n'
            '    {"rank": 3, "action": "...", "apps_affected": "...", "rationale": "...", "timeline": "..."},\n'
            '    {"rank": 4, "action": "...", "apps_affected": "...", "rationale": "...", "timeline": "..."},\n'
            '    {"rank": 5, "action": "...", "apps_affected": "...", "rationale": "...", "timeline": "..."}\n'
            '  ],\n'
            '  "migration_roadmap": [\n'
            '    {"phase": 1, "title": "...", "duration": "0-6 months", "description": "...", "apps_count": 0},\n'
            '    {"phase": 2, "title": "...", "duration": "6-12 months", "description": "...", "apps_count": 0},\n'
            '    {"phase": 3, "title": "...", "duration": "12-24 months", "description": "...", "apps_count": 0}\n'
            '  ],\n'
            '  "decommission_rationale": "paragraph explaining decommission recommendations based on capability redundancy data",\n'
            '  "risk_assessment": ["risk 1 citing data", "risk 2 citing data", "risk 3 citing data"]\n'
            "}\n"
            "Return ONLY the JSON. No markdown fences, no text outside JSON."
        )

        try:
            raw = _generate(model, prompt, timeout=75, num_predict=800)
            result = _extract_json(raw)
            defaults: Dict[str, Any] = {
                "rationalization_narrative": "",
                "priority_actions": [],
                "migration_roadmap": [],
                "decommission_rationale": "",
                "risk_assessment": [],
            }
            for key, default in defaults.items():
                if key not in result:
                    result[key] = default
            result["available"]  = True
            result["model_used"] = model
            logger.info("OllamaService.generate_traceability_insights [model=%s]: done", model)
            return result
        except Exception as exc:
            logger.warning("OllamaService.generate_traceability_insights failed: %s", exc)
            return {"available": False, "error": str(exc), "model_used": model}

    # ------------------------------------------------------------------ #
    #  Per-app annotation (lightweight, called per record)                 #
    # ------------------------------------------------------------------ #

    # Function: annotate_application
    @staticmethod
    def annotate_application(
        app_record: Dict[str, Any],
        model: Optional[str] = None,
    ) -> str:
        """
        Return a single-sentence LLM annotation for one application record.
        Used to populate the `llm_annotation` field in ConsolidatedApp rows.
        """
        model = model or _available_model()
        if model is None:
            return ""

        # Build a concise record summary
        relevant = {
            k: v for k, v in app_record.items()
            if v and k not in ("ai_predicted_columns", "ai_prediction_confidence",
                               "created_at", "updated_at", "llm_annotation")
        }

        prompt = f"""Summarise this enterprise application in ONE concise sentence (max 25 words)
for an executive IT rationalization report.

Record:
{json.dumps(relevant, ensure_ascii=False, default=str)}

One sentence summary:"""

        try:
            response = _generate(model, prompt, timeout=30)
            # Extract first non-empty line
            for line in response.splitlines():
                line = line.strip().strip('"').strip("'")
                if len(line) > 10:
                    return line
            return response.strip()[:200]
        except Exception:
            return ""

    # ------------------------------------------------------------------ #
    #  Harmonization Wave Plan LLM Review                                  #
    # ------------------------------------------------------------------ #

    # Function: generate_wave_plan_review
    @staticmethod
    def generate_wave_plan_review(
        apps: List[Dict[str, Any]],
        scaffold: List[Dict[str, Any]],
        constraints: Dict[str, Any],
        preferred_model: Optional[str] = None,
        temperature: float = 0.2,
        num_ctx: int = 8192,
        max_apps: int = 80,
        timeout: int = 120,
        num_predict: int = 4096,
        think: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Ask the LLM to review a deterministically bin-packed wave schedule and
        propose refinements (wave re-assignment, per-wave theme/rationale).

        The caller (wave_plan_service) treats every suggestion as advisory: it
        only accepts a proposed wave re-assignment when the app_id exists in
        *apps* and the wave_number is within the valid range, so a bad or
        hallucinated LLM response degrades to the deterministic *scaffold*
        rather than corrupting the plan.

        Parameters
        ----------
        apps : list[dict]
            Slim per-application records (app_id, application_name, tshirt_size,
            complexity, migration_type, quick_win, change_impact, risk,
            dependencies, wave_eligibility_score).
        scaffold : list[dict]
            The deterministic bin-packed schedule: [{"wave_number", "app_ids"}].
        constraints : dict
            Program constraints: sprint_weeks, cutover_frequency_months,
            max_waves, parallel_streams.

        Returns
        -------
        dict with keys: available, model_used, wave_assignments,
                        wave_summaries, overall_summary
        """
        model = _available_model(preferred=preferred_model)
        if model is None:
            return {
                "available": False, "model_used": None,
                "wave_assignments": [], "wave_summaries": [], "overall_summary": "",
            }

        apps_json = json.dumps(apps[:max_apps], ensure_ascii=False, default=str)
        scaffold_json = json.dumps(scaffold, ensure_ascii=False, default=str)
        constraints_json = json.dumps(constraints, ensure_ascii=False, default=str)

        prompt = (
            "You are a senior application harmonization program manager planning migration waves.\n"
            "Applications flagged High complexity have ALREADY been excluded from this scope — "
            "do not add or reference them.\n\n"
            f"=== PROGRAM CONSTRAINTS ===\n{constraints_json}\n\n"
            "=== APPLICATIONS IN SCOPE (Low/Medium complexity only) ===\n"
            f"{apps_json}\n\n"
            "=== DETERMINISTIC DRAFT SCHEDULE (bin-packed by T-shirt size / sprint capacity) ===\n"
            f"{scaffold_json}\n\n"
            "Review the draft schedule. You may re-assign an app to a different wave_number ONLY when it "
            "improves sequencing (e.g. quick wins pulled earlier, a dependency's app moved to an earlier "
            "or equal wave, risk apps spread out), while respecting wave sprint capacity roughly as drafted. "
            "Every app_id you return MUST come from the applications list above — never invent one. "
            "wave_number MUST be between 1 and the max_waves given in constraints.\n\n"
            "Return a single JSON object with EXACTLY these keys:\n"
            "{\n"
            '  "wave_assignments": [{"app_id": "...", "wave_number": 1, "rationale": "short reason"}],\n'
            '  "wave_summaries": [{"wave_number": 1, "theme": "short theme", "rationale": "why these apps together"}],\n'
            '  "overall_summary": "2-3 sentence executive summary of the wave sequencing strategy"\n'
            "}\n"
            "Only include an entry in wave_assignments for apps you are CHANGING from the draft; "
            "omit apps that should keep their drafted wave. Return ONLY the JSON object."
        )

        try:
            raw = _generate(model, prompt, timeout=timeout, force_json=True, num_predict=num_predict, num_ctx=num_ctx,
                             temperature=temperature, think=think)
            parsed = _extract_json(raw)
            wave_assignments = parsed.get("wave_assignments")
            wave_summaries = parsed.get("wave_summaries")
            result = {
                "available": True,
                "model_used": model,
                "wave_assignments": wave_assignments if isinstance(wave_assignments, list) else [],
                "wave_summaries": wave_summaries if isinstance(wave_summaries, list) else [],
                "overall_summary": parsed.get("overall_summary") or "",
            }
            logger.info(
                "OllamaService.generate_wave_plan_review [model=%s]: %d re-assignments, %d wave summaries",
                model, len(result["wave_assignments"]), len(result["wave_summaries"]),
            )
            return result
        except Exception as exc:
            logger.warning("OllamaService.generate_wave_plan_review failed: %s", exc)
            return {
                "available": False, "error": str(exc), "model_used": model,
                "wave_assignments": [], "wave_summaries": [], "overall_summary": "",
            }
