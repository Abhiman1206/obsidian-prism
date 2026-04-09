from __future__ import annotations

from datetime import datetime, timezone
import uuid

from app.domain.business.report_writer import write_executive_report


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_business_reporting(run_id: str, translated_rows: list[dict]) -> dict:
    report = write_executive_report(run_id, translated_rows)
    report["report_id"] = f"report-{uuid.uuid4().hex[:12]}"
    report["generated_at"] = _utc_timestamp()
    return report
