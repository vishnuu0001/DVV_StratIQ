# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Validated, transactional imports for Technical Assessment workbooks.
# Date: 2025-08-07
# ---------------------------------------------------------------------------
"""Validated, transactional imports for Technical Assessment workbooks."""
import hashlib
import json
import math
import re
from datetime import date, datetime
from pathlib import Path
from openpyxl import load_workbook
from sqlalchemy import desc
from app import db
from app.models.technical_assessment import (
    BusinessValidation,
    TechnicalAssessmentImport,
    TechnicalEvaluationCategorizeMeta,
    TechnicalEvaluationCategorizeRow,
    WaveInput,
)
from app.services.ollama_service import OllamaService

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


# Function: _is_yellow_cell
def _is_yellow_cell(cell):
    fill = getattr(cell, "fill", None)
    if not fill or getattr(fill, "fill_type", None) in (None, "none"):
        return False
    color = getattr(fill, "fgColor", None) or getattr(fill, "start_color", None)
    if not color:
        return False
    rgb = (getattr(color, "rgb", None) or "").upper()
    if rgb and any(rgb.endswith(token) for token in ("FFFF00", "FFF200", "FFEB3B", "FFEA00")):
        return True
    index = (getattr(color, "index", None) or "").upper()
    return index in {"FFFFFF00", "FFFF00"}


# Function: _detect_header_row
def _detect_header_row(sheet):
    max_scan = min(sheet.max_row, 15)
    for row_idx in range(1, max_scan + 1):
        values = [
            _norm_header_key(_clean(sheet.cell(row=row_idx, column=col).value))
            for col in range(1, sheet.max_column + 1)
        ]
        has_topic = any(value in {"topic", "categorization", "category"} for value in values)
        has_product = any(
            value in {"product", "applicationname", "name"}
            or value.startswith("product")
            for value in values
        )
        if has_topic and has_product:
            return row_idx
    return 1


# Function: _market_enrichment_default
def _market_enrichment_default(highlighted_headers):
    return {header: "Unknown" for header in highlighted_headers}


# Function: _sanitize_market_payload
def _sanitize_market_payload(payload, highlighted_headers):
    result = _market_enrichment_default(highlighted_headers)
    if not isinstance(payload, dict):
        return result
    for header in highlighted_headers:
        value = payload.get(header)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            result[header] = text[:500]
    return result


# Function: _norm_key
def _norm_key(value):
    if value is None:
        return ""
    text = str(value).strip().casefold()
    return " ".join(text.split())


# Function: _norm_header_key
def _norm_header_key(value):
    if value is None:
        return ""
    text = str(value).strip().casefold()
    text = re.sub(r"[^a-z0-9]+", "", text)
    return text


# Function: _pick_header_by_alias
def _pick_header_by_alias(headers, aliases, startswith=False):
    normalized = [(_norm_header_key(header), header) for header in headers]
    for key, header in normalized:
        if key in aliases:
            return header
    if startswith:
        for key, header in normalized:
            if any(key.startswith(alias) for alias in aliases):
                return header
    return None


# Function: _parse_categorize_sheet
def _parse_categorize_sheet(sheet):
    topic_aliases = {
        "topic",
        "categorization",
        "category",
        "topiccategorization",
    }
    product_aliases = {
        "product",
        "applicationname",
        "application",
        "businessapplication",
        "businessapplications",
        "appname",
        "name",
    }
    size_aliases = {
        "size",
        "tshirtsize",
        "complexity",
    }

    header_row_idx = _detect_header_row(sheet)
    headers = []
    highlighted_headers = []
    for col_idx in range(1, sheet.max_column + 1):
        cell = sheet.cell(row=header_row_idx, column=col_idx)
        header = str(_clean(cell.value) or "").strip()
        if not header:
            header = f"Column {col_idx}"
        headers.append(header)
        if _is_yellow_cell(cell):
            highlighted_headers.append(header)

    key_map = _dedupe_headers(headers)
    topic_col = _pick_header_by_alias(
        key_map,
        topic_aliases,
        startswith=True,
    ) or (key_map[0] if key_map else "Topic")

    product_col = _pick_header_by_alias(
        key_map,
        product_aliases,
        startswith=True,
    )

    size_col = _pick_header_by_alias(
        key_map,
        size_aliases,
        startswith=True,
    )

    if not highlighted_headers:
        highlighted_headers = [
            header for header in key_map
            if header not in {topic_col, product_col, size_col}
            and any(token in header.casefold() for token in ("compliance", "dynamic", "alarm", "market", "cots", "capabilities"))
        ]

    rows = []
    last_topic = ""
    for row_idx in range(header_row_idx + 1, sheet.max_row + 1):
        values = [_clean(sheet.cell(row=row_idx, column=col).value) for col in range(1, sheet.max_column + 1)]
        if not any(value not in (None, "") for value in values):
            continue
        payload = {key: values[i] for i, key in enumerate(key_map)}
        raw_topic = str(payload.get(topic_col) or "").strip()
        topic = raw_topic or last_topic
        product = str(payload.get(product_col) or "").strip() if product_col else ""
        size = str(payload.get(size_col) or "").strip() if size_col else ""
        if raw_topic:
            last_topic = raw_topic
        if not topic or not product:
            continue
        rows.append((row_idx, topic, product, size or None, payload))

    return {
        "sheet": sheet.title,
        "header_row_idx": header_row_idx,
        "key_map": key_map,
        "highlighted_headers": highlighted_headers,
        "topic_col": topic_col,
        "product_col": product_col,
        "size_col": size_col,
        "rows": rows,
    }


