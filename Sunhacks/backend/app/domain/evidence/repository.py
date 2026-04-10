from app.domain.evidence.schema import LineageRecord
from app.infra.database import get_db


class LineageRepository:
    def add(self, record: LineageRecord) -> None:
        conn = get_db()
        conn.execute(
            """INSERT OR REPLACE INTO lineage_records
               (lineage_id, run_id, repository_id, artifact_type, artifact_id,
                source_provider, source_locator, claim_ref, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                record.lineage_id,
                record.run_id,
                record.repository_id,
                record.artifact_type,
                record.artifact_id,
                record.source_provider,
                record.source_locator,
                record.claim_ref,
                record.created_at,
            ),
        )
        conn.commit()

    def get_lineage(self, run_id: str | None = None, repository_id: str | None = None) -> list[LineageRecord]:
        conn = get_db()
        conditions: list[str] = []
        params: list[str] = []
        if run_id is not None:
            conditions.append("run_id = ?")
            params.append(run_id)
        if repository_id is not None:
            conditions.append("repository_id = ?")
            params.append(repository_id)

        where = f" WHERE {' AND '.join(conditions)}" if conditions else ""
        rows = conn.execute(
            f"SELECT * FROM lineage_records{where} ORDER BY created_at ASC",
            params,
        ).fetchall()

        results: list[LineageRecord] = []
        for row in rows:
            results.append(
                LineageRecord(
                    lineage_id=row["lineage_id"],
                    run_id=row["run_id"],
                    repository_id=row["repository_id"],
                    artifact_type=row["artifact_type"],
                    artifact_id=row["artifact_id"],
                    source_provider=row["source_provider"],
                    source_locator=row["source_locator"],
                    claim_ref=row["claim_ref"],
                    created_at=row["created_at"],
                )
            )
        return results
