from __future__ import annotations

from fastapi import APIRouter

from app.domain.risk.repository import RISK_FORECAST_REPOSITORY

router = APIRouter(prefix="/api/risk-forecasts", tags=["risk-forecasts"])


@router.get("/{run_id}")
def get_risk_forecasts(run_id: str) -> list[dict]:
    return RISK_FORECAST_REPOSITORY.get_ranked_by_run(run_id)