from fastapi import APIRouter

from app.api.schemas.run import CreateRunRequest, CreateRunResponse, RunStatus, RunStatusResponse, utc_now

router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.post("", response_model=CreateRunResponse)
def create_run(payload: CreateRunRequest) -> CreateRunResponse:
    return CreateRunResponse(
        run_id=f"run-{payload.repository_id}",
        status=RunStatus.QUEUED,
        created_at=utc_now(),
    )


@router.get("/{run_id}", response_model=RunStatusResponse)
def get_run_status(run_id: str) -> RunStatusResponse:
    return RunStatusResponse(
        run_id=run_id,
        status=RunStatus.RUNNING,
        updated_at=utc_now(),
        message="Run accepted and in progress",
    )
