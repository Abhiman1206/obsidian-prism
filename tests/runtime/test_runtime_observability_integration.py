import loan_agents.runtime.service as service
from loan_agents.runtime.metrics import collect_run_metrics, reset_metrics


def _payload(correlation_id: str) -> dict[str, str]:
    return {
        "applicant_id": "app-obs",
        "document_id": "document_valid_123",
        "correlation_id": correlation_id,
    }


def test_success_run_includes_metrics_payload(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")
    reset_metrics()

    result = service.run_pipeline(_payload("corr-success"), "crewai")

    assert result["status"] == "success"
    assert "metrics" in result
    assert result["metrics"]["correlation_id"] == "corr-success"
    assert "stage_durations_ms" in result["metrics"]


def test_failure_run_has_matching_correlation_id_in_failure_and_metrics(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")
    reset_metrics()

    def boom(payload):
        raise RuntimeError("provider down")

    monkeypatch.setattr(service, "run_crewai_pipeline", boom)
    result = service.run_pipeline(_payload("corr-failure"), "crewai")

    assert result["status"] == "failed"
    assert result["correlation_id"] == "corr-failure"
    metrics = collect_run_metrics("corr-failure")
    assert metrics["correlation_id"] == "corr-failure"
    assert metrics["failure_categories"][result["error"]["failure_category"]] >= 1
