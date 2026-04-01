# Phase 08 Release Checklist: Vercel + Render

## Scope

- Requirement DEP-01: Frontend deployable to Vercel with environment-based backend URL.
- Requirement DEP-02: Backend deployable to Render with health/readiness and required env contract.

## Preflight

- [x] Confirm repository quality gates pass locally:
  - `npm --prefix frontend run lint`
  - `npm --prefix frontend run typecheck`
  - `npm --prefix frontend run test -- --run`
  - `npm --prefix frontend run build`
  - `python -m pytest -q`
- [ ] Confirm backend runtime contract env vars are prepared for Render:
  - Required secret: `LLM_API_KEY`
  - Required CORS origin list: `CORS_ALLOWED_ORIGINS`
- [ ] Confirm frontend runtime API env var is prepared for Vercel:
  - `VITE_RUNTIME_API_URL=https://<render-service-domain>`

## Deploy Order

1. Deploy backend service on Render.
2. Verify backend health and readiness.
3. Deploy frontend on Vercel using backend URL from step 2.
4. Run cross-service smoke tests.

Local status as of 2026-04-01:

- Frontend lint/typecheck/tests/build: passed.
- Focused runtime endpoint tests: passed.
- Full `pytest -q`: one unrelated pre-existing failure in `tests/foundation/test_contracts.py`.
- `ruff check`: passed.
- `mypy`: existing unrelated errors in `src/loan_agents/orchestration/pipeline.py`.

## Render Backend Deployment

- [ ] Create a new Render Web Service from repository root using [render.yaml](render.yaml).
- [ ] Set secret values in Render dashboard:
  - `LLM_API_KEY`
  - `CORS_ALLOWED_ORIGINS` to include the Vercel production domain.
- [ ] Ensure service starts with command:
  - `python -m uvicorn loan_agents.runtime.asgi:app --host 0.0.0.0 --port $PORT`

### Backend Smoke Checks

- [ ] `curl https://<render-service-domain>/health`
- [ ] `curl https://<render-service-domain>/readiness`
- [ ] `curl -X POST https://<render-service-domain>/run -H "Content-Type: application/json" -d '{"applicant_id":"app_100","document_id":"document_valid_123","mode":"crewai"}'`

Expected signals:

- `/health` returns `{"status":"ok","service":"loan-agents"}`.
- `/readiness` reports `status: "ready"` and `checks.llm_api_key: true`.
- `/run` returns normalized response keys: `status`, `decision`, `mode`, `stages`, `error`.

## Vercel Frontend Deployment

- [ ] Create/import Vercel project with root directory `frontend/`.
- [ ] Use [frontend/vercel.json](frontend/vercel.json) for deterministic build/output behavior.
- [ ] Set environment variables in Vercel project:
  - `VITE_RUNTIME_API_URL=https://<render-service-domain>`
  - Optional: `VITE_USE_MOCK=false`
  - Optional: `VITE_RUNTIME_TIMEOUT_MS=10000`
- [ ] Deploy to production and validate app load.

### Frontend Smoke Checks

- [ ] Open `https://<vercel-app-domain>/`.
- [ ] Submit test payload (`app_100`, `document_valid_123`, `crewai`).
- [ ] Confirm success lifecycle and result panel populate from backend response.
- [ ] Confirm frontend failures show structured error envelope if backend returns an error.

## Observability Checks

- [ ] Confirm Render logs include correlation-aware run traces for test submission.
- [ ] Confirm `/run` failures still return structured error envelope (no raw stack trace leakage).
- [ ] Confirm response latency is captured in runtime metrics payload for successful runs.

## Rollback

1. Roll back backend first if API regressions are detected:
   - Restore previous Render deployment.
   - Re-run `/health`, `/readiness`, and `/run` smoke checks.
2. Roll back frontend second:
   - Promote previous known-good Vercel deployment.
3. Restore environment settings snapshot if config drift is involved.
4. Keep failing deployment artifacts and logs for incident follow-up.

## Handoff

- [ ] Record deployed URLs:
  - Frontend: `https://<vercel-app-domain>/`
  - Backend health: `https://<render-service-domain>/health`
  - Backend readiness: `https://<render-service-domain>/readiness`
- [ ] Share ownership notes:
  - Platform owner for Render env vars/secrets.
  - Frontend owner for Vercel env and release rollbacks.