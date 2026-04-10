from __future__ import annotations

import json

from app.infra.database import get_db


class RiskForecastRepository:
    def add_many(self, records: list[dict]) -> None:
        conn = get_db()
        for record in records:
            conn.execute(
                """INSERT INTO risk_forecasts
                   (run_id, repository_id, component_id, horizon_days,
                    risk_probability, confidence, top_signals_json, forecasted_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record.get("run_id", ""),
                    record.get("repository_id", ""),
                    record.get("component_id", ""),
                    int(record.get("horizon_days", 90)),
                    float(record.get("risk_probability", 0.0)),
                    float(record.get("confidence", 0.0)),
                    json.dumps(record.get("top_signals", [])),
                    record.get("forecasted_at", ""),
                ),
            )
        conn.commit()

    def get_ranked_by_run(self, run_id: str) -> list[dict]:
        conn = get_db()
        rows = conn.execute(
            """SELECT * FROM risk_forecasts
               WHERE run_id = ?
               ORDER BY risk_probability DESC, component_id ASC""",
            (run_id,),
        ).fetchall()
        results: list[dict] = []
        for row in rows:
            results.append(
                {
                    "run_id": row["run_id"],
                    "repository_id": row["repository_id"],
                    "component_id": row["component_id"],
                    "horizon_days": row["horizon_days"],
                    "risk_probability": row["risk_probability"],
                    "confidence": row["confidence"],
                    "top_signals": json.loads(row["top_signals_json"] or "[]"),
                    "forecasted_at": row["forecasted_at"],
                }
            )
        return results


RISK_FORECAST_REPOSITORY = RiskForecastRepository()