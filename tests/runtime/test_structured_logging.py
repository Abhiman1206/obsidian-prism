from loan_agents.runtime.logging import log_failure_event, log_stage_event


def test_log_stage_event_includes_required_operational_fields() -> None:
    event = log_stage_event(
        correlation_id="corr-1",
        stage="document",
        mode="crewai",
        status="success",
        duration_ms=42,
    )

    assert set(event.keys()) >= {"timestamp", "correlation_id", "stage", "mode", "status", "duration_ms"}
    assert event["correlation_id"] == "corr-1"
    assert event["stage"] == "document"


def test_structured_logging_redacts_sensitive_fields_in_metadata() -> None:
    event = log_failure_event(
        correlation_id="corr-2",
        stage="dispatch",
        mode="langgraph",
        duration_ms=7,
        failure_category="provider",
        metadata={
            "LLM_API_KEY": "plain-secret",
            "token": "Bearer abc123",
            "nested": {"password": "abc", "message": "safe"},
        },
    )

    assert event["metadata"]["LLM_API_KEY"] == "***REDACTED***"
    assert event["metadata"]["token"] == "***REDACTED***"
    assert event["metadata"]["nested"]["password"] == "***REDACTED***"
    assert event["metadata"]["nested"]["message"] == "safe"
