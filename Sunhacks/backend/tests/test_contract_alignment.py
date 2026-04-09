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


def _frontend_contracts_source() -> str:
    contracts_file = ROOT / "frontend" / "lib" / "contracts" / "index.ts"
    return contracts_file.read_text(encoding="utf-8")


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


def test_frontend_contracts_include_core_backend_fields() -> None:
    source = _frontend_contracts_source()

    assert "export type RunStatus = \"queued\" | \"running\" | \"succeeded\" | \"failed\";" in source
    assert "export interface HealthFactor" in source
    assert "factors: HealthFactor[];" in source

    for field in ComponentProfile.model_fields.keys():
        assert field in source

    for field in HealthScore.model_fields.keys():
        assert field in source

    for field in RiskForecast.model_fields.keys():
        assert field in source

    for field in ExecutiveReportSummary.model_fields.keys():
        assert field in source
