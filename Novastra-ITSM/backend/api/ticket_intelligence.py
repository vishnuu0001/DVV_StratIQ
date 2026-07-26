# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — backend/api (ticket_intelligence.py)
# Date: 2026-07-03
# ---------------------------------------------------------------------------
from __future__ import annotations
import asyncio, json, logging, re
from fastapi import APIRouter, Body, Depends, HTTPException
from backend.api.auth import get_current_user
import backend.config as cfg

router = APIRouter(prefix="/api/ticket-intelligence", tags=["Ticket Intelligence"])
logger = logging.getLogger(__name__)
_LLM_TIMEOUT = 60


# Function: _call_llm
def _call_llm(system_msg: str, user_msg: str) -> str:
    from langchain_ollama import ChatOllama
    from backend.llm.router import assert_ollama_gpu_available

    assert_ollama_gpu_available(cfg.OLLAMA_MODEL)
    llm = ChatOllama(
        model=cfg.OLLAMA_MODEL, base_url=cfg.OLLAMA_BASE_URL,
        # Classification/reranking responses are compact JSON. A 384-token cap
        # avoids long 14B generations exceeding the Azure/IIS proxy timeout.
        temperature=0.1, num_predict=384, num_ctx=4096,
        repeat_penalty=1.1, top_k=20, top_p=0.9,
        format="json", timeout=_LLM_TIMEOUT, keep_alive=cfg.OLLAMA_KEEP_ALIVE,
    )
    # The endpoint already runs this function via asyncio.to_thread. A nested
    # ThreadPoolExecutor caused its context manager to wait for the worker even
    # after Future.result(timeout=...) fired, defeating the timeout entirely.
    result = llm.invoke([("system", system_msg), ("human", user_msg)])
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


# Function: _heuristic_classify
def _heuristic_classify(title: str, description: str) -> dict:
    text = (title + " " + description).lower()
    if any(w in text for w in ["password", "login", "access", "account", "locked"]):
        cat, sub, pri = "Access Management", "Password / Account", "P3"
    elif any(w in text for w in ["crash", "down", "outage", "critical", "p1"]):
        cat, sub, pri = "Availability", "Service Outage", "P1"
    elif any(w in text for w in ["slow", "performance", "timeout", "latency"]):
        cat, sub, pri = "Performance", "Degradation", "P2"
    elif any(w in text for w in ["network", "vpn", "connectivity", "internet"]):
        cat, sub, pri = "Network", "Connectivity", "P3"
    elif any(w in text for w in ["email", "outlook", "exchange", "teams"]):
        cat, sub, pri = "Communication Tools", "Email / Messaging", "P3"
    else:
        cat, sub, pri = "General IT", "Other", "P4"
    urgency = "High" if pri in ("P1", "P2") else "Medium" if pri == "P3" else "Low"
    return {"category": cat, "subcategory": sub, "priority": pri,
            "urgency": urgency, "assignment_group": "Service Desk",
            "confidence": 0.55, "reasoning": "Keyword heuristic classification", "llm_used": False}


# Function: classify_ticket
@router.post("/classify")
async def classify_ticket(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    title = payload.get("title", "")
    description = payload.get("description", "")
    assignment_group = payload.get("assignment_group", "")

    system_msg = (
        "You are an ITSM ticket classifier. Return ONLY a JSON object with keys: "
        "category, subcategory, priority (P1/P2/P3/P4), urgency (High/Medium/Low), "
        "assignment_group, confidence (0.0-1.0), reasoning. No extra text."
    )
    user_msg = f"Title: {title}\nDescription: {description}\nHint assignment_group: {assignment_group}"

    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, user_msg), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed["llm_used"] = True
        for k, v in _heuristic_classify(title, description).items():
            parsed.setdefault(k, v)
        return parsed
    except Exception as exc:
        logger.warning("classify_ticket LLM failed: %s", exc)
        return _heuristic_classify(title, description)


# Function: _word_overlap
def _word_overlap(a: str, b: str) -> float:
    sa = set(re.findall(r'\b\w+\b', a.lower()))
    sb = set(re.findall(r'\b\w+\b', b.lower()))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


# Function: find_duplicates
@router.post("/find-duplicates")
async def find_duplicates(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    title = payload.get("title", "")
    description = payload.get("description", "")
    existing = payload.get("existing_tickets", [])

    query_text = title + " " + description
    scored = []
    for t in existing:
        t_text = t.get("title", "") + " " + t.get("description", "")
        score = _word_overlap(query_text, t_text)
        scored.append((score, t))
    scored.sort(key=lambda x: x[0], reverse=True)
    top5 = scored[:5]

    results = []
    for score, t in top5:
        rel = "duplicate" if score > 0.7 else "related" if score > 0.4 else "similar"
        results.append({"ticket_id": t.get("id", ""), "title": t.get("title", ""),
                        "similarity_score": round(score, 3), "relationship": rel})

    llm_used = False
    if top5:
        try:
            items_text = "\n".join(f"- ID:{r['ticket_id']} | {r['title']} | score:{r['similarity_score']}" for r in results)
            sys = ("Rerank these duplicate ticket candidates by relevance to the query. "
                   "Return JSON: {\"ranked\": [{\"ticket_id\": ..., \"relationship\": \"duplicate|related|similar\"}]}")
            user = f"Query: {title}\nCandidates:\n{items_text}"
            raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, sys, user), timeout=60)
            parsed = _extract_json(raw) or {}
            ranked = parsed.get("ranked", [])
            if ranked:
                id_order = {r["ticket_id"]: i for i, r in enumerate(ranked)}
                results = sorted(results, key=lambda x: id_order.get(x["ticket_id"], 99))
                for res, rank in zip(results, ranked):
                    res["relationship"] = rank.get("relationship", res["relationship"])
                llm_used = True
        except Exception as exc:
            logger.warning("find_duplicates LLM rerank failed: %s", exc)

    return {"duplicates": results, "llm_used": llm_used}


# Function: summarize_thread
@router.post("/summarize")
async def summarize_thread(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    ticket_id = payload.get("ticket_id", "")
    thread = payload.get("thread", [])

    # Function: _heuristic
    def _heuristic():
        msgs = [f"{m.get('author','')}: {m.get('content','')}" for m in thread[:3]]
        return {"ticket_id": ticket_id, "summary": " | ".join(msgs)[:300],
                "key_actions": ["Review thread above"], "next_steps": ["Follow up with assignee"],
                "llm_used": False}

    thread_text = "\n".join(
        f"[{m.get('timestamp','')}] {m.get('author','')}: {m.get('content','')}" for m in thread
    )
    system_msg = (
        "You are an ITSM analyst. Summarize this ticket thread in ≤150 words for shift handoff. "
        "Return JSON: {\"summary\": str, \"key_actions\": [str], \"next_steps\": [str]}"
    )
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, thread_text), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed["ticket_id"] = ticket_id
        parsed["llm_used"] = True
        parsed.setdefault("summary", "")
        parsed.setdefault("key_actions", [])
        parsed.setdefault("next_steps", [])
        return parsed
    except Exception as exc:
        logger.warning("summarize_thread LLM failed: %s", exc)
        return _heuristic()
