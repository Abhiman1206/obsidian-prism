"""Shared adapter result normalization helpers."""

from typing import Any

from loan_agents.domain.contracts import PipelineResult


def build_success_result(mode: str, decision: str, stages: dict[str, Any]) -> dict[str, Any]:
    return PipelineResult(
        status="success",
        decision=decision,
        mode=mode,
        stages=stages,
        error=None,
    ).to_dict()


def build_adapter_failure(
    mode: str,
    code: str,
    message: str,
    *,
    failure_category: str = "invalid_document",
    retry_count: int = 0,
    stage: str = "document",
    stages: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return PipelineResult(
        status="failed",
        decision="error",
        mode=mode,
        stages=stages or {"document": {"status": "failed", "provider": "mock"}},
        error={
            "code": code,
            "message": message,
            "failure_category": failure_category,
            "retry_count": retry_count,
            "stage": stage,
        },
    ).to_dict()