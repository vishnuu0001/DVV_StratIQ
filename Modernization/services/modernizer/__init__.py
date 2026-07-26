# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: services/modernizer.py
# Date: 2025-07-12
# ---------------------------------------------------------------------------
"""
services/modernizer.py
Code generation engine — transforms legacy analysis into modernized .NET 8 MES output.

Output structure (returned as dict[filename → content]):
  ModernizedApp/
    README.md                                    — migration guide
    Database/
      schema_mssql.sql                           — MS SQL equivalent schema
      migration_notes.md                         — Oracle → MSSQL migration notes
    Services/
      <Domain>Service/
        <Domain>Service.csproj                   — .NET 8 microservice project
        Program.cs                               — Minimal API entry point
        Models/<Entity>.cs                       — Domain models
        Repositories/I<Entity>Repository.cs      — Repository interface
        Repositories/<Entity>Repository.cs       — EF Core implementation
        Services/I<Domain>Service.cs
        Services/<Domain>Service.cs
        Controllers/<Domain>Controller.cs        — Minimal API route group
    Frontend/
      <Domain>/
        <Domain>.razor                           — Blazor component
        <Domain>.js                              — JavaScript interop module
        Shared/
          ApiClient.js                           — Fetch-based API client module
"""
from __future__ import annotations

from .target_config import TARGET_STACKS
from .conversion_pipeline import modernize_project
from .prompt_pipeline import generate_from_prompt, _unresolved_requirement_placeholders
from .domain_generators.stack_signals import _detect_domain_requirements
from .validation_orchestration import _generate_validated, _single_file_extension

__all__ = [
    "TARGET_STACKS",
    "modernize_project",
    "generate_from_prompt",
    "_unresolved_requirement_placeholders",
    "_detect_domain_requirements",
    "_generate_validated",
    "_single_file_extension",
]
