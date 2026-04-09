def mine_incremental(commits: list[dict], last_processed_commit_sha: str | None) -> list[dict]:
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
