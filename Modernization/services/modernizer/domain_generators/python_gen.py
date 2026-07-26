# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — services/modernizer/domain_generators (python_gen.py)
# Date: 2025-10-07
# ---------------------------------------------------------------------------
from __future__ import annotations

import functools
import hashlib
import json
import logging
import os
import re
import tempfile
import textwrap
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

    # Frontend generation now lives in the caller (_llm_gen_domain) — a C#
    # backend can pair with any frontend framework, not just the AVEVA/plain-JS
    # templates this function used to hardcode.


# Function: _llm_domain_python
def _llm_domain_python(
    files: "Dict[str, str]",
    domain: str,
    root_ns: str,
    domain_tables: "List[str]",
    context: str,
    prod_rules: str,
    model: str,
    system: str,
    tables: "List[str]",
    on_step: "Optional[Callable[[str], None]]",
    generate: "Callable[..., str]",
    on_validation: "Optional[Callable[[object, int], None]]" = None,
) -> None:
    """Add Python / FastAPI domain files to *files* (mutates in-place)."""
    from .._shared import _TOKENS_DEFAULT, _TOKENS_MIGRATION, _adaptive_num_ctx
    from ..validation_orchestration import _generate_validated
    pkg  = domain.lower()
    base = f"ModernizedApp/app/{pkg}"

    # SQLAlchemy model + Pydantic schemas (LLM)
    try:
        if on_step:
            on_step(f"[{domain}] Generating SQLAlchemy models + Pydantic schemas…")
        prompt = (
            f"{context}\n{prod_rules}\n\n"
            f"Generate a COMPLETE Python file containing:\n"
            f"1. SQLAlchemy 2 ORM model class {domain.rstrip('s')} (in app/models/{pkg}.py style):\n"
            f"   - from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship\n"
            f"   - ALL relevant columns with proper types, nullable constraints, defaults, indexes\n"
            f"   - is_active: Mapped[bool] = mapped_column(default=True, index=True)\n"
            f"   - created_at, updated_at with server_default and onupdate\n"
            f"   - __tablename__, __repr__\n"
            f"   - Domain-specific fields inferred from '{domain}' and tables: {', '.join(domain_tables)}\n"
            f"2. Pydantic v2 schemas:\n"
            f"   - {domain.rstrip('s')}Base(BaseModel): shared fields with validators\n"
            f"   - {domain.rstrip('s')}Create({domain.rstrip('s')}Base): create request\n"
            f"   - {domain.rstrip('s')}Update(BaseModel): all Optional fields for partial update\n"
            f"   - {domain.rstrip('s')}Response({domain.rstrip('s')}Base): response with id, created_at, updated_at\n"
            f"   - model_config = ConfigDict(from_attributes=True)\n"
            f"   - Field validators with real business rules (e.g. name min/max length, positive amounts)\n"
            f"3. Separate PagedResponse[T] generic schema\n"
            f"Output ONLY the Python file content. No markdown fences."
        )
        _rel = f"{base}/models.py"
        _content, _result, _attempts = _generate_validated(
            prompt, model=model, system=system, max_tokens=_TOKENS_DEFAULT,
            num_ctx=_adaptive_num_ctx(len(prompt) + len(system), _TOKENS_DEFAULT),
            rel_path=_rel, language="python",
            on_attempt=(lambda a, m, _d=domain: on_step(f"[{_d}] Fixing models + schemas — attempt {a}/{m}…")) if on_step else None,
        )
        files[_rel] = _content
        if on_validation:
            on_validation(_result, _attempts)
    except Exception as exc:
        files[f"{base}/models.py"] = f"# LLM generation failed: {exc}\n"

    # FastAPI router with full CRUD (LLM)
    try:
        if on_step:
            on_step(f"[{domain}] Generating FastAPI router…")
        prompt = (
            f"{context}\n{prod_rules}\n\n"
            f"Generate a COMPLETE production-ready FastAPI async router for the {domain} domain.\n"
            f"File: app/routers/{pkg}.py\n\n"
            f"Requirements:\n"
            f"- from fastapi import APIRouter, Depends, HTTPException, status, Query\n"
            f"- from sqlalchemy.ext.asyncio import AsyncSession\n"
            f"- from app.database import get_db\n"
            f"- from app.models.{pkg} import {domain.rstrip('s')}, {domain.rstrip('s')}Create, {domain.rstrip('s')}Update, {domain.rstrip('s')}Response, PagedResponse\n"
            f"- import logging; logger = logging.getLogger(__name__)\n"
            f"- router = APIRouter(prefix='/api/{pkg}', tags=['{domain}'])\n"
            f"- ALL 5 endpoints fully async:\n"
            f"    GET  /  \u2192 paginated list: async def get_{pkg}(page:int=1, size:int=20, search:str='', db:AsyncSession=Depends(get_db))\n"
            f"       * select with .where(is_active==True) + ilike search + offset/limit + total count\n"  # nosec B608
            f"       * returns PagedResponse[{domain.rstrip('s')}Response]\n"
            f"    GET  /{{item_id}}  \u2192 async def get_{pkg[:-1]}(item_id:int, db:AsyncSession=Depends(get_db))\n"
            f"       * 404 HTTPException if not found\n"
            f"    POST /  \u2192 async def create_{pkg[:-1]}(data:{domain.rstrip('s')}Create, db:AsyncSession=Depends(get_db))\n"
            f"       * 409 conflict check for duplicate name/key if applicable\n"
            f"       * db.add(obj); await db.commit(); await db.refresh(obj); return obj\n"
            f"       * status_code=status.HTTP_201_CREATED\n"
            f"    PUT  /{{item_id}}  \u2192 async def update_{pkg[:-1]}(item_id:int, data:{domain.rstrip('s')}Update, db:AsyncSession=Depends(get_db))\n"
            f"       * partial update: only update fields that are not None\n"
            f"       * 404 if not found\n"
            f"    DELETE /{{item_id}}  \u2192 async def delete_{pkg[:-1]}(item_id:int, db:AsyncSession=Depends(get_db))\n"
            f"       * soft-delete: set is_active=False, await db.commit()\n"
            f"       * 404 if not found; return 204 No Content\n"
            f"- logger.info on success, logger.warning on not-found, logger.error on exceptions\n"
            f"- Domain tables: {', '.join(domain_tables)}\n"
            f"Output ONLY the Python file content. No markdown fences."
        )
        _rel = f"{base}/router.py"
        _content, _result, _attempts = _generate_validated(
            prompt, model=model, system=system, max_tokens=_TOKENS_DEFAULT,
            num_ctx=_adaptive_num_ctx(len(prompt) + len(system), _TOKENS_DEFAULT),
            rel_path=_rel, language="python",
            on_attempt=(lambda a, m, _d=domain: on_step(f"[{_d}] Fixing FastAPI router — attempt {a}/{m}…")) if on_step else None,
        )
        files[_rel] = _content
        if on_validation:
            on_validation(_result, _attempts)
    except Exception as exc:
        files[f"{base}/router.py"] = f"# LLM generation failed: {exc}\n"

    # Alembic migration (LLM)
    try:
        if on_step:
            on_step(f"[{domain}] Generating Alembic migration…")
        prompt = (
            f"{context}\n{prod_rules}\n\n"
            f"Generate a COMPLETE Alembic migration script for the {domain} domain:\n"
            f"- Standard Alembic revision header with revision, down_revision, branch_labels, depends_on\n"
            f"- upgrade() function: op.create_table('{pkg}', all columns with proper types and constraints)\n"
            f"- downgrade() function: op.drop_table('{pkg}')\n"
            f"- Include all indexes: op.create_index() for commonly queried fields\n"
            f"- Tables: {', '.join(domain_tables)}\n"
            f"- PostgreSQL 16 compatible types (use sa.DateTime(timezone=True), sa.Text, etc.)\n"
            f"Output ONLY the Python migration file content. No markdown fences."
        )
        _rel = f"{base}/migration.py"
        _content, _result, _attempts = _generate_validated(
            prompt, model=model, system=system, max_tokens=_TOKENS_MIGRATION,
            num_ctx=_adaptive_num_ctx(len(prompt) + len(system), _TOKENS_MIGRATION),
            rel_path=_rel, language="python",
            on_attempt=(lambda a, m, _d=domain: on_step(f"[{_d}] Fixing Alembic migration — attempt {a}/{m}…")) if on_step else None,
        )
        files[_rel] = _content
        if on_validation:
            on_validation(_result, _attempts)
    except Exception as exc:
        files[f"{base}/migration.py"] = f"# LLM generation failed: {exc}\n"
