---
phase: 02
slug: repository-ingestion-and-evidence-graph
researched: 2026-04-10
sources:
  - .planning/research/ARCHITECTURE.md
  - .planning/research/STACK.md
  - .planning/research/PITFALLS.md
  - PRD.md
---

# Phase 02 Research Notes

## Scope
Build provider registration/auth, repository ingestion adapters, incremental mining, and evidence lineage persistence.

## Confirmed Constraints
- Use canonical typed contracts first, then wire ingestion behavior.
- Normalize GitHub and GitLab payloads into one internal schema to avoid drift.
- Incremental ingestion is mandatory; avoid full-history rescans on each run.
- Lineage must be written during ingestion, not after report generation.

## Recommended Libraries and Patterns
- API and contracts: FastAPI + pydantic
- Provider HTTP calls: httpx with timeout and retry wrappers
- Commit mining: PyDriller with checkpoint-based incremental windows
- Persistence interface: repository pattern for ingestion artifacts and lineage events
- Testing: pytest contract and integration tests for adapter normalization and checkpoints

## Pitfalls To Prevent In This Phase
1. Provider schema mismatch between GitHub and GitLab payloads.
2. Ingestion jobs that do not resume from checkpoints.
3. Missing lineage links between ingestion artifacts and future report claims.

## Phase 02 Deliverable Focus
- Repository registration APIs for GitHub/GitLab.
- Normalized ingestion adapters for commits, changed files, and cadence signals.
- Incremental PyDriller miner with resume checkpoints.
- Evidence graph schema and lineage writer for ingestion outputs.
