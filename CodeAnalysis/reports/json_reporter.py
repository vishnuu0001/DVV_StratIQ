# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Serialises a complete AnalysisResult to a structured JSON file.
# Date: 2026-06-25
# ---------------------------------------------------------------------------
"""
json_reporter.py
----------------
Serialises a complete AnalysisResult to a structured JSON file.
"""
from __future__ import annotations

import dataclasses
import json
from datetime import datetime
from pathlib import Path
from typing import Any


# Function: _default
def _default(obj: Any) -> Any:
    """Custom JSON serialiser for dataclasses, Path, sets, etc."""
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dataclasses.asdict(obj)
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, set):
        return sorted(obj)
    raise TypeError(f"Not serialisable: {type(obj)}")


# Function: write_json
def write_json(result, output_dir: Path) -> Path:
    """
    Write the full analysis result as JSON.

    Parameters
    ----------
    result      : AnalysisResult  (from core.analyzer)
    output_dir  : directory to write the file into

    Returns the path to the written file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = result.repo_name.replace("/", "_").replace("\\", "_")
    ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path  = output_dir / f"{safe_name}_{ts}_report.json"

    payload = {
        "meta": {
            "tool":       "CodeAnalysis",
            "version":    "1.0.0",
            "generated":  datetime.now().isoformat(),
            "repo":       result.repo_name,
            "repo_url":   result.repo_url,
        },
        "summary": {
            "total_sloc":        result.total_sloc,
            "languages_detected": result.languages_detected,
            "file_count":        result.total_files,
        },
        "software_health":     result.health,
        "technical_debt":      result.debt,
        "cloud_maturity":      result.cloud,
        "open_source_safety":  result.oss,
        "business_impact":     result.impact,
        "language_reports":    result.language_reports,
    }

    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, default=_default)

    return out_path