# Function: _wave_size_lookup
def _wave_size_lookup():
    """Build product/application-name -> size lookup from latest Wave Inputs."""
    wave_import = latest_import("wave_inputs")
    if not wave_import:
        return {}

    lookup = {}
    rows = WaveInput.query.filter_by(import_id=wave_import.id).all()
    for row in rows:
        size_value = row.tshirt_size or row.complexity
        if not size_value:
            continue
        app_name_key = _norm_key(row.application_name)
        app_id_key = _norm_key(row.app_id)
        if app_name_key and app_name_key not in lookup:
            lookup[app_name_key] = str(size_value)
        if app_id_key and app_id_key not in lookup:
            lookup[app_id_key] = str(size_value)
    return lookup


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
        if dataset_type == "technical_evaluation_categorize":
            TechnicalEvaluationCategorizeMeta.query.filter_by(import_id=imp.id).delete(synchronize_session=False)
        db.session.delete(imp)
    if existing_imports:
        db.session.flush()


# Function: clear_dataset
def clear_dataset(dataset_type):
    """Delete all imported data (and import log rows) for one dataset type."""
    child_model = {
        "business_validations": BusinessValidation,
        "wave_inputs": WaveInput,
        "technical_evaluation_categorize": TechnicalEvaluationCategorizeRow,
    }.get(dataset_type)
    if child_model is None:
        raise ValueError(f"Unsupported dataset type: {dataset_type}")
    imports = TechnicalAssessmentImport.query.filter_by(dataset_type=dataset_type).all()
    cleared_rows = 0
    for imp in imports:
        cleared_rows += child_model.query.filter_by(import_id=imp.id).delete(synchronize_session=False)
        if dataset_type == "technical_evaluation_categorize":
            TechnicalEvaluationCategorizeMeta.query.filter_by(import_id=imp.id).delete(synchronize_session=False)
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


# Function: import_technical_evaluation_categorize
def import_technical_evaluation_categorize(path, source_filename, imported_by):
    workbook = load_workbook(path, read_only=False, data_only=True)
    try:
        candidates = []
        missing_product = []
        for sheet in workbook.worksheets:
            parsed = _parse_categorize_sheet(sheet)
            if parsed["product_col"]:
                candidates.append(parsed)
            else:
                missing_product.append(parsed)

        if not candidates:
            diagnostics = []
            for parsed in missing_product[:4]:
                sample_headers = ", ".join(parsed["key_map"][:8])
                diagnostics.append(f"{parsed['sheet']}: {sample_headers}")
            detail = "; ".join(diagnostics) if diagnostics else "no readable worksheets"
            raise ValueError(
                "Workbook validation failed: Product column is required "
                f"(checked sheets: {detail})"
            )

        best = max(candidates, key=lambda item: len(item["rows"]))
        if not best["rows"]:
            raise ValueError(
                "Workbook validation failed: no Topic/Product rows found "
                f"(detected sheet: {best['sheet']})"
            )

        key_map = best["key_map"]
        highlighted_headers = best["highlighted_headers"]
        topic_col = best["topic_col"]
        product_col = best["product_col"]
        size_col = best["size_col"]
        rows = best["rows"]

        checksum = _checksum(path)
        _replace_dataset("technical_evaluation_categorize", checksum, TechnicalEvaluationCategorizeRow)

        record = TechnicalAssessmentImport(
            dataset_type="technical_evaluation_categorize",
            source_filename=source_filename,
            source_sheet=best["sheet"],
            checksum_sha256=checksum,
            row_count=len(rows),
            imported_by=imported_by,
        )
        db.session.add(record)
        db.session.flush()

        db.session.add(TechnicalEvaluationCategorizeMeta(
            import_id=record.id,
            headers_json=json.dumps(key_map, ensure_ascii=False),
            highlighted_headers_json=json.dumps(highlighted_headers, ensure_ascii=False),
            topic_column=topic_col,
            product_column=product_col,
            size_column=size_col,
        ))

        for row_number, topic, product, size, payload in rows:
            db.session.add(TechnicalEvaluationCategorizeRow(
                import_id=record.id,
                row_number=row_number,
                topic=topic,
                product=product,
                size=size,
                row_payload_json=json.dumps(payload, ensure_ascii=False, default=str),
                enrichment_payload_json=json.dumps(_market_enrichment_default(highlighted_headers), ensure_ascii=False),
            ))

        db.session.commit()
        return record
    finally:
        workbook.close()


