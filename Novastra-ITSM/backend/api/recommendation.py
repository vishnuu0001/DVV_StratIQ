# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — backend/api (recommendation.py)
# Date: 2026-03-11
# ---------------------------------------------------------------------------
from __future__ import annotations
import asyncio, json, logging, re
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Body, Depends, HTTPException
from backend.api.auth import get_current_user
import backend.config as cfg

router = APIRouter(prefix="/api/recommend", tags=["Recommendation Engine"])
logger = logging.getLogger(__name__)
_LLM_TIMEOUT = 90

_CATEGORY_SKILLS: dict[str, list[str]] = {
    "Network": ["network_admin", "infrastructure"],
    "Database": ["dba", "oracle_dba", "sql_admin"],
    "Application": ["app_support", "dev_support"],
    "Security": ["security_analyst", "iam_admin"],
    "Hardware": ["hardware_tech", "field_support"],
    "SAP": ["sap_basis", "sap_functional"],
    "Storage": ["storage_admin", "backup_admin"],
    "Cloud": ["cloud_ops", "azure_admin", "aws_admin"],
}


# Function: _call_llm
def _call_llm(system_msg: str, user_msg: str) -> str:
    from langchain_ollama import ChatOllama
    from backend.llm.router import assert_ollama_gpu_available
    assert_ollama_gpu_available(cfg.OLLAMA_MODEL)
    llm = ChatOllama(
        model=cfg.OLLAMA_MODEL, base_url=cfg.OLLAMA_BASE_URL,
        temperature=0.1, num_predict=2048, num_ctx=5120,
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


# Function: _keyword_similarity
def _keyword_similarity(text_a: str, text_b: str) -> float:
    """Simple Jaccard similarity on word sets."""
    tokens_a = set(re.findall(r'\b\w{3,}\b', text_a.lower()))
    tokens_b = set(re.findall(r'\b\w{3,}\b', text_b.lower()))
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)


# Function: next_best_action
@router.post("/next-action")
async def next_best_action(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    ticket_id = payload.get("ticket_id", "")
    title = payload.get("title", "")
    description = payload.get("description", "")
    status = payload.get("status", "Open")
    priority = payload.get("priority", "P3")
    category = payload.get("category", "")
    age_hours = float(payload.get("age_hours", 0))
    history = payload.get("history", [])

    heuristic_actions = []
    if status.lower() in ("open", "new"):
        heuristic_actions.append({"action": "Acknowledge ticket", "rationale": "First response SLA", "urgency": "HIGH"})
    if age_hours > 4 and priority in ("P1", "P2"):
        heuristic_actions.append({"action": "Escalate to senior engineer", "rationale": f"P{priority[-1]} ticket open {age_hours:.0f}h", "urgency": "CRITICAL"})
    if category:
        skills = _CATEGORY_SKILLS.get(category, [])
        if skills:
            heuristic_actions.append({"action": f"Route to {skills[0]}", "rationale": f"Skill match for {category}", "urgency": "MEDIUM"})
    heuristic_actions.append({"action": "Search knowledge base for resolution steps", "rationale": "Faster resolution via KB", "urgency": "MEDIUM"})
    if not heuristic_actions:
        heuristic_actions.append({"action": "Review ticket and gather more details", "rationale": "Insufficient context", "urgency": "LOW"})

    history_text = "\n".join(f"[{h.get('timestamp','')}] {h.get('actor','')}: {h.get('note','')}" for h in history[-10:])
    system_msg = (
        "You are an ITSM next-best-action advisor. Recommend the most impactful next actions for this ticket. "
        "Return JSON: {\"recommended_actions\": [{\"action\": str, \"rationale\": str, \"urgency\": str, \"estimated_time_mins\": int}], "
        "\"priority_override\": str, \"summary\": str}"
    )
    user_msg = (f"Ticket: {ticket_id} | {title}\nStatus: {status} | Priority: {priority} | Category: {category}\n"
                f"Age: {age_hours}h\nDescription: {description[:500]}\nHistory:\n{history_text}")
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, user_msg), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed.setdefault("recommended_actions", heuristic_actions)
        parsed.setdefault("summary", f"Next best actions for {ticket_id or 'ticket'}.")
        parsed["llm_used"] = True
        return parsed
    except Exception as exc:
        logger.warning("next_action LLM failed: %s", exc)
        return {"recommended_actions": heuristic_actions, "summary": "Heuristic recommendations.", "llm_used": False}


# Function: similar_tickets
@router.post("/similar-tickets")
async def similar_tickets(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    query_text = payload.get("title", "") + " " + payload.get("description", "")
    ticket_pool: list[dict] = payload.get("ticket_pool", [])
    top_k: int = int(payload.get("top_k", 5))

    if not ticket_pool:
        return {"similar_tickets": [], "search_strategy": "no_pool"}

    # Heuristic similarity ranking
    scored = []
    for t in ticket_pool:
        t_text = t.get("title", "") + " " + t.get("description", "")
        score = _keyword_similarity(query_text, t_text)
        if score > 0.05:
            scored.append({**t, "similarity_score": round(score, 3)})
    scored.sort(key=lambda x: -x["similarity_score"])
    heuristic_results = scored[:top_k]

    if not heuristic_results:
        return {"similar_tickets": [], "search_strategy": "keyword", "llm_used": False}

    system_msg = (
        "You are a ticket similarity ranker. Re-rank and annotate the similar tickets. "
        "Return JSON: {\"similar_tickets\": [{\"ticket_id\": str, \"similarity_score\": float, "
        "\"match_reason\": str, \"resolution_hint\": str}]}"
    )
    candidates_text = "\n".join(
        f"[{t.get('id','')}] {t.get('title','')} | Resolution: {t.get('resolution','')[:80]}"
        for t in heuristic_results
    )
    user_msg = f"Query: {query_text[:500]}\n\nCandidates:\n{candidates_text}"
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, user_msg), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed.setdefault("similar_tickets", [
            {"ticket_id": t.get("id", ""), "similarity_score": t["similarity_score"],
             "match_reason": "Keyword similarity", "resolution_hint": t.get("resolution", "")}
            for t in heuristic_results
        ])
        parsed["search_strategy"] = "llm_reranked"
        parsed["llm_used"] = True
        return parsed
    except Exception as exc:
        logger.warning("similar_tickets LLM failed: %s", exc)
        return {
            "similar_tickets": [
                {"ticket_id": t.get("id", ""), "similarity_score": t["similarity_score"],
                 "match_reason": "Keyword match", "resolution_hint": t.get("resolution", "")}
                for t in heuristic_results
            ],
            "search_strategy": "keyword",
            "llm_used": False,
        }


