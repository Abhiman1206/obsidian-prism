from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.domain.contracts import (  # noqa: E402
    ComponentProfile,
    ExecutiveReportSummary,
    HealthScore,
    RiskForecast,
)


def test_backend_contract_exports_exist() -> None:
    assert ComponentProfile is not None
    assert HealthScore is not None
    assert RiskForecast is not None
    assert ExecutiveReportSummary is not None


def test_risk_forecast_has_expected_fields() -> None:
    fields = set(RiskForecast.model_fields.keys())
    assert {
        "component_id",
        "horizon_days",
        "risk_probability",
        "confidence",
        "top_signals",
    }.issubset(fields)
