# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Relational storage for Technical Assessment workbook inputs.
# Date: 2026-01-27
# ---------------------------------------------------------------------------
"""Relational storage for Technical Assessment workbook inputs."""
from datetime import datetime
from app import db


class TechnicalAssessmentImport(db.Model):
    __tablename__ = "technical_assessment_imports"
    id = db.Column(db.Integer, primary_key=True)
    dataset_type = db.Column(db.String(32), nullable=False, index=True)
    source_filename = db.Column(db.String(500), nullable=False)
    source_sheet = db.Column(db.String(128), nullable=False)
    checksum_sha256 = db.Column(db.String(64), nullable=False, index=True)
    row_count = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(32), nullable=False, default="committed")
    imported_by = db.Column(db.String(255))
    imported_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Function: to_dict
    def to_dict(self):
        return {
            "id": self.id, "dataset_type": self.dataset_type,
            "source_filename": self.source_filename, "source_sheet": self.source_sheet,
            "checksum_sha256": self.checksum_sha256, "row_count": self.row_count,
            "status": self.status, "imported_by": self.imported_by,
            "imported_at": self.imported_at.isoformat() if self.imported_at else None,
        }


class BusinessValidation(db.Model):
    __tablename__ = "technical_assessment_business_validations"
    id = db.Column(db.Integer, primary_key=True)
    import_id = db.Column(db.Integer, db.ForeignKey("technical_assessment_imports.id", ondelete="CASCADE"), nullable=False, index=True)
    row_number = db.Column(db.Integer, nullable=False)
    application_number = db.Column(db.String(64), nullable=False, index=True)
    name = db.Column(db.String(500), nullable=False)
    categorization = db.Column(db.String(500), index=True)
    application_family = db.Column(db.String(500))
    business_owner = db.Column(db.String(500))
    department = db.Column(db.String(255))
    olb_level_2 = db.Column(db.String(255))
    it_application_owner = db.Column(db.String(500))
    gd_segments = db.Column(db.String(255))
    department_2 = db.Column(db.String(255))
    olb_level_23 = db.Column(db.String(255))
    architecture_type = db.Column(db.String(255))
    platform_host = db.Column(db.String(500))
    application_type = db.Column(db.String(500))
    install_type = db.Column(db.String(255))
    capabilities = db.Column(db.Text)
    inconsistency = db.Column(db.Boolean, nullable=False, default=False)
    rationale = db.Column(db.Text)
    __table_args__ = (db.UniqueConstraint("import_id", "application_number", name="uq_business_validation_import_app"),)

    # Function: to_dict
    def to_dict(self):
        return {
            "id": self.id, "row_number": self.row_number,
            "application_number": self.application_number, "name": self.name,
            "categorization": self.categorization, "application_family": self.application_family,
            "business_owner": self.business_owner, "department": self.department,
            "olb_level_2": self.olb_level_2, "it_application_owner": self.it_application_owner,
            "gd_segments": self.gd_segments, "department_2": self.department_2,
            "olb_level_23": self.olb_level_23, "architecture_type": self.architecture_type,
            "platform_host": self.platform_host, "application_type": self.application_type,
            "install_type": self.install_type, "capabilities": self.capabilities,
            "inconsistency": self.inconsistency, "rationale": self.rationale,
        }


class WaveInput(db.Model):
    __tablename__ = "technical_assessment_wave_inputs"
    id = db.Column(db.Integer, primary_key=True)
    import_id = db.Column(db.Integer, db.ForeignKey("technical_assessment_imports.id", ondelete="CASCADE"), nullable=False, index=True)
    row_number = db.Column(db.Integer, nullable=False)
    app_id = db.Column(db.String(64), nullable=False, index=True)
    application_name = db.Column(db.String(500), nullable=False)
    topic = db.Column(db.String(500), index=True)
    business_capability = db.Column(db.Text)
    # The real Wave_Plan_Input template has two columns both literally titled
    # "Migration Type" (col E and col J) — migration_approach is the first
    # (col E); migration_type is the second, canonical one whose values match
    # the Reference_Lists sheet exactly (Data Migration Only / Functional
    # Migration / Modernization).
    migration_approach = db.Column(db.String(100))
    capability_confirmed = db.Column(db.Boolean)
    business_rationale = db.Column(db.Text)
    disposition = db.Column(db.String(100))
    target_platform = db.Column(db.String(500))
    migration_type = db.Column(db.String(100))
    tshirt_size = db.Column(db.String(16))
    complexity = db.Column(db.String(50))
    table_count = db.Column(db.Integer)
    data_volume_records = db.Column(db.BigInteger)
    change_impact = db.Column(db.String(50))
    risk = db.Column(db.String(50))
    quick_win = db.Column(db.Boolean)
    business_criticality = db.Column(db.String(50))
    department = db.Column(db.String(255))
    business_owner = db.Column(db.String(500))
    install_type = db.Column(db.String(255))
    site_region = db.Column(db.String(500))
    dependencies = db.Column(db.Text)
    dependency_readiness = db.Column(db.String(500))
    earliest_start = db.Column(db.Date)
    latest_finish = db.Column(db.Date)
    regulatory_hold = db.Column(db.Boolean)
    assessment_effort_hours = db.Column(db.Numeric(14, 2))
    migration_effort_hours = db.Column(db.Numeric(14, 2))
    total_effort_hours = db.Column(db.Numeric(14, 2))
    wave_eligibility_score = db.Column(db.Numeric(10, 2))
    proposed_wave = db.Column(db.String(50))
    sme_owner = db.Column(db.String(500))
    workshop_date = db.Column(db.Date)
    signoff_status = db.Column(db.String(100))
    comments = db.Column(db.Text)
    __table_args__ = (db.UniqueConstraint("import_id", "app_id", name="uq_wave_input_import_app"),)

    # Function: to_dict
    def to_dict(self):
        result = {column.name: getattr(self, column.name) for column in self.__table__.columns if column.name != "import_id"}
        for key in ("earliest_start", "latest_finish", "workshop_date"):
            if result.get(key):
                result[key] = result[key].isoformat()
        for key in ("assessment_effort_hours", "migration_effort_hours", "total_effort_hours", "wave_eligibility_score"):
            if result.get(key) is not None:
                result[key] = float(result[key])
        return result

