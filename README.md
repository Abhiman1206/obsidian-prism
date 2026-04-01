# Chapter 15 Agents Productionization

## Foundation Extraction Runtime

The extracted runtime exposes a callable service entrypoint:

- Signature: run_pipeline(input_payload: dict, mode: str) -> dict
- Accepted mode values: crewai, langgraph
- Required environment variable: LLM_API_KEY

Failure behavior is deterministic and always returns a structured envelope with
status, decision, mode, stages, and error keys.

One input payload shape works for both orchestration strategies:

```python
from loan_agents.runtime.service import run_pipeline

payload = {"applicant_id": "app_100", "document_id": "document_valid_123"}

crewai_result = run_pipeline(payload, "crewai")
langgraph_result = run_pipeline(payload, "langgraph")
```

Both calls return the same normalized response schema and deterministic decision
behavior for the same document scenario.

## Environment Configuration

Runtime settings can be defined in a root `.env` file (for local development)
or exported in the shell. Shell environment variables take precedence over
`.env` values.

Example `.env`:

```env
LLM_API_KEY=test-key
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

## Reproducible Setup

Create a virtual environment and install pinned dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

## Quality Gates (CI Parity)

Run the same checks used by pull-request CI:

```bash
python -m ruff check src tests
python -m mypy src/loan_agents
python -m pytest -q
```

All commands are non-interactive and deterministic when installed from
`requirements-dev.txt`.

## Container Runtime

Build and run the runtime service locally:

```bash
docker build -t loan-agents:local .
docker run --rm -p 8000:8000 -e LLM_API_KEY=test-key loan-agents:local
```

Smoke-check endpoints:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/readiness
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d '{"applicant_id":"app_100","document_id":"document_valid_123","mode":"crewai"}'
```

For release preflight, smoke, and rollback steps, see
`.planning/phases/05-release-hardening/05-RELEASE-CHECKLIST.md`.

## Frontend Application (Phase 06)

The repository includes a standalone frontend app in `frontend/` for loan input,
request lifecycle visibility, and normalized decision rendering.

Install frontend dependencies:

```bash
npm --prefix frontend ci
```

Run the frontend locally:

```bash
npm --prefix frontend run dev
```

Frontend quality gates:

```bash
npm --prefix frontend run lint
npm --prefix frontend run typecheck
npm --prefix frontend run test -- --run
npm --prefix frontend run build
```

Runtime integration seam:

- `VITE_USE_MOCK=false` enables backend runtime integration (default behavior in Phase 07).
- Set `VITE_USE_MOCK=true` to force local mock responses.
- `VITE_RUNTIME_API_URL` defaults to `http://localhost:8000`.

This allows Phase 06 to stay standalone while preserving direct backend wiring for
Phase 07 integration.

## Frontend/Backend Integration (Phase 07)

Backend CORS is controlled through environment variables:

- `CORS_ALLOWED_ORIGINS`: comma-separated frontend origins (default: `http://localhost:5173`)
- `CORS_ALLOW_CREDENTIALS`: optional boolean (`true`/`false`, default `false`)

Local connected run sequence:

```bash
# Terminal 1: start backend
python -m uvicorn loan_agents.runtime.asgi:app --host 0.0.0.0 --port 8000

# Terminal 2: start frontend (connected mode)
npm --prefix frontend run dev
```

Connected smoke checks:

```bash
python -m pytest tests/runtime/test_runtime_api_endpoints.py -q
python -m pytest tests/runtime/test_runtime_observability_integration.py -q
npm --prefix frontend run test -- --run integration
```

Troubleshooting:

- If browser requests fail with CORS errors, verify the frontend origin exactly matches one entry in `CORS_ALLOWED_ORIGINS`.
- If frontend reports `NETWORK_ERROR`, confirm backend is running at `VITE_RUNTIME_API_URL` and `/health` returns 200.
- If `/readiness` is `not_ready`, ensure `LLM_API_KEY` is set for the backend process.

## Platform Deployment (Phase 08)

Phase 08 adds platform-ready deployment definitions for both services:

- Frontend deployment config: `frontend/vercel.json`
- Frontend env contract: `frontend/.env.example`
- Backend deployment config: `render.yaml`
- Deployment + rollback runbook: `.planning/phases/08-deployment-vercel-render/08-RELEASE-CHECKLIST.md`

### Frontend on Vercel

Use `frontend/` as the Vercel project root and set environment variables:

- `VITE_RUNTIME_API_URL=https://<render-service-domain>`
- Optional `VITE_USE_MOCK=false`
- Optional `VITE_RUNTIME_TIMEOUT_MS=10000`

`frontend/vercel.json` defines deterministic install/build/output behavior and SPA rewrites.

### Backend on Render

Use infrastructure blueprint from `render.yaml`.

Required Render secrets/config:

- `LLM_API_KEY` (required)
- `CORS_ALLOWED_ORIGINS` (required, must include frontend origin)

Configured endpoints after deploy:

- `https://<render-service-domain>/health`
- `https://<render-service-domain>/readiness`
- `https://<render-service-domain>/run`

### Deployment Verification Matrix

Local validation before promotion:

```bash
npm --prefix frontend run lint
npm --prefix frontend run typecheck
npm --prefix frontend run test -- --run
npm --prefix frontend run build
python -m pytest -q
```

Post-deploy smoke checks:

```bash
curl https://<render-service-domain>/health
curl https://<render-service-domain>/readiness
curl -X POST https://<render-service-domain>/run -H "Content-Type: application/json" -d '{"applicant_id":"app_100","document_id":"document_valid_123","mode":"crewai"}'
```

For full preflight, rollout order, observability checks, and rollback steps, use:

- `.planning/phases/08-deployment-vercel-render/08-RELEASE-CHECKLIST.md`
