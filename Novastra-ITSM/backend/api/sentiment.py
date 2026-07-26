# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — backend/api (sentiment.py)
# Date: 2026-04-24
# ---------------------------------------------------------------------------
from __future__ import annotations
import asyncio, json, logging, re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Body, Depends, HTTPException
from backend.api.auth import get_current_user
import backend.config as cfg

router = APIRouter(prefix="/api/sentiment", tags=["Sentiment Analysis"])
logger = logging.getLogger(__name__)
_LLM_TIMEOUT = 90

_NEG_WORDS = {"frustrated", "angry", "terrible", "worst", "broken", "failed", "useless", "horrible", "unacceptable"}
_VIP_WORDS = {"vp", "director", "ceo", "cto", "cio", "executive", "manager", "head of"}
_URG_WORDS = {"urgent", "asap", "immediately", "critical", "cannot work", "blocked", "down"}


# Function: _call_llm
def _call_llm(system_msg: str, user_msg: str) -> str:
    from langchain_ollama import ChatOllama
    from backend.llm.router import assert_ollama_gpu_available
    assert_ollama_gpu_available(cfg.OLLAMA_MODEL)
    llm = ChatOllama(
        model=cfg.OLLAMA_MODEL, base_url=cfg.OLLAMA_BASE_URL,
        temperature=0.1, num_predict=2048, num_ctx=6144,
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


# Function: _heuristic_sentiment
def _heuristic_sentiment(text: str) -> dict:
    words = set(re.findall(r'\b\w+\b', text.lower()))
    neg_hits = words & _NEG_WORDS
    vip = bool(any(v in text.lower() for v in _VIP_WORDS))
    urg = bool(words & _URG_WORDS)
    if neg_hits:
        sentiment = "frustrated"
        esc_risk = 0.75
    elif urg:
        sentiment = "negative"
        esc_risk = 0.55
    else:
        sentiment = "neutral"
        esc_risk = 0.2
    return {"sentiment": sentiment, "urgency_signal": urg, "vip_indicator": vip,
            "escalation_risk": esc_risk, "emotion_tags": list(neg_hits)[:5],
            "priority_recommendation": "P1" if vip and urg else "P2" if urg else "P3",
            "llm_used": False}


# Function: score_ticket
@router.post("/score-ticket")
async def score_ticket(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    ticket_id = payload.get("ticket_id", "")
    description = payload.get("description", "")
    updates = payload.get("updates", [])
    full_text = description + " " + " ".join(updates)

    system_msg = (
        "You are a sentiment analyst for ITSM tickets. "
        "Return JSON: {\"sentiment\": \"positive|neutral|negative|frustrated\", "
        "\"urgency_signal\": bool, \"vip_indicator\": bool, \"escalation_risk\": float (0-1), "
        "\"emotion_tags\": [str], \"priority_recommendation\": str}"
    )
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, full_text), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed["ticket_id"] = ticket_id
        parsed["llm_used"] = True
        h = _heuristic_sentiment(full_text)
        for k, v in h.items():
            parsed.setdefault(k, v)
        return parsed
    except Exception as exc:
        logger.warning("score_ticket LLM failed: %s", exc)
        result = _heuristic_sentiment(full_text)
        result["ticket_id"] = ticket_id
        return result


# Function: analyze_survey
@router.post("/analyze-survey")
async def analyze_survey(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    responses = payload.get("responses", [])

    ratings = [r.get("rating", 3) for r in responses if r.get("rating")]
    csat = round(sum(ratings) / max(len(ratings), 1), 2)
    overall = "positive" if csat >= 4 else "neutral" if csat >= 3 else "negative"

    responses_text = "\n".join(
        f"Rating:{r.get('rating','')} | {r.get('free_text','')[:150]}" for r in responses[:50]
    )
    system_msg = (
        "You are a customer experience analyst. Extract themes from CSAT/XLA survey responses. "
        "Return JSON: {\"themes\": [{\"theme\": str, \"frequency\": int, \"sentiment\": str, "
        "\"sample_quotes\": [str]}], \"overall_sentiment\": str, \"top_issues\": [str], \"recommendations\": [str]}"
    )
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, responses_text), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed["csat_score"] = csat
        parsed["llm_used"] = True
        parsed.setdefault("overall_sentiment", overall)
        parsed.setdefault("themes", [])
        parsed.setdefault("top_issues", [])
        parsed.setdefault("recommendations", [])
        return parsed
    except Exception as exc:
        logger.warning("analyze_survey LLM failed: %s", exc)
        return {"themes": [], "overall_sentiment": overall, "csat_score": csat,
                "top_issues": [], "recommendations": [], "llm_used": False}


# Function: coach_response
@router.post("/coach-response")
async def coach_response(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    ticket_id = payload.get("ticket_id", "")
    agent_draft = payload.get("agent_draft", "")
    customer_message = payload.get("customer_message", "")

    system_msg = (
        "You are an ITSM communication coach. Review the agent's draft response and improve it. "
        "Return JSON: {\"tone_score\": float (0-10), \"empathy_score\": float (0-10), "
        "\"professionalism_score\": float (0-10), \"issues\": [str], "
        "\"suggestions\": [str], \"improved_draft\": str}"
    )
    user_msg = f"Customer message:\n{customer_message}\n\nAgent draft:\n{agent_draft}"
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, user_msg), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed["ticket_id"] = ticket_id
        parsed["original_draft"] = agent_draft
        parsed["llm_used"] = True
        parsed.setdefault("tone_score", 7.0)
        parsed.setdefault("empathy_score", 7.0)
        parsed.setdefault("professionalism_score", 7.0)
        parsed.setdefault("issues", [])
        parsed.setdefault("suggestions", [])
        parsed.setdefault("improved_draft", agent_draft)
        return parsed
    except Exception as exc:
        logger.warning("coach_response LLM failed: %s", exc)
        return {"ticket_id": ticket_id, "original_draft": agent_draft, "tone_score": 7.0,
                "empathy_score": 7.0, "professionalism_score": 7.0,
                "issues": [], "suggestions": ["Add empathy acknowledgement at the start"],
                "improved_draft": agent_draft, "llm_used": False}
