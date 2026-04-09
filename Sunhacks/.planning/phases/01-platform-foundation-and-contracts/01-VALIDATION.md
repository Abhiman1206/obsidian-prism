---
phase: 01
slug: platform-foundation-and-contracts
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-09
---

# Phase 01 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + TypeScript build checks |
| **Config file** | none — Wave 0 installs and initializes |
| **Quick run command** | `python -m pytest -q` |
| **Full suite command** | `python -m pytest -q ; npm run typecheck ; npm run build` |
| **Estimated runtime** | ~120 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest -q`
- **After every plan wave:** Run `python -m pytest -q ; npm run typecheck ; npm run build`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | PLAT-01 | integration | `python -m pytest tests/backend/test_health.py -q` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 1 | PLAT-01 | build | `npm run typecheck ; npm run build` | ❌ W0 | ⬜ pending |
| 01-03-01 | 03 | 2 | PLAT-01 | contract | `python -m pytest tests/contracts/test_contracts.py -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/backend/test_health.py` — backend scaffold verification
- [ ] `tests/contracts/test_contracts.py` — shared contract verification
- [ ] `frontend/package.json scripts` — `typecheck` and `build` commands

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Responsive shell behavior at mobile/desktop breakpoints | PLAT-01 | visual layout correctness | Open frontend at 390px and 1440px widths, verify shell spacing/nav behavior |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 120s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
