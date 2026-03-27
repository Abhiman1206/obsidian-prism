from loan_agents.document.mock_data import get_document_content
from loan_agents.domain.contracts import PipelineInput, PipelineResult


def test_pipeline_input_maps_required_fields() -> None:
    data = {
        "applicant_id": "app_001",
        "document_id": "document_valid_123",
        "mode": "crewai",
    }
    model = PipelineInput.from_dict(data)
    assert model.applicant_id == "app_001"
    assert model.document_id == "document_valid_123"
    assert model.mode == "crewai"


def test_pipeline_result_has_required_shape() -> None:
    result = PipelineResult(
        status="success",
        decision="approve",
        mode="langgraph",
        stages={"document": {"status": "ok"}},
        error=None,
    ).to_dict()
    assert set(result.keys()) == {"status", "decision", "mode", "stages", "error"}


def test_document_provider_contains_all_scenarios() -> None:
    assert "Applicant name" in get_document_content("document_valid_123")
    assert "Applicant name" in get_document_content("document_risky_789")
    assert "Applicant name" in get_document_content("document_invalid_456")


def test_unknown_document_returns_explicit_error_payload() -> None:
    payload = get_document_content("document_unknown_999")
    assert payload.startswith("ERROR: unknown document_id=")
