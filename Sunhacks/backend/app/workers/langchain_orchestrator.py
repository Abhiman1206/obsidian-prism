from __future__ import annotations

from app.api.schemas.run import RunStatus
from app.domain.business.translation import translate_risk_to_business_impact
from app.domain.ingestion.checkpoints import CheckpointStore
from app.domain.risk.features import build_risk_features
from app.workers.business_reporting import run_business_reporting
from app.workers.health_scoring import run_health_scoring
from app.workers.incremental_ingestion import run_incremental_ingestion
from app.workers.provider_ingestion import run_provider_ingestion
from app.workers.risk_forecasting import run_risk_forecasting


def _fetch_provider_page(_cursor: object) -> dict:
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


def _build_metric_rows(components: list[str]) -> list[dict]:
    rows: list[dict] = []
    for component in components:
        rows.append(
            {
                "component_id": component,
                "maintainability_index": 78.0,
                "complexity": 12.0,
                "contributors": ["radon_complexity", "radon_maintainability"],
            }
        )
    return rows


def _build_volatility_map(components: list[str]) -> dict[str, float]:
    return {component: 0.22 for component in components}


def _should_fail(repository_id: str, stage_name: str) -> bool:
    token = f"fail-{stage_name}"
    return token in repository_id


def orchestrate_run(run_id: str, repository_id: str, provider: str, branch: str | None) -> dict[str, object]:
    try:
        if _should_fail(repository_id, "provider"):
            raise RuntimeError("provider stage forced failure")

        provider_payload = run_provider_ingestion(
            repository_id=repository_id,
            provider=provider,
            fetch_commits=_fetch_provider_page,
            cadence_source={
                "deployment_count": 6,
                "issue_opened_count": 4,
                "issue_closed_count": 5,
            },
        )

        if _should_fail(repository_id, "incremental"):
            raise RuntimeError("incremental stage forced failure")

        raw_commits = _fetch_provider_page(None).get("items", [])

        checkpoint_store = CheckpointStore()
        _ = run_incremental_ingestion(
            repository_id=repository_id,
            provider=provider,
            commits=raw_commits,
            checkpoint_store=checkpoint_store,
            persist_records=lambda _rows: None,
        )

        components = [
            "backend/app/main.py",
            "backend/app/workers/provider_ingestion.py",
            "backend/app/workers/risk_forecasting.py",
        ]
        metric_rows = _build_metric_rows(components)
        volatility_map = _build_volatility_map(components)

        if _should_fail(repository_id, "health"):
            raise RuntimeError("health stage forced failure")

        health_rows = run_health_scoring(
            run_id=run_id,
            repository_id=repository_id,
            metric_rows=metric_rows,
            volatility_by_component=volatility_map,
        )

        risk_features = build_risk_features(health_rows=health_rows, ingestion_payload=provider_payload, horizon_days=90)

        if _should_fail(repository_id, "risk"):
            raise RuntimeError("risk stage forced failure")

        forecasts = run_risk_forecasting(run_id=run_id, repository_id=repository_id, feature_rows=risk_features)

        if _should_fail(repository_id, "business"):
            raise RuntimeError("business stage forced failure")

        translated = translate_risk_to_business_impact(forecasts)
        _ = run_business_reporting(run_id=run_id, translated_rows=translated)

        return {
            "status": RunStatus.SUCCEEDED,
            "message": f"Run completed successfully on branch {branch or 'default'}",
        }
    except Exception as exc:
        return {
            "status": RunStatus.FAILED,
            "message": f"Run failed: {exc}",
        }
