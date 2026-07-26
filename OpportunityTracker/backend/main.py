# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: OpportunityTracker — backend (main.py)
# Date: 2026-02-05
# ---------------------------------------------------------------------------
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine, ensure_wave_schema_migrations
from routers import auth as auth_router
from routers import opportunities as opp_router
from routers import wave_analysis as wave_router
from routers import financial as financial_router
import models_wave  # noqa: F401 - registers wave-planning tables with Base before create_all()

Base.metadata.create_all(bind=engine)
ensure_wave_schema_migrations(engine)

app = FastAPI(title="Opportunity Tracker API", version="1.0.0")

ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5183,http://localhost:3000,http://localhost:5177,http://localhost:8090,http://127.0.0.1:8090",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api")
app.include_router(opp_router.router, prefix="/api")
app.include_router(wave_router.router, prefix="/api")
app.include_router(financial_router.router, prefix="/api")


# Function: health
@app.get("/health")
def health():
    return {"status": "ok", "service": "opportunity-tracker", "port": 8092}
