from collections.abc import Callable
from urllib.parse import quote

from app.infra.providers.base import BaseProviderClient
from app.infra.secrets.provider_credentials import ProviderCredentialBundle


class GitLabClient(BaseProviderClient):
    def fetch_commits(self, fetch_page: Callable[[int | None], dict]) -> list[dict]:
        raw_commits = self.paginate(fetch_page, initial_cursor=None)
        commits: list[dict] = []

        for commit in raw_commits:
            commits.append(
                {
                    "sha": commit["id"],
                    "authored_at": commit["authored_at"],
                    "author_email": commit["author_email"],
                    "files": [
                        {
                            "path": file_item.get("new_path", file_item.get("old_path", "")),
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
            ProviderCredentialBundle(provider="gitlab", token=token, scopes=("api",))
        )
        project_path = quote(repository, safe="")

        def fetch_page(cursor: int | None) -> dict:
            params = {"page": cursor} if cursor is not None else None
            return request_get(f"/projects/{project_path}/repository/commits", headers, params)

        return self.fetch_commits(fetch_page)

    def fetch_operational_signals(
        self,
        repository: str,
        token: str,
        request_get: Callable[[str, dict[str, str], dict | None], dict],
    ) -> dict:
        headers = self.build_auth_headers(
            ProviderCredentialBundle(provider="gitlab", token=token, scopes=("api",))
        )
        project_path = quote(repository, safe="")
        issues = request_get(f"/projects/{project_path}/issues", headers, None)
        deployments = request_get(f"/projects/{project_path}/deployments", headers, None)

        return {
            "issue_opened_count": int(issues.get("open", 0)),
            "issue_closed_count": int(issues.get("closed", 0)),
            "deployment_count": int(deployments.get("count", 0)),
        }
