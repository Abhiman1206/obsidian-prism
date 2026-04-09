from app.infra.providers.github_client import GitHubClient
from app.infra.providers.gitlab_client import GitLabClient



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

    try:
        GitLabClient(timeout_seconds=-1)
        assert False, "Expected timeout validation failure"
    except ValueError:
        assert True
