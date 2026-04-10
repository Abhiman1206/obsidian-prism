from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.domain.business.report_writer import write_executive_report  # noqa: E402


def _translated_rows() -> list[dict]:
    return [
        {
            "component_id": "src/core.py",
            "expected_engineering_hours": 28.0,
            "expected_downtime_hours": 7.5,
            "expected_total_cost": 16450.0,
            "cost_drivers": ["downtime_exposure", "engineering_effort"],
        },
        {
            "component_id": "src/payments.py",
            "expected_engineering_hours": 22.0,
            "expected_downtime_hours": 4.8,
            "expected_total_cost": 12160.0,
            "cost_drivers": ["engineering_effort", "downtime_exposure"],
        },
    ]


def test_report_writer_returns_required_sections() -> None:
    report = write_executive_report("run-biz-02", _translated_rows())

    assert report["run_id"] == "run-biz-02"
    assert "executive_summary" in report
    assert "top_risks" in report
    assert "cost_of_inaction" in report
    assert "recommended_priorities" in report


def test_report_summary_avoids_engineering_jargon() -> None:
    report = write_executive_report("run-biz-02", _translated_rows())

    summary = report["executive_summary"].lower()
    disallowed_tokens = ["cyclomatic", "maintainability", "refactor"]
    assert not any(token in summary for token in disallowed_tokens)


def test_recommendations_are_cost_priority_ordered() -> None:
    report = write_executive_report("run-biz-02", _translated_rows())

    priorities = report["recommended_priorities"]
    ordered_components = [item["component_id"] for item in priorities]
    assert ordered_components == ["src/core.py", "src/payments.py"]
