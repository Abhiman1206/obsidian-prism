# Roadmap: Predictive Engineering Intelligence Platform

## Overview

This roadmap builds a production-ready predictive engineering intelligence product from foundations to deployment, prioritizing trustworthy data ingestion, explainable risk forecasts, and executive-grade business impact reporting. The sequence ensures architecture and contracts stabilize first, then analytics, then business translation, then responsive UI, and finally hardening/deployment.

## Phases

- [x] **Phase 1: Platform Foundation and Contracts** - Establish FastAPI/Next.js project skeleton, domain contracts, and orchestration baseline.
- [x] **Phase 2: Repository Ingestion and Evidence Graph** - Implement GitHub/GitLab/PyDriller ingestion with canonical storage and lineage.
- [x] **Phase 3: Code Health Scoring Engine** - Build Radon-driven scoring pipeline and explainable component health outputs.
- [x] **Phase 4: 90-Day Predictive Risk Forecasting** - Implement risk model, confidence scoring, and ranked risk outputs.
- [ ] **Phase 5: Business Impact Synthesis** - Translate technical risk into executive-friendly cost-of-inaction reporting.
- [ ] **Phase 6: Responsive Next.js Dashboard and Reporting UX** - Deliver mobile/desktop dashboards and report drill-down views.
- [ ] **Phase 7: Reliability Hardening and Render Deployment** - Add robustness, observability, Docker productionization, and Render rollout.

## Phase Details

### Phase 1: Platform Foundation and Contracts
**Goal**: Stand up baseline backend/frontend structure and typed contracts that all downstream phases depend on.
**Depends on**: Nothing (first phase)
**Requirements**: PLAT-01
**Success Criteria** (what must be TRUE):
  1. FastAPI API skeleton exists with typed schemas for analysis run lifecycle.
  2. Next.js app shell exists with responsive layout foundation.
  3. Shared domain contracts for components, scores, risks, and reports are defined.
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md — Scaffold FastAPI service structure with schema contracts and health endpoints.
- [x] 01-02-PLAN.md — Scaffold Next.js responsive shell with routing and base design system.
- [x] 01-03-PLAN.md — Define shared domain models and orchestration interfaces.

### Phase 2: Repository Ingestion and Evidence Graph
**Goal**: Build reliable repository data intake and traceable evidence persistence.
**Depends on**: Phase 1
**Requirements**: INGEST-01, INGEST-02, INGEST-03, INGEST-04, INGEST-05, AUDIT-01
**Success Criteria** (what must be TRUE):
  1. User can register/connect GitHub and GitLab repositories for analysis.
  2. System ingests historical and incremental repository activity into canonical storage.
  3. Evidence lineage records are written for all ingestion artifacts.
**Plans**: 4 plans

Plans:
- [x] 02-01-PLAN.md — Implement provider auth/config and repository registration APIs.
- [x] 02-02-PLAN.md — Build GitHub/GitLab ingestion adapters with pagination and normalization.
- [x] 02-03-PLAN.md — Build PyDriller incremental miner and persistence flows.
- [x] 02-04-PLAN.md — Implement evidence graph schema and lineage writer for ingestion stage.

### Phase 3: Code Health Scoring Engine
**Goal**: Compute explainable component health scores from source analysis and change dynamics.
**Depends on**: Phase 2
**Requirements**: HEALTH-01, HEALTH-02, HEALTH-03
**Success Criteria** (what must be TRUE):
  1. Radon-derived complexity and maintainability metrics are computed per component.
  2. Health score is generated with stable weighting and normalization logic.
  3. Health results expose contributing factors for explainability.
**Plans**: 3 plans

Plans:
- [x] 03-01-PLAN.md — Implement Radon metric extraction and expand health factor contracts.
- [x] 03-02-PLAN.md — Implement deterministic health score normalization and weighted aggregation.
- [x] 03-03-PLAN.md — Persist and expose explainability-rich health score payloads via API.

