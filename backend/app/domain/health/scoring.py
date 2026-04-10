from __future__ import annotations

MAINTAINABILITY_WEIGHT = 0.45
COMPLEXITY_WEIGHT = 0.35
VOLATILITY_WEIGHT = 0.20


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _normalize_maintainability(maintainability_index: float) -> float:
    return clamp01(maintainability_index / 100.0)


def _normalize_complexity(complexity: float) -> float:
    # Lower complexity is healthier; 50+ is treated as worst-case.
    return clamp01(1.0 - (complexity / 50.0))


def _normalize_volatility(volatility: float) -> float:
    # Lower volatility is healthier.
    return clamp01(1.0 - volatility)


def score_component(
    *,
    component_id: str,
    maintainability_index: float,
    complexity: float,
    volatility: float,
    contributors: list[str] | None = None,
) -> dict:
    maintainability_normalized = _normalize_maintainability(maintainability_index)
    complexity_normalized = _normalize_complexity(complexity)
    volatility_normalized = _normalize_volatility(volatility)

    weighted_score = (
        maintainability_normalized * MAINTAINABILITY_WEIGHT
        + complexity_normalized * COMPLEXITY_WEIGHT
        + volatility_normalized * VOLATILITY_WEIGHT
    )

    factors = [
        {
            "name": "maintainability",
            "weight": MAINTAINABILITY_WEIGHT,
            "raw_value": float(maintainability_index),
            "normalized_value": maintainability_normalized,
            "direction": "positive",
        },
        {
            "name": "complexity",
            "weight": COMPLEXITY_WEIGHT,
            "raw_value": float(complexity),
            "normalized_value": complexity_normalized,
            "direction": "negative",
        },
        {
            "name": "volatility",
            "weight": VOLATILITY_WEIGHT,
            "raw_value": float(volatility),
            "normalized_value": volatility_normalized,
            "direction": "negative",
        },
    ]

    merged_contributors = list(contributors or [])
    if "weighted_health_score" not in merged_contributors:
        merged_contributors.append("weighted_health_score")

    return {
        "component_id": component_id,
        "score": round(clamp01(weighted_score) * 100.0, 2),
        "contributors": merged_contributors,
        "factors": factors,
    }
