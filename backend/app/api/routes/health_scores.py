from __future__ import annotations

from fastapi import APIRouter

from app.domain.health.repository import HEALTH_SCORE_REPOSITORY

router = APIRouter(prefix="/api/health-scores", tags=["health-scores"])


@router.get("/{run_id}")
def get_health_scores(run_id: str) -> list[dict]:
    return HEALTH_SCORE_REPOSITORY.get_by_run(run_id)
