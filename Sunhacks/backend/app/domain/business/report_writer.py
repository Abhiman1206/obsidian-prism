from __future__ import annotations


def _ordered_rows(translated_rows: list[dict]) -> list[dict]:
    return sorted(
        translated_rows,
        key=lambda row: (
            -float(row.get("expected_total_cost", 0.0)),
            str(row.get("component_id", "")),
        ),
    )


def _cost_of_inaction_total(rows: list[dict]) -> float:
    return round(sum(float(row.get("expected_total_cost", 0.0)) for row in rows), 2)


def write_executive_report(run_id: str, translated_rows: list[dict]) -> dict:
    ordered = _ordered_rows(translated_rows)
    total_cost = _cost_of_inaction_total(ordered)

    top_risks = [
        {
            "component_id": str(row.get("component_id", "")),
            "expected_total_cost": round(float(row.get("expected_total_cost", 0.0)), 2),
            "expected_engineering_hours": round(float(row.get("expected_engineering_hours", 0.0)), 2),
            "expected_downtime_hours": round(float(row.get("expected_downtime_hours", 0.0)), 2),
        }
        for row in ordered
    ]

    priorities = [
        {
            "component_id": item["component_id"],
            "action": "Reduce failure exposure in next sprint",
            "expected_total_cost": item["expected_total_cost"],
        }
        for item in top_risks
    ]

    summary = (
        f"Current delivery risk could cost approximately ${total_cost:,.2f} over the next 90 days "
        "if left unaddressed. Focus first on the highest-cost components to reduce likely downtime "
        "and rework expense."
    )

    return {
        "run_id": run_id,
        "executive_summary": summary,
        "cost_of_inaction_estimate": total_cost,
        "top_risks": top_risks,
        "cost_of_inaction": {
            "expected_total_cost": total_cost,
            "summary": "Estimated near-term cost exposure from unresolved component risk.",
        },
        "recommended_priorities": priorities,
    }
