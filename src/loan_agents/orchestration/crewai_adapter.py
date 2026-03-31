"""CrewAI adapter wrapper with normalized output."""

from typing import Any

from loan_agents.document.mock_data import get_document_content
from loan_agents.orchestration.normalized import build_adapter_failure, build_success_result


def run_crewai_pipeline(input_payload: dict[str, Any]) -> dict[str, Any]:
    content = get_document_content(str(input_payload["document_id"]))
    if content.startswith("ERROR:"):
        return build_adapter_failure(mode="crewai", code="DOCUMENT_ERROR", message=content)

    decision = "approve" if "Income: 96000" in content else "review"
    return build_success_result(
        mode="crewai",
        decision=decision,
        stages={"document": {"status": "processed", "provider": "mock"}},
    )
