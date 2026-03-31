import time

import loan_agents.runtime.service as service


def _payload(correlation_id: str = "corr-default") -> dict[str, str]:
    return {
        "applicant_id": "app_1",
        "document_id": "document_valid_123",
        "correlation_id": correlation_id,
    }


def test_invalid_mode_returns_mission_report_fields() -> None:
    result = service.run_pipeline(_payload("corr-invalid"), "unknown")

    assert result["status"] == "failed"
    assert result["correlation_id"] == "corr-invalid"
    assert result["error"]["failure_category"] == "invalid_mode"
    assert result["error"]["retry_count"] == 0
    assert result["error"]["stage"] == "dispatch"


def test_provider_exception_maps_to_provider_failure_category(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")

    def boom(payload):
        raise RuntimeError("provider down")

    monkeypatch.setattr(service, "run_crewai_pipeline", boom)
    result = service.run_pipeline(_payload("corr-provider"), "crewai")

    assert result["status"] == "failed"
    assert result["error"]["failure_category"] == "provider"
    assert isinstance(result["error"]["retry_count"], int)


def test_timeout_maps_to_timeout_failure_category(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")
    monkeypatch.setenv("RUN_TIMEOUT_SECONDS", "0.01")

    def slow_call(payload):
        time.sleep(0.02)
        return {
            "status": "success",
            "decision": "approve",
            "mode": "crewai",
            "stages": {"document": {"status": "processed"}},
            "error": None,
        }

    monkeypatch.setattr(service, "run_crewai_pipeline", slow_call)
    result = service.run_pipeline(_payload("corr-timeout"), "crewai")

    assert result["status"] == "failed"
    assert result["error"]["failure_category"] == "timeout"


def test_rate_limit_maps_to_rate_limit_failure_category(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")
    monkeypatch.setenv("REQUESTS_PER_MINUTE", "0")

    result = service.run_pipeline(_payload("corr-rate"), "langgraph")

    assert result["status"] == "failed"
    assert result["error"]["failure_category"] == "rate_limit"
    assert result["error"]["retry_count"] == 0
