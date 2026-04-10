from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.api.dependencies.auth import resolve_authenticated_user_id
from app.api.schemas.run import CreateRunRequest, CreateRunResponse, RunStatus, RunStatusResponse, utc_now
from app.domain.repositories.connection_repository import REPOSITORY_CONNECTION_REPOSITORY
from app.infra.secrets.provider_credentials import ProviderCredentialsService
from app.workers.langchain_orchestrator import orchestrate_run

router = APIRouter(prefix="/api/runs", tags=["runs"])

_RUN_STATUSES: dict[str, RunStatusResponse] = {}
_credentials_service = ProviderCredentialsService()


@router.post("", response_model=CreateRunResponse)
def create_run(
    payload: CreateRunRequest,
    current_user_id: str = Depends(resolve_authenticated_user_id),
) -> CreateRunResponse:
    repository_connection = REPOSITORY_CONNECTION_REPOSITORY.get(payload.repository_id)
    repository_slug: str | None = None
    provider_token: str | None = None
    if repository_connection is not None:
        if repository_connection.owner_user_id:
            if repository_connection.owner_user_id != current_user_id:
                raise HTTPException(status_code=403, detail="Run not allowed for this user")
        if not repository_connection.run_ready:
            raise HTTPException(status_code=403, detail="Repository is not authorized for analysis")
        if repository_connection.provider != payload.provider:
            raise HTTPException(status_code=400, detail="Provider mismatch for repository")

        runtime_bundle = _credentials_service.get_runtime_bundle(payload.repository_id)
        if runtime_bundle is None:
            raise HTTPException(status_code=403, detail="Repository credentials are unavailable")

        repository_slug = repository_connection.repository_slug
        provider_token = runtime_bundle.token

    now = utc_now()
    run_id = f"run-{uuid4().hex}"
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
        repository_slug=repository_slug,
        provider_token=provider_token,
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
