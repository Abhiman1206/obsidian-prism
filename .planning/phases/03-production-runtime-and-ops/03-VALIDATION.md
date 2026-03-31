---
phase: 03
slug: production-runtime-and-ops
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-03-31
---

# Phase 03 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | pytest.ini |
| **Quick run command** | `python -m pytest tests/runtime -q` |
| **Full suite command** | `python -m pytest -q` |
| **Estimated runtime** | ~40 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/runtime -q`
- **After every plan wave:** Run `python -m pytest tests/runtime tests/foundation -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | RELI-01 | unit | `python -m pytest tests/runtime/test_execution_policy.py -q` | ❌ W0 | pending |
| 03-01-02 | 01 | 1 | RELI-02 | unit | `python -m pytest tests/runtime/test_rate_limiter.py -q` | ❌ W0 | pending |
| 03-01-03 | 01 | 1 | RELI-03 | integration | `python -m pytest tests/runtime/test_failure_mission_report.py -q` | ❌ W0 | pending |
| 03-02-01 | 02 | 2 | OPER-01 | unit | `python -m pytest tests/runtime/test_runtime_api_endpoints.py::test_health_and_readiness -q` | ❌ W0 | pending |
| 03-02-02 | 02 | 2 | OPER-02, OPER-03, SECU-03 | integration | `python -m pytest tests/runtime/test_runtime_api_endpoints.py tests/runtime/test_structured_logging.py -q` | ❌ W0 | pending |
| 03-03-01 | 03 | 3 | OPER-04 | unit | `python -m pytest tests/runtime/test_metrics.py -q` | ❌ W0 | pending |
| 03-03-02 | 03 | 3 | OPER-04, RELI-03 | integration | `python -m pytest tests/runtime/test_metrics.py tests/runtime/test_failure_mission_report.py -q` | ❌ W0 | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [ ] tests/runtime/test_execution_policy.py - runtime retry/backoff/timeout policy tests
- [ ] tests/runtime/test_rate_limiter.py - bounded rate behavior tests
- [ ] tests/runtime/test_failure_mission_report.py - structured mission-report failure envelope tests
- [ ] tests/runtime/test_runtime_api_endpoints.py - health/readiness/run endpoint tests
- [ ] tests/runtime/test_structured_logging.py - correlation + redaction log tests
- [ ] tests/runtime/test_metrics.py - duration/retry/failure metrics tests

---

## Manual-Only Verifications

All Phase 3 behaviors target automated verification.

---

## Validation Sign-Off

- [x] All tasks have automated verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all missing references
- [x] No watch-mode flags
- [x] Feedback latency under 60s target
- [x] nyquist_compliant: true set in frontmatter

**Approval:** pending
