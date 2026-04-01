---
mode: agent
description: Run release hardening and update release checklist artifacts
---

Perform release hardening for this repository and update release tracking files.

Required context:
- `.planning/phases/05-release-hardening/05-RELEASE-CHECKLIST.md`
- `README.md`
- `pyproject.toml`
- `pytest.ini`
- CI workflow files under `.github/workflows/`

Tasks:
1. Verify release checklist items against current code and tests.
2. Run quality checks relevant to release readiness.
3. Update checklist status with concrete evidence.
4. Identify blockers, risks, and required follow-up actions.
5. Keep documentation and commands consistent with real project behavior.

Output:
- Updated checklist file(s)
- Summary of pass/fail items and next actions

User inputs:
- Optional release version: {{RELEASE_VERSION}}
- Optional hardening scope: {{HARDENING_SCOPE}}
