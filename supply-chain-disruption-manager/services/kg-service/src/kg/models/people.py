# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: People domain models.
# Date: 2025-07-30
# ---------------------------------------------------------------------------
"""People domain models."""
from __future__ import annotations

from typing import Literal

from kg.models.base import BaseEntity


class Person(BaseEntity):
    domain: Literal["people"] = "people"  # type: ignore[override]
    name: str
    role: str
    email: str
    phone: str | None = None
    region: str | None = None
