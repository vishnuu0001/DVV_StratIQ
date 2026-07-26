# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — csm_backend/app/api (routes_upload.py)
# Date: 2025-10-02
# ---------------------------------------------------------------------------
from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse

from app import store
from app.core.exceptions import InvalidFileTypeError
from app.models.workbook import WorkbookUploadResponse, SheetInfo
from app.services.workbook_parser_service import WorkbookParserService
from app.services.sheet_normalizer_service import SheetNormalizerService
from app.services.input_assumption_service import InputAssumptionService
from app.services.vendor_spend_service import VendorSpendService
from app.services.tower_consolidation_service import TowerConsolidationService
from app.services.transition_cost_service import TransitionCostService
from app.services.savings_summary_service import SavingsSummaryService
from app.services.executive_dashboard_service import ExecutiveDashboardService
from app.services.vendor_landscape_service import VendorLandscapeService
from app.services.techm_growth_service import TechMGrowthService
from app.services.transformation_capacity_service import TransformationCapacityService
from app.services.operating_model_service import OperatingModelService
from app.services.vendor_heatmap_service import VendorHeatmapService
from app.services.roadmap_service import RoadmapService
from app.services.calculation_audit_service import CalculationAuditService

router = APIRouter()


# Function: upload_workbook
@router.post("/csm/workbooks/upload", response_model=WorkbookUploadResponse)
async def upload_workbook(file: UploadFile = File(...)) -> WorkbookUploadResponse:
    """Upload and parse a Consolidation Savings Model .xlsx workbook."""
    filename = file.filename or ""
    if not filename.lower().endswith(".xlsx"):
        raise InvalidFileTypeError(filename)

    file_bytes = await file.read()

    # Parse workbook
    parser = WorkbookParserService()
    parsed = parser.parse(file_bytes)

    # Compute all derived data up-front and cache in store
    input_svc = InputAssumptionService()
    derived_inputs = input_svc.calculate_derived_inputs(parsed.inputs)

    vendor_svc = VendorSpendService()
    tower_svc = TowerConsolidationService()
    tower_result = tower_svc.calculate_model(parsed.vendor_records, parsed.inputs, parsed.tower_params)

    transition_svc = TransitionCostService()
    transition_result = transition_svc.calculate(tower_result.rows, parsed.inputs)

    savings_svc = SavingsSummaryService()
    savings_summary = savings_svc.summarise(tower_result)

    dashboard_svc = ExecutiveDashboardService()
    dashboard = dashboard_svc.build(
        workbook_id="pending",  # will be updated after store.new_workbook_id()
        vendor_records=parsed.vendor_records,
        tower_result=tower_result,
        inputs=parsed.inputs,
        validation=parsed.validation,
    )

    landscape_svc = VendorLandscapeService()
    landscape_data, landscape_audit = landscape_svc.analyse(parsed.vendor_records)

    techm_svc = TechMGrowthService()
    techm_data = techm_svc.calculate(parsed.vendor_records)

    capacity_svc = TransformationCapacityService()
    capacity_data = capacity_svc.calculate(parsed.vendor_records)

    heatmap_svc = VendorHeatmapService()
    heatmap_data = heatmap_svc.calculate(parsed.vendor_records)

    operating_svc = OperatingModelService()
    operating_data = operating_svc.analyse(parsed.vendor_records, parsed.inputs)

    roadmap_svc = RoadmapService()
    roadmap_data = roadmap_svc.generate(tower_result, parsed.inputs)

    audit_svc = CalculationAuditService()
    full_audit = audit_svc.build_full_audit(
        inputs=parsed.inputs,
        derived=derived_inputs,
        vendor_records=parsed.vendor_records,
        tower_result=tower_result,
        additional_audits={
            "vendor_landscape": landscape_audit,
            "techm_growth": techm_data.get("calculation_audit", {}),
            "transformation_capacity": capacity_data.get("calculation_audit", {}),
            "heatmap": heatmap_data.get("calculation_audit", {}),
            "operating_model": operating_data.get("calculation_audit", {}),
        },
    )

    # Build sheet info metadata
    normalizer = SheetNormalizerService()
    sheet_infos = normalizer.get_sheet_infos(parsed.raw_sheets)

    # Generate workbook ID and store all results
    workbook_id = store.new_workbook_id()

    store.put(workbook_id, {
        "filename": filename,
        "inputs": parsed.inputs,
        "derived_inputs": derived_inputs,
        "vendor_records": parsed.vendor_records,
        "tower_params": parsed.tower_params,
        "tower_result": tower_result,
        "transition_result": transition_result,
        "savings_summary": savings_summary,
        "landscape": landscape_data,
        "landscape_audit": landscape_audit,
        "techm": techm_data,
        "capacity": capacity_data,
        "heatmap": heatmap_data,
        "operating_model": operating_data,
        "roadmap": roadmap_data,
        "full_audit": full_audit,
        "validation": parsed.validation,
        "sheet_names": parsed.sheet_names,
        "sheet_infos": sheet_infos,
    })

    return WorkbookUploadResponse(
        workbook_id=workbook_id,
        filename=filename,
        status="success",
        sheet_count=len(sheet_infos),
        sheets=sheet_infos,
        validation=parsed.validation,
        message=f"Workbook parsed successfully. {len(parsed.vendor_records)} vendor records loaded.",
    )
