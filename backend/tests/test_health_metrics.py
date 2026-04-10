from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.domain.health.metrics import collect_python_files, compute_radon_metrics


def test_collects_python_file_metrics_shape() -> None:
    artifacts = [
        {"path": "src/service/core.py"},
    ]

    python_files = collect_python_files(artifacts)
    metrics = compute_radon_metrics(python_files)

    assert len(metrics) == 1
    metric = metrics[0]
    assert {"component_id", "complexity", "maintainability_index"}.issubset(metric.keys())


def test_excluded_paths_are_skipped_from_analysis() -> None:
    artifacts = [
        {"path": "node_modules/pkg/index.py"},
        {"path": ".venv/lib/python3.12/site.py"},
        {"path": "dist/generated.py"},
        {"path": "build/generated.py"},
        {"path": "__pycache__/cached.py"},
        {"path": "src/keep.py"},
    ]

    python_files = collect_python_files(artifacts)

    assert python_files == ["src/keep.py"]


def test_radon_unavailable_returns_deterministic_fallback(monkeypatch) -> None:
    import builtins

    original_import = builtins.__import__

    def _mock_import(name: str, *args, **kwargs):  # type: ignore[no-untyped-def]
        if name.startswith("radon"):
            raise ImportError("radon missing")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _mock_import)

    metrics = compute_radon_metrics(["src/fallback.py"])

    assert len(metrics) == 1
    assert metrics[0]["complexity"] == 0.0
    assert metrics[0]["maintainability_index"] == 100.0
    assert "radon_unavailable" in metrics[0]["contributors"]
