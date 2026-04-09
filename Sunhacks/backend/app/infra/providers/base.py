from typing import Any, Callable


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
