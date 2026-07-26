# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — backend/app/csm (store.py)
# Date: 2026-06-15
# ---------------------------------------------------------------------------
from __future__ import annotations

import uuid
from typing import Any, Dict

_store: Dict[str, Any] = {}


# Function: new_workbook_id
def new_workbook_id() -> str:
    return str(uuid.uuid4())


# Function: put
def put(workbook_id: str, data: Any) -> None:
    _store[workbook_id] = data


# Function: get
def get(workbook_id: str) -> Any:
    return _store.get(workbook_id)


# Function: exists
def exists(workbook_id: str) -> bool:
    return workbook_id in _store


# Function: delete
def delete(workbook_id: str) -> None:
    _store.pop(workbook_id, None)


# Function: list_ids
def list_ids() -> list[str]:
    return list(_store.keys())
