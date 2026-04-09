from collections.abc import Callable

from app.infra.providers.base import BaseProviderClient


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
