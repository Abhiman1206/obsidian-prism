"""GitHub API LangChain tools for commit and signal retrieval."""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx
from langchain_core.tools import tool

from app.infra.providers.base import BaseProviderClient
from app.infra.providers.errors import map_httpx_error
from app.infra.secrets.provider_credentials import ProviderCredentialBundle


logger = logging.getLogger(__name__)


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


_GITHUB_BASE = "https://api.github.com"


def _github_base() -> str:
    return (_load_env("GITHUB_API_BASE") or _GITHUB_BASE).rstrip("/")


def _auth_headers(token: str) -> dict[str, str]:
    bundle = ProviderCredentialBundle(provider="github", token=token, scopes=("repo",))
    return BaseProviderClient().build_auth_headers(bundle)


def _request_json(
    url: str,
    headers: dict[str, str],
    params: dict[str, Any] | None = None,
    timeout: int = 20,
) -> Any:
    client = BaseProviderClient(timeout_seconds=timeout)
    operation = url.rsplit("/", 1)[-1] or "request"

    def _do() -> Any:
        try:
            resp = httpx.get(url, headers=headers, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            mapped = map_httpx_error("github", operation, exc)
            logger.warning(
                "audit_event=provider_call_failure provider=github operation=%s error_code=%s status_code=%s",
                mapped.operation,
                mapped.error_code,
                mapped.status_code if mapped.status_code is not None else "none",
            )
            raise mapped

    return client.run_with_retry(_do, retries=3)


def _paginated_count(
    endpoint: str, headers: dict[str, str], params: dict[str, Any] | None = None, max_pages: int = 10
) -> int:
    base = _github_base()
    total = 0
    page = 1
    while page <= max_pages:
        merged: dict[str, Any] = {"per_page": 100, "page": page}
        if params:
            merged.update(params)
        payload = _request_json(f"{base}{endpoint}", headers, merged)
        if not isinstance(payload, list):
            break
        total += len(payload)
        if len(payload) < 100:
            break
        page += 1
    return total


@tool
def github_fetch_commits(repository: str, token: str = "") -> dict:
    """Fetch paginated commit history with file-level diffs from a GitHub repository.

    Args:
        repository: GitHub repository slug (e.g. 'owner/repo').
        token: Optional runtime token. If omitted, falls back to GITHUB_API_KEY.

    Returns:
        dict with 'commits' list and 'commit_count' integer.
    """
    resolved_token = token.strip() or (_load_env("GITHUB_API_KEY") or "")
    if not resolved_token:
        raise RuntimeError("GITHUB_API_KEY is required")

    headers = _auth_headers(resolved_token)
    base = _github_base()
    all_commits: list[dict] = []
    page = 1
    max_pages = 10

    while page <= max_pages:
        listing = _request_json(
            f"{base}/repos/{repository}/commits",
            headers,
            {"per_page": 30, "page": page},
        )
        if not isinstance(listing, list) or not listing:
            break

        for commit_item in listing:
            if not isinstance(commit_item, dict):
                continue
            sha = str(commit_item.get("sha", "")).strip()
            if not sha:
                continue

            detail = _request_json(f"{base}/repos/{repository}/commits/{sha}", headers)
            files_raw = detail.get("files", []) if isinstance(detail, dict) else []
            files: list[dict] = []
            if isinstance(files_raw, list):
                for f in files_raw:
                    if isinstance(f, dict):
                        files.append(
                            {
                                "path": str(f.get("filename", "")),
                                "additions": int(f.get("additions", 0)),
                                "deletions": int(f.get("deletions", 0)),
                            }
                        )

            commit_meta = commit_item.get("commit", {}) or {}
            author_meta = commit_meta.get("author", {}) or {}

            all_commits.append(
                {
                    "sha": sha,
                    "authored_at": author_meta.get("date"),
                    "author_email": author_meta.get("email"),
                    "files": files,
                }
            )

        if len(listing) < 30:
            break
        page += 1

    return {"commits": all_commits, "commit_count": len(all_commits)}


@tool
def github_fetch_signals(repository: str, token: str = "") -> dict:
    """Fetch operational signals (issues, deployments) from a GitHub repository.

    Args:
        repository: GitHub repository slug (e.g. 'owner/repo').
        token: Optional runtime token. If omitted, falls back to GITHUB_API_KEY.

    Returns:
        dict with issue_opened_count, issue_closed_count, deployment_count.
    """
    resolved_token = token.strip() or (_load_env("GITHUB_API_KEY") or "")
    if not resolved_token:
        raise RuntimeError("GITHUB_API_KEY is required")

    headers = _auth_headers(resolved_token)
    open_count = _paginated_count(f"/repos/{repository}/issues", headers, {"state": "open"})
    closed_count = _paginated_count(f"/repos/{repository}/issues", headers, {"state": "closed"})
    deploy_count = _paginated_count(f"/repos/{repository}/deployments", headers)

    return {
        "issue_opened_count": open_count,
        "issue_closed_count": closed_count,
        "deployment_count": deploy_count,
    }
