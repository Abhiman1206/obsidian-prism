from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.domain.business.translation import (  # noqa: E402
    DEFAULT_BUSINESS_ASSUMPTIONS,
    translate_risk_to_business_impact,
)


def _risk_rows() -> list[dict]:
    return [
        {
            "component_id": "src/gamma.py",
            "risk_probability": 0.72,
            "confidence": 0.60,
        },
        {
            "component_id": "src/alpha.py",
            "risk_probability": 0.72,
            "confidence": 0.60,
        },
        {
            "component_id": "src/core.py",
            "risk_probability": 0.93,
            "confidence": 0.88,
        },
    ]


def test_translation_includes_expected_time_and_cost_fields() -> None:
    translated = translate_risk_to_business_impact(_risk_rows())

    assert len(translated) == 3

    required_fields = {
        "component_id",
        "expected_engineering_hours",
        "expected_downtime_hours",
        "expected_total_cost",
        "cost_drivers",
    }
    assert required_fields.issubset(translated[0].keys())

    for row in translated:
        assert row["expected_engineering_hours"] >= 0
        assert row["expected_downtime_hours"] >= 0
        assert row["expected_total_cost"] >= 0
        assert isinstance(row["cost_drivers"], list)


def test_assumption_overrides_change_outputs_and_are_deterministic() -> None:
    base = translate_risk_to_business_impact(_risk_rows())
    overrides = {
        "engineering_hourly_rate": DEFAULT_BUSINESS_ASSUMPTIONS["engineering_hourly_rate"] * 2,
        "downtime_hourly_cost": DEFAULT_BUSINESS_ASSUMPTIONS["downtime_hourly_cost"] * 2,
    }
    overridden = translate_risk_to_business_impact(_risk_rows(), assumptions=overrides)
    overridden_again = translate_risk_to_business_impact(_risk_rows(), assumptions=overrides)

    assert overridden == overridden_again

    base_cost_by_component = {row["component_id"]: row["expected_total_cost"] for row in base}
    for row in overridden:
        assert row["expected_total_cost"] > base_cost_by_component[row["component_id"]]


def test_translation_is_sorted_by_total_cost_desc_then_component_id_asc() -> None:
    translated = translate_risk_to_business_impact(_risk_rows())

    ordered_pairs = [
        (row["expected_total_cost"], row["component_id"])
        for row in translated
    ]
    assert ordered_pairs == sorted(ordered_pairs, key=lambda item: (-item[0], item[1]))
