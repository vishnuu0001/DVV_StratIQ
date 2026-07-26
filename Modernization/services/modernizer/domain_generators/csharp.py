# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — services/modernizer/domain_generators (csharp.py)
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



# Function: _llm_domain_csharp
# Function: _gen_csharp_endpoints
def _gen_csharp_endpoints(
    files, base, domain, root_ns, context, prod_rules, source_sec,
    data_access_using, data_access_rule, domain_tables, antipatterns,
    target, model, system, on_step, on_validation,
) -> bool:
    from .._shared import _TOKENS_DEFAULT, _adaptive_num_ctx
    from ..validation_orchestration import _generate_validated
    try:
        if on_step:
            on_step(f"[{domain}] Generating Endpoints/Controller…")
        if target.get("name", "").startswith("AVEVA"):
            prompt = (
                f"{context}\n{prod_rules}{source_sec}\n\n"
                f"Generate a COMPLETE .NET 8 Minimal API route group for the {domain} domain "
                f"as a static extension method class {domain}Endpoints with RegisterRoutes(WebApplication app).\n"
                f"AVEVA MES architecture requirements:\n"
                f"- using statements for Microsoft.AspNetCore.*, FluentValidation, {data_access_using}, ILogger\n"
                f"- Namespace {root_ns}.{domain}Service.Endpoints\n"
                f"- Record DTOs: {domain}Request (Create/Update), {domain}Response\n"
                f"- IValidator<{domain}Request> from FluentValidation with all rules implemented in the same file\n"
                f"- ILogger<{domain}Endpoints> injected and used at info/warn/error levels\n"
                f"- Full CRUD route handlers:\n"
                f"    app.MapGet(\"/api/{domain.lower()}\", ...) → paginated list using IQueryable + Skip/Take\n"
                f"    app.MapGet(\"/api/{domain.lower()}/{{id:int}}\", ...) → single item or 404 ProblemDetails\n"
                f"    app.MapPost(\"/api/{domain.lower()}\", ...) → 201 with Location header\n"
                f"    app.MapPut(\"/api/{domain.lower()}/{{id:int}}\", ...) → 200 or 404\n"
                f"    app.MapDelete(\"/api/{domain.lower()}/{{id:int}}\", ...) → 204 or 404\n"
                f"{data_access_rule}\n"
                f"- Tables: {', '.join(domain_tables)}\n"
                f"- Fix anti-patterns: {', '.join(antipatterns) or 'none'}\n"
                f"- Every lambda/handler must be async Task\n"
                f"Output ONLY the complete C# file content. No markdown fences."
            )
        else:
            prompt = (
                f"{context}\n{prod_rules}\n\n"
                f"Generate a COMPLETE .NET 8 Minimal API route handler class for the {domain} domain:\n"
                f"- using statements for Microsoft.AspNetCore.Http, {data_access_using}, FluentValidation, ILogger, System.ComponentModel.DataAnnotations\n"
                f"- Namespace {root_ns}.{domain}Service.Endpoints\n"
                f"- static class {domain}Endpoints with RegisterRoutes(WebApplication app) extension method\n"
                f"- DTOs: {domain}CreateRequest record, {domain}UpdateRequest record, {domain}Response record (map entity → response)\n"
                f"- AbstractValidator<{domain}CreateRequest> and AbstractValidator<{domain}UpdateRequest> fully implemented\n"
                f"- Full CRUD:\n"
                f"    GET /api/{domain.lower()} → paginated (page/pageSize query params) list\n"
                f"    GET /api/{domain.lower()}/{{id:int}} → single item or TypedResults.NotFound()\n"
                f"    POST /api/{domain.lower()} → TypedResults.Created() with Location header\n"
                f"    PUT /api/{domain.lower()}/{{id:int}} → update or TypedResults.NotFound()\n"
                f"    DELETE /api/{domain.lower()}/{{id:int}} → TypedResults.NoContent() or TypedResults.NotFound()\n"
                f"- All handlers async Task<IResult>\n"
                f"- ILogger<{domain}Endpoints> with info (success), warn (not found), error (exceptions)\n"
                f"- Cancellation token propagated through\n"
                f"{data_access_rule}\n"
                f"- Tables: {', '.join(domain_tables)}\n"
                f"- Fix anti-patterns: {', '.join(antipatterns) or 'none'}\n"
                f"Output ONLY the complete C# file content. No markdown fences."
            )
        _rel = f"{base}/Endpoints/{domain}Endpoints.cs"
        _content, _result, _attempts = _generate_validated(
            prompt, model=model, system=system, max_tokens=_TOKENS_DEFAULT,
            num_ctx=_adaptive_num_ctx(len(prompt) + len(system), _TOKENS_DEFAULT),
            rel_path=_rel, language="csharp",
            on_attempt=(lambda a, m, _d=domain: on_step(f"[{_d}] Fixing Endpoints/Controller — attempt {a}/{m}…")) if on_step else None,
        )
        files[_rel] = _content
        if on_validation:
            on_validation(_result, _attempts)
        return True
    except Exception as exc:
        files[f"{base}/Endpoints/{domain}Endpoints.cs"] = f"// LLM generation failed: {exc}\n"
        return False


