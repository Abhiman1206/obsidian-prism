# Chapter 15 Agents Productionization

## Foundation Extraction Runtime

The extracted runtime exposes a callable service entrypoint:

- Signature: run_pipeline(input_payload: dict, mode: str) -> dict
- Accepted mode values: crewai, langgraph
- Required environment variable: LLM_API_KEY

Failure behavior is deterministic and always returns a structured envelope with
status, decision, mode, stages, and error keys.
