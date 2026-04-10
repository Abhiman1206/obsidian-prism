"""Technical Engineer Report PDF — detailed code health and inactiveness analysis.

Designed for engineering teams, CTOs, and technical stakeholders who need
granular code health, component inactiveness, loss counts, complexity
breakdowns, and full data lineage provenance trails.
"""

from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------

def _health_color(score: float) -> colors.Color:
    """Return traffic-light color for a health score (0-100)."""
    if score < 50:
        return colors.Color(0.85, 0.20, 0.20, 0.15)  # red tint
    if score < 80:
        return colors.Color(0.95, 0.70, 0.10, 0.15)  # amber tint
    return colors.Color(0.20, 0.75, 0.30, 0.15)  # green tint


def _risk_color(probability: float) -> colors.Color:
    """Return traffic-light color for risk probability (0-1)."""
    if probability > 0.5:
        return colors.Color(0.85, 0.20, 0.20, 0.15)
    if probability > 0.25:
        return colors.Color(0.95, 0.70, 0.10, 0.15)
    return colors.Color(0.20, 0.75, 0.30, 0.15)


# ---------------------------------------------------------------------------
# Chart generation helpers (matplotlib -> PNG bytes)
# ---------------------------------------------------------------------------

def _make_health_bar_chart(health_rows: list[dict], max_items: int = 15) -> bytes | None:
    """Horizontal bar chart of health scores for worst components."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    sorted_rows = sorted(health_rows, key=lambda r: float(r.get("score", 100)))[:max_items]
    if not sorted_rows:
        return None

    labels = [r.get("component_id", "?").rsplit("/", 1)[-1] for r in sorted_rows]
    scores = [float(r.get("score", 0)) for r in sorted_rows]
    bar_colors = []
    for s in scores:
        if s < 50:
            bar_colors.append("#DC3545")
        elif s < 80:
            bar_colors.append("#FFC107")
        else:
            bar_colors.append("#28A745")

    fig, ax = plt.subplots(figsize=(7, max(3, len(labels) * 0.4)))
    ax.barh(labels, scores, color=bar_colors, edgecolor="#333", linewidth=0.5)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Health Score", fontsize=9)
    ax.set_title("Component Health Scores (Lowest First)", fontsize=11, fontweight="bold")
    ax.invert_yaxis()
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", labelsize=7)
    ax.tick_params(axis="x", labelsize=8)
    plt.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def _make_complexity_scatter(health_rows: list[dict]) -> bytes | None:
    """Scatter plot: Maintainability Index vs Cyclomatic Complexity."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    mi_vals = []
    cc_vals = []
    labels = []
    for r in health_rows:
        factors = r.get("factors", [])
        mi = next((f["raw_value"] for f in factors if f.get("name") == "maintainability"), None)
        cc = next((f["raw_value"] for f in factors if f.get("name") == "complexity"), None)
        if mi is not None and cc is not None:
            mi_vals.append(float(mi))
            cc_vals.append(float(cc))
            labels.append(r.get("component_id", "?").rsplit("/", 1)[-1])

    if not mi_vals:
        return None

    fig, ax = plt.subplots(figsize=(7, 4.5))
    scatter_colors = []
    for mi, cc in zip(mi_vals, cc_vals):
        if mi < 40 or cc > 20:
            scatter_colors.append("#DC3545")
        elif mi < 65 or cc > 10:
            scatter_colors.append("#FFC107")
        else:
            scatter_colors.append("#28A745")

    ax.scatter(mi_vals, cc_vals, c=scatter_colors, s=60, alpha=0.8, edgecolors="#333", linewidth=0.5)
    ax.set_xlabel("Maintainability Index", fontsize=9)
    ax.set_ylabel("Cyclomatic Complexity", fontsize=9)
    ax.set_title("Code Quality Map: Maintainability vs Complexity", fontsize=11, fontweight="bold")
    ax.axhline(y=10, color="#FFC107", linestyle="--", alpha=0.5, linewidth=0.8)
    ax.axvline(x=65, color="#FFC107", linestyle="--", alpha=0.5, linewidth=0.8)
    ax.text(15, 10.5, "DANGER ZONE", fontsize=7, color="#DC3545", alpha=0.7)
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Main PDF builder
# ---------------------------------------------------------------------------

