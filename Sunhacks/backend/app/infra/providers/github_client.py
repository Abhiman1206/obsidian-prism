from collections.abc import Callable

from app.infra.providers.base import BaseProviderClient
from app.infra.secrets.provider_credentials import ProviderCredentialBundle


class GitHubClient(BaseProviderClient):
    def fetch_commits(self, fetch_page: Callable[[str | None], dict]) -> list[dict]:
        raw_commits = self.paginate(fetch_page, initial_cursor=None)
        commits: list[dict] = []

        for commit in raw_commits:
            commits.append(
                {
                    "sha": commit["sha"],
                    "authored_at": commit["authored_at"],
                    "author_email": commit["author_email"],
                    "files": [
                        {
                            "path": file_item["path"],
                            "additions": file_item.get("additions", 0),
                            "deletions": file_item.get("deletions", 0),
                        }
                        for file_item in commit.get("files", [])
                    ],
                }
            )

        return commits

    def fetch_commits_from_api(
        self,
        repository: str,
        token: str,
        request_get: Callable[[str, dict[str, str], dict | None], dict],
    ) -> list[dict]:
        headers = self.build_auth_headers(
            ProviderCredentialBundle(provider="github", token=token, scopes=("repo",))
        )

        def fetch_page(cursor: str | None) -> dict:
            params = {"cursor": cursor} if cursor is not None else None
            return request_get(f"/repos/{repository}/commits", headers, params)

        return self.fetch_commits(fetch_page)

    def fetch_operational_signals(
        self,
        repository: str,
        token: str,
        request_get: Callable[[str, dict[str, str], dict | None], dict],
    ) -> dict:
        headers = self.build_auth_headers(
            ProviderCredentialBundle(provider="github", token=token, scopes=("repo",))
        )
        issues = request_get(f"/repos/{repository}/issues", headers, None)
        deployments = request_get(f"/repos/{repository}/deployments", headers, None)

        return {
            "issue_opened_count": int(issues.get("open", 0)),
            "issue_closed_count": int(issues.get("closed", 0)),
            "deployment_count": int(deployments.get("count", 0)),
        }
