# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — services/modernizer/domain_generators (go.py)
# Date: 2025-08-03
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



# Function: _llm_domain_go
def _llm_domain_go(
    files: "Dict[str, str]",
    domain: str,
    root_ns: str,
    domain_tables: "List[str]",
    context: str,
    prod_rules: str,
    backend_tech: str,
    model: str,
    system: str,
    tables: "List[str]",
    on_step: "Optional[Callable[[str], None]]",
    generate: "Callable[..., str]",
    on_validation: "Optional[Callable[[object, int], None]]" = None,
) -> None:
    """Add idiomatic Go domain files to *files* (mutates in-place). Real Go —
    no C#/.NET vocabulary — using pgx for Postgres access and either Gin or
    the standard library net/http router, chosen from backend_tech."""
    from .._shared import _TOKENS_DEFAULT, _TOKENS_MIGRATION, _adaptive_num_ctx
    from ..validation_orchestration import _generate_validated
    pkg  = domain.lower()
    base = f"ModernizedApp/internal/{pkg}"
    entity = domain.rstrip("s")
    use_gin = "gin" in (backend_tech or "").lower()
    use_fiber = "fiber" in (backend_tech or "").lower()

    # Repository layer (LLM)
    try:
        if on_step:
            on_step(f"[{domain}] Generating repository layer…")
        prompt = (
            f"{context}\n{prod_rules}\n\n"
            f"Generate a COMPLETE Go file for the {domain} domain's data-access layer.\n"
            f"File: internal/{pkg}/repository.go\n\n"
            f"Requirements:\n"
            f"- package {pkg}\n"
            f"- import \"context\", \"errors\", \"github.com/jackc/pgx/v5\", \"github.com/jackc/pgx/v5/pgxpool\"\n"
            f"- struct {entity} with exported PascalCase fields matching columns inferred from domain '{domain}' "
            f"and tables: {', '.join(domain_tables)}; each field tagged `db:\"snake_case_name\" json:\"camelCase\"`\n"
            f"- struct Create{entity}Request and Update{entity}Request with only the mutable fields\n"
            f"- var ErrNotFound = errors.New(\"{pkg}: not found\")\n"
            f"- type Repository struct {{ pool *pgxpool.Pool }}\n"
            f"- func NewRepository(pool *pgxpool.Pool) *Repository\n"
            f"- COMPLETE methods, every one taking context.Context as the first argument and using "
            f"parameterized queries ($1, $2, ...) - never string-formatted SQL:\n"
            f"    * List(ctx context.Context, limit, offset int, search string) ([]{entity}, int, error) "
            f"- paginated, filters is_active = true, second query for total count\n"
            f"    * GetByID(ctx context.Context, id int64) ({entity}, error) - wraps pgx.ErrNoRows as ErrNotFound\n"
            f"    * Create(ctx context.Context, req Create{entity}Request) ({entity}, error)\n"
            f"    * Update(ctx context.Context, id int64, req Update{entity}Request) ({entity}, error) "
            f"- partial update, only set fields present in the request\n"
            f"    * Delete(ctx context.Context, id int64) error - soft delete: UPDATE ... SET is_active = false\n"
            f"Output ONLY the Go file content. No markdown fences."
        )
        _rel = f"{base}/repository.go"
        _content, _result, _attempts = _generate_validated(
            prompt, model=model, system=system, max_tokens=_TOKENS_DEFAULT,
            num_ctx=_adaptive_num_ctx(len(prompt) + len(system), _TOKENS_DEFAULT),
            rel_path=_rel, language="go",
            on_attempt=(lambda a, m, _d=domain: on_step(f"[{_d}] Fixing repository layer — attempt {a}/{m}…")) if on_step else None,
        )
        files[_rel] = _content
        if on_validation:
            on_validation(_result, _attempts)
    except Exception as exc:
        files[f"{base}/repository.go"] = f"// LLM generation failed: {exc}\n"

    # HTTP handlers (LLM) — Gin or net/http, per backend_tech
    try:
        if on_step:
            on_step(f"[{domain}] Generating HTTP handlers…")
        if use_fiber:
            prompt = (
                f"{context}\n{prod_rules}\n\n"
                f"Generate a COMPLETE Go handler for {domain} using github.com/gofiber/fiber/v2. "
                f"Define Handler, NewHandler, RegisterRoutes(*fiber.App), and full list/get/create/update/delete "
                f"handlers under /api/{pkg}. Parse path/query values safely, validate JSON bodies, propagate "
                f"c.UserContext() to Repository calls, and return correct JSON status codes. "
                f"Output ONLY the Go source file for package {pkg}."
            )
        elif use_gin:
            prompt = (
                f"{context}\n{prod_rules}\n\n"
                f"Generate a COMPLETE Go file for the {domain} domain's HTTP handlers using the Gin web framework.\n"
                f"File: internal/{pkg}/handler.go\n\n"
                f"Requirements:\n"
                f"- package {pkg}\n"
                f"- import \"net/http\", \"strconv\", \"errors\", \"github.com/gin-gonic/gin\"\n"
                f"- type Handler struct {{ repo *Repository }}\n"
                f"- func NewHandler(repo *Repository) *Handler\n"
                f"- func (h *Handler) RegisterRoutes(rg *gin.RouterGroup) registering all 5 CRUD routes under /{pkg}\n"
                f"- ALL 5 handlers fully implemented, each propagating c.Request.Context() to the repository call:\n"
                f"    GET    /{pkg}      -> List, paginated via ?page=&size= query params, JSON {{items, total, page, size}}\n"
                f"    GET    /{pkg}/:id  -> GetByID, 404 gin.H{{\"error\":...}} if errors.Is(err, ErrNotFound)\n"
                f"    POST   /{pkg}      -> Create, c.ShouldBindJSON, 201 on success, 400 on bind error\n"
                f"    PUT    /{pkg}/:id  -> Update, 404 if not found\n"
                f"    DELETE /{pkg}/:id  -> Delete, 204 on success, 404 if not found\n"
                f"- non-404 repository errors mapped to 500 with a generic message (never leak the raw error)\n"
                f"Output ONLY the Go file content. No markdown fences."
            )
        else:
            prompt = (
                f"{context}\n{prod_rules}\n\n"
                f"Generate a COMPLETE Go file for the {domain} domain's HTTP handlers using ONLY the standard "
                f"library net/http (Go 1.22+ http.ServeMux with method+path patterns) - no third-party router.\n"
                f"File: internal/{pkg}/handler.go\n\n"
                f"Requirements:\n"
                f"- package {pkg}\n"
                f"- import \"net/http\", \"encoding/json\", \"strconv\", \"errors\"\n"
                f"- type Handler struct {{ repo *Repository }}\n"
                f"- func NewHandler(repo *Repository) *Handler\n"
                f"- func (h *Handler) RegisterRoutes(mux *http.ServeMux) registering all 5 CRUD routes under /{pkg} "
                f"using Go 1.22 ServeMux patterns (e.g. \"GET /{pkg}\", \"GET /{pkg}/{{id}}\", \"POST /{pkg}\", "
                f"\"PUT /{pkg}/{{id}}\", \"DELETE /{pkg}/{{id}}\")\n"
                f"- ALL 5 handlers fully implemented using r.Context(), json.NewEncoder(w).Encode(...) for "
                f"responses, and http.Error(w, ...) on failure\n"
                f"- errors.Is(err, ErrNotFound) mapped to http.StatusNotFound, everything else to "
                f"http.StatusInternalServerError with a generic message\n"
                f"Output ONLY the Go file content. No markdown fences."
            )
        _rel = f"{base}/handler.go"
        _content, _result, _attempts = _generate_validated(
            prompt, model=model, system=system, max_tokens=_TOKENS_DEFAULT,
            num_ctx=_adaptive_num_ctx(len(prompt) + len(system), _TOKENS_DEFAULT),
            rel_path=_rel, language="go",
            on_attempt=(lambda a, m, _d=domain: on_step(f"[{_d}] Fixing HTTP handlers — attempt {a}/{m}…")) if on_step else None,
        )
        files[_rel] = _content
        if on_validation:
            on_validation(_result, _attempts)
    except Exception as exc:
        files[f"{base}/handler.go"] = f"// LLM generation failed: {exc}\n"

    # SQL migration (LLM)
    try:
        if on_step:
            on_step(f"[{domain}] Generating SQL migration…")
        prompt = (
            f"{context}\n{prod_rules}\n\n"
            f"Generate a COMPLETE PostgreSQL migration SQL script for the {domain} domain:\n"
            f"- CREATE TABLE {pkg} with all relevant columns inferred from domain '{domain}' and tables: "
            f"{', '.join(domain_tables)}, proper types and constraints\n"
            f"- is_active boolean not null default true; created_at, updated_at timestamptz not null default now()\n"
            f"- Indexes for commonly filtered/queried columns\n"
            f"- End with a commented-out DROP TABLE {pkg}; as the rollback\n"
            f"Output ONLY the SQL file content. No markdown fences."
        )
        _rel = f"ModernizedApp/migrations/{pkg}.sql"
        _content, _result, _attempts = _generate_validated(
            prompt, model=model, system=system, max_tokens=_TOKENS_MIGRATION,
            num_ctx=_adaptive_num_ctx(len(prompt) + len(system), _TOKENS_MIGRATION),
            rel_path=_rel, language="sql",
            on_attempt=(lambda a, m, _d=domain: on_step(f"[{_d}] Fixing SQL migration — attempt {a}/{m}…")) if on_step else None,
        )
        files[_rel] = _content
        if on_validation:
            on_validation(_result, _attempts)
    except Exception as exc:
        files[f"ModernizedApp/migrations/{pkg}.sql"] = f"-- LLM generation failed: {exc}\n"
