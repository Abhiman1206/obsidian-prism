# Phase 1: Foundation Extraction - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-03-27
**Phase:** 01-foundation-extraction
**Areas discussed:** Module boundaries and package layout, Secrets and config loading strategy, Entrypoint contract for extracted code

---

## Module boundaries and package layout

| Option | Description | Selected |
|--------|-------------|----------|
| Layered package (recommended) | `src/loan_agents/{domain,tools,runtime,orchestration}` for clear boundaries and reuse. | |
| Feature folders | Group by workflow stages (validation, credit, risk, compliance) first. | ✓ |
| Single core module first | Minimal split now, refactor later. | |

**User's choice:** Feature folders
**Notes:** Preferred initial migration structure while still accepting shared contracts and thin adapters.

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated `domain/contracts.py` | Single source for typed models used by both orchestration paths. | ✓ |
| Inside each orchestrator package | CrewAI and LangGraph each define their own schemas. | |
| Flat `models.py` at package root | Central file but less explicit domain grouping. | |

**User's choice:** Dedicated `domain/contracts.py`
**Notes:** Shared contract source is locked.

| Option | Description | Selected |
|--------|-------------|----------|
| Unify into one source (recommended) | Single implementation in `tools/mock_data.py` with scenario IDs. | ✓ |
| Keep two variants temporarily | Preserve both until later cleanup. | |
| Replace with fixture loader now | Move scenarios to JSON fixtures immediately. | |

**User's choice:** Unify into one source
**Notes:** Duplicate helper should be removed during extraction.

| Option | Description | Selected |
|--------|-------------|----------|
| Thin adapters, shared core (recommended) | Common business logic in shared modules; framework wrappers stay thin. | ✓ |
| Keep framework logic embedded | Mirror notebook style first, split later. | |
| Abstract framework interface immediately | Introduce orchestration protocol layer now. | |

**User's choice:** Thin adapters, shared core
**Notes:** Framework separation required but no heavy abstraction layer yet.

## Secrets and config loading strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Environment variables (recommended) | Simple, deploy-friendly, works locally and CI/CD. | ✓ |
| `.env` file only | Developer convenience, weaker production posture. | |
| Pluggable secret provider interface | Supports vault later, slightly more setup now. | |

**User's choice:** Environment variables
**Notes:** Runtime must be non-interactive.

| Option | Description | Selected |
|--------|-------------|----------|
| Fail fast on missing required keys (recommended) | Block startup if required values absent/invalid. | ✓ |
| Warn and continue with defaults | Higher risk of hidden runtime failures. | |
| Mode-based strictness | Strict in prod, relaxed in dev. | |

**User's choice:** Fail fast on missing required keys
**Notes:** Startup validation behavior is strict by default.

| Option | Description | Selected |
|--------|-------------|----------|
| Keep current `GOOGLE_API_KEY` plus generic aliases | Backward compatible while enabling extension. | |
| Rename immediately to generic `LLM_API_KEY` | Cleaner abstraction, but breaks direct parity. | ✓ |
| Provider-specific only | Separate keys per provider, no generic alias. | |

**User's choice:** Rename immediately to `LLM_API_KEY`
**Notes:** Generic provider-agnostic contract chosen for extraction baseline.

| Option | Description | Selected |
|--------|-------------|----------|
| Always redact secret values (recommended) | Never print raw key material, include only key names. | ✓ |
| Partial reveal in debug mode | Show prefix/suffix when debug enabled. | |
| No masking in local dev | Fast troubleshooting, higher leakage risk. | |

**User's choice:** Always redact secret values
**Notes:** Security-first logging posture locked.

## Entrypoint contract for extracted code

| Option | Description | Selected |
|--------|-------------|----------|
| Callable Python service interface (recommended) | `run_pipeline(input, mode)` callable used by tests and future API. | ✓ |
| CLI command only | Start with command invocation, add callable later. | |
| FastAPI endpoint immediately | Expose HTTP at once in Phase 1. | |

**User's choice:** Callable Python service interface
**Notes:** API layer can be added later without changing core invocation.

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit enum argument (recommended) | `mode='crewai'|'langgraph'` required by caller. | ✓ |
| Auto-detect by available deps | Mode inferred at runtime. | |
| Separate functions per framework | `run_crewai` and `run_langgraph` only. | |

**User's choice:** Explicit enum argument
**Notes:** Mode ambiguity removed.

| Option | Description | Selected |
|--------|-------------|----------|
| Normalized structured dict (recommended) | Decision, stage outputs, and error block in one schema. | ✓ |
| Raw framework result | Return Crew/LangGraph native output directly. | |
| Markdown report string | Match notebook-style reporting first. | |

**User's choice:** Normalized structured dict
**Notes:** Contract should be stable and framework-agnostic.

| Option | Description | Selected |
|--------|-------------|----------|
| Return structured failure only (recommended) | No silent fallback to other mode; deterministic behavior. | ✓ |
| Auto-fallback to other framework | Try alternate mode automatically. | |
| Raise exception to caller | No failure envelope, caller handles all. | |

**User's choice:** Return structured failure only
**Notes:** Deterministic error semantics chosen.

## the agent's Discretion

- Exact submodule naming under feature folders
- Internal helper abstractions around settings and redaction

## Deferred Ideas

None.
