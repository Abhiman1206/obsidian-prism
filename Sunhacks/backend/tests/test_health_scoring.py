from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.domain.health.scoring import score_component


def test_score_is_in_0_to_100_range() -> None:
    scored = score_component(
        component_id="src/service/a.py",
        maintainability_index=85.0,
        complexity=4.0,
        volatility=0.2,
    )

    assert 0 <= scored["score"] <= 100


def test_weights_are_fixed_and_factor_names_are_expected() -> None:
    scored = score_component(
        component_id="src/service/a.py",
        maintainability_index=85.0,
        complexity=4.0,
        volatility=0.2,
    )

    factors = scored["factors"]
    names = {factor["name"] for factor in factors}
    weights = {factor["name"]: factor["weight"] for factor in factors}

    assert names == {"maintainability", "complexity", "volatility"}
    assert weights["maintainability"] == 0.45
    assert weights["complexity"] == 0.35
    assert weights["volatility"] == 0.20


def test_normalized_values_are_clamped_to_unit_interval() -> None:
    scored = score_component(
        component_id="src/service/a.py",
        maintainability_index=500.0,
        complexity=-50.0,
        volatility=99.0,
    )

    for factor in scored["factors"]:
        assert 0 <= factor["normalized_value"] <= 1


def test_healthier_metrics_produce_higher_score() -> None:
    healthier = score_component(
        component_id="src/service/healthy.py",
        maintainability_index=90.0,
        complexity=2.0,
        volatility=0.05,
    )
    riskier = score_component(
        component_id="src/service/risky.py",
        maintainability_index=20.0,
        complexity=45.0,
        volatility=0.95,
    )

    assert healthier["score"] > riskier["score"]
