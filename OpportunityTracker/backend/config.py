# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: OpportunityTracker — backend (config.py)
# Date: 2025-10-09
# ---------------------------------------------------------------------------
import os

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")
OLLAMA_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
HARMONIZATION_DOCX_PATH = os.getenv("HARMONIZATION_DOCX_PATH", os.path.join(_DATA_DIR, "Harmonization Services.docx"))
MODERNIZATION_DOCX_PATH = os.getenv("MODERNIZATION_DOCX_PATH", os.path.join(_DATA_DIR, "Modernization Services.docx"))
