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
