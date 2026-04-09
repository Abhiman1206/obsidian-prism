from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes.health import router as health_router
from app.api.routes.health_scores import router as health_scores_router
from app.api.routes.lineage import router as lineage_router
from app.api.routes.repositories import router as repositories_router
from app.api.routes.runs import router as runs_router
from app.api.schemas.run import ErrorResponse


app = FastAPI(title="Predictive Engineering Intelligence API")
app.include_router(health_router)
app.include_router(health_scores_router)
app.include_router(lineage_router)
app.include_router(repositories_router)
app.include_router(runs_router)


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
	details = {"errors": str(exc.errors())}
	payload = ErrorResponse(
		error_code="validation_error",
		message="Request validation failed",
		details=details,
	)
	return JSONResponse(status_code=422, content=payload.model_dump())
