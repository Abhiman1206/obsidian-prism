from __future__ import annotations

from io import BytesIO

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Response

from app.domain.business.repository import EXECUTIVE_REPORT_REPOSITORY

router = APIRouter(prefix="/api/executive-reports", tags=["executive-reports"])


@router.get("/{run_id}")
def get_executive_reports(run_id: str) -> list[dict]:
    return EXECUTIVE_REPORT_REPOSITORY.get_by_run(run_id)


@router.get("/{run_id}/{report_id}/pdf")
def get_executive_report_pdf(run_id: str, report_id: str) -> Response:
    reports = EXECUTIVE_REPORT_REPOSITORY.get_by_run(run_id)
    selected = next((report for report in reports if report.get("report_id") == report_id), None)
    if selected is None:
        raise HTTPException(status_code=404, detail="Report not found")

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import Paragraph
        from reportlab.platypus import SimpleDocTemplate
        from reportlab.platypus import Spacer
    except Exception as exc:
        raise HTTPException(status_code=500, detail="PDF generation dependency missing") from exc

    report_buffer = BytesIO()
    doc = SimpleDocTemplate(
        report_buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Executive AI Risk Report", styles["Title"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"Run ID: {selected.get('run_id', run_id)}", styles["Normal"]))
    story.append(Paragraph(f"Report ID: {selected.get('report_id', report_id)}", styles["Normal"]))
    story.append(Paragraph(f"Generated At: {selected.get('generated_at', 'unknown')}", styles["Normal"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Executive Summary", styles["Heading2"]))
    story.append(Paragraph(selected.get("executive_summary", "No summary available."), styles["Normal"]))
    story.append(Spacer(1, 10))

    total_cost = float(selected.get("cost_of_inaction_estimate", 0.0))
    story.append(Paragraph("Cost of Inaction", styles["Heading2"]))
    story.append(Paragraph(f"Projected 90-day cost: ${total_cost:,.2f}", styles["Normal"]))

    cost_section = selected.get("cost_of_inaction", {})
    if isinstance(cost_section, dict):
        summary = str(cost_section.get("summary", ""))
        if summary:
            story.append(Paragraph(summary, styles["Normal"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Top Risks", styles["Heading2"]))
    for risk in selected.get("top_risks", [])[:10]:
        component_id = str(risk.get("component_id", "unknown"))
        expected_total_cost = float(risk.get("expected_total_cost", 0.0))
        expected_engineering_hours = float(risk.get("expected_engineering_hours", 0.0))
        expected_downtime_hours = float(risk.get("expected_downtime_hours", 0.0))
        story.append(
            Paragraph(
                (
                    f"- {component_id}: ${expected_total_cost:,.2f} "
                    f"(engineering {expected_engineering_hours:.1f}h, downtime {expected_downtime_hours:.1f}h)"
                ),
                styles["Normal"],
            )
        )
    story.append(Spacer(1, 10))

    story.append(Paragraph("Recommended Priorities", styles["Heading2"]))
    for index, priority in enumerate(selected.get("recommended_priorities", [])[:10], start=1):
        action = str(priority.get("action", "No action provided"))
        component_id = str(priority.get("component_id", "unknown"))
        expected_total_cost = float(priority.get("expected_total_cost", 0.0))
        story.append(
            Paragraph(
                f"{index}. [{component_id}] {action} (impact ${expected_total_cost:,.2f})",
                styles["Normal"],
            )
        )

    doc.build(story)
    pdf_bytes = report_buffer.getvalue()
    filename = f"{report_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )
