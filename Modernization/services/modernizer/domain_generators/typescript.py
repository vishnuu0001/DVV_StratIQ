# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — services/modernizer/domain_generators (typescript.py)
# Date: 2026-02-26
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



# Function: _llm_domain_typescript
def _llm_domain_typescript(
    files: "Dict[str, str]",
    domain: str,
    root_ns: str,
    domain_tables: "List[str]",
    context: str,
    prod_rules: str,
    source_sec: str,
    guide_sec: str,
    model: str,
    system: str,
    fw: str,
    target: dict,
    on_step: "Optional[Callable[[str], None]]",
    generate: "Callable[..., str]",
    on_validation: "Optional[Callable[[object, int], None]]" = None,
) -> set:
    """Add TypeScript/React domain files to *files* (mutates in-place)."""
    from .._shared import _TOKENS_COMPONENT, _TOKENS_MIGRATION, _adaptive_num_ctx
    from ..scaffolds.typescript import _gen_ts_component
    from ..validation_orchestration import _generate_validated
    base = f"ModernizedApp/src/components/{domain}"
    generated_paths = set()

    # Full CRUD page component
    try:
        if on_step:
            on_step(f"[{domain}] Generating UI component…")
        prompt = (
            f"{context}\n{prod_rules}{source_sec}{guide_sec}\n\n"
            f"Generate a COMPLETE, PRODUCTION-READY {fw} component named {domain}Page "
            f"that fully manages {domain} data with ALL of the following implemented:\n"
            f"- TypeScript strict mode: all types defined (interface {domain}Item, CreateRequest, UpdateRequest)\n"
            f"- useEffect to fetch paginated data from GET /api/{domain.lower()}?page=0&size=20\n"
            f"- Full list table with sortable columns, pagination controls (prev/next, page info)\n"
            f"- Search/filter input that debounces (300 ms) and queries ?search=term\n"
            f"- Loading skeleton state (show spinner while fetching)\n"
            f"- Error state with retry button\n"
            f"- Create modal with controlled form inputs, submit calls POST /api/{domain.lower()}\n"
            f"- Edit modal pre-populated with existing row data, submit calls PUT /api/{domain.lower()}/{{id}}\n"
            f"- Delete confirmation dialog, calls DELETE /api/{domain.lower()}/{{id}}\n"
            f"- Toast/notification feedback on create/update/delete success and error\n"
            f"- useCallback / useMemo where appropriate to prevent unnecessary re-renders\n"
            f"- All async operations wrapped in try/catch; errors shown inline\n"
            f"- Tailwind CSS classes for styling\n"
            f"Source tables: {', '.join(domain_tables)}\n"
            f"Output ONLY the complete TypeScript .tsx file. No markdown fences."
        )
        ext = ".tsx" if fw in ("React",) else ".ts"
        _rel = f"{base}/{domain}Page{ext}"
        _content, _result, _attempts = _generate_validated(
            prompt, model=model, system=system, max_tokens=_TOKENS_COMPONENT,
            num_ctx=_adaptive_num_ctx(len(prompt) + len(system), _TOKENS_COMPONENT),
            rel_path=_rel, language="typescript",
            on_attempt=(lambda a, m, _d=domain: on_step(f"[{_d}] Fixing UI component — attempt {a}/{m}…")) if on_step else None,
        )
        files[_rel] = _content
        if on_validation:
            on_validation(_result, _attempts)
        if _result.passed:
            generated_paths.add(_rel)
    except Exception as exc:
        ext = ".tsx"
        files[f"{base}/{domain}Page{ext}"] = f"// LLM generation failed: {exc}\n"

    # API service layer
    try:
        if on_step:
            on_step(f"[{domain}] Generating API service layer…")
        prompt = (
            f"{context}\n{prod_rules}{source_sec}\n\n"
            f"Generate a COMPLETE TypeScript API service module for the {domain} domain:\n"
            f"- Typed API client using native fetch\n"
            f"- getAll(params: {{page?:number, size?:number, search?:string}}): Promise<PageResult<{domain}Item>>\n"
            f"- getById(id: number): Promise<{domain}Item>\n"
            f"- create(data: Create{domain}Request): Promise<{domain}Item>\n"
            f"- update(id: number, data: Update{domain}Request): Promise<{domain}Item>\n"
            f"- remove(id: number): Promise<void>\n"
            f"- All interfaces ({domain}Item, Create{domain}Request, Update{domain}Request, PageResult<T>) defined\n"
            f"- Throw descriptive Error on non-2xx responses with status code and body\n"
            f"- API_BASE from import.meta.env.VITE_API_URL with fallback to '/api'\n"
            f"- export all interfaces at bottom of file\n"
            f"Output ONLY the TypeScript file. No markdown fences."
        )
        _rel = f"{base}/{domain}Service.ts"
        _content, _result, _attempts = _generate_validated(
            prompt, model=model, system=system, max_tokens=_TOKENS_MIGRATION,
            num_ctx=_adaptive_num_ctx(len(prompt) + len(system), _TOKENS_MIGRATION),
            rel_path=_rel, language="typescript",
            on_attempt=(lambda a, m, _d=domain: on_step(f"[{_d}] Fixing API service layer — attempt {a}/{m}…")) if on_step else None,
        )
        files[_rel] = _content
        if on_validation:
            on_validation(_result, _attempts)
        if _result.passed:
            generated_paths.add(_rel)
    except Exception as exc:
        _gen_ts_component(files, root_ns, domain, target.get("name", ""))
    return generated_paths
