# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: OpportunityTracker — backend (models_wave.py)
# Date: 2025-08-05
# ---------------------------------------------------------------------------
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class UploadedDataset(Base):
    __tablename__ = "wave_uploaded_datasets"

    id = Column(Integer, primary_key=True, index=True)
    kind = Column(String, nullable=False)  # 'scope' | 'categorization'
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    row_count = Column(Integer, nullable=False, default=0)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    rows = relationship("DatasetRow", back_populates="dataset", cascade="all, delete-orphan")


class DatasetRow(Base):
    """Normalized row storage, parsed once at upload time (never re-parse the xlsx later)."""
    __tablename__ = "wave_dataset_rows"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("wave_uploaded_datasets.id"), nullable=False, index=True)
    source_row_index = Column(Integer, nullable=False)
    data = Column(Text, nullable=False)  # JSON blob of the normalized row

    dataset = relationship("UploadedDataset", back_populates="rows")


class AnalysisJob(Base):
    __tablename__ = "wave_analysis_jobs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, nullable=False, default="pending")  # pending|running|done|failed
    scope_dataset_id = Column(Integer, ForeignKey("wave_uploaded_datasets.id"), nullable=False)
    categorization_dataset_id = Column(Integer, ForeignKey("wave_uploaded_datasets.id"), nullable=False)
    total_categories = Column(Integer, nullable=False, default=0)
    completed_categories = Column(Integer, nullable=False, default=0)
    llm_model = Column(String, nullable=True)
    unmatched_categories = Column(Text, nullable=True)  # JSON list, categorization values with no scope match
    user_guidance = Column(Text, nullable=True)  # free-text, advisory-only steering for this run
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)


class WaveCategorySummary(Base):
    """L1 rollup + narrative. One row per (job, category)."""
    __tablename__ = "wave_category_summaries"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("wave_analysis_jobs.id"), nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="pending")  # pending|running|done|failed
    current_step = Column(String, nullable=True)  # human-readable sub-progress, e.g. "Classifying batch 2/3"
    error_message = Column(Text, nullable=True)
    description = Column(Text, nullable=False, default="")
    estimated_app_count = Column(Integer, nullable=False, default=0)
    actual_app_count = Column(Integer, nullable=False, default=0)
    timeline_start = Column(String, nullable=True)
    timeline_end = Column(String, nullable=True)
    classification_logic_notes = Column(Text, nullable=False, default="")
    llm_raw_response = Column(Text, nullable=True)

    apps = relationship("WaveApp", back_populates="category_summary", cascade="all, delete-orphan")


class WaveApp(Base):
    """L3 per-app detail. One row per app per completed job."""
    __tablename__ = "wave_apps"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("wave_analysis_jobs.id"), nullable=False, index=True)
    category_summary_id = Column(Integer, ForeignKey("wave_category_summaries.id"), nullable=False, index=True)
    category = Column(String, nullable=False, index=True)

    app_id = Column(String, nullable=False)
    app_name = Column(String, nullable=False)
    dept = Column(String, nullable=False, default="")        # business-side OLB Level 2 — clustering key
    dept_full = Column(String, nullable=False, default="")   # business-side Department
    dept2 = Column(String, nullable=False, default="")       # IT-org-side OLB Level 2 — display only
    business_owner = Column(String, nullable=False, default="")
    it_owner = Column(String, nullable=False, default="")
    capabilities_raw = Column(Text, nullable=False, default="")
    capability_count = Column(Integer, nullable=False, default=0)
    capability_tier = Column(String, nullable=False, default="")  # Simple|Complex
    matched_specialized_capability = Column(Boolean, nullable=False, default=False)
    matched_specialized_term = Column(String, nullable=True)
    data_quality_flag = Column(Boolean, nullable=False, default=False)  # = Inconsistency
    remediation_required = Column(Boolean, nullable=False, default=False)

    migration_type = Column(String, nullable=False, default="TBD (data gap)")

    disposition = Column(String, nullable=False, default="Harmonization")  # "Harmonization" | "Modernization"
    service_module = Column(String, nullable=True)  # Rehost|Replatform|Refactor|Replace, only if Modernization
    modernization_trigger_category = Column(String, nullable=True)  # IT Security Risk|Legal/Compliance|Technology EOL|Structural Necessity
    disposition_rationale = Column(Text, nullable=False, default="")

    wave = Column(String, nullable=False, default="")  # deterministic, e.g. "Wave 0 (Pilot)", "Wave 1"
    change_management = Column(String, nullable=False, default="")
    decommissioning = Column(String, nullable=False, default="")
    stream2_assessment = Column(String, nullable=True)
    stream3_execution = Column(String, nullable=True)
    ams_transition_start = Column(String, nullable=True)

    notes_assumptions = Column(Text, nullable=False, default="")
    wave_assignment_rationale = Column(Text, nullable=False, default="")

    rejoins_wave = Column(String, nullable=True)
    rejoin_rationale = Column(Text, nullable=True)

    category_summary = relationship("WaveCategorySummary", back_populates="apps")
