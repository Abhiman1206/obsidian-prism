# Phase 03 Research: Production Runtime and Ops

**Phase:** 3 - Production Runtime and Ops
**Date:** 2026-03-31
**Status:** Complete

## Objective

Research how to add production runtime safeguards and operational observability on top of the current dual-orchestrator baseline.

## Inputs Reviewed

- .planning/ROADMAP.md
- .planning/REQUIREMENTS.md
- .planning/PROJECT.md
- .planning/STATE.md
- src/loan_agents/runtime/service.py
- src/loan_agents/runtime/settings.py
- src/loan_agents/runtime/errors.py
- src/loan_agents/runtime/redaction.py
- tests/foundation/test_service_entrypoint.py
- tests/foundation/test_mode_contract.py
- Chapter_15_Agents.ipynb

## Current-State Findings

1. Service execution currently performs mode validation and adapter dispatch but has no bounded retry/backoff wrapper.
2. Rate controls are not configurable in settings and there is no runtime request-throttling guard.
3. Structured failure envelope exists (`build_failure`) but does not include mission-report metadata (correlation id, category, retry stats).
4. There are no deployment-style health/readiness/run endpoint functions exposed yet.
5. No metrics emitter exists for stage duration, retry counts, or failure categories.
6. Redaction helper exists but logging hooks are not present, so SECU-03 is only partially prepared.

## Recommended Implementation Strategy

### A. Runtime Safety Controls (RELI-01, RELI-02, RELI-03)
- Add runtime policy settings for:
  - `MAX_RETRIES`
  - `BACKOFF_MULTIPLIER`
  - `BACKOFF_MIN_SECONDS`
  - `BACKOFF_MAX_SECONDS`
  - `REQUESTS_PER_MINUTE`
  - `RUN_TIMEOUT_SECONDS`
- Add a robust execution wrapper module that enforces:
  - bounded retries
  - exponential backoff caps
  - timeout cap per run
  - per-process rate gate
- Extend failure envelope to include deterministic mission-report fields:
  - `correlation_id`
  - `failure_category`
  - `retry_count`
  - `stage`

### B. Operational API Surface (OPER-01, OPER-02, OPER-03, SECU-03)
- Create a small runtime API module with callable endpoint handlers:
  - `health()`
  - `readiness()`
  - `run(payload, mode, correlation_id)`
- Ensure run handler accepts typed input and returns normalized result payload.
- Add structured JSON logging hooks with correlation id and stage telemetry.
- Ensure sensitive values (API keys, secrets) are always masked through `redact_secret`.

### C. Metrics and Observability (OPER-04)
- Create runtime metrics module to record:
  - stage duration
  - retries
  - failure category counts
- Attach metrics collection to run lifecycle and include in mission report.

## Validation Architecture

### Verification Layers
1. Unit tests for runtime policy parsing, backoff/retry boundaries, and redaction-aware logging payloads.
2. Service-level tests for timeout/retry/failure-category behavior.
3. Operational endpoint tests for health/readiness/run payload contracts.
4. Metrics tests verifying deterministic counters and duration recording.

### Nyquist Notes for Phase 03
- Every plan task must include an automated command and assert concrete payload keys.
- Add targeted tests before implementation in logic-heavy tasks (runtime wrapper and metrics).
- Keep quick suite under 60 seconds by scoping to phase-specific test files.

## Risks and Mitigations

- Risk: Retry logic can introduce flaky tests due to sleep timing.
  - Mitigation: inject time/sleep dependency for deterministic unit tests.
- Risk: Logging and metrics instrumentation can leak sensitive values.
  - Mitigation: force redaction in logger adapter and test forbidden plaintext tokens.
- Risk: Endpoint abstractions can overfit one framework.
  - Mitigation: expose framework-agnostic callable handlers and keep transport wiring out of phase scope.

## Recommendation

Split phase 3 into three execution plans:
1. Runtime guardrails + mission-report failure envelope.
2. Operational endpoint surface + structured logging/redaction.
3. Metrics instrumentation + integrated runtime observability checks.
