from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class CreateRunRequest(BaseModel):
    repository_id: str = Field(min_length=1)
    provider: str = Field(pattern="^(github|gitlab)$")
    branch: str | None = None


class CreateRunResponse(BaseModel):
    run_id: str
    status: RunStatus
    created_at: datetime


class RunStatusResponse(BaseModel):
    run_id: str
    status: RunStatus
    updated_at: datetime
    message: str | None = None


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: dict[str, str] | None = None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
