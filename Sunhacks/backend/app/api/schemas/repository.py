from enum import StrEnum

from pydantic import BaseModel, Field

from app.api.schemas.provider_auth import ProviderAuthPayload


class AuthorizationStatus(StrEnum):
    AUTHORIZED = "authorized"
    PENDING = "pending"
    FAILED = "failed"


class AuthorizationReason(StrEnum):
    AUTHORIZED_COLLABORATOR = "authorized_collaborator"
    MISSING_REPO_ACCESS = "missing_repo_access"
    TOKEN_INVALID = "token_invalid"
    RATE_LIMITED = "rate_limited"
    TRANSIENT_ERROR = "transient_error"
    PROVIDER_ERROR = "provider_error"


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
    authorization_reason: AuthorizationReason = AuthorizationReason.PROVIDER_ERROR
    run_ready: bool
    owner_user_id: str | None = None
    token_owner_login: str | None = None


class RepositoryRevalidateRequest(BaseModel):
    repository_id: str = Field(min_length=1)
    provider: str = Field(pattern="^(github|gitlab)$")


class RepositoryRevalidateResponse(BaseModel):
    repository_id: str
    provider: str = Field(pattern="^(github|gitlab)$")
    authorization_status: AuthorizationStatus
    authorization_reason: AuthorizationReason
    run_ready: bool
    owner_user_id: str | None = None


class RepositoryAnalysisRequest(BaseModel):
    repository_url: str = Field(min_length=1)


class RepositoryCommitInsight(BaseModel):
    sha: str
    message: str
    author: str
    committed_at: str
    url: str


class RepositoryLanguageStat(BaseModel):
    language: str
    bytes: int
    percentage: float


class RepositoryHealthSummary(BaseModel):
    score: int
    summary: str


class RepositoryAnalysisResponse(BaseModel):
    provider: str = Field(pattern="^github$")
    repository_url: str
    repository_name: str
    description: str | None = None
    default_branch: str
    stars: int
    forks: int
    watchers: int
    open_issues: int
    contributor_count: int
    archived: bool
    has_readme: bool
    file_count: int = 0
    repository_size_bytes: int = 0
    primary_language: str | None = None
    languages: list[RepositoryLanguageStat]
    topics: list[str]
    recent_commits: list[RepositoryCommitInsight]
    pushed_at: str | None = None
    health: RepositoryHealthSummary
