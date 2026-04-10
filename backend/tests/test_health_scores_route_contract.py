from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient

from app.main import app
from app.workers.health_scoring import persist_health_scores


def test_health_scores_route_returns_records_for_run() -> None:
    persist_health_scores(
        [
            {
                "component_id": "src/service/core.py",
                "score": 82.5,
                "run_id": "run-health-1",
                "repository_id": "repo-1",
                "contributors": ["weighted_health_score"],
                "factors": [
                    {
                        "name": "maintainability",
                        "weight": 0.45,
                        "raw_value": 85.0,
                        "normalized_value": 0.85,
                        "direction": "positive",
                    }
                ],
                "measured_at": "2026-04-10T00:00:00Z",
            }
        ]
    )

    client = TestClient(app)
    response = client.get("/api/health-scores/run-health-1")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) >= 1

    record = payload[0]
    assert {
        "component_id",
        "score",
        "run_id",
        "repository_id",
        "contributors",
        "factors",
        "measured_at",
    }.issubset(record.keys())

    first_factor = record["factors"][0]
    assert {"name", "weight", "raw_value", "normalized_value", "direction"}.issubset(
        first_factor.keys()
    )


def test_health_scores_route_returns_empty_list_for_unknown_run() -> None:
    client = TestClient(app)

    response = client.get("/api/health-scores/unknown-run")

    assert response.status_code == 200
    assert response.json() == []
