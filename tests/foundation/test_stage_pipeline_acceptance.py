import pytest

from loan_agents.runtime.service import run_pipeline

pytestmark = pytest.mark.deterministic_validation


_REQUIRED_STAGE_ORDER = ("document", "credit", "risk", "compliance")


def _payload(document_id: str) -> dict[str, str]:
    return {
        "applicant_id": "acc-acceptance",
        "document_id": document_id,
    }


@pytest.mark.parametrize("mode", ["crewai", "langgraph"])
def test_happy_path_executes_all_four_stages_and_emits_stage_artifacts(monkeypatch, mode: str) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")

    result = run_pipeline(_payload("document_valid_123"), mode)

    assert result["status"] == "success"
    assert result["decision"] == "approve"

    stages = result["stages"]
    assert tuple(stages.keys()) == _REQUIRED_STAGE_ORDER

    assert stages["document"]["status"] == "processed"
    assert stages["document"]["artifact"]["customer_id"] == "CUST-12345"

    assert stages["credit"]["status"] == "processed"
    assert stages["credit"]["artifact"]["credit_score"] == 810

    assert stages["risk"]["status"] == "processed"
    assert stages["risk"]["artifact"]["risk_level"] == "LOW"

    assert stages["compliance"]["status"] == "processed"
    assert stages["compliance"]["artifact"]["is_compliant"] is True


@pytest.mark.parametrize("mode", ["crewai", "langgraph"])
def test_risky_path_executes_all_four_stages_and_marks_review(monkeypatch, mode: str) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")

    result = run_pipeline(_payload("document_risky_789"), mode)

    assert result["status"] == "success"
    assert result["decision"] == "review"

    stages = result["stages"]
    assert tuple(stages.keys()) == _REQUIRED_STAGE_ORDER
    assert stages["document"]["status"] == "processed"
    assert stages["credit"]["artifact"]["credit_score"] == 550
    assert stages["risk"]["artifact"]["risk_level"] == "HIGH"
    assert stages["compliance"]["artifact"]["is_compliant"] is False


@pytest.mark.parametrize("mode", ["crewai", "langgraph"])
def test_invalid_document_fails_with_document_stage_and_skips_remaining(monkeypatch, mode: str) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")

    result = run_pipeline(_payload("document_invalid_456"), mode)

    assert result["status"] == "failed"
    assert result["error"]["code"] == "DOCUMENT_ERROR"
    assert result["error"]["stage"] == "document"

    stages = result["stages"]
    assert stages["document"]["status"] == "failed"
    assert stages["credit"]["status"] == "skipped"
    assert stages["risk"]["status"] == "skipped"
    assert stages["compliance"]["status"] == "skipped"
