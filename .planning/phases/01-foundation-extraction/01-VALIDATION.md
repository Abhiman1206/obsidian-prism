---
phase: 01
slug: foundation-extraction
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-03-27
---

# Phase 01 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | `pytest.ini` (Wave 0 creates) |
| **Quick run command** | `python -m pytest tests/foundation -q` |
| **Full suite command** | `python -m pytest -q` |
| **Estimated runtime** | ~25 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/foundation -q`
- **After every plan wave:** Run `python -m pytest -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | ARCH-01 | unit | `python -m pytest tests/foundation/test_contracts.py -q` | ❌ W0 | pending |
| 01-01-02 | 01 | 1 | SECU-01 | unit | `python -m pytest tests/foundation/test_settings.py -q` | ❌ W0 | pending |
| 01-01-03 | 01 | 1 | SECU-02 | unit | `python -m pytest tests/foundation/test_settings.py -q` | ❌ W0 | pending |
| 01-02-01 | 02 | 2 | ARCH-01 | integration | `python -m pytest tests/foundation/test_service_entrypoint.py -q` | ❌ W0 | pending |
| 01-02-02 | 02 | 2 | ARCH-01 | integration | `python -m pytest tests/foundation/test_mode_contract.py -q` | ❌ W0 | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [ ] `tests/foundation/test_contracts.py` - contract model checks
- [ ] `tests/foundation/test_settings.py` - settings validation checks
- [ ] `tests/foundation/test_service_entrypoint.py` - callable contract checks
- [ ] `pytest.ini` - baseline pytest configuration

---

## Manual-Only Verifications

All Phase 1 behaviors have automated verification targets.

---

## Validation Sign-Off

- [x] All tasks have automated verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all missing references
- [x] No watch-mode flags
- [x] Feedback latency under 60s target
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
