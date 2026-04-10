def _summarize_commit(commit: dict) -> dict:
    files = commit.get("files", [])
    insertions = sum(file_item.get("additions", 0) for file_item in files)
    deletions = sum(file_item.get("deletions", 0) for file_item in files)

    return {
        "commit_sha": commit["sha"],
        "authored_at": commit["authored_at"],
        "author_email": commit["author_email"],
        "files_changed": len(files),
        "insertions": insertions,
        "deletions": deletions,
    }


def _build_churn(commits: list[dict]) -> list[dict]:
    by_author: dict[str, dict] = {}
    for commit in commits:
        author = commit["author_email"]
        by_author.setdefault(author, {"commits": 0, "files": set()})
        by_author[author]["commits"] += 1
        for file_item in commit.get("files", []):
            by_author[author]["files"].add(file_item.get("path"))

    churn = []
    for contributor, stats in by_author.items():
        churn.append(
            {
                "contributor": contributor,
                "commits_last_30d": stats["commits"],
                "files_touched_last_30d": len(stats["files"]),
            }
        )

    return churn


def normalize_provider_payload(repository_id: str, provider: str, commits: list[dict]) -> dict:
    canonical_commits = [_summarize_commit(commit) for commit in commits]
    churn = _build_churn(commits)

    return {
        "repository_id": repository_id,
        "provider": provider,
        "commits": canonical_commits,
        "churn": churn,
    }
