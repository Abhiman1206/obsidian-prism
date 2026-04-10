"""Data Mining Agent — retrieves repository data from GitHub/GitLab/PyDriller.

PRD Role: Specializes in data retrieval. Equipped with the GitHub/GitLab API and
PyDriller tools, it mines commit histories, deployment frequencies, and historical
bug patterns.
"""

from __future__ import annotations

from typing import Any

from app.agents.base_agent import BaseSpecialistAgent
from app.agents.shared_memory import EpistemicMemory
from app.domain.ingestion.normalization import normalize_provider_payload
from app.domain.ingestion.provider_signals import extract_cadence_signals
from app.tools.github_tool import github_fetch_commits, github_fetch_signals
from app.tools.gitlab_tool import gitlab_fetch_commits, gitlab_fetch_signals
from app.tools.pydriller_tool import pydriller_mine_repository


class DataMiningAgent(BaseSpecialistAgent):
    name = "data_mining_agent"
    role_description = (
        "You are a Data Mining specialist agent. Your job is to retrieve commit history, "
        "deployment frequency, issue tracking data, and contributor churn from the target "
        "repository. Use the appropriate provider tool (GitHub or GitLab) to fetch commits "
        "and operational signals. Write all results to shared memory for downstream agents."
    )
    tools = [
        github_fetch_commits,
        github_fetch_signals,
        gitlab_fetch_commits,
        gitlab_fetch_signals,
        pydriller_mine_repository,
    ]

    def execute_deterministic(self, memory: EpistemicMemory) -> dict[str, Any]:
        """Deterministic execution: fetch commits and signals from provider."""
        provider = memory.read("provider", "github")
        repository = memory.read("repository", "")

        # Fetch commits
        if provider == "github":
            commit_tool = self._get_tool("github_fetch_commits")
            signal_tool = self._get_tool("github_fetch_signals")
        elif provider == "gitlab":
            commit_tool = self._get_tool("gitlab_fetch_commits")
            signal_tool = self._get_tool("gitlab_fetch_signals")
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        commit_result = self._invoke_tool(commit_tool, {"repository": repository}, memory)
        raw_commits = commit_result.get("commits", []) if isinstance(commit_result, dict) else []

        # Fetch operational signals
        signal_result = self._invoke_tool(signal_tool, {"repository": repository}, memory)
        cadence_raw = signal_result if isinstance(signal_result, dict) else {}

        # Normalize to canonical format
        canonical = normalize_provider_payload(
            repository_id=memory.repository_id,
            provider=provider,
            commits=raw_commits,
        )
        cadence = extract_cadence_signals(cadence_raw)

        # Write to shared memory
        memory.write(self.name, "raw_commits", raw_commits)
        memory.write(self.name, "canonical_payload", canonical)
        memory.write(self.name, "cadence_signals", cadence)
        memory.write(self.name, "churn", canonical.get("churn", []))

        return {
            "status": "complete",
            "agent": self.name,
            "mode": "deterministic",
            "commit_count": len(raw_commits),
            "has_signals": bool(cadence_raw),
        }

    def _process_tool_result(self, tool_name: str, result: Any, memory: EpistemicMemory) -> None:
        """Process tool results and write to shared memory when in LLM mode."""
        if "fetch_commits" in tool_name and isinstance(result, dict):
            raw_commits = result.get("commits", [])
            memory.write(self.name, "raw_commits", raw_commits)

            canonical = normalize_provider_payload(
                repository_id=memory.repository_id,
                provider=memory.read("provider", "github"),
                commits=raw_commits,
            )
            memory.write(self.name, "canonical_payload", canonical)
            memory.write(self.name, "churn", canonical.get("churn", []))

        elif "fetch_signals" in tool_name and isinstance(result, dict):
            cadence = extract_cadence_signals(result)
            memory.write(self.name, "cadence_signals", cadence)
