from app.domain.ingestion.checkpoints import CheckpointStore
from app.workers.incremental_ingestion import run_incremental_ingestion



def test_checkpoint_store_persists_and_loads_marker() -> None:
    store = CheckpointStore()

    store.save(
        repository_id="repo-acme-platform",
        provider="github",
        last_processed_commit_sha="abc123",
        last_processed_at="2026-04-01T00:00:00Z",
        status="complete",
    )

    checkpoint = store.load("repo-acme-platform", "github")

    assert checkpoint["last_processed_commit_sha"] == "abc123"
    assert checkpoint["status"] == "complete"



def test_checkpoint_store_defaults_to_empty_state() -> None:
    store = CheckpointStore()

    checkpoint = store.load("repo-acme-platform", "gitlab")

    assert checkpoint["last_processed_commit_sha"] is None
    assert checkpoint["last_processed_at"] is None
    assert checkpoint["status"] == "idle"


def test_incremental_worker_advances_checkpoint_after_successful_persist() -> None:
    store = CheckpointStore()

    commits = [
        {"sha": "a1", "authored_at": "2026-03-01T00:00:00Z", "files": []},
        {"sha": "b2", "authored_at": "2026-03-02T00:00:00Z", "files": []},
    ]

    persisted = []

    def persist(records: list[dict]) -> None:
        persisted.extend(records)

    result = run_incremental_ingestion(
        repository_id="repo-acme-platform",
        provider="github",
        commits=commits,
        checkpoint_store=store,
        persist_records=persist,
    )

    assert len(result["mined_commits"]) == 2
    assert persisted[-1]["sha"] == "b2"
    checkpoint = store.load("repo-acme-platform", "github")
    assert checkpoint["last_processed_commit_sha"] == "b2"
    assert checkpoint["status"] == "complete"


def test_incremental_worker_does_not_advance_checkpoint_on_persist_failure() -> None:
    store = CheckpointStore()
    commits = [{"sha": "a1", "authored_at": "2026-03-01T00:00:00Z", "files": []}]

    def persist(_records: list[dict]) -> None:
        raise RuntimeError("persist failed")

    try:
        run_incremental_ingestion(
            repository_id="repo-acme-platform",
            provider="github",
            commits=commits,
            checkpoint_store=store,
            persist_records=persist,
        )
        assert False, "Expected runtime error from persistence failure"
    except RuntimeError:
        checkpoint = store.load("repo-acme-platform", "github")
        assert checkpoint["last_processed_commit_sha"] is None
        assert checkpoint["status"] == "failed"


def test_incremental_worker_can_run_with_repository_path_mode() -> None:
    store = CheckpointStore()
    persisted = []

    def persist(records: list[dict]) -> None:
        persisted.extend(records)

    result = run_incremental_ingestion(
        repository_id="repo-acme-platform",
        provider="github",
        commits=None,
        repository_path="./repo",
        checkpoint_store=store,
        persist_records=persist,
        mine_commits=lambda **_kwargs: [
            {"sha": "a1", "authored_at": "2026-03-01T00:00:00Z", "files": []},
            {"sha": "b2", "authored_at": "2026-03-02T00:00:00Z", "files": []},
        ],
    )

    assert len(result["mined_commits"]) == 2
    assert persisted[-1]["sha"] == "b2"
    checkpoint = store.load("repo-acme-platform", "github")
    assert checkpoint["last_processed_commit_sha"] == "b2"
