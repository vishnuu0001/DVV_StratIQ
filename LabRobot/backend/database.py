# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: LabRobot — backend (database.py)
# Date: 2026-07-02
# ---------------------------------------------------------------------------
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

SQLALCHEMY_DATABASE_URL = "sqlite:///./lab_management.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# Function: get_db
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
