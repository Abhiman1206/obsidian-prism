from dataclasses import dataclass

from app.api.schemas.provider_auth import ProviderAuthPayload


@dataclass(frozen=True)
class ProviderCredentialBundle:
    provider: str
    token: str
    scopes: tuple[str, ...]


class ProviderCredentialsService:
    def prepare(self, payload: ProviderAuthPayload) -> ProviderCredentialBundle:
        return ProviderCredentialBundle(
            provider=payload.provider,
            token=payload.access_token,
            scopes=tuple(payload.scopes),
        )

    def is_authorized(self, bundle: ProviderCredentialBundle) -> bool:
        return bool(bundle.token and bundle.scopes)
