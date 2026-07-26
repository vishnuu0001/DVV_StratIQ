# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §4.3: embed via Ollama (nomic-embed-text locally; configurable per P6/EMBEDDING_PROVIDER
# Date: 2026-06-18
# ---------------------------------------------------------------------------
"""§4.3: embed via Ollama (nomic-embed-text locally; configurable per P6/EMBEDDING_PROVIDER
in spirit, though only Ollama is wired up in this deployment)."""
from __future__ import annotations

from traceforge.config import OLLAMA_EMBED_BATCH_SIZE
from traceforge.llm.ollama import OllamaProvider

_provider = OllamaProvider()


# Function: embed_texts
async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    # Bound request size so large supporting documents do not create a single huge
    # Ollama payload or monopolise the shared GPU for the whole ingestion run.
    embeddings: list[list[float]] = []
    batch_size = max(1, OLLAMA_EMBED_BATCH_SIZE)
    for offset in range(0, len(texts), batch_size):
        batch = texts[offset : offset + batch_size]
        batch_embeddings = await _provider.embed(batch)
        if len(batch_embeddings) != len(batch):
            raise RuntimeError(
                f"Ollama returned {len(batch_embeddings)} embeddings for {len(batch)} chunks"
            )
        embeddings.extend(batch_embeddings)
    return embeddings
