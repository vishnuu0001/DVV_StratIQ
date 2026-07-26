# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — backend/api (nlp.py)
# Date: 2026-05-17
# ---------------------------------------------------------------------------
from __future__ import annotations
import asyncio, json, logging, re
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Body, Depends, HTTPException
from backend.api.auth import get_current_user
import backend.config as cfg

router = APIRouter(prefix="/api/nlp", tags=["NLP Capabilities"])
logger = logging.getLogger(__name__)
_LLM_TIMEOUT = 90

_INTENT_LABELS = [
    "create_incident", "resolve_incident", "update_ticket", "escalate_ticket",
    "check_status", "find_knowledge", "request_access", "report_outage",
    "run_rca", "predict_sla", "search_cmdb", "schedule_change",
    "approve_change", "assign_ticket", "close_ticket", "generate_report",
]

_INC_RE = re.compile(r'\bINC\d{7,10}\b', re.IGNORECASE)
_SOLMAN_RE = re.compile(r'\b[A-Z]{2,4}\d{10}\b')
_DELIVERY_RE = re.compile(r'\b\d{10}\b')
_EMAIL_RE = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
_DATE_RE = re.compile(r'\b(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4})\b', re.IGNORECASE)
_CI_KEYWORDS = re.compile(r'\b([A-Z]{2,8}-[A-Z0-9]{3,12}|[A-Z]{2,}(?:SRV|DB|APP|WEB|PROD|DEV|UAT)\d*)\b')
_PRIO_RE = re.compile(r'\b(P[1-4]|Priority\s+[1-4]|Critical|High|Medium|Low)\b', re.IGNORECASE)
_SAP_SYS_RE = re.compile(r'\b(SAP\s+(?:ECC|S/4|BW|CRM|SRM|PI|XI|PO|GRC|WM|MM|FI|CO|SD|PP|HR|PM|QM))\b', re.IGNORECASE)


# Function: _call_llm
def _call_llm(system_msg: str, user_msg: str) -> str:
    from langchain_ollama import ChatOllama
    from backend.llm.router import assert_ollama_gpu_available
    assert_ollama_gpu_available(cfg.OLLAMA_MODEL)
    llm = ChatOllama(
        model=cfg.OLLAMA_MODEL, base_url=cfg.OLLAMA_BASE_URL,
        temperature=0.1, num_predict=1024, num_ctx=4096,
        repeat_penalty=1.1, top_k=20, top_p=0.9,
        format="json", timeout=_LLM_TIMEOUT, keep_alive=cfg.OLLAMA_KEEP_ALIVE,
    )
    with ThreadPoolExecutor(max_workers=1) as pool:
        result = pool.submit(llm.invoke, [("system", system_msg), ("human", user_msg)]).result(timeout=_LLM_TIMEOUT)
    return result.content if hasattr(result, "content") else str(result)


# Function: _extract_json
def _extract_json(raw: str) -> dict | list | None:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except Exception:
        pass
    for sc, ec in [('{', '}'), ('[', ']')]:
        s, e = text.find(sc), text.rfind(ec)
        if s >= 0 and e > s:
            try:
                return json.loads(text[s:e+1])
            except Exception:
                pass
    return None


# Function: _heuristic_intent
def _heuristic_intent(text: str) -> dict:
    t = text.lower()
    if any(w in t for w in ["create", "open", "raise", "new", "log"]):
        intent = "create_incident"
    elif any(w in t for w in ["resolve", "close", "fix", "solved"]):
        intent = "resolve_incident"
    elif any(w in t for w in ["escalate", "escalation", "urgent"]):
        intent = "escalate_ticket"
    elif any(w in t for w in ["status", "update", "check", "where", "how"]):
        intent = "check_status"
    elif any(w in t for w in ["knowledge", "article", "kb", "document", "find"]):
        intent = "find_knowledge"
    elif any(w in t for w in ["outage", "down", "offline", "unavailable"]):
        intent = "report_outage"
    elif any(w in t for w in ["rca", "root cause", "analysis"]):
        intent = "run_rca"
    elif any(w in t for w in ["sla", "breach", "deadline"]):
        intent = "predict_sla"
    elif any(w in t for w in ["change", "schedule", "deploy"]):
        intent = "schedule_change"
    elif any(w in t for w in ["report", "metrics", "dashboard"]):
        intent = "generate_report"
    else:
        intent = "find_knowledge"
    return {"intent": intent, "confidence": 0.6, "llm_used": False}


# Function: _regex_entities
def _regex_entities(text: str) -> dict:
    return {
        "incident_numbers": _INC_RE.findall(text),
        "solman_ids": _SOLMAN_RE.findall(text),
        "delivery_numbers": _DELIVERY_RE.findall(text),
        "emails": _EMAIL_RE.findall(text),
        "dates": _DATE_RE.findall(text),
        "ci_names": _CI_KEYWORDS.findall(text),
        "priorities": _PRIO_RE.findall(text),
        "sap_systems": _SAP_SYS_RE.findall(text),
    }


