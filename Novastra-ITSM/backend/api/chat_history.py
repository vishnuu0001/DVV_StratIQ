# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Chat history API with per-user persistence and retention cleanup.
# Date: 2025-10-12
# ---------------------------------------------------------------------------
"""Chat history API with per-user persistence and retention cleanup."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.auth import get_current_user
from backend.services.chat_history_store import (
    create_session,
    delete_session,
    list_sessions,
    replace_session_messages,
)

router = APIRouter(prefix="/api/chat-history", tags=["Chat History"])


class HistoryMessage(BaseModel):
    role: str = Field(..., min_length=1, max_length=20)
    content: str = Field(..., min_length=1, max_length=12000)
    sources: Optional[List[Dict[str, Any]]] = None
    confidence: Optional[float] = None
    context_used: Optional[bool] = None


class CreateSessionRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    provider: str = Field(default="ollama", min_length=1, max_length=40)
    chat_type: str = Field(default="general", min_length=1, max_length=40)


class UpdateSessionMessagesRequest(BaseModel):
    messages: List[HistoryMessage] = Field(default_factory=list)
    title: Optional[str] = Field(default=None, max_length=120)


# Function: get_sessions
@router.get("/sessions")
async def get_sessions(current_user: dict = Depends(get_current_user), limit: int = 100):
    return {"sessions": list_sessions(current_user["id"], include_messages=True, limit=limit)}


# Function: create_history_session
@router.post("/sessions")
async def create_history_session(request: CreateSessionRequest, current_user: dict = Depends(get_current_user)):
    session = create_session(
        user_id=current_user["id"],
        title=request.title,
        provider=request.provider,
        chat_type=request.chat_type,
    )
    return session


# Function: update_history_session
@router.put("/sessions/{session_id}")
async def update_history_session(
    session_id: str,
    request: UpdateSessionMessagesRequest,
    current_user: dict = Depends(get_current_user),
):
    session = replace_session_messages(
        user_id=current_user["id"],
        session_id=session_id,
        messages=[m.model_dump() for m in request.messages],
        title=request.title,
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


# Function: delete_history_session
@router.delete("/sessions/{session_id}")
async def delete_history_session(session_id: str, current_user: dict = Depends(get_current_user)):
    deleted = delete_session(current_user["id"], session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"deleted": True}