### Phase 4: 90-Day Predictive Risk Forecasting
**Goal**: Forecast near-term component failure risk with ranked outputs and confidence signals.
**Depends on**: Phase 3
**Requirements**: RISK-01, RISK-02, RISK-03
**Success Criteria** (what must be TRUE):
  1. System produces 90-day risk probabilities for analyzed components.
  2. Risk output includes confidence and top contributing predictors.
  3. Ranked high-risk component lists are retrievable by analysis run.
**Plans**: 3 plans

Plans:
- [x] 04-01-PLAN.md — Implement risk feature pipeline combining health, churn, and historical defect proxies.
- [x] 04-02-PLAN.md — Implement deterministic forecasting model, confidence estimation, and contributor signals.
- [x] 04-03-PLAN.md — Expose ranked risk forecast APIs with run-scoped retrieval and contributor details.

### Phase 5: Business Impact Synthesis
**Goal**: Convert predictive technical outputs into executive-ready financial decision support.
**Depends on**: Phase 4
**Requirements**: BIZ-01, BIZ-02, BIZ-03
**Success Criteria** (what must be TRUE):
  1. Technical risks are translated into time and monetary impact estimates.
  2. Executive report content is plain-language and action-oriented.
  3. Cost-of-inaction and priority recommendations are clearly presented.
**Plans**: 3 plans

Plans:
- [x] 05-01-PLAN.md — Define deterministic business assumptions and KPI translation engine.
- [x] 05-02-PLAN.md — Implement executive narrative writer templates and report contract alignment.
- [ ] 05-03-PLAN.md — Persist evidence-linked report claims and expose executive report retrieval API.

### Phase 6: Responsive Next.js Dashboard and Reporting UX
**Goal**: Deliver intuitive, responsive visualization and report interaction for executive and leadership users.
**Depends on**: Phase 5
**Requirements**: UI-01, UI-02, UI-03
**Success Criteria** (what must be TRUE):
  1. Users can view and filter ranked risk dashboards in web UI.
  2. Users can open executive reports with section-level evidence drill-down.
  3. Primary dashboard/report workflows work across mobile and desktop breakpoints.
**Plans**: 3 plans

Plans:
- [ ] 06-01: Build responsive risk dashboard views with ranking and KPI summaries.
- [ ] 06-02: Build executive report pages with drill-down evidence linking.
- [ ] 06-03: Complete accessibility and responsive QA polish across critical screens.

### Phase 7: Reliability Hardening and Render Deployment
**Goal**: Ensure resilient operations and deploy production-ready containerized services on Render.
**Depends on**: Phase 6
**Requirements**: AUDIT-02, AUDIT-03, PLAT-02, PLAT-03
**Success Criteria** (what must be TRUE):
  1. External API/tool paths have timeout, retry, and degraded-mode handling.
  2. Backend/frontend services run in Docker and deploy successfully on Render.
  3. Observability and run-failure diagnostics are available for operations.
**Plans**: 4 plans

Plans:
- [ ] 07-01: Implement watchdog timeout and adaptive retry wrappers.
- [ ] 07-02: Add fault-tolerant task orchestration and graceful degradation handling.
- [ ] 07-03: Finalize Docker images and deployment configuration for Render.
- [ ] 07-04: Add monitoring, health checks, and operational runbooks.

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Platform Foundation and Contracts | 3/3 | Complete | 2026-04-09 |
| 2. Repository Ingestion and Evidence Graph | 4/4 | Complete | 2026-04-10 |
| 3. Code Health Scoring Engine | 3/3 | Complete | 2026-04-10 |
| 4. 90-Day Predictive Risk Forecasting | 3/3 | Complete | 2026-04-10 |
| 5. Business Impact Synthesis | 0/3 | Not started | - |
| 6. Responsive Next.js Dashboard and Reporting UX | 0/3 | Not started | - |
| 7. Reliability Hardening and Render Deployment | 0/4 | Not started | - |
