from fastapi import APIRouter

from app.api.schemas.repository import RepositoryRegistrationRequest, RepositoryRegistrationResponse
from app.domain.repositories.registry import RepositoryRegistryService

router = APIRouter(prefix="/api/repositories", tags=["repositories"])

_registry = RepositoryRegistryService()


@router.post("/register", response_model=RepositoryRegistrationResponse)
def register_repository(payload: RepositoryRegistrationRequest) -> RepositoryRegistrationResponse:
    return _registry.register_repository(payload)
