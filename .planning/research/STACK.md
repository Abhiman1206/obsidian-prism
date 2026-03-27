# Stack Research: Agent Workflow Productionization

## Recommended 2026 Stack

## Runtime
- Python 3.11
- uv or pip-tools for deterministic dependency locking
- pydantic-settings for typed environment configuration

## Agent Framework Layer
- CrewAI (latest stable) for role-based orchestration path
- LangGraph (latest stable) for deterministic state-machine path
- langchain-core and langchain-google-genai only where needed by selected model provider

## API and Service Layer
- FastAPI for production API surface and health endpoints
- Uvicorn or Gunicorn+Uvicorn workers for serving

## Data, Validation, and Contracts
- Pydantic v2 models for all application payload schemas
- JSON logging via structlog or stdlib logging JSON formatter

## Reliability and Safety
- tenacity for retries with bounded exponential backoff
- Limits via ratelimit or migration to service-level rate control middleware
- Circuit breaker and timeout controls at LLM/tool-call boundaries

## Quality and Delivery
- pytest + pytest-cov for unit/integration tests
- ruff + mypy for lint/type checks
- pre-commit for local quality gates
- GitHub Actions for CI
- Docker multi-stage build for packaging and deployment parity

## What Not To Use (for this project phase)
- Notebook-first runtime execution as production path - weak isolation and poor operability
- Global mutable state shared across agent runs - harms concurrency and test determinism
- Hardcoded API keys or interactive prompts in runtime code - violates production secret handling

## Confidence
- High: FastAPI, pytest, ruff/mypy, Docker, pydantic
- Medium: Keeping both CrewAI and LangGraph in same deployable package (requires disciplined module boundaries)
- Medium: Provider-specific SDK stability across model updates
