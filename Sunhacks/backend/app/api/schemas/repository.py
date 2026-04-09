from enum import StrEnum

from pydantic import BaseModel, Field

from app.api.schemas.provider_auth import ProviderAuthPayload


class AuthorizationStatus(StrEnum):
    AUTHORIZED = "authorized"
    PENDING = "pending"
    FAILED = "failed"


class RepositoryRegistrationRequest(BaseModel):
    provider: str = Field(pattern="^(github|gitlab)$")
    repository_url: str = Field(min_length=1)
    repository_name: str = Field(min_length=1)
    auth: ProviderAuthPayload


class RepositoryRegistrationResponse(BaseModel):
    repository_id: str
    provider: str = Field(pattern="^(github|gitlab)$")
    repository_url: str = Field(min_length=1)
    authorization_status: AuthorizationStatus
    run_ready: bool
