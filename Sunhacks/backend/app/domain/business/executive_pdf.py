"""Executive KPI Report PDF — CEO/CTO business impact with charts and infographics.

Designed for non-technical executives. Translates technical risk data into
business KPIs, cost-of-inaction estimates, and actionable priorities.
Features matplotlib-generated pie charts, bar charts, histograms, and
waterfall visualizations embedded directly into the PDF.
"""

from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ---------------------------------------------------------------------------
# Chart Builders (matplotlib -> PNG bytes in-memory)
# ---------------------------------------------------------------------------

def _make_risk_pie_chart(forecasts: list[dict]) -> bytes | None:
    """Pie chart: high / medium / low risk distribution."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    high = sum(1 for f in forecasts if float(f.get("risk_probability", 0)) > 0.5)
    medium = sum(1 for f in forecasts if 0.25 < float(f.get("risk_probability", 0)) <= 0.5)
    low = sum(1 for f in forecasts if float(f.get("risk_probability", 0)) <= 0.25)

    if high + medium + low == 0:
        return None

    sizes = [high, medium, low]
    labels_with_count = [f"High Risk ({high})", f"Medium Risk ({medium})", f"Low Risk ({low})"]
    chart_colors = ["#DC3545", "#FFC107", "#28A745"]

    # Remove zero-count slices
    filtered = [(s, l, c) for s, l, c in zip(sizes, labels_with_count, chart_colors) if s > 0]
    if not filtered:
        return None
    sizes, labels_with_count, chart_colors = zip(*filtered)

    fig, ax = plt.subplots(figsize=(5, 4))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels_with_count, colors=chart_colors,
        autopct="%1.0f%%", startangle=90, pctdistance=0.75,
        wedgeprops={"linewidth": 1.5, "edgecolor": "white"},
    )
    for t in texts:
        t.set_fontsize(9)
    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight("bold")
        at.set_color("white")
    ax.set_title("Component Risk Distribution", fontsize=12, fontweight="bold", pad=15)

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def _make_cost_bar_chart(translated: list[dict], max_items: int = 10) -> bytes | None:
    """Horizontal bar chart: top N components by projected cost."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    top = sorted(translated, key=lambda r: -float(r.get("expected_total_cost", 0)))[:max_items]
    if not top:
        return None

    labels = [r.get("component_id", "?").rsplit("/", 1)[-1] for r in reversed(top)]
    eng_costs = [float(r.get("expected_engineering_hours", 0)) * 140.0 for r in reversed(top)]
    downtime_costs = [float(r.get("expected_downtime_hours", 0)) * 1800.0 for r in reversed(top)]

    fig, ax = plt.subplots(figsize=(7, max(3.5, len(labels) * 0.45)))
    y_pos = range(len(labels))

    ax.barh(y_pos, eng_costs, color="#4A90D9", label="Engineering Cost", edgecolor="#333", linewidth=0.3, height=0.6)
    ax.barh(y_pos, downtime_costs, left=eng_costs, color="#E74C3C", label="Downtime Cost", edgecolor="#333", linewidth=0.3, height=0.6)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=7.5)
    ax.set_xlabel("Projected Cost ($)", fontsize=9)
    ax.set_title("Top Components by Cost Exposure", fontsize=12, fontweight="bold")
    ax.legend(fontsize=8, loc="lower right")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def _make_health_histogram(health_rows: list[dict]) -> bytes | None:
    """Histogram of health score distribution."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        return None

    scores = [float(r.get("score", 0)) for r in health_rows]
    if not scores:
        return None

    fig, ax = plt.subplots(figsize=(6, 3.5))
    bins = [0, 20, 40, 50, 60, 70, 80, 90, 100]
    n, bin_edges, patches = ax.hist(scores, bins=bins, edgecolor="#333", linewidth=0.5)

    for patch, left_edge in zip(patches, bin_edges[:-1]):
        if left_edge < 50:
            patch.set_facecolor("#DC3545")
        elif left_edge < 80:
            patch.set_facecolor("#FFC107")
        else:
            patch.set_facecolor("#28A745")

    ax.set_xlabel("Health Score", fontsize=9)
    ax.set_ylabel("Number of Components", fontsize=9)
    ax.set_title("Health Score Distribution", fontsize=12, fontweight="bold")
    legend_handles = [
        mpatches.Patch(color="#DC3545", label="Critical (<50)"),
        mpatches.Patch(color="#FFC107", label="Warning (50-80)"),
        mpatches.Patch(color="#28A745", label="Healthy (>80)"),
    ]
    ax.legend(handles=legend_handles, fontsize=7.5, loc="upper left")
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def _make_signal_breakdown_chart(forecasts: list[dict], max_items: int = 8) -> bytes | None:
    """Stacked bar chart showing signal contribution breakdown for top risk components."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        return None

    top = sorted(forecasts, key=lambda f: -float(f.get("risk_probability", 0)))[:max_items]
    if not top:
        return None

    labels = [r.get("component_id", "?").rsplit("/", 1)[-1] for r in top]
    signal_names = ["health_risk", "contributor_churn", "defect_signal", "deployment_instability"]
    signal_colors = {"health_risk": "#E74C3C", "contributor_churn": "#F39C12", "defect_signal": "#9B59B6", "deployment_instability": "#3498DB"}

    signal_data: dict[str, list[float]] = {s: [] for s in signal_names}
    for f in top:
        sig_map = {s.get("signal_name", ""): float(s.get("contribution_strength", 0)) for s in f.get("top_signals", [])}
        for sn in signal_names:
            signal_data[sn].append(sig_map.get(sn, 0.0))

    fig, ax = plt.subplots(figsize=(7, max(3, len(labels) * 0.45)))
    y_pos = np.arange(len(labels))
    left = np.zeros(len(labels))

    for sn in signal_names:
        vals = np.array(signal_data[sn])
        ax.barh(y_pos, vals, left=left, color=signal_colors[sn], label=sn.replace("_", " ").title(), edgecolor="#333", linewidth=0.3, height=0.6)
        left += vals

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=7.5)
    ax.set_xlabel("Signal Contribution", fontsize=9)
    ax.set_title("Risk Signal Breakdown by Component", fontsize=12, fontweight="bold")
    ax.legend(fontsize=7, loc="lower right")
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

