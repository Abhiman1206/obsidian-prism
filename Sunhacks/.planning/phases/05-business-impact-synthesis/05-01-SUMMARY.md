---
phase: 05-business-impact-synthesis
plan: 01
subsystem: business-impact-translation
tags: [business, risk, translation]
completed_at: 2026-04-10
duration: 20m
commits:
  - bc7b9f2
  - 98fe2ba
key_files:
  created:
    - backend/tests/test_business_impact_translation.py
    - backend/app/domain/business/translation.py
    - backend/app/domain/business/__init__.py
  modified: []
decisions:
  - "Business translation uses fixed numeric assumptions with optional overrides"
  - "Output ordering is deterministic by expected_total_cost desc then component_id asc"
---

# Phase 05 Plan 01: Deterministic Business Impact Translation Summary

Implemented deterministic translation from risk forecasts into business-facing time and cost KPIs with configurable assumptions.

## Completed Work

1. Added TDD RED tests in backend/tests/test_business_impact_translation.py:
- Defines required output fields: expected_engineering_hours, expected_downtime_hours, expected_total_cost, and cost_drivers.
- Validates deterministic output with assumption overrides.
- Validates deterministic ordering by expected_total_cost and component_id.

2. Implemented translation module in backend/app/domain/business/translation.py:
- Added DEFAULT_BUSINESS_ASSUMPTIONS.
- Added translate_risk_to_business_impact with deterministic formulas.
- Added explainability via ordered cost_drivers labels.
- Added deterministic sort behavior.

3. Exported business translation API in backend/app/domain/business/__init__.py.

## Verification

- pytest backend/tests/test_business_impact_translation.py -q
- Result: 3 passed

## Deviations from Plan

None - plan executed as written.

## Known Stubs

None.

## Self-Check: PASSED

- Verified created files exist:
  - backend/tests/test_business_impact_translation.py
  - backend/app/domain/business/translation.py
  - backend/app/domain/business/__init__.py
- Verified commits exist in git history:
  - bc7b9f2
  - 98fe2ba
