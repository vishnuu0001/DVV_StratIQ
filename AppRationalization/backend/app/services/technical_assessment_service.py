# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Validated, transactional imports for Technical Assessment workbooks.
# Date: 2025-08-07
# ---------------------------------------------------------------------------
"""Validated, transactional imports for Technical Assessment workbooks."""
import hashlib
import math
from datetime import date, datetime
from pathlib import Path
from openpyxl import load_workbook
from sqlalchemy import desc
from app import db
from app.models.technical_assessment import BusinessValidation, TechnicalAssessmentImport, WaveInput

BUSINESS_SHEET = "Business_Applications"
WAVE_SHEET = "Wave_Plan_Input"
BUSINESS_HEADERS = [
    "Number", "Name", "Categorization", "Application family", "Business owner", "Department",
    "OLB Level 2", "IT Application owner", "GD Segments", "Department2", "OLB Level 23",
    "Architecture type", "Platform Host", "Application type", "Install type",
    "Capabilities", "Inconsistency", "Rationale",
]
WAVE_HEADERS = [
    "App ID", "Application Name", "Topic (Categorization)", "Business Capability (from source col P)",
    "Migration Type",  # first of two same-labelled columns in the real template — see _dedupe_headers
    "Capability Confirmed?", "Business Rationale", "Disposition", "Target Platform", "Migration Type",
    "T-Shirt Size", "Complexity", "# Tables", "Data Volume (records)", "Change Impact", "Risk",
    "Quick Win", "Business Criticality", "Department", "Business Owner", "Install Type", "Site / Region",
    "Dependencies (App IDs)", "Dependency Readiness", "Earliest Start", "Latest Finish", "Regulatory Hold?",
    "Assessment Effort (hrs)", "Migration Effort (hrs)", "Total Effort (hrs)", "Wave Eligibility Score",
    "Proposed Wave", "SME / Owner", "Workshop Date", "Sign-off Status", "Comments",
]


# Function: _clean
def _clean(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return value.strip() if isinstance(value, str) else value


# Function: _bool
def _bool(value):
    value = _clean(value)
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"yes", "true", "1", "x"}


# Function: _int
def _int(value):
    value = _clean(value)
    if value in (None, "") or (isinstance(value, str) and value.startswith("=")):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


# Function: _number
def _number(value):
    value = _clean(value)
    if value in (None, "") or (isinstance(value, str) and value.startswith("=")):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# Function: _date
def _date(value):
    value = _clean(value)
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value:
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


