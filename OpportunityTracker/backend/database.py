# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: OpportunityTracker — backend (database.py)
# Date: 2026-03-13
# ---------------------------------------------------------------------------
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DB_PATH = os.getenv("OT_DB_PATH", "opportunity_tracker.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Function: get_db
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Columns added to existing wave-planning tables after their initial release.
# Base.metadata.create_all() only creates missing TABLES, not columns on tables
# that already exist, so additive columns need an explicit, idempotent ALTER TABLE.
_WAVE_SCHEMA_MIGRATIONS = {
    "wave_apps": {
        "disposition": "VARCHAR NOT NULL DEFAULT 'Harmonization'",
        "service_module": "VARCHAR",
        "modernization_trigger_category": "VARCHAR",
        "disposition_rationale": "TEXT NOT NULL DEFAULT ''",
    },
    "wave_analysis_jobs": {
        "user_guidance": "TEXT",
    },
}


# Function: ensure_wave_schema_migrations
def ensure_wave_schema_migrations(engine) -> None:
    with engine.connect() as conn:
        for table, columns in _WAVE_SCHEMA_MIGRATIONS.items():
            existing = {row[1] for row in conn.exec_driver_sql(f"PRAGMA table_info({table})")}
            for col_name, col_def in columns.items():
                if col_name in existing:
                    continue
                conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")
        conn.commit()
