# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: db/models.py
# Date: 2025-10-18
# ---------------------------------------------------------------------------
"""
db/models.py
SQLAlchemy ORM models for CodeAnalysis.

TABLE MAP (one row = one analysis job unless noted)
────────────────────────────────────────────────────
ca_jobs                  – master job registry (PK: job_id)
  ├─ ca_app_profile      – App Profile tab  (1:1 with ca_jobs)
  ├─ ca_health           – Health scores    (1:1)
  ├─ ca_debt             – Technical Debt   (1:1)
  ├─ ca_cloud            – Cloud Maturity   (1:1)
  ├─ ca_oss              – OSS Safety score (1:1)
  │    └─ ca_oss_deps    – per-dependency rows (1:N via job_id)
  ├─ ca_impact           – Business Impact  (1:1)
  ├─ ca_co2              – CO₂ Reduction    (1:1)
  ├─ ca_green            – Green Impact     (1:1)
  │    └─ ca_green_deficiencies (1:N)
  ├─ ca_architecture     – Architecture tab (1:1)
  │    ├─ ca_arch_layers (1:N)
  │    └─ ca_arch_nodes  (1:N)
  ├─ ca_cloud_recs       – Cloud Services tab (1:1)
  ├─ ca_lang_reports     – Languages tab (1:N per language)
  │    └─ ca_lang_files  – per-file metrics (1:N per language report)
  ├─ ca_health_per_lang  – Health by Tech tab row (1:N)
  └─ ca_ai_analysis      – AI Analysis tab (1:1)
       ├─ ca_ai_debt_hotspots   (1:N)
       ├─ ca_ai_cloud_blockers  (1:N)
       ├─ ca_ai_microservices   (1:N)
       ├─ ca_ai_business_rules  (1:N)
       └─ ca_ai_transform_paths (1:N)
"""
from __future__ import annotations

import json as _json
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Text, func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


# ── helpers ───────────────────────────────────────────────────────────────────

# Function: _j
def _j(v) -> str | None:
    """Serialise a Python object to JSON text; None → None."""
    return _json.dumps(v) if v is not None else None


# Function: _dj
def _dj(v) -> object:
    """Deserialise JSON text; None → None."""
    return _json.loads(v) if v is not None else None


# ═══════════════════════════════════════════════════════════════════════════════
# MASTER JOB REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

