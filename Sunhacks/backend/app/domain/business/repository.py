from __future__ import annotations


class ExecutiveReportRepository:
    def __init__(self) -> None:
        self._records: list[dict] = []

    def add(self, record: dict) -> None:
        self._records.append(record)

    def get_by_run(self, run_id: str) -> list[dict]:
        filtered = [record for record in self._records if record.get("run_id") == run_id]
        return sorted(filtered, key=lambda record: str(record.get("generated_at", "")), reverse=True)


EXECUTIVE_REPORT_REPOSITORY = ExecutiveReportRepository()
