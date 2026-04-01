"""LangGraph adapter wrapper with normalized output."""

from typing import Any

from loan_agents.orchestration.pipeline import execute_domain_pipeline


def run_langgraph_pipeline(input_payload: dict[str, Any]) -> dict[str, Any]:
    return execute_domain_pipeline(input_payload=input_payload, mode="langgraph")
