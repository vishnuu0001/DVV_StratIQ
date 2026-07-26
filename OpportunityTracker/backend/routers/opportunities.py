# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: OpportunityTracker — backend/routers (opportunities.py)
# Date: 2025-12-18
# ---------------------------------------------------------------------------
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Opportunity
from schemas import OpportunityCreate, OpportunityUpdate, OpportunityOut, ImportResultOut
from auth import get_current_user
from opportunity_import import parse_fy27_plan_tracker, resolve_upsert_key

router = APIRouter(tags=["opportunities"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Function: list_opportunities
@router.get("/opportunities", response_model=List[OpportunityOut])
def list_opportunities(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.query(Opportunity).order_by(Opportunity.id).all()
    return [_to_out(r) for r in rows]


# Function: create_opportunity
@router.post("/opportunities", response_model=OpportunityOut, status_code=201)
def create_opportunity(data: OpportunityCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = Opportunity(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


# Function: update_opportunity
@router.put("/opportunities/{opp_id}", response_model=OpportunityOut)
def update_opportunity(opp_id: int, data: OpportunityUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Opportunity not found.")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


# Function: delete_opportunity
@router.delete("/opportunities/{opp_id}", status_code=204)
def delete_opportunity(opp_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Opportunity not found.")
    db.delete(obj)
    db.commit()


# Function: import_opportunities
@router.post("/opportunities/import", response_model=ImportResultOut)
def import_opportunities(file: UploadFile = File(...), db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Bulk-import the 'FY 27 Plan Tracker' sheet — parse once at upload time,
    upsert against existing opportunities (by CRM Ref # if real, else by
    opportunity_name+customer_group), never re-parse the xlsx later."""
    ext = os.path.splitext(file.filename or "")[1] or ".xlsx"
    dest = os.path.join(UPLOAD_DIR, f"opp_import_{uuid.uuid4().hex}{ext}")
    with open(dest, "wb") as f:
        f.write(file.file.read())

    try:
        parsed_rows, warnings = parse_fy27_plan_tracker(dest)
    except Exception as exc:
        os.remove(dest)
        raise HTTPException(
            status_code=422,
            detail=f"File does not match the FY 27 Plan Tracker template: {exc}",
        )
    finally:
        if os.path.exists(dest):
            os.remove(dest)

    # Load existing rows once into a lookup, not N queries per import row.
    existing_by_key: dict[tuple[str, str], Opportunity] = {}
    for existing in db.query(Opportunity).all():
        existing_by_key[resolve_upsert_key({
            "crm_ref": existing.crm_ref,
            "opportunity_name": existing.opportunity_name,
            "customer_group": existing.customer_group,
        })] = existing

    created = 0
    updated = 0
    for row in parsed_rows:
        key = resolve_upsert_key(row)
        existing = existing_by_key.get(key)
        if existing:
            for k, v in row.items():
                setattr(existing, k, v)
            updated += 1
        else:
            obj = Opportunity(**row)
            db.add(obj)
            db.flush()  # so a later duplicate row in the same file also matches this key
            existing_by_key[key] = obj
            created += 1

    db.commit()
    return ImportResultOut(created=created, updated=updated, warnings=warnings)


# Function: _to_out
def _to_out(obj: Opportunity) -> OpportunityOut:
    return OpportunityOut(
        id=obj.id,
        region=obj.region,
        customer_group=obj.customer_group,
        sub_vertical=obj.sub_vertical,
        solution_offering=obj.solution_offering,
        so_coe_leader=obj.so_coe_leader,
        crm_ref=obj.crm_ref,
        opportunity_name=obj.opportunity_name,
        oppty_stage=obj.oppty_stage,
        start_date=obj.start_date,
        oppty_owner=obj.oppty_owner,
        tcv_mn=obj.tcv_mn,
        q1_mn=obj.q1_mn,
        q2_mn=obj.q2_mn,
        q3_mn=obj.q3_mn,
        q4_mn=obj.q4_mn,
        fy27_mn=obj.fy27_mn,
        remarks=obj.remarks,
        hyperscaler=obj.hyperscaler,
        delivery_ibu=obj.delivery_ibu,
        delivery_ibu_leader=obj.delivery_ibu_leader,
        delivery_validation=obj.delivery_validation,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )
