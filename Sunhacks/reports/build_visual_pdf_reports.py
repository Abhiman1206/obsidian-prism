from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
import json

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing, String


def _latest_file(pattern: str, folder: Path) -> Path:
    matches = sorted(folder.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not matches:
        raise FileNotFoundError(f"No files found for pattern: {pattern}")
    return matches[0]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _title(canvas: Canvas, title: str, subtitle: str) -> None:
    canvas.setFont("Helvetica-Bold", 18)
    canvas.drawString(2 * cm, 27.5 * cm, title)
    canvas.setFont("Helvetica", 10)
    canvas.setFillColor(colors.HexColor("#4B5563"))
    canvas.drawString(2 * cm, 26.9 * cm, subtitle)
    canvas.setFillColor(colors.black)


def _kpi_box(canvas: Canvas, x: float, y: float, w: float, h: float, label: str, value: str) -> None:
    canvas.setStrokeColor(colors.HexColor("#D1D5DB"))
    canvas.setFillColor(colors.HexColor("#F9FAFB"))
    canvas.roundRect(x, y, w, h, 6, stroke=1, fill=1)
    canvas.setFillColor(colors.HexColor("#6B7280"))
    canvas.setFont("Helvetica", 9)
    canvas.drawString(x + 8, y + h - 16, label)
    canvas.setFillColor(colors.HexColor("#111827"))
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(x + 8, y + 10, value)
    canvas.setFillColor(colors.black)


def _draw_executive_pdf(out_path: Path, report: dict) -> None:
    repo = report["repository"]
    cost = report["cost_of_inaction"]
    risk_probability = report["risk_probability"]
    incidents = report["incidents_90d"]

    c = Canvas(str(out_path), pagesize=A4)
    _title(
        c,
        "Executive KPI Report (Visual)",
        f"Repo: {repo.get('repository_name', 'N/A')} | Generated: {datetime.now(tz=UTC).isoformat()}",
    )

    # KPI cards
    _kpi_box(c, 2 * cm, 23.3 * cm, 5.6 * cm, 2.8 * cm, "Health Score", f"{repo.get('health', {}).get('score', 0)}/100")
    _kpi_box(c, 8 * cm, 23.3 * cm, 5.6 * cm, 2.8 * cm, "Risk Probability", f"{risk_probability * 100:.0f}%")
    _kpi_box(c, 14 * cm, 23.3 * cm, 5.6 * cm, 2.8 * cm, "Projected Incidents", f"{incidents}")

    # Pie chart for risk probability
    pie_d = Drawing(250, 180)
    pie = Pie()
    pie.x = 20
    pie.y = 25
    pie.width = 140
    pie.height = 140
    pie.data = [round(risk_probability * 100, 2), round((1 - risk_probability) * 100, 2)]
    pie.labels = ["Risk", "Stability"]
    pie.slices[0].fillColor = colors.HexColor("#EF4444")
    pie.slices[1].fillColor = colors.HexColor("#10B981")
    pie_d.add(pie)
    pie_d.add(String(10, 170, "90-Day Risk Profile", fontSize=11))
    pie_d.drawOn(c, 2 * cm, 15 * cm)

    # Bar chart for cost breakdown
    bar_d = Drawing(300, 180)
    bc = VerticalBarChart()
    bc.x = 40
    bc.y = 35
    bc.height = 120
    bc.width = 230
    bc.data = [[
        cost.get("engineering_cost_loss", 0),
        cost.get("downtime_cost_loss", 0),
        cost.get("total_cost_inaction", 0),
    ]]
    bc.categoryAxis.categoryNames = ["Eng Cost", "Downtime", "Total"]
    bc.valueAxis.valueMin = 0
    bc.bars[0].fillColor = colors.HexColor("#3B82F6")
    bar_d.add(bc)
    bar_d.add(String(10, 170, "Cost of Inaction (USD)", fontSize=11))
    bar_d.drawOn(c, 10.5 * cm, 15 * cm)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, 14 * cm, "Priority Actions")
    c.setFont("Helvetica", 10)
    y = 13.4 * cm
    for i, item in enumerate(report.get("priorities", []), start=1):
        c.drawString(2.2 * cm, y, f"{i}. {item}")
        y -= 0.6 * cm

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#6B7280"))
    c.drawString(2 * cm, 1.5 * cm, "Generated from latest CEO JSON report.")
    c.save()


def _draw_technical_pdf(out_path: Path, report: dict) -> None:
    activity = report["activity"]
    flags = report["flags"]
    codebase = report["codebase"]
    repo = report["repository"]

    c = Canvas(str(out_path), pagesize=A4)
    _title(
        c,
        "Technical KPI Report (Visual)",
        f"Repo: {repo.get('origin', 'N/A')} | Branch: {repo.get('branch', 'N/A')}",
    )

    _kpi_box(c, 2 * cm, 23.3 * cm, 4.4 * cm, 2.8 * cm, "Commits (90d)", str(activity.get("commit_count", 0)))
    _kpi_box(c, 6.8 * cm, 23.3 * cm, 4.4 * cm, 2.8 * cm, "Active Days", str(activity.get("active_day_count", 0)))
    _kpi_box(c, 11.6 * cm, 23.3 * cm, 4.4 * cm, 2.8 * cm, "Inactive Days", str(activity.get("inactive_day_count", 0)))
    _kpi_box(c, 16.4 * cm, 23.3 * cm, 3.6 * cm, 2.8 * cm, "Flags", str(flags.get("total_flag_count", 0)))

    # Activity distribution chart
    act_d = Drawing(280, 190)
    act_bc = VerticalBarChart()
    act_bc.x = 45
    act_bc.y = 35
    act_bc.height = 130
    act_bc.width = 210
    act_bc.data = [[activity.get("active_day_count", 0), activity.get("inactive_day_count", 0)]]
    act_bc.categoryAxis.categoryNames = ["Active", "Inactive"]
    act_bc.valueAxis.valueMin = 0
    act_bc.bars[0].fillColor = colors.HexColor("#6366F1")
    act_d.add(act_bc)
    act_d.add(String(10, 174, "Activity Distribution (90 days)", fontSize=11))
    act_d.drawOn(c, 2 * cm, 15 * cm)

    # Flag breakdown chart
    f = flags.get("flag_breakdown", {})
    flag_d = Drawing(320, 190)
    flag_bc = VerticalBarChart()
    flag_bc.x = 40
    flag_bc.y = 35
    flag_bc.height = 130
    flag_bc.width = 250
    flag_bc.data = [[
        f.get("inactive_day_flags", 0),
        f.get("low_activity_week_flags", 0),
        f.get("stale_file_flags", 0),
        f.get("single_contributor_risk_flag", 0),
    ]]
    flag_bc.categoryAxis.categoryNames = ["Inactive", "LowWk", "Stale", "1-Owner"]
    flag_bc.valueAxis.valueMin = 0
    flag_bc.bars[0].fillColor = colors.HexColor("#F59E0B")
    flag_d.add(flag_bc)
    flag_d.add(String(10, 174, "Risk Flag Breakdown", fontSize=11))
    flag_d.drawOn(c, 9.2 * cm, 15 * cm)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, 14 * cm, "Codebase KPI Snapshot")
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, 13.3 * cm, f"Tracked files: {codebase.get('tracked_file_count', 0)}")
    c.drawString(2 * cm, 12.7 * cm, f"Touched files in window: {codebase.get('files_touched_in_window', 0)}")
    c.drawString(2 * cm, 12.1 * cm, f"Stale files: {codebase.get('stale_file_count', 0)}")
    c.drawString(2 * cm, 11.5 * cm, f"Contributors: {activity.get('contributor_count', 0)}")
    c.drawString(2 * cm, 10.9 * cm, f"Activeness ratio: {activity.get('activeness_ratio', 0)}%")

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#6B7280"))
    c.drawString(2 * cm, 1.5 * cm, "Generated from latest technical JSON report.")
    c.save()


def main() -> None:
    out_dir = Path(__file__).resolve().parent

    ceo_json = _latest_file("CEO-Abhiman1206-AI_APP-*.json", out_dir)
    tech_json = _latest_file("TECH-ACTIVITY-AI_APP-*.json", out_dir)

    ceo = _load_json(ceo_json)
    tech = _load_json(tech_json)

    stamp = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S")
    ceo_pdf = out_dir / f"CEO-AI_APP-VISUAL-{stamp}.pdf"
    tech_pdf = out_dir / f"TECH-AI_APP-VISUAL-{stamp}.pdf"

    _draw_executive_pdf(ceo_pdf, ceo)
    _draw_technical_pdf(tech_pdf, tech)

    print(str(ceo_pdf))
    print(str(tech_pdf))


if __name__ == "__main__":
    main()
