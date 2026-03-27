# Architecture Research: Agent Workflow Productionization

## Suggested Components

1. `domain/`
- Business entities and typed schemas
- Validation, scoring, and compliance policy interfaces

2. `tools/`
- Document fetch, credit lookup, risk calculation, compliance checks
- Tool adapters abstracting framework-specific wrappers

3. `orchestration/crewai/`
- CrewAI agent/task/crew assembly
- Crew execution adapters and result normalization

4. `orchestration/langgraph/`
- State definitions, nodes, edges, and invoke adapters
- Graph compile and run wrappers

5. `runtime/`
- Robust execution wrapper (retry, throttle, timeout, classification)
- Shared error types and mission-report formatting

6. `api/`
- FastAPI routes and request handlers
- Health checks, version endpoint, and run endpoints

7. `observability/`
- Logging, correlation IDs, metrics hooks

8. `tests/`
- Unit tests for domain/tools/runtime
- Integration tests for CrewAI and LangGraph parity paths

## Data Flow
1. API receives request with application/document IDs and mode.
2. Request validated into typed input model.
3. Runtime wrapper executes selected orchestration path.
4. Orchestration calls tool adapters and aggregates outputs.
5. Business outcome normalized into response contract.
6. Metrics/logging emitted at each stage with correlation ID.

## Build Order Implications
1. Extract domain models and tool logic from notebook
2. Implement runtime safety wrapper as shared service
3. Implement CrewAI and LangGraph adapters using shared domain layer
4. Add API surface and operational endpoints
5. Add tests and CI
6. Add containerization and deployment config

## Boundary Rules
- Business logic cannot live in notebook/runtime scripts
- Framework-specific classes cannot leak into API contracts
- Tool outputs must be normalized to shared domain response models
