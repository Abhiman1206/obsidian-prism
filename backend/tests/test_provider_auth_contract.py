from pydantic import ValidationError

from app.api.schemas.provider_auth import ProviderAuthPayload
from app.api.schemas.repository import RepositoryRegistrationRequest, RepositoryRegistrationResponse
from app.infra.secrets.provider_credentials import ProviderCredentialBundle, ProviderCredentialsService


def test_provider_auth_rejects_invalid_provider() -> None:
    try:
        ProviderAuthPayload(
            provider="bitbucket",
            access_token="token-123",
            scopes=["repo:read"],
        )
        assert False, "Expected validation error for invalid provider"
    except ValidationError:
        assert True


def test_provider_auth_requires_non_empty_scopes() -> None:
    try:
        ProviderAuthPayload(
            provider="github",
            access_token="token-123",
            scopes=[],
        )
        assert False, "Expected validation error for empty scopes"
    except ValidationError:
        assert True


def test_repository_registration_request_accepts_github_and_gitlab_only() -> None:
    payload = RepositoryRegistrationRequest(
        provider="gitlab",
        repository_url="https://gitlab.com/acme/platform",
        repository_name="acme/platform",
        auth=ProviderAuthPayload(
            provider="gitlab",
            access_token="token-123",
            scopes=["api"],
        ),
    )

    assert payload.provider == "gitlab"


def test_repository_registration_response_has_run_readiness_metadata() -> None:
    response = RepositoryRegistrationResponse(
        repository_id="repo-acme-platform",
        provider="github",
        repository_url="https://github.com/acme/platform",
        authorization_status="authorized",
        run_ready=True,
    )

    assert response.run_ready is True


def test_provider_auth_rejects_blank_access_token() -> None:
    try:
        ProviderAuthPayload(
            provider="github",
            access_token="   ",
            scopes=["repo:read"],
        )
        assert False, "Expected validation error for blank token"
    except ValidationError:
        assert True


def test_provider_credentials_prepare_trims_and_filters_scopes() -> None:
    service = ProviderCredentialsService()
    payload = ProviderAuthPayload(
        provider="gitlab",
        access_token="token-123",
        scopes=["api", " ", "read_repository"],
    )

    bundle = service.prepare(payload)

    assert bundle.provider == "gitlab"
    assert bundle.scopes == ("api", "read_repository")


def test_provider_credentials_is_authorized_requires_valid_token_and_scopes() -> None:
    service = ProviderCredentialsService()

    assert service.is_authorized(ProviderCredentialBundle(provider="github", token="token-123", scopes=("repo",)))
    assert service.is_authorized(ProviderCredentialBundle(provider="github", token="", scopes=("repo",))) is False
    assert service.is_authorized(ProviderCredentialBundle(provider="github", token="token-123", scopes=())) is False
