from __future__ import annotations

from fastapi import APIRouter

from app.domain.business.repository import EXECUTIVE_REPORT_REPOSITORY

router = APIRouter(prefix="/api/executive-reports", tags=["executive-reports"])


@router.get("/{run_id}")
def get_executive_reports(run_id: str) -> list[dict]:
    return EXECUTIVE_REPORT_REPOSITORY.get_by_run(run_id)
