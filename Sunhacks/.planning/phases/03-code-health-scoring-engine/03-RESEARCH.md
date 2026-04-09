---
phase: 03-code-health-scoring-engine
status: complete
created: 2026-04-10
requirements: [HEALTH-01, HEALTH-02, HEALTH-03]
---

# Phase 3 Research: Code Health Scoring Engine

## Objective
Design an implementation path for deterministic, explainable health scoring from repository source artifacts produced in Phase 2.

## Existing Codebase Signals
- Backend is service-first: API route -> domain service/worker -> repository boundary.
- Tests are pytest-based and are written before implementation in small RED/GREEN slices.
- Contracts are centralized in `contracts/v1` and mirrored in frontend `frontend/lib/contracts/index.ts`.
- Evidence and query patterns already exist (`domain/evidence/*`, `api/routes/lineage.py`).

## Recommended Architecture

### 1) Radon metrics extraction boundary
Create `backend/app/domain/health/metrics.py` with pure functions:
- `collect_python_files(payload: dict) -> list[str]`
- `compute_radon_metrics(files: list[str]) -> list[dict]`
- `build_metric_snapshot(run_id: str, repository_id: str, metrics: list[dict]) -> list[dict]`

Notes:
- Prefer Radon when import succeeds.
- If Radon is unavailable or file parsing fails, return deterministic fallback values and include a contributor marker (`radon_unavailable` or `analysis_error`).
- Ignore generated and non-source files (`node_modules`, `.venv`, `dist`, `build`, `__pycache__`, minified files).

### 2) Health score aggregation boundary
Create `backend/app/domain/health/scoring.py`:
- Input: complexity + maintainability + volatility values per component.
- Output: normalized score in [0,100] and explainability object.

Recommended stable weighting (v1 deterministic baseline):
- Maintainability: 0.45
- Cyclomatic complexity: 0.35
- Change volatility: 0.20

Normalization guidance:
- Maintainability index is positive signal: higher is better.
- Complexity and volatility are inverse signals: higher is worse.
- Clamp each normalized dimension to [0,1], then compute weighted aggregate.
- Final score = round(100 * aggregate, 2)

### 3) Explainability persistence and API exposure
Create `backend/app/domain/health/repository.py` and `backend/app/api/routes/health_scores.py`:
- Store run-scoped health records in a repository boundary similar to `LineageRepository`.
- Expose `GET /api/health-scores/{run_id}` returning list of typed records.
- Record contributors with both labels and values (not only labels).

## Data Contract Updates
Current `HealthScore` is too shallow (`contributors: list[str]`).
Update `contracts/v1/health.py` and frontend mirror to include factors:
- `component_id: str`
- `score: float (0..100)`
- `contributors: list[str]` (kept for compatibility)
- `factors: list[HealthFactor]` where each factor includes:
  - `name: str`
  - `weight: float`
  - `raw_value: float`
  - `normalized_value: float`
  - `direction: str` (`positive` | `negative`)
- `measured_at: datetime`
- `run_id: str`
- `repository_id: str`

## File and Module Targets
- `backend/app/domain/health/metrics.py` (new)
- `backend/app/domain/health/scoring.py` (new)
- `backend/app/domain/health/repository.py` (new)
- `backend/app/workers/health_scoring.py` (new)
- `backend/app/api/routes/health_scores.py` (new)
- `backend/app/main.py` (modify route registration)
- `contracts/v1/health.py` (modify)
- `frontend/lib/contracts/index.ts` (modify)
- `backend/tests/test_health_metrics.py` (new)
- `backend/tests/test_health_scoring.py` (new)
- `backend/tests/test_health_scores_route_contract.py` (new)
- `backend/tests/test_contract_alignment.py` (update assertions if needed)

## Risks and Mitigations
- Risk: Radon not installed in runtime.
  - Mitigation: Safe import with deterministic fallback factors and explicit contributor marker.
- Risk: Non-Python repositories in future phases.
  - Mitigation: Metrics extractor should return empty metric list plus clear contributor marker instead of failing.
- Risk: Contract drift backend/frontend.
  - Mitigation: Maintain alignment tests and extend mirrored TS interfaces in the same plan.

## Validation Architecture

### Required checks per requirement
- HEALTH-01: `pytest backend/tests/test_health_metrics.py -q`
- HEALTH-02: `pytest backend/tests/test_health_scoring.py -q`
- HEALTH-03: `pytest backend/tests/test_health_scores_route_contract.py -q`
- Contract parity: `pytest backend/tests/test_contract_alignment.py -q`

### Full regression gate
- `pytest backend/tests -q`

### Expected verification properties
- Metrics include complexity + maintainability per component/module.
- Score remains within [0,100] and uses fixed deterministic weights.
- API payload includes factor-level explainability fields for each returned health score.

## Recommendation
Proceed with three plans in dependency order:
1. Radon metrics extraction and health factor contract extension.
2. Scoring + normalization algorithm with deterministic weights and unit tests.
3. Persistence/repository + API exposure for explainability metadata.
