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


def build_adapter_failure(mode: str, code: str, message: str) -> dict[str, Any]:
    return PipelineResult(
        status="failed",
        decision="error",
        mode=mode,
        stages={"document": {"status": "failed", "provider": "mock"}},
        error={
            "code": code,
            "message": message,
            "failure_category": "invalid_document",
            "retry_count": 0,
            "stage": "document",
        },
    ).to_dict()