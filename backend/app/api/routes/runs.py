from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas.run import CreateRunRequest, CreateRunResponse, RunStatus, RunStatusResponse, utc_now
from app.workers.langchain_orchestrator import orchestrate_run

router = APIRouter(prefix="/api/runs", tags=["runs"])

_RUN_STATUSES: dict[str, RunStatusResponse] = {}


@router.post("", response_model=CreateRunResponse)
def create_run(payload: CreateRunRequest) -> CreateRunResponse:
    now = utc_now()
    safe_id = payload.repository_id.replace("/", "-")
    run_id = f"run-{safe_id}"
    _RUN_STATUSES[run_id] = RunStatusResponse(
        run_id=run_id,
        status=RunStatus.QUEUED,
        updated_at=now,
        message="Run queued",
    )

    result = orchestrate_run(
        run_id=run_id,
        repository_id=payload.repository_id,
        provider=payload.provider,
        branch=payload.branch,
    )

    _RUN_STATUSES[run_id] = RunStatusResponse(
        run_id=run_id,
        status=result["status"],
        updated_at=utc_now(),
        message=result["message"],
    )

    return CreateRunResponse(run_id=run_id, status=result["status"], created_at=now)


@router.get("/{run_id}", response_model=RunStatusResponse)
def get_run_status(run_id: str) -> RunStatusResponse:
    existing = _RUN_STATUSES.get(run_id)
    if existing is not None:
        return existing

    return RunStatusResponse(
        run_id=run_id,
        status=RunStatus.FAILED,
        updated_at=utc_now(),
        message="Run not found",
    )
