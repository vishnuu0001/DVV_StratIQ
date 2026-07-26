# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: AI_Vehicle_Loan — api (main.py)
# Date: 2025-10-13
# ---------------------------------------------------------------------------
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import random

try:
    from .data_service import data_service, VEHICLE_DATABASE
    from .auth import AI_VEHICLE_LOAN_APP, auth_required, decode_access_token, extract_bearer_token
except ImportError:
    from data_service import data_service, VEHICLE_DATABASE
    from auth import AI_VEHICLE_LOAN_APP, auth_required, decode_access_token, extract_bearer_token

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_PUBLIC_PATHS = {"/", "/api/health", "/docs", "/openapi.json", "/redoc"}


# Function: enforce_auth
@app.middleware("http")
async def enforce_auth(request: Request, call_next):
    path = request.url.path
    if request.method == "OPTIONS" or not auth_required() or not path.startswith("/api") or path in _PUBLIC_PATHS:
        return await call_next(request)
    token = extract_bearer_token(request.headers.get("Authorization", ""))
    if not token:
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=401)
    if payload.get("role") != "admin" and AI_VEHICLE_LOAN_APP not in (payload.get("apps") or []):
        return JSONResponse({"error": "Access denied for AI Vehicle Loan"}, status_code=403)
    request.state.auth = payload
    return await call_next(request)


class AnalysisRequest(BaseModel):
    vehicle_id: int
    user_score: int


# Function: health
@app.get("/api/health")
async def health():
    return {"status": "ok", "module": "AI_Vehicle_Loan"}


# Function: get_vehicles
@app.get("/api/vehicles")
async def get_vehicles():
    """Returns inventory with fixed /api prefix to resolve 404."""
    return data_service.get_all_vehicles()


# Function: get_stats
@app.get("/api/stats")
async def get_stats():
    """Returns dashboard analytics."""
    return {
        "todays_approvals": random.randint(20, 50),
        "average_rate": "6.61%",
        "active_users": random.randint(150, 400)
    }


# Function: analyze_loan
@app.post("/api/analyze-loan")
async def analyze_loan(request: AnalysisRequest):
    """Performs score-based branching for Alice vs Bob."""
    vehicle = next((v for v in VEHICLE_DATABASE if v["id"] == request.vehicle_id), None)
    score = request.user_score

    if score >= 700:
        status = "Approved"
        # Prime matches for Alice
        lenders = [
            {"name": "Global Finance", "apr": "5.29%", "match": "98%"},
            {"name": "Stellar Bank", "apr": "5.45%", "match": "92%"},
            {"name": "Velocity Credit", "apr": "5.80%", "match": "89%"}
        ]
    else:
        status = "Declined"
        lenders = []

    return {
        "status": status,
        "credit_score": score,
        "lenders": lenders,
        "vehicle_model": vehicle["model"] if vehicle else "Unknown"
    }
