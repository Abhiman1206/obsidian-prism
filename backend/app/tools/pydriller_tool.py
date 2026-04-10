"""PyDriller LangChain tool for local repository mining."""

from __future__ import annotations

from langchain_core.tools import tool


@tool
def pydriller_mine_repository(repository_path: str, since_sha: str = "") -> dict:
    """Mine commit history from a local Git repository using PyDriller.

    Args:
        repository_path: Absolute path to a local Git repository.
        since_sha: Optional SHA to resume from. Only commits after this SHA are returned.

    Returns:
        dict with 'commits' list and 'commit_count' integer.
    """
    from app.infra.miners.pydriller_miner import load_repository_commits, mine_incremental

    all_commits = load_repository_commits(repository_path)

    if since_sha:
        filtered = mine_incremental(
            commits=all_commits,
            last_processed_commit_sha=since_sha,
            repository_path=repository_path,
        )
    else:
        filtered = all_commits

    return {"commits": filtered, "commit_count": len(filtered)}
