# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Base specialist agent interface and response model.
# Date: 2025-11-17
# ---------------------------------------------------------------------------
"""Base specialist agent interface and response model."""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Literal

import structlog
from pydantic import BaseModel, Field

from agents.config import get_settings
from agents.llm.ollama_client import chat as ollama_chat

log = structlog.get_logger(__name__)


class SpecialistResponse(BaseModel):
    agent_name: str
    status: Literal["completed", "blocked", "scope_violation", "failed"]
    actions_taken: list[dict] = Field(default_factory=list)
    findings: str = ""
    blockers: list[str] = Field(default_factory=list)
    recommendation: str = ""
    confidence: float = 0.0
    requires_human_approval: bool = False
    irreversible_actions: list[str] = Field(default_factory=list)
    duration_ms: int = 0
    token_input: int = 0
    token_output: int = 0
    cost_usd: float = 0.0


class BaseSpecialist(ABC):
    name: str = "base"
    role: str = "base"
    domain: str = "general"
    tools: list[str] = []

    # Function: _check_scope
    def _check_scope(self, brief: dict) -> bool:
        """Return True if this brief is in this specialist's domain."""
        disruption_type = brief.get("disruption_type", "")
        return True  # Subclasses can override

    # Function: run
    async def run(self, brief: dict) -> SpecialistResponse:
        """Execute the specialist on a brief."""
        start = time.monotonic()
        settings = get_settings()

        if not self._in_scope(brief):
            return SpecialistResponse(
                agent_name=self.name,
                status="scope_violation",
                findings=f"Brief is out of scope for {self.role} agent (domain: {self.domain})",
                recommendation="Delegate to appropriate specialist",
                confidence=1.0,
                duration_ms=0,
            )

        try:
            if settings.use_mock:
                resp = await self._mock_run(brief)
            else:
                resp = await self._llm_run(brief)
        except Exception as exc:
            log.error("specialist_failed", agent=self.name, error=str(exc))
            resp = SpecialistResponse(
                agent_name=self.name,
                status="failed",
                findings=f"Specialist {self.name} encountered an error: {exc}",
                recommendation="Manual investigation required",
                confidence=0.0,
                blockers=[str(exc)],
            )

        elapsed_ms = int((time.monotonic() - start) * 1000)
        resp.duration_ms = elapsed_ms
        log.info(
            "specialist_completed",
            agent=self.name,
            status=resp.status,
            duration_ms=elapsed_ms,
            confidence=resp.confidence,
        )
        return resp

    # Function: _in_scope
    def _in_scope(self, brief: dict) -> bool:
        """Default scope check — subclasses override to be restrictive."""
        return True

    # Function: _mock_run
    @abstractmethod
    async def _mock_run(self, brief: dict) -> SpecialistResponse:
        """Return a deterministic mock response."""

    # Function: _llm_run
    async def _llm_run(self, brief: dict) -> SpecialistResponse:
        """Call the local Ollama model to run this specialist. Falls back to mock on error."""
        try:
            import json

            settings = get_settings()

            prompt_path = _prompt_file()
            try:
                with open(prompt_path) as f:
                    system_prompt = f.read()
            except FileNotFoundError:
                system_prompt = (
                    f"You are the {self.role} agent. Scope: {self.domain} only.\n"
                    f"Tools available: {', '.join(self.tools)}\n"
                    "Respond with JSON matching SpecialistResponse schema."
                )

            system_prompt = (
                system_prompt
                .replace("{role_name}", self.role)
                .replace("{domain}", self.domain)
                .replace("{tool_list}", ", ".join(self.tools))
            )

            user_content = f"Brief:\n{json.dumps(brief, indent=2)}"

            result = await ollama_chat(
                base_url=settings.ollama_base_url,
                model=settings.specialist_model,
                system=system_prompt,
                user=user_content,
                max_tokens=2048,
            )

            import re
            match = re.search(r"\{.*\}", result.text, re.DOTALL)
            if match:
                data = json.loads(match.group())
                return SpecialistResponse(
                    agent_name=self.name,
                    status=data.get("status", "completed"),
                    actions_taken=data.get("actions_taken", []),
                    findings=data.get("findings", ""),
                    blockers=data.get("blockers", []),
                    recommendation=data.get("recommendation", ""),
                    confidence=float(data.get("confidence", 0.8)),
                    requires_human_approval=bool(data.get("requires_human_approval", False)),
                    irreversible_actions=data.get("irreversible_actions", []),
                    token_input=result.prompt_tokens,
                    token_output=result.completion_tokens,
                    cost_usd=0.0,
                )
        except Exception as exc:
            log.warning("llm_specialist_failed", agent=self.name, error=str(exc))

        return await self._mock_run(brief)


# Function: _prompt_file
def _prompt_file() -> str:
    import os
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    return os.path.join(base, "prompts", "specialist.md")
