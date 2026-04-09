from __future__ import annotations


class HealthScoreRepository:
    def __init__(self) -> None:
        self._records: list[dict] = []

    def add_many(self, records: list[dict]) -> None:
        self._records.extend(records)

    def get_by_run(self, run_id: str) -> list[dict]:
        return [record for record in self._records if record.get("run_id") == run_id]


HEALTH_SCORE_REPOSITORY = HealthScoreRepository()
