# Features Research: Agent Workflow Productionization

## Table Stakes (Must-Have)

### Configuration and Secrets
- Environment-based configuration with strict validation at startup
- Non-interactive secret loading (env vars, secret manager, CI/CD injection)

### Workflow Execution
- Deterministic execution entry points for CrewAI and LangGraph paths
- Explicit request/response schemas for each pipeline stage
- Support for happy path and known unhappy paths (invalid docs, low credit)

### Reliability
- Retry and throttling controls configurable per environment
- Timeouts and clear error classification for dependency failures
- Idempotent request handling where possible

### Observability
- Structured logs with correlation IDs
- Metrics for stage duration, failure rate, retry count
- Health/readiness endpoints for deployment monitoring

### Quality and Safety
- Unit and integration test coverage over business rules and orchestration
- Static checks and CI gates before merge/release

## Differentiators (Nice-to-Have)
- Provider abstraction for multiple LLM vendors
- Policy simulation mode with what-if analysis
- Run replay and audit timeline views
- Fine-grained human-in-the-loop intervention points

## Anti-Features (Do Not Build in v1)
- Full UI dashboard before backend hardening is complete
- Expanding business scope (new loan products) before stabilizing current workflow
- Premature microservice decomposition for a small codebase

## Complexity Notes
- High: Framework parity and consistent outputs across CrewAI/LangGraph
- Medium: Robust observability and audit metadata propagation
- Medium: Error taxonomy and deterministic fallback handling
- Low: Basic API wrapping and schema extraction from notebook logic

## Dependencies
- Core workflow module must exist before API wrapping
- Unified domain models must exist before tests and traceability
- CI pipeline depends on finalized command entry points
