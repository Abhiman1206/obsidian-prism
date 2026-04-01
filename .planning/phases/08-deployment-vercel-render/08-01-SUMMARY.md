# Phase 08-01 Summary: Platform Deployment

## Scope Delivered

Phase 08 delivered deployment-ready platform artifacts for hosting frontend on Vercel and backend on Render, plus an operational runbook that captures preflight, smoke validation, observability checks, and rollback.

## What Was Implemented

- Frontend deployment contract:
  - Added `frontend/vercel.json` with deterministic Vite build/output and SPA rewrite configuration.
  - Added `frontend/.env.example` documenting runtime API URL and deployment-safe frontend runtime variables.
- Backend deployment contract:
  - Added `render.yaml` with a Render web service definition, install/start commands, health check path, and explicit runtime environment contract.
- Cross-platform runbook:
  - Added `.planning/phases/08-deployment-vercel-render/08-RELEASE-CHECKLIST.md` with:
    - Preflight checks
    - Deployment order (Render before Vercel)
    - Backend and frontend smoke checks
    - Observability checks
    - Rollback and handoff steps
- Documentation updates:
  - Updated `README.md` with Phase 08 deployment instructions, env variable contract, and verification matrix commands.
- Test updates:
  - Added `frontend/tests/env.test.ts` to verify deployment environment defaults and runtime API URL normalization behavior.

## Verification Results

Commands run and passing in this phase:

- `npm --prefix frontend run lint`
- `npm --prefix frontend run typecheck`
- `npm --prefix frontend run test -- --run`
- `npm --prefix frontend run build`
- `python -m pytest tests/runtime/test_runtime_api_endpoints.py -q`
- `python -m pytest tests/runtime/test_runtime_observability_integration.py -q`

Commands documented but not executed here due to missing live deployment URLs:

- `curl https://<render-service-domain>/health`
- `curl https://<render-service-domain>/readiness`
- `curl -X POST https://<render-service-domain>/run ...`

## Requirement Status

- DEP-01: Complete
- DEP-02: Complete

## Open Gaps

- Live post-deploy smoke checks on actual Render and Vercel domains remain an operator handoff task after first production deployment.