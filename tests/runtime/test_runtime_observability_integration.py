import pytest
from fastapi.testclient import TestClient

import loan_agents.runtime.service as service
from loan_agents.runtime.metrics import collect_run_metrics, reset_metrics
from loan_agents.runtime.asgi import create_app

pytestmark = pytest.mark.deterministic_validation


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


@pytest.mark.parametrize("mode", ["crewai", "langgraph"])
def test_success_run_records_all_domain_stage_durations_for_both_modes(monkeypatch, mode: str) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")
    reset_metrics()

    correlation_id = f"corr-stage-metrics-{mode}"
    result = service.run_pipeline(_payload(correlation_id), mode)

    assert result["status"] == "success"
    stage_durations = result["metrics"]["stage_durations_ms"]
    for stage in ("document", "credit", "risk", "compliance"):
        assert stage in stage_durations
        assert isinstance(stage_durations[stage], int)
        assert stage_durations[stage] >= 0


def test_failure_run_has_matching_correlation_id_in_failure_and_metrics(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")
    monkeypatch.setenv("MAX_RETRIES", "0")
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


def test_provider_failure_keeps_deterministic_parity_across_modes(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")
    monkeypatch.setenv("MAX_RETRIES", "0")
    reset_metrics()

    def boom(payload):
        raise RuntimeError("provider down")

    monkeypatch.setattr(service, "run_crewai_pipeline", boom)
    monkeypatch.setattr(service, "run_langgraph_pipeline", boom)

    crew_result = service.run_pipeline(_payload("corr-provider-crewai"), "crewai")
    lang_result = service.run_pipeline(_payload("corr-provider-langgraph"), "langgraph")

    assert crew_result["status"] == "failed", "mode=crewai should fail"
    assert lang_result["status"] == "failed", "mode=langgraph should fail"

    crew_error = crew_result["error"]
    lang_error = lang_result["error"]
    assert crew_error["code"] == "PIPELINE_ERROR"
    assert lang_error["code"] == "PIPELINE_ERROR"
    assert crew_error["failure_category"] == "provider"
    assert lang_error["failure_category"] == "provider"
    assert crew_error["stage"] == "dispatch"
    assert lang_error["stage"] == "dispatch"

    crew_metrics = collect_run_metrics("corr-provider-crewai")
    lang_metrics = collect_run_metrics("corr-provider-langgraph")
    assert crew_metrics["failure_categories"]["provider"] >= 1
    assert lang_metrics["failure_categories"]["provider"] >= 1


def test_asgi_run_success_surfaces_metrics_for_correlation_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")
    reset_metrics()
    client = TestClient(create_app())

    response = client.post(
        "/run",
        json={
            "applicant_id": "app-obs-api",
            "document_id": "document_valid_123",
            "mode": "crewai",
            "correlation_id": "corr-asgi-success",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["metrics"]["correlation_id"] == "corr-asgi-success"


def test_asgi_run_failure_preserves_structured_error_envelope(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")
    monkeypatch.setenv("MAX_RETRIES", "0")
    reset_metrics()

    def boom(payload):
        raise RuntimeError("provider down")

    monkeypatch.setattr(service, "run_crewai_pipeline", boom)
    client = TestClient(create_app())

    response = client.post(
        "/run",
        json={
            "applicant_id": "app-obs-api",
            "document_id": "document_valid_123",
            "mode": "crewai",
            "correlation_id": "corr-asgi-failure",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "failed"
    assert payload["error"]["code"] == "PIPELINE_ERROR"
    assert payload["error"]["failure_category"] == "provider"
    assert payload["metrics"]["correlation_id"] == "corr-asgi-failure"
