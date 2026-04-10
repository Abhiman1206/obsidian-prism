from app.api.schemas.repository import AuthorizationStatus, RepositoryRegistrationRequest, RepositoryRegistrationResponse
from app.infra.secrets.provider_credentials import ProviderCredentialsService


class RepositoryRegistryService:
    def __init__(self, credentials_service: ProviderCredentialsService | None = None) -> None:
        self._credentials_service = credentials_service or ProviderCredentialsService()

    def register_repository(self, payload: RepositoryRegistrationRequest) -> RepositoryRegistrationResponse:
        credentials = self._credentials_service.prepare(payload.auth)
        authorized = self._credentials_service.is_authorized(credentials)
        status = AuthorizationStatus.AUTHORIZED if authorized else AuthorizationStatus.FAILED

        repository_id = payload.repository_name.replace("/", "-").replace(" ", "-")
        repository_id = f"repo-{repository_id}"

        return RepositoryRegistrationResponse(
            repository_id=repository_id,
            provider=payload.provider,
            repository_url=payload.repository_url,
            authorization_status=status,
            run_ready=authorized,
        )
