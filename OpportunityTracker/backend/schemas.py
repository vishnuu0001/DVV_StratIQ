# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: OpportunityTracker — backend (schemas.py)
# Date: 2025-12-07
# ---------------------------------------------------------------------------
from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime


class OpportunityBase(BaseModel):
    region: str = ""
    customer_group: str = ""
    sub_vertical: str = ""
    solution_offering: str = ""
    so_coe_leader: str = ""
    crm_ref: str = ""
    opportunity_name: str
    oppty_stage: str = "Prospecting"
    start_date: str = ""
    oppty_owner: str = ""
    tcv_mn: float = Field(default=0.0, ge=0)
    q1_mn: float = Field(default=0.0, ge=0)
    q2_mn: float = Field(default=0.0, ge=0)
    q3_mn: float = Field(default=0.0, ge=0)
    q4_mn: float = Field(default=0.0, ge=0)
    remarks: str = ""
    hyperscaler: str = ""
    delivery_ibu: str = ""
    delivery_ibu_leader: str = ""
    delivery_validation: str = "No"


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityUpdate(OpportunityBase):
    pass


class OpportunityOut(OpportunityBase):
    id: int
    fy27_mn: float
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ImportResultOut(BaseModel):
    created: int
    updated: int
    warnings: list[str] = Field(default_factory=list)


class FinancialSummaryOut(BaseModel):
    target_fy27_mn: float
    actual_fy27_mn: float
    gap_fy27_mn: float
    attainment_pct: float
    opportunity_count: int
    closed_won_count: int
    by_region: list[dict[str, Any]]
    by_stage: list[dict[str, Any]]
    by_sub_vertical: list[dict[str, Any]]
    data_quality: dict[str, Any]
    gap_closure_plan: list[dict[str, Any]]
    deals_needed_to_close_gap: int


class NarrativeStartResponse(BaseModel):
    job_id: int
    status: str


class NarrativeJobOut(BaseModel):
    job_id: int
    status: str
    llm_model: Optional[str] = None
    narrative_text: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class NarrativeStartRequest(BaseModel):
    user_guidance: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str
    username: str
    role: str
