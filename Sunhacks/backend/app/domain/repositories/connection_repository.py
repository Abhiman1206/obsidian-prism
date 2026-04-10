from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json

from app.infra.database import get_db


@dataclass(frozen=True)
class RepositoryConnectionRecord:
    repository_id: str
    provider: str
    repository_url: str
    repository_slug: str
    owner_user_id: str | None
    token_owner_login: str | None
    provider_user_id: str | None
    token_ciphertext: str
    scopes: tuple[str, ...]
    authorization_status: str
    authorization_reason: str
    run_ready: bool
    created_at: str
    updated_at: str


class RepositoryConnectionRepository:
    def upsert(self, record: RepositoryConnectionRecord) -> None:
        conn = get_db()
        conn.execute(
            """
            INSERT INTO repository_connections
                        (repository_id, provider, repository_url, repository_slug, owner_user_id,
                         token_owner_login, provider_user_id, token_ciphertext, scopes_json,
                         authorization_status, authorization_reason, run_ready, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(repository_id) DO UPDATE SET
              provider = excluded.provider,
              repository_url = excluded.repository_url,
              repository_slug = excluded.repository_slug,
                            owner_user_id = excluded.owner_user_id,
                            token_owner_login = excluded.token_owner_login,
                            provider_user_id = excluded.provider_user_id,
              token_ciphertext = excluded.token_ciphertext,
              scopes_json = excluded.scopes_json,
              authorization_status = excluded.authorization_status,
                            authorization_reason = excluded.authorization_reason,
              run_ready = excluded.run_ready,
              updated_at = excluded.updated_at
            """,
            (
                record.repository_id,
                record.provider,
                record.repository_url,
                record.repository_slug,
                                record.owner_user_id,
                                record.token_owner_login,
                                record.provider_user_id,
                record.token_ciphertext,
                json.dumps(list(record.scopes)),
                record.authorization_status,
                                record.authorization_reason,
                1 if record.run_ready else 0,
                record.created_at,
                record.updated_at,
            ),
        )
        conn.commit()

    def get(self, repository_id: str) -> RepositoryConnectionRecord | None:
        conn = get_db()
        row = conn.execute(
            """
            SELECT repository_id, provider, repository_url, repository_slug,
                     owner_user_id, token_owner_login, provider_user_id,
                     token_ciphertext, scopes_json, authorization_status,
                     authorization_reason,
                   run_ready, created_at, updated_at
            FROM repository_connections
            WHERE repository_id = ?
            """,
            (repository_id,),
        ).fetchone()

        if row is None:
            return None

        scopes_raw = json.loads(row["scopes_json"] or "[]")
        scopes = tuple(str(scope) for scope in scopes_raw if isinstance(scope, str) and scope)
        return RepositoryConnectionRecord(
            repository_id=str(row["repository_id"]),
            provider=str(row["provider"]),
            repository_url=str(row["repository_url"]),
            repository_slug=str(row["repository_slug"]),
            owner_user_id=str(row["owner_user_id"]) if row["owner_user_id"] is not None else None,
            token_owner_login=str(row["token_owner_login"]) if row["token_owner_login"] is not None else None,
            provider_user_id=str(row["provider_user_id"]) if row["provider_user_id"] is not None else None,
            token_ciphertext=str(row["token_ciphertext"]),
            scopes=scopes,
            authorization_status=str(row["authorization_status"]),
            authorization_reason=str(row["authorization_reason"]),
            run_ready=bool(row["run_ready"]),
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
        )

    def get_for_owner(self, repository_id: str, owner_user_id: str) -> RepositoryConnectionRecord | None:
        record = self.get(repository_id)
        if record is None:
            return None
        if record.owner_user_id is None:
            return record
        if record.owner_user_id != owner_user_id:
            return None
        return record


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


REPOSITORY_CONNECTION_REPOSITORY = RepositoryConnectionRepository()
