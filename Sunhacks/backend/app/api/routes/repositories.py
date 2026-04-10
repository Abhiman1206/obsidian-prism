from fastapi import APIRouter, HTTPException

from app.api.schemas.repository import (
    RepositoryAnalysisRequest,
    RepositoryAnalysisResponse,
    RepositoryRegistrationRequest,
    RepositoryRegistrationResponse,
)
from app.domain.repositories.analyzer import RepositoryAnalyzerService
from app.domain.repositories.registry import RepositoryRegistryService

router = APIRouter(prefix="/api/repositories", tags=["repositories"])

_registry = RepositoryRegistryService()
_analyzer = RepositoryAnalyzerService()


@router.post("/register", response_model=RepositoryRegistrationResponse)
def register_repository(payload: RepositoryRegistrationRequest) -> RepositoryRegistrationResponse:
    return _registry.register_repository(payload)


@router.post("/analyze", response_model=RepositoryAnalysisResponse)
def analyze_repository(payload: RepositoryAnalysisRequest) -> RepositoryAnalysisResponse:
    try:
        return _analyzer.analyze_repository(payload.repository_url)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
