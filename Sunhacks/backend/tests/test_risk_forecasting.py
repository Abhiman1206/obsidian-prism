from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.domain.risk.forecasting import forecast_component_risk


def _feature_rows() -> tuple[dict, dict, dict]:
    low = {
        "component_id": "src/low.py",
        "horizon_days": 90,
        "health_score": 0.9,
        "contributor_churn_intensity": 0.1,
        "deployment_cadence": 0.8,
        "defect_signal_proxy": 0.05,
        "feature_risk_pressure": 0.18,
    }
    medium = {
        "component_id": "src/medium.py",
        "horizon_days": 90,
        "health_score": 0.65,
        "contributor_churn_intensity": 0.45,
        "deployment_cadence": 0.4,
        "defect_signal_proxy": 0.2,
        "feature_risk_pressure": 0.46,
    }
    high = {
        "component_id": "src/high.py",
        "horizon_days": 90,
        "health_score": 0.35,
        "contributor_churn_intensity": 0.9,
        "deployment_cadence": 0.1,
        "defect_signal_proxy": 0.55,
        "feature_risk_pressure": 0.82,
    }
    return low, medium, high


def test_forecast_output_contains_probability_confidence_and_ranked_signals() -> None:
    _, _, high = _feature_rows()

    forecast = forecast_component_risk(high)

    assert 0 <= forecast["risk_probability"] <= 1
    assert 0 <= forecast["confidence"] <= 1

    top_signals = forecast["top_signals"]
    assert isinstance(top_signals, list)
    assert len(top_signals) >= 3
    assert {"signal_name", "contribution_strength"}.issubset(top_signals[0].keys())

    strengths = [signal["contribution_strength"] for signal in top_signals]
    assert strengths == sorted(strengths, reverse=True)


def test_higher_feature_pressure_yields_higher_probability() -> None:
    low, medium, high = _feature_rows()

    low_forecast = forecast_component_risk(low)
    medium_forecast = forecast_component_risk(medium)
    high_forecast = forecast_component_risk(high)

    assert low_forecast["risk_probability"] < medium_forecast["risk_probability"] < high_forecast["risk_probability"]


def test_confidence_decreases_when_feature_completeness_is_low() -> None:
    _, medium, _ = _feature_rows()
    incomplete = {
        "component_id": "src/incomplete.py",
        "horizon_days": 90,
        "feature_risk_pressure": medium["feature_risk_pressure"],
        "health_score": medium["health_score"],
    }

    complete_forecast = forecast_component_risk(medium)
    incomplete_forecast = forecast_component_risk(incomplete)

    assert incomplete_forecast["confidence"] < complete_forecast["confidence"]