# Function: _gen_csharp_service
def _gen_csharp_service(files, base, domain, root_ns, context, prod_rules, model, system, on_step, on_validation) -> bool:
    from .._shared import _TOKENS_DEFAULT, _adaptive_num_ctx
    from ..validation_orchestration import _generate_validated
    try:
        if on_step:
            on_step(f"[{domain}] Generating Service implementation…")
        prompt = (
            f"{context}\n{prod_rules}\n\n"
            f"Generate TWO C# files separated by the sentinel line '// ===FILE===':\n\n"
            f"FILE 1: Interface I{domain}Service in namespace {root_ns}.{domain}Service.Services\n"
            f"- Task<PagedResult<{domain}Response>> GetAllAsync(int page, int pageSize, CancellationToken ct)\n"
            f"- Task<{domain}Response?> GetByIdAsync(int id, CancellationToken ct)\n"
            f"- Task<{domain}Response> CreateAsync({domain}CreateRequest request, CancellationToken ct)\n"
            f"- Task<{domain}Response?> UpdateAsync(int id, {domain}UpdateRequest request, CancellationToken ct)\n"
            f"- Task<bool> DeleteAsync(int id, CancellationToken ct)\n"
            f"- record PagedResult<T>(IReadOnlyList<T> Items, int TotalCount, int Page, int PageSize)\n\n"
            f"FILE 2: {domain}ServiceImpl class in namespace {root_ns}.{domain}Service.Services\n"
            f"- Constructor injection of I{domain}Repository _repository and ILogger<{domain}ServiceImpl> _logger\n"
            f"- COMPLETE implementation of every method:\n"
            f"  * GetAllAsync: call repository, map to responses, return paged result with total count\n"
            f"  * GetByIdAsync: call repository, return mapped response or null\n"
            f"  * CreateAsync: validate business rules, save via repository, log info, return response\n"
            f"  * UpdateAsync: fetch existing, apply all changed fields from request, save, log info, return response or null\n"
            f"  * DeleteAsync: fetch existing, soft-delete (IsActive=false + UpdatedAt=DateTime.UtcNow), save, log warn, return bool\n"
            f"- All async methods use await, no .Result or .Wait() calls\n"
            f"- Try/catch with ILogger.LogError on unexpected exceptions, re-throw as domain exception\n"
            f"Output ONLY the C# content. No markdown fences."
        )
        _rel = f"{base}/Services/{domain}ServiceImpl.cs"
        _content, _result, _attempts = _generate_validated(
            prompt, model=model, system=system, max_tokens=_TOKENS_DEFAULT,
            num_ctx=_adaptive_num_ctx(len(prompt) + len(system), _TOKENS_DEFAULT),
            rel_path=_rel, language="csharp",
            on_attempt=(lambda a, m, _d=domain: on_step(f"[{_d}] Fixing Service implementation — attempt {a}/{m}…")) if on_step else None,
        )
        files[_rel] = _content
        if on_validation:
            on_validation(_result, _attempts)
        return True
    except Exception as exc:
        files[f"{base}/Services/{domain}ServiceImpl.cs"] = f"// LLM generation failed: {exc}\n"
        return False


