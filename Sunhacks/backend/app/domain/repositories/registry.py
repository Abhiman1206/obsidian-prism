from urllib.parse import urlparse

from app.api.schemas.repository import (
    AuthorizationReason,
    AuthorizationStatus,
    RepositoryRegistrationRequest,
    RepositoryRegistrationResponse,
    RepositoryRevalidateRequest,
    RepositoryRevalidateResponse,
)
from app.domain.repositories.connection_repository import REPOSITORY_CONNECTION_REPOSITORY, RepositoryConnectionRecord, utc_now_iso
from app.infra.secrets.provider_credentials import ProviderCredentialsService


class RepositoryRegistryService:
    def __init__(self, credentials_service: ProviderCredentialsService | None = None) -> None:
        self._credentials_service = credentials_service or ProviderCredentialsService()

    def register_repository(
        self,
        payload: RepositoryRegistrationRequest,
        current_user_id: str,
    ) -> RepositoryRegistrationResponse:
        credentials = self._credentials_service.prepare(payload.auth)
        repository_slug = self._parse_repository_slug(payload.provider, payload.repository_url)
        authorization = self._credentials_service.validate_repository_access_detailed(credentials, repository_slug)
        authorized = authorization.authorized
        status = AuthorizationStatus.AUTHORIZED if authorized else AuthorizationStatus.FAILED
        reason = self._to_reason(authorization.reason)

        repository_id = payload.repository_name.replace("/", "-").replace(" ", "-")
        repository_id = f"repo-{repository_id}"
        now = utc_now_iso()

        REPOSITORY_CONNECTION_REPOSITORY.upsert(
            RepositoryConnectionRecord(
                repository_id=repository_id,
                provider=payload.provider,
                repository_url=payload.repository_url,
                repository_slug=repository_slug,
                owner_user_id=current_user_id,
                token_owner_login=authorization.token_owner_login,
                provider_user_id=authorization.provider_user_id,
                token_ciphertext=self._credentials_service.encrypt_token(credentials.token),
                scopes=credentials.scopes,
                authorization_status=status.value,
                authorization_reason=reason.value,
                run_ready=authorized,
                created_at=now,
                updated_at=now,
            )
        )

        return RepositoryRegistrationResponse(
            repository_id=repository_id,
            provider=payload.provider,
            repository_url=payload.repository_url,
            authorization_status=status,
            authorization_reason=reason,
            run_ready=authorized,
            owner_user_id=current_user_id,
            token_owner_login=authorization.token_owner_login,
        )

    def revalidate_repository_access(
        self,
        payload: RepositoryRevalidateRequest,
        current_user_id: str,
    ) -> RepositoryRevalidateResponse:
        existing = REPOSITORY_CONNECTION_REPOSITORY.get_for_owner(payload.repository_id, current_user_id)
        if existing is None:
            raise ValueError("Repository connection not found for caller")

        credentials = self._credentials_service.get_runtime_bundle(payload.repository_id)
        if credentials is None:
            return RepositoryRevalidateResponse(
                repository_id=payload.repository_id,
                provider=payload.provider,
                authorization_status=AuthorizationStatus.FAILED,
                authorization_reason=AuthorizationReason.TOKEN_INVALID,
                run_ready=False,
                owner_user_id=existing.owner_user_id,
            )

        authorization = self._credentials_service.validate_repository_access_detailed(
            credentials,
            existing.repository_slug,
        )
        authorized = authorization.authorized
        status = AuthorizationStatus.AUTHORIZED if authorized else AuthorizationStatus.FAILED
        reason = self._to_reason(authorization.reason)
        now = utc_now_iso()

        REPOSITORY_CONNECTION_REPOSITORY.upsert(
            RepositoryConnectionRecord(
                repository_id=existing.repository_id,
                provider=existing.provider,
                repository_url=existing.repository_url,
                repository_slug=existing.repository_slug,
                owner_user_id=existing.owner_user_id,
                token_owner_login=authorization.token_owner_login or existing.token_owner_login,
                provider_user_id=authorization.provider_user_id or existing.provider_user_id,
                token_ciphertext=existing.token_ciphertext,
                scopes=existing.scopes,
                authorization_status=status.value,
                authorization_reason=reason.value,
                run_ready=authorized,
                created_at=existing.created_at,
                updated_at=now,
            )
        )

        return RepositoryRevalidateResponse(
            repository_id=existing.repository_id,
            provider=existing.provider,
            authorization_status=status,
            authorization_reason=reason,
            run_ready=authorized,
            owner_user_id=existing.owner_user_id,
        )

    def _to_reason(self, raw: str) -> AuthorizationReason:
        try:
            return AuthorizationReason(raw)
        except ValueError:
            return AuthorizationReason.PROVIDER_ERROR

    def _parse_repository_slug(self, provider: str, repository_url: str) -> str:
        cleaned = repository_url.strip()
        if not cleaned:
            return ""

        if cleaned.startswith("git@"):
            slug = cleaned.split(":", 1)[-1]
        else:
            parsed = urlparse(cleaned)
            slug = parsed.path

        slug = slug.strip("/")
        if slug.endswith(".git"):
            slug = slug[:-4]

        if provider == "github":
            parts = [part for part in slug.split("/") if part]
            return "/".join(parts[:2]) if len(parts) >= 2 else slug

        return slug
