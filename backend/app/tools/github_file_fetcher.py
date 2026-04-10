"""GitHub file content fetcher LangChain tool for Radon source analysis."""

from __future__ import annotations

import base64
import os
from typing import Any

import httpx
from langchain_core.tools import tool

from app.infra.providers.base import BaseProviderClient
from app.infra.secrets.provider_credentials import ProviderCredentialBundle

EXCLUDED_PATHS = ("node_modules", "__pycache__", ".venv", "dist", "build", ".git")
MAX_FILES = 50


def _load_env(key: str) -> str | None:
    from pathlib import Path

    value = os.getenv(key)
    if value:
        return value
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return None
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() == key:
            cleaned = v.strip().strip('"').strip("'")
            if cleaned:
                return cleaned
    return None


def _github_base() -> str:
    return (_load_env("GITHUB_API_BASE") or "https://api.github.com").rstrip("/")


def _auth_headers(token: str) -> dict[str, str]:
    bundle = ProviderCredentialBundle(provider="github", token=token, scopes=("repo",))
    return BaseProviderClient().build_auth_headers(bundle)


def _is_excluded(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return any(part in normalized for part in EXCLUDED_PATHS)


def _fetch_file(base: str, repository: str, path: str, headers: dict[str, str]) -> str | None:
    """Fetch a single file's decoded content from GitHub."""
    client = BaseProviderClient(timeout_seconds=15)

    def _do() -> str | None:
        resp = httpx.get(
            f"{base}/repos/{repository}/contents/{path}",
            headers=headers,
            params={"ref": "HEAD"},
            timeout=15,
        )
        if resp.status_code != 200:
            return None
        body = resp.json()
        if not isinstance(body, dict) or body.get("encoding") != "base64":
            return None
        content_b64 = body.get("content", "")
        if not content_b64:
            return None
        return base64.b64decode(content_b64).decode("utf-8", errors="replace")

    try:
        return client.run_with_retry(_do, retries=2)
    except Exception:
        return None


@tool
def fetch_python_file_contents(repository: str, file_paths: list[str]) -> list[dict]:
    """Fetch Python source file contents from a GitHub repository for Radon analysis.

    Args:
        repository: GitHub repository slug (e.g. 'owner/repo').
        file_paths: List of file paths to fetch (e.g. ['src/main.py', 'lib/utils.py']).

    Returns:
        List of dicts with 'path' and 'source' keys for successfully fetched files.
    """
    token = _load_env("GITHUB_API_KEY")
    if not token:
        raise RuntimeError("GITHUB_API_KEY is required")

    headers = _auth_headers(token)
    base = _github_base()

    # Filter to .py files, skip excluded paths, limit count
    py_paths = [
        p for p in file_paths
        if p.endswith(".py") and not _is_excluded(p)
    ][:MAX_FILES]

    results: list[dict] = []
    for path in py_paths:
        source = _fetch_file(base, repository, path, headers)
        if source is not None:
            results.append({"path": path, "source": source})

    return results