def build_technical_pdf(
    run_id: str,
    repository_id: str,
    health_rows: list[dict],
    forecasts: list[dict],
    raw_commits: list[dict],
    cadence_signals: dict,
    lineage_records: list[dict],
    generated_at: str | None = None,
) -> bytes:
    """Build the Technical Engineer Report PDF and return raw bytes."""

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TechTitle", parent=styles["Title"], fontSize=18, textColor=colors.HexColor("#1a1a2e"))
    section_style = ParagraphStyle("Section", parent=styles["Heading2"], fontSize=13, textColor=colors.HexColor("#16213e"), spaceBefore=14, spaceAfter=6)
    subsection_style = ParagraphStyle("Subsection", parent=styles["Heading3"], fontSize=11, textColor=colors.HexColor("#0f3460"), spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle("TechBody", parent=styles["Normal"], fontSize=8.5, leading=12, textColor=colors.HexColor("#2d2d2d"))
    small_style = ParagraphStyle("Small", parent=styles["Normal"], fontSize=7.5, leading=10, textColor=colors.HexColor("#555555"))
    kpi_style = ParagraphStyle("KPI", parent=styles["Normal"], fontSize=20, leading=24, textColor=colors.HexColor("#0f3460"), alignment=1)
    kpi_label_style = ParagraphStyle("KPILabel", parent=styles["Normal"], fontSize=8, leading=10, textColor=colors.HexColor("#666"), alignment=1)

    story: list[Any] = []
    ts = generated_at or datetime.now(timezone.utc).isoformat()

    # ---- Title ----
    story.append(Paragraph("Technical Engineering Report", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Repository: <b>{repository_id}</b> &nbsp;|&nbsp; Run: <font size=7>{run_id}</font> &nbsp;|&nbsp; Generated: {ts[:19]}", small_style))
    story.append(Spacer(1, 12))

    # ---- KPI Summary Row ----
    total_components = len(health_rows)
    avg_health = round(sum(float(r.get("score", 0)) for r in health_rows) / max(total_components, 1), 1)
    total_commits = len(raw_commits)
    high_risk = sum(1 for f in forecasts if float(f.get("risk_probability", 0)) > 0.5)
    critical_health = sum(1 for r in health_rows if float(r.get("score", 0)) < 50)

    unique_authors: set[str] = set()
    for c in raw_commits:
        if isinstance(c, dict):
            email = c.get("author_email", "")
            if email:
                unique_authors.add(str(email))

    kpi_data = [
        [Paragraph(str(total_components), kpi_style), Paragraph(f"{avg_health}", kpi_style), Paragraph(str(total_commits), kpi_style), Paragraph(str(len(unique_authors)), kpi_style), Paragraph(str(high_risk), kpi_style), Paragraph(str(critical_health), kpi_style)],
        [Paragraph("Components", kpi_label_style), Paragraph("Avg Health", kpi_label_style), Paragraph("Commits", kpi_label_style), Paragraph("Contributors", kpi_label_style), Paragraph("High Risk", kpi_label_style), Paragraph("Critical", kpi_label_style)],
    ]
    kpi_table = Table(kpi_data, colWidths=[doc.width / 6] * 6)
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f4ff")),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f8f9fa")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e9ecef")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    # ---- Health Score Bar Chart ----
    story.append(Paragraph("1. Component Health Scores", section_style))
    chart_bytes = _make_health_bar_chart(health_rows)
    if chart_bytes:
        story.append(Image(BytesIO(chart_bytes), width=16 * cm, height=8 * cm))
        story.append(Spacer(1, 8))

    # ---- Complexity Scatter ----
    scatter_bytes = _make_complexity_scatter(health_rows)
    if scatter_bytes:
        story.append(Paragraph("Maintainability vs Complexity", subsection_style))
        story.append(Image(BytesIO(scatter_bytes), width=16 * cm, height=9 * cm))
        story.append(Spacer(1, 10))

    # ---- Full Health Table ----
    story.append(Paragraph("Detailed Health Breakdown", subsection_style))
    h_header = ["Component", "Score", "MI", "CC", "Volatility", "Contributors"]
    h_data = [h_header]
    sorted_health = sorted(health_rows, key=lambda r: float(r.get("score", 100)))
    for r in sorted_health:
        factors = {f["name"]: f for f in r.get("factors", [])}
        mi_raw = factors.get("maintainability", {}).get("raw_value", "-")
        cc_raw = factors.get("complexity", {}).get("raw_value", "-")
        vol_raw = factors.get("volatility", {}).get("raw_value", "-")
        contribs = [c for c in r.get("contributors", []) if "@" in str(c)]
        contrib_str = ", ".join(contribs[:3]) if contribs else "-"
        cid = str(r.get("component_id", ""))
        if len(cid) > 45:
            cid = "..." + cid[-42:]
        h_data.append([cid, f"{float(r.get('score', 0)):.1f}", f"{mi_raw}", f"{cc_raw}", f"{vol_raw}", contrib_str])

    col_widths = [6.5 * cm, 1.5 * cm, 1.5 * cm, 1.3 * cm, 1.8 * cm, 4.5 * cm]
    health_table = Table(h_data, colWidths=col_widths, repeatRows=1)
    table_style_cmds: list[Any] = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("FONTSIZE", (0, 1), (-1, -1), 7),
        ("LEADING", (0, 0), (-1, -1), 10),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#adb5bd")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dee2e6")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]
    for row_idx in range(1, len(h_data)):
        score_val = float(sorted_health[row_idx - 1].get("score", 100))
        table_style_cmds.append(("BACKGROUND", (0, row_idx), (-1, row_idx), _health_color(score_val)))
    health_table.setStyle(TableStyle(table_style_cmds))
    story.append(health_table)
    story.append(Spacer(1, 14))

    # ---- Repository Activity / Inactiveness ----
    story.append(Paragraph("2. Repository Activity & Inactiveness", section_style))

    issue_opened = int(cadence_signals.get("issue_opened_count", 0)) if isinstance(cadence_signals, dict) else 0
    issue_closed = int(cadence_signals.get("issue_closed_count", 0)) if isinstance(cadence_signals, dict) else 0
    deploy_count = int(cadence_signals.get("deployment_count", 0)) if isinstance(cadence_signals, dict) else 0
    net_issues = issue_opened - issue_closed

    activity_data = [
        ["Metric", "Value", "Assessment"],
        ["Total Commits Analyzed", str(total_commits), "OK" if total_commits > 10 else "LOW"],
        ["Unique Contributors", str(len(unique_authors)), "OK" if len(unique_authors) > 1 else "SINGLE AUTHOR"],
        ["Open Issues", str(issue_opened), "HIGH" if issue_opened > 20 else "OK"],
        ["Closed Issues", str(issue_closed), "GOOD" if issue_closed > issue_opened * 0.5 else "BACKLOG GROWING"],
        ["Net Unresolved Issues", str(max(net_issues, 0)), "RISK" if net_issues > 10 else "OK"],
        ["Deployments Detected", str(deploy_count), "ACTIVE" if deploy_count > 0 else "NONE DETECTED"],
    ]
    act_table = Table(activity_data, colWidths=[6 * cm, 3 * cm, 6 * cm], repeatRows=1)
    act_style_cmds: list = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16213e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#adb5bd")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dee2e6")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for row_idx in range(1, len(activity_data)):
        assessment = activity_data[row_idx][2]
        if assessment in ("HIGH", "RISK", "BACKLOG GROWING", "LOW", "SINGLE AUTHOR", "NONE DETECTED"):
            act_style_cmds.append(("BACKGROUND", (2, row_idx), (2, row_idx), colors.Color(0.85, 0.20, 0.20, 0.12)))
        elif assessment in ("GOOD", "ACTIVE"):
            act_style_cmds.append(("BACKGROUND", (2, row_idx), (2, row_idx), colors.Color(0.20, 0.75, 0.30, 0.12)))
    act_table.setStyle(TableStyle(act_style_cmds))
    story.append(act_table)
    story.append(Spacer(1, 14))

    # ---- Risk Forecast Table ----
    story.append(Paragraph("3. 90-Day Risk Forecasts", section_style))
    sorted_forecasts = sorted(forecasts, key=lambda f: -float(f.get("risk_probability", 0)))

    r_header = ["Component", "Risk %", "Confidence", "Top Signal", "Strength"]
    r_data = [r_header]
    for f in sorted_forecasts[:20]:
        top_sig = f.get("top_signals", [{}])[0] if f.get("top_signals") else {}
        cid = str(f.get("component_id", ""))
        if len(cid) > 45:
            cid = "..." + cid[-42:]
        r_data.append([
            cid,
            f"{float(f.get('risk_probability', 0)) * 100:.1f}%",
            f"{float(f.get('confidence', 0)):.2f}",
            str(top_sig.get("signal_name", "-")),
            f"{float(top_sig.get('contribution_strength', 0)):.4f}",
        ])

    risk_table = Table(r_data, colWidths=[6.5 * cm, 1.5 * cm, 2 * cm, 3.5 * cm, 2 * cm], repeatRows=1)
    risk_style: list = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("FONTSIZE", (0, 1), (-1, -1), 7),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#adb5bd")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dee2e6")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    for row_idx, f in enumerate(sorted_forecasts[:20], start=1):
        risk_style.append(("BACKGROUND", (0, row_idx), (-1, row_idx), _risk_color(float(f.get("risk_probability", 0)))))
    risk_table.setStyle(TableStyle(risk_style))
    story.append(risk_table)
    story.append(Spacer(1, 14))

    # ---- Lineage Provenance ----
    story.append(Paragraph("4. Data Lineage & Provenance Trail", section_style))
    story.append(Paragraph(
        "Every metric in this report traces back to a specific tool invocation. "
        "The following records show the complete provenance chain for this analysis run.",
        body_style,
    ))
    story.append(Spacer(1, 6))

    if lineage_records:
        lin_header = ["Type", "Tool / Artifact", "Provider", "Timestamp"]
        lin_data = [lin_header]
        for rec in lineage_records:
            if isinstance(rec, dict):
                lin_data.append([
                    str(rec.get("artifact_type", "")),
                    str(rec.get("source_locator", rec.get("artifact_id", ""))),
                    str(rec.get("source_provider", "")),
                    str(rec.get("created_at", ""))[:19],
                ])
        lin_table = Table(lin_data, colWidths=[2.5 * cm, 7 * cm, 2.5 * cm, 4 * cm], repeatRows=1)
        lin_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3460")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#adb5bd")),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dee2e6")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(lin_table)
    else:
        story.append(Paragraph("No lineage records available for this run.", small_style))

    story.append(Spacer(1, 20))
    story.append(Paragraph(
        f"<i>End of Technical Report  |  Generated by Predictive Engineering Intelligence  |  {ts[:19]}</i>",
        small_style,
    ))

    doc.build(story)
    return buf.getvalue()