# Function: _gen_csharp_repository
def _gen_csharp_repository(files, base, domain, root_ns, context, prod_rules, is_dapper, model, system, on_step, on_validation) -> bool:
    from .._shared import _TOKENS_DEFAULT, _adaptive_num_ctx
    from ..validation_orchestration import _generate_validated
    try:
        if on_step:
            on_step(f"[{domain}] Generating Repository ({'Dapper' if is_dapper else 'EF Core'})…")
        repo_impl_spec = (
            f"FILE 2: {domain}Repository implementing I{domain}Repository using Dapper:\n"
            f"- Constructor injection of IDbConnectionFactory _connectionFactory (CreateConnection() returns IDbConnection)\n"
            f"- COMPLETE async implementations using Dapper's QueryAsync/QuerySingleOrDefaultAsync/ExecuteAsync\n"
            f"  against parameterized raw SQL (NEVER string-concatenated SQL) on the {domain} table\n"
            f"- GetPagedAsync uses a paginated SQL query (OFFSET/FETCH) plus a separate COUNT(*) query for Total\n"
            f"- Also include {domain}Entity class: Id, Name, IsActive, CreatedAt, UpdatedAt — plus domain-specific fields for {domain}\n"
            f"- IDbConnectionFactory interface: IDbConnection CreateConnection()\n"
            f"- {domain}Service.csproj with .NET 8, Dapper, Microsoft.Data.SqlClient, and validation NuGet packages "
            f"(NO EntityFrameworkCore package reference)\n"
        ) if is_dapper else (
            f"FILE 2: {domain}Repository implementing I{domain}Repository using EF Core:\n"
            f"- Constructor injection of {root_ns}DbContext _context\n"
            f"- COMPLETE async implementations using _context.Set<{domain}Entity>()\n"
            f"- GetPagedAsync uses .Where(x => x.IsActive).Skip((page-1)*pageSize).Take(pageSize)\n"
            f"- Also include {domain}Entity class: Id, Name, IsActive, CreatedAt, UpdatedAt — plus domain-specific fields for {domain}\n"
            f"- {root_ns}DbContext partial class with DbSet<{domain}Entity> {domain}s and OnModelCreating config\n"
            f"- {domain}Service.csproj with .NET 8, EF Core, and validation NuGet packages\n"
        )
        prompt = (
            f"{context}\n{prod_rules}\n\n"
            f"Generate TWO C# files separated by '// ===FILE===':\n\n"
            f"FILE 1: I{domain}Repository interface in namespace {root_ns}.{domain}Service.Repositories\n"
            f"- Task<({domain}Entity[] Items, int Total)> GetPagedAsync(int page, int pageSize, CancellationToken ct)\n"
            f"- Task<{domain}Entity?> GetByIdAsync(int id, CancellationToken ct)\n"
            f"- Task<{domain}Entity> AddAsync({domain}Entity entity, CancellationToken ct)\n"
            f"- Task<{domain}Entity> UpdateAsync({domain}Entity entity, CancellationToken ct)\n"
            f"- Task SaveChangesAsync(CancellationToken ct)\n\n"
            f"{repo_impl_spec}"
            f"Output ONLY C# content. No markdown fences."
        )
        _rel = f"{base}/Repositories/{domain}Repository.cs"
        _content, _result, _attempts = _generate_validated(
            prompt, model=model, system=system, max_tokens=_TOKENS_DEFAULT,
            num_ctx=_adaptive_num_ctx(len(prompt) + len(system), _TOKENS_DEFAULT),
            rel_path=_rel, language="csharp",
            on_attempt=(lambda a, m, _d=domain: on_step(f"[{_d}] Fixing Repository — attempt {a}/{m}…")) if on_step else None,
        )
        files[_rel] = _content
        if on_validation:
            on_validation(_result, _attempts)
        return True
    except Exception as exc:
        files[f"{base}/Repositories/{domain}Repository.cs"] = f"// LLM generation failed: {exc}\n"
        return False


# Function: _llm_domain_csharp
def _llm_domain_csharp(
    files: "Dict[str, str]",
    domain: str,
    root_ns: str,
    domain_tables: "List[str]",
    antipatterns: "List[str]",
    context: str,
    prod_rules: str,
    source_sec: str,
    model: str,
    system: str,
    tables: "List[str]",
    target: dict,
    on_step: "Optional[Callable[[str], None]]",
    generate: "Callable[..., str]",
    on_validation: "Optional[Callable[[object, int], None]]" = None,
) -> None:
    """Add .NET 8 C# Minimal API domain files to *files* (mutates in-place)."""
    from ..scaffolds.csharp import _gen_service, _gen_service_scaffold
    base = f"ModernizedApp/Services/{domain}Service"
    is_dapper = "dapper" in (target.get("db_tech") or "").lower()
    db_target = target.get("db_target", "mssql")
    data_access_using = "System.Data, Dapper" if is_dapper else "EF Core"
    data_access_rule  = (
        f"- Repository pattern via I{domain}Repository injected via DI "
        "(Dapper over IDbConnection — parameterized SQL, no DbContext/EF Core)"
        if is_dapper else
        f"- Use EF Core DbContext injected via DI (not new'd up)\n"
        f"- Repository pattern via I{domain}Repository injected via DI"
    )

    # Tracks whether each LLM call actually succeeded, so the caller can tell
    # a complete, self-consistent LLM-generated backend (all three) from a
    # partial one (see end of function).
    endpoints_ok = _gen_csharp_endpoints(
        files, base, domain, root_ns, context, prod_rules, source_sec,
        data_access_using, data_access_rule, domain_tables, antipatterns,
        target, model, system, on_step, on_validation,
    )
    service_ok = _gen_csharp_service(files, base, domain, root_ns, context, prod_rules, model, system, on_step, on_validation)
    repo_ok = _gen_csharp_repository(files, base, domain, root_ns, context, prod_rules, is_dapper, model, system, on_step, on_validation)

    # Project scaffolding: either wire up the LLM-generated Endpoints/Service/
    # Repository trio (all three succeeded), or fall back to the fully
    # self-consistent deterministic implementation. Never both — the
    # deterministic templates use the SAME type names as the LLM prompts
    # (I{domain}Service / {domain}ServiceImpl in the same namespace), so
    # calling _gen_service() unconditionally after the LLM path succeeded
    # used to emit a second, colliding definition of those types — a compile
    # error, not just redundant clutter.
    if endpoints_ok and service_ok and repo_ok:
        _gen_service_scaffold(files, root_ns, domain, is_dapper=is_dapper, db_target=db_target)
    else:
        for _path in (
            f"{base}/Endpoints/{domain}Endpoints.cs",
            f"{base}/Services/{domain}ServiceImpl.cs",
            f"{base}/Repositories/{domain}Repository.cs",
        ):
            files.pop(_path, None)
        _gen_service(files, root_ns, domain, tables, is_dapper=is_dapper, db_target=db_target)