# Function: get_technical_evaluation_categorize_dashboard
def get_technical_evaluation_categorize_dashboard(topic=None, search=""):
    import_record = latest_import("technical_evaluation_categorize")
    if not import_record:
        return {
            "items": [],
            "topics": [],
            "total": 0,
            "import": None,
            "highlighted_headers": [],
            "headers": [],
            "selected_topic": topic,
        }

    meta = TechnicalEvaluationCategorizeMeta.query.filter_by(import_id=import_record.id).first()
    meta_data = meta.to_dict() if meta else {"headers": [], "highlighted_headers": []}

    query = TechnicalEvaluationCategorizeRow.query.filter_by(import_id=import_record.id)
    if topic:
        query = query.filter(TechnicalEvaluationCategorizeRow.topic == topic)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(db.or_(
            TechnicalEvaluationCategorizeRow.topic.ilike(pattern),
            TechnicalEvaluationCategorizeRow.product.ilike(pattern),
        ))
    rows = query.order_by(TechnicalEvaluationCategorizeRow.row_number).all()
    size_lookup = _wave_size_lookup()

    topics = [
        value[0]
        for value in TechnicalEvaluationCategorizeRow.query
        .with_entities(TechnicalEvaluationCategorizeRow.topic)
        .filter_by(import_id=import_record.id)
        .distinct()
        .order_by(TechnicalEvaluationCategorizeRow.topic)
        .all()
    ]

    return {
        "items": [
            {
                **row.to_dict(),
                "size": size_lookup.get(_norm_key(row.product)) or row.size,
            }
            for row in rows
        ],
        "topics": topics,
        "total": len(rows),
        "import": import_record.to_dict(),
        "headers": meta_data.get("headers", []),
        "highlighted_headers": meta_data.get("highlighted_headers", []),
        "selected_topic": topic,
        "meta": meta_data,
    }


# Function: enrich_technical_evaluation_categorize_topic
def enrich_technical_evaluation_categorize_topic(topic):
    selected_topic = (topic or "").strip()
    if not selected_topic:
        raise ValueError("Topic is required")

    import_record = latest_import("technical_evaluation_categorize")
    if not import_record:
        raise ValueError("No categorized workbook import found")

    meta = TechnicalEvaluationCategorizeMeta.query.filter_by(import_id=import_record.id).first()
    if not meta:
        raise ValueError("Categorize metadata is unavailable for the latest import")
    meta_data = meta.to_dict()
    highlighted_headers = meta_data.get("highlighted_headers", [])
    if not highlighted_headers:
        raise ValueError("No highlighted capability columns found in the uploaded workbook")

    rows = TechnicalEvaluationCategorizeRow.query.filter_by(
        import_id=import_record.id,
        topic=selected_topic,
    ).order_by(TechnicalEvaluationCategorizeRow.row_number).all()
    if not rows:
        raise ValueError(f"No products found for topic '{selected_topic}'")

    size_lookup = _wave_size_lookup()
    products = []
    for row in rows:
        data = row.to_dict()
        resolved_size = size_lookup.get(_norm_key(row.product)) or row.size
        products.append({
            "id": row.id,
            "product": row.product,
            "size": resolved_size,
            "context": data.get("row_payload", {}),
        })

    enrichment = OllamaService.generate_market_product_enrichment(
        selected_topic,
        products,
        highlighted_headers,
    )

    now = datetime.utcnow()
    for row in rows:
        payload = _sanitize_market_payload(enrichment.get(str(row.id)) or {}, highlighted_headers)
        row.enrichment_payload_json = json.dumps(payload, ensure_ascii=False)
        row.market_checked_at = now
    db.session.commit()

    return get_technical_evaluation_categorize_dashboard(topic=selected_topic)


# Function: latest_import
def latest_import(dataset_type):
    return TechnicalAssessmentImport.query.filter_by(dataset_type=dataset_type).order_by(
        desc(TechnicalAssessmentImport.imported_at), desc(TechnicalAssessmentImport.id)).first()
