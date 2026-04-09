from __future__ import annotations

from datetime import datetime, timezone

from app.domain.risk.forecasting import forecast_component_risk


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_risk_forecasting(run_id: str, repository_id: str, feature_rows: list[dict]) -> list[dict]:
    forecasted_at = _utc_timestamp()
    rows: list[dict] = []

    for feature_row in feature_rows:
        forecast = forecast_component_risk(feature_row)
        rows.append(
            {
                **forecast,
                "run_id": run_id,
                "repository_id": repository_id,
                "forecasted_at": forecasted_at,
            }
        )

    return rows