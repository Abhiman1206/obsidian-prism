---
phase: 04-90-day-predictive-risk-forecasting
plan: 01
subsystem: risk-feature-engineering
tags: [risk, forecasting, features, deterministic]
completed_at: 2026-04-10
duration: 22m
commits:
  - c845c34
  - a9fb2aa
key_files:
  created:
    - backend/tests/test_risk_features.py
    - backend/app/domain/risk/__init__.py
    - backend/app/domain/risk/features.py
  modified: []
decisions:
  - "Feature pressure uses fixed deterministic weights over health, churn, defect proxy, and deployment instability"
  - "Feature rows are sorted by feature_risk_pressure desc then component_id asc"
---

# Phase 04 Plan 01: Risk Feature Engineering Summary

Implemented deterministic 90-day feature extraction from health and ingestion signals, with explicit pressure ranking for downstream forecasting.

## Completed Work

1. Added TDD RED tests in backend/tests/test_risk_features.py covering:
- Required feature keys and horizon_days=90.
- Stable deterministic ordering.
- Stable 4-decimal feature values for identical inputs.

2. Implemented risk feature module in backend/app/domain/risk/features.py:
- Added build_risk_features(health_rows, ingestion_payload, horizon_days=90).
- Derived contributor_churn_intensity from normalized churn counts.
- Derived deployment_cadence from cadence deployment_count.
- Derived defect_signal_proxy from non-negative issue delta.
- Derived feature_risk_pressure via fixed weighted sum.
- Enforced deterministic sorting by pressure then component.

3. Exported build_risk_features in backend/app/domain/risk/__init__.py.

## Verification

- pytest backend/tests/test_risk_features.py -q
- Result: 3 passed

## Deviations from Plan

None - plan executed as written.

## Known Stubs

None.

## Self-Check: PASSED

- Verified created files exist.
- Verified commits c845c34 and a9fb2aa exist in git history.