class CAJob(Base):
    """
    One row per analysis job.  Acts as the root PK that all other
    tables reference.  Mirrors the file-backed `.jobs/{id}.json` store.
    """
    __tablename__ = "ca_jobs"

    job_id      = Column(String(64), primary_key=True)
    job_type    = Column(String(16), nullable=False, default="single")  # single | portfolio | ai
    status      = Column(String(16), nullable=False, default="pending") # pending|running|done|error
    progress    = Column(Integer,    nullable=False, default=0)
    message     = Column(Text,       nullable=True)
    repo_name   = Column(String(255),nullable=True)
    repo_url    = Column(String(500),nullable=True)
    repo_path   = Column(String(500),nullable=True)
    json_path   = Column(String(500),nullable=True)
    html_path   = Column(String(500),nullable=True)
    created_at  = Column(DateTime,   server_default=func.now(), nullable=False)
    completed_at= Column(DateTime,   nullable=True)

    # 1:1 children
    app_profile     = relationship("CAAppProfile",    back_populates="job", uselist=False, cascade="all, delete-orphan")
    health          = relationship("CAHealth",         back_populates="job", uselist=False, cascade="all, delete-orphan")
    debt            = relationship("CADebt",           back_populates="job", uselist=False, cascade="all, delete-orphan")
    cloud           = relationship("CACloud",          back_populates="job", uselist=False, cascade="all, delete-orphan")
    oss             = relationship("CAOss",            back_populates="job", uselist=False, cascade="all, delete-orphan")
    impact          = relationship("CAImpact",         back_populates="job", uselist=False, cascade="all, delete-orphan")
    co2             = relationship("CACo2",            back_populates="job", uselist=False, cascade="all, delete-orphan")
    green           = relationship("CAGreen",          back_populates="job", uselist=False, cascade="all, delete-orphan")
    architecture    = relationship("CAArchitecture",   back_populates="job", uselist=False, cascade="all, delete-orphan")
    cloud_recs      = relationship("CACloudRecs",      back_populates="job", uselist=False, cascade="all, delete-orphan")
    ai_analysis     = relationship("CAAiAnalysis",     back_populates="job", uselist=False, cascade="all, delete-orphan")

    # 1:N children
    oss_deps        = relationship("CAOssDep",         back_populates="job", cascade="all, delete-orphan")
    lang_reports    = relationship("CALangReport",     back_populates="job", cascade="all, delete-orphan")
    health_per_lang = relationship("CAHealthPerLang",  back_populates="job", cascade="all, delete-orphan")

    # Function: to_dict
    def to_dict(self) -> dict:
        return {
            "job_id":       self.job_id,
            "job_type":     self.job_type,
            "status":       self.status,
            "progress":     self.progress,
            "message":      self.message,
            "repo_name":    self.repo_name,
            "repo_url":     self.repo_url,
            "created_at":   self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — APP PROFILE  (rationalization_profile scorecard)
# ═══════════════════════════════════════════════════════════════════════════════

class CAAppProfile(Base):
    __tablename__ = "ca_app_profile"

    id                       = Column(Integer,    primary_key=True, autoincrement=True)
    job_id                   = Column(String(64), ForeignKey("ca_jobs.job_id", ondelete="CASCADE"), unique=True, nullable=False)
    app_id                   = Column(String(64), nullable=True)
    app_name                 = Column(String(255),nullable=True)
    server_name              = Column(String(255),nullable=True)
    repo_name                = Column(String(500),nullable=True)
    total_sloc               = Column(Integer,    nullable=True)
    total_files              = Column(Integer,    nullable=True)
    languages_detected       = Column(Text,       nullable=True)   # JSON list
    application_architecture = Column(String(128),nullable=True)
    source_code_availability = Column(String(64), nullable=True)
    programming_language     = Column(Text,       nullable=True)
    primary_language         = Column(String(64), nullable=True)
    component_coupling       = Column(String(32), nullable=True)
    cloud_suitability        = Column(String(64), nullable=True)
    cloud_score              = Column(Float,      nullable=True)
    volume_external_deps     = Column(String(64), nullable=True)
    total_deps_count         = Column(Integer,    nullable=True)
    api_readiness            = Column(String(64), nullable=True)
    code_protocol_degree     = Column(String(32), nullable=True)
    code_design              = Column(String(32), nullable=True)
    elegance_score           = Column(Float,      nullable=True)
    complexity_volume        = Column(String(128),nullable=True)
    complexity_level         = Column(String(32), nullable=True)
    avg_cyclomatic           = Column(Float,      nullable=True)
    distributed_architecture = Column(String(255),nullable=True)

    job = relationship("CAJob", back_populates="app_profile")

    # Function: to_dict
    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "app_id": self.app_id,
            "app_name": self.app_name,
            "server_name": self.server_name,
            "repo_name": self.repo_name,
            "total_sloc": self.total_sloc,
            "total_files": self.total_files,
            "languages_detected": _dj(self.languages_detected),
            "application_architecture": self.application_architecture,
            "source_code_availability": self.source_code_availability,
            "programming_language": self.programming_language,
            "primary_language": self.primary_language,
            "component_coupling": self.component_coupling,
            "cloud_suitability": self.cloud_suitability,
            "cloud_score": self.cloud_score,
            "volume_external_deps": self.volume_external_deps,
            "total_deps_count": self.total_deps_count,
            "api_readiness": self.api_readiness,
            "code_protocol_degree": self.code_protocol_degree,
            "code_design": self.code_design,
            "elegance_score": self.elegance_score,
            "complexity_volume": self.complexity_volume,
            "complexity_level": self.complexity_level,
            "avg_cyclomatic": self.avg_cyclomatic,
            "distributed_architecture": self.distributed_architecture,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# TAB — HEALTH SCORES
# ═══════════════════════════════════════════════════════════════════════════════

class CAHealth(Base):
    __tablename__ = "ca_health"

    id              = Column(Integer,    primary_key=True, autoincrement=True)
    job_id          = Column(String(64), ForeignKey("ca_jobs.job_id", ondelete="CASCADE"), unique=True, nullable=False)
    health          = Column(Float,      nullable=True)
    maintainability = Column(Float,      nullable=True)
    reliability     = Column(Float,      nullable=True)
    elegance        = Column(Float,      nullable=True)
    risk_label      = Column(String(32), nullable=True)

    job = relationship("CAJob", back_populates="health")

    # Function: to_dict
    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in
                ("job_id","health","maintainability","reliability","elegance","risk_label")}


