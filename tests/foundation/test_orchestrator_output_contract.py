from loan_agents.orchestration import run_crewai_pipeline, run_langgraph_pipeline


def _base_payload(document_id: str) -> dict[str, str]:
    return {"applicant_id": "app_01", "document_id": document_id}


def test_adapter_outputs_have_required_contract_keys() -> None:
    crew = run_crewai_pipeline(_base_payload("document_valid_123"))
    lang = run_langgraph_pipeline(_base_payload("document_valid_123"))

    assert set(crew.keys()) == {"status", "decision", "mode", "stages", "error"}
    assert set(lang.keys()) == {"status", "decision", "mode", "stages", "error"}


def test_adapter_decision_and_stage_parity_for_same_inputs() -> None:
    crew_valid = run_crewai_pipeline(_base_payload("document_valid_123"))
    lang_valid = run_langgraph_pipeline(_base_payload("document_valid_123"))

    assert crew_valid["decision"] == lang_valid["decision"] == "approve"
    assert crew_valid["stages"] == lang_valid["stages"]

    crew_risky = run_crewai_pipeline(_base_payload("document_risky_789"))
    lang_risky = run_langgraph_pipeline(_base_payload("document_risky_789"))

    assert crew_risky["decision"] == lang_risky["decision"] == "review"
    assert crew_risky["stages"] == lang_risky["stages"]


def test_unknown_document_returns_normalized_failure_for_both_adapters() -> None:
    crew = run_crewai_pipeline(_base_payload("document_unknown_999"))
    lang = run_langgraph_pipeline(_base_payload("document_unknown_999"))

    assert crew["status"] == "failed"
    assert lang["status"] == "failed"
    assert crew["error"]["code"] == "DOCUMENT_ERROR"
    assert lang["error"]["code"] == "DOCUMENT_ERROR"
    assert crew["error"]["failure_category"] == "invalid_document"
    assert lang["error"]["failure_category"] == "invalid_document"
    assert crew["error"]["retry_count"] == 0
    assert lang["error"]["retry_count"] == 0
    assert crew["error"]["stage"] == "document"
    assert lang["error"]["stage"] == "document"
    assert crew["mode"] == "crewai"
    assert lang["mode"] == "langgraph"
