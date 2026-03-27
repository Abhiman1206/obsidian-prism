# Phase 01 Research: Foundation Extraction

**Phase:** 1 - Foundation Extraction
**Date:** 2026-03-27
**Status:** Complete

## Objective

Research how to extract the notebook implementation into a production-safe module baseline while honoring locked decisions in `01-CONTEXT.md`.

## Inputs Reviewed

- `.planning/phases/01-foundation-extraction/01-CONTEXT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/PROJECT.md`
- `Chapter_15_Agents.ipynb`

## Current-State Findings

1. Secret handling is interactive (`getpass`) and directly mutates env state in notebook runtime.
2. `get_document_content` exists in duplicated forms, creating drift risk.
3. Tool logic, orchestration setup, and execution wrappers are co-located in notebook code cells.
4. Runtime resilience behavior already exists (`robust_execute`) and should be preserved as a module utility.

## Recommended Extraction Strategy

### A. Package Baseline (feature-first, per context D-01)
- Create package root `src/loan_agents/`.
- Create feature modules:
  - `src/loan_agents/document/`
  - `src/loan_agents/credit/`
  - `src/loan_agents/risk/`
  - `src/loan_agents/compliance/`
- Create shared modules:
  - `src/loan_agents/domain/contracts.py` (per D-02)
  - `src/loan_agents/runtime/settings.py`
  - `src/loan_agents/runtime/errors.py`
  - `src/loan_agents/runtime/redaction.py`
  - `src/loan_agents/runtime/service.py`
  - `src/loan_agents/orchestration/crewai_adapter.py`
  - `src/loan_agents/orchestration/langgraph_adapter.py`

### B. Config/Security Baseline (per D-05, D-06, D-07, D-08)
- Introduce typed settings object with required `LLM_API_KEY`.
- Fail startup if missing required keys.
- Remove interactive prompts from runtime path.
- Centralize redaction helpers and prevent secret value logging.

### C. Runtime Contract Baseline (per D-09 to D-12)
- `run_pipeline(input_payload, mode)` callable entrypoint.
- Explicit mode argument: `"crewai" | "langgraph"`.
- Always return normalized dictionary:
  - `status`, `decision`, `mode`, `stages`, `error`.
- No implicit mode fallback.

## Suggested Verification Focus

- Confirm no `getpass(` usage in extracted runtime modules.
- Confirm `LLM_API_KEY` is required in settings.
- Confirm single canonical `get_document_content` implementation exists.
- Confirm `run_pipeline` returns structured failure envelope on provider/config errors.

## Validation Architecture

### Verification Layers
1. Static checks: module boundaries and required symbols.
2. Unit tests: settings validation, redaction, and contract normalization.
3. Smoke path: invoke callable with sample scenarios for both modes.

### Phase 1 Nyquist Notes
- Add Wave 0 tests first because no current test infrastructure exists.
- Every execution task in plans should reference automated checks or explicit Wave 0 dependencies.

## Risks and Mitigations

- Risk: Over-extracting framework internals in Phase 1.
  - Mitigation: Keep adapters thin and defer deep orchestration improvements to Phase 2.
- Risk: Secret naming migration breaks notebook parity.
  - Mitigation: Keep migration notes and optional compatibility shim in non-runtime notebook utility.
- Risk: Hidden duplicate behavior remains in notebook.
  - Mitigation: Explicitly create one canonical mock-data function and document ownership.

## Recommendation

Proceed with two plans:
- Plan 01: package skeleton, contracts, settings, and Wave 0 tests.
- Plan 02: callable service + thin adapters + extraction smoke checks.
