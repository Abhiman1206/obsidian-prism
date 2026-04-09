---
phase: 03
slug: code-health-scoring-engine
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-10
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | none — uses repository defaults |
| **Quick run command** | `pytest backend/tests/test_health_metrics.py backend/tests/test_health_scoring.py backend/tests/test_health_scores_route_contract.py -q` |
| **Full suite command** | `pytest backend/tests -q` |
| **Estimated runtime** | ~40 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest backend/tests/test_health_metrics.py backend/tests/test_health_scoring.py backend/tests/test_health_scores_route_contract.py -q`
- **After every plan wave:** Run `pytest backend/tests -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | HEALTH-01 | unit | `pytest backend/tests/test_health_metrics.py -q` | ✅ | ⬜ pending |
| 03-01-02 | 01 | 1 | HEALTH-03 | contract | `pytest backend/tests/test_contract_alignment.py -q` | ✅ | ⬜ pending |
| 03-02-01 | 02 | 2 | HEALTH-02 | unit | `pytest backend/tests/test_health_scoring.py -q` | ✅ | ⬜ pending |
| 03-03-01 | 03 | 3 | HEALTH-03 | api contract | `pytest backend/tests/test_health_scores_route_contract.py -q` | ✅ | ⬜ pending |
| 03-03-02 | 03 | 3 | HEALTH-01, HEALTH-02, HEALTH-03 | integration | `pytest backend/tests -q` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/test_health_metrics.py` — stubs for HEALTH-01
- [ ] `backend/tests/test_health_scoring.py` — stubs for HEALTH-02
- [ ] `backend/tests/test_health_scores_route_contract.py` — stubs for HEALTH-03

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
