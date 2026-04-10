from collections.abc import Callable

from app.domain.ingestion.normalization import normalize_provider_payload
from app.domain.ingestion.provider_signals import extract_cadence_signals
from app.infra.providers.github_client import GitHubClient
from app.infra.providers.gitlab_client import GitLabClient


def _fetch_with_provider(provider: str, fetch_commits: Callable) -> list[dict]:
    if provider == "github":
        return GitHubClient().fetch_commits(fetch_commits)
    if provider == "gitlab":
        return GitLabClient().fetch_commits(fetch_commits)

    raise ValueError(f"Unsupported provider: {provider}")


def run_provider_ingestion(
    repository_id: str,
    provider: str,
    fetch_commits: Callable | None = None,
    cadence_source: dict | None = None,
    repository: str | None = None,
    token: str | None = None,
    request_get: Callable[[str, dict[str, str], dict | None], dict] | None = None,
) -> dict:
    if repository is not None and token is not None and request_get is not None:
        if provider == "github":
            client = GitHubClient()
        elif provider == "gitlab":
            client = GitLabClient()
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        commits = client.fetch_commits_from_api(repository=repository, token=token, request_get=request_get)
        cadence_source = client.fetch_operational_signals(repository=repository, token=token, request_get=request_get)
    else:
        if fetch_commits is None:
            raise ValueError("fetch_commits is required for callback ingestion mode")
        commits = _fetch_with_provider(provider, fetch_commits)

    canonical = normalize_provider_payload(
        repository_id=repository_id,
        provider=provider,
        commits=commits,
    )
    canonical["cadence"] = extract_cadence_signals(cadence_source)

    return canonical
