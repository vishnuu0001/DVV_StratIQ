# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — csm_backend/app/models (vendor_spend.py)
# Date: 2026-03-13
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class VendorSpendRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    vendor: str
    spend_category: str
    tower: str
    service_scope: str = ""
    role_type: str = ""
    criticality: str = ""
    pricing_basis: str = ""
    fte_count: Optional[int] = None
    avg_rate_per_hr: Optional[Decimal] = None
    annual_fixed_spend: Optional[Decimal] = None
    annual_spend: Decimal
    source_notes: str = ""


class SpendBreakdown(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    category: str
    total_spend: Decimal
    vendor_count: int
    pct_of_total: Decimal


class VendorSpendSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_spend: Decimal
    vendor_count: int
    unique_vendors: int
    by_category: List[SpendBreakdown]
    by_tower: List[SpendBreakdown]
