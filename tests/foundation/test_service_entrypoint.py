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
