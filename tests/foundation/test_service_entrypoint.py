from loan_agents.runtime.service import run_pipeline


def test_run_pipeline_with_valid_payload_and_mode(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")
    payload = {"applicant_id": "app_1", "document_id": "document_valid_123"}

    result = run_pipeline(payload, "crewai")
    assert result["status"] == "success"
    assert result["mode"] == "crewai"
    assert set(result.keys()) == {"status", "decision", "mode", "stages", "error"}


def test_run_pipeline_rejects_unknown_mode() -> None:
    payload = {"applicant_id": "app_1", "document_id": "document_valid_123"}
    result = run_pipeline(payload, "unknown")

    assert result["status"] == "failed"
    assert result["error"]["code"] == "INVALID_MODE"
    assert set(result.keys()) == {"status", "decision", "mode", "stages", "error"}


def test_run_pipeline_returns_failure_when_config_missing(monkeypatch) -> None:
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    payload = {"applicant_id": "app_1", "document_id": "document_valid_123"}
    result = run_pipeline(payload, "langgraph")

    assert result["status"] == "failed"
    assert result["mode"] == "langgraph"
    assert result["error"]["code"] == "PIPELINE_ERROR"


def test_run_pipeline_dispatches_normalized_payload_to_adapter(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")
    captured: dict[str, str] = {}

    def fake_crewai(payload):
        captured.update(payload)
        return {
            "status": "success",
            "decision": "approve",
            "mode": "crewai",
            "stages": {"document": {"status": "processed", "provider": "mock"}},
            "error": None,
        }

    monkeypatch.setattr("loan_agents.runtime.service.run_crewai_pipeline", fake_crewai)

    result = run_pipeline({"applicant_id": 101, "document_id": 202}, "crewai")

    assert result["status"] == "success"
    assert captured == {"applicant_id": "101", "document_id": "202", "mode": "crewai"}
