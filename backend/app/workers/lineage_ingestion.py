from app.domain.evidence.lineage_writer import LineageWriter
from app.domain.evidence.repository import LineageRepository
from app.domain.evidence.schema import LineageRecord


LINEAGE_REPOSITORY = LineageRepository()
LINEAGE_WRITER = LineageWriter(LINEAGE_REPOSITORY)


def ingest_lineage_payload(run_id: str, repository_id: str, artifacts: list[dict]) -> list[LineageRecord]:
    return LINEAGE_WRITER.write_lineage(
        run_id=run_id,
        repository_id=repository_id,
        artifacts=artifacts,
    )
