from collections.abc import Callable

from app.domain.ingestion.checkpoints import CheckpointStore
from app.domain.ingestion.persistence import persist_ingestion_artifacts
from app.infra.miners.pydriller_miner import mine_incremental


def run_incremental_ingestion(
    repository_id: str,
    provider: str,
    commits: list[dict] | None,
    checkpoint_store: CheckpointStore,
    persist_records: Callable[[list[dict]], None],
    repository_path: str | None = None,
    mine_commits: Callable[..., list[dict]] = mine_incremental,
) -> dict:
    checkpoint_store.save(
        repository_id=repository_id,
        provider=provider,
        last_processed_commit_sha=checkpoint_store.load(repository_id, provider)["last_processed_commit_sha"],
        last_processed_at=checkpoint_store.load(repository_id, provider)["last_processed_at"],
        status="running",
    )

    checkpoint = checkpoint_store.load(repository_id, provider)
    last_sha = checkpoint.get("last_processed_commit_sha")
    mined_commits = mine_commits(
        commits=commits,
        last_processed_commit_sha=last_sha,
        repository_path=repository_path,
    )

    try:
        persist_ingestion_artifacts(mined_commits, persist_records)
    except Exception:
        checkpoint_store.save(
            repository_id=repository_id,
            provider=provider,
            last_processed_commit_sha=last_sha,
            last_processed_at=checkpoint.get("last_processed_at"),
            status="failed",
        )
        raise

    if mined_commits:
        tail = mined_commits[-1]
        checkpoint_store.save(
            repository_id=repository_id,
            provider=provider,
            last_processed_commit_sha=tail.get("sha"),
            last_processed_at=tail.get("authored_at"),
            status="complete",
        )
    else:
        checkpoint_store.save(
            repository_id=repository_id,
            provider=provider,
            last_processed_commit_sha=last_sha,
            last_processed_at=checkpoint.get("last_processed_at"),
            status="complete",
        )

    return {
        "repository_id": repository_id,
        "provider": provider,
        "mined_commits": mined_commits,
    }
