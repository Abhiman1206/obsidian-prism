from __future__ import annotations

from dataclasses import dataclass

import httpx


@dataclass(slots=True)
class ProviderRequestError(Exception):
    provider: str
    operation: str
    error_code: str
    status_code: int | None = None
    detail: str | None = None

    def __str__(self) -> str:
        status = f" status={self.status_code}" if self.status_code is not None else ""
        suffix = f" detail={self.detail}" if self.detail else ""
        return f"{self.provider}:{self.operation}:{self.error_code}{status}{suffix}"

    def to_safe_message(self) -> str:
        if self.error_code == "auth_failed":
            return f"{self.provider} authentication failed for {self.operation}"
        if self.error_code == "rate_limited":
            return f"{self.provider} rate limit reached for {self.operation}"
        if self.error_code == "transient_error":
            return f"{self.provider} transient network error during {self.operation}"
        if self.error_code == "upstream_error":
            return f"{self.provider} upstream error during {self.operation}"
        return f"{self.provider} provider call failed during {self.operation}"


def map_httpx_error(provider: str, operation: str, exc: Exception) -> ProviderRequestError:
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        detail = exc.response.text[:200] if exc.response.text else None
        if status in {401, 403}:
            return ProviderRequestError(provider, operation, "auth_failed", status, detail)
        if status == 429:
            return ProviderRequestError(provider, operation, "rate_limited", status, detail)
        if status >= 500:
            return ProviderRequestError(provider, operation, "upstream_error", status, detail)
        return ProviderRequestError(provider, operation, "provider_error", status, detail)

    if isinstance(exc, (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError, httpx.ConnectTimeout)):
        return ProviderRequestError(provider, operation, "transient_error", None, str(exc))

    return ProviderRequestError(provider, operation, "provider_error", None, str(exc))
