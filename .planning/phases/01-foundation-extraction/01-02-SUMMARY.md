---
phase: 01-foundation-extraction
plan: 02
subsystem: api
tags: [python, service, adapters, crewai, langgraph]
requires:
  - phase: 01-foundation-extraction
    provides: shared contracts, settings, and mock fixtures
provides:
  - Callable run_pipeline service with explicit mode dispatch
  - Structured deterministic failure envelope for mode/config/provider errors
  - Thin CrewAI and LangGraph adapter wrappers over shared contracts
  - Foundation runtime documentation for entrypoint usage
affects: [dual-orchestrator, production-runtime, validation]
tech-stack:
  added: []
  patterns: [thin adapters, explicit mode contract, normalized error envelope]
key-files:
  created:
    - src/loan_agents/runtime/service.py
    - src/loan_agents/runtime/errors.py
    - src/loan_agents/orchestration/crewai_adapter.py
    - src/loan_agents/orchestration/langgraph_adapter.py
    - tests/foundation/test_service_entrypoint.py
    - tests/foundation/test_mode_contract.py
    - README.md
  modified: []
key-decisions:
  - "Kept service dispatch explicit with no mode fallback to preserve deterministic behavior"
  - "Wrapped all runtime and provider errors in a uniform failure envelope"
patterns-established:
  - "Service entrypoints return stable output keys on both success and failure"
  - "Framework-specific code stays in thin adapter modules"
requirements-completed: [ARCH-01]
duration: 14min
completed: 2026-03-27
---

# Phase 01 Plan 02 Summary

**Callable pipeline runtime with explicit crewai/langgraph mode routing, structured failure handling, and thin framework adapters over shared contracts.**

## Performance

- **Duration:** 14 min
- **Started:** 2026-03-27T22:01:00Z
- **Completed:** 2026-03-27T22:15:00Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments
- Implemented run_pipeline with explicit mode validation and adapter dispatch.
- Added thin orchestration wrappers for CrewAI and LangGraph with normalized outputs.
- Documented entrypoint contract and verified behavior with mode and service tests.

## Task Commits

1. **Task 1: Build callable service contract with explicit mode dispatch** - `acb757d` (feat)
2. **Task 2: Add thin orchestration adapters for CrewAI and LangGraph** - `957f5a2` (feat)
3. **Task 3: Document extraction entrypoint and execute foundation smoke verification** - `41fd51d` (docs)

**Plan metadata:** pending

## Files Created/Modified
- `src/loan_agents/runtime/service.py` - Deterministic callable entrypoint and mode routing.
- `src/loan_agents/runtime/errors.py` - Structured failure envelope helper.
- `src/loan_agents/orchestration/crewai_adapter.py` - CrewAI adapter wrapper.
- `src/loan_agents/orchestration/langgraph_adapter.py` - LangGraph adapter wrapper.
- `tests/foundation/test_service_entrypoint.py` - Entrypoint contract tests.
- `tests/foundation/test_mode_contract.py` - Dispatch and adapter-failure contract tests.
- `README.md` - Runtime interface documentation.

## Decisions Made
- Used direct adapter function imports in service for transparent dispatch and easier monkeypatch testing.
- Preserved selected mode in all failure envelopes for deterministic downstream behavior.

## Deviations from Plan
None - plan executed as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 2 can now focus on dual-orchestrator normalization over a working callable baseline.
- Foundation suite validates mode-specific and failure-contract behavior.

---
*Phase: 01-foundation-extraction*
*Completed: 2026-03-27*
