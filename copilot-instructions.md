# Copilot Instructions (Project)

This repository is initialized with a GSD planning workflow.

## Source of Truth
- `.planning/PROJECT.md` for project context and scope boundaries
- `.planning/REQUIREMENTS.md` for checkable requirement IDs
- `.planning/ROADMAP.md` for phase ordering and success criteria
- `.planning/STATE.md` for active phase and continuity

## Working Rules
- Prefer small, verifiable increments that map to roadmap phase goals.
- Preserve deterministic behavior in risk/compliance logic.
- Keep CrewAI and LangGraph paths contract-compatible.
- Do not introduce interactive secret prompts in runtime code.
- Maintain structured error handling and observability hooks.

## Quality Gate
Before closing a phase, ensure:
1. Covered requirement IDs are implemented and testable.
2. Tests and static checks pass.
3. Documentation and state files are updated.

## Next Command
Run `/gsd-discuss-phase 1` to start execution planning.
