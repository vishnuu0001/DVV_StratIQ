# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Technical Assessment upload and data APIs.
# Date: 2025-09-06
# ---------------------------------------------------------------------------
"""Technical Assessment upload and data APIs."""
import tempfile
from pathlib import Path
from flask import Blueprint, current_app, g, jsonify, request
from werkzeug.utils import secure_filename
from app import db
from app.models.technical_assessment import (
    BusinessValidation,
    TechnicalAssessmentImport,
    TechnicalEvaluationCategorizeRow,
    WaveInput,
)
from app.services.technical_assessment_service import (
    clear_dataset,
    enrich_technical_evaluation_categorize_topic,
    get_technical_evaluation_categorize_dashboard,
    import_business_validations,
    import_technical_evaluation_categorize,
    import_wave_inputs,
    latest_import,
)

technical_assessment_bp = Blueprint(
    "technical_assessment", __name__, url_prefix="/api/technical-assessment"
)
DATASET_KINDS = {"business-validations", "wave-inputs", "technical-evaluation-categorize"}

DATASET_MAP = {
    "business-validations": {
        "dataset_type": "business_validations",
        "importer": import_business_validations,
        "model": BusinessValidation,
    },
    "wave-inputs": {
        "dataset_type": "wave_inputs",
        "importer": import_wave_inputs,
        "model": WaveInput,
    },
    "technical-evaluation-categorize": {
        "dataset_type": "technical_evaluation_categorize",
        "importer": import_technical_evaluation_categorize,
        "model": TechnicalEvaluationCategorizeRow,
    },
}


# Function: _user
def _user():
    return getattr(getattr(g, "current_user", None), "username", "system")


# Function: _import
def _import(kind, path, filename):
    try:
        importer = DATASET_MAP[kind]["importer"]
        result = importer(path, filename, _user())
        return jsonify({"message": "Import completed", "import": result.to_dict()}), 201
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 422
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception("Technical Assessment import failed")
        return jsonify({"error": f"Import failed: {exc}"}), 500


# Function: upload
@technical_assessment_bp.post("/<kind>/upload")
def upload(kind):
    if kind not in DATASET_KINDS:
        return jsonify({"error": "Unsupported dataset"}), 404
    uploaded = request.files.get("file")
    if not uploaded or not uploaded.filename:
        return jsonify({"error": "An .xlsx file is required"}), 400
    filename = secure_filename(uploaded.filename)
    if Path(filename).suffix.lower() != ".xlsx":
        return jsonify({"error": "Only .xlsx workbooks are supported"}), 415
    with tempfile.TemporaryDirectory(prefix="technical-assessment-") as folder:
        path = Path(folder) / filename
        uploaded.save(path)
        return _import(kind, path, filename)


# Function: list_rows
@technical_assessment_bp.get("/<kind>")
def list_rows(kind):
    if kind not in DATASET_KINDS:
        return jsonify({"error": "Unsupported dataset"}), 404
    dataset_type = DATASET_MAP[kind]["dataset_type"]
    if kind == "technical-evaluation-categorize":
        topic = (request.args.get("topic") or "").strip() or None
        search = (request.args.get("search") or "").strip()
        return jsonify(get_technical_evaluation_categorize_dashboard(topic=topic, search=search))

    import_record = latest_import(dataset_type)
    if not import_record:
        return jsonify({"items": [], "total": 0, "import": None})
    model = DATASET_MAP[kind]["model"]
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 25, type=int), 1), 200)
    search = (request.args.get("search") or "").strip()
    query = model.query.filter_by(import_id=import_record.id)
    if search:
        pattern = f"%{search}%"
        if model is BusinessValidation:
            query = query.filter(db.or_(model.application_number.ilike(pattern), model.name.ilike(pattern),
                                        model.categorization.ilike(pattern)))
        else:
            query = query.filter(db.or_(model.app_id.ilike(pattern), model.application_name.ilike(pattern),
                                        model.topic.ilike(pattern)))
    pagination = query.order_by(model.row_number).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "items": [row.to_dict() for row in pagination.items], "total": pagination.total,
        "page": page, "per_page": per_page, "import": import_record.to_dict(),
    })


# Function: clear
@technical_assessment_bp.delete("/<kind>/clear")
def clear(kind):
    if kind not in DATASET_KINDS:
        return jsonify({"error": "Unsupported dataset"}), 404
    try:
        dataset_type = DATASET_MAP[kind]["dataset_type"]
        cleared_rows = clear_dataset(dataset_type)
        return jsonify({"message": "Data cleared", "cleared_rows": cleared_rows})
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception("Technical Assessment clear failed")
        return jsonify({"error": f"Clear failed: {exc}"}), 500


# Function: imports
@technical_assessment_bp.get("/imports")
def imports():
    rows = TechnicalAssessmentImport.query.order_by(TechnicalAssessmentImport.imported_at.desc()).limit(100).all()
    return jsonify([row.to_dict() for row in rows])


# Function: enrich_categorize_topic
@technical_assessment_bp.post("/technical-evaluation-categorize/enrich")
def enrich_categorize_topic():
    payload = request.get_json(silent=True) or {}
    topic = (payload.get("topic") or "").strip()
    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    try:
        dashboard = enrich_technical_evaluation_categorize_topic(topic)
        return jsonify(dashboard)
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 422
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception("Technical Evaluation categorize enrichment failed")
        return jsonify({"error": f"Enrichment failed: {exc}"}), 500
