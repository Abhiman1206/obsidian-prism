from dataclasses import dataclass

from app.api.schemas.provider_auth import ProviderAuthPayload


@dataclass(frozen=True)
class ProviderCredentialBundle:
    provider: str
    token: str
    scopes: tuple[str, ...]


class ProviderCredentialsService:
    def prepare(self, payload: ProviderAuthPayload) -> ProviderCredentialBundle:
        scopes = tuple(scope.strip() for scope in payload.scopes if scope.strip())
        return ProviderCredentialBundle(
            provider=payload.provider,
            token=payload.access_token.strip(),
            scopes=scopes,
        )

    def is_authorized(self, bundle: ProviderCredentialBundle) -> bool:
        return bool(bundle.token and bundle.scopes)
