from app.domain.ingestion.provider_signals import extract_cadence_signals
from app.workers.provider_ingestion import run_provider_ingestion



def test_extract_cadence_returns_counts_when_available() -> None:
    cadence = extract_cadence_signals(
        {
            "issue_opened_count": 8,
            "issue_closed_count": 5,
            "deployment_count": 3,
            "period_start": "2026-03-01",
            "period_end": "2026-03-31",
        }
    )

    assert cadence["issue_opened_count"] == 8
    assert cadence["issue_closed_count"] == 5
    assert cadence["deployment_count"] == 3
    assert cadence["period_start"] == "2026-03-01"
    assert cadence["period_end"] == "2026-03-31"



def test_extract_cadence_returns_zero_defaults_when_missing() -> None:
    cadence = extract_cadence_signals(None)

    assert cadence["issue_opened_count"] == 0
    assert cadence["issue_closed_count"] == 0
    assert cadence["deployment_count"] == 0
    assert cadence["period_start"] is None
    assert cadence["period_end"] is None


def test_run_provider_ingestion_dispatches_and_returns_canonical_payload() -> None:
    def github_fetch(cursor: str | None) -> dict:
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
                "next_cursor": None,
            }
        return {"items": [], "next_cursor": None}

    payload = run_provider_ingestion(
        repository_id="repo-acme-platform",
        provider="github",
        fetch_commits=github_fetch,
        cadence_source={
            "issue_opened_count": 2,
            "issue_closed_count": 1,
            "deployment_count": 1,
            "period_start": "2026-03-01",
            "period_end": "2026-03-31",
        },
    )

    assert payload["repository_id"] == "repo-acme-platform"
    assert payload["provider"] == "github"
    assert payload["commits"][0]["commit_sha"] == "abc123"
    assert payload["cadence"]["deployment_count"] == 1


def test_github_client_fetches_operational_signals_for_pr_issue_and_deployment_counts() -> None:
    from app.infra.providers.github_client import GitHubClient

    def request_get(endpoint: str, headers: dict[str, str], params: dict | None = None) -> dict:
        if endpoint.endswith("/issues"):
            return {"open": 5, "closed": 3}
        if endpoint.endswith("/deployments"):
            return {"count": 2}
        return {"items": [], "next_cursor": None}

    signals = GitHubClient().fetch_operational_signals(
        repository="acme/platform",
        token="gh-token",
        request_get=request_get,
    )

    assert signals["issue_opened_count"] == 5
    assert signals["issue_closed_count"] == 3
    assert signals["deployment_count"] == 2


def test_run_provider_ingestion_supports_authenticated_runtime_mode() -> None:
    def request_get(endpoint: str, headers: dict[str, str], params: dict | None = None) -> dict:
        if endpoint.endswith("/commits"):
            return {
                "items": [
                    {
                        "sha": "abc123",
                        "authored_at": "2026-04-01T00:00:00Z",
                        "author_email": "dev@acme.com",
                        "files": [{"path": "a.py", "additions": 10, "deletions": 2}],
                    }
                ],
                "next_cursor": None,
            }
        if endpoint.endswith("/issues"):
            return {"open": 2, "closed": 1}
        if endpoint.endswith("/deployments"):
            return {"count": 1}
        return {"items": [], "next_cursor": None}

    payload = run_provider_ingestion(
        repository_id="repo-acme-platform",
        provider="github",
        repository="acme/platform",
        token="gh-token",
        request_get=request_get,
    )

    assert payload["provider"] == "github"
    assert payload["commits"][0]["commit_sha"] == "abc123"
    assert payload["cadence"]["issue_opened_count"] == 2
