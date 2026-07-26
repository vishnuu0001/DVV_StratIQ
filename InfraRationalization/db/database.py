# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: db/database.py
# Date: 2025-12-25
# ---------------------------------------------------------------------------
"""
db/database.py
SQLAlchemy engine + session factory for InfraRationalization.

Uses SQLite by default (file: infra_scans.db next to this package).
Override with env var:  INFRA_DB_URL=postgresql://user:pass@host/dbname
"""
from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

_DB_DIR = Path(__file__).resolve().parent.parent / "data"
_DB_DIR.mkdir(exist_ok=True)

_DEFAULT_DB_URL = f"sqlite:///{_DB_DIR / 'infra_scans.db'}"
DB_URL = os.environ.get("INFRA_DB_URL", _DEFAULT_DB_URL)

# SQLite needs check_same_thread=False for FastAPI (multiple threads per process)
_connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}

engine = create_engine(
    DB_URL,
    connect_args=_connect_args,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Function: init_db
def init_db() -> None:
    """Create all tables if they don't already exist."""
    Base.metadata.create_all(bind=engine)


# Function: get_db
def get_db():
    """FastAPI dependency — yields a DB session and closes it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
