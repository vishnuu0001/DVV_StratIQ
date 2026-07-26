# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Shared cosine-similarity helper for the dedup (dedupe.py) and conflict-detection
#   (conflicts.py) passes — both compare requirement-statement embeddings in plain
#   Python rather than pgvector, since the working set for a single project's DRAFT
#   requirements is small enough (hundreds, not millions) that an in-process O(n^2)
#   comparison is simpler than round-tripping through the database per pair.
# Date: 2026-07-24
# ---------------------------------------------------------------------------
from __future__ import annotations


# Function: cosine_similarity
def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)
