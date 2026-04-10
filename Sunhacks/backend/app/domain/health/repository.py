from __future__ import annotations

import json

from app.infra.database import get_db


class HealthScoreRepository:
    def add_many(self, records: list[dict]) -> None:
        conn = get_db()
        for record in records:
            conn.execute(
                """INSERT INTO health_scores
                   (run_id, repository_id, component_id, score, factors_json, contributors_json, measured_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    record.get("run_id", ""),
                    record.get("repository_id", ""),
                    record.get("component_id", ""),
                    float(record.get("score", 0.0)),
                    json.dumps(record.get("factors", [])),
                    json.dumps(record.get("contributors", [])),
                    record.get("measured_at", ""),
                ),
            )
        conn.commit()

    def get_by_run(self, run_id: str) -> list[dict]:
        conn = get_db()
        rows = conn.execute(
            "SELECT * FROM health_scores WHERE run_id = ? ORDER BY score ASC",
            (run_id,),
        ).fetchall()
        results: list[dict] = []
        for row in rows:
            results.append(
                {
                    "run_id": row["run_id"],
                    "repository_id": row["repository_id"],
                    "component_id": row["component_id"],
                    "score": row["score"],
                    "factors": json.loads(row["factors_json"] or "[]"),
                    "contributors": json.loads(row["contributors_json"] or "[]"),
                    "measured_at": row["measured_at"],
                }
            )
        return results


HEALTH_SCORE_REPOSITORY = HealthScoreRepository()
