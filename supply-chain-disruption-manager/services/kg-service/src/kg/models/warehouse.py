# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Warehouse domain models.
# Date: 2025-10-04
# ---------------------------------------------------------------------------
"""Warehouse domain models."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from kg.models.base import BaseEntity


class Dock(BaseEntity):
    kind: Literal["Dock"] = "Dock"  # type: ignore[override]
    domain: Literal["warehouse"] = "warehouse"  # type: ignore[override]
    warehouse_id: str
    appointment_window_start: datetime | None = None
    appointment_window_end: datetime | None = None
    current_load: int = 0


class GRN(BaseEntity):
    kind: Literal["GRN"] = "GRN"  # type: ignore[override]
    domain: Literal["warehouse"] = "warehouse"  # type: ignore[override]
    po_id: str
    asn_id: str
    received_qty: Decimal
    short_qty: Decimal
    damaged_qty: Decimal
    received_at: datetime


class QualityInspection(BaseEntity):
    kind: Literal["QualityInspection"] = "QualityInspection"  # type: ignore[override]
    domain: Literal["warehouse"] = "warehouse"  # type: ignore[override]
    grn_id: str
    sample_size: int
    defect_rate: float
    disposition: Literal["PENDING", "ACCEPT", "REJECT", "REWORK"] = "PENDING"
    closed_at: datetime | None = None


class Bin(BaseEntity):
    kind: Literal["Bin"] = "Bin"  # type: ignore[override]
    domain: Literal["warehouse"] = "warehouse"  # type: ignore[override]
    warehouse_id: str
    zone: str
    capacity: Decimal
    current_qty: Decimal


class StockLot(BaseEntity):
    kind: Literal["StockLot"] = "StockLot"  # type: ignore[override]
    domain: Literal["warehouse"] = "warehouse"  # type: ignore[override]
    material_id: str
    bin_id: str
    qty_on_hand: Decimal
    qty_allocated: Decimal
    expiry_date: date | None = None
    lot_number: str
