from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
import json
import subprocess
import sys


DAYS_WINDOW = 90


@dataclass
class CommitEntry:
    sha: str
    epoch_seconds: int
    author: str
    message: str

    @property
    def committed_at(self) -> datetime:
        return datetime.fromtimestamp(self.epoch_seconds, tz=UTC)



def _run_git(repo_dir: Path, args: list[str]) -> str:
    cmd = ["git", *args]
    completed = subprocess.run(
        cmd,
        cwd=str(repo_dir),
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout



def _ensure_reportlab() -> None:
    try:
        import reportlab  # noqa: F401
    except Exception:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])



def _window_days(end_day: date, days: int) -> list[date]:
    start = end_day - timedelta(days=days - 1)
    return [start + timedelta(days=i) for i in range(days)]



def _parse_commits(raw: str) -> list[CommitEntry]:
    commits: list[CommitEntry] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("\x1f")
        if len(parts) != 4:
            continue
        sha, epoch_s, author, message = parts
        try:
            commits.append(
                CommitEntry(
                    sha=sha.strip(),
                    epoch_seconds=int(epoch_s.strip()),
                    author=author.strip() or "unknown",
                    message=message.strip(),
                )
            )
        except ValueError:
            continue
    return commits



def _collect_metrics(repo_dir: Path, days_window: int) -> dict:
    now = datetime.now(tz=UTC)
    end_day = now.date()
    start_day = end_day - timedelta(days=days_window - 1)

    repo_name = _run_git(repo_dir, ["config", "--get", "remote.origin.url"]).strip() or repo_dir.name
    head_branch = _run_git(repo_dir, ["rev-parse", "--abbrev-ref", "HEAD"]).strip() or "unknown"

    commit_raw = _run_git(
        repo_dir,
        [
            "log",
            f"--since={days_window}.days",
            "--pretty=format:%H%x1f%ct%x1f%an%x1f%s",
        ],
    )
    commits = _parse_commits(commit_raw)

    tracked_files_raw = _run_git(repo_dir, ["ls-files"])
    tracked_files = {line.strip() for line in tracked_files_raw.splitlines() if line.strip()}

    touched_files_raw = _run_git(repo_dir, ["log", f"--since={days_window}.days", "--name-only", "--pretty=format:"])
    touched_files = {line.strip() for line in touched_files_raw.splitlines() if line.strip()}

    day_commits: Counter[date] = Counter()
    author_commits: Counter[str] = Counter()
    for commit in commits:
        day_commits[commit.committed_at.date()] += 1
        author_commits[commit.author] += 1

    all_days = _window_days(end_day, days_window)
    active_days = [d for d in all_days if day_commits.get(d, 0) > 0]
    inactive_days = [d for d in all_days if day_commits.get(d, 0) == 0]

    weekly_commits: defaultdict[str, int] = defaultdict(int)
    for day in all_days:
        iso = day.isocalendar()
        week_key = f"{iso.year}-W{iso.week:02d}"
        weekly_commits[week_key] += day_commits.get(day, 0)

    low_activity_weeks = {week: count for week, count in weekly_commits.items() if count < 2}

    touched_tracked_files = tracked_files & touched_files
    stale_files = sorted(tracked_files - touched_files)

    inactivity_loss_count = len(inactive_days)
    flags = {
        "inactive_day_flags": inactivity_loss_count,
        "low_activity_week_flags": len(low_activity_weeks),
        "stale_file_flags": len(stale_files),
        "single_contributor_risk_flag": 1 if len(author_commits) <= 1 and len(commits) > 0 else 0,
    }
    total_flag_count = sum(flags.values())

    top_authors = [
        {"author": author, "commit_count": count}
        for author, count in author_commits.most_common(5)
    ]

    recent_commits = [
        {
            "sha": c.sha,
            "committed_at": c.committed_at.isoformat().replace("+00:00", "Z"),
            "author": c.author,
            "message": c.message,
        }
        for c in commits[:10]
    ]

    return {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "repository": {
            "path": str(repo_dir),
            "origin": repo_name,
            "branch": head_branch,
        },
        "window": {
            "days": days_window,
            "start_date": start_day.isoformat(),
            "end_date": end_day.isoformat(),
        },
        "activity": {
            "commit_count": len(commits),
            "active_day_count": len(active_days),
            "inactive_day_count": len(inactive_days),
            "activeness_ratio": round((len(active_days) / days_window) * 100.0, 2),
            "inactivity_loss_count": inactivity_loss_count,
            "contributor_count": len(author_commits),
            "top_authors": top_authors,
            "low_activity_weeks": low_activity_weeks,
        },
        "flags": {
            "flag_breakdown": flags,
            "total_flag_count": total_flag_count,
            "flag_severity": "high" if total_flag_count >= 80 else ("medium" if total_flag_count >= 40 else "low"),
        },
        "codebase": {
            "tracked_file_count": len(tracked_files),
            "files_touched_in_window": len(touched_tracked_files),
            "stale_file_count": len(stale_files),
            "sample_stale_files": stale_files[:25],
        },
        "recent_commits": recent_commits,
        "notes": [
            "Inactivity loss count equals number of days in the 90-day window with zero commits.",
            "Total flag count aggregates inactivity days, low-activity weeks, stale files, and contributor concentration risk.",
        ],
    }



