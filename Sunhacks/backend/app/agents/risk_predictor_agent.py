"""Predictive Risk Agent — forecasts 90-day component failure risk.

PRD Role: Synthesizes historical bug frequencies, code complexity, and deployment
velocity to forecast which components are statistically most likely to fail or
degrade in the next 90 days.
"""

from __future__ import annotations

from typing import Any

from app.agents.base_agent import BaseSpecialistAgent
from app.agents.shared_memory import EpistemicMemory
from app.domain.risk.features import build_risk_features
from app.domain.risk.forecasting import forecast_component_risk


class RiskPredictorAgent(BaseSpecialistAgent):
    name = "risk_predictor_agent"
    role_description = (
        "You are a Predictive Risk specialist agent. Your job is to read health scores, "
        "churn patterns, and operational signals from shared memory and forecast which "
        "components are most likely to fail or degrade within the next 90 days. "
        "Produce a ranked list of components by risk probability with confidence scores "
        "and contributing signal breakdowns."
    )
    tools = []  # Pure computation — no external tools

    def execute_deterministic(self, memory: EpistemicMemory) -> dict[str, Any]:
        """Deterministic execution: build features and forecast risk."""
        from datetime import datetime, timezone

        health_rows = memory.read("health_rows", [])
        cadence_signals = memory.read("cadence_signals", {})
        churn = memory.read("churn", [])

        # Build ingestion payload shape expected by build_risk_features
        ingestion_payload = {
            "churn": churn,
            "cadence": cadence_signals,
        }

        # Build risk features from health + ingestion signals
        risk_features = build_risk_features(
            health_rows=health_rows,
            ingestion_payload=ingestion_payload,
            horizon_days=90,
        )

        # Forecast each component
        forecasted_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        forecasts: list[dict] = []
        for feature_row in risk_features:
            forecast = forecast_component_risk(feature_row)
            forecasts.append(
                {
                    **forecast,
                    "run_id": memory.run_id,
                    "repository_id": memory.repository_id,
                    "forecasted_at": forecasted_at,
                }
            )

        memory.write(self.name, "risk_features", risk_features)
        memory.write(self.name, "forecasts", forecasts)

        return {
            "status": "complete",
            "agent": self.name,
            "mode": "deterministic",
            "components_forecasted": len(forecasts),
            "high_risk_count": sum(1 for f in forecasts if f.get("risk_probability", 0) > 0.5),
        }
