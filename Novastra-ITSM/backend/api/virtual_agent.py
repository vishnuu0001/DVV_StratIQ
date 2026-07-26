# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — backend/api (virtual_agent.py)
# Date: 2026-05-08
# ---------------------------------------------------------------------------
from __future__ import annotations
import asyncio, json, logging, re, threading, uuid
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Body, Depends, HTTPException
from backend.api.auth import get_current_user
import backend.config as cfg

router = APIRouter(prefix="/api/virtual-agent", tags=["Virtual Agent"])
logger = logging.getLogger(__name__)
_LLM_TIMEOUT = 60  # reduced from 90 — L0/L1 replies are short

# ── Cached LLM (created once, reused across requests) ────────────────────────
_CHAT_LLM = None
_CHAT_LLM_LOCK = threading.Lock()

# Function: _get_chat_llm
def _get_chat_llm():
    global _CHAT_LLM
    if _CHAT_LLM is not None:
        return _CHAT_LLM
    with _CHAT_LLM_LOCK:
        if _CHAT_LLM is None:
            from langchain_ollama import ChatOllama
            _CHAT_LLM = ChatOllama(
                model=cfg.OLLAMA_MODEL,
                base_url=cfg.OLLAMA_BASE_URL,
                temperature=0.3,
                num_predict=512,   # L0/L1 replies are concise — was 2048
                num_ctx=4096,      # trimmed from 6144
                repeat_penalty=1.1,
                top_k=20,
                top_p=0.9,
                format="json",
                timeout=_LLM_TIMEOUT,
                keep_alive=cfg.OLLAMA_KEEP_ALIVE,
            )
            logger.info("Virtual-agent LLM instance created and cached")
    return _CHAT_LLM


_TRANSLATE_LLM = None
_TRANSLATE_LLM_LOCK = threading.Lock()

# Function: _get_translate_llm
def _get_translate_llm():
    global _TRANSLATE_LLM
    if _TRANSLATE_LLM is not None:
        return _TRANSLATE_LLM
    with _TRANSLATE_LLM_LOCK:
        if _TRANSLATE_LLM is None:
            from langchain_ollama import ChatOllama
            _TRANSLATE_LLM = ChatOllama(
                model=cfg.OLLAMA_MODEL,
                base_url=cfg.OLLAMA_BASE_URL,
                temperature=0.1,
                num_predict=1024,
                num_ctx=4096,
                format="json",
                timeout=_LLM_TIMEOUT,
                keep_alive=cfg.OLLAMA_KEEP_ALIVE,
            )
    return _TRANSLATE_LLM


# Function: _extract_json
def _extract_json(raw: str) -> dict | None:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except Exception:
        pass
    s, e = text.find('{'), text.rfind('}')
    if s >= 0 and e > s:
        try:
            return json.loads(text[s:e + 1])
        except Exception:
            pass
    return None


