"""Callable extraction service entrypoint."""

from typing import Any

from loan_agents.domain.contracts import PipelineInput
from loan_agents.orchestration import run_crewai_pipeline, run_langgraph_pipeline
from loan_agents.runtime.errors import build_failure
from loan_agents.runtime.settings import load_settings

ALLOWED_MODES = {"crewai", "langgraph"}


def run_pipeline(input_payload: dict[str, Any], mode: str) -> dict[str, Any]:
    if mode not in ALLOWED_MODES:
        return build_failure(
            status="failed",
            mode=mode,
            code="INVALID_MODE",
            message=f"Unsupported mode: {mode}",
        )

    try:
        load_settings()
        PipelineInput.from_dict({**input_payload, "mode": mode})

        if mode == "crewai":
            return run_crewai_pipeline(input_payload)
        return run_langgraph_pipeline(input_payload)
    except Exception as exc:
        return build_failure(
            status="failed",
            mode=mode,
            code="PIPELINE_ERROR",
            message=str(exc),
        )
