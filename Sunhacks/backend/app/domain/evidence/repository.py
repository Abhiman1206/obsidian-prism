from app.domain.evidence.schema import LineageRecord


class LineageRepository:
    def __init__(self) -> None:
        self._records: list[LineageRecord] = []

    def add(self, record: LineageRecord) -> None:
        self._records.append(record)

    def get_lineage(self, run_id: str | None = None, repository_id: str | None = None) -> list[LineageRecord]:
        records = self._records
        if run_id is not None:
            records = [record for record in records if record.run_id == run_id]
        if repository_id is not None:
            records = [record for record in records if record.repository_id == repository_id]
        return records
