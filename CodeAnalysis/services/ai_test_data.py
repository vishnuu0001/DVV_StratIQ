# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: LLM-powered test-data generation advisor.
# Date: 2026-03-31
# ---------------------------------------------------------------------------
"""
services/ai_test_data.py
-------------------------
LLM-powered test-data generation advisor.

Scans the repository for entity/model/DTO classes, database schemas,
and produces representative test data sets plus testing strategy.
"""
from __future__ import annotations

import logging
import os
import re
from pathlib import Path

from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)

_SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    "dist", "build", "target", "vendor",
}

_SYSTEM = """\
You are a QA architect and test-data specialist. Given entity/model definitions
from source code, you generate realistic test data sets and testing strategies.
Always return valid JSON and nothing else."""

_PROMPT_TMPL = """\
Generate a test-data strategy for repository "{repo_name}".

ENTITY / MODEL DEFINITIONS found in code:
{entities}

DATABASE / ORM ARTIFACTS:
{orm_artifacts}

LANGUAGES: {languages}
TOTAL SLOC: {sloc}

Produce a JSON report:
{{
  "summary": "<approach to test data for this system>",
  "entities": [
    {{
      "name": "<entity name>",
      "fields": [
        {{
          "name": "<field name>",
          "type": "<inferred data type>",
          "sample_values": ["<3 representative sample values>"],
          "constraints": "<any inferred constraints e.g. NOT NULL, positive integer>"
        }}
      ],
      "sample_records": [
        {{ "<field>": "<value>", "...": "..." }}
      ]
    }}
  ],
  "test_scenarios": [
    {{
      "name": "<scenario name>",
      "type": "<happy-path|edge-case|negative|performance|security>",
      "description": "<what is being tested>",
      "test_data": "<description of the data needed>"
    }}
  ],
  "data_generation_tools": ["<recommended tools like Faker, Factory Boy, etc.>"],
  "seeding_strategy": "<how to load test data into the application for CI/CD>"
}}

Return ONLY the JSON."""


_ENTITY_PAT = re.compile(
    r"(?:class\s+(\w+)|@Entity|@Table|@Document|data class\s+(\w+)|struct\s+(\w+))", re.I
)
_FIELD_PAT  = re.compile(r"(?:val|var|private|public|protected|let|const)?\s+(\w+)\s*[:=]\s*(\w[\w<>\[\]]*)")
_ORM_PAT    = re.compile(r"(@Column|@Id|@ManyToOne|@OneToMany|@Field|models\.CharField|models\.\w+Field)", re.I)


# Function: _is_model_path
def _is_model_path(rel_lower: str) -> bool:
    return any(k in rel_lower for k in ["model", "entity", "dto", "domain", "schema", "record"])


# Function: _scan_file_for_entities
def _scan_file_for_entities(fpath: Path, root: Path, entity_lines: list, orm_lines: list) -> int:
    """Scan a single file for entity/ORM lines; returns chars added."""
    try:
        rel_parts = fpath.relative_to(root).parts
    except ValueError:
        return 0

    rel_lower = "/".join(rel_parts).lower()
    is_model = _is_model_path(rel_lower)

    try:
        text = fpath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return 0

    rel_str = "/".join(rel_parts)
    added_chars = 0
    for line in text.splitlines():
        if _ENTITY_PAT.search(line) or is_model:
            entry = f"  [{rel_str}] {line.strip()[:100]}"
            entity_lines.append(entry)
            added_chars += len(entry)
        if _ORM_PAT.search(line):
            orm_lines.append(f"  [{rel_str}] {line.strip()[:100]}")
    return added_chars


# Function: _collect_entities
def _collect_entities(repo_path: str, max_chars: int = 3000) -> tuple[str, str]:
    """
    Scan for class/model/entity definitions and ORM artifacts.
    Returns (entities_txt, orm_txt).
    """
    root = Path(repo_path)

    entity_lines: list[str] = []
    orm_lines:    list[str] = []
    chars = 0

    for dirpath, dirnames, filenames in os.walk(str(root)):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        if chars >= max_chars:
            break
        dir_path = Path(dirpath)
        for fname in filenames:
            if chars >= max_chars:
                break
            fpath = dir_path / fname
            if fpath.suffix.lower() not in {".py", ".java", ".cs", ".kt", ".ts", ".js"}:
                continue
            chars += _scan_file_for_entities(fpath, root, entity_lines, orm_lines)

    return (
        "\n".join(entity_lines[:150]) or "  (no entity definitions found)",
        "\n".join(orm_lines[:80])     or "  (no ORM annotations found)",
    )


# Function: analyse_test_data
def analyse_test_data(
    analysis_result: dict,
    repo_path: str,
    model: str | None = None,
    client: OllamaClient | None = None,
) -> dict:
    client = client or OllamaClient()

    entities, orm_artifacts = _collect_entities(repo_path)

    prompt = _PROMPT_TMPL.format(
        repo_name    = analysis_result.get("repo_name", "unknown"),
        entities     = entities,
        orm_artifacts = orm_artifacts,
        languages    = ", ".join(analysis_result.get("languages_detected", ["unknown"])),
        sloc         = analysis_result.get("total_sloc", 0),
    )

    try:
        result = client.generate_json(prompt, model=model, system=_SYSTEM, timeout=480)
        result["_model_used"] = model or client.best_available_model()
        return result
    except Exception as exc:
        logger.error("ai_test_data failed: %s", exc)
        return {"error": str(exc), "summary": "AI analysis unavailable."}
