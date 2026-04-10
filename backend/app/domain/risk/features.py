from __future__ import annotations


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def _build_churn_lookup(ingestion_payload: dict) -> dict[str, float]:
    churn_rows = ingestion_payload.get("churn", []) if isinstance(ingestion_payload, dict) else []
    lookup: dict[str, float] = {}

    for row in churn_rows:
        if not isinstance(row, dict):
            continue
        contributor = str(row.get("contributor", "")).strip()
        if not contributor:
            continue
        commits = _safe_float(row.get("commits_last_30d", 0.0))
        files_touched = _safe_float(row.get("files_touched_last_30d", 0.0))
        lookup[contributor] = _clamp((commits + files_touched) / 20.0)

    return lookup


def _build_cadence_features(ingestion_payload: dict) -> tuple[float, float]:
    cadence = ingestion_payload.get("cadence", {}) if isinstance(ingestion_payload, dict) else {}
    if not isinstance(cadence, dict):
        cadence = {}

    deployment_count = _safe_float(cadence.get("deployment_count", 0.0))
    issue_opened = _safe_float(cadence.get("issue_opened_count", 0.0))
    issue_closed = _safe_float(cadence.get("issue_closed_count", 0.0))

    deployment_cadence = _clamp(deployment_count / 20.0)
    defect_signal_proxy = _clamp(max(issue_opened - issue_closed, 0.0) / 20.0)
    return deployment_cadence, defect_signal_proxy


def _contributor_churn_intensity(contributors: list[object], churn_lookup: dict[str, float]) -> float:
    if not contributors:
        return 0.0

    normalized = [churn_lookup.get(str(contributor), 0.0) for contributor in contributors]
    return round(sum(normalized) / len(normalized), 4)


def build_risk_features(
    health_rows: list[dict],
    ingestion_payload: dict,
    horizon_days: int = 90,
) -> list[dict]:
    churn_lookup = _build_churn_lookup(ingestion_payload)
    deployment_cadence, defect_signal_proxy = _build_cadence_features(ingestion_payload)
    rows: list[dict] = []

    for row in health_rows:
        component_id = str(row.get("component_id", "")).strip()
        if not component_id:
            continue

        health_score = _clamp(_safe_float(row.get("score", 0.0), 0.0) / 100.0)
        health_risk = 1.0 - health_score
        contributors = list(row.get("contributors", [])) if isinstance(row.get("contributors", []), list) else []

        contributor_churn_intensity = _contributor_churn_intensity(contributors, churn_lookup)
        feature_risk_pressure = round(
            (0.50 * health_risk)
            + (0.25 * contributor_churn_intensity)
            + (0.15 * defect_signal_proxy)
            + (0.10 * (1.0 - deployment_cadence)),
            4,
        )

        rows.append(
            {
                "component_id": component_id,
                "horizon_days": int(horizon_days),
                "health_score": round(health_score, 4),
                "contributor_churn_intensity": round(contributor_churn_intensity, 4),
                "deployment_cadence": round(deployment_cadence, 4),
                "defect_signal_proxy": round(defect_signal_proxy, 4),
                "feature_risk_pressure": feature_risk_pressure,
            }
        )

    return sorted(rows, key=lambda item: (-item["feature_risk_pressure"], item["component_id"]))