"""Callable extraction service entrypoint."""

from typing import Any

from loan_agents.domain.contracts import PipelineInput
from loan_agents.orchestration import run_crewai_pipeline, run_langgraph_pipeline
from loan_agents.runtime.execution_policy import (
    PolicyExecutionError,
    RuntimeExecutionPolicy,
    execute_with_policy,
)
from loan_agents.runtime.errors import build_failure
from loan_agents.runtime.settings import load_settings

ALLOWED_MODES = {"crewai", "langgraph"}


def _correlation_id(input_payload: dict[str, Any]) -> str | None:
    raw = input_payload.get("correlation_id")
    if raw is None:
        return None
    value = str(raw).strip()
    return value or None


def run_pipeline(input_payload: dict[str, Any], mode: str) -> dict[str, Any]:
    correlation_id = _correlation_id(input_payload)

    if mode not in ALLOWED_MODES:
        return build_failure(
            status="failed",
            mode=mode,
            code="INVALID_MODE",
            message=f"Unsupported mode: {mode}",
            failure_category="invalid_mode",
            retry_count=0,
            stage="dispatch",
            correlation_id=correlation_id,
        )

    try:
        settings = load_settings()
        policy = RuntimeExecutionPolicy.from_settings(settings)
        normalized_input = PipelineInput.from_dict({**input_payload, "mode": mode})
        normalized_payload = {
            "applicant_id": normalized_input.applicant_id,
            "document_id": normalized_input.document_id,
            "mode": normalized_input.mode,
        }

        if correlation_id:
            normalized_payload["correlation_id"] = correlation_id

        def dispatch_call() -> dict[str, Any]:
            if mode == "crewai":
                return run_crewai_pipeline(normalized_payload)
            return run_langgraph_pipeline(normalized_payload)

        outcome = execute_with_policy(
            dispatch_call,
            policy=policy,
            correlation_id=correlation_id or "n/a",
            stage="dispatch",
        )
        return outcome.value
    except ValueError as exc:
        return build_failure(
            status="failed",
            mode=mode,
            code="PIPELINE_ERROR",
            message=str(exc),
            failure_category="config",
            retry_count=0,
            stage="dispatch",
            correlation_id=correlation_id,
        )
    except PolicyExecutionError as exc:
        code = "PIPELINE_ERROR"
        if exc.failure_category == "timeout":
            code = "TIMEOUT"
        elif exc.failure_category == "rate_limit":
            code = "RATE_LIMIT"

        return build_failure(
            status="failed",
            mode=mode,
            code=code,
            message=str(exc),
            failure_category=exc.failure_category,
            retry_count=exc.retry_count,
            stage=exc.stage,
            correlation_id=correlation_id,
        )
    except Exception as exc:
        return build_failure(
            status="failed",
            mode=mode,
            code="PIPELINE_ERROR",
            message=str(exc),
            failure_category="provider",
            retry_count=0,
            stage="dispatch",
            correlation_id=correlation_id,
        )
