from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies.auth import resolve_authenticated_user_id
from app.api.schemas.repository import (
    RepositoryAnalysisRequest,
    RepositoryAnalysisResponse,
    RepositoryRegistrationRequest,
    RepositoryRegistrationResponse,
    RepositoryRevalidateRequest,
    RepositoryRevalidateResponse,
)
from app.domain.repositories.analyzer import RepositoryAnalyzerService
from app.domain.repositories.registry import RepositoryRegistryService

router = APIRouter(prefix="/api/repositories", tags=["repositories"])

_registry = RepositoryRegistryService()
_analyzer = RepositoryAnalyzerService()


@router.post("/register", response_model=RepositoryRegistrationResponse)
def register_repository(
    payload: RepositoryRegistrationRequest,
    current_user_id: str = Depends(resolve_authenticated_user_id),
) -> RepositoryRegistrationResponse:
    return _registry.register_repository(payload, current_user_id)


@router.post("/revalidate", response_model=RepositoryRevalidateResponse)
def revalidate_repository(
    payload: RepositoryRevalidateRequest,
    current_user_id: str = Depends(resolve_authenticated_user_id),
) -> RepositoryRevalidateResponse:
    try:
        return _registry.revalidate_repository_access(payload, current_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/analyze", response_model=RepositoryAnalysisResponse)
def analyze_repository(payload: RepositoryAnalysisRequest) -> RepositoryAnalysisResponse:
    try:
        return _analyzer.analyze_repository(payload.repository_url)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
