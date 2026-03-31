"""Structured error envelope helpers for runtime responses."""

from typing import Any


def build_failure(
    status: str,
    mode: str,
    code: str,
    message: str,
    *,
    failure_category: str = "provider",
    retry_count: int = 0,
    stage: str = "dispatch",
    correlation_id: str | None = None,
) -> dict[str, Any]:
    response: dict[str, Any] = {
        "status": status,
        "decision": "undetermined",
        "mode": mode,
        "stages": {},
        "error": {
            "code": code,
            "message": message,
            "failure_category": failure_category,
            "retry_count": retry_count,
            "stage": stage,
        },
    }
    if correlation_id:
        response["correlation_id"] = correlation_id
    return response
