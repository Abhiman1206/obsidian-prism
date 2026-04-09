class CheckpointStore:
    def __init__(self) -> None:
        self._store: dict[tuple[str, str], dict] = {}

    def load(self, repository_id: str, provider: str) -> dict:
        key = (repository_id, provider)
        if key not in self._store:
            return {
                "repository_id": repository_id,
                "provider": provider,
                "last_processed_commit_sha": None,
                "last_processed_at": None,
                "status": "idle",
            }

        return self._store[key]

    def save(
        self,
        repository_id: str,
        provider: str,
        last_processed_commit_sha: str | None,
        last_processed_at: str | None,
        status: str,
    ) -> dict:
        payload = {
            "repository_id": repository_id,
            "provider": provider,
            "last_processed_commit_sha": last_processed_commit_sha,
            "last_processed_at": last_processed_at,
            "status": status,
        }
        self._store[(repository_id, provider)] = payload
        return payload
