from collections.abc import Callable
from typing import Any, TypeVar

from app.infra.providers.errors import ProviderRequestError
from app.infra.secrets.provider_credentials import ProviderCredentialBundle

T = TypeVar("T")


class BaseProviderClient:
    def __init__(self, timeout_seconds: int = 10, max_pages: int = 200) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")
        if max_pages <= 0:
            raise ValueError("max_pages must be greater than zero")

        self.timeout_seconds = timeout_seconds
        self.max_pages = max_pages

    def paginate(self, fetch_page: Callable[[Any], dict], initial_cursor: Any = None) -> list[dict]:
        cursor = initial_cursor
        pages = 0
        items: list[dict] = []

        while pages < self.max_pages:
            batch = fetch_page(cursor)
            batch_items = batch.get("items", [])
            items.extend(batch_items)

            cursor = batch.get("next_cursor")
            pages += 1
            if cursor is None:
                break

        return items

    def build_auth_headers(self, credentials: ProviderCredentialBundle) -> dict[str, str]:
        if credentials.provider == "github":
            return {
                "Authorization": f"Bearer {credentials.token}",
                "Accept": "application/json",
            }

        return {
            "PRIVATE-TOKEN": credentials.token,
            "Accept": "application/json",
        }

    def run_with_retry(self, operation: Callable[[], T], retries: int = 3) -> T:
        if retries <= 0:
            raise ValueError("retries must be greater than zero")

        attempt = 0
        while True:
            try:
                return operation()
            except ProviderRequestError as exc:
                attempt += 1
                should_retry = exc.error_code in {"transient_error", "rate_limited", "upstream_error"}
                if not should_retry or attempt >= retries:
                    raise
            except Exception:
                attempt += 1
                if attempt >= retries:
                    raise
