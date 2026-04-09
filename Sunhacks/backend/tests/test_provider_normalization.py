from app.infra.providers.github_client import GitHubClient
from app.infra.providers.gitlab_client import GitLabClient
from app.domain.ingestion.normalization import normalize_provider_payload



def test_github_adapter_collects_paginated_commit_batches_with_files() -> None:
    def fetch_page(cursor: str | None) -> dict:
        if cursor is None:
            return {
                "items": [
                    {
                        "sha": "abc123",
                        "authored_at": "2026-04-01T00:00:00Z",
                        "author_email": "dev@acme.com",
                        "files": [{"path": "a.py", "additions": 10, "deletions": 2}],
                    }
                ],
                "next_cursor": "page-2",
            }
        return {
            "items": [
                {
                    "sha": "def456",
                    "authored_at": "2026-04-02T00:00:00Z",
                    "author_email": "dev2@acme.com",
                    "files": [{"path": "b.py", "additions": 4, "deletions": 1}],
                }
            ],
            "next_cursor": None,
        }

    client = GitHubClient(timeout_seconds=5)
    commits = client.fetch_commits(fetch_page)

    assert len(commits) == 2
    assert commits[0]["sha"] == "abc123"
    assert commits[1]["files"][0]["path"] == "b.py"



def test_gitlab_adapter_collects_paginated_commit_batches_with_files() -> None:
    def fetch_page(cursor: int | None) -> dict:
        if cursor is None:
            return {
                "items": [
                    {
                        "id": "gl-1",
                        "authored_at": "2026-04-03T00:00:00Z",
                        "author_email": "dev@acme.com",
                        "files": [{"new_path": "c.py", "additions": 5, "deletions": 0}],
                    }
                ],
                "next_cursor": 2,
            }
        return {
            "items": [
                {
                    "id": "gl-2",
                    "authored_at": "2026-04-04T00:00:00Z",
                    "author_email": "dev2@acme.com",
                    "files": [{"new_path": "d.py", "additions": 3, "deletions": 2}],
                }
            ],
            "next_cursor": None,
        }

    client = GitLabClient(timeout_seconds=5)
    commits = client.fetch_commits(fetch_page)

    assert len(commits) == 2
    assert commits[0]["sha"] == "gl-1"
    assert commits[1]["files"][0]["path"] == "d.py"



def test_provider_clients_enforce_timeout_boundaries() -> None:
    try:
        GitHubClient(timeout_seconds=0)
        assert False, "Expected timeout validation failure"
    except ValueError:
        assert True


def test_normalize_provider_payload_builds_canonical_commit_and_churn_shape() -> None:
    payload = normalize_provider_payload(
        repository_id="repo-acme-platform",
        provider="github",
        commits=[
            {
                "sha": "abc123",
                "authored_at": "2026-04-01T00:00:00Z",
                "author_email": "dev@acme.com",
                "files": [
                    {"path": "a.py", "additions": 10, "deletions": 2},
                    {"path": "b.py", "additions": 5, "deletions": 1},
                ],
            },
            {
                "sha": "def456",
                "authored_at": "2026-04-02T00:00:00Z",
                "author_email": "dev@acme.com",
                "files": [{"path": "c.py", "additions": 2, "deletions": 0}],
            },
        ],
    )

    assert payload["repository_id"] == "repo-acme-platform"
    assert payload["provider"] == "github"
    assert len(payload["commits"]) == 2
    assert payload["commits"][0]["files_changed"] == 2
    assert payload["commits"][0]["insertions"] == 15
    assert payload["commits"][0]["deletions"] == 3
    assert payload["churn"][0]["contributor"] == "dev@acme.com"
    assert payload["churn"][0]["commits_last_30d"] == 2
    assert payload["churn"][0]["files_touched_last_30d"] == 3

    try:
        GitLabClient(timeout_seconds=-1)
        assert False, "Expected timeout validation failure"
    except ValueError:
        assert True
