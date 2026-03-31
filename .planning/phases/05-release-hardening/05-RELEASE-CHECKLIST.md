# Phase 05 Release Checklist

## Preflight

- Confirm working tree is clean and CI checks pass (`ruff`, `mypy`, `pytest`).
- Confirm required runtime env var is available: `LLM_API_KEY`.
- Confirm target image tag is set (example: `loan-agents:v1.0.0`).

## Build

```bash
docker build -t loan-agents:v1.0.0 .
```

## Smoke Test

1. Run container:

```bash
docker run --rm -p 8000:8000 -e LLM_API_KEY=test-key loan-agents:v1.0.0
```

2. Health check:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok","service":"loan-agents"}
```

3. Readiness check:

```bash
curl http://localhost:8000/readiness
```

Expected response contains:

- `status: "ready"`
- `checks.llm_api_key: true`

4. Run-path smoke test:

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"applicant_id":"app_100","document_id":"document_valid_123","mode":"crewai"}'
```

Expected response contains top-level keys:

- `status`
- `decision`
- `mode`
- `stages`
- `error`

## Rollback Basics

1. Stop current deployment and redeploy last known-good image tag.
2. Verify `/health` and `/readiness` on the rolled-back version.
3. Re-run the `/run` smoke request with the same payload used above.
4. Keep failed tag for forensic analysis and open an incident note with failing command output.
