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
    fetch_commits: Callable,
    cadence_source: dict | None = None,
) -> dict:
    commits = _fetch_with_provider(provider, fetch_commits)
    canonical = normalize_provider_payload(
        repository_id=repository_id,
        provider=provider,
        commits=commits,
    )
    canonical["cadence"] = extract_cadence_signals(cadence_source)

    return canonical
