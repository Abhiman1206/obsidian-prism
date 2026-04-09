# Predictive Engineering Intelligence Platform

## What This Is

A multi-agent engineering intelligence platform that analyzes software repositories and predicts component-level failure risk over the next 90 days. It converts technical signals (complexity, churn, deployment velocity, and test coverage) into executive-ready business impact reports in time and money. The product is built for non-technical CEOs first, with CTO and engineering leadership workflows as a secondary audience.

## Core Value

Translate engineering risk into financially actionable decisions for executives before incidents happen.

## Requirements

### Validated

- [x] GitHub/GitLab repository registration contracts and endpoints are in place (Phase 2).
- [x] Provider ingestion, normalization, and cadence extraction produce canonical payloads (Phase 2).
- [x] Incremental checkpoint-based ingestion resume semantics are implemented (Phase 2).
- [x] Ingestion evidence lineage is persisted and queryable by run (Phase 2).
- [x] Deterministic module health scoring computes explainable weighted factors from maintainability/complexity/volatility (Phase 3).
- [x] Health score results are persisted per run and exposed via API with factor-level explainability payloads (Phase 3).
- [x] Deterministic 90-day risk features are generated per component from health and ingestion signals (Phase 4).
- [x] Risk forecasts include bounded probability, confidence, and ranked typed contributor signals (Phase 4).
- [x] Ranked risk forecasts are persisted and retrievable by run through stable API contracts (Phase 4).

### Active

- [ ] Quantify business cost of inaction and generate CEO-safe narrative reports.
- [ ] Provide responsive web UI for risk dashboards and executive reporting.
- [ ] Run production backend on FastAPI in Docker and deploy on Render.

### Out of Scope

- Native mobile apps in v1 — web-first delivery minimizes time-to-value.
- Real-time streaming risk recomputation on every commit — scheduled batch + on-demand analysis is sufficient for v1.
- Fully autonomous remediation code changes — product focus is intelligence and prioritization, not auto-fixing.

## Context

- Product is defined by the PRD in the repository root.
- Architecture follows supervisor-orchestrated multi-agent workflow with specialist agents.
- Backend target stack is FastAPI + Python tooling (LangChain, PyDriller, Radon) in Docker.
- Deployment target is Render with containerized services.
- Frontend target stack is Next.js with responsive design for desktop and mobile executive consumption.
- Reports require strict auditability: each business claim must be traceable to source technical signals.

## Constraints

- **Tech Stack**: FastAPI backend + Next.js frontend + LangChain orchestration — aligns with requested implementation and tooling ecosystem.
- **Deployment**: Containerized runtime on Render — consistent deploy model across environments.
- **Data Reliability**: External APIs and parsing tasks must tolerate timeout, retries, and partial failures — workflow cannot freeze on transient faults.
- **Auditability**: Every KPI in executive reports must map to deterministic evidence chain — prevents black-box outputs.
- **UX**: Executive-facing reports must be jargon-light and financially framed — primary user is non-technical.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use FastAPI for backend APIs and orchestration entrypoints | Mature async Python ecosystem and direct integration with PyDriller/Radon/LangChain | — Pending |
| Use Next.js for frontend | Strong SSR/app routing and responsive UI patterns for dashboard/report pages | — Pending |
| Deploy via Docker on Render | Reproducible runtime and straightforward CI/CD for backend/frontend services | — Pending |
| Build supervisor + specialist agent architecture | Matches PRD requirement for decomposed task orchestration and role separation | — Pending |
| Prioritize business-impact translation in v1 | Core differentiator for CEO audience and adoption | — Pending |
| Normalize provider payloads before persistence | Avoid GitHub/GitLab drift across downstream scoring/risk/reporting phases | Applied in Phase 2 |
| Advance checkpoints only after persistence success | Prevent data loss and duplicate processing during incremental ingestion retries | Applied in Phase 2 |
| Persist lineage records at ingestion time | Preserve deterministic claim-to-source traceability for auditability | Applied in Phase 2 |
| Use fixed health factor weights and clamped normalization | Keep score behavior deterministic and explainable for executive-facing reporting | Applied in Phase 3 |
| Persist health scores behind repository boundary with run-scoped API reads | Keep write/read responsibilities explicit and stable for downstream risk/report consumers | Applied in Phase 3 |
| Use deterministic risk pressure and forecast contributor weighting | Ensure risk outputs remain reproducible, explainable, and contract-safe | Applied in Phase 4 |
| Expose risk forecasts via run-scoped ranked repository reads | Keep API behavior stable with deterministic ordering and empty-run semantics | Applied in Phase 4 |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-10 after Phase 4 completion*
