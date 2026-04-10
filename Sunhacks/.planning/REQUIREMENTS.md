# Requirements: Predictive Engineering Intelligence Platform

**Defined:** 2026-04-09
**Core Value:** Translate engineering risk into financially actionable decisions for executives before incidents happen.

## v1 Requirements

### Repository Ingestion

- [x] **INGEST-01**: User can connect a GitHub repository and authorize analysis scopes.
- [x] **INGEST-02**: User can connect a GitLab repository and authorize analysis scopes.
- [x] **INGEST-03**: System can ingest commit history, changed files, and contributor churn for selected repositories.
- [x] **INGEST-04**: System can capture issue/deployment cadence signals from provider APIs when available.
- [x] **INGEST-05**: Ingestion jobs can resume incrementally without reprocessing full history.

### Code Health Scoring

- [x] **HEALTH-01**: System computes cyclomatic complexity and maintainability metrics per module/file using Radon.
- [x] **HEALTH-02**: System derives a normalized health score per component from complexity, maintainability, and change volatility inputs.
- [x] **HEALTH-03**: Health score output includes contributing factors for explainability.

### Predictive Risk Forecasting

- [ ] **RISK-01**: System forecasts 90-day failure/degradation risk per component using historical and health features.
- [ ] **RISK-02**: Risk output includes confidence and top contributing signals per component.
- [ ] **RISK-03**: System returns ranked high-risk component list for each analysis run.

### Business Impact Translation

- [x] **BIZ-01**: System translates technical risk outputs into estimated time-cost impact using configurable assumptions.
- [x] **BIZ-02**: System generates an executive report in non-technical language.
- [x] **BIZ-03**: Report highlights cost of inaction and prioritization recommendations.

### Auditability and Reliability

- [x] **AUDIT-01**: Every report claim can be traced to source metrics and data lineage records.
- [ ] **AUDIT-02**: External API/tool calls are guarded by timeout and adaptive retry policies.
- [ ] **AUDIT-03**: Pipeline can fail gracefully at task level without freezing entire run.

### Frontend Experience (Next.js)

- [x] **UI-01**: User can view repository risk dashboard with ranked components and key metrics.
- [x] **UI-02**: User can view and navigate executive report sections with evidence drill-down links.
- [x] **UI-03**: Dashboard and report pages are responsive and usable on mobile and desktop.

### Backend and Deployment (FastAPI + Docker + Render)

- [x] **PLAT-01**: Backend APIs are implemented in FastAPI with typed request/response contracts.
- [ ] **PLAT-02**: Backend and frontend are containerized for deterministic runtime behavior.
- [ ] **PLAT-03**: Application stack is deployable on Render with environment-driven configuration.

### Integration Runtime Hardening

- [x] **LCH-01**: Run orchestration uses real LangChain package runnables for staged execution.
- [x] **API-01**: GitHub/GitLab authenticated APIs provide commits plus PR/MR, issue, and deployment signals.
- [x] **MINER-01**: Incremental ingestion supports direct PyDriller repository mining with checkpoint-safe resume behavior.

## v2 Requirements

### Advanced Decision Intelligence

- **ADV-01**: User can run scenario simulations comparing mitigation investment vs projected risk reduction.
- **ADV-02**: System supports role-personalized report modes for CEO, CTO, and engineering leadership.
- **ADV-03**: System tracks forecast drift and calibration over time with backtesting views.

### Multi-Repo Portfolio Intelligence

- **PORT-01**: User can benchmark risk posture across multiple repositories and teams.
- **PORT-02**: System can produce portfolio-level exposure and budget prioritization recommendations.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Native mobile applications | Web-first strategy is sufficient for executive consumption in v1 |
| Autonomous code remediation | Product focus is risk intelligence, not automated code changes |
| Real-time recomputation on every commit | High cost/complexity with low incremental value for initial users |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| INGEST-01 | Phase 2 | Complete |
| INGEST-02 | Phase 2 | Complete |
| INGEST-03 | Phase 2 | Complete |
| INGEST-04 | Phase 2 | Complete |
| INGEST-05 | Phase 2 | Complete |
| HEALTH-01 | Phase 3 | Complete |
| HEALTH-02 | Phase 3 | Complete |
| HEALTH-03 | Phase 3 | Complete |
| RISK-01 | Phase 4 | Pending |
| RISK-02 | Phase 4 | Pending |
| RISK-03 | Phase 4 | Pending |
| BIZ-01 | Phase 5 | Complete |
| BIZ-02 | Phase 5 | Complete |
| BIZ-03 | Phase 5 | Complete |
| AUDIT-01 | Phase 2 | Complete |
| AUDIT-02 | Phase 7 | Pending |
| AUDIT-03 | Phase 7 | Pending |
| UI-01 | Phase 6 | Complete |
| UI-02 | Phase 6 | Complete |
| UI-03 | Phase 6 | Complete |
| PLAT-01 | Phase 1 | Complete |
| PLAT-02 | Phase 7 | Pending |
| PLAT-03 | Phase 7 | Pending |
| LCH-01 | Phase 8 | Complete |
| API-01 | Phase 8 | Complete |
| MINER-01 | Phase 8 | Complete |

**Coverage:**
- v1 requirements: 26 total
- Mapped to phases: 26
- Unmapped: 0

---
*Requirements defined: 2026-04-09*
*Last updated: 2026-04-09 after initial definition*
