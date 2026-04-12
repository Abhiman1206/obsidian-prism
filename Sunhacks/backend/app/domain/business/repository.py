from __future__ import annotations

import json

from app.infra.database import get_db


class ExecutiveReportRepository:
    def add(self, record: dict) -> None:
        conn = get_db()
        conn.execute(
            """INSERT INTO executive_reports
               (run_id, report_id, executive_summary, cost_of_inaction, report_json, generated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                record.get("run_id", ""),
                record.get("report_id", ""),
                record.get("executive_summary", ""),
                float(record.get("cost_of_inaction_estimate", 0.0)),
                json.dumps(record),
                record.get("generated_at", ""),
            ),
        )
        conn.commit()

    def get_by_run(self, run_id: str) -> list[dict]:
        conn = get_db()
        rows = conn.execute(
            """SELECT * FROM executive_reports
               WHERE run_id = ?
               ORDER BY generated_at DESC""",
            (run_id,),
        ).fetchall()
        results: list[dict] = []
        for row in rows:
            results.append(json.loads(row["report_json"] or "{}"))
        return results

    def get_latest(self) -> dict | None:
        conn = get_db()
        row = conn.execute(
            """SELECT report_json FROM executive_reports
               ORDER BY generated_at DESC
               LIMIT 1"""
        ).fetchone()
        if row is None:
            return None
        return json.loads(row["report_json"] or "{}")


EXECUTIVE_REPORT_REPOSITORY = ExecutiveReportRepository()
