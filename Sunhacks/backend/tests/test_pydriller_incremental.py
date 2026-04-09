from app.infra.miners.pydriller_miner import mine_incremental



def test_mine_incremental_returns_unseen_commits_after_checkpoint() -> None:
    commits = [
        {"sha": "a1", "authored_at": "2026-03-01T00:00:00Z", "files": []},
        {"sha": "b2", "authored_at": "2026-03-02T00:00:00Z", "files": []},
        {"sha": "c3", "authored_at": "2026-03-03T00:00:00Z", "files": []},
    ]

    unseen = mine_incremental(commits, last_processed_commit_sha="b2")

    assert [commit["sha"] for commit in unseen] == ["c3"]



def test_mine_incremental_returns_empty_when_no_new_commits() -> None:
    commits = [{"sha": "a1", "authored_at": "2026-03-01T00:00:00Z", "files": []}]

    unseen = mine_incremental(commits, last_processed_commit_sha="a1")

    assert unseen == []
