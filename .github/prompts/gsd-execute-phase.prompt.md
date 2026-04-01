---
mode: agent
description: Execute a GSD phase with tests and verification
---

Implement phase {{PHASE_ID}} end-to-end in this repository.

Required context:
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- Phase plan and notes for {{PHASE_ID}} in `.planning/phases/`

Execution contract:
1. Implement planned code changes with minimal scope.
2. Add or update tests for acceptance criteria.
3. Run relevant validation commands and report outcomes.
4. Update phase artifacts/checklists to reflect completion status.
5. Summarize what was implemented, verified, and any open gaps.

Quality rules:
- Preserve deterministic behavior across orchestration paths.
- Keep runtime observability and structured errors intact.
- Avoid refactors unrelated to {{PHASE_ID}}.

User inputs:
- Phase ID: {{PHASE_ID}}
- Optional target files: {{TARGET_FILES}}
- Optional non-goals: {{NON_GOALS}}
