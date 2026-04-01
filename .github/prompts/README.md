# Copilot Prompt Workflows

This folder contains reusable prompt workflows for GitHub Copilot Chat in VS Code.

## How to run

1. Open Copilot Chat.
2. Open the prompt picker and choose one of the prompt files in this folder.
3. Provide the requested inputs (phase ID, goal, constraints).
4. Let the agent run and apply changes.

If your VS Code build supports slash prompt discovery, these files will also appear as runnable prompt entries.

## Included workflows

- `gsd-plan-phase.prompt.md`: Produce or refine a phase plan from `.planning/` sources.
- `gsd-execute-phase.prompt.md`: Implement a planned phase end-to-end with verification.
- `gsd-add-tests.prompt.md`: Add test coverage for a completed phase from UAT criteria.
- `gsd-release-hardening.prompt.md`: Run release hardening checks and update checklist artifacts.
