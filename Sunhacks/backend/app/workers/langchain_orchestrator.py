"""LangChain Multi-Agent Orchestrator.

Replaces the previous monolithic function chain with a true multi-agent
supervisor architecture using:
- Specialist agents with LangChain tool integration
- Shared epistemic memory for inter-agent communication
- SQLite-backed persistence for all results
- Automatic lineage recording for causal traceability
- Groq LLM for agent reasoning with deterministic fallback
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from app.agents.shared_memory import EpistemicMemory
from app.agents.supervisor import SupervisorAgent
from app.api.schemas.run import RunStatus
from app.domain.business.repository import EXECUTIVE_REPORT_REPOSITORY
from app.domain.health.repository import HEALTH_SCORE_REPOSITORY
from app.domain.risk.repository import RISK_FORECAST_REPOSITORY

logger = logging.getLogger(__name__)


def _load_env_var(key: str) -> str | None:
    value = os.getenv(key)
    if value:
        return value
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return None
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, raw_value = line.split("=", 1)
        if k.strip() != key:
            continue
        cleaned = raw_value.strip().strip('"').strip("'")
        if cleaned:
            return cleaned
    return None


def get_orchestration_engine() -> str:
    """Return the orchestration engine identifier."""
    return "langchain-multi-agent"


def get_runtime_credentials_status() -> dict[str, bool]:
    """Return the current runtime credential configuration status."""
    return {
        "groq_configured": bool(_load_env_var("GROQ_API_KEY")),
        "github_configured": bool(_load_env_var("GITHUB_API_KEY")),
        "gitlab_configured": bool(_load_env_var("GITLAB_API_KEY")),
    }


def _repository_slug(repository_id: str) -> str:
    """Derive a repository slug from the repository ID."""
    if "/" in repository_id:
        return repository_id
    suffix = repository_id.removeprefix("repo-")
    parts = [part for part in suffix.split("-") if part]
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    if parts:
        return f"acme/{parts[0]}"
    return "acme/platform"


def _persist_results(memory: EpistemicMemory) -> None:
    """Persist all agent results from shared memory to SQLite repositories."""
    # Persist health scores
    health_rows = memory.read("health_rows", [])
    if health_rows:
        try:
            HEALTH_SCORE_REPOSITORY.add_many(health_rows)
            logger.info("Persisted %d health scores", len(health_rows))
        except Exception as exc:
            logger.error("Failed to persist health scores: %s", exc)

    # Persist risk forecasts
    forecasts = memory.read("forecasts", [])
    if forecasts:
        try:
            RISK_FORECAST_REPOSITORY.add_many(forecasts)
            logger.info("Persisted %d risk forecasts", len(forecasts))
        except Exception as exc:
            logger.error("Failed to persist risk forecasts: %s", exc)

    # Persist executive report (with technical report data embedded)
    report = memory.read("report")
    if report and isinstance(report, dict):
        # Attach technical report data so the PDF endpoints can access it
        technical_report = memory.read("technical_report")
        if technical_report and isinstance(technical_report, dict):
            report["technical_report"] = technical_report

        try:
            EXECUTIVE_REPORT_REPOSITORY.add(report)
            logger.info("Persisted executive report %s", report.get("report_id", ""))
        except Exception as exc:
            logger.error("Failed to persist executive report: %s", exc)


def orchestrate_run(
    run_id: str,
    repository_id: str,
    provider: str,
    branch: str | None,
    repository_slug: str | None = None,
    provider_token: str | None = None,
) -> dict[str, object]:
    """Execute a full analysis run using the multi-agent supervisor architecture.

    Flow:
    1. Create shared epistemic memory for this run
    2. Initialize provider and repository context
    3. Delegate to SupervisorAgent which orchestrates:
       DataMiningAgent → HealthAnalystAgent → RiskPredictorAgent → ReportWriterAgent
    4. Persist all results to SQLite
    5. Return status
    """
    repository = repository_slug or _repository_slug(repository_id)

    # Create shared memory and seed with run context
    memory = EpistemicMemory(run_id=run_id, repository_id=repository_id)
    memory.write("supervisor", "provider", provider)
    memory.write("supervisor", "repository", repository)
    memory.write("supervisor", "branch", branch)
    memory.write("supervisor", "repository_id", repository_id)
    if provider_token:
        memory.write("supervisor", "provider_token", provider_token)

    try:
        # Create and run the supervisor
        supervisor = SupervisorAgent()
        result = supervisor.run(memory)

        # Persist results from memory to repositories
        _persist_results(memory)

        if result["status"] == "failed":
            stage_errors = [
                s.get("error", "unknown")
                for s in result.get("stages", [])
                if s.get("status") == "failed"
            ]
            return {
                "status": RunStatus.FAILED,
                "message": f"Run failed: {'; '.join(stage_errors)}",
            }

        creds = get_runtime_credentials_status()
        groq_status = "groq-enabled" if creds["groq_configured"] else "groq-missing"
        degraded = result.get("degraded_stages", [])
        degraded_info = f" (degraded: {', '.join(degraded)})" if degraded else ""

        stage_summaries = []
        for s in result.get("stages", []):
            agent = s.get("agent", s.get("stage", ""))
            mode = s.get("mode", "unknown")
            stage_summaries.append(f"{agent}[{mode}]")

        return {
            "status": RunStatus.SUCCEEDED,
            "message": (
                f"Multi-agent run completed ({groq_status}) on branch {branch or 'default'}"
                f"{degraded_info}. Pipeline: {' → '.join(stage_summaries)}"
            ),
        }

    except Exception as exc:
        logger.exception("Orchestration failed: %s", exc)
        return {
            "status": RunStatus.FAILED,
            "message": f"Run failed: {exc}",
        }
