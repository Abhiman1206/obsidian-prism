"""Code Health Analyst Agent — computes health scores using Radon metrics.

PRD Role: Acts as the quantitative evaluator. Uses the Radon tool to compute
cyclomatic complexity, maintainability indices, and test coverage trends,
assigning a real-time health score to each module.
"""

from __future__ import annotations

from typing import Any

from app.agents.base_agent import BaseSpecialistAgent
from app.agents.shared_memory import EpistemicMemory
from app.domain.health.scoring import score_component
from app.tools.github_file_fetcher import fetch_python_file_contents
from app.tools.radon_tool import radon_analyze_files


class HealthAnalystAgent(BaseSpecialistAgent):
    name = "health_analyst_agent"
    role_description = (
        "You are a Code Health Analyst agent. Your job is to compute cyclomatic complexity "
        "and maintainability metrics for each Python module using Radon. First, identify "
        "Python files from the commit data in shared memory. Then fetch their source code "
        "and analyze them with the Radon tool. Write health scores to shared memory."
    )
    tools = [fetch_python_file_contents, radon_analyze_files]

    def execute_deterministic(self, memory: EpistemicMemory) -> dict[str, Any]:
        """Deterministic execution: identify files, fetch source, run Radon, score."""
        raw_commits = memory.read("raw_commits", [])
        repository = memory.read("repository", "")
        provider = memory.read("provider", "github")

        # Extract unique Python file paths from commits
        file_set: set[str] = set()
        component_volatility: dict[str, float] = {}
        component_contributors: dict[str, set[str]] = {}

        for commit in raw_commits:
            if not isinstance(commit, dict):
                continue
            author = str(commit.get("author_email", "unknown@unknown"))
            for f in commit.get("files", []):
                if not isinstance(f, dict):
                    continue
                path = str(f.get("path", ""))
                if path.endswith(".py") and not any(
                    ex in path for ex in ("node_modules", "__pycache__", ".venv", "dist", "build")
                ):
                    file_set.add(path)
                    component_volatility.setdefault(path, 0.0)
                    component_volatility[path] += 1.0
                    component_contributors.setdefault(path, set())
                    component_contributors[path].add(author)

        py_paths = sorted(file_set)

        # Fetch source code and run Radon
        metric_rows: list[dict] = []
        if py_paths and provider == "github":
            fetcher_tool = self._get_tool("fetch_python_file_contents")
            if fetcher_tool:
                file_contents = self._invoke_tool(
                    fetcher_tool,
                    {"repository": repository, "file_paths": py_paths},
                    memory,
                )
                if isinstance(file_contents, list) and file_contents:
                    radon_tool = self._get_tool("radon_analyze_files")
                    if radon_tool:
                        metric_rows = self._invoke_tool(
                            radon_tool,
                            {"file_contents": file_contents},
                            memory,
                        )
                        if not isinstance(metric_rows, list):
                            metric_rows = []

        # Fall back to commit-derived metrics if Radon didn't produce results
        if not metric_rows:
            metric_rows = self._derive_fallback_metrics(raw_commits)

        # Normalize volatility to [0, 1]
        max_touches = max(component_volatility.values()) if component_volatility else 1.0
        volatility_map: dict[str, float] = {
            path: min(1.0, touches / max(max_touches, 20.0))
            for path, touches in component_volatility.items()
        }

        # Add contributor info to metric rows
        for row in metric_rows:
            cid = row.get("component_id", "")
            if cid in component_contributors:
                existing = set(row.get("contributors", []))
                existing.update(component_contributors.get(cid, set()))
                row["contributors"] = sorted(existing)

        # Score each component using the existing deterministic scorer
        health_rows = self._score_components(
            memory.run_id,
            memory.repository_id,
            metric_rows,
            volatility_map,
        )

        memory.write(self.name, "metric_rows", metric_rows)
        memory.write(self.name, "volatility_map", volatility_map)
        memory.write(self.name, "health_rows", health_rows)

        return {
            "status": "complete",
            "agent": self.name,
            "mode": "deterministic",
            "components_analyzed": len(metric_rows),
            "radon_used": any("radon" in str(r.get("contributors", [])) for r in metric_rows),
        }

    def _score_components(
        self,
        run_id: str,
        repository_id: str,
        metric_rows: list[dict],
        volatility_map: dict[str, float],
    ) -> list[dict]:
        """Score components using the existing deterministic scorer."""
        from datetime import datetime, timezone

        measured_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        scored: list[dict] = []

        for metric in metric_rows:
            cid = metric.get("component_id", "")
            volatility = volatility_map.get(cid, 0.0)
            result = score_component(
                component_id=cid,
                maintainability_index=float(metric.get("maintainability_index", 100.0)),
                complexity=float(metric.get("complexity", 0.0)),
                volatility=float(volatility),
                contributors=list(metric.get("contributors", [])),
            )
            scored.append(
                {
                    **result,
                    "run_id": run_id,
                    "repository_id": repository_id,
                    "measured_at": measured_at,
                }
            )

        return scored

    def _derive_fallback_metrics(self, raw_commits: list[dict]) -> list[dict]:
        """Derive metrics from commit history when Radon is unavailable."""
        component_map: dict[str, dict[str, Any]] = {}

        for commit in raw_commits:
            if not isinstance(commit, dict):
                continue
            for f in commit.get("files", []):
                if not isinstance(f, dict):
                    continue
                path = str(f.get("path", ""))
                if not path:
                    continue
                state = component_map.setdefault(path, {"touches": 0, "additions": 0, "deletions": 0})
                state["touches"] += 1
                state["additions"] += max(int(f.get("additions", 0)), 0)
                state["deletions"] += max(int(f.get("deletions", 0)), 0)

        if not component_map:
            return [
                {
                    "component_id": "repository-summary",
                    "maintainability_index": 100.0,
                    "complexity": 0.0,
                    "contributors": ["fallback_metrics"],
                }
            ]

        rows: list[dict] = []
        for cid, state in sorted(component_map.items()):
            touches = float(state["touches"])
            churn = float(state["additions"] + state["deletions"])
            mi = max(20.0, 100.0 - min(80.0, (touches * 1.8) + (churn / 250.0)))
            cx = min(50.0, 1.0 + (touches * 0.7) + (churn / 180.0))
            rows.append(
                {
                    "component_id": cid,
                    "maintainability_index": round(mi, 2),
                    "complexity": round(cx, 2),
                    "contributors": ["fallback_metrics"],
                }
            )
        return rows

    def _process_tool_result(self, tool_name: str, result: Any, memory: EpistemicMemory) -> None:
        if tool_name == "radon_analyze_files" and isinstance(result, list):
            memory.write(self.name, "metric_rows", result)
