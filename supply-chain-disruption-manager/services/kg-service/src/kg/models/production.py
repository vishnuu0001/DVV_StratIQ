# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Production domain models.
# Date: 2026-04-19
# ---------------------------------------------------------------------------
"""Production domain models."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from kg.models.base import BaseEntity


class ProductionOrder(BaseEntity):
    kind: Literal["ProductionOrder"] = "ProductionOrder"  # type: ignore[override]
    domain: Literal["production"] = "production"  # type: ignore[override]
    finished_good_id: str
    qty: Decimal
    start_date: date
    due_date: date
    status: Literal["PLANNED", "RELEASED", "RUNNING", "COMPLETED", "CANCELLED"] = "PLANNED"


class BOMComponent(BaseModel):
    material_id: str
    qty_per: Decimal
    uom: str


class BOM(BaseEntity):
    kind: Literal["BOM"] = "BOM"  # type: ignore[override]
    domain: Literal["production"] = "production"  # type: ignore[override]
    parent_material_id: str
    version: str
    components: list[BOMComponent] = []


class MaterialIssue(BaseEntity):
    kind: Literal["MaterialIssue"] = "MaterialIssue"  # type: ignore[override]
    domain: Literal["production"] = "production"  # type: ignore[override]
    production_order_id: str
    material_id: str
    qty_issued: Decimal
    source_bin_id: str
    dest_workcenter_id: str
    issued_at: datetime


class WorkCenter(BaseEntity):
    kind: Literal["WorkCenter"] = "WorkCenter"  # type: ignore[override]
    domain: Literal["production"] = "production"  # type: ignore[override]
    shopfloor_id: str
    line: str
    capacity_per_hr: Decimal
    current_order_id: str | None = None


class ShopFloor(BaseEntity):
    kind: Literal["ShopFloor"] = "ShopFloor"  # type: ignore[override]
    domain: Literal["production"] = "production"  # type: ignore[override]
    plant_address: str
    shift_pattern: str
