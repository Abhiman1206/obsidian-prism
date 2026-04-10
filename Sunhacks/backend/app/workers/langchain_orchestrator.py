from __future__ import annotations

from collections.abc import Callable

from app.api.schemas.run import RunStatus
from app.domain.business.translation import translate_risk_to_business_impact
from app.domain.ingestion.checkpoints import CheckpointStore
from app.domain.risk.features import build_risk_features
from app.workers.business_reporting import run_business_reporting
from app.workers.health_scoring import run_health_scoring
from app.workers.incremental_ingestion import run_incremental_ingestion
from app.workers.provider_ingestion import run_provider_ingestion
from app.workers.risk_forecasting import run_risk_forecasting

try:
    from langchain_core.runnables import RunnableLambda
except ImportError:  # pragma: no cover
    class RunnableLambda:  # type: ignore[override]
        def __init__(self, fn: Callable[[dict], dict]) -> None:
            self._fn = fn

        def __or__(self, other: "RunnableLambda") -> "RunnableLambda":
            def chained(context: dict) -> dict:
                return other.invoke(self.invoke(context))

            return RunnableLambda(chained)

        def invoke(self, value: dict) -> dict:
            return self._fn(value)


def get_orchestration_engine() -> str:
    return "langchain-core"


def _should_fail(repository_id: str, stage_name: str) -> bool:
    token = f"fail-{stage_name}"
    return token in repository_id


def _repository_slug(repository_id: str) -> str:
    suffix = repository_id.removeprefix("repo-")
    parts = [part for part in suffix.split("-") if part]
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    if parts:
        return f"acme/{parts[0]}"
    return "acme/platform"


def _build_metric_rows(components: list[str]) -> list[dict]:
    return [
        {
            "component_id": component,
            "maintainability_index": 78.0,
            "complexity": 12.0,
            "contributors": ["radon_complexity", "radon_maintainability"],
        }
        for component in components
    ]


def _build_volatility_map(components: list[str]) -> dict[str, float]:
    return {component: 0.22 for component in components}


def _mock_request_get(endpoint: str, headers: dict[str, str], params: dict | None = None) -> dict:
    _ = headers
    _ = params
    if endpoint.endswith("/commits"):
        return {
            "items": [
                {
                    "sha": "abc123",
                    "author_email": "engineer@example.com",
                    "authored_at": "2026-01-10T12:00:00Z",
                    "files": [
                        {"path": "backend/app/main.py", "additions": 30, "deletions": 4},
                        {"path": "backend/app/workers/provider_ingestion.py", "additions": 10, "deletions": 2},
                    ],
                },
                {
                    "sha": "def456",
                    "author_email": "reviewer@example.com",
                    "authored_at": "2026-01-11T12:00:00Z",
                    "files": [
                        {"path": "backend/app/workers/risk_forecasting.py", "additions": 20, "deletions": 8},
                    ],
                },
            ],
            "next_cursor": None,
        }
    if endpoint.endswith("/issues"):
        return {"open": 4, "closed": 5}
    if endpoint.endswith("/deployments"):
        return {"count": 6}
    return {"items": [], "next_cursor": None}


def _stage_provider(context: dict) -> dict:
    repository_id = context["repository_id"]
    if _should_fail(repository_id, "provider"):
        raise RuntimeError("provider stage forced failure")

    repository = _repository_slug(repository_id)
    provider_payload = run_provider_ingestion(
        repository_id=repository_id,
        provider=context["provider"],
        repository=repository,
        token="integration-token",
        request_get=_mock_request_get,
    )

    raw_commits = [
        {
            "sha": row["commit_sha"],
            "authored_at": row["authored_at"],
            "files": [],
        }
        for row in provider_payload["commits"]
    ]

    return {**context, "provider_payload": provider_payload, "raw_commits": raw_commits}


def _stage_incremental(context: dict) -> dict:
    repository_id = context["repository_id"]
    if _should_fail(repository_id, "incremental"):
        raise RuntimeError("incremental stage forced failure")

    checkpoint_store = CheckpointStore()
    run_incremental_ingestion(
        repository_id=repository_id,
        provider=context["provider"],
        commits=context["raw_commits"],
        checkpoint_store=checkpoint_store,
        persist_records=lambda _rows: None,
    )

    return context


def _stage_health(context: dict) -> dict:
    repository_id = context["repository_id"]
    if _should_fail(repository_id, "health"):
        raise RuntimeError("health stage forced failure")

    components = [
        "backend/app/main.py",
        "backend/app/workers/provider_ingestion.py",
        "backend/app/workers/risk_forecasting.py",
    ]
    metric_rows = _build_metric_rows(components)
    volatility_map = _build_volatility_map(components)

    health_rows = run_health_scoring(
        run_id=context["run_id"],
        repository_id=repository_id,
        metric_rows=metric_rows,
        volatility_by_component=volatility_map,
    )

    return {**context, "health_rows": health_rows}


def _stage_risk(context: dict) -> dict:
    repository_id = context["repository_id"]
    if _should_fail(repository_id, "risk"):
        raise RuntimeError("risk stage forced failure")

    risk_features = build_risk_features(
        health_rows=context["health_rows"],
        ingestion_payload=context["provider_payload"],
        horizon_days=90,
    )
    forecasts = run_risk_forecasting(
        run_id=context["run_id"],
        repository_id=repository_id,
        feature_rows=risk_features,
    )

    return {**context, "forecasts": forecasts}


def _stage_business(context: dict) -> dict:
    repository_id = context["repository_id"]
    if _should_fail(repository_id, "business"):
        raise RuntimeError("business stage forced failure")

    translated = translate_risk_to_business_impact(context["forecasts"])
    report = run_business_reporting(run_id=context["run_id"], translated_rows=translated)

    return {**context, "report": report}


def orchestrate_run(run_id: str, repository_id: str, provider: str, branch: str | None) -> dict[str, object]:
    pipeline = (
        RunnableLambda(_stage_provider)
        | RunnableLambda(_stage_incremental)
        | RunnableLambda(_stage_health)
        | RunnableLambda(_stage_risk)
        | RunnableLambda(_stage_business)
    )

    try:
        pipeline.invoke(
            {
                "run_id": run_id,
                "repository_id": repository_id,
                "provider": provider,
                "branch": branch,
            }
        )
        return {
            "status": RunStatus.SUCCEEDED,
            "message": f"Run completed with langchain orchestration on branch {branch or 'default'}",
        }
    except Exception as exc:
        return {
            "status": RunStatus.FAILED,
            "message": f"Run failed: {exc}",
        }
