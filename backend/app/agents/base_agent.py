"""Base agent class for specialist agents in the multi-agent system.

Provides:
- Dual execution mode: LLM-driven (Groq) or deterministic fallback
- Automatic lineage recording for every tool invocation
- Timeout and retry wrappers for tool calls
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from langchain_core.tools import BaseTool

from app.agents.shared_memory import EpistemicMemory
from app.domain.evidence.lineage_writer import LineageWriter
from app.domain.evidence.repository import LineageRepository

logger = logging.getLogger(__name__)

_LINEAGE_REPOSITORY = LineageRepository()
_LINEAGE_WRITER = LineageWriter(_LINEAGE_REPOSITORY)


def _load_env(key: str) -> str | None:
    value = os.getenv(key)
    if value:
        return value
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return None
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() == key:
            cleaned = v.strip().strip('"').strip("'")
            if cleaned:
                return cleaned
    return None


class BaseSpecialistAgent:
    """Base class for specialist agents."""

    name: str = "base"
    role_description: str = "A specialist agent."
    tools: list[BaseTool] = []

    def __init__(self, timeout_seconds: int = 60) -> None:
        self.timeout_seconds = timeout_seconds
        self._tool_call_index = 0

    def _invoke_tool(
        self,
        tool_instance: BaseTool,
        args: dict[str, Any],
        memory: EpistemicMemory,
    ) -> Any:
        """Invoke a single tool with lineage recording."""
        self._tool_call_index += 1
        tool_name = tool_instance.name

        logger.info("Agent %s invoking tool %s with args %s", self.name, tool_name, list(args.keys()))

        result = tool_instance.invoke(args)

        # Write lineage record for this tool invocation
        try:
            _LINEAGE_WRITER.write_lineage(
                run_id=memory.run_id,
                repository_id=memory.repository_id,
                artifacts=[
                    {
                        "artifact_type": "tool_output",
                        "artifact_id": f"{tool_name}:{self._tool_call_index}",
                        "source_provider": self.name,
                        "source_locator": f"{tool_name}({','.join(args.keys())})",
                        "claim_ref": f"{memory.run_id}:{self.name}:{tool_name}",
                    }
                ],
            )
        except Exception as exc:
            logger.warning("Lineage write failed for %s: %s", tool_name, exc)

        return result

    def _get_tool(self, name: str) -> BaseTool | None:
        """Find a tool by name."""
        for t in self.tools:
            if t.name == name:
                return t
        return None

    def execute_deterministic(self, memory: EpistemicMemory) -> dict[str, Any]:
        """Execute agent in deterministic mode (no LLM). Override in subclasses."""
        raise NotImplementedError("Subclasses must implement execute_deterministic")

    def execute(self, memory: EpistemicMemory, task: str = "") -> dict[str, Any]:
        """Execute the agent. Tries LLM mode first, falls back to deterministic."""
        groq_key = _load_env("GROQ_API_KEY")

        if groq_key:
            try:
                return self._execute_with_llm(memory, task, groq_key)
            except Exception as exc:
                logger.warning(
                    "Agent %s LLM mode failed (%s), falling back to deterministic",
                    self.name,
                    exc,
                )

        return self.execute_deterministic(memory)

    def _execute_with_llm(self, memory: EpistemicMemory, task: str, api_key: str) -> dict[str, Any]:
        """Execute agent using Groq LLM for reasoning about tool usage."""
        try:
            from langchain_groq import ChatGroq
        except ImportError:
            logger.info("langchain-groq not available, using deterministic mode")
            return self.execute_deterministic(memory)

        model_name = _load_env("GROQ_MODEL") or "llama-3.3-70b-versatile"
        llm = ChatGroq(
            api_key=api_key,
            model=model_name,
            temperature=0.1,
            max_tokens=1024,
        )

        if not self.tools:
            return self.execute_deterministic(memory)

        llm_with_tools = llm.bind_tools(self.tools)

        memory_snapshot = {k: _summarize_value(memory.read(k)) for k in memory.keys()}

        messages = [
            {"role": "system", "content": self.role_description},
            {
                "role": "user",
                "content": (
                    f"Task: {task}\n\n"
                    f"Current shared memory keys: {list(memory_snapshot.keys())}\n"
                    f"Memory summary: {memory_snapshot}\n\n"
                    f"Available tools: {[t.name for t in self.tools]}\n"
                    "Execute the necessary tools to complete your task. "
                    "Return a brief summary of what you accomplished."
                ),
            },
        ]

        response = llm_with_tools.invoke(messages)

        # Process tool calls from LLM response
        tool_calls = getattr(response, "tool_calls", [])
        if tool_calls:
            for tc in tool_calls:
                tool_instance = self._get_tool(tc["name"])
                if tool_instance:
                    result = self._invoke_tool(tool_instance, tc["args"], memory)
                    self._process_tool_result(tc["name"], result, memory)

        # If no tool calls, LLM decided no tools needed — run deterministic
        if not tool_calls:
            return self.execute_deterministic(memory)

        return {"status": "complete", "agent": self.name, "mode": "llm", "tool_calls": len(tool_calls)}

    def _process_tool_result(self, tool_name: str, result: Any, memory: EpistemicMemory) -> None:
        """Process a tool result and write to shared memory. Override in subclasses."""
        pass


def _summarize_value(value: Any, max_length: int = 200) -> str:
    """Produce a short summary of a memory value for LLM context."""
    if value is None:
        return "null"
    if isinstance(value, list):
        return f"list[{len(value)} items]"
    if isinstance(value, dict):
        return f"dict[keys={list(value.keys())[:5]}]"
    text = str(value)
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text
