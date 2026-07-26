# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — backend/api (knowledge_mgmt.py)
# Date: 2025-11-13
# ---------------------------------------------------------------------------
from __future__ import annotations
import asyncio, json, logging, re
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from fastapi import APIRouter, Body, Depends, HTTPException
from backend.api.auth import get_current_user
import backend.config as cfg

router = APIRouter(prefix="/api/knowledge-mgmt", tags=["Knowledge Management"])
logger = logging.getLogger(__name__)
_LLM_TIMEOUT = 90


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


# Function: _template_article
def _template_article(title: str, resolution_steps: list[str], category: str, tags: list[str]) -> dict:
    steps_md = "\n".join(f"{i+1}. {s}" for i, s in enumerate(resolution_steps))
    draft = f"# {title}\n\n## Summary\nThis article describes how to resolve {title}.\n\n## Resolution Steps\n{steps_md}\n"
    return {
        "article_title": title, "summary": f"Step-by-step guide for: {title}",
        "symptoms": ["User reports " + title],
        "resolution_steps": resolution_steps,
        "prerequisites": ["Access to relevant system"], "notes": "",
        "tags": tags or [category],
        "draft_markdown": draft, "llm_used": False,
    }


# Function: generate_article
@router.post("/generate-article")
async def generate_article(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    ticket_id = payload.get("ticket_id", "")
    title = payload.get("title", "")
    resolution_steps = payload.get("resolution_steps", [])
    category = payload.get("category", "")
    tags = payload.get("tags", [])

    steps_text = "\n".join(f"- {s}" for s in resolution_steps)
    system_msg = (
        "You are a Knowledge Base author. Generate a structured KB article from a resolved ticket. "
        "Return JSON: {\"article_title\": str, \"summary\": str, \"symptoms\": [str], "
        "\"resolution_steps\": [str], \"prerequisites\": [str], \"notes\": str, "
        "\"tags\": [str], \"draft_markdown\": str}"
    )
    user_msg = f"Ticket ID: {ticket_id}\nTitle: {title}\nCategory: {category}\nResolution Steps:\n{steps_text}"

    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, user_msg), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed["llm_used"] = True
        parsed.setdefault("article_title", title)
        parsed.setdefault("summary", "")
        parsed.setdefault("symptoms", [])
        parsed.setdefault("resolution_steps", resolution_steps)
        parsed.setdefault("prerequisites", [])
        parsed.setdefault("notes", "")
        parsed.setdefault("tags", tags)
        parsed.setdefault("draft_markdown", "")
        return parsed
    except Exception as exc:
        logger.warning("generate_article LLM failed: %s", exc)
        return _template_article(title, resolution_steps, category, tags)


# Function: gap_analysis
@router.post("/gap-analysis")
async def gap_analysis(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    tickets = payload.get("unresolved_tickets", [])

    cat_counts: Counter = Counter(t.get("category", "General") for t in tickets)
    heuristic_gaps = [
        {"topic": cat, "frequency": count,
         "priority": "HIGH" if count > 5 else "MEDIUM" if count > 2 else "LOW",
         "suggested_article_title": f"How to resolve {cat} issues",
         "coverage_status": "Missing"}
        for cat, count in cat_counts.most_common(10)
    ]
    total = len(tickets)
    covered = max(0, total - sum(cat_counts.values()))
    coverage_score = round((covered / total * 100) if total else 100, 1)

    tickets_text = "\n".join(
        f"- [{t.get('category','')}] {t.get('title','')}: {t.get('description','')[:100]}"
        for t in tickets[:50]
    )
    system_msg = (
        "You are a KB Gap Analyst. Identify topics missing from the knowledge base based on unresolved tickets. "
        "Return JSON: {\"gaps\": [{\"topic\": str, \"frequency\": int, \"priority\": str, "
        "\"suggested_article_title\": str, \"coverage_status\": str}], "
        "\"coverage_score\": float, \"total_unresolved\": int}"
    )
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, tickets_text), timeout=60)
        parsed = _extract_json(raw) or {}
        parsed["llm_used"] = True
        parsed.setdefault("gaps", heuristic_gaps)
        parsed.setdefault("total_unresolved", total)
        parsed.setdefault("coverage_score", coverage_score)
        return parsed
    except Exception as exc:
        logger.warning("gap_analysis LLM failed: %s", exc)
        return {"gaps": heuristic_gaps, "total_unresolved": total,
                "coverage_score": coverage_score, "llm_used": False}
