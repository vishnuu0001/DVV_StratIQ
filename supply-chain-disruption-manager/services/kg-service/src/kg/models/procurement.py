# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Procurement domain models.
# Date: 2026-02-01
# ---------------------------------------------------------------------------
"""Procurement domain models."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from kg.models.base import BaseEntity


class Supplier(BaseEntity):
    kind: Literal["Supplier"] = "Supplier"  # type: ignore[override]
    domain: Literal["procurement"] = "procurement"  # type: ignore[override]
    name: str
    country: str
    tier: Literal[1, 2, 3]
    lead_time_days: int
    reliability_score: float
    contract_id: str | None = None


class PurchaseOrder(BaseEntity):
    kind: Literal["PurchaseOrder"] = "PurchaseOrder"  # type: ignore[override]
    domain: Literal["procurement"] = "procurement"  # type: ignore[override]
    supplier_id: str
    buyer_id: str
    status: Literal["DRAFT", "OPEN", "ACK", "SHIPPED", "RECEIVED", "CLOSED", "CANCELLED"] = "OPEN"
    currency: str
    total_value: Decimal
    expected_delivery: date


class PurchaseOrderLine(BaseEntity):
    kind: Literal["PurchaseOrderLine"] = "PurchaseOrderLine"  # type: ignore[override]
    domain: Literal["procurement"] = "procurement"  # type: ignore[override]
    po_id: str
    material_id: str
    qty_ordered: Decimal
    uom: Literal["EA", "KG", "L", "M", "BOX"]
    unit_price: Decimal
    need_by_date: date


class Material(BaseEntity):
    kind: Literal["Material"] = "Material"  # type: ignore[override]
    domain: Literal["procurement"] = "procurement"  # type: ignore[override]
    description: str
    category: Literal["RAW", "SFG", "FG", "PACKAGING"]
    criticality: Literal["A", "B", "C"]
    safety_stock: Decimal
    shelf_life_days: int | None = None
