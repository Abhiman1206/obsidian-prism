"""GitLab API LangChain tools for commit and signal retrieval."""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import quote

import httpx
from langchain_core.tools import tool

from app.infra.providers.base import BaseProviderClient
from app.infra.secrets.provider_credentials import ProviderCredentialBundle


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


_GITLAB_BASE = "https://gitlab.com/api/v4"


def _gitlab_base() -> str:
    return (_load_env("GITLAB_API_BASE") or _GITLAB_BASE).rstrip("/")


def _auth_headers(token: str) -> dict[str, str]:
    bundle = ProviderCredentialBundle(provider="gitlab", token=token, scopes=("api",))
    return BaseProviderClient().build_auth_headers(bundle)


def _request_json(
    url: str,
    headers: dict[str, str],
    params: dict[str, Any] | None = None,
    timeout: int = 20,
) -> Any:
    client = BaseProviderClient(timeout_seconds=timeout)

    def _do() -> Any:
        resp = httpx.get(url, headers=headers, params=params, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    return client.run_with_retry(_do, retries=3)


def _paginated_count(
    endpoint: str, headers: dict[str, str], params: dict[str, Any] | None = None, max_pages: int = 10
) -> int:
    base = _gitlab_base()
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
def gitlab_fetch_commits(repository: str) -> dict:
    """Fetch paginated commit history with file-level diffs from a GitLab repository.

    Args:
        repository: GitLab project path (e.g. 'group/project').

    Returns:
        dict with 'commits' list and 'commit_count' integer.
    """
    token = _load_env("GITLAB_API_KEY")
    if not token:
        raise RuntimeError("GITLAB_API_KEY is required")

    headers = _auth_headers(token)
    base = _gitlab_base()
    project = quote(repository, safe="")
    all_commits: list[dict] = []
    page = 1
    max_pages = 10

    while page <= max_pages:
        listing = _request_json(
            f"{base}/projects/{project}/repository/commits",
            headers,
            {"per_page": 30, "page": page},
        )
        if not isinstance(listing, list) or not listing:
            break

        for commit_item in listing:
            if not isinstance(commit_item, dict):
                continue
            sha = str(commit_item.get("id", "")).strip()
            if not sha:
                continue

            diff_payload = _request_json(
                f"{base}/projects/{project}/repository/commits/{sha}/diff",
                headers,
            )
            files: list[dict] = []
            if isinstance(diff_payload, list):
                for f in diff_payload:
                    if isinstance(f, dict):
                        files.append(
                            {
                                "path": str(f.get("new_path", f.get("old_path", ""))),
                                "additions": int(f.get("additions", 0)),
                                "deletions": int(f.get("deletions", 0)),
                            }
                        )

            all_commits.append(
                {
                    "sha": sha,
                    "authored_at": commit_item.get("created_at") or commit_item.get("authored_date"),
                    "author_email": commit_item.get("author_email"),
                    "files": files,
                }
            )

        if len(listing) < 30:
            break
        page += 1

    return {"commits": all_commits, "commit_count": len(all_commits)}


@tool
def gitlab_fetch_signals(repository: str) -> dict:
    """Fetch operational signals (issues, deployments) from a GitLab repository.

    Args:
        repository: GitLab project path (e.g. 'group/project').

    Returns:
        dict with issue_opened_count, issue_closed_count, deployment_count.
    """
    token = _load_env("GITLAB_API_KEY")
    if not token:
        raise RuntimeError("GITLAB_API_KEY is required")

    headers = _auth_headers(token)
    project = quote(repository, safe="")
    open_count = _paginated_count(f"/projects/{project}/issues", headers, {"state": "opened"})
    closed_count = _paginated_count(f"/projects/{project}/issues", headers, {"state": "closed"})
    deploy_count = _paginated_count(f"/projects/{project}/deployments", headers)

    return {
        "issue_opened_count": open_count,
        "issue_closed_count": closed_count,
        "deployment_count": deploy_count,
    }
