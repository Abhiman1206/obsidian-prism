"""ASGI application exposing runtime health, readiness, and run endpoints."""

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from loan_agents.runtime import api
from loan_agents.runtime.settings import load_cors_allow_credentials, load_cors_allowed_origins


def create_app() -> FastAPI:
    application = FastAPI(title="loan-agents", version="1.0.0")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(load_cors_allowed_origins()),
        allow_credentials=load_cors_allow_credentials(),
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    @application.get("/health")
    def health() -> dict[str, Any]:
        return api.health()

    @application.get("/readiness")
    def readiness() -> dict[str, Any]:
        return api.readiness()

    @application.post("/run")
    def run(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return api.run(payload)
        except KeyError as exc:
            raise HTTPException(status_code=422, detail=f"Missing field: {exc}") from exc

    return application


app = create_app()
