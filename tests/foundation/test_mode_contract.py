import loan_agents.runtime.service as service


def test_dispatch_calls_adapter_matching_mode(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")

    def fake_crewai(payload):
        return {
            "status": "success",
            "decision": "approve",
            "mode": "crewai",
            "stages": {"x": "y"},
            "error": None,
        }

    def fake_langgraph(payload):
        return {
            "status": "success",
            "decision": "approve",
            "mode": "langgraph",
            "stages": {"x": "y"},
            "error": None,
        }

    monkeypatch.setattr(service, "run_crewai_pipeline", fake_crewai)
    monkeypatch.setattr(service, "run_langgraph_pipeline", fake_langgraph)

    payload = {"applicant_id": "a", "document_id": "document_valid_123"}
    crew = service.run_pipeline(payload, "crewai")
    lang = service.run_pipeline(payload, "langgraph")

    assert crew["mode"] == "crewai"
    assert lang["mode"] == "langgraph"


def test_adapter_failures_return_structured_failure_with_selected_mode(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")
    monkeypatch.setenv("MAX_RETRIES", "0")

    def boom(payload):
        raise RuntimeError("provider down")

    monkeypatch.setattr(service, "run_crewai_pipeline", boom)

    payload = {"applicant_id": "a", "document_id": "document_valid_123"}
    result = service.run_pipeline(payload, "crewai")

    assert result["status"] == "failed"
    assert result["mode"] == "crewai"
    assert result["error"]["code"] == "PIPELINE_ERROR"
