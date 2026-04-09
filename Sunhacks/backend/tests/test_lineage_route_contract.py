from fastapi.testclient import TestClient

from app.main import app
from app.workers.lineage_ingestion import ingest_lineage_payload



def test_lineage_route_returns_records_for_run() -> None:
    ingest_lineage_payload(
        run_id="run-xyz",
        repository_id="repo-acme-platform",
        artifacts=[
            {
                "artifact_type": "commit",
                "artifact_id": "c1",
                "source_provider": "github",
                "source_locator": "https://github.com/acme/platform/commit/c1",
                "claim_ref": "claim-1",
            }
        ],
    )

    client = TestClient(app)
    response = client.get("/api/lineage/run-xyz")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["run_id"] == "run-xyz"
    assert body[0]["artifact_type"] == "commit"



def test_lineage_route_returns_empty_list_for_unknown_run() -> None:
    client = TestClient(app)

    response = client.get("/api/lineage/unknown-run")

    assert response.status_code == 200
    assert response.json() == []
