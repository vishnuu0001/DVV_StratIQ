# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Logistics domain models.
# Date: 2025-11-16
# ---------------------------------------------------------------------------
"""Logistics domain models."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from kg.models.base import BaseEntity


class ASN(BaseEntity):
    kind: Literal["ASN"] = "ASN"  # type: ignore[override]
    domain: Literal["logistics"] = "logistics"  # type: ignore[override]
    po_id: str
    carrier_id: str
    ship_date: datetime
    eta: datetime
    incoterm: Literal["EXW", "FCA", "FOB", "CIF", "DAP", "DDP"]
    handling_units: list[str] = []


class Carrier(BaseEntity):
    kind: Literal["Carrier"] = "Carrier"  # type: ignore[override]
    domain: Literal["logistics"] = "logistics"  # type: ignore[override]
    name: str
    mode: Literal["AIR", "SEA", "ROAD", "RAIL", "MULTIMODAL"]
    service_level: str
    tracking_api: str | None = None
    on_time_performance: float


class Shipment(BaseEntity):
    kind: Literal["Shipment"] = "Shipment"  # type: ignore[override]
    domain: Literal["logistics"] = "logistics"  # type: ignore[override]
    asn_id: str
    status: Literal["BOOKED", "IN_TRANSIT", "ARRIVED", "EXCEPTION", "DELIVERED"] = "BOOKED"
    current_location: str | None = None
    last_event_at: datetime


class Container(BaseEntity):
    kind: Literal["Container"] = "Container"  # type: ignore[override]
    domain: Literal["logistics"] = "logistics"  # type: ignore[override]
    shipment_id: str
    type: Literal["PALLET", "CARTON", "CONT_20FT", "CONT_40FT"]
    seal_no: str
    gross_weight_kg: Decimal


class Customs(BaseEntity):
    kind: Literal["Customs"] = "Customs"  # type: ignore[override]
    domain: Literal["logistics"] = "logistics"  # type: ignore[override]
    shipment_id: str
    port: str
    status: Literal["PENDING", "CLEARED", "HELD", "REJECTED"] = "PENDING"
    duties_amount: Decimal | None = None
    cleared_at: datetime | None = None
