# Roadmap: Chapter 15 Agents Productionization

**Created:** 2026-03-27
**Granularity:** Standard
**Total tracked requirements:** 24 (v1: 18, v2: 6)
**Mapped requirements:** 24
**Coverage:** 100%

## Phase Summary

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | Foundation Extraction | Convert notebook prototype into modular, secure project foundation | ARCH-01, SECU-01, SECU-02 | 4 |
| 2 | Dual-Orchestrator Core | Implement normalized CrewAI and LangGraph execution over shared contracts | ARCH-02, ARCH-03 | 4 |
| 3 | Production Runtime and Ops | Add API/runtime safeguards, observability, and operational endpoints | RELI-01, RELI-02, RELI-03, OPER-01, OPER-02, OPER-03, OPER-04, SECU-03 | 5 |
| 4 | Deterministic Validation | Verify deterministic behavior for happy and unhappy paths across orchestrators | RELI-04, QUAL-01, QUAL-02 | 4 |
| 5 | Release Hardening | Enforce CI quality gates and package deployment artifacts | QUAL-03, QUAL-04 | 4 |
| 6 | Frontend Application | Build the web frontend for loan intake, execution progress, and result display | FE-01, FE-02 | 4 |
| 7 | Frontend/Backend Integration | Connect frontend workflows to runtime API with cross-origin safety | INT-01, INT-02 | 4 |
| 8 | Platform Deployment | Deploy frontend on Vercel and backend on Render with operational checks | DEP-01, DEP-02 | 4 |

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
- [x] 03-01-PLAN.md - Add runtime guardrails and mission-report failure envelope
- [x] 03-02-PLAN.md - Implement operational endpoints and structured redacted logging
- [x] 03-03-PLAN.md - Add metrics instrumentation and observability integration checks

Status: Complete (2026-03-31)

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

**Plans:** 2 plans

Plans:
- [x] 04-01-PLAN.md - Harden deterministic unhappy-path unit contracts and metadata parity
- [x] 04-02-PLAN.md - Build integration parity matrix and unattended diagnostics suite

Status: Complete (2026-03-31)

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

**Plans:** 2/2 plans complete

Plans:
- [x] 05-01-PLAN.md - Enforce deterministic CI quality gates and dependency lock workflow
- [x] 05-02-PLAN.md - Add container packaging artifacts and release smoke/rollback checklist

Status: Complete (2026-03-31)

**UI hint**: no

## Phase 6: Frontend Application
Goal: Build a production-ready frontend application for loan workflow inputs and normalized decision presentation.

Requirements:
- FE-01
- FE-02

Success criteria:
1. A dedicated frontend app can collect applicant/document inputs required by backend contracts.
2. Frontend validates required fields and user-facing constraints before submission.
3. UI shows clear loading/progress, success output, and structured failure messages.
4. Frontend build/test/lint commands are documented and run in CI-ready form.

**Plans:** 1 plan

Plans:
- [x] 06-01-PLAN.md - Create frontend app shell, validated input flow, and result visualization baseline

Status: Complete (2026-03-31)

**UI hint**: yes

## Phase 7: Frontend/Backend Integration
Goal: Connect frontend workflows to backend runtime endpoints for end-to-end execution.

Requirements:
- INT-01
- INT-02

Success criteria:
1. Frontend submits typed payloads to backend `/run` and renders normalized response contracts.
2. Backend CORS and environment settings support deployed frontend origins safely.
3. Integration tests cover success and structured failure scenarios across the boundary.
4. Local and staging smoke checks verify the connected flow end to end.

**Plans:** 1 plan

Plans:
- [x] 07-01-PLAN.md - Implement API client integration, CORS-safe backend config, and end-to-end smoke coverage

Status: Complete (2026-03-31)

**UI hint**: yes

## Phase 8: Platform Deployment
Goal: Deploy frontend to Vercel and backend to Render with documented operations and rollback.

Requirements:
- DEP-01
- DEP-02

Success criteria:
1. Frontend is deployed on Vercel with environment-managed backend endpoint configuration.
2. Backend is deployed on Render with health/readiness checks and required secret settings.
3. Deployment runbook includes preflight, smoke, observability checks, and rollback steps.
4. Release checklist captures post-deploy verification for both services.

**Plans:** 1 plan

Plans:
- [x] 08-01-PLAN.md - Configure Vercel and Render deployment pipelines with runbook-backed verification

Status: Complete (2026-04-01)

**UI hint**: yes

---
*Last updated: 2026-04-01 after phase 8 completion*
