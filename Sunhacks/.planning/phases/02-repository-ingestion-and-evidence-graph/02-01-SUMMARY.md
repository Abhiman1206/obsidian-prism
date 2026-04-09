---
phase: 02-repository-ingestion-and-evidence-graph
plan: 01
subsystem: api
tags: [fastapi, pydantic, repository-registration, provider-auth]
requires:
  - phase: 01-platform-foundation-and-contracts
    provides: typed API schemas and validation error envelope
provides:
  - github and gitlab repository registration endpoint
  - provider auth payload contract
  - repository registration typed response contract
affects: [02-02, 02-03, 02-04]
tech-stack:
  added: []
  patterns: [route-to-service boundary, provider credential abstraction]
key-files:
  created:
    - backend/app/api/schemas/provider_auth.py
    - backend/app/api/schemas/repository.py
    - backend/app/api/routes/repositories.py
    - backend/app/domain/repositories/registry.py
    - backend/app/infra/secrets/provider_credentials.py
    - backend/tests/test_provider_auth_contract.py
    - backend/tests/test_repository_registration_contract.py
  modified:
    - backend/app/main.py
key-decisions:
  - "Repository registration logic is isolated in RepositoryRegistryService."
  - "Provider token normalization is abstracted behind ProviderCredentialsService."
patterns-established:
  - "Route handlers delegate orchestration to domain services."
  - "Provider contracts use strict regex constraints and typed status enums."
requirements-completed: [INGEST-01, INGEST-02]
duration: 25 min
completed: 2026-04-10
---

# Phase 2 Plan 1: Repository Registration Contracts Summary

**GitHub and GitLab repository registration APIs now return typed run-readiness metadata through a strict provider-auth contract boundary.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-04-10T00:00:00Z
- **Completed:** 2026-04-10T00:25:00Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments
- Added strict provider auth and repository registration request/response schemas.
- Implemented `/api/repositories/register` with service-layer delegation and credential abstraction.
- Added/expanded tests for provider validation, GitHub/GitLab success paths, and missing-scope failures.

## Task Commits

1. **Task 1 (RED): failing provider auth schema contracts** - `46b5af8` (test)
2. **Task 1 (GREEN): provider auth and repository schemas** - `e3a8740` (feat)
3. **Task 2 (RED): failing repository route contracts** - `fa8c66c` (test)
4. **Task 2 (GREEN): registration route and service wiring** - `a5c9f91` (feat)
5. **Task 3: provider registration contract coverage expansion** - `56b4d4d` (test)

## Files Created/Modified
- backend/app/api/schemas/provider_auth.py - provider auth payload schema
- backend/app/api/schemas/repository.py - repository request/response contracts
- backend/app/api/routes/repositories.py - registration API route
- backend/app/domain/repositories/registry.py - registration service logic
- backend/app/infra/secrets/provider_credentials.py - token/scopes abstraction
- backend/app/main.py - route registration
- backend/tests/test_provider_auth_contract.py - schema contract tests
- backend/tests/test_repository_registration_contract.py - route contract tests

## Decisions Made
- Isolated provider credential preparation from route handlers for easier future secret-source swaps.
- Kept authorization status as enum values (`authorized|pending|failed`) for downstream adapter stability.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- Initial route tests failed with `404` because repository routes were not mounted yet; resolved by wiring new router in `app.main`.

## User Setup Required

External provider OAuth credentials are still required at runtime (`GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `GITLAB_CLIENT_ID`, `GITLAB_CLIENT_SECRET`).

## Next Phase Readiness
- Canonical provider registration output is now available for ingestion adapter plans.
- Ready for 02-02 provider ingestion and normalization implementation.

## Self-Check: PASSED
- Verified key created files exist on disk.
- Verified task commits exist in git history for `02-01`.

---
*Phase: 02-repository-ingestion-and-evidence-graph*
*Completed: 2026-04-10*
