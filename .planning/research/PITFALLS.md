# Pitfalls Research: Agent Workflow Productionization

## Pitfall 1: Framework Drift and Inconsistent Decisions
- Warning signs: CrewAI and LangGraph outputs diverge for same input.
- Prevention: Shared domain calculators and strict response contract tests.
- Phase mapping: Phase 2 and Phase 4.

## Pitfall 2: Hidden Notebook Coupling
- Warning signs: Runtime still depends on notebook globals or cell order.
- Prevention: Move all executable logic to package modules and call from notebook optionally.
- Phase mapping: Phase 1.

## Pitfall 3: Secret Handling Regressions
- Warning signs: API keys prompted interactively or logged accidentally.
- Prevention: Centralized settings loader, secret masking, startup validation.
- Phase mapping: Phase 1 and Phase 3.

## Pitfall 4: Retry Storms and Quota Exhaustion
- Warning signs: Cascading retries, high latency spikes, frequent 429 loops.
- Prevention: Bounded retries, jitter, timeout caps, and per-mode limits.
- Phase mapping: Phase 2 and Phase 3.

## Pitfall 5: Weak Test Surface
- Warning signs: Only notebook-manual verification exists.
- Prevention: Unit tests for tools and policy logic, integration tests for full pipeline paths.
- Phase mapping: Phase 4.

## Pitfall 6: Non-actionable Observability
- Warning signs: Logs are unstructured and cannot correlate per request.
- Prevention: Structured JSON logs, trace IDs, and stage-level metrics.
- Phase mapping: Phase 3.
