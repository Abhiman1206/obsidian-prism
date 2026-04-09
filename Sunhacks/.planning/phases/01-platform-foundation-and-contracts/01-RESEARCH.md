# Phase 01 Research: Platform Foundation and Contracts

## Scope
Phase 1 establishes the delivery foundation for all downstream phases. It must produce a runnable FastAPI baseline, a runnable Next.js shell, and explicit typed contracts that define the analysis lifecycle and core domain payloads.

## standard_stack
- Backend runtime: Python 3.12, FastAPI 0.115.x, uvicorn
- Backend typing and validation: pydantic 2.10.x
- Backend project tooling: pytest, ruff, mypy
- Frontend runtime: Next.js 15.x, React 19.x, TypeScript 5.x
- Frontend state baseline (defer integration details to later phase): TanStack Query 5.x
- Containers and deploy target baseline: Docker, Render

## architecture_patterns
1. Contract-first backend foundation
- Define pydantic request/response schemas before implementing non-trivial endpoint behavior.
- Keep analysis lifecycle as explicit states (queued, running, succeeded, failed).

2. Boundary-separated backend structure
- Separate API routers/schemas from domain/orchestration concerns even in scaffold stage.
- Create folders now so downstream phases avoid structural churn.

3. UI shell-first frontend foundation
- Build responsive layout primitives first (app shell, top-level nav, content containers).
- Keep route structure aligned with roadmap artifacts (dashboard, runs, reports placeholders).

4. Shared domain model package pattern
- Create one shared contract surface for component, health score, risk, and report types.
- Favor generated or mirrored types with strict versioning boundaries (v1 contracts path).

## dont_hand_roll
- Do not hand-roll validation logic where pydantic schemas can enforce structure.
- Do not hand-roll HTTP clients or low-level transport wrappers in this phase.
- Do not invent custom state machine frameworks for run lifecycle; use simple typed enum/state field.

## common_pitfalls
- Building UI before backend contracts are fixed, causing repetitive frontend rewrites.
- Mixing orchestration code into route handlers, causing hard-to-test modules.
- Defining ambiguous payload fields (for example, score without units or scale metadata).
- Omitting error envelope conventions in contracts, which fragments downstream API behavior.

## phase_decisions
- Preserve auditability from day one by including run_id and timestamp fields in baseline contracts.
- Maintain business readability downstream by reserving report contract fields for business-language summaries.
- Keep phase 1 limited to foundation and typed scaffolding, not production forecasting logic.

## implementation_recommendations
- Establish backend directories: api/routes, api/schemas, domain/contracts, orchestration, infra.
- Establish frontend directories: app, components/layout, components/ui, lib/contracts.
- Add health endpoint and a minimal analysis run endpoint pair (create run, get run status) with typed schemas.
- Define v1 contract files for: ComponentProfile, HealthScore, RiskForecast, ExecutiveReportSummary.

## Validation Architecture
For Phase 1, verification should prove three truths:
1. FastAPI service starts and responds on health endpoint.
2. Next.js app starts and renders responsive shell on mobile and desktop widths.
3. Contract files exist and are used by both backend and frontend type layers.

Mandatory automated checks for plans in this phase:
- Backend: pytest smoke + import/type checks
- Frontend: TypeScript check and build
- End-to-end scaffold check: both services boot with expected routes

## sources
- .planning/ROADMAP.md
- .planning/REQUIREMENTS.md
- PRD.md
- .planning/research/STACK.md
- .planning/research/ARCHITECTURE.md
- .planning/research/PITFALLS.md
- .planning/research/SUMMARY.md
