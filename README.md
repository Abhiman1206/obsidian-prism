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
