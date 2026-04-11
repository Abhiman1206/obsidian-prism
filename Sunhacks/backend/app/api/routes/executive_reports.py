from __future__ import annotations

from io import BytesIO

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Response

from app.domain.business.repository import EXECUTIVE_REPORT_REPOSITORY

router = APIRouter(prefix="/api/executive-reports", tags=["executive-reports"])


@router.get("/latest")
def get_latest_executive_report() -> dict | None:
    return EXECUTIVE_REPORT_REPOSITORY.get_latest()


@router.get("/{run_id}")
def get_executive_reports(run_id: str) -> list[dict]:
    return EXECUTIVE_REPORT_REPOSITORY.get_by_run(run_id)


# ---------------------------------------------------------------------------
# Technical Engineer PDF
# ---------------------------------------------------------------------------

@router.get("/{run_id}/{report_id}/technical-pdf")
def get_technical_pdf(run_id: str, report_id: str) -> Response:
    """Download the Technical Engineer Report PDF."""
    reports = EXECUTIVE_REPORT_REPOSITORY.get_by_run(run_id)
    selected = next((r for r in reports if r.get("report_id") == report_id), None)
    if selected is None:
        raise HTTPException(status_code=404, detail="Report not found")

    technical_data = selected.get("technical_report")
    if not technical_data or not isinstance(technical_data, dict):
        raise HTTPException(status_code=404, detail="Technical report data not found for this run")

    try:
        from app.domain.business.technical_pdf import build_technical_pdf
    except ImportError as exc:
        raise HTTPException(status_code=500, detail="Technical PDF generator unavailable") from exc

    # Gather lineage records for this run
    lineage_records: list[dict] = []
    try:
        from app.domain.evidence.repository import LineageRepository
        repo = LineageRepository()
        records = repo.get_lineage(run_id=run_id)
        lineage_records = [r.model_dump() if hasattr(r, "model_dump") else dict(r) for r in records]
    except Exception:
        pass  # Lineage is optional for the PDF

    pdf_bytes = build_technical_pdf(
        run_id=run_id,
        repository_id=technical_data.get("repository_id", run_id),
        health_rows=technical_data.get("health_rows", []),
        forecasts=technical_data.get("forecasts", []),
        raw_commits=[{}] * technical_data.get("raw_commits_count", 0),  # We store count, not full data
        cadence_signals=technical_data.get("cadence_signals", {}),
        lineage_records=lineage_records,
        generated_at=technical_data.get("generated_at"),
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="technical-{report_id}.pdf"'},
    )


# ---------------------------------------------------------------------------
# Executive KPI PDF (with charts, tables, infographics)
# ---------------------------------------------------------------------------

@router.get("/{run_id}/{report_id}/executive-pdf")
def get_executive_pdf(run_id: str, report_id: str) -> Response:
    """Download the Executive KPI Report PDF with charts and infographics."""
    reports = EXECUTIVE_REPORT_REPOSITORY.get_by_run(run_id)
    selected = next((r for r in reports if r.get("report_id") == report_id), None)
    if selected is None:
        raise HTTPException(status_code=404, detail="Report not found")

    try:
        from app.domain.business.executive_pdf import build_executive_pdf
    except ImportError as exc:
        raise HTTPException(status_code=500, detail="Executive PDF generator unavailable") from exc

    # Reconstruct translated rows from top_risks
    translated: list[dict] = []
    for risk in selected.get("top_risks", []):
        translated.append({
            "component_id": risk.get("component_id", ""),
            "expected_engineering_hours": float(risk.get("expected_engineering_hours", 0)),
            "expected_downtime_hours": float(risk.get("expected_downtime_hours", 0)),
            "expected_total_cost": float(risk.get("expected_total_cost", 0)),
            "cost_drivers": risk.get("cost_drivers", ["downtime_exposure", "engineering_effort"]),
        })

    # Get health rows and forecasts from the technical report data if available
    technical_data = selected.get("technical_report", {})
    health_rows = technical_data.get("health_rows", []) if isinstance(technical_data, dict) else []
    forecasts = technical_data.get("forecasts", []) if isinstance(technical_data, dict) else []

    pdf_bytes = build_executive_pdf(
        run_id=run_id,
        repository_id=technical_data.get("repository_id", run_id) if isinstance(technical_data, dict) else run_id,
        report=selected,
        health_rows=health_rows,
        forecasts=forecasts,
        translated=translated,
        generated_at=selected.get("generated_at"),
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="executive-{report_id}.pdf"'},
    )


# ---------------------------------------------------------------------------
# Legacy PDF endpoint (backward compatible)
# ---------------------------------------------------------------------------

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
