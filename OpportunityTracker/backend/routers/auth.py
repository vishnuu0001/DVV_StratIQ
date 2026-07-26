# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: OpportunityTracker — backend/routers (auth.py)
# Date: 2026-03-31
# ---------------------------------------------------------------------------
from fastapi import APIRouter
from schemas import LoginRequest, TokenResponse
from auth import authenticate, create_token

router = APIRouter(tags=["auth"])


# Function: login
@router.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest):
    user = authenticate(req.username, req.password)
    token = create_token(user["username"])
    return TokenResponse(token=token, username=user["username"], role=user["role"])
