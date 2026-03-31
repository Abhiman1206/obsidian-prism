# Requirements: Chapter 15 Agents Productionization

**Defined:** 2026-03-27
**Core Value:** Deliver reliable and auditable loan-origination agent decisions with deterministic behavior and safe failure handling in production.

## v1 Requirements

### Project Structure

- [x] **ARCH-01**: Code from the notebook is extracted into a Python package with separated modules for domain, tools, orchestration, and runtime.
- [x] **ARCH-02**: A single CLI/API entry path can run either CrewAI or LangGraph orchestration mode from the same input contract.
- [x] **ARCH-03**: Shared domain models define normalized output contracts used by both framework implementations.

### Security and Configuration

- [x] **SECU-01**: Runtime loads required secrets/configuration from environment or secret manager without interactive prompts.
- [x] **SECU-02**: Startup validation fails fast when required config is missing or invalid.
- [ ] **SECU-03**: Sensitive values are masked in logs and error outputs.

### Reliability and Safety

- [ ] **RELI-01**: Safe execution wrapper enforces bounded retries with exponential backoff and timeout caps.
- [ ] **RELI-02**: Rate-limit behavior is configurable per environment and prevents unbounded request bursts.
- [ ] **RELI-03**: Runtime returns structured mission-report failures rather than raw stack traces.
- [ ] **RELI-04**: Known unhappy paths (invalid document, low credit score, provider failure) produce deterministic outcomes.

### API and Operations

- [ ] **OPER-01**: Service exposes health and readiness endpoints suitable for deployment checks.
- [ ] **OPER-02**: Run endpoint accepts typed input and returns standardized result payloads.
- [ ] **OPER-03**: Structured logs include request correlation ID and stage-level execution details.
- [ ] **OPER-04**: Metrics capture per-stage duration, retry counts, and failure categories.

### Quality and Delivery

- [ ] **QUAL-01**: Unit tests cover tool logic, risk/compliance rules, and runtime wrapper behavior.
- [ ] **QUAL-02**: Integration tests verify parity-critical scenarios across CrewAI and LangGraph paths.
- [x] **QUAL-03**: CI pipeline enforces lint, type check, and tests before merge.
- [x] **QUAL-04**: Project ships with containerized runtime definition and reproducible dependency lock.

## v2 Requirements

### Advanced Capabilities

- **ADV-01**: Pluggable multi-provider LLM backend support with routing policies.
- **ADV-02**: Human-in-the-loop approval checkpoints for configurable policy thresholds.
- **ADV-03**: Persistent run history with replay and audit dashboard.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Full web frontend dashboard | Not required for initial production hardening |
| New lending product workflows | Scope is stabilization of existing chapter workflow |
| Real bureau/vendor contracts | Current milestone focuses on architecture and runtime readiness first |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| ARCH-01 | Phase 1 | Complete |
| ARCH-02 | Phase 2 | Complete |
| ARCH-03 | Phase 2 | Complete |
| SECU-01 | Phase 1 | Complete |
| SECU-02 | Phase 1 | Complete |
| SECU-03 | Phase 3 | Pending |
| RELI-01 | Phase 3 | Pending |
| RELI-02 | Phase 3 | Pending |
| RELI-03 | Phase 3 | Pending |
| RELI-04 | Phase 4 | Complete |
| OPER-01 | Phase 3 | Pending |
| OPER-02 | Phase 3 | Pending |
| OPER-03 | Phase 3 | Pending |
| OPER-04 | Phase 3 | Pending |
| QUAL-01 | Phase 4 | Complete |
| QUAL-02 | Phase 4 | Complete |
| QUAL-03 | Phase 5 | Complete |
| QUAL-04 | Phase 5 | Complete |

**Coverage:**
- v1 requirements: 18 total
- Mapped to phases: 18
- Unmapped: 0

---
*Requirements defined: 2026-03-27*
*Last updated: 2026-03-31 after phase 5 completion*
