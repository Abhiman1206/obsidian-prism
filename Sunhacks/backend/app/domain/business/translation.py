from __future__ import annotations

from typing import Any

DEFAULT_BUSINESS_ASSUMPTIONS: dict[str, float] = {
    "engineering_hours_multiplier": 36.0,
    "downtime_hours_multiplier": 10.0,
    "engineering_hourly_rate": 140.0,
    "downtime_hourly_cost": 1800.0,
}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def _merged_assumptions(overrides: dict | None) -> dict[str, float]:
    assumptions = dict(DEFAULT_BUSINESS_ASSUMPTIONS)
    if not overrides:
        return assumptions

    for key, value in overrides.items():
        if key in assumptions:
            assumptions[key] = _safe_float(value, assumptions[key])

    return assumptions


def _cost_drivers(engineering_cost: float, downtime_cost: float) -> list[str]:
    pairs = [
        ("downtime_exposure", downtime_cost),
        ("engineering_effort", engineering_cost),
    ]
    pairs.sort(key=lambda item: (-item[1], item[0]))
    return [label for label, _ in pairs]


def translate_risk_to_business_impact(risk_rows: list[dict], assumptions: dict | None = None) -> list[dict]:
    merged = _merged_assumptions(assumptions)

    translated: list[dict] = []
    for row in risk_rows:
        probability = _clamp(_safe_float(row.get("risk_probability")))
        confidence = _clamp(_safe_float(row.get("confidence")))

        expected_engineering_hours = round(
            probability * confidence * merged["engineering_hours_multiplier"],
            2,
        )
        expected_downtime_hours = round(
            probability * (0.5 + (0.5 * confidence)) * merged["downtime_hours_multiplier"],
            2,
        )

        engineering_cost = expected_engineering_hours * merged["engineering_hourly_rate"]
        downtime_cost = expected_downtime_hours * merged["downtime_hourly_cost"]
        expected_total_cost = round(engineering_cost + downtime_cost, 2)

        translated.append(
            {
                "component_id": str(row.get("component_id", "")),
                "expected_engineering_hours": expected_engineering_hours,
                "expected_downtime_hours": expected_downtime_hours,
                "expected_total_cost": expected_total_cost,
                "cost_drivers": _cost_drivers(engineering_cost, downtime_cost),
            }
        )

    return sorted(
        translated,
        key=lambda item: (-float(item["expected_total_cost"]), item["component_id"]),
    )
