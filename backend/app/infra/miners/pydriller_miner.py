def load_repository_commits(repository_path: str) -> list[dict]:
    try:
        from pydriller import Repository
    except ImportError as exc:  # pragma: no cover - guarded by integration tests/mocks
        raise RuntimeError("pydriller package is required for repository mining mode") from exc

    mined: list[dict] = []
    for commit in Repository(repository_path).traverse_commits():
        files = []
        for modified in getattr(commit, "modified_files", []) or []:
            files.append(
                {
                    "path": getattr(modified, "new_path", None) or getattr(modified, "old_path", ""),
                    "additions": int(getattr(modified, "added_lines", 0) or 0),
                    "deletions": int(getattr(modified, "deleted_lines", 0) or 0),
                }
            )

        author = getattr(commit, "author", None)
        mined.append(
            {
                "sha": commit.hash,
                "authored_at": commit.author_date.isoformat() if getattr(commit, "author_date", None) else None,
                "author_email": getattr(author, "email", "unknown@example.com"),
                "files": files,
            }
        )

    return mined


def mine_incremental(
    commits: list[dict] | None,
    last_processed_commit_sha: str | None,
    repository_path: str | None = None,
) -> list[dict]:
    if commits is None:
        if not repository_path:
            raise ValueError("repository_path is required when commits are not provided")
        commits = load_repository_commits(repository_path)

    if not commits:
        return []

    if not last_processed_commit_sha:
        return commits

    found_checkpoint = False
    unseen: list[dict] = []
    for commit in commits:
        if found_checkpoint:
            unseen.append(commit)
            continue

        if commit.get("sha") == last_processed_commit_sha:
            found_checkpoint = True

    if not found_checkpoint:
        return commits

    return unseen
