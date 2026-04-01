---
mode: agent
description: Generate or complete test coverage for a finished phase
---

Create missing tests for phase {{PHASE_ID}} using phase UAT and implemented behavior.

Read first:
- `.planning/REQUIREMENTS.md`
- `.planning/phases/` artifacts for {{PHASE_ID}}
- Existing tests under `tests/`

Tasks:
1. Identify uncovered acceptance criteria for {{PHASE_ID}}.
2. Add focused tests in the appropriate test modules.
3. Prefer deterministic, fast tests with clear assertions.
4. Run targeted tests first, then broader suite if needed.
5. Report coverage improvements and any remaining gaps.

Constraints:
- Do not rewrite passing tests unless necessary.
- Match repository test style and fixtures.

User inputs:
- Phase ID: {{PHASE_ID}}
- Optional test scope: {{TEST_SCOPE}}
