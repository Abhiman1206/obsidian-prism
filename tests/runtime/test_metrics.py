from loan_agents.runtime.metrics import (
    collect_run_metrics,
    record_failure_category,
    record_retry,
    record_stage_duration,
    reset_metrics,
)


def test_metrics_capture_stage_duration_retry_and_failure_counts() -> None:
    reset_metrics()
    correlation_id = "corr-metrics-1"

    record_stage_duration(correlation_id=correlation_id, stage="document", duration_ms=12)
    record_retry(correlation_id=correlation_id)
    record_retry(correlation_id=correlation_id)
    record_failure_category(correlation_id=correlation_id, category="timeout")

    metrics = collect_run_metrics(correlation_id=correlation_id)

    assert metrics["stage_durations_ms"]["document"] == 12
    assert metrics["retry_count"] == 2
    assert metrics["failure_categories"]["timeout"] == 1
