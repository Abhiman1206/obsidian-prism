from __future__ import annotations

from datetime import datetime, timezone
import uuid

from app.domain.business.repository import EXECUTIVE_REPORT_REPOSITORY
from app.domain.business.report_writer import write_executive_report


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _build_claims(run_id: str, report: dict) -> list[dict]:
    claims: list[dict] = []
    for index, item in enumerate(report.get("recommended_priorities", []), start=1):
        component_id = str(item.get("component_id", ""))
        claims.append(
            {
                "claim_id": f"claim-{index}",
                "claim_text": (
                    f"{component_id} is prioritized due to projected cost exposure of "
                    f"${float(item.get('expected_total_cost', 0.0)):,.2f}."
                ),
                "lineage_refs": [f"{run_id}:{component_id}:risk-forecast"],
            }
        )
    return claims


def persist_executive_report(report: dict) -> None:
    EXECUTIVE_REPORT_REPOSITORY.add(report)


def run_business_reporting(run_id: str, translated_rows: list[dict]) -> dict:
    report = write_executive_report(run_id, translated_rows)
    report["report_id"] = f"report-{uuid.uuid4().hex[:12]}"
    report["generated_at"] = _utc_timestamp()
    report["claims"] = _build_claims(run_id, report)
    return report
