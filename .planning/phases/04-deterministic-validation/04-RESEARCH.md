# Phase 04 Research: Deterministic Validation

**Phase:** 4 - Deterministic Validation
**Date:** 2026-03-31
**Status:** Complete

## Objective

Research how to verify deterministic outcomes for both happy and unhappy paths across CrewAI and LangGraph, with unattended diagnostics and parity guarantees.

## Inputs Reviewed

- .planning/ROADMAP.md
- .planning/REQUIREMENTS.md
- .planning/PROJECT.md
- .planning/STATE.md
- .planning/phases/02-dual-orchestrator-core/02-02-SUMMARY.md
- .planning/phases/03-production-runtime-and-ops/03-01-SUMMARY.md
- .planning/phases/03-production-runtime-and-ops/03-03-SUMMARY.md
- src/loan_agents/runtime/service.py
- src/loan_agents/orchestration/normalized.py
- src/loan_agents/orchestration/crewai_adapter.py
- src/loan_agents/orchestration/langgraph_adapter.py
- src/loan_agents/document/mock_data.py
- tests/foundation/test_dual_mode_samples.py
- tests/foundation/test_orchestrator_output_contract.py
- tests/runtime/test_failure_mission_report.py

## Current-State Findings

1. Both orchestration adapters already return normalized top-level keys, and existing parity tests validate success-path decision parity.
2. Runtime mission-report failures include deterministic metadata for invalid mode, timeout, rate limit, and provider errors.
3. Adapter-level document failures (`DOCUMENT_ERROR`) currently return only `code` and `message`, without mission-report metadata fields used elsewhere (`failure_category`, `retry_count`, `stage`).
4. Existing parity tests cover one pass per scenario but do not assert repeat-run determinism for known unhappy paths.
5. Existing tests are split across foundation and runtime, but there is no dedicated deterministic matrix test that compares sanitized results across multiple runs and both modes.

## Recommended Implementation Strategy

### A. Unit-Level Deterministic Contract Hardening (QUAL-01)

- Extend adapter failure normalization to include deterministic mission-report metadata:
  - `failure_category: invalid_document`
  - `retry_count: 0`
  - `stage: document`
- Add unit tests for:
  - normalized helper output (success + adapter failure)
  - adapter contract parity for known document scenarios
  - runtime wrapper unhappy-path metadata stability for existing policy failures

### B. Integration Deterministic Matrix (QUAL-02, RELI-04)

- Create integration-style parity matrix tests that execute both modes for:
  - happy path (`document_valid_123`)
  - low-score/review path (`document_risky_789`)
  - invalid document path (`document_unknown_999`)
  - provider-failure path (controlled monkeypatch)
- Assert deterministic parity on shared fields across modes and repeat runs.
- Ignore expected per-run variances (`mode`, `correlation_id`, dynamic timing metrics) by sanitizing result payloads before equality assertions.

### C. Unattended Diagnostics and Failure Clarity

- Keep all verification automated with explicit pytest commands scoped to deterministic-validation files.
- Ensure failing assertions print scenario/mode labels for fast diagnosis.
- Add a phase-focused aggregate command that runs quickly and unattended.

## Validation Architecture

### Verification Layers

1. Unit tests for normalized adapter error contract and runtime wrapper failure metadata behavior.
2. Integration matrix tests for dual-mode parity across known happy and unhappy scenarios.
3. Repeat-run determinism checks ensuring same scenario yields stable outcomes.
4. Phase-focused unattended command suitable for CI and local verification.

### Nyquist Notes for Phase 04

- Every plan task includes an automated pytest command.
- Deterministic matrix tests must compare normalized payload subsets, not raw runtime-specific fields.
- Keep quick feedback under 60 seconds with targeted test-file selection.

## Risks and Mitigations

- Risk: Over-constraining parity can fail on intentional mode-specific metadata.
  - Mitigation: sanitize non-parity fields before equality checks and document exclusions.
- Risk: Provider-failure tests can become flaky if monkeypatch scope leaks.
  - Mitigation: use function-scoped monkeypatch in each test and isolate side effects.
- Risk: Existing tests may assume legacy adapter failure shape.
  - Mitigation: update affected tests in the same task to assert deterministic enriched error shape.

## Recommendation

Create two execution plans:
1. Unit-level deterministic contract hardening and unhappy-path metadata normalization.
2. Integration parity matrix and unattended deterministic diagnostics command.
