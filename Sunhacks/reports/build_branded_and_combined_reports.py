from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
import json

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing, String


PRIMARY = colors.HexColor("#0F172A")
ACCENT = colors.HexColor("#0EA5E9")
MUTED = colors.HexColor("#64748B")
CARD_BG = colors.HexColor("#F8FAFC")
BORDER = colors.HexColor("#CBD5E1")


def _latest_file(pattern: str, folder: Path) -> Path:
    matches = sorted(folder.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not matches:
        raise FileNotFoundError(f"No files found for pattern: {pattern}")
    return matches[0]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _header(canvas: Canvas, title: str, subtitle: str) -> None:
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, 27.2 * cm, A4[0], 2.5 * cm, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 15)
    canvas.drawString(1.6 * cm, 28.5 * cm, title)
    canvas.setFont("Helvetica", 9)
    canvas.drawString(1.6 * cm, 27.9 * cm, subtitle)
    canvas.setFillColor(colors.black)


def _kpi(canvas: Canvas, x: float, y: float, w: float, h: float, label: str, value: str) -> None:
    canvas.setStrokeColor(BORDER)
    canvas.setFillColor(CARD_BG)
    canvas.roundRect(x, y, w, h, 6, stroke=1, fill=1)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 9)
    canvas.drawString(x + 8, y + h - 16, label)
    canvas.setFillColor(PRIMARY)
    canvas.setFont("Helvetica-Bold", 13)
    canvas.drawString(x + 8, y + 10, value)
    canvas.setFillColor(colors.black)


def _draw_exec_page(canvas: Canvas, ceo: dict) -> None:
    repo = ceo["repository"]
    cost = ceo["cost_of_inaction"]
    risk = ceo["risk_probability"]
    incidents = ceo["incidents_90d"]

    _header(
        canvas,
        "AI_APP Executive KPI Dashboard",
        f"Repository: {repo.get('repository_name', 'N/A')} | Generated: {datetime.now(tz=UTC).isoformat()}",
    )

    _kpi(canvas, 1.6 * cm, 23.6 * cm, 5.8 * cm, 2.7 * cm, "Health Score", f"{repo.get('health', {}).get('score', 0)}/100")
    _kpi(canvas, 7.8 * cm, 23.6 * cm, 5.8 * cm, 2.7 * cm, "90D Risk", f"{risk * 100:.0f}%")
    _kpi(canvas, 14.0 * cm, 23.6 * cm, 5.4 * cm, 2.7 * cm, "Incidents", str(incidents))

    pie_d = Drawing(245, 175)
    pie = Pie()
    pie.x = 22
    pie.y = 22
    pie.width = 132
    pie.height = 132
    pie.data = [round(risk * 100, 2), round((1 - risk) * 100, 2)]
    pie.labels = ["Risk", "Stability"]
    pie.slices[0].fillColor = colors.HexColor("#DC2626")
    pie.slices[1].fillColor = colors.HexColor("#16A34A")
    pie_d.add(pie)
    pie_d.add(String(8, 160, "Risk Composition", fontSize=10, fillColor=PRIMARY))
    pie_d.drawOn(canvas, 1.6 * cm, 15.0 * cm)

    cost_d = Drawing(310, 175)
    bar = VerticalBarChart()
    bar.x = 36
    bar.y = 30
    bar.width = 245
    bar.height = 120
    bar.data = [[
        cost.get("engineering_cost_loss", 0),
        cost.get("downtime_cost_loss", 0),
        cost.get("total_cost_inaction", 0),
    ]]
    bar.categoryAxis.categoryNames = ["Eng", "Downtime", "Total"]
    bar.valueAxis.valueMin = 0
    bar.bars[0].fillColor = ACCENT
    cost_d.add(bar)
    cost_d.add(String(8, 160, "Cost of Inaction (USD)", fontSize=10, fillColor=PRIMARY))
    cost_d.drawOn(canvas, 8.8 * cm, 15.0 * cm)

    canvas.setFont("Helvetica-Bold", 11)
    canvas.setFillColor(PRIMARY)
    canvas.drawString(1.6 * cm, 14.2 * cm, "Leadership Priorities")
    canvas.setFont("Helvetica", 9.5)
    y = 13.6 * cm
    for i, item in enumerate(ceo.get("priorities", []), start=1):
        canvas.drawString(1.8 * cm, y, f"{i}. {item}")
        y -= 0.55 * cm

    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(1.6 * cm, 1.2 * cm, "Branded visual report generated from repository analytics JSON.")
    canvas.setFillColor(colors.black)


