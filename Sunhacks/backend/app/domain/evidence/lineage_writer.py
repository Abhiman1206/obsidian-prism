from datetime import datetime, timezone
import uuid

from app.domain.evidence.repository import LineageRepository
from app.domain.evidence.schema import LineageRecord


class LineageWriter:
    def __init__(self, repository: LineageRepository) -> None:
        self._repository = repository

    def write_lineage(self, run_id: str, repository_id: str, artifacts: list[dict]) -> list[LineageRecord]:
        records: list[LineageRecord] = []
        for artifact in artifacts:
            record = LineageRecord(
                lineage_id=f"lin-{run_id}-{uuid.uuid4().hex[:12]}",
                run_id=run_id,
                repository_id=repository_id,
                artifact_type=artifact["artifact_type"],
                artifact_id=artifact["artifact_id"],
                source_provider=artifact["source_provider"],
                source_locator=artifact["source_locator"],
                claim_ref=artifact["claim_ref"],
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            self._repository.add(record)
            records.append(record)

        return records
