---
phase: 04
slug: deterministic-validation
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-03-31
---

# Phase 04 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | pytest.ini |
| **Quick run command** | `python -m pytest tests/foundation/test_orchestrator_output_contract.py tests/runtime/test_failure_mission_report.py -q` |
| **Full suite command** | `python -m pytest tests/foundation/test_orchestrator_output_contract.py tests/foundation/test_dual_mode_samples.py tests/runtime/test_failure_mission_report.py tests/runtime/test_runtime_observability_integration.py -q` |
| **Estimated runtime** | ~45 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/foundation/test_orchestrator_output_contract.py tests/runtime/test_failure_mission_report.py -q`
- **After every plan wave:** Run `python -m pytest tests/foundation/test_orchestrator_output_contract.py tests/foundation/test_dual_mode_samples.py tests/runtime/test_failure_mission_report.py tests/runtime/test_runtime_observability_integration.py -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | QUAL-01 | unit | `python -m pytest tests/foundation/test_orchestrator_output_contract.py -q` | ✅ | pending |
| 04-01-02 | 01 | 1 | RELI-04, QUAL-01 | unit | `python -m pytest tests/runtime/test_failure_mission_report.py tests/foundation/test_dual_mode_samples.py -q` | ✅ | pending |
| 04-02-01 | 02 | 2 | QUAL-02, RELI-04 | integration | `python -m pytest tests/runtime/test_runtime_observability_integration.py tests/foundation/test_dual_mode_samples.py -q` | ✅ | pending |
| 04-02-02 | 02 | 2 | QUAL-02 | integration | `python -m pytest tests/foundation/test_orchestrator_output_contract.py tests/runtime/test_runtime_observability_integration.py tests/runtime/test_failure_mission_report.py -q` | ✅ | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

All Phase 4 behaviors target automated verification.

---

## Validation Sign-Off

- [x] All tasks have automated verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all missing references
- [x] No watch-mode flags
- [x] Feedback latency under 60s target
- [x] nyquist_compliant: true set in frontmatter

**Approval:** pending
