"""Structured runtime telemetry logging helpers."""

from datetime import datetime, timezone
import json
import logging
from typing import Any

from loan_agents.runtime.redaction import redact_mapping


LOGGER = logging.getLogger("loan_agents.runtime")


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _emit(event: dict[str, Any]) -> dict[str, Any]:
    LOGGER.info(json.dumps(event, sort_keys=True))
    return event


def log_stage_event(
    *,
    correlation_id: str,
    stage: str,
    mode: str,
    status: str,
    duration_ms: int,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    event = {
        "timestamp": _timestamp(),
        "event": "stage",
        "correlation_id": correlation_id,
        "stage": stage,
        "mode": mode,
        "status": status,
        "duration_ms": duration_ms,
        "metadata": redact_mapping(metadata or {}),
    }
    return _emit(event)


def log_failure_event(
    *,
    correlation_id: str,
    stage: str,
    mode: str,
    duration_ms: int,
    failure_category: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    event = {
        "timestamp": _timestamp(),
        "event": "failure",
        "correlation_id": correlation_id,
        "stage": stage,
        "mode": mode,
        "status": "failed",
        "duration_ms": duration_ms,
        "failure_category": failure_category,
        "metadata": redact_mapping(metadata or {}),
    }
    return _emit(event)
