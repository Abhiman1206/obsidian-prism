"""Thin orchestration adapter exports."""

from loan_agents.orchestration.crewai_adapter import run_crewai_pipeline
from loan_agents.orchestration.langgraph_adapter import run_langgraph_pipeline

__all__ = ["run_crewai_pipeline", "run_langgraph_pipeline"]
