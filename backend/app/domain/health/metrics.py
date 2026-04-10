from __future__ import annotations

from pathlib import Path

EXCLUDED_PATH_PARTS = (
    "node_modules",
    ".venv",
    "dist",
    "build",
    "__pycache__",
)


def _is_excluded(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return any(part in normalized for part in EXCLUDED_PATH_PARTS)


def collect_python_files(artifacts: list[dict]) -> list[str]:
    component_files: list[str] = []
    for artifact in artifacts:
        path = str(artifact.get("path", ""))
        if not path.endswith(".py"):
            continue
        if _is_excluded(path):
            continue
        component_files.append(path)
    return component_files


def _fallback_metric(component_id: str, marker: str) -> dict:
    return {
        "component_id": component_id,
        "complexity": 0.0,
        "maintainability_index": 100.0,
        "contributors": [marker],
    }


def compute_radon_metrics(component_files: list[str]) -> list[dict]:
    try:
        from radon.complexity import cc_visit
        from radon.metrics import mi_visit
    except Exception:
        return [_fallback_metric(component_id=file_path, marker="radon_unavailable") for file_path in component_files]

    results: list[dict] = []
    for file_path in component_files:
        try:
            source = Path(file_path).read_text(encoding="utf-8")
            complexity_blocks = cc_visit(source)
            avg_complexity = (
                sum(block.complexity for block in complexity_blocks) / len(complexity_blocks)
                if complexity_blocks
                else 0.0
            )
            maintainability = float(mi_visit(source, multi=True))
            results.append(
                {
                    "component_id": file_path,
                    "complexity": float(avg_complexity),
                    "maintainability_index": maintainability,
                    "contributors": ["radon_complexity", "radon_maintainability"],
                }
            )
        except Exception:
            results.append(_fallback_metric(component_id=file_path, marker="analysis_error"))

    return results
