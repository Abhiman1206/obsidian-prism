import pytest

from loan_agents.runtime.service import run_pipeline

pytestmark = pytest.mark.deterministic_validation


def _sample_payload(document_id: str) -> dict[str, str]:
    return {"applicant_id": "app_sample", "document_id": document_id}


def _parity_view(result: dict[str, object]) -> dict[str, object]:
    return {
        "status": result["status"],
        "decision": result["decision"],
        "stages": result["stages"],
        "error": result["error"],
    }


@pytest.mark.parametrize(
    ("scenario", "document_id", "expected_status", "expected_decision", "expected_error_code"),
    [
        ("happy", "document_valid_123", "success", "approve", None),
        ("risky", "document_risky_789", "success", "review", None),
        ("unknown", "document_unknown_999", "failed", "error", "DOCUMENT_ERROR"),
    ],
)
def test_dual_mode_scenario_matrix_keeps_parity(
    monkeypatch,
    scenario: str,
    document_id: str,
    expected_status: str,
    expected_decision: str,
    expected_error_code: str | None,
) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")
    payload = _sample_payload(document_id)

    crew = run_pipeline(payload, "crewai")
    lang = run_pipeline(payload, "langgraph")

    crew_parity = _parity_view(crew)
    lang_parity = _parity_view(lang)

    assert crew_parity == lang_parity, f"scenario={scenario} parity mismatch"
    assert crew_parity["status"] == expected_status, f"scenario={scenario} wrong status"
    assert crew_parity["decision"] == expected_decision, f"scenario={scenario} wrong decision"
    if expected_error_code is None:
        assert crew_parity["error"] is None, f"scenario={scenario} expected no error"
    else:
        error = crew_parity["error"]
        assert isinstance(error, dict), f"scenario={scenario} expected error dict"
        assert error["code"] == expected_error_code, f"scenario={scenario} wrong error code"


def test_unknown_document_is_deterministic_across_repeated_runs(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "key")
    payload = _sample_payload("document_unknown_999")

    crew_first = run_pipeline(payload, "crewai")
    crew_second = run_pipeline(payload, "crewai")
    lang_first = run_pipeline(payload, "langgraph")
    lang_second = run_pipeline(payload, "langgraph")

    assert _parity_view(crew_first) == _parity_view(crew_second), "mode=crewai repeat mismatch"
    assert _parity_view(lang_first) == _parity_view(lang_second), "mode=langgraph repeat mismatch"
    assert _parity_view(crew_first) == _parity_view(lang_first), "cross-mode unknown parity mismatch"
