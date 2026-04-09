---
phase: 04-90-day-predictive-risk-forecasting
plan: 03
subsystem: risk-forecast-retrieval-api
tags: [risk, api, repository, ranking]
completed_at: 2026-04-10
duration: 21m
commits:
  - 3387020
  - d6edf00
key_files:
  created:
    - backend/tests/test_risk_forecasts_route_contract.py
    - backend/app/domain/risk/repository.py
    - backend/app/api/routes/risk_forecasts.py
  modified:
    - backend/app/workers/risk_forecasting.py
    - backend/app/main.py
decisions:
  - "Risk forecast storage follows existing in-memory repository pattern"
  - "Route ranking enforces risk_probability desc then component_id asc"
---

# Phase 04 Plan 03: Ranked Risk Forecast Retrieval Summary

Implemented run-scoped persistence and API retrieval for ranked 90-day risk forecasts, including confidence and contributor details.

## Completed Work

1. Added TDD RED route tests in backend/tests/test_risk_forecasts_route_contract.py:
- Validates deterministic ranking behavior.
- Validates required payload fields including top_signals entries.
- Validates unknown-run returns HTTP 200 with empty list.

2. Implemented repository in backend/app/domain/risk/repository.py:
- Added RiskForecastRepository singleton.
- Added add_many(records).
- Added get_ranked_by_run(run_id) with deterministic sort.

3. Updated worker persistence in backend/app/workers/risk_forecasting.py:
- Added persist_risk_forecasts(records) helper.

4. Added API route in backend/app/api/routes/risk_forecasts.py:
- Added GET /api/risk-forecasts/{run_id}.

5. Wired router in backend/app/main.py.

## Verification

- pytest backend/tests/test_risk_forecasts_route_contract.py -q
- Result: 2 passed

## Deviations from Plan

None - plan executed as written.

## Known Stubs

None.

## Self-Check: PASSED

- Verified created/modified files exist.
- Verified commits 3387020 and d6edf00 exist in git history.
