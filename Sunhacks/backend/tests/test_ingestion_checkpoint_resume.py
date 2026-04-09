from app.domain.ingestion.checkpoints import CheckpointStore



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