# Function: detect_intent
@router.post("/intent")
async def detect_intent(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    text = payload.get("text", "")
    if not text.strip():
        raise HTTPException(status_code=400, detail="text is required")

    heuristic = _heuristic_intent(text)
    system_msg = (
        f"You are an ITSM intent classifier. Classify the user's intent into one of: {', '.join(_INTENT_LABELS)}.\n"
        "Return JSON: {\"intent\": str, \"confidence\": float, \"sub_intent\": str, \"entities\": {\"ticket_ids\": [str], \"cis\": [str]}}"
    )
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, f"User text: {text}"), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed.setdefault("intent", heuristic["intent"])
        parsed.setdefault("confidence", 0.85)
        parsed["llm_used"] = True
        parsed["regex_entities"] = _regex_entities(text)
        return parsed
    except Exception as exc:
        logger.warning("intent LLM failed: %s", exc)
        heuristic["regex_entities"] = _regex_entities(text)
        return heuristic


# Function: extract_entities
@router.post("/entities")
async def extract_entities(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    text = payload.get("text", "")
    if not text.strip():
        raise HTTPException(status_code=400, detail="text is required")

    regex_result = _regex_entities(text)
    system_msg = (
        "You are an ITSM NER system. Extract named entities from the text. "
        "Return JSON: {\"persons\": [str], \"organizations\": [str], \"locations\": [str], "
        "\"ci_names\": [str], \"incident_ids\": [str], \"change_ids\": [str], \"products\": [str], \"errors\": [str]}"
    )
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, f"Text: {text[:2000]}"), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed["llm_used"] = True
        parsed["regex_entities"] = regex_result
        return parsed
    except Exception as exc:
        logger.warning("entities LLM failed: %s", exc)
        return {"llm_used": False, "regex_entities": regex_result}


# Function: topic_modeling
@router.post("/topics")
async def topic_modeling(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    texts: list[str] = payload.get("texts", [])
    num_topics: int = int(payload.get("num_topics", 5))
    if not texts:
        raise HTTPException(status_code=400, detail="texts list is required")

    # Heuristic: keyword frequency
    stopwords = {"the", "a", "an", "is", "in", "on", "at", "to", "for", "of", "and", "or", "with", "not"}
    word_freq: dict[str, int] = {}
    for t in texts:
        for w in re.findall(r'\b[a-z]{3,}\b', t.lower()):
            if w not in stopwords:
                word_freq[w] = word_freq.get(w, 0) + 1
    top_words = sorted(word_freq.items(), key=lambda x: -x[1])[:30]
    heuristic_topics = [
        {"topic_id": i + 1, "label": f"Topic {i+1}", "keywords": [w for w, _ in top_words[i*5:(i+1)*5]], "doc_count": len(texts) // num_topics}
        for i in range(min(num_topics, 5))
    ]

    corpus = "\n---\n".join(texts[:30])
    system_msg = (
        f"You are a topic modeling assistant. Identify {num_topics} distinct topics in this corpus. "
        "Return JSON: {\"topics\": [{\"topic_id\": int, \"label\": str, \"keywords\": [str], \"doc_count\": int, \"representative_excerpt\": str}]}"
    )
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, f"Corpus ({len(texts)} documents):\n{corpus[:3000]}"), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed.setdefault("topics", heuristic_topics)
        parsed["total_documents"] = len(texts)
        parsed["llm_used"] = True
        return parsed
    except Exception as exc:
        logger.warning("topics LLM failed: %s", exc)
        return {"topics": heuristic_topics, "total_documents": len(texts), "llm_used": False}


# Function: extract_relations
@router.post("/relations")
async def extract_relations(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    text = payload.get("text", "")
    entities = payload.get("entities", [])
    if not text.strip():
        raise HTTPException(status_code=400, detail="text is required")

    entities_str = ", ".join(entities) if entities else "all entities"
    system_msg = (
        "You are a relation extraction engine. Extract relationships between entities. "
        "Return JSON: {\"relations\": [{\"subject\": str, \"predicate\": str, \"object\": str, \"confidence\": float}]}"
    )
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, f"Entities: {entities_str}\nText: {text[:2000]}"), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed.setdefault("relations", [])
        parsed["llm_used"] = True
        return parsed
    except Exception as exc:
        logger.warning("relations LLM failed: %s", exc)
        return {"relations": [], "llm_used": False}


# Function: summarize_batch
@router.post("/summarize-batch")
async def summarize_batch(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    texts: list[str] = payload.get("texts", [])
    max_length: int = int(payload.get("max_length", 200))
    if not texts:
        raise HTTPException(status_code=400, detail="texts list is required")

    combined = "\n---\n".join(f"Doc {i+1}: {t[:500]}" for i, t in enumerate(texts[:20]))
    system_msg = (
        f"Summarize each document concisely (max {max_length} chars each). "
        "Return JSON: {\"summaries\": [{\"doc_id\": int, \"summary\": str, \"key_points\": [str]}]}"
    )
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, combined[:4000]), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed.setdefault("summaries", [{"doc_id": i+1, "summary": t[:max_length], "key_points": []} for i, t in enumerate(texts)])
        parsed["llm_used"] = True
        return parsed
    except Exception as exc:
        logger.warning("summarize_batch LLM failed: %s", exc)
        return {
            "summaries": [{"doc_id": i+1, "summary": t[:max_length], "key_points": []} for i, t in enumerate(texts)],
            "llm_used": False,
        }
