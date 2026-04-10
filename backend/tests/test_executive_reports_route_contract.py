from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient

from app.main import app
from app.workers.business_reporting import persist_executive_report


def test_executive_reports_route_returns_sorted_reports_with_claim_lineage_refs() -> None:
    persist_executive_report(
        {
            "report_id": "report-old",
            "run_id": "run-biz-03",
            "executive_summary": "Cost exposure is material and needs immediate action.",
            "cost_of_inaction_estimate": 9500.0,
            "top_risks": [
                {
                    "component_id": "src/orders.py",
                    "expected_total_cost": 5200.0,
                    "expected_engineering_hours": 14.0,
                    "expected_downtime_hours": 3.2,
                }
            ],
            "cost_of_inaction": {
                "expected_total_cost": 9500.0,
                "summary": "Projected near-term business loss from unresolved risk.",
            },
            "recommended_priorities": [
                {
                    "component_id": "src/orders.py",
                    "action": "Reduce release-blocking risk this sprint",
                    "expected_total_cost": 5200.0,
                }
            ],
            "claims": [
                {
                    "claim_id": "claim-1",
                    "claim_text": "Orders service has highest short-term cost exposure.",
                    "lineage_refs": ["lineage-a", "lineage-b"],
                }
            ],
            "generated_at": "2026-04-10T00:00:00Z",
        }
    )

    persist_executive_report(
        {
            "report_id": "report-new",
            "run_id": "run-biz-03",
            "executive_summary": "Primary risk concentration remains in customer-facing modules.",
            "cost_of_inaction_estimate": 11000.0,
            "top_risks": [
                {
                    "component_id": "src/billing.py",
                    "expected_total_cost": 6100.0,
                    "expected_engineering_hours": 16.0,
                    "expected_downtime_hours": 3.8,
                }
            ],
            "cost_of_inaction": {
                "expected_total_cost": 11000.0,
                "summary": "Projected near-term business loss from unresolved risk.",
            },
            "recommended_priorities": [
                {
                    "component_id": "src/billing.py",
                    "action": "Contain billing interruption risk first",
                    "expected_total_cost": 6100.0,
                }
            ],
            "claims": [
                {
                    "claim_id": "claim-2",
                    "claim_text": "Billing service risk is tied to customer churn exposure.",
                    "lineage_refs": ["lineage-c"],
                }
            ],
            "generated_at": "2026-04-10T01:00:00Z",
        }
    )

    client = TestClient(app)
    response = client.get("/api/executive-reports/run-biz-03")

    assert response.status_code == 200
    payload = response.json()
    assert [row["report_id"] for row in payload] == ["report-new", "report-old"]

    required_fields = {
        "report_id",
        "run_id",
        "executive_summary",
        "cost_of_inaction_estimate",
        "top_risks",
        "cost_of_inaction",
        "recommended_priorities",
        "claims",
        "generated_at",
    }
    assert required_fields.issubset(payload[0].keys())

    claim = payload[0]["claims"][0]
    assert {"claim_id", "claim_text", "lineage_refs"}.issubset(claim.keys())
    assert isinstance(claim["lineage_refs"], list)


def test_executive_reports_route_returns_empty_list_for_unknown_run() -> None:
    client = TestClient(app)

    response = client.get("/api/executive-reports/unknown-run")

    assert response.status_code == 200
    assert response.json() == []
