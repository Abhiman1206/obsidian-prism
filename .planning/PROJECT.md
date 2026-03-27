# Chapter 15 Agents Productionization

## What This Is

This project transforms the Chapter 15 notebook prototype into a production-ready, testable, and operable multi-agent loan origination system. It keeps the same business workflow (validation, credit, risk, compliance) while replacing notebook-only execution patterns with modular code, environment-safe configuration, deployment packaging, and observability. The primary users are engineering teams and platform operators who need reliable, auditable agent workflows in real environments.

## Core Value

Deliver reliable and auditable loan-origination agent decisions with deterministic behavior and safe failure handling in production.

## Requirements

### Validated

- [x] Notebook extraction baseline validated in Phase 1 (contracts, orchestration stubs, runtime modules)
- [x] Non-interactive environment-based secret handling validated in Phase 1
- [x] Fail-fast configuration validation validated in Phase 1

### Active

- [ ] Expand extracted package to full dual-orchestrator parity and production runtime controls.
- [ ] Add production guardrails: retry/rate-limit controls, and structured error reports.
- [ ] Add broader automated tests, CI checks, and deployment-ready run paths.

### Out of Scope

- Full real bureau/vendor integrations in v1 - this phase focuses on production hardening of current mock-driven logic.
- Building a frontend UI - current scope is backend workflow and operational readiness.

## Context

Current implementation is a single notebook (`Chapter_15_Agents.ipynb`) containing both CrewAI and LangGraph examples, inline dependency installation, direct API key prompts, duplicate helper definitions, and mixed demo/reporting logic. For production use, this must be restructured into maintainable modules, deterministic execution entry points, and test coverage for both happy/unhappy paths.

## Constraints

- **Runtime**: Python-based implementation must remain compatible with CrewAI and LangGraph ecosystems - current architecture depends on both frameworks.
- **Security**: No interactive secret prompts in runtime paths - production requires environment/secret manager injection.
- **Reliability**: Must preserve safe-mode behavior (rate limit + retry + graceful failures) - these are explicit notebook design goals.
- **Cost/Quota**: Should support low-quota operation and deterministic fallback modes - notebook targets free-tier API limits.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Keep both CrewAI and LangGraph implementations | The chapter's core educational and comparative value is framework parity | - Pending |
| Treat notebook as source of business rules, not production runtime | Notebook cells are not suitable as operational boundaries | - Pending |
| Prioritize testability and deterministic behavior before feature expansion | Production readiness requires confidence and repeatability first | - Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? -> Move to Out of Scope with reason
2. Requirements validated? -> Move to Validated with phase reference
3. New requirements emerged? -> Add to Active
4. Decisions to log? -> Add to Key Decisions
5. "What This Is" still accurate? -> Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check - still the right priority?
3. Audit Out of Scope - reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-27 after phase 1 completion*