# ═══════════════════════════════════════════════════════════════════════════════
# TAB — TECHNICAL DEBT ADVISOR
# ═══════════════════════════════════════════════════════════════════════════════

class CADebt(Base):
    __tablename__ = "ca_debt"

    id            = Column(Integer,    primary_key=True, autoincrement=True)
    job_id        = Column(String(64), ForeignKey("ca_jobs.job_id", ondelete="CASCADE"), unique=True, nullable=False)
    debt_months   = Column(Float,      nullable=True)
    debt_usd      = Column(Float,      nullable=True)
    density       = Column(Float,      nullable=True)
    interest_rate = Column(Float,      nullable=True)
    risk_label    = Column(String(32), nullable=True)

    job = relationship("CAJob", back_populates="debt")

    # Function: to_dict
    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in
                ("job_id","debt_months","debt_usd","density","interest_rate","risk_label")}


# ═══════════════════════════════════════════════════════════════════════════════
# TAB — CLOUD MATURITY (CloudReady tab)
# ═══════════════════════════════════════════════════════════════════════════════

class CACloud(Base):
    __tablename__ = "ca_cloud"

    id                       = Column(Integer,    primary_key=True, autoincrement=True)
    job_id                   = Column(String(64), ForeignKey("ca_jobs.job_id", ondelete="CASCADE"), unique=True, nullable=False)
    total                    = Column(Float,      nullable=True)
    cloud_ready_scan         = Column(Float,      nullable=True)
    boosters_score           = Column(Float,      nullable=True)
    blockers_score           = Column(Float,      nullable=True)
    stateless_design         = Column(Float,      nullable=True)
    containerization         = Column(Float,      nullable=True)
    api_surface              = Column(Float,      nullable=True)
    config_externalization   = Column(Float,      nullable=True)
    logging_observability    = Column(Float,      nullable=True)
    ci_cd_artifacts          = Column(Float,      nullable=True)
    roadblocks_count         = Column(Integer,    nullable=True)
    boosters                 = Column(Text,       nullable=True)   # JSON list
    blockers                 = Column(Text,       nullable=True)   # JSON list

    job = relationship("CAJob", back_populates="cloud")

    # Function: to_dict
    def to_dict(self) -> dict:
        d = {k: getattr(self, k) for k in (
            "job_id","total","cloud_ready_scan","boosters_score","blockers_score",
            "stateless_design","containerization","api_surface","config_externalization",
            "logging_observability","ci_cd_artifacts","roadblocks_count")}
        d["boosters"] = _dj(self.boosters)
        d["blockers"]  = _dj(self.blockers)
        return d


# ═══════════════════════════════════════════════════════════════════════════════
# TAB — SECURITY / OSS SAFETY
# ═══════════════════════════════════════════════════════════════════════════════

class CAOss(Base):
    __tablename__ = "ca_oss"

    id                  = Column(Integer,    primary_key=True, autoincrement=True)
    job_id              = Column(String(64), ForeignKey("ca_jobs.job_id", ondelete="CASCADE"), unique=True, nullable=False)
    total               = Column(Float,      nullable=True)
    vulnerable_count    = Column(Integer,    nullable=True)
    cve_critical        = Column(Integer,    nullable=True)
    cve_high            = Column(Integer,    nullable=True)
    cve_medium          = Column(Integer,    nullable=True)
    cve_low             = Column(Integer,    nullable=True)
    license_high_risk   = Column(Integer,    nullable=True)
    license_medium_risk = Column(Integer,    nullable=True)
    license_low_risk    = Column(Integer,    nullable=True)

    job  = relationship("CAJob", back_populates="oss")

    # Function: to_dict
    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in (
            "job_id","total","vulnerable_count","cve_critical","cve_high",
            "cve_medium","cve_low","license_high_risk","license_medium_risk","license_low_risk")}


