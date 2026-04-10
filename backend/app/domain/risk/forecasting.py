from __future__ import annotations


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def _signal_contributions(feature_row: dict) -> list[dict]:
    health_score = _clamp(_safe_float(feature_row.get("health_score", 0.0)))
    churn = _clamp(_safe_float(feature_row.get("contributor_churn_intensity", 0.0)))
    defect = _clamp(_safe_float(feature_row.get("defect_signal_proxy", 0.0)))
    deployment = _clamp(_safe_float(feature_row.get("deployment_cadence", 0.0)))

    contributions = [
        {"signal_name": "health_risk", "contribution_strength": round(0.45 * (1.0 - health_score), 4)},
        {"signal_name": "contributor_churn", "contribution_strength": round(0.25 * churn, 4)},
        {"signal_name": "defect_signal", "contribution_strength": round(0.20 * defect, 4)},
        {
            "signal_name": "deployment_instability",
            "contribution_strength": round(0.10 * (1.0 - deployment), 4),
        },
    ]

    return sorted(contributions, key=lambda signal: (-signal["contribution_strength"], signal["signal_name"]))


def _feature_completeness(feature_row: dict) -> float:
    required = [
        "health_score",
        "contributor_churn_intensity",
        "deployment_cadence",
        "defect_signal_proxy",
        "feature_risk_pressure",
    ]
    present = sum(1 for key in required if key in feature_row and feature_row.get(key) is not None)
    return present / len(required)


def forecast_component_risk(feature_row: dict) -> dict:
    pressure = _clamp(_safe_float(feature_row.get("feature_risk_pressure", 0.0)))
    contributions = _signal_contributions(feature_row)
    contribution_total = sum(signal["contribution_strength"] for signal in contributions)

    risk_probability = _clamp(round((0.65 * pressure) + (0.35 * contribution_total), 4))
    completeness = _feature_completeness(feature_row)
    spread = abs(pressure - 0.5) * 2.0
    confidence = _clamp(round((0.60 * completeness) + (0.40 * spread), 4))

    return {
        "component_id": str(feature_row.get("component_id", "")),
        "horizon_days": int(feature_row.get("horizon_days", 90)),
        "risk_probability": risk_probability,
        "confidence": confidence,
        "top_signals": contributions,
    }