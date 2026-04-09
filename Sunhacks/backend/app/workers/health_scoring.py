from __future__ import annotations

from datetime import datetime, timezone

from app.domain.health.scoring import score_component


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_health_scoring(
    run_id: str,
    repository_id: str,
    metric_rows: list[dict],
    volatility_by_component: dict[str, float],
) -> list[dict]:
    measured_at = _utc_timestamp()
    scored_rows: list[dict] = []

    for metric in metric_rows:
        component_id = metric["component_id"]
        volatility = volatility_by_component.get(component_id, 0.0)
        scored = score_component(
            component_id=component_id,
            maintainability_index=float(metric.get("maintainability_index", 100.0)),
            complexity=float(metric.get("complexity", 0.0)),
            volatility=float(volatility),
            contributors=list(metric.get("contributors", [])),
        )
        scored_rows.append(
            {
                **scored,
                "run_id": run_id,
                "repository_id": repository_id,
                "measured_at": measured_at,
            }
        )

    return scored_rows