class CAOssDep(Base):
    """One row per dependency detected by OSS Safety scanner."""
    __tablename__ = "ca_oss_deps"

    id             = Column(Integer,    primary_key=True, autoincrement=True)
    job_id         = Column(String(64), ForeignKey("ca_jobs.job_id", ondelete="CASCADE"), nullable=False)
    name           = Column(String(255),nullable=True)
    ecosystem      = Column(String(64), nullable=True)
    latest_version = Column(String(64), nullable=True)
    license        = Column(String(128),nullable=True)
    license_risk   = Column(String(32), nullable=True)
    vulnerable     = Column(Boolean,    nullable=True)
    vuln_count     = Column(Integer,    nullable=True)
    cve_severity   = Column(String(32), nullable=True)
    cve_ids        = Column(Text,       nullable=True)   # JSON list
    age_years      = Column(Float,      nullable=True)
    age_ok         = Column(Boolean,    nullable=True)

    job = relationship("CAJob", back_populates="oss_deps")

    # Function: to_dict
    def to_dict(self) -> dict:
        d = {k: getattr(self, k) for k in (
            "id","job_id","name","ecosystem","latest_version","license","license_risk",
            "vulnerable","vuln_count","cve_severity","age_years","age_ok")}
        d["cve_ids"] = _dj(self.cve_ids)
        return d


# ═══════════════════════════════════════════════════════════════════════════════
# TAB — BUSINESS IMPACT
# ═══════════════════════════════════════════════════════════════════════════════

class CAImpact(Base):
    __tablename__ = "ca_impact"

    id            = Column(Integer,    primary_key=True, autoincrement=True)
    job_id        = Column(String(64), ForeignKey("ca_jobs.job_id", ondelete="CASCADE"), unique=True, nullable=False)
    total         = Column(Float,      nullable=True)
    criticality   = Column(Float,      nullable=True)
    reach         = Column(Float,      nullable=True)
    revenue_risk  = Column(Float,      nullable=True)

    job = relationship("CAJob", back_populates="impact")

    # Function: to_dict
    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in
                ("job_id","total","criticality","reach","revenue_risk")}


# ═══════════════════════════════════════════════════════════════════════════════
# TAB — CO₂ REDUCTION
# ═══════════════════════════════════════════════════════════════════════════════

class CACo2(Base):
    __tablename__ = "ca_co2"

    id               = Column(Integer,    primary_key=True, autoincrement=True)
    job_id           = Column(String(64), ForeignKey("ca_jobs.job_id", ondelete="CASCADE"), unique=True, nullable=False)
    co2_tons_year    = Column(Float,      nullable=True)
    energy_kwh_year  = Column(Float,      nullable=True)
    cost_saving_usd  = Column(Float,      nullable=True)
    trees_equivalent = Column(Integer,    nullable=True)

    job = relationship("CAJob", back_populates="co2")

    # Function: to_dict
    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in
                ("job_id","co2_tons_year","energy_kwh_year","cost_saving_usd","trees_equivalent")}


# ═══════════════════════════════════════════════════════════════════════════════
# TAB — GREEN IMPACT
# ═══════════════════════════════════════════════════════════════════════════════

class CAGreen(Base):
    __tablename__ = "ca_green"

    id                = Column(Integer,    primary_key=True, autoincrement=True)
    job_id            = Column(String(64), ForeignKey("ca_jobs.job_id", ondelete="CASCADE"), unique=True, nullable=False)
    green_score       = Column(Float,      nullable=True)
    total_occurrences = Column(Integer,    nullable=True)
    total_effort_days = Column(Float,      nullable=True)
    risk_label        = Column(String(32), nullable=True)
    category_totals   = Column(Text,       nullable=True)   # JSON dict

    deficiencies = relationship("CAGreenDeficiency", back_populates="green", cascade="all, delete-orphan")
    job          = relationship("CAJob", back_populates="green")

    # Function: to_dict
    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "green_score": self.green_score,
            "total_occurrences": self.total_occurrences,
            "total_effort_days": self.total_effort_days,
            "risk_label": self.risk_label,
            "category_totals": _dj(self.category_totals),
        }


