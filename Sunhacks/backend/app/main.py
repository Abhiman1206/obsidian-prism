from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.health import router as health_router
from app.api.routes.health_scores import router as health_scores_router
from app.api.routes.lineage import router as lineage_router
from app.api.routes.executive_reports import router as executive_reports_router
from app.api.routes.repositories import router as repositories_router
from app.api.routes.risk_forecasts import router as risk_forecasts_router
from app.api.routes.runs import router as runs_router
from app.api.schemas.run import ErrorResponse
from app.infra.database import init_db


def _resolve_allowed_origins() -> list[str]:
	configured = os.getenv("ALLOWED_ORIGINS", "").strip()
	if configured:
		return [origin.strip() for origin in configured.split(",") if origin.strip()]
	return [
		"http://localhost:3000",
		"http://127.0.0.1:3000",
	]


@asynccontextmanager
async def lifespan(application: FastAPI):
    init_db()
    yield


app = FastAPI(title="Predictive Engineering Intelligence API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
	allow_origins=_resolve_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(health_scores_router)
app.include_router(lineage_router)
app.include_router(executive_reports_router)
app.include_router(repositories_router)
app.include_router(risk_forecasts_router)
app.include_router(runs_router)


@app.middleware("http")
async def authenticated_identity_middleware(request: Request, call_next):
	# Placeholder extraction hook: in production this should be set by upstream auth.
	user_id = request.headers.get("x-user-id")
	if not user_id and os.getenv("APP_ENV", "development") != "production":
		user_id = "user-local"
	request.state.authenticated_user_id = user_id
	return await call_next(request)


@app.get("/healthz")
def healthz() -> dict[str, str]:
	return {
		"status": "ok",
		"service": "predictive-engineering-intelligence",
	}


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
	details = {"errors": str(exc.errors())}
	payload = ErrorResponse(
		error_code="validation_error",
		message="Request validation failed",
		details=details,
	)
	return JSONResponse(status_code=422, content=payload.model_dump())