def _draw_tech_page(canvas: Canvas, tech: dict) -> None:
    repo = tech["repository"]
    activity = tech["activity"]
    flags = tech["flags"]
    codebase = tech["codebase"]

    _header(
        canvas,
        "AI_APP Technical KPI Dashboard",
        f"Origin: {repo.get('origin', 'N/A')} | Branch: {repo.get('branch', 'N/A')}",
    )

    _kpi(canvas, 1.6 * cm, 23.6 * cm, 4.5 * cm, 2.7 * cm, "Commits", str(activity.get("commit_count", 0)))
    _kpi(canvas, 6.4 * cm, 23.6 * cm, 4.5 * cm, 2.7 * cm, "Active Days", str(activity.get("active_day_count", 0)))
    _kpi(canvas, 11.2 * cm, 23.6 * cm, 4.5 * cm, 2.7 * cm, "Inactive Days", str(activity.get("inactive_day_count", 0)))
    _kpi(canvas, 16.0 * cm, 23.6 * cm, 3.4 * cm, 2.7 * cm, "Flags", str(flags.get("total_flag_count", 0)))

    act_d = Drawing(275, 180)
    act_bar = VerticalBarChart()
    act_bar.x = 40
    act_bar.y = 30
    act_bar.width = 210
    act_bar.height = 125
    act_bar.data = [[activity.get("active_day_count", 0), activity.get("inactive_day_count", 0)]]
    act_bar.categoryAxis.categoryNames = ["Active", "Inactive"]
    act_bar.valueAxis.valueMin = 0
    act_bar.bars[0].fillColor = colors.HexColor("#2563EB")
    act_d.add(act_bar)
    act_d.add(String(8, 164, "Activity Split (90 days)", fontSize=10, fillColor=PRIMARY))
    act_d.drawOn(canvas, 1.6 * cm, 15.0 * cm)

    breakdown = flags.get("flag_breakdown", {})
    risk_d = Drawing(320, 180)
    risk_bar = VerticalBarChart()
    risk_bar.x = 34
    risk_bar.y = 30
    risk_bar.width = 255
    risk_bar.height = 125
    risk_bar.data = [[
        breakdown.get("inactive_day_flags", 0),
        breakdown.get("low_activity_week_flags", 0),
        breakdown.get("stale_file_flags", 0),
        breakdown.get("single_contributor_risk_flag", 0),
    ]]
    risk_bar.categoryAxis.categoryNames = ["Inactive", "LowWk", "Stale", "1Owner"]
    risk_bar.valueAxis.valueMin = 0
    risk_bar.bars[0].fillColor = colors.HexColor("#EA580C")
    risk_d.add(risk_bar)
    risk_d.add(String(8, 164, "Flag Breakdown", fontSize=10, fillColor=PRIMARY))
    risk_d.drawOn(canvas, 8.4 * cm, 15.0 * cm)

    canvas.setFont("Helvetica-Bold", 11)
    canvas.setFillColor(PRIMARY)
    canvas.drawString(1.6 * cm, 14.2 * cm, "Codebase KPI Snapshot")
    canvas.setFont("Helvetica", 9.5)
    canvas.drawString(1.8 * cm, 13.6 * cm, f"Tracked files: {codebase.get('tracked_file_count', 0)}")
    canvas.drawString(1.8 * cm, 13.1 * cm, f"Touched in window: {codebase.get('files_touched_in_window', 0)}")
    canvas.drawString(1.8 * cm, 12.6 * cm, f"Stale files: {codebase.get('stale_file_count', 0)}")
    canvas.drawString(1.8 * cm, 12.1 * cm, f"Contributors: {activity.get('contributor_count', 0)}")
    canvas.drawString(1.8 * cm, 11.6 * cm, f"Activeness ratio: {activity.get('activeness_ratio', 0)}%")

    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(1.6 * cm, 1.2 * cm, "Branded visual report generated from repository analytics JSON.")
    canvas.setFillColor(colors.black)


def _build_single_pdf(path: Path, draw_fn, data: dict) -> None:
    c = Canvas(str(path), pagesize=A4)
    draw_fn(c, data)
    c.save()


def _build_combined_pdf(path: Path, ceo: dict, tech: dict) -> None:
    c = Canvas(str(path), pagesize=A4)
    _draw_exec_page(c, ceo)
    c.showPage()
    _draw_tech_page(c, tech)
    c.save()


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    ceo_json = _latest_file("CEO-Abhiman1206-AI_APP-*.json", out_dir)
    tech_json = _latest_file("TECH-ACTIVITY-AI_APP-*.json", out_dir)

    ceo = _load_json(ceo_json)
    tech = _load_json(tech_json)

    stamp = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S")
    ceo_pdf = out_dir / f"CEO-AI_APP-BRANDED-{stamp}.pdf"
    tech_pdf = out_dir / f"TECH-AI_APP-BRANDED-{stamp}.pdf"
    combined_pdf = out_dir / f"AI_APP-COMBINED-BRANDED-{stamp}.pdf"

    _build_single_pdf(ceo_pdf, _draw_exec_page, ceo)
    _build_single_pdf(tech_pdf, _draw_tech_page, tech)
    _build_combined_pdf(combined_pdf, ceo, tech)

    print(str(ceo_pdf))
    print(str(tech_pdf))
    print(str(combined_pdf))


if __name__ == "__main__":
    main()