class CAGreenDeficiency(Base):
    __tablename__ = "ca_green_deficiencies"

    id            = Column(Integer,    primary_key=True, autoincrement=True)
    green_id      = Column(Integer,    ForeignKey("ca_green.id", ondelete="CASCADE"), nullable=False)
    job_id        = Column(String(64), nullable=False)
    rule_key      = Column(String(32), nullable=True)
    category      = Column(String(64), nullable=True)
    label         = Column(String(128),nullable=True)
    language      = Column(String(64), nullable=True)
    occurrences   = Column(Integer,    nullable=True)
    effort_days   = Column(Float,      nullable=True)
    affected_files= Column(Text,       nullable=True)   # JSON list

    green = relationship("CAGreen", back_populates="deficiencies")

    # Function: to_dict
    def to_dict(self) -> dict:
        d = {k: getattr(self, k) for k in
             ("id","job_id","rule_key","category","label","language","occurrences","effort_days")}
        d["affected_files"] = _dj(self.affected_files)
        return d


# ═══════════════════════════════════════════════════════════════════════════════
# TAB — ARCHITECTURE LAYERS
# ═══════════════════════════════════════════════════════════════════════════════

class CAArchitecture(Base):
    __tablename__ = "ca_architecture"

    id          = Column(Integer,    primary_key=True, autoincrement=True)
    job_id      = Column(String(64), ForeignKey("ca_jobs.job_id", ondelete="CASCADE"), unique=True, nullable=False)
    total_files = Column(Integer,    nullable=True)
    has_data    = Column(Boolean,    nullable=True)
    layer_counts= Column(Text,       nullable=True)   # JSON dict
    layer_sloc  = Column(Text,       nullable=True)   # JSON dict

    layers = relationship("CAArchLayer", back_populates="arch", cascade="all, delete-orphan")
    nodes  = relationship("CAArchNode",  back_populates="arch", cascade="all, delete-orphan")
    job    = relationship("CAJob", back_populates="architecture")

    # Function: to_dict
    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "total_files": self.total_files,
            "has_data": self.has_data,
            "layer_counts": _dj(self.layer_counts),
            "layer_sloc":   _dj(self.layer_sloc),
        }


class CAArchLayer(Base):
    __tablename__ = "ca_arch_layers"

    id           = Column(Integer,    primary_key=True, autoincrement=True)
    arch_id      = Column(Integer,    ForeignKey("ca_architecture.id", ondelete="CASCADE"), nullable=False)
    job_id       = Column(String(64), nullable=False)
    name         = Column(String(64), nullable=True)
    file_count   = Column(Integer,    nullable=True)
    sloc         = Column(Integer,    nullable=True)
    pct          = Column(Float,      nullable=True)
    technologies = Column(Text,       nullable=True)   # JSON list

    arch = relationship("CAArchitecture", back_populates="layers")

    # Function: to_dict
    def to_dict(self) -> dict:
        d = {k: getattr(self, k) for k in ("id","job_id","name","file_count","sloc","pct")}
        d["technologies"] = _dj(self.technologies)
        return d


class CAArchNode(Base):
    __tablename__ = "ca_arch_nodes"

    id       = Column(Integer,    primary_key=True, autoincrement=True)
    arch_id  = Column(Integer,    ForeignKey("ca_architecture.id", ondelete="CASCADE"), nullable=False)
    job_id   = Column(String(64), nullable=False)
    name     = Column(String(500),nullable=True)
    layer    = Column(String(64), nullable=True)
    language = Column(String(64), nullable=True)
    sloc     = Column(Integer,    nullable=True)

    arch = relationship("CAArchitecture", back_populates="nodes")

    # Function: to_dict
    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in ("id","job_id","name","layer","language","sloc")}


# ═══════════════════════════════════════════════════════════════════════════════
# TAB — CLOUD SERVICES / RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════════════════════════

class CACloudRecs(Base):
    __tablename__ = "ca_cloud_recs"

    id                = Column(Integer,    primary_key=True, autoincrement=True)
    job_id            = Column(String(64), ForeignKey("ca_jobs.job_id", ondelete="CASCADE"), unique=True, nullable=False)
    total_services    = Column(Integer,    nullable=True)
    detected_triggers = Column(Text,       nullable=True)   # JSON list
    by_category       = Column(Text,       nullable=True)   # full JSON blob

    job = relationship("CAJob", back_populates="cloud_recs")

    # Function: to_dict
    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "total_services": self.total_services,
            "detected_triggers": _dj(self.detected_triggers),
            "by_category": _dj(self.by_category),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# TAB — LANGUAGES  (one row per language per job)
# ═══════════════════════════════════════════════════════════════════════════════

