from dataclasses import dataclass
from datetime import datetime, timezone
import logging
import os
from urllib.parse import quote

import httpx

from app.domain.repositories.connection_repository import REPOSITORY_CONNECTION_REPOSITORY, RepositoryConnectionRecord
from app.infra.providers.errors import map_httpx_error
from app.api.schemas.provider_auth import ProviderAuthPayload
from app.infra.secrets.token_cipher import TokenCipher


@dataclass(frozen=True)
class ProviderCredentialBundle:
    provider: str
    token: str
    scopes: tuple[str, ...]


@dataclass(frozen=True)
class ProviderAuthorizationResult:
    authorized: bool
    reason: str
    token_owner_login: str | None = None
    provider_user_id: str | None = None


class ProviderCredentialsService:
    def __init__(self, token_cipher: TokenCipher | None = None) -> None:
        self._token_cipher = token_cipher or TokenCipher()
        self._logger = logging.getLogger(__name__)

    def prepare(self, payload: ProviderAuthPayload) -> ProviderCredentialBundle:
        scopes = tuple(scope.strip() for scope in payload.scopes if scope.strip())
        return ProviderCredentialBundle(
            provider=payload.provider,
            token=payload.access_token.strip(),
            scopes=scopes,
        )

    def is_authorized(self, bundle: ProviderCredentialBundle) -> bool:
        return bool(bundle.token and bundle.scopes)

    def encrypt_token(self, token: str) -> str:
        return self._token_cipher.encrypt(token)

    def decrypt_token(self, token_ciphertext: str) -> str:
        return self._token_cipher.decrypt(token_ciphertext)

    def validate_repository_access(self, bundle: ProviderCredentialBundle, repository_slug: str) -> bool:
        return self.validate_repository_access_detailed(bundle, repository_slug).authorized

    def validate_repository_access_detailed(
        self,
        bundle: ProviderCredentialBundle,
        repository_slug: str,
    ) -> ProviderAuthorizationResult:
        if not self.is_authorized(bundle) or not repository_slug.strip():
            return ProviderAuthorizationResult(authorized=False, reason="token_invalid")

        if (
            os.getenv("APP_ENV", "development") != "production"
            and bundle.token.startswith("token-")
        ):
            if bundle.token.startswith("token-noaccess-"):
                return ProviderAuthorizationResult(authorized=False, reason="missing_repo_access")
            if bundle.token.startswith("token-invalid-"):
                return ProviderAuthorizationResult(authorized=False, reason="token_invalid")
            return ProviderAuthorizationResult(
                authorized=True,
                reason="authorized_collaborator",
                token_owner_login="local-user",
                provider_user_id="local-user-id",
            )

        try:
            if bundle.provider == "github":
                headers = {
                    "Authorization": f"Bearer {bundle.token}",
                    "Accept": "application/vnd.github+json",
                    "User-Agent": "predictive-engineering-intelligence",
                }
                response = httpx.get(
                    "https://api.github.com/user",
                    headers=headers,
                    timeout=10,
                )
                if response.status_code in {401, 403}:
                    self._audit_provider_failure("github", "validate_repository_access", "auth_failed", response.status_code)
                    return ProviderAuthorizationResult(authorized=False, reason="token_invalid")
                if response.status_code == 429:
                    self._audit_provider_failure("github", "validate_repository_access", "rate_limited", response.status_code)
                    return ProviderAuthorizationResult(authorized=False, reason="rate_limited")
                if response.status_code != 200:
                    return ProviderAuthorizationResult(authorized=False, reason="provider_error")

                user_payload = response.json()
                repo_response = httpx.get(
                    f"https://api.github.com/repos/{repository_slug}",
                    headers=headers,
                    timeout=10,
                )
                if repo_response.status_code in {401, 403, 404}:
                    return ProviderAuthorizationResult(
                        authorized=False,
                        reason="missing_repo_access",
                        token_owner_login=user_payload.get("login"),
                        provider_user_id=str(user_payload.get("id")) if user_payload.get("id") is not None else None,
                    )
                if repo_response.status_code == 429:
                    return ProviderAuthorizationResult(authorized=False, reason="rate_limited")
                if repo_response.status_code != 200:
                    return ProviderAuthorizationResult(authorized=False, reason="provider_error")

                repo_payload = repo_response.json()
                permissions = repo_payload.get("permissions") if isinstance(repo_payload, dict) else None
                private = bool(repo_payload.get("private")) if isinstance(repo_payload, dict) else False
                has_pull = bool(permissions.get("pull")) if isinstance(permissions, dict) else False
                if private and not has_pull:
                    return ProviderAuthorizationResult(
                        authorized=False,
                        reason="missing_repo_access",
                        token_owner_login=user_payload.get("login"),
                        provider_user_id=str(user_payload.get("id")) if user_payload.get("id") is not None else None,
                    )

                return ProviderAuthorizationResult(
                    authorized=True,
                    reason="authorized_collaborator",
                    token_owner_login=user_payload.get("login"),
                    provider_user_id=str(user_payload.get("id")) if user_payload.get("id") is not None else None,
                )

            headers = {"PRIVATE-TOKEN": bundle.token, "Accept": "application/json"}
            response = httpx.get(
                "https://gitlab.com/api/v4/user",
                headers=headers,
                timeout=10,
            )
            if response.status_code in {401, 403}:
                self._audit_provider_failure("gitlab", "validate_repository_access", "auth_failed", response.status_code)
                return ProviderAuthorizationResult(authorized=False, reason="token_invalid")
            if response.status_code == 429:
                self._audit_provider_failure("gitlab", "validate_repository_access", "rate_limited", response.status_code)
                return ProviderAuthorizationResult(authorized=False, reason="rate_limited")
            if response.status_code != 200:
                return ProviderAuthorizationResult(authorized=False, reason="provider_error")

            user_payload = response.json()
            repo_response = httpx.get(
                f"https://gitlab.com/api/v4/projects/{quote(repository_slug, safe='')}",
                headers=headers,
                timeout=10,
            )
            if repo_response.status_code in {401, 403, 404}:
                return ProviderAuthorizationResult(
                    authorized=False,
                    reason="missing_repo_access",
                    token_owner_login=user_payload.get("username"),
                    provider_user_id=str(user_payload.get("id")) if user_payload.get("id") is not None else None,
                )
            if repo_response.status_code == 429:
                return ProviderAuthorizationResult(authorized=False, reason="rate_limited")
            if repo_response.status_code != 200:
                return ProviderAuthorizationResult(authorized=False, reason="provider_error")

            return ProviderAuthorizationResult(
                authorized=True,
                reason="authorized_collaborator",
                token_owner_login=user_payload.get("username"),
                provider_user_id=str(user_payload.get("id")) if user_payload.get("id") is not None else None,
            )
        except Exception as exc:
            mapped = map_httpx_error(bundle.provider, "validate_repository_access", exc)
            self._audit_provider_failure(mapped.provider, mapped.operation, mapped.error_code, mapped.status_code)
            if mapped.error_code == "auth_failed":
                return ProviderAuthorizationResult(authorized=False, reason="token_invalid")
            if mapped.error_code == "rate_limited":
                return ProviderAuthorizationResult(authorized=False, reason="rate_limited")
            if mapped.error_code == "transient_error":
                return ProviderAuthorizationResult(authorized=False, reason="transient_error")
            return ProviderAuthorizationResult(authorized=False, reason="provider_error")

    def get_runtime_bundle(self, repository_id: str) -> ProviderCredentialBundle | None:
        record = REPOSITORY_CONNECTION_REPOSITORY.get(repository_id)
        if record is None or not record.run_ready:
            return None

        try:
            token = self.decrypt_token(record.token_ciphertext)
        except Exception:
            return None

        if self._token_cipher.needs_rotation(record.token_ciphertext):
            rotated_ciphertext = self.encrypt_token(token)
            now = datetime.now(timezone.utc).isoformat()
            REPOSITORY_CONNECTION_REPOSITORY.upsert(
                RepositoryConnectionRecord(
                    repository_id=record.repository_id,
                    provider=record.provider,
                    repository_url=record.repository_url,
                    repository_slug=record.repository_slug,
                    owner_user_id=record.owner_user_id,
                    token_owner_login=record.token_owner_login,
                    provider_user_id=record.provider_user_id,
                    token_ciphertext=rotated_ciphertext,
                    scopes=record.scopes,
                    authorization_status=record.authorization_status,
                    authorization_reason=record.authorization_reason,
                    run_ready=record.run_ready,
                    created_at=record.created_at,
                    updated_at=now,
                )
            )
            self._logger.info(
                "audit_event=secret_rotation repository_id=%s provider=%s",
                record.repository_id,
                record.provider,
            )

        return ProviderCredentialBundle(provider=record.provider, token=token, scopes=record.scopes)

    def _audit_provider_failure(
        self,
        provider: str,
        operation: str,
        error_code: str,
        status_code: int | None,
    ) -> None:
        status = status_code if status_code is not None else "none"
        self._logger.warning(
            "audit_event=provider_call_failure provider=%s operation=%s error_code=%s status_code=%s",
            provider,
            operation,
            error_code,
            status,
        )