# Function: recommend_knowledge
@router.post("/knowledge")
async def recommend_knowledge(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    query = payload.get("query", "")
    category = payload.get("category", "")
    kb_articles: list[dict] = payload.get("articles", [])
    top_k: int = int(payload.get("top_k", 5))

    search_text = f"{query} {category}"
    scored = []
    for art in kb_articles:
        art_text = art.get("title", "") + " " + art.get("content", "")[:500]
        score = _keyword_similarity(search_text, art_text)
        scored.append({**art, "relevance_score": round(score, 3)})
    scored.sort(key=lambda x: -x["relevance_score"])
    top = scored[:top_k]

    if not top:
        return {"articles": [], "llm_used": False}

    system_msg = (
        "You are a knowledge recommendation engine. Rank articles by relevance and explain why each is useful. "
        "Return JSON: {\"articles\": [{\"article_id\": str, \"title\": str, \"relevance_score\": float, \"why_relevant\": str, \"excerpt\": str}]}"
    )
    articles_text = "\n".join(f"[{a.get('id','')}] {a.get('title','')} | {a.get('content','')[:100]}" for a in top)
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, f"Query: {query}\nCategory: {category}\nArticles:\n{articles_text}"), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed.setdefault("articles", [
            {"article_id": a.get("id", ""), "title": a.get("title", ""),
             "relevance_score": a["relevance_score"], "why_relevant": "Keyword match", "excerpt": a.get("content", "")[:200]}
            for a in top
        ])
        parsed["llm_used"] = True
        return parsed
    except Exception as exc:
        logger.warning("recommend_knowledge LLM failed: %s", exc)
        return {
            "articles": [
                {"article_id": a.get("id", ""), "title": a.get("title", ""),
                 "relevance_score": a["relevance_score"], "why_relevant": "Keyword match", "excerpt": a.get("content", "")[:200]}
                for a in top
            ],
            "llm_used": False,
        }


# Function: recommend_assignee
@router.post("/assignee")
async def recommend_assignee(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    category = payload.get("category", "")
    priority = payload.get("priority", "P3")
    description = payload.get("description", "")
    available_agents: list[dict] = payload.get("agents", [])

    skills = _CATEGORY_SKILLS.get(category, ["general_support"])
    heuristic_picks = []
    for agent in available_agents:
        agent_skills = agent.get("skills", [])
        match_score = sum(1 for s in skills if s in agent_skills) / max(len(skills), 1)
        workload = agent.get("open_tickets", 0)
        score = match_score * 0.7 + max(0, (10 - workload) / 10) * 0.3
        heuristic_picks.append({**agent, "_score": round(score, 3)})
    heuristic_picks.sort(key=lambda x: -x["_score"])
    top_picks = heuristic_picks[:3]

    system_msg = (
        "You are an ITSM assignment advisor. Pick the best assignee based on skills, workload and ticket context. "
        "Return JSON: {\"recommended_assignee\": {\"agent_id\": str, \"name\": str, \"reason\": str, \"confidence\": float}, "
        "\"alternatives\": [{\"agent_id\": str, \"name\": str, \"reason\": str}]}"
    )
    agents_text = "\n".join(
        f"{a.get('name','')} ({a.get('agent_id','')}) | Skills: {', '.join(a.get('skills',[]))} | Open: {a.get('open_tickets',0)}"
        for a in top_picks
    )
    user_msg = f"Ticket category: {category} | Priority: {priority}\nDescription: {description[:300]}\n\nAgents:\n{agents_text}"
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, user_msg), timeout=60)
        parsed = _extract_json(raw) or {}
        if top_picks and "recommended_assignee" not in parsed:
            best = top_picks[0]
            parsed["recommended_assignee"] = {
                "agent_id": best.get("agent_id", ""),
                "name": best.get("name", ""),
                "reason": f"Best skill match for {category}",
                "confidence": best["_score"],
            }
        parsed["llm_used"] = True
        return parsed
    except Exception as exc:
        logger.warning("recommend_assignee LLM failed: %s", exc)
        best = top_picks[0] if top_picks else {}
        return {
            "recommended_assignee": {
                "agent_id": best.get("agent_id", ""),
                "name": best.get("name", ""),
                "reason": f"Skill match for {category}",
                "confidence": best.get("_score", 0.5),
            },
            "alternatives": [
                {"agent_id": a.get("agent_id", ""), "name": a.get("name", ""), "reason": "Skill match"}
                for a in top_picks[1:]
            ],
            "llm_used": False,
        }