class CALangReport(Base):
    __tablename__ = "ca_lang_reports"

    id               = Column(Integer,    primary_key=True, autoincrement=True)
    job_id           = Column(String(64), ForeignKey("ca_jobs.job_id", ondelete="CASCADE"), nullable=False)
    language         = Column(String(64), nullable=True)
    file_count       = Column(Integer,    nullable=True)
    total_sloc       = Column(Integer,    nullable=True)
    avg_complexity   = Column(Float,      nullable=True)
    max_complexity   = Column(Integer,    nullable=True)
    total_functions  = Column(Integer,    nullable=True)
    total_classes    = Column(Integer,    nullable=True)
    long_methods_pct = Column(Float,      nullable=True)
    deep_nesting_pct = Column(Float,      nullable=True)
    comment_ratio    = Column(Float,      nullable=True)
    bad_practices    = Column(Text,       nullable=True)   # JSON dict
    dependencies     = Column(Text,       nullable=True)   # JSON list

    files = relationship("CALangFile", back_populates="lang_report", cascade="all, delete-orphan")
    job   = relationship("CAJob", back_populates="lang_reports")

    # Function: to_dict
    def to_dict(self) -> dict:
        d = {k: getattr(self, k) for k in (
            "id","job_id","language","file_count","total_sloc","avg_complexity",
            "max_complexity","total_functions","total_classes","long_methods_pct",
            "deep_nesting_pct","comment_ratio")}
        d["bad_practices"] = _dj(self.bad_practices)
        d["dependencies"]  = _dj(self.dependencies)
        return d


class CALangFile(Base):
    """Per-file metrics — one row per source file per language per job."""
    __tablename__ = "ca_lang_files"

    id              = Column(Integer,    primary_key=True, autoincrement=True)
    lang_report_id  = Column(Integer,    ForeignKey("ca_lang_reports.id", ondelete="CASCADE"), nullable=False)
    job_id          = Column(String(64), nullable=False)
    name            = Column(String(500),nullable=True)
    sloc            = Column(Integer,    nullable=True)
    total_lines     = Column(Integer,    nullable=True)
    comment_lines   = Column(Integer,    nullable=True)
    blank_lines     = Column(Integer,    nullable=True)
    complexity      = Column(Integer,    nullable=True)
    cognitive       = Column(Integer,    nullable=True)
    functions       = Column(Integer,    nullable=True)
    classes         = Column(Integer,    nullable=True)
    long_methods    = Column(Integer,    nullable=True)
    deep_nesting    = Column(Integer,    nullable=True)
    magic_numbers   = Column(Integer,    nullable=True)
    todo_comments   = Column(Integer,    nullable=True)
    comment_ratio   = Column(Float,      nullable=True)
    error           = Column(Text,       nullable=True)

    lang_report = relationship("CALangReport", back_populates="files")

    # Function: to_dict
    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in (
            "id","job_id","name","sloc","total_lines","comment_lines","blank_lines",
            "complexity","cognitive","functions","classes","long_methods","deep_nesting",
            "magic_numbers","todo_comments","comment_ratio","error")}


# ═══════════════════════════════════════════════════════════════════════════════
# TAB — HEALTH BY TECH (one row per language per job)
# ═══════════════════════════════════════════════════════════════════════════════

class CAHealthPerLang(Base):
    __tablename__ = "ca_health_per_lang"

    id           = Column(Integer,    primary_key=True, autoincrement=True)
    job_id       = Column(String(64), ForeignKey("ca_jobs.job_id", ondelete="CASCADE"), nullable=False)
    language     = Column(String(64), nullable=True)
    health       = Column(Float,      nullable=True)
    debt_months  = Column(Float,      nullable=True)
    risk_label   = Column(String(32), nullable=True)
    extras       = Column(Text,       nullable=True)   # JSON for any extra per-lang fields

    job = relationship("CAJob", back_populates="health_per_lang")

    # Function: to_dict
    def to_dict(self) -> dict:
        d = {k: getattr(self, k) for k in
             ("id","job_id","language","health","debt_months","risk_label")}
        d["extras"] = _dj(self.extras)
        return d


# ═══════════════════════════════════════════════════════════════════════════════
# TAB — AI ANALYSIS  (parent + 5 typed sub-tables)
# ═══════════════════════════════════════════════════════════════════════════════

