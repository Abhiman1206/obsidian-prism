"""ASGI application exposing runtime health, readiness, and run endpoints."""

from typing import Any

from fastapi import FastAPI, HTTPException

from loan_agents.runtime import api

app = FastAPI(title="loan-agents", version="1.0.0")


@app.get("/health")
def health() -> dict[str, Any]:
    return api.health()


@app.get("/readiness")
def readiness() -> dict[str, Any]:
    return api.readiness()


@app.post("/run")
def run(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return api.run(payload)
    except KeyError as exc:
        raise HTTPException(status_code=422, detail=f"Missing field: {exc}") from exc
