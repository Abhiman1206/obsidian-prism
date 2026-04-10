from collections.abc import Callable


def persist_ingestion_artifacts(records: list[dict], writer: Callable[[list[dict]], None]) -> None:
    writer(records)