class CAAiAnalysis(Base):
    """
    AI Analysis parent record — one per job.
    Stores summary fields + full JSON blob for each of the 5 sub-analyses.
    Child tables store normalised rows for querying specific findings.
    """
    __tablename__ = "ca_ai_analysis"

    id               = Column(Integer,    primary_key=True, autoincrement=True)
    job_id           = Column(String(64), ForeignKey("ca_jobs.job_id", ondelete="CASCADE"), unique=True, nullable=False)
    ai_job_id        = Column(String(64), nullable=True)   # the ai_* job id
    model_used       = Column(String(128),nullable=True)
    status           = Column(String(16), nullable=True, default="pending")
    created_at       = Column(DateTime,   default=datetime.utcnow)

    # Summary strings from each sub-analysis
    debt_summary           = Column(Text, nullable=True)
    cloud_blockers_summary = Column(Text, nullable=True)
    microservices_summary  = Column(Text, nullable=True)
    business_rules_summary = Column(Text, nullable=True)
    transformation_summary = Column(Text, nullable=True)

    # Migration readiness (from cloud_blockers)
    migration_readiness  = Column(String(32), nullable=True)
    target_architecture  = Column(Text,       nullable=True)
    # Transformation maturity
    current_maturity     = Column(String(32), nullable=True)
    target_state         = Column(Text,       nullable=True)
    total_effort_months  = Column(Integer,    nullable=True)
    roi_narrative        = Column(Text,       nullable=True)
    # Business rules
    domain               = Column(String(128),nullable=True)
    key_entities         = Column(Text,       nullable=True)   # JSON list
    # Microservices
    decomposition_strategy = Column(String(64),nullable=True)
    data_store_strategy    = Column(String(64),nullable=True)
    # Tab assessments (JSON blob for the per-tab AI summaries)
    tab_assessments      = Column(Text,       nullable=True)   # JSON dict

    # 1:N children
    debt_hotspots   = relationship("CAAiDebtHotspot",     back_populates="ai_analysis", cascade="all, delete-orphan")
    cloud_blockers  = relationship("CAAiCloudBlocker",    back_populates="ai_analysis", cascade="all, delete-orphan")
    microservices   = relationship("CAAiMicroservice",    back_populates="ai_analysis", cascade="all, delete-orphan")
    business_rules  = relationship("CAAiBusinessRule",    back_populates="ai_analysis", cascade="all, delete-orphan")
    transform_paths = relationship("CAAiTransformPath",   back_populates="ai_analysis", cascade="all, delete-orphan")
    job             = relationship("CAJob", back_populates="ai_analysis")

    # Function: to_dict
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "ai_job_id": self.ai_job_id,
            "model_used": self.model_used,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "debt_summary": self.debt_summary,
            "cloud_blockers_summary": self.cloud_blockers_summary,
            "microservices_summary": self.microservices_summary,
            "business_rules_summary": self.business_rules_summary,
            "transformation_summary": self.transformation_summary,
            "migration_readiness": self.migration_readiness,
            "target_architecture": self.target_architecture,
            "current_maturity": self.current_maturity,
            "target_state": self.target_state,
            "total_effort_months": self.total_effort_months,
            "roi_narrative": self.roi_narrative,
            "domain": self.domain,
            "key_entities": _dj(self.key_entities),
            "decomposition_strategy": self.decomposition_strategy,
            "data_store_strategy": self.data_store_strategy,
            "tab_assessments": _dj(self.tab_assessments),
        }


class CAAiDebtHotspot(Base):
    """AI Tech-Debt tab — one row per hotspot file."""
    __tablename__ = "ca_ai_debt_hotspots"

    id              = Column(Integer,    primary_key=True, autoincrement=True)
    ai_analysis_id  = Column(Integer,    ForeignKey("ca_ai_analysis.id", ondelete="CASCADE"), nullable=False)
    job_id          = Column(String(64), nullable=False)
    file            = Column(String(500),nullable=True)
    priority        = Column(String(16), nullable=True)
    issue           = Column(Text,       nullable=True)
    recommendation  = Column(Text,       nullable=True)
    root_cause      = Column(Text,       nullable=True)
    impact          = Column(Text,       nullable=True)
    effort_days     = Column(Float,      nullable=True)
    debt_category   = Column(String(64), nullable=True)
    metrics         = Column(Text,       nullable=True)   # JSON dict

    ai_analysis = relationship("CAAiAnalysis", back_populates="debt_hotspots")

    # Function: to_dict
    def to_dict(self) -> dict:
        d = {k: getattr(self, k) for k in (
            "id","job_id","file","priority","issue","recommendation",
            "root_cause","impact","effort_days","debt_category")}
        d["metrics"] = _dj(self.metrics)
        return d


