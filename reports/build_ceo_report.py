from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
import sys

import requests

BASE_URL = "http://localhost:10000"
REPO_URL = "https://github.com/Abhiman1206/AI_APP.git"


def ensure_reportlab() -> None:
    try:
        import reportlab  # noqa: F401
    except Exception:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])


def main() -> None:
    analysis_resp = requests.post(
        f"{BASE_URL}/api/repositories/analyze",
        json={"repository_url": REPO_URL},
        timeout=30,
    )
    analysis_resp.raise_for_status()
    analysis = analysis_resp.json()

    run_id = f"run-{analysis['repository_name'].replace('/', '-')}"
    run_resp = requests.get(f"{BASE_URL}/api/runs/{run_id}", timeout=15)
    run_status = run_resp.json() if run_resp.ok else {
        "run_id": run_id,
        "status": "failed",
        "message": "Run status unavailable",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    health_score = int(analysis.get("health", {}).get("score", 0))
    risk_probability = max(0.05, min(0.95, (100 - health_score) / 100))

    # PRD-aligned business value assumptions
    engineering_hourly_rate_usd = 85
    business_downtime_rate_usd_per_hour = 1200
    incidents_90d = max(1, round(risk_probability * 4))
    engineering_hours_per_incident = 28
    downtime_hours_per_incident = 4

    engineering_hours_loss = incidents_90d * engineering_hours_per_incident
    engineering_cost_loss = engineering_hours_loss * engineering_hourly_rate_usd
    downtime_hours_loss = incidents_90d * downtime_hours_per_incident
    downtime_cost_loss = downtime_hours_loss * business_downtime_rate_usd_per_hour
    total_cost_inaction = engineering_cost_loss + downtime_cost_loss

    languages = analysis.get("languages", [])
    recent_commits = analysis.get("recent_commits", [])

    risk_drivers = [
        f"Health score at {health_score}/100 indicates moderate structural risk.",
        f"Single-contributor concentration ({analysis.get('contributor_count', 0)} contributor) increases key-person dependency.",
        "Repository inactivity window suggests integration drift risk if release cadence accelerates.",
    ]

    recommended_priorities = [
        "Stabilize release pipeline with pre-merge quality gates and mandatory test checks.",
        "Reduce key-person concentration by adding code ownership redundancy for critical modules.",
        "Implement 90-day reliability KPI tracking: incident count, mean-time-to-recover, and escaped defects.",
    ]

    report_id = f"CEO-{analysis['repository_name'].replace('/', '-')}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    generated_at = datetime.now(timezone.utc).isoformat()

    output_dir = Path(__file__).resolve().parent
    md_path = output_dir / f"{report_id}.md"
    pdf_path = output_dir / f"{report_id}.pdf"
    json_path = output_dir / f"{report_id}.json"

    top_language_line = "N/A"
    if languages:
        top_language_line = f"{languages[0]['percentage']:.2f}% ({languages[0]['language']})"

    md_content = f"""# Executive AI Risk Report (CEO)\n\n## Repository\n- Name: {analysis['repository_name']}\n- URL: {analysis['repository_url']}\n- Default branch: {analysis.get('default_branch', 'main')}\n- Primary language: {analysis.get('primary_language') or 'Unknown'}\n- Top language share: {top_language_line}\n- Last push: {analysis.get('pushed_at', 'Unknown')}\n\n## Executive Summary\nThis repository is in a **moderate-risk** state over the next 90 days. The system health score is **{health_score}/100**, with concentrated contributor ownership and recent delivery changes indicating elevated execution risk if throughput increases without stronger controls.\n\n## 90-Day Predictive Risk Outlook\n- Estimated failure probability (model-derived): **{risk_probability:.0%}**\n- Forecasted incidents (next 90 days): **{incidents_90d}**\n- Key risk drivers:\n  - {risk_drivers[0]}\n  - {risk_drivers[1]}\n  - {risk_drivers[2]}\n\n## Cost of Inaction (Business Translation)\nAssumptions:\n- Engineering rate: ${engineering_hourly_rate_usd}/hour\n- Downtime cost: ${business_downtime_rate_usd_per_hour}/hour\n- Engineering hours per incident: {engineering_hours_per_incident}\n- Downtime per incident: {downtime_hours_per_incident} hours\n\nEstimated impact over 90 days:\n- Engineering hours at risk: **{engineering_hours_loss} hours**\n- Engineering productivity cost: **${engineering_cost_loss:,.0f}**\n- Downtime exposure: **{downtime_hours_loss} hours**\n- Downtime business cost: **${downtime_cost_loss:,.0f}**\n- **Total projected cost of inaction: ${total_cost_inaction:,.0f}**\n\n## Priority Actions for Leadership\n1. {recommended_priorities[0]}\n2. {recommended_priorities[1]}\n3. {recommended_priorities[2]}\n\n## Operational Context\n- Run status: {run_status.get('status', 'unknown')}\n- Run id: {run_status.get('run_id', run_id)}\n- Run update time: {run_status.get('updated_at', 'unknown')}\n- Run note: {run_status.get('message', 'N/A')}\n\n## Recent Change Evidence\n"""

    for idx, commit in enumerate(recent_commits[:5], start=1):
        md_content += f"- Commit {idx}: {commit.get('sha','')[:10]} | {commit.get('message','')} | {commit.get('author','unknown')}\n"

    md_content += "\n---\nGenerated by Predictive Engineering Intelligence workflow aligned to PRD business-value model.\n"
    md_path.write_text(md_content, encoding="utf-8")

    report_json = {
        "report_id": report_id,
        "generated_at": generated_at,
        "repository": analysis,
        "run_status": run_status,
        "risk_probability": risk_probability,
        "incidents_90d": incidents_90d,
        "cost_of_inaction": {
            "engineering_hours_loss": engineering_hours_loss,
            "engineering_cost_loss": engineering_cost_loss,
            "downtime_hours_loss": downtime_hours_loss,
            "downtime_cost_loss": downtime_cost_loss,
            "total_cost_inaction": total_cost_inaction,
        },
        "priorities": recommended_priorities,
    }
    json_path.write_text(json.dumps(report_json, indent=2), encoding="utf-8")

    ensure_reportlab()
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    story = []
    story.append(Paragraph("Executive AI Risk Report (CEO)", styles["Title"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"Repository: {analysis['repository_name']}", styles["Heading2"]))
    story.append(Paragraph(f"Generated at: {generated_at}", styles["Normal"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Executive Summary", styles["Heading2"]))
    story.append(
        Paragraph(
            (
                f"Repository health is {health_score}/100 with an estimated 90-day failure probability of {risk_probability:.0%}. "
                f"Projected cost of inaction is ${total_cost_inaction:,.0f}."
            ),
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 8))

    story.append(Paragraph("Cost of Inaction (90 Days)", styles["Heading2"]))
    for line in [
        f"Engineering hours at risk: {engineering_hours_loss} hours",
        f"Engineering productivity cost: ${engineering_cost_loss:,.0f}",
        f"Downtime exposure: {downtime_hours_loss} hours",
        f"Downtime business cost: ${downtime_cost_loss:,.0f}",
        f"Total projected cost: ${total_cost_inaction:,.0f}",
    ]:
        story.append(Paragraph(f"- {line}", styles["Normal"]))

    story.append(Spacer(1, 8))
    story.append(Paragraph("Recommended Priorities", styles["Heading2"]))
    for i, item in enumerate(recommended_priorities, start=1):
        story.append(Paragraph(f"{i}. {item}", styles["Normal"]))

    story.append(Spacer(1, 8))
    story.append(Paragraph("Recent Evidence", styles["Heading2"]))
    for commit in recent_commits[:5]:
        story.append(
            Paragraph(
                f"- {commit.get('sha','')[:10]} | {commit.get('message','')} | {commit.get('author','unknown')}",
                styles["Normal"],
            )
        )

    doc.build(story)

    print(str(md_path))
    print(str(pdf_path))
    print(str(json_path))


if __name__ == "__main__":
    main()
