---
mode: agent
description: Build or refine a GSD phase plan from project artifacts
---

You are working in a repository that follows the GSD planning workflow.

Goal:
Create or refine the implementation plan for phase: {{PHASE_ID}}.

Required context to read before planning:
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- Existing phase folder under `.planning/phases/` for {{PHASE_ID}} if present

Output requirements:
1. Produce or update a phase plan document in the matching phase directory.
2. Map plan tasks to requirement IDs.
3. Include verification strategy (tests, lint, runtime checks).
4. Include explicit risks, assumptions, and rollback notes.
5. Keep tasks atomic and execution-ready.

Execution behavior:
- Prefer concrete edits over abstract advice.
- If phase artifacts are missing, create the minimal required files and continue.
- Do not change unrelated phases.

User inputs:
- Phase ID: {{PHASE_ID}}
- Optional objective override: {{OBJECTIVE_OVERRIDE}}
- Optional constraints: {{CONSTRAINTS}}
