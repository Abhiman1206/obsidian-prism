"""Callable extraction service entrypoint."""

import time
from typing import Any

from loan_agents.domain.contracts import PipelineInput
from loan_agents.orchestration import run_crewai_pipeline, run_langgraph_pipeline
from loan_agents.runtime.execution_policy import (
    PolicyExecutionError,
    RuntimeExecutionPolicy,
    execute_with_policy,
)
from loan_agents.runtime.errors import build_failure
from loan_agents.runtime.logging import log_failure_event, log_stage_event
from loan_agents.runtime.metrics import (
    collect_run_metrics,
    record_failure_category,
    record_retry,
    record_stage_duration,
)
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
    trace_id = correlation_id or "n/a"

    if mode not in ALLOWED_MODES:
        record_failure_category(correlation_id=trace_id, category="invalid_mode")
        log_failure_event(
            correlation_id=trace_id,
            stage="dispatch",
            mode=mode,
            duration_ms=0,
            failure_category="invalid_mode",
        )
        failure = build_failure(
            status="failed",
            mode=mode,
            code="INVALID_MODE",
            message=f"Unsupported mode: {mode}",
            failure_category="invalid_mode",
            retry_count=0,
            stage="dispatch",
            correlation_id=correlation_id,
        )
        if correlation_id:
            failure["metrics"] = collect_run_metrics(trace_id)
        return failure

    try:
        started_at = time.monotonic()
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
            correlation_id=trace_id,
            stage="dispatch",
        )
        log_stage_event(
            correlation_id=trace_id,
            stage="dispatch",
            mode=mode,
            status="success",
            duration_ms=max(0, int((time.monotonic() - started_at) * 1000)),
        )
        record_stage_duration(correlation_id=trace_id, stage="dispatch", duration_ms=outcome.duration_ms)
        for _ in range(outcome.retry_count):
            record_retry(correlation_id=trace_id)

        result = outcome.value
        if correlation_id:
            result["metrics"] = collect_run_metrics(trace_id)
        return result
    except ValueError as exc:
        record_failure_category(correlation_id=trace_id, category="config")
        log_failure_event(
            correlation_id=trace_id,
            stage="dispatch",
            mode=mode,
            duration_ms=0,
            failure_category="config",
            metadata={"message": str(exc)},
        )
        failure = build_failure(
            status="failed",
            mode=mode,
            code="PIPELINE_ERROR",
            message=str(exc),
            failure_category="config",
            retry_count=0,
            stage="dispatch",
            correlation_id=correlation_id,
        )
        if correlation_id:
            failure["metrics"] = collect_run_metrics(trace_id)
        return failure
    except PolicyExecutionError as exc:
        code = "PIPELINE_ERROR"
        if exc.failure_category == "timeout":
            code = "TIMEOUT"
        elif exc.failure_category == "rate_limit":
            code = "RATE_LIMIT"

        record_failure_category(correlation_id=trace_id, category=exc.failure_category)
        for _ in range(exc.retry_count):
            record_retry(correlation_id=trace_id)

        log_failure_event(
            correlation_id=trace_id,
            stage=exc.stage,
            mode=mode,
            duration_ms=0,
            failure_category=exc.failure_category,
            metadata={"message": str(exc)},
        )

        failure = build_failure(
            status="failed",
            mode=mode,
            code=code,
            message=str(exc),
            failure_category=exc.failure_category,
            retry_count=exc.retry_count,
            stage=exc.stage,
            correlation_id=correlation_id,
        )
        if correlation_id:
            failure["metrics"] = collect_run_metrics(trace_id)
        return failure
    except Exception as exc:
        record_failure_category(correlation_id=trace_id, category="provider")
        log_failure_event(
            correlation_id=trace_id,
            stage="dispatch",
            mode=mode,
            duration_ms=0,
            failure_category="provider",
            metadata={"message": str(exc)},
        )
        failure = build_failure(
            status="failed",
            mode=mode,
            code="PIPELINE_ERROR",
            message=str(exc),
            failure_category="provider",
            retry_count=0,
            stage="dispatch",
            correlation_id=correlation_id,
        )
        if correlation_id:
            failure["metrics"] = collect_run_metrics(trace_id)
        return failure
