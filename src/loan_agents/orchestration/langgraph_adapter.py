"""LangGraph adapter wrapper with normalized output."""

from typing import Any

from loan_agents.document.mock_data import get_document_content


def run_langgraph_pipeline(input_payload: dict[str, Any]) -> dict[str, Any]:
    content = get_document_content(str(input_payload["document_id"]))
    if content.startswith("ERROR:"):
        raise ValueError(content)

    decision = "approve" if "Income: 96000" in content else "review"
    return {
        "status": "success",
        "decision": decision,
        "mode": "langgraph",
        "stages": {"document": {"status": "processed", "provider": "mock"}},
        "error": None,
    }
