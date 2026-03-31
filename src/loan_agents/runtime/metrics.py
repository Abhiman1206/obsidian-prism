"""In-memory runtime metrics collector keyed by correlation ID."""

from copy import deepcopy
from threading import Lock
from typing import Any


_METRICS_LOCK = Lock()
_RUN_METRICS: dict[str, dict[str, Any]] = {}


def _ensure_bucket(correlation_id: str) -> dict[str, Any]:
    if correlation_id not in _RUN_METRICS:
        _RUN_METRICS[correlation_id] = {
            "correlation_id": correlation_id,
            "stage_durations_ms": {},
            "retry_count": 0,
            "failure_categories": {},
        }
    return _RUN_METRICS[correlation_id]


def record_stage_duration(*, correlation_id: str, stage: str, duration_ms: int) -> None:
    with _METRICS_LOCK:
        bucket = _ensure_bucket(correlation_id)
        bucket["stage_durations_ms"][stage] = max(0, int(duration_ms))


def record_retry(*, correlation_id: str) -> None:
    with _METRICS_LOCK:
        bucket = _ensure_bucket(correlation_id)
        bucket["retry_count"] += 1


def record_failure_category(*, correlation_id: str, category: str) -> None:
    with _METRICS_LOCK:
        bucket = _ensure_bucket(correlation_id)
        failures = bucket["failure_categories"]
        failures[category] = failures.get(category, 0) + 1


def collect_run_metrics(correlation_id: str) -> dict[str, Any]:
    with _METRICS_LOCK:
        bucket = _ensure_bucket(correlation_id)
        return deepcopy(bucket)


def reset_metrics() -> None:
    with _METRICS_LOCK:
        _RUN_METRICS.clear()
