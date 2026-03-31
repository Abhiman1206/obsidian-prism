"""Framework-agnostic runtime endpoint handlers."""

from typing import Any

from loan_agents.domain.contracts import PipelineInput
from loan_agents.runtime.metrics import collect_run_metrics
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
    correlation_id: str | None = None
    if "correlation_id" in request:
        correlation_id = str(request["correlation_id"])
        payload["correlation_id"] = correlation_id

    result = run_pipeline(payload, mode)
    if correlation_id and "metrics" not in result:
        result["metrics"] = collect_run_metrics(correlation_id)
    return result
