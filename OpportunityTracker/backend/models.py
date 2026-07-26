# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: OpportunityTracker — backend (models.py)
# Date: 2026-05-09
# ---------------------------------------------------------------------------
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, func
from database import Base


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, nullable=False, default="")
    customer_group = Column(String, nullable=False, default="")
    sub_vertical = Column(String, nullable=False, default="")
    solution_offering = Column(String, nullable=False, default="")
    so_coe_leader = Column(String, nullable=False, default="")
    crm_ref = Column(String, nullable=False, default="")
    opportunity_name = Column(String, nullable=False)
    oppty_stage = Column(String, nullable=False, default="Prospecting")
    start_date = Column(String, nullable=False, default="")
    oppty_owner = Column(String, nullable=False, default="")
    tcv_mn = Column(Float, nullable=False, default=0.0)
    q1_mn = Column(Float, nullable=False, default=0.0)
    q2_mn = Column(Float, nullable=False, default=0.0)
    q3_mn = Column(Float, nullable=False, default=0.0)
    q4_mn = Column(Float, nullable=False, default=0.0)
    remarks = Column(String, nullable=False, default="")
    hyperscaler = Column(String, nullable=False, default="")
    delivery_ibu = Column(String, nullable=False, default="")
    delivery_ibu_leader = Column(String, nullable=False, default="")
    delivery_validation = Column(String, nullable=False, default="No")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Function: fy27_mn
    @property
    def fy27_mn(self) -> float:
        return round((self.q1_mn or 0) + (self.q2_mn or 0) + (self.q3_mn or 0) + (self.q4_mn or 0), 4)


class FinancialNarrativeJob(Base):
    """One row per Ollama gap-analysis narrative request. summary_snapshot freezes
    the exact Target/Actual/Gap numbers the narrative was generated from, so a
    stale narrative can never be silently misattributed to newer opportunity data."""
    __tablename__ = "financial_narrative_jobs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, nullable=False, default="pending")  # pending|running|done|failed
    llm_model = Column(String, nullable=True)
    summary_snapshot = Column(Text, nullable=False, default="")
    narrative_text = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
