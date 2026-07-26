# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: OpportunityTracker — backend (schemas_wave.py)
# Date: 2025-11-13
# ---------------------------------------------------------------------------
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DatasetOut(BaseModel):
    id: int
    kind: str
    filename: str
    row_count: int
    uploaded_at: Optional[datetime]

    class Config:
        from_attributes = True


class CategoryPreviewOut(BaseModel):
    category: str
    app_count: int
    matched_in_scope: bool


class AnalysisSubmitRequest(BaseModel):
    scope_dataset_id: int
    categorization_dataset_id: int
    categories: Optional[list[str]] = None  # None/empty = analyze every category found
    user_guidance: Optional[str] = None  # free-text, advisory-only steering for this run (server truncates to 2000 chars)


class AnalysisSubmitResponse(BaseModel):
    job_id: int
    status: str
    total_categories: int
    unmatched_categories: list[str]


class CategoryStatusOut(BaseModel):
    category: str
    status: str
    current_step: Optional[str] = None
    error_message: Optional[str] = None


class JobStatusOut(BaseModel):
    job_id: int
    status: str
    total_categories: int
    completed_categories: int
    llm_model: Optional[str] = None
    error_message: Optional[str] = None
    categories: list[CategoryStatusOut]


class CategorySummaryOut(BaseModel):
    category: str
    status: str
    error_message: Optional[str] = None
    description: str
    estimated_app_count: int
    actual_app_count: int
    timeline_start: Optional[str] = None
    timeline_end: Optional[str] = None
    classification_logic_notes: str
    data_quality_issues: int
    functional_migration_only: int
    full_consolidation: int
    data_migration_only: int
    tbd_count: int
    wave_count: int
    harmonization_count: int
    modernization_count: int


class WaveSummaryOut(BaseModel):
    wave: str
    app_count: int
    data_quality_flags: int
    functional_migration_only: int
    full_consolidation: int
    data_migration_only: int
    tbd_count: int
    harmonization_count: int
    modernization_count: int
    stream2_assessment: Optional[str] = None
    stream3_execution: Optional[str] = None
    ams_transition_start: Optional[str] = None
    primary_departments: str
    sequencing_rationale: str


class WaveAppOut(BaseModel):
    app_id: str
    app_name: str
    dept: str
    dept_full: str
    dept2: str
    business_owner: str
    it_owner: str
    capabilities_raw: str
    capability_count: int
    capability_tier: str
    data_quality_flag: bool
    remediation_required: bool
    migration_type: str
    disposition: str
    service_module: Optional[str] = None
    modernization_trigger_category: Optional[str] = None
    disposition_rationale: str
    wave: str
    change_management: str
    decommissioning: str
    stream2_assessment: Optional[str] = None
    stream3_execution: Optional[str] = None
    ams_transition_start: Optional[str] = None
    notes_assumptions: str
    wave_assignment_rationale: str
    rejoins_wave: Optional[str] = None
    rejoin_rationale: Optional[str] = None

    class Config:
        from_attributes = True


class GanttRowOut(BaseModel):
    label: str
    app_count: int
    start_quarter: str
    phases: list[str]
