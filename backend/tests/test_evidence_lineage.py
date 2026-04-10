from app.domain.evidence.lineage_writer import LineageWriter
from app.domain.evidence.repository import LineageRepository
from app.domain.evidence.schema import LineageRecord



def test_lineage_writer_persists_one_record_per_artifact() -> None:
    repo = LineageRepository()
    writer = LineageWriter(repo)

    records = writer.write_lineage(
        run_id="run-001",
        repository_id="repo-acme-platform",
        artifacts=[
            {
                "artifact_type": "commit",
                "artifact_id": "c1",
                "source_provider": "github",
                "source_locator": "https://github.com/acme/platform/commit/c1",
                "claim_ref": "claim-1",
            },
            {
                "artifact_type": "cadence",
                "artifact_id": "cad-1",
                "source_provider": "pydriller",
                "source_locator": "pydriller://repo-acme-platform/cad-1",
                "claim_ref": "claim-2",
            },
        ],
    )

    assert len(records) == 2
    assert records[0].run_id == "run-001"
    assert records[1].artifact_type == "cadence"



def test_lineage_repository_queries_by_run_id() -> None:
    repo = LineageRepository()
    rec = LineageRecord(
        lineage_id="lin-1",
        run_id="run-001",
        repository_id="repo-acme-platform",
        artifact_type="commit",
        artifact_id="c1",
        source_provider="github",
        source_locator="https://github.com/acme/platform/commit/c1",
        claim_ref="claim-1",
        created_at="2026-04-10T00:00:00Z",
    )
    repo.add(rec)

    found = repo.get_lineage(run_id="run-001")

    assert len(found) == 1
    assert found[0].lineage_id == "lin-1"
