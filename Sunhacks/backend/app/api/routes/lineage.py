from fastapi import APIRouter

from app.domain.evidence.schema import LineageRecord
from app.workers.lineage_ingestion import LINEAGE_REPOSITORY

router = APIRouter(prefix="/api/lineage", tags=["lineage"])


@router.get("/{run_id}", response_model=list[LineageRecord])
def get_lineage(run_id: str) -> list[LineageRecord]:
    return LINEAGE_REPOSITORY.get_lineage(run_id=run_id)
