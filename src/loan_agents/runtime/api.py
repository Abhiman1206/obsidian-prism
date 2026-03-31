"""Framework-agnostic runtime endpoint handlers."""

from typing import Any

from loan_agents.domain.contracts import PipelineInput
from loan_agents.runtime.service import run_pipeline
from loan_agents.runtime.settings import load_settings


def health() -> dict[str, Any]:
    return {"status": "ok", "service": "loan-agents"}


def readiness() -> dict[str, Any]:
    checks = {"llm_api_key": True}
    try:
        load_settings()
    except ValueError:
        checks["llm_api_key"] = False

    status = "ready" if all(checks.values()) else "not_ready"
    return {"status": status, "checks": checks}


def run(request: dict[str, Any]) -> dict[str, Any]:
    mode = str(request.get("mode", "crewai"))
    normalized = PipelineInput.from_dict(
        {
            "applicant_id": request["applicant_id"],
            "document_id": request["document_id"],
            "mode": mode,
        }
    )

    payload: dict[str, Any] = {
        "applicant_id": normalized.applicant_id,
        "document_id": normalized.document_id,
        "mode": normalized.mode,
    }
    if "correlation_id" in request:
        payload["correlation_id"] = str(request["correlation_id"])

    return run_pipeline(payload, mode)