def build_executive_pdf(
    run_id: str,
    repository_id: str,
    report: dict,
    health_rows: list[dict],
    forecasts: list[dict],
    translated: list[dict],
    generated_at: str | None = None,
) -> bytes:
    """Build the Executive KPI Report PDF and return raw bytes."""

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
    title_style = ParagraphStyle("ExecTitle", parent=styles["Title"], fontSize=20, textColor=colors.HexColor("#1a1a2e"))
    subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=10, textColor=colors.HexColor("#6c757d"), alignment=1, spaceAfter=12)
    section_style = ParagraphStyle("Section", parent=styles["Heading2"], fontSize=14, textColor=colors.HexColor("#16213e"), spaceBefore=16, spaceAfter=8)
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=9, leading=13, textColor=colors.HexColor("#2d2d2d"), spaceAfter=6)
    small_style = ParagraphStyle("Small", parent=styles["Normal"], fontSize=7.5, leading=10, textColor=colors.HexColor("#666"))
    kpi_value_style = ParagraphStyle("KPIValue", parent=styles["Normal"], fontSize=22, leading=26, textColor=colors.HexColor("#0f3460"), alignment=1)
    kpi_label_style = ParagraphStyle("KPILabel", parent=styles["Normal"], fontSize=8, leading=10, textColor=colors.HexColor("#888"), alignment=1)
    callout_style = ParagraphStyle("Callout", parent=styles["Normal"], fontSize=10, leading=14, textColor=colors.HexColor("#1a1a2e"), backColor=colors.HexColor("#f0f4ff"), borderPadding=8, spaceAfter=10)

    story: list[Any] = []
    ts = generated_at or datetime.now(timezone.utc).isoformat()

    total_cost = float(report.get("cost_of_inaction_estimate", 0.0))
    total_components = len(health_rows)
    avg_health = round(sum(float(r.get("score", 0)) for r in health_rows) / max(total_components, 1), 1)
    high_risk = sum(1 for f in forecasts if float(f.get("risk_probability", 0)) > 0.5)
    critical_health = sum(1 for r in health_rows if float(r.get("score", 0)) < 50)

    # ---- Title ----
    story.append(Paragraph("Executive Risk Intelligence Report", title_style))
    story.append(Paragraph(f"{repository_id}  |  90-Day Forecast  |  {ts[:10]}", subtitle_style))

    # ---- KPI Dashboard ----
    story.append(Paragraph("Key Performance Indicators", section_style))

    kpi_data = [
        [
            Paragraph(f"${total_cost:,.0f}", kpi_value_style),
            Paragraph(f"{total_components}", kpi_value_style),
            Paragraph(f"{avg_health}/100", kpi_value_style),
            Paragraph(f"{high_risk}", kpi_value_style),
        ],
        [
            Paragraph("Cost of Inaction (90-day)", kpi_label_style),
            Paragraph("Components Analyzed", kpi_label_style),
            Paragraph("Avg Health Score", kpi_label_style),
            Paragraph("High Risk Components", kpi_label_style),
        ],
    ]

    kpi_table = Table(kpi_data, colWidths=[doc.width / 4] * 4)
    kpi_bg_colors = [
        colors.HexColor("#fff3f3") if total_cost > 100000 else colors.HexColor("#f0fff0"),
        colors.HexColor("#f0f4ff"),
        colors.HexColor("#fff8e1") if avg_health < 70 else colors.HexColor("#f0fff0"),
        colors.HexColor("#fff3f3") if high_risk > 0 else colors.HexColor("#f0fff0"),
    ]
    kpi_style_cmds: list = [
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#dee2e6")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e9ecef")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]
    for col_idx, bg in enumerate(kpi_bg_colors):
        kpi_style_cmds.append(("BACKGROUND", (col_idx, 0), (col_idx, 0), bg))
        kpi_style_cmds.append(("BACKGROUND", (col_idx, 1), (col_idx, 1), colors.HexColor("#fafbfc")))
    kpi_table.setStyle(TableStyle(kpi_style_cmds))
    story.append(kpi_table)
    story.append(Spacer(1, 12))

    # ---- Executive Summary ----
    story.append(Paragraph("Executive Summary", section_style))
    summary_text = str(report.get("executive_summary", "No summary available."))
    story.append(Paragraph(summary_text, callout_style))

    # ---- Risk Distribution Pie Chart ----
    story.append(Paragraph("Risk Distribution", section_style))
    pie_bytes = _make_risk_pie_chart(forecasts)
    if pie_bytes:
        story.append(Image(BytesIO(pie_bytes), width=12 * cm, height=9.5 * cm))
        story.append(Spacer(1, 8))

    # ---- Cost Exposure Bar Chart ----
    story.append(Paragraph("Cost Exposure by Component", section_style))
    story.append(Paragraph(
        "The chart below shows the projected financial impact per component, "
        "split between engineering remediation cost (developer time) and "
        "potential downtime revenue loss.",
        body_style,
    ))
    cost_bytes = _make_cost_bar_chart(translated)
    if cost_bytes:
        story.append(Image(BytesIO(cost_bytes), width=16 * cm, height=8 * cm))
        story.append(Spacer(1, 10))

    # ---- Health Score Histogram ----
    story.append(Paragraph("Portfolio Health Distribution", section_style))
    hist_bytes = _make_health_histogram(health_rows)
    if hist_bytes:
        story.append(Image(BytesIO(hist_bytes), width=14 * cm, height=8 * cm))
        story.append(Spacer(1, 10))

    # ---- Signal Breakdown Stacked Bar ----
    story.append(Paragraph("What's Driving the Risk?", section_style))
    story.append(Paragraph(
        "Each component's risk probability is composed of four measurable signals. "
        "This breakdown shows which factors contribute most to each component's risk score.",
        body_style,
    ))
    sig_bytes = _make_signal_breakdown_chart(forecasts)
    if sig_bytes:
        story.append(Image(BytesIO(sig_bytes), width=16 * cm, height=7.5 * cm))
        story.append(Spacer(1, 10))

    # ---- Business Impact Table ----
    story.append(Paragraph("Business Impact Breakdown", section_style))
    bi_header = ["Component", "Eng. Hours", "Downtime Hours", "Projected Cost", "Primary Driver"]
    bi_data = [bi_header]
    for t in translated[:15]:
        cid = str(t.get("component_id", ""))
        if len(cid) > 40:
            cid = "..." + cid[-37:]
        drivers = t.get("cost_drivers", [])
        primary = str(drivers[0]).replace("_", " ").title() if drivers else "-"
        bi_data.append([
            cid,
            f"{float(t.get('expected_engineering_hours', 0)):.1f}h",
            f"{float(t.get('expected_downtime_hours', 0)):.1f}h",
            f"${float(t.get('expected_total_cost', 0)):,.2f}",
            primary,
        ])

    bi_table = Table(bi_data, colWidths=[5.5 * cm, 2.3 * cm, 2.6 * cm, 3 * cm, 3.2 * cm], repeatRows=1)
    bi_style_cmds: list = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("FONTSIZE", (0, 1), (-1, -1), 7.5),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#adb5bd")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dee2e6")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (1, 1), (3, -1), "RIGHT"),
    ]
    for row_idx in range(1, len(bi_data)):
        alt_bg = colors.HexColor("#f8f9fa") if row_idx % 2 == 0 else colors.white
        bi_style_cmds.append(("BACKGROUND", (0, row_idx), (-1, row_idx), alt_bg))
    bi_table.setStyle(TableStyle(bi_style_cmds))
    story.append(bi_table)
    story.append(Spacer(1, 14))

    # ---- Recommended Priorities ----
    story.append(Paragraph("Recommended Priorities", section_style))
    story.append(Paragraph(
        "Based on the analysis, the following components should be prioritized "
        "for remediation to maximize risk reduction per dollar invested:",
        body_style,
    ))
    priorities = report.get("recommended_priorities", [])[:10]
    for idx, p in enumerate(priorities, 1):
        cid = str(p.get("component_id", "?"))
        cost = float(p.get("expected_total_cost", 0))
        action = str(p.get("action", "Reduce failure exposure"))
        story.append(Paragraph(
            f"<b>{idx}.</b> <b>{cid.rsplit('/', 1)[-1]}</b> "
            f"&mdash; {action} &nbsp; "
            f"<font color='#DC3545'><b>(${cost:,.2f} exposure)</b></font>",
            body_style,
        ))
    story.append(Spacer(1, 14))

    # ---- Cost Assumptions ----
    story.append(Paragraph("Methodology & Assumptions", section_style))
    assumptions_data = [
        ["Parameter", "Value", "Description"],
        ["Engineering Rate", "$140/hr", "Fully-loaded cost of engineer remediation time"],
        ["Downtime Cost", "$1,800/hr", "Estimated revenue loss during service disruption"],
        ["Eng. Hours Multiplier", "36 hours", "Expected engineering effort per failure event"],
        ["Downtime Multiplier", "10 hours", "Expected downtime duration per failure event"],
        ["Forecast Horizon", "90 days", "Predictive window for component failure risk"],
    ]
    assump_table = Table(assumptions_data, colWidths=[4 * cm, 3 * cm, 9.5 * cm], repeatRows=1)
    assump_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16213e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#adb5bd")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dee2e6")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fafbfc")),
    ]))
    story.append(assump_table)
    story.append(Spacer(1, 20))

    # ---- Footer ----
    story.append(Paragraph(
        f"<i>This report was generated by the Predictive Engineering Intelligence platform. "
        f"All claims are evidence-linked and traceable through the lineage system. "
        f"Report ID: {report.get('report_id', 'N/A')} | {ts[:19]}</i>",
        small_style,
    ))

    doc.build(story)
    return buf.getvalue()
