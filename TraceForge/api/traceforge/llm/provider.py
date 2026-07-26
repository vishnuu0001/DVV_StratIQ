# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: P6: 'The LLM is swappable. All model calls go through a single LLMProvider
# Date: 2025-08-01
# ---------------------------------------------------------------------------
"""P6: 'The LLM is swappable. All model calls go through a single LLMProvider
interface.' Only OllamaProvider is implemented in this deployment (no Anthropic /
Azure OpenAI — see Requirements.MD's deployment-constraint note at the top), but every
agent codes against this ABC so a second provider is a config change, not a rewrite."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from dataclasses import dataclass


@dataclass
class LLMResponse:
    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int


class LLMProvider(ABC):
    # Function: generate
    @abstractmethod
    async def generate(
        self, system: str, user: str, *, temperature: float, max_tokens: int,
        json_mode: bool = True, progress: Callable[[int], Awaitable[None]] | None = None,
    ) -> LLMResponse:
        """Structured-JSON generation by default (spec §5: 'Output is structured JSON
        only') — callers validate the returned text against a Pydantic schema themselves.
        Pass json_mode=False for plain-prose callers (e.g. doc_author's section prose):
        forcing JSON-grammar-constrained output onto a prompt that asks for prose
        produces garbled/wrapped text, not the requested paragraphs."""

    # Function: embed
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        ...