class CAAiCloudBlocker(Base):
    """AI CloudReady tab — one row per cloud migration blocker."""
    __tablename__ = "ca_ai_cloud_blockers"

    id             = Column(Integer,    primary_key=True, autoincrement=True)
    ai_analysis_id = Column(Integer,    ForeignKey("ca_ai_analysis.id", ondelete="CASCADE"), nullable=False)
    job_id         = Column(String(64), nullable=False)
    title          = Column(String(255),nullable=True)
    type           = Column(String(64), nullable=True)
    severity       = Column(String(16), nullable=True)
    description    = Column(Text,       nullable=True)
    fix_suggestion = Column(Text,       nullable=True)
    remediation    = Column(Text,       nullable=True)
    effort_days    = Column(Float,      nullable=True)

    ai_analysis = relationship("CAAiAnalysis", back_populates="cloud_blockers")

    # Function: to_dict
    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in (
            "id","job_id","title","type","severity","description",
            "fix_suggestion","remediation","effort_days")}


class CAAiMicroservice(Base):
    """AI Microservices tab — one row per proposed microservice."""
    __tablename__ = "ca_ai_microservices"

    id               = Column(Integer,    primary_key=True, autoincrement=True)
    ai_analysis_id   = Column(Integer,    ForeignKey("ca_ai_analysis.id", ondelete="CASCADE"), nullable=False)
    job_id           = Column(String(64), nullable=False)
    name             = Column(String(128),nullable=True)
    responsibility   = Column(Text,       nullable=True)
    api_type         = Column(String(32), nullable=True)
    estimated_kloc   = Column(Float,      nullable=True)
    dependencies     = Column(Text,       nullable=True)   # JSON list
    migration_order  = Column(Integer,    nullable=True)

    ai_analysis = relationship("CAAiAnalysis", back_populates="microservices")

    # Function: to_dict
    def to_dict(self) -> dict:
        d = {k: getattr(self, k) for k in (
            "id","job_id","name","responsibility","api_type","estimated_kloc","migration_order")}
        d["dependencies"] = _dj(self.dependencies)
        return d


class CAAiBusinessRule(Base):
    """AI Business Rules tab — one row per extracted rule."""
    __tablename__ = "ca_ai_business_rules"

    id             = Column(Integer,    primary_key=True, autoincrement=True)
    ai_analysis_id = Column(Integer,    ForeignKey("ca_ai_analysis.id", ondelete="CASCADE"), nullable=False)
    job_id         = Column(String(64), nullable=False)
    title          = Column(String(255),nullable=True)
    type           = Column(String(64), nullable=True)
    description    = Column(Text,       nullable=True)
    confidence     = Column(String(16), nullable=True)
    source_file    = Column(String(500),nullable=True)

    ai_analysis = relationship("CAAiAnalysis", back_populates="business_rules")

    # Function: to_dict
    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in (
            "id","job_id","title","type","description","confidence","source_file")}


class CAAiTransformPath(Base):
    """AI Transformation tab — one row per transformation path."""
    __tablename__ = "ca_ai_transform_paths"

    id             = Column(Integer,    primary_key=True, autoincrement=True)
    ai_analysis_id = Column(Integer,    ForeignKey("ca_ai_analysis.id", ondelete="CASCADE"), nullable=False)
    job_id         = Column(String(64), nullable=False)
    current        = Column(String(128),nullable=True)
    recommended    = Column(String(128),nullable=True)
    category       = Column(String(64), nullable=True)
    value_score    = Column(Float,      nullable=True)
    risk           = Column(String(16), nullable=True)
    steps          = Column(Text,       nullable=True)   # JSON list

    ai_analysis = relationship("CAAiAnalysis", back_populates="transform_paths")

    # Function: to_dict
    def to_dict(self) -> dict:
        d = {k: getattr(self, k) for k in (
            "id","job_id","current","recommended","category","value_score","risk")}
        d["steps"] = _dj(self.steps)
        return d
