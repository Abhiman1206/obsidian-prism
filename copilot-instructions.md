# Project Instructions: Predictive Engineering Intelligence Platform

## Mission

Build a production-grade Predictive Engineering Intelligence Platform that turns repository-level engineering risk into executive financial decision support.

## Product Scope

- Backend: FastAPI (Python) in Docker.
- Frontend: Next.js responsive application.
- Deployment: Render.
- Core capabilities:
  - GitHub/GitLab repository ingestion.
  - Code health scoring.
  - 90-day predictive component risk forecasting.
  - Business impact translation for executive reports.
  - Traceable evidence lineage for all report claims.

## Workflow Sources of Truth

- [PROJECT](.planning/PROJECT.md)
- [REQUIREMENTS](.planning/REQUIREMENTS.md)
- [ROADMAP](.planning/ROADMAP.md)
- [STATE](.planning/STATE.md)
- Research: .planning/research/

## Non-Negotiable Engineering Standards

- Preserve auditability: every major KPI and recommendation must be traceable to deterministic evidence.
- Avoid jargon in executive output: prioritize business language and explicit cost framing.
- Keep reliability first for tool/API integrations: timeouts, retries, graceful degradation.
- Build mobile-friendly and desktop-friendly UI from the start.
- Keep contracts typed and explicit between backend, agents, and frontend.

## Implementation Defaults

- Prefer small, testable increments aligned to roadmap phases.
- Keep orchestration logic isolated from pure domain scoring logic.
- Do not introduce autonomous code-remediation features in v1.
- Keep deployment container-first and environment-driven.

## Next Command

After initialization, continue with:
- `/gsd-plan-phase 1`

Optional before planning:
- `/gsd-discuss-phase 1`
