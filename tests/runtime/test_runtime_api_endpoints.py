import pytest
from fastapi.testclient import TestClient

from loan_agents.runtime.asgi import create_app
from loan_agents.runtime.api import health, readiness, run

pytestmark = pytest.mark.deterministic_validation


def test_health_returns_ok_service_payload() -> None:
    result = health()

    assert result["status"] == "ok"
    assert result["service"] == "loan-agents"


def test_readiness_reports_ready_when_required_config_is_present(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")

    result = readiness()

    assert result["status"] == "ready"
    assert result["checks"]["llm_api_key"] is True


def test_readiness_reports_not_ready_when_required_config_is_missing(monkeypatch) -> None:
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    result = readiness()

    assert result["status"] == "not_ready"
    assert result["checks"]["llm_api_key"] is False


def test_run_accepts_typed_request_and_returns_pipeline_payload(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")

    expected = {
        "status": "success",
        "decision": "approve",
        "mode": "langgraph",
        "stages": {"document": {"status": "processed"}},
        "error": None,
    }

    def fake_run_pipeline(payload, mode):
        assert payload["applicant_id"] == "101"
        assert payload["document_id"] == "202"
        assert payload["mode"] == "langgraph"
        assert payload["correlation_id"] == "corr-api"
        assert mode == "langgraph"
        return expected

    monkeypatch.setattr("loan_agents.runtime.api.run_pipeline", fake_run_pipeline)
    result = run(
        {
            "applicant_id": 101,
            "document_id": 202,
            "mode": "langgraph",
            "correlation_id": "corr-api",
        }
    )

    assert result == expected


def test_cors_preflight_allows_configured_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:4173")
    app = create_app()
    client = TestClient(app)

    response = client.options(
        "/run",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_cors_preflight_rejects_unconfigured_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173")
    app = create_app()
    client = TestClient(app)

    response = client.options(
        "/run",
        headers={
            "Origin": "https://malicious.example",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 400
    assert response.headers.get("access-control-allow-origin") is None
