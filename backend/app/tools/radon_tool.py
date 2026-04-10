"""Radon LangChain tool for Python code health analysis."""

from __future__ import annotations

from langchain_core.tools import tool


@tool
def radon_analyze_files(file_contents: list[dict]) -> list[dict]:
    """Compute cyclomatic complexity and maintainability index for Python source files using Radon.

    Args:
        file_contents: List of dicts with 'path' and 'source' keys.

    Returns:
        List of dicts with component_id, complexity, maintainability_index, contributors.
    """
    try:
        from radon.complexity import cc_visit
        from radon.metrics import mi_visit
    except ImportError:
        return [
            {
                "component_id": item.get("path", "unknown"),
                "complexity": 0.0,
                "maintainability_index": 100.0,
                "contributors": ["radon_unavailable"],
            }
            for item in file_contents
        ]

    results: list[dict] = []
    for item in file_contents:
        path = str(item.get("path", "unknown"))
        source = str(item.get("source", ""))
        if not source.strip():
            results.append(
                {
                    "component_id": path,
                    "complexity": 0.0,
                    "maintainability_index": 100.0,
                    "contributors": ["empty_source"],
                }
            )
            continue

        try:
            blocks = cc_visit(source)
            avg_complexity = (
                sum(block.complexity for block in blocks) / len(blocks)
                if blocks
                else 0.0
            )
            maintainability = float(mi_visit(source, multi=True))
            results.append(
                {
                    "component_id": path,
                    "complexity": round(float(avg_complexity), 2),
                    "maintainability_index": round(maintainability, 2),
                    "contributors": ["radon_complexity", "radon_maintainability"],
                }
            )
        except Exception:
            results.append(
                {
                    "component_id": path,
                    "complexity": 0.0,
                    "maintainability_index": 100.0,
                    "contributors": ["analysis_error"],
                }
            )

    return results
