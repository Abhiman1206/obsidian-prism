---
phase: 02-repository-ingestion-and-evidence-graph
plan: 02
subsystem: api
tags: [provider-adapters, normalization, cadence, ingestion-worker]
requires:
  - phase: 02-01
    provides: canonical provider and repository registration contract fields
provides:
  - github and gitlab adapter clients with deterministic pagination
  - canonical commit and churn normalization flow
  - ingestion worker that merges cadence and normalized provider payloads
affects: [02-03, 02-04]
tech-stack:
  added: []
  patterns: [provider adapter dispatch, canonical payload normalization]
key-files:
  created:
    - backend/app/infra/providers/base.py
    - backend/app/infra/providers/github_client.py
    - backend/app/infra/providers/gitlab_client.py
    - backend/app/domain/ingestion/normalization.py
    - backend/app/domain/ingestion/provider_signals.py
    - backend/app/workers/provider_ingestion.py
    - backend/tests/test_provider_normalization.py
    - backend/tests/test_provider_signals.py
  modified:
    - backend/tests/test_provider_signals.py
key-decisions:
  - "Provider-specific commit payloads are transformed to canonical commit/churn records before persistence."
  - "Cadence extraction returns default zero values when provider signal APIs are missing."
patterns-established:
  - "Worker orchestration dispatches adapters by provider and then runs shared normalization."
  - "Timeout/pagination checks are enforced at adapter-construction boundaries."
requirements-completed: [INGEST-03, INGEST-04]
duration: 30 min
completed: 2026-04-10
---

# Phase 2 Plan 2: Provider Adapter Normalization Summary

**GitHub/GitLab ingestion adapters now emit a unified canonical payload for commits, churn, and cadence signals through a shared worker entrypoint.**

## Performance

- **Duration:** 30 min
- **Started:** 2026-04-10T00:25:00Z
- **Completed:** 2026-04-10T00:55:00Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments
- Added base provider client and concrete GitHub/GitLab adapters with pagination handling.
- Implemented canonical normalization for commits and contributor churn outputs.
- Added cadence extraction and provider ingestion orchestration entrypoint with dispatch-by-provider.

## Task Commits
1. **Task 1 (RED): failing provider adapter pagination tests** - `5233c3a` (test)
2. **Task 1 (GREEN): adapter client implementations** - `250519d` (feat)
3. **Task 2 (RED): failing normalization/cadence tests** - `166ae40` (test)
4. **Task 2 (GREEN): normalization and cadence extraction** - `004f4ec` (feat)
5. **Task 3 (RED): failing worker orchestration test** - `571d34f` (test)
6. **Task 3 (GREEN): provider_ingestion worker wiring** - `053ec3a` (feat)

## Files Created/Modified
- backend/app/infra/providers/base.py - shared pagination/timeout adapter primitive
- backend/app/infra/providers/github_client.py - GitHub adapter mapper
- backend/app/infra/providers/gitlab_client.py - GitLab adapter mapper
- backend/app/domain/ingestion/normalization.py - canonical commit/churn normalization
- backend/app/domain/ingestion/provider_signals.py - cadence extraction defaults
- backend/app/workers/provider_ingestion.py - provider dispatch + assembly worker
- backend/tests/test_provider_normalization.py - adapter + normalization tests
- backend/tests/test_provider_signals.py - cadence + worker orchestration tests

## Decisions Made
- Normalization emits contributor churn from file-touch aggregation to stabilize downstream risk feature inputs.
- Missing cadence sources are treated as optional and default to zero/None values to avoid ingestion hard failures.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- None.

## User Setup Required

None - provider callbacks were modeled with callable stubs in tests and do not require live API credentials at this stage.

## Next Phase Readiness
- Incremental mining can now reuse canonical payload contracts from provider ingestion.
- Ready for 02-03 checkpoint-based incremental ingestion implementation.

## Self-Check: PASSED
- Verified key created files exist on disk.
- Verified task commits exist in git history for `02-02`.

---
*Phase: 02-repository-ingestion-and-evidence-graph*
*Completed: 2026-04-10*