# ── Instant heuristic fast-path ──────────────────────────────────────────────
# Handles the most common L0 intents without any LLM call.
_FAST_RESPONSES: list[tuple[list[str], str, str]] = [
    # (keywords, response, intent)
    (["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "howdy", "greet"],
     "Hello! I'm your L0/L1 IT Support Virtual Agent. How can I help you today? I can assist with password resets, VPN issues, software requests, and general IT queries.",
     "greeting"),
    (["password", "reset", "forgot", "locked out", "unlock account", "change password"],
     "To reset your password:\n1. Visit the Self-Service Password Reset portal at https://sspr.company.com\n2. Verify your identity via your mobile number or backup email.\n3. Set a new password.\n\nAlternatively, call the IT Service Desk at ext. 4357. Is there anything else I can help you with?",
     "password_reset"),
    (["vpn", "remote access", "connect from home", "cisco anyconnect", "remote work"],
     "To connect via VPN:\n1. Open Cisco AnyConnect on your device.\n2. Enter: vpn.company.com\n3. Log in with your network username and password.\n\nIf AnyConnect fails to launch, restart it and try again. For persistent issues, raise an incident at servicedesk.company.com.",
     "vpn_support"),
    (["software", "install", "installation", "application request", "app request", "license"],
     "To request software installation:\n1. Go to the IT Service Catalog at servicedesk.company.com/catalog\n2. Search for the software you need.\n3. Submit a request.\n\nApproval typically takes 1–2 business days. Is there a specific application you need?",
     "software_request"),
    (["slow", "laptop slow", "computer slow", "performance", "freezing", "hanging"],
     "For a slow computer, try these steps:\n1. Restart the device.\n2. Close unnecessary browser tabs and applications.\n3. Check for Windows updates (Settings → Update & Security).\n4. Run Disk Cleanup.\n\nIf the issue persists after a restart, raise an incident at servicedesk.company.com.",
     "performance_issue"),
    (["printer", "print", "printing", "cannot print"],
     "For printer issues:\n1. Check the printer is powered on and connected to the network.\n2. Remove and re-add the printer (Settings → Printers & Scanners).\n3. Clear the print queue.\n\nIf the issue continues, raise an incident and a technician will assist.",
     "printer_issue"),
    (["email", "outlook", "teams", "microsoft teams", "not receiving email", "office 365"],
     "For email or Teams issues:\n1. Restart the application.\n2. Check your internet connection.\n3. Sign out and sign back in.\n\nFor persistent issues, visit servicedesk.company.com or call ext. 4357.",
     "communication_tool"),
    (["thank", "thanks", "thank you", "cheers", "bye", "goodbye", "that's all", "thats all"],
     "You're welcome! Feel free to reach out whenever you need IT support. Have a great day!",
     "farewell"),
]


# Function: _fast_heuristic
def _fast_heuristic(message: str, session_id: str) -> dict | None:
    """Return an instant response if the message matches a known L0 pattern."""
    msg = message.lower().strip()
    for keywords, response, intent in _FAST_RESPONSES:
        if any(kw in msg for kw in keywords):
            escalate = any(w in msg for w in ["urgent", "critical", "manager", "vp", "director"])
            return {
                "response": response,
                "intent": intent,
                "confidence": 0.92,
                "escalate": escalate,
                "session_id": session_id,
                "llm_used": False,
            }
    return None


# Function: _sync_chat
def _sync_chat(system_msg: str, messages: list) -> str:
    llm = _get_chat_llm()
    with ThreadPoolExecutor(max_workers=1) as pool:
        result = pool.submit(llm.invoke, messages).result(timeout=_LLM_TIMEOUT)
    return result.content if hasattr(result, "content") else str(result)


# Function: _sync_translate
def _sync_translate(system_msg: str, user_msg: str) -> str:
    llm = _get_translate_llm()
    with ThreadPoolExecutor(max_workers=1) as pool:
        result = pool.submit(llm.invoke, [("system", system_msg), ("human", user_msg)]).result(timeout=_LLM_TIMEOUT)
    return result.content if hasattr(result, "content") else str(result)


# Function: _heuristic_chat
def _heuristic_chat(message: str, session_id: str) -> dict:
    msg = message.lower()
    if any(w in msg for w in ["password", "login", "access", "locked"]):
        response = "I can help with password resets. Please visit the Self-Service Portal at https://sspr.company.com or call ext. 4357."
        intent = "password_reset"
    elif any(w in msg for w in ["vpn", "remote", "connect"]):
        response = "For VPN issues: open Cisco AnyConnect, enter vpn.company.com, and log in with your network credentials."
        intent = "vpn_support"
    else:
        response = "I'm here to help with IT support. Could you please describe your issue in more detail? I can assist with password resets, VPN, software requests, and more."
        intent = "general_inquiry"
    return {
        "response": response, "intent": intent, "confidence": 0.7,
        "escalate": False, "session_id": session_id, "llm_used": False,
    }


# Function: chat
@router.post("/chat")
async def chat(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    message = (payload.get("message") or "").strip()
    session_id = payload.get("session_id") or str(uuid.uuid4())
    history = payload.get("history") or []
    language = payload.get("language", "en")

    if not message:
        return {"response": "Please type a message.", "intent": "empty", "confidence": 1.0,
                "escalate": False, "session_id": session_id, "llm_used": False}

    # ── Fast path: instant response for known L0 intents ─────────────────────
    fast = _fast_heuristic(message, session_id)
    if fast:
        return fast

    # ── LLM path ─────────────────────────────────────────────────────────────
    # Only last 5 turns to minimise context length
    recent = history[-10:]  # 5 user+agent pairs = 10 messages
    system_msg = (
        "You are a concise L0/L1 IT Support Virtual Agent. "
        "Reply in under 80 words. Be friendly, direct, and helpful. "
        "If the issue needs human support, set escalate=true. "
        f"Reply in language: {language}. "
        'Return ONLY valid JSON: {"response": "...", "intent": "...", "confidence": 0.0, "escalate": false}'
    )
    lc_messages: list = [("system", system_msg)]
    for m in recent:
        role = "human" if m.get("role") == "user" else "assistant"
        lc_messages.append((role, m.get("content", "")))
    lc_messages.append(("human", message))

    try:
        raw = await asyncio.to_thread(_sync_chat, system_msg, lc_messages)
        parsed = _extract_json(raw) or {}
        parsed["session_id"] = session_id
        parsed["llm_used"] = True
        parsed.setdefault("response", "I'm working on your request. Please hold on.")
        parsed.setdefault("intent", "unknown")
        parsed.setdefault("confidence", 0.8)
        parsed.setdefault("escalate", False)
        return parsed
    except Exception as exc:
        logger.warning("virtual_agent chat LLM failed: %s", exc)
        return _heuristic_chat(message, session_id)


# Function: translate
@router.post("/translate")
async def translate(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    text = payload.get("text", "").strip()
    target_language = payload.get("target_language", "English")

    if not text:
        return {"translated": "", "source_language_detected": "unknown",
                "target_language": target_language, "llm_used": False}

    system_msg = (
        "You are a professional translator. Translate accurately. "
        'Return ONLY valid JSON: {"translated": "...", "source_language_detected": "..."}'
    )
    user_msg = f"Translate to {target_language}:\n\n{text}"

    try:
        raw = await asyncio.to_thread(_sync_translate, system_msg, user_msg)
        parsed = _extract_json(raw) or {}
        parsed.setdefault("translated", text)
        parsed.setdefault("source_language_detected", "unknown")
        parsed["target_language"] = target_language
        parsed["llm_used"] = True
        return parsed
    except Exception as exc:
        logger.warning("translate LLM failed: %s", exc)
        return {"translated": text, "source_language_detected": "unknown",
                "target_language": target_language, "llm_used": False}