# Function: _checksum
def _checksum(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


# Function: _dedupe_headers
def _dedupe_headers(headers):
    """Disambiguate repeated header names (e.g. the real Wave_Plan_Input
    template has two columns both literally titled "Migration Type") into
    unique dict keys — "Name", "Name #2", "Name #3", ... — so a naive
    ``dict(zip(headers, values))`` can't silently drop a duplicate column's
    values by overwriting them with the next same-named column's values.
    The *equality* check against expected_headers still uses the raw,
    undeduplicated list, since that's what's literally in the file.
    """
    seen = {}
    keys = []
    for header in headers:
        seen[header] = seen.get(header, 0) + 1
        keys.append(header if seen[header] == 1 else f"{header} #{seen[header]}")
    return keys


# Function: _read
def _read(path, sheet, expected_headers):
    # data_only=True: several columns (effort hours, wave eligibility score)
    # are Excel formulas in the real template — read the cached calculated
    # value, not the formula text, or every numeric converter downstream
    # would discard them as unparseable and silently null the column.
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        if sheet not in workbook.sheetnames:
            raise ValueError(f"Required worksheet '{sheet}' was not found")
        worksheet = workbook[sheet]
        headers = [_clean(cell.value) for cell in next(worksheet.iter_rows(min_row=1, max_row=1))]
        if headers != expected_headers:
            missing = [header for header in expected_headers if header not in headers]
            raise ValueError(f"Unexpected {sheet} schema. Missing columns: {missing}")
        dict_keys = _dedupe_headers(headers)
        rows = []
        for row_number, values in enumerate(worksheet.iter_rows(min_row=2, values_only=True), 2):
            if any(_clean(value) is not None for value in values):
                rows.append((row_number, dict(zip(dict_keys, values))))
        return rows
    finally:
        workbook.close()


# Function: _replace_dataset
def _replace_dataset(dataset_type, checksum, child_model):
    """Reject an exact re-upload of a file already loaded for this dataset;
    otherwise clear every previous import of this dataset type so only the
    newly uploaded file's data exists afterward — imports never accumulate
    across re-uploads, keeping the table's contents unique to the current file.
    """
    existing_imports = TechnicalAssessmentImport.query.filter_by(dataset_type=dataset_type).all()
    if any(imp.checksum_sha256 == checksum for imp in existing_imports):
        raise ValueError("This exact file has already been imported — no changes detected.")
    for imp in existing_imports:
        child_model.query.filter_by(import_id=imp.id).delete(synchronize_session=False)
        db.session.delete(imp)
    if existing_imports:
        db.session.flush()


# Function: clear_dataset
def clear_dataset(dataset_type):
    """Delete all imported data (and import log rows) for one dataset type."""
    child_model = BusinessValidation if dataset_type == "business_validations" else WaveInput
    imports = TechnicalAssessmentImport.query.filter_by(dataset_type=dataset_type).all()
    cleared_rows = 0
    for imp in imports:
        cleared_rows += child_model.query.filter_by(import_id=imp.id).delete(synchronize_session=False)
        db.session.delete(imp)
    if dataset_type == "wave_inputs":
        # Derived schedules can't outlive their source Wave Inputs.
        from app.models.wave_schedule import WaveSchedule, WaveScheduleWave, WaveScheduleTask, WaveScheduleApp
        WaveScheduleApp.query.delete(synchronize_session=False)
        WaveScheduleTask.query.delete(synchronize_session=False)
        WaveScheduleWave.query.delete(synchronize_session=False)
        WaveSchedule.query.delete(synchronize_session=False)
    db.session.commit()
    return cleared_rows


# Function: import_business_validations
def import_business_validations(path, source_filename, imported_by):
    rows = _read(path, BUSINESS_SHEET, BUSINESS_HEADERS)
    errors, seen = [], set()
    for row_number, row in rows:
        app_id = str(_clean(row["Number"]) or "")
        if not app_id:
            errors.append({"row": row_number, "message": "Number is required"})
        elif app_id in seen:
            errors.append({"row": row_number, "message": f"Duplicate application Number: {app_id}"})
        seen.add(app_id)
    if errors:
        raise ValueError(f"Workbook validation failed: {errors[:10]}")
    checksum = _checksum(path)
    _replace_dataset("business_validations", checksum, BusinessValidation)
    record = TechnicalAssessmentImport(
        dataset_type="business_validations", source_filename=source_filename,
        source_sheet=BUSINESS_SHEET, checksum_sha256=checksum,
        row_count=len(rows), imported_by=imported_by,
    )
    db.session.add(record)
    db.session.flush()
    for row_number, row in rows:
        db.session.add(BusinessValidation(
            import_id=record.id, row_number=row_number, application_number=str(_clean(row["Number"])),
            name=str(_clean(row["Name"]) or ""), categorization=_clean(row["Categorization"]),
            application_family=_clean(row["Application family"]), business_owner=_clean(row["Business owner"]),
            department=_clean(row["Department"]), olb_level_2=_clean(row["OLB Level 2"]),
            it_application_owner=_clean(row["IT Application owner"]), gd_segments=_clean(row["GD Segments"]),
            department_2=_clean(row["Department2"]), olb_level_23=_clean(row["OLB Level 23"]),
            architecture_type=_clean(row["Architecture type"]), platform_host=_clean(row["Platform Host"]),
            application_type=_clean(row["Application type"]), install_type=_clean(row["Install type"]),
            capabilities=_clean(row["Capabilities"]), inconsistency=bool(_bool(row["Inconsistency"])),
            rationale=_clean(row["Rationale"]),
        ))
    db.session.commit()
    return record


# Function: import_wave_inputs
def import_wave_inputs(path, source_filename, imported_by):
    rows = _read(path, WAVE_SHEET, WAVE_HEADERS)
    # The workbook's documented example is never operational data.
    rows = [(number, row) for number, row in rows if str(_clean(row["App ID"]) or "") != "APM0000000"]
    errors, seen = [], set()
    for row_number, row in rows:
        app_id = str(_clean(row["App ID"]) or "")
        if not app_id:
            errors.append({"row": row_number, "message": "App ID is required"})
        elif app_id in seen:
            errors.append({"row": row_number, "message": f"Duplicate App ID: {app_id}"})
        seen.add(app_id)
    if errors:
        raise ValueError(f"Workbook validation failed: {errors[:10]}")
    checksum = _checksum(path)
    _replace_dataset("wave_inputs", checksum, WaveInput)
    record = TechnicalAssessmentImport(
        dataset_type="wave_inputs", source_filename=source_filename, source_sheet=WAVE_SHEET,
        checksum_sha256=checksum, row_count=len(rows), imported_by=imported_by,
    )
    db.session.add(record)
    db.session.flush()
    fields = [
        ("topic", "Topic (Categorization)", _clean), ("business_capability", "Business Capability (from source col P)", _clean),
        ("capability_confirmed", "Capability Confirmed?", _bool), ("business_rationale", "Business Rationale", _clean),
        ("disposition", "Disposition", _clean), ("target_platform", "Target Platform", _clean),
        # Two columns are both literally titled "Migration Type" in the real template (col E, col J).
        # _dedupe_headers renames the first occurrence's dict key unchanged and the second to "... #2".
        ("migration_approach", "Migration Type", _clean), ("migration_type", "Migration Type #2", _clean),
        ("tshirt_size", "T-Shirt Size", _clean),
        ("complexity", "Complexity", _clean), ("table_count", "# Tables", _int),
        ("data_volume_records", "Data Volume (records)", _int), ("change_impact", "Change Impact", _clean),
        ("risk", "Risk", _clean), ("quick_win", "Quick Win", _bool),
        ("business_criticality", "Business Criticality", _clean), ("department", "Department", _clean),
        ("business_owner", "Business Owner", _clean), ("install_type", "Install Type", _clean),
        ("site_region", "Site / Region", _clean), ("dependencies", "Dependencies (App IDs)", _clean),
        ("dependency_readiness", "Dependency Readiness", _clean), ("earliest_start", "Earliest Start", _date),
        ("latest_finish", "Latest Finish", _date), ("regulatory_hold", "Regulatory Hold?", _bool),
        ("assessment_effort_hours", "Assessment Effort (hrs)", _number),
        ("migration_effort_hours", "Migration Effort (hrs)", _number), ("total_effort_hours", "Total Effort (hrs)", _number),
        ("wave_eligibility_score", "Wave Eligibility Score", _number), ("proposed_wave", "Proposed Wave", _clean),
        ("sme_owner", "SME / Owner", _clean), ("workshop_date", "Workshop Date", _date),
        ("signoff_status", "Sign-off Status", _clean), ("comments", "Comments", _clean),
    ]
    for row_number, row in rows:
        values = {field: converter(row[header]) for field, header, converter in fields}
        db.session.add(WaveInput(import_id=record.id, row_number=row_number,
                                 app_id=str(_clean(row["App ID"])), application_name=str(_clean(row["Application Name"]) or ""),
                                 **values))
    db.session.commit()

    # Wave Planning is calculated on demand (the "Predict Wave Planning"
    # button), not eagerly here — every calculation now mandatorily calls
    # Ollama, so eagerly recomputing all ~20 topics on every import would
    # block the upload response for many minutes. The next "Predict Wave
    # Planning" click always recalculates fresh against this import anyway.

    return record


# Function: latest_import
def latest_import(dataset_type):
    return TechnicalAssessmentImport.query.filter_by(dataset_type=dataset_type).order_by(
        desc(TechnicalAssessmentImport.imported_at), desc(TechnicalAssessmentImport.id)).first()
