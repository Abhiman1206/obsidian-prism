"""Supervisor (Project Manager) Agent — orchestrates the multi-agent workflow.

PRD Role: Receives the high-level request, plans the workflow, delegates tasks
to specialist agents, and manages dependencies between them.

Execution DAG:
  DataMiningAgent → HealthAnalystAgent → RiskPredictorAgent → ReportWriterAgent
"""

from __future__ import annotations

import logging
from typing import Any

from app.agents.data_mining_agent import DataMiningAgent
from app.agents.health_analyst_agent import HealthAnalystAgent
from app.agents.report_writer_agent import ReportWriterAgent
from app.agents.risk_predictor_agent import RiskPredictorAgent
from app.agents.shared_memory import EpistemicMemory

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """Project Manager orchestrator that delegates to specialist agents."""

    name = "supervisor_agent"

    def __init__(self) -> None:
        self.data_mining = DataMiningAgent(timeout_seconds=120)
        self.health_analyst = HealthAnalystAgent(timeout_seconds=120)
        self.risk_predictor = RiskPredictorAgent(timeout_seconds=60)
        self.report_writer = ReportWriterAgent(timeout_seconds=60)

        self.stage_results: list[dict[str, Any]] = []

    def run(self, memory: EpistemicMemory) -> dict[str, Any]:
        """Execute the full multi-agent pipeline with fault tolerance."""
        stages = [
            ("data_mining", self.data_mining, "Retrieve repository data from provider APIs"),
            ("health_analysis", self.health_analyst, "Analyze code health using Radon metrics"),
            ("risk_prediction", self.risk_predictor, "Forecast 90-day component failure risk"),
            ("business_report", self.report_writer, "Translate risks into executive business report"),
        ]

        overall_status = "succeeded"
        degraded_stages: list[str] = []

        for stage_name, agent, task_description in stages:
            logger.info("Supervisor delegating to %s: %s", agent.name, task_description)

            try:
                result = agent.execute(memory, task=task_description)
                result["stage"] = stage_name
                self.stage_results.append(result)
                logger.info("Stage %s completed: %s", stage_name, result.get("status"))

            except Exception as exc:
                logger.error("Stage %s failed: %s", stage_name, exc)
                failure_result = {
                    "stage": stage_name,
                    "status": "failed",
                    "agent": agent.name,
                    "error": str(exc),
                }
                self.stage_results.append(failure_result)

                # Determine severity — data_mining failure is fatal
                if stage_name == "data_mining":
                    overall_status = "failed"
                    break  # Cannot continue without data
                else:
                    overall_status = "degraded"
                    degraded_stages.append(stage_name)
                    # Continue with remaining stages using whatever data is available

        return {
            "status": overall_status,
            "stages": self.stage_results,
            "degraded_stages": degraded_stages,
            "memory_keys": memory.keys(),
        }
