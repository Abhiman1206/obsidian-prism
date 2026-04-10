from app.infra.database import get_db


class CheckpointStore:
    def load(self, repository_id: str, provider: str) -> dict:
        conn = get_db()
        row = conn.execute(
            "SELECT * FROM checkpoints WHERE repository_id = ? AND provider = ?",
            (repository_id, provider),
        ).fetchone()
        if row is None:
            return {
                "repository_id": repository_id,
                "provider": provider,
                "last_processed_commit_sha": None,
                "last_processed_at": None,
                "status": "idle",
            }
        return {
            "repository_id": row["repository_id"],
            "provider": row["provider"],
            "last_processed_commit_sha": row["last_sha"],
            "last_processed_at": row["last_processed_at"],
            "status": row["status"],
        }

    def save(
        self,
        repository_id: str,
        provider: str,
        last_processed_commit_sha: str | None,
        last_processed_at: str | None,
        status: str,
    ) -> dict:
        conn = get_db()
        conn.execute(
            """INSERT INTO checkpoints (repository_id, provider, last_sha, last_processed_at, status)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(repository_id, provider)
               DO UPDATE SET last_sha=excluded.last_sha,
                             last_processed_at=excluded.last_processed_at,
                             status=excluded.status""",
            (repository_id, provider, last_processed_commit_sha, last_processed_at, status),
        )
        conn.commit()
        return {
            "repository_id": repository_id,
            "provider": provider,
            "last_processed_commit_sha": last_processed_commit_sha,
            "last_processed_at": last_processed_at,
            "status": status,
        }
