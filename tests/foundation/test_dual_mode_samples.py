from loan_agents.runtime.service import run_pipeline


def _sample_payload(document_id: str) -> dict[str, str]:
    return {"applicant_id": "app_sample", "document_id": document_id}


def test_single_payload_shape_runs_both_modes_for_valid_document(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")
    payload = _sample_payload("document_valid_123")

    crew = run_pipeline(payload, "crewai")
    lang = run_pipeline(payload, "langgraph")

    assert crew["status"] == "success"
    assert lang["status"] == "success"
    assert crew["decision"] == lang["decision"] == "approve"


def test_risky_document_keeps_decision_parity_across_modes(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")
    payload = _sample_payload("document_risky_789")

    crew = run_pipeline(payload, "crewai")
    lang = run_pipeline(payload, "langgraph")

    assert crew["status"] == "success"
    assert lang["status"] == "success"
    assert crew["decision"] == lang["decision"] == "review"


def test_unknown_document_returns_normalized_failure_with_selected_mode(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")
    payload = _sample_payload("document_unknown_999")

    crew = run_pipeline(payload, "crewai")
    lang = run_pipeline(payload, "langgraph")

    assert crew["status"] == "failed"
    assert lang["status"] == "failed"
    assert crew["mode"] == "crewai"
    assert lang["mode"] == "langgraph"
    assert crew["error"]["code"] == "DOCUMENT_ERROR"
    assert lang["error"]["code"] == "DOCUMENT_ERROR"
