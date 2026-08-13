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
_VALID_PRIORITIES = {"P1", "P2", "P3", "P4"}
_VALID_URGENCIES = {"High", "Medium", "Low"}


# Function: _call_llm
def _call_llm(system_msg: str, user_msg: str) -> str:
    from langchain_ollama import ChatOllama
    from backend.llm.router import assert_ollama_gpu_available

    # Use the live model selected in Settings (and shown in the UI). The
    # analysis-model default is resolved at process startup and can otherwise
    # become stale after an administrator switches the Ollama model.
    model = cfg.OLLAMA_MODEL
    assert_ollama_gpu_available(model)
    llm = ChatOllama(
        model=model, base_url=cfg.OLLAMA_BASE_URL,
        # Classification/reranking responses are compact JSON. A 384-token cap
        # avoids long 14B generations exceeding the Azure/IIS proxy timeout.
        temperature=0.0,
        num_predict=min(384, cfg.OLLAMA_ANALYSIS_NUM_PREDICT),
        num_ctx=cfg.OLLAMA_ANALYSIS_NUM_CTX,
        num_gpu=cfg.OLLAMA_NUM_GPU,
        repeat_penalty=1.1, top_k=20, top_p=0.9,
        format="json", timeout=cfg.OLLAMA_ANALYSIS_TIMEOUT_SECONDS,
        keep_alive=cfg.OLLAMA_KEEP_ALIVE,
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


# Function: _validate_classification
def _validate_classification(parsed: object) -> dict:
    """Validate and normalize an Ollama classification without heuristic defaults."""
    if not isinstance(parsed, dict):
        raise ValueError("Ollama did not return a JSON object")

    required_text = ("category", "subcategory", "assignment_group", "reasoning")
    missing = [key for key in required_text if not str(parsed.get(key) or "").strip()]
    if missing:
        raise ValueError(f"Ollama response is missing: {', '.join(missing)}")

    priority = str(parsed.get("priority") or "").strip().upper()
    urgency = str(parsed.get("urgency") or "").strip().title()
    if priority not in _VALID_PRIORITIES:
        raise ValueError("Ollama returned an invalid priority")
    if urgency not in _VALID_URGENCIES:
        raise ValueError("Ollama returned an invalid urgency")

    try:
        confidence = float(parsed.get("confidence"))
    except (TypeError, ValueError) as exc:
        raise ValueError("Ollama returned an invalid confidence") from exc
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("Ollama confidence must be between 0 and 1")

    return {
        "category": str(parsed["category"]).strip(),
        "subcategory": str(parsed["subcategory"]).strip(),
        "priority": priority,
        "urgency": urgency,
        "assignment_group": str(parsed["assignment_group"]).strip(),
        "confidence": confidence,
        "reasoning": str(parsed["reasoning"]).strip(),
        "llm_used": True,
        "provider": "ollama",
        "model": cfg.OLLAMA_MODEL,
    }


# Function: _validate_summary
def _validate_summary(parsed: object, source_text: str) -> dict:
    """Accept only complete, source-grounded Ollama summary output."""
    if not isinstance(parsed, dict):
        raise ValueError("Ollama did not return a JSON object")
    summary = str(parsed.get("summary") or "").strip()
    if not summary:
        raise ValueError("Ollama returned an empty summary")

    key_actions = parsed.get("key_actions")
    next_steps = parsed.get("next_steps")
    if not isinstance(key_actions, list) or not isinstance(next_steps, list):
        raise ValueError("Ollama actions and next steps must be JSON arrays")

    stop_words = {
        "about", "after", "before", "being", "from", "have", "into", "issue",
        "that", "their", "there", "these", "they", "this", "ticket", "user", "with",
    }
    source_terms = {w for w in re.findall(r"[a-z0-9]+", source_text.lower()) if len(w) >= 4 and w not in stop_words}
    summary_terms = {w for w in re.findall(r"[a-z0-9]+", summary.lower()) if len(w) >= 4 and w not in stop_words}
    if source_terms and summary_terms and len(source_terms & summary_terms) / len(summary_terms) < 0.18:
        raise ValueError("Ollama summary is not grounded in the supplied thread")

    return {
        "summary": summary,
        "key_actions": [str(item).strip() for item in key_actions if str(item).strip()],
        "next_steps": [str(item).strip() for item in next_steps if str(item).strip()],
        "llm_used": True,
        "provider": "ollama",
        "model": cfg.OLLAMA_MODEL,
    }


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
        "You are an expert ITSM ticket classifier. Infer the classification from the complete "
        "ticket semantics, not keyword matching. Return ONLY a JSON object with keys: "
        "category, subcategory, priority (P1/P2/P3/P4), urgency (High/Medium/Low), "
        "assignment_group, confidence (0.0-1.0), reasoning. The reasoning must briefly explain "
        "the semantic evidence and business impact. Apply this priority rubric: P1 is a critical "
        "widespread outage, P2 is major service degradation or high business impact, P3 is a "
        "standard incident with limited impact, and P4 is a routine request or low-impact issue. "
        "Keep priority and urgency consistent. No Markdown and no extra text."
    )
    user_msg = f"Title: {title}\nDescription: {description}\nHint assignment_group: {assignment_group}"

    try:
        timeout = max(5, int(cfg.OLLAMA_ANALYSIS_TIMEOUT_SECONDS)) + 5
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, user_msg), timeout=timeout)
        return _validate_classification(_extract_json(raw))
    except Exception as exc:
        model = cfg.OLLAMA_MODEL
        logger.exception("Ollama ticket classification failed (model=%s): %s", model, exc)
        raise HTTPException(
            status_code=503,
            detail=(
                f"Ollama classification failed using model '{model}'. "
                "Verify that Ollama is reachable and the configured model is installed and running. "
                "No heuristic classification was returned."
            ),
        ) from exc


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
    ticket_id = str(payload.get("ticket_id") or "").strip()
    raw_thread = payload.get("thread", [])
    if not ticket_id:
        raise HTTPException(status_code=422, detail="Ticket ID is required for summarization.")
    if not isinstance(raw_thread, list):
        raise HTTPException(status_code=422, detail="Thread messages must be a list.")

    thread = []
    for message in raw_thread:
        if not isinstance(message, dict):
            continue
        content = str(message.get("content") or "").strip()
        if content:
            thread.append({
                "author": str(message.get("author") or "Unknown").strip(),
                "timestamp": str(message.get("timestamp") or "").strip(),
                "content": content,
            })
    if not thread:
        raise HTTPException(
            status_code=422,
            detail="Add at least one non-empty thread message before summarizing.",
        )

    thread_text = "\n".join(
        f"[{m.get('timestamp','')}] {m.get('author','')}: {m.get('content','')}" for m in thread
    )
    system_msg = (
        "You are an evidence-grounded ITSM shift-handoff analyst. Use ONLY facts explicitly "
        "present in the supplied thread. Do not import facts from other tickets, prior prompts, "
        "general knowledge, or assumptions. Write a concise summary of the reported issue and "
        "current state (maximum 120 words). key_actions must contain ONLY actions explicitly "
        "documented as already completed. next_steps must contain ONLY pending actions explicitly "
        "documented in the thread. Use an empty array when completed actions or pending steps are "
        "not stated. Return ONLY JSON: "
        "{\"summary\": str, \"key_actions\": [str], \"next_steps\": [str]}."
    )
    try:
        timeout = max(5, int(cfg.OLLAMA_ANALYSIS_TIMEOUT_SECONDS)) + 5
        user_msg = f"Ticket ID: {ticket_id}\nThread (the only source of truth):\n{thread_text}"
        raw = await asyncio.wait_for(asyncio.to_thread(_call_llm, system_msg, user_msg), timeout=timeout)
        result = _validate_summary(_extract_json(raw), thread_text)
        result["ticket_id"] = ticket_id
        return result
    except Exception as exc:
        logger.exception("Ollama thread summarization failed (ticket=%s): %s", ticket_id, exc)
        raise HTTPException(
            status_code=503,
            detail=(
                f"Ollama could not produce a grounded summary for ticket '{ticket_id}'. "
                "Review the thread content and try again; no fallback summary was returned."
            ),
        ) from exc
