# Research Summary: Chapter 15 Agents Productionization

## Stack
Use Python 3.11 with modular package structure, FastAPI for runtime API surface, pydantic for contracts/config, tenacity for retries, structured logging, pytest+ruff+mypy for quality gates, and Docker for deployability.

## Table Stakes
- Modularized non-notebook runtime code
- Typed request/response contracts
- Deterministic execution for both CrewAI and LangGraph paths
- Safe retries/throttling/timeouts
- Structured logs and deployment health checks
- Automated tests and CI gates

## Differentiators
- Cross-framework parity validation and unified decision reports
- Replayable mission reports and richer audit traces
- Optional provider abstraction for model portability

## Watch Out For
- Framework output drift without shared business rule core
- Interactive or leaked secret flows
- Retry storms that worsen quota failures
- Missing end-to-end tests for unhappy paths

## Milestone Context
Greenfield productionization initiative from an educational notebook baseline. Scope should prioritize reliability, security, and testability before adding new product features.
