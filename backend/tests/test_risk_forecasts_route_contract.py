from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient

from app.main import app
from app.workers.risk_forecasting import persist_risk_forecasts


def test_risk_forecasts_route_returns_ranked_records_for_run() -> None:
    persist_risk_forecasts(
        [
            {
                "component_id": "src/beta.py",
                "horizon_days": 90,
                "risk_probability": 0.72,
                "confidence": 0.82,
                "top_signals": [
                    {"signal_name": "health_risk", "contribution_strength": 0.45},
                    {"signal_name": "contributor_churn", "contribution_strength": 0.22},
                ],
                "run_id": "run-risk-1",
                "repository_id": "repo-1",
                "forecasted_at": "2026-04-10T00:00:00Z",
            },
            {
                "component_id": "src/alpha.py",
                "horizon_days": 90,
                "risk_probability": 0.72,
                "confidence": 0.91,
                "top_signals": [
                    {"signal_name": "health_risk", "contribution_strength": 0.47},
                    {"signal_name": "defect_signal", "contribution_strength": 0.18},
                ],
                "run_id": "run-risk-1",
                "repository_id": "repo-1",
                "forecasted_at": "2026-04-10T00:00:00Z",
            },
            {
                "component_id": "src/core.py",
                "horizon_days": 90,
                "risk_probability": 0.91,
                "confidence": 0.77,
                "top_signals": [
                    {"signal_name": "health_risk", "contribution_strength": 0.5},
                    {"signal_name": "contributor_churn", "contribution_strength": 0.25},
                ],
                "run_id": "run-risk-1",
                "repository_id": "repo-1",
                "forecasted_at": "2026-04-10T00:00:00Z",
            },
        ]
    )

    client = TestClient(app)
    response = client.get("/api/risk-forecasts/run-risk-1")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)

    ordered_components = [row["component_id"] for row in payload]
    assert ordered_components == ["src/core.py", "src/alpha.py", "src/beta.py"]

    required_fields = {
        "component_id",
        "horizon_days",
        "risk_probability",
        "confidence",
        "top_signals",
        "run_id",
        "repository_id",
        "forecasted_at",
    }
    assert required_fields.issubset(payload[0].keys())
    assert {"signal_name", "contribution_strength"}.issubset(payload[0]["top_signals"][0].keys())


def test_risk_forecasts_route_returns_empty_list_for_unknown_run() -> None:
    client = TestClient(app)

    response = client.get("/api/risk-forecasts/unknown-run")

    assert response.status_code == 200
    assert response.json() == []