def _build_markdown(report: dict) -> str:
    repo = report["repository"]
    window = report["window"]
    activity = report["activity"]
    flags = report["flags"]
    codebase = report["codebase"]

    md = []
    md.append("# Technical Activity Loss Report")
    md.append("")
    md.append("## Repository")
    md.append(f"- Origin: {repo['origin']}")
    md.append(f"- Branch: {repo['branch']}")
    md.append(f"- Local path: {repo['path']}")
    md.append("")
    md.append("## 90-Day Window")
    md.append(f"- Start: {window['start_date']}")
    md.append(f"- End: {window['end_date']}")
    md.append(f"- Days: {window['days']}")
    md.append("")
    md.append("## Activeness and Loss Count")
    md.append(f"- Commits: {activity['commit_count']}")
    md.append(f"- Active days: {activity['active_day_count']}")
    md.append(f"- Inactive days: {activity['inactive_day_count']}")
    md.append(f"- Activeness ratio: {activity['activeness_ratio']}%")
    md.append(f"- Inactivity loss count: {activity['inactivity_loss_count']}")
    md.append(f"- Contributors: {activity['contributor_count']}")
    md.append("")
    md.append("## Flag Count")
    md.append(f"- Total flag count: {flags['total_flag_count']}")
    md.append(f"- Severity: {flags['flag_severity']}")
    for key, value in flags["flag_breakdown"].items():
        md.append(f"- {key}: {value}")
    md.append("")
    md.append("## Codebase Staleness")
    md.append(f"- Tracked files: {codebase['tracked_file_count']}")
    md.append(f"- Touched in window: {codebase['files_touched_in_window']}")
    md.append(f"- Stale files: {codebase['stale_file_count']}")
    md.append("")
    md.append("## Top Authors")
    for row in activity.get("top_authors", []):
        md.append(f"- {row['author']}: {row['commit_count']} commits")
    md.append("")
    md.append("## Recent Commits")
    for row in report.get("recent_commits", []):
        md.append(f"- {row['sha'][:10]} | {row['committed_at']} | {row['author']} | {row['message']}")
    md.append("")
    md.append("## Notes")
    for note in report.get("notes", []):
        md.append(f"- {note}")
    md.append("")
    return "\n".join(md)



def _build_pdf(report: dict, pdf_path: Path) -> None:
    _ensure_reportlab()

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph
    from reportlab.platypus import SimpleDocTemplate
    from reportlab.platypus import Spacer

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    activity = report["activity"]
    flags = report["flags"]
    codebase = report["codebase"]
    window = report["window"]
    repo = report["repository"]

    story = []
    story.append(Paragraph("Technical Activity Loss Report", styles["Title"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"Generated: {report['generated_at']}", styles["Normal"]))
    story.append(Paragraph(f"Repository origin: {repo['origin']}", styles["Normal"]))
    story.append(Paragraph(f"Branch: {repo['branch']}", styles["Normal"]))
    story.append(Paragraph(f"Window: {window['start_date']} to {window['end_date']} ({window['days']} days)", styles["Normal"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Activeness and Loss Count", styles["Heading2"]))
    for line in [
        f"Commits in window: {activity['commit_count']}",
        f"Active days: {activity['active_day_count']}",
        f"Inactive days: {activity['inactive_day_count']}",
        f"Activeness ratio: {activity['activeness_ratio']}%",
        f"Inactivity loss count: {activity['inactivity_loss_count']}",
        f"Contributors: {activity['contributor_count']}",
    ]:
        story.append(Paragraph(f"- {line}", styles["Normal"]))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Flag Count", styles["Heading2"]))
    story.append(Paragraph(f"Total flag count: {flags['total_flag_count']} (severity: {flags['flag_severity']})", styles["Normal"]))
    for key, value in flags["flag_breakdown"].items():
        story.append(Paragraph(f"- {key}: {value}", styles["Normal"]))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Codebase Staleness", styles["Heading2"]))
    for line in [
        f"Tracked files: {codebase['tracked_file_count']}",
        f"Touched files in window: {codebase['files_touched_in_window']}",
        f"Stale files: {codebase['stale_file_count']}",
    ]:
        story.append(Paragraph(f"- {line}", styles["Normal"]))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Top Authors", styles["Heading2"]))
    for row in activity.get("top_authors", []):
        story.append(Paragraph(f"- {row['author']}: {row['commit_count']} commits", styles["Normal"]))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Recent Commits", styles["Heading2"]))
    for row in report.get("recent_commits", []):
        story.append(
            Paragraph(
                f"- {row['sha'][:10]} | {row['committed_at']} | {row['author']} | {row['message']}",
                styles["Normal"],
            )
        )

    doc.build(story)



def main() -> None:
    repo_dir = Path(__file__).resolve().parents[1]
    report = _collect_metrics(repo_dir=repo_dir, days_window=DAYS_WINDOW)

    stamp = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S")
    report_id = f"TECH-ACTIVITY-{stamp}"

    out_dir = Path(__file__).resolve().parent
    json_path = out_dir / f"{report_id}.json"
    md_path = out_dir / f"{report_id}.md"
    pdf_path = out_dir / f"{report_id}.pdf"

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(_build_markdown(report), encoding="utf-8")
    _build_pdf(report, pdf_path)

    print(str(json_path))
    print(str(md_path))
    print(str(pdf_path))


if __name__ == "__main__":
    main()
