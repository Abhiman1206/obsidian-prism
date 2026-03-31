# Roadmap: Chapter 15 Agents Productionization

**Created:** 2026-03-27
**Granularity:** Standard
**Total v1 requirements:** 18
**Mapped requirements:** 18
**Coverage:** 100%

## Phase Summary

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | Foundation Extraction | Convert notebook prototype into modular, secure project foundation | ARCH-01, SECU-01, SECU-02 | 4 |
| 2 | Dual-Orchestrator Core | Implement normalized CrewAI and LangGraph execution over shared contracts | ARCH-02, ARCH-03 | 4 |
| 3 | Production Runtime and Ops | Add API/runtime safeguards, observability, and operational endpoints | RELI-01, RELI-02, RELI-03, OPER-01, OPER-02, OPER-03, OPER-04, SECU-03 | 5 |
| 4 | Deterministic Validation | Verify deterministic behavior for happy and unhappy paths across orchestrators | RELI-04, QUAL-01, QUAL-02 | 4 |
| 5 | Release Hardening | Enforce CI quality gates and package deployment artifacts | QUAL-03, QUAL-04 | 4 |

## Phase Details

## Phase 1: Foundation Extraction
Goal: Extract notebook code into a maintainable package baseline with non-interactive secure configuration.

Requirements:
- ARCH-01
- SECU-01
- SECU-02

Success criteria:
1. Notebook business logic is moved into importable modules with clear boundaries.
2. Runtime no longer prompts interactively for secrets in production paths.
3. Configuration validation fails fast with clear messages for missing required settings.
4. Existing notebook scenarios can be invoked through module entry points.

**Plans:** 2 plans

Plans:
- [x] 01-01-PLAN.md - Build extraction foundation (contracts, settings, mock-data, Wave 0 tests)
- [x] 01-02-PLAN.md - Add callable service and thin framework adapters

Status: Complete (2026-03-27)

**UI hint**: no

## Phase 2: Dual-Orchestrator Core
Goal: Ensure CrewAI and LangGraph run over shared contracts and produce normalized outputs.

Requirements:
- ARCH-02
- ARCH-03

Success criteria:
1. Single input schema can execute both orchestration strategies.
2. Shared output schema is returned consistently by both orchestration paths.
3. Framework-specific code remains isolated from API-level contracts.
4. Sample inputs from chapter run successfully in both modes.

**Plans:** 2 plans

Plans:
- [x] 02-01-PLAN.md - Normalize adapter outputs through shared contract helpers
- [x] 02-02-PLAN.md - Enforce single-input dual-mode service parity and sample matrix coverage

Status: Complete (2026-03-31)

**UI hint**: no

## Phase 3: Production Runtime and Ops
Goal: Add operational safety controls and observability required for production.

Requirements:
- RELI-01
- RELI-02
- RELI-03
- OPER-01
- OPER-02
- OPER-03
- OPER-04
- SECU-03

Success criteria:
1. Runtime enforces bounded retries, backoff, and timeout limits.
2. Rate controls are environment-configurable and tested for expected behavior.
3. API exposes health/readiness endpoints and typed run endpoint.
4. Structured logs include correlation IDs and stage telemetry.
5. Metrics for duration, retries, and failures are emitted per run.

**Plans:** 3 plans

Plans:
- [ ] 03-01-PLAN.md - Add runtime guardrails and mission-report failure envelope
- [ ] 03-02-PLAN.md - Implement operational endpoints and structured redacted logging
- [ ] 03-03-PLAN.md - Add metrics instrumentation and observability integration checks

**UI hint**: no

## Phase 4: Deterministic Validation
Goal: Prove behavior parity and deterministic outcomes under expected scenarios.

Requirements:
- RELI-04
- QUAL-01
- QUAL-02

Success criteria:
1. Unit tests cover scoring/compliance logic and wrapper error behavior.
2. Integration tests validate happy path and known unhappy paths.
3. CrewAI and LangGraph outputs satisfy parity expectations for shared scenarios.
4. Test suite runs unattended and reports clear failure diagnostics.

**UI hint**: no

## Phase 5: Release Hardening
Goal: Finalize continuous quality gates and deployment packaging.

Requirements:
- QUAL-03
- QUAL-04

Success criteria:
1. CI pipeline executes lint, type-check, and tests on pull requests.
2. Dependency locking and reproducible install workflow are documented and enforced.
3. Container build succeeds and starts service with required runtime settings.
4. Release checklist documents smoke tests and rollback basics.

**UI hint**: no

---
*Last updated: 2026-03-31 after phase 3 planning*
