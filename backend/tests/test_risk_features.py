from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.domain.risk.features import build_risk_features


def _sample_health_rows() -> list[dict]:
    return [
        {
            "component_id": "src/alpha.py",
            "score": 60.0,
            "contributors": ["alice@example.com"],
            "run_id": "run-123",
            "repository_id": "repo-123",
            "measured_at": "2026-04-10T00:00:00Z",
        },
        {
            "component_id": "src/beta.py",
            "score": 82.0,
            "contributors": ["bob@example.com"],
            "run_id": "run-123",
            "repository_id": "repo-123",
            "measured_at": "2026-04-10T00:00:00Z",
        },
    ]


def _sample_ingestion_payload() -> dict:
    return {
        "churn": [
            {
                "contributor": "alice@example.com",
                "commits_last_30d": 8,
                "files_touched_last_30d": 12,
            },
            {
                "contributor": "bob@example.com",
                "commits_last_30d": 4,
                "files_touched_last_30d": 5,
            },
        ],
        "cadence": {
            "issue_opened_count": 7,
            "issue_closed_count": 3,
            "deployment_count": 2,
        },
    }


def test_feature_rows_include_required_fields_and_90_day_horizon() -> None:
    rows = build_risk_features(_sample_health_rows(), _sample_ingestion_payload())

    assert len(rows) == 2
    required_keys = {
        "component_id",
        "horizon_days",
        "health_score",
        "contributor_churn_intensity",
        "deployment_cadence",
        "defect_signal_proxy",
        "feature_risk_pressure",
    }

    for row in rows:
        assert row["horizon_days"] == 90
        assert required_keys.issubset(row.keys())


def test_features_are_deterministically_sorted_by_pressure_then_component() -> None:
    rows = build_risk_features(_sample_health_rows(), _sample_ingestion_payload())

    ordered_components = [row["component_id"] for row in rows]
    assert ordered_components == ["src/alpha.py", "src/beta.py"]

    pressures = [round(row["feature_risk_pressure"], 4) for row in rows]
    assert pressures == [0.57, 0.3225]


def test_feature_values_are_stable_to_four_decimals_for_identical_inputs() -> None:
    first = build_risk_features(_sample_health_rows(), _sample_ingestion_payload())
    second = build_risk_features(_sample_health_rows(), _sample_ingestion_payload())

    first_snapshot = [
        {
            "component_id": row["component_id"],
            "contributor_churn_intensity": round(row["contributor_churn_intensity"], 4),
            "deployment_cadence": round(row["deployment_cadence"], 4),
            "defect_signal_proxy": round(row["defect_signal_proxy"], 4),
            "feature_risk_pressure": round(row["feature_risk_pressure"], 4),
        }
        for row in first
    ]
    second_snapshot = [
        {
            "component_id": row["component_id"],
            "contributor_churn_intensity": round(row["contributor_churn_intensity"], 4),
            "deployment_cadence": round(row["deployment_cadence"], 4),
            "defect_signal_proxy": round(row["defect_signal_proxy"], 4),
            "feature_risk_pressure": round(row["feature_risk_pressure"], 4),
        }
        for row in second
    ]

    assert first_snapshot == second_snapshot
    assert first_snapshot == [
        {
            "component_id": "src/alpha.py",
            "contributor_churn_intensity": 1.0,
            "deployment_cadence": 0.1,
            "defect_signal_proxy": 0.2,
            "feature_risk_pressure": 0.57,
        },
        {
            "component_id": "src/beta.py",
            "contributor_churn_intensity": 0.45,
            "deployment_cadence": 0.1,
            "defect_signal_proxy": 0.2,
            "feature_risk_pressure": 0.3225,
        },
    ]
