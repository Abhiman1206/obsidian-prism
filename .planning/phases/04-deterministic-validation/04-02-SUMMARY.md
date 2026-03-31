---
phase: 04-deterministic-validation
plan: 02
subsystem: testing
tags: [python, pytest, integration, parity, diagnostics]
requires:
  - phase: 04-deterministic-validation
    plan: 01
    provides: Deterministic adapter and runtime unhappy-path unit contract hardening
provides:
  - Table-driven dual-mode parity matrix for happy, risky, and unknown document scenarios
  - Provider-failure integration parity checks with correlation-linked metrics assertions
  - Unattended deterministic-validation marker suite for phase-focused diagnostics
affects: [deterministic-validation, runtime, orchestration, ci]
tech-stack:
  added: []
  patterns: [table-driven parity scenario matrix, marker-based unattended verification suite]
key-files:
  created: []
  modified:
    - tests/foundation/test_dual_mode_samples.py
    - tests/runtime/test_runtime_observability_integration.py
    - pytest.ini
    - tests/runtime/test_runtime_api_endpoints.py
    - tests/runtime/test_failure_mission_report.py
key-decisions:
  - "Parity checks compare normalized/sanitized shared payload fields and ignore expected mode-specific differences."
  - "Deterministic validation is exposed through a dedicated pytest marker for unattended phase diagnostics."
patterns-established:
  - "Phase parity tests should be table-driven with scenario labels for clear unattended failures."
  - "Deterministic-validation tests are grouped under a dedicated marker for targeted CI runs."
requirements-completed: [QUAL-02, RELI-04]
duration: 13min
completed: 2026-03-31
---

# Phase 04 Plan 02 Summary

**Dual-mode parity validation now runs as a table-driven deterministic matrix with an unattended marker-based diagnostics suite.**

## Performance

- **Duration:** 13 min
- **Started:** 2026-03-31T00:12:00Z
- **Completed:** 2026-03-31T00:25:00Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Refactored dual-mode coverage into a scenario matrix with parity assertions for happy, risky, and unknown document paths.
- Added provider-failure integration parity checks for both modes with correlation-linked metrics validation.
- Registered and applied `deterministic_validation` pytest marker to enable unattended phase-focused diagnostics.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add integration parity matrix for known happy and unhappy scenarios** - `a68cd04` (test)
2. **Task 2: Add unattended diagnostics entrypoint for deterministic-validation suite** - `10a1b63` (test)

## Files Created/Modified
- `tests/foundation/test_dual_mode_samples.py` - Added table-driven scenario parity matrix and repeat-run deterministic checks.
- `tests/runtime/test_runtime_observability_integration.py` - Added provider-failure parity checks across both modes.
- `pytest.ini` - Registered deterministic_validation marker.
- `tests/runtime/test_runtime_api_endpoints.py` - Added deterministic_validation marker for unattended suite inclusion.
- `tests/runtime/test_failure_mission_report.py` - Added deterministic_validation marker for unhappy-path diagnostics inclusion.

## Decisions Made
- Kept parity equality focused on normalized deterministic fields and avoided asserting known per-mode variance.
- Used a marker-based suite so unattended deterministic diagnostics are easy to run in CI and local verification.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Deterministic validation parity and unattended diagnostics are in place for phase-level verification.

---
*Phase: 04-deterministic-validation*
*Completed: 2026-03-31*
