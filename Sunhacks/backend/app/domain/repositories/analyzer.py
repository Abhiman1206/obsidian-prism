from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re

import httpx

from app.api.schemas.repository import (
    RepositoryAnalysisResponse,
    RepositoryCommitInsight,
    RepositoryHealthSummary,
    RepositoryLanguageStat,
)


class RepositoryAnalyzerService:
    def __init__(self, timeout_seconds: int = 15) -> None:
        self._timeout_seconds = timeout_seconds
        self._base_url = "https://api.github.com"
        self._cache_path = Path(__file__).resolve().parents[3] / "data" / "repository_analysis_cache.json"
        self._cache = self._load_cache()

    def analyze_repository(self, repository_url: str) -> RepositoryAnalysisResponse:
        slug = self._extract_github_slug(repository_url)

        cached = self._cache.get(slug)

        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "predictive-engineering-intelligence",
        }

        try:
            with httpx.Client(timeout=self._timeout_seconds, headers=headers) as client:
                repo_data, _ = self._get_json(client, f"/repos/{slug}")
                languages_payload, _ = self._get_json(client, f"/repos/{slug}/languages")
                commits_payload, _ = self._get_json(client, f"/repos/{slug}/commits", params={"per_page": 5})
                _, contributor_headers = self._get_json(
                    client,
                    f"/repos/{slug}/contributors",
                    params={"per_page": 1, "anon": "1"},
                )

                readme_status = client.get(f"{self._base_url}/repos/{slug}/readme")
                has_readme = readme_status.status_code == 200
        except Exception as exc:
            if cached:
                return RepositoryAnalysisResponse.model_validate(cached)
            raise RuntimeError(f"Unable to analyze repository at this moment: {exc}") from exc

        if not isinstance(repo_data, dict):
            raise RuntimeError("Unexpected repository response from GitHub")

        languages = self._build_language_stats(languages_payload)
        recent_commits = self._build_recent_commits(slug, commits_payload)
        contributor_count = self._extract_contributor_count(contributor_headers)

        score = self._compute_health_score(
            has_readme=has_readme,
            description=repo_data.get("description"),
            archived=bool(repo_data.get("archived", False)),
            stars=int(repo_data.get("stargazers_count", 0)),
            open_issues=int(repo_data.get("open_issues_count", 0)),
            topics=repo_data.get("topics", []),
            pushed_at=repo_data.get("pushed_at"),
        )

        analysis = RepositoryAnalysisResponse(
            provider="github",
            repository_url=f"https://github.com/{slug}",
            repository_name=slug,
            description=repo_data.get("description"),
            default_branch=str(repo_data.get("default_branch", "main")),
            stars=int(repo_data.get("stargazers_count", 0)),
            forks=int(repo_data.get("forks_count", 0)),
            watchers=int(repo_data.get("subscribers_count", 0)),
            open_issues=int(repo_data.get("open_issues_count", 0)),
            contributor_count=contributor_count,
            archived=bool(repo_data.get("archived", False)),
            has_readme=has_readme,
            primary_language=repo_data.get("language"),
            languages=languages,
            topics=self._sanitize_topics(repo_data.get("topics", [])),
            recent_commits=recent_commits,
            pushed_at=repo_data.get("pushed_at"),
            health=RepositoryHealthSummary(score=score, summary=self._build_health_summary(score)),
        )

        self._cache[slug] = analysis.model_dump()
        self._save_cache()
        return analysis

    def _extract_github_slug(self, repository_url: str) -> str:
        value = repository_url.strip()
        if not value:
            raise ValueError("Repository URL is required")

        if value.startswith("git@github.com:"):
            value = value.replace("git@github.com:", "", 1)
        elif value.startswith("https://github.com/"):
            value = value.replace("https://github.com/", "", 1)
        elif value.startswith("http://github.com/"):
            value = value.replace("http://github.com/", "", 1)

        value = value.strip("/")
        if value.endswith(".git"):
            value = value[:-4]

        if not re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", value):
            raise ValueError("Only GitHub repositories are currently supported")

        return value

    def _get_json(
        self,
        client: httpx.Client,
        path: str,
        params: dict[str, str | int] | None = None,
    ) -> tuple[dict | list, httpx.Headers]:
        response = client.get(f"{self._base_url}{path}", params=params)
        if response.status_code >= 400:
            detail = response.text or "GitHub API request failed"
            raise RuntimeError(f"GitHub API error ({response.status_code}): {detail}")
        return response.json(), response.headers

    def _build_language_stats(self, payload: dict | list) -> list[RepositoryLanguageStat]:
        if not isinstance(payload, dict):
            return []

        total_bytes = sum(int(v) for v in payload.values())
        if total_bytes <= 0:
            return []

        stats: list[RepositoryLanguageStat] = []
        for language, byte_count in sorted(payload.items(), key=lambda item: item[1], reverse=True):
            bytes_int = int(byte_count)
            percentage = round((bytes_int / total_bytes) * 100, 2)
            stats.append(
                RepositoryLanguageStat(language=str(language), bytes=bytes_int, percentage=percentage)
            )
        return stats

    def _build_recent_commits(self, slug: str, payload: dict | list) -> list[RepositoryCommitInsight]:
        if not isinstance(payload, list):
            return []

        commits: list[RepositoryCommitInsight] = []
        for item in payload[:5]:
            if not isinstance(item, dict):
                continue

            sha = str(item.get("sha", ""))
            commit_data = item.get("commit", {}) if isinstance(item.get("commit"), dict) else {}
            author_data = commit_data.get("author", {}) if isinstance(commit_data.get("author"), dict) else {}
            message = str(commit_data.get("message", "")).strip().splitlines()[0]

            commits.append(
                RepositoryCommitInsight(
                    sha=sha,
                    message=message,
                    author=str(author_data.get("name", "unknown")),
                    committed_at=str(author_data.get("date", "")),
                    url=f"https://github.com/{slug}/commit/{sha}",
                )
            )
        return commits

    def _extract_contributor_count(self, headers: httpx.Headers) -> int:
        link_header = headers.get("link", "")
        if not link_header:
            return 1

        match = re.search(r"[?&]page=(\d+)>; rel=\"last\"", link_header)
        if not match:
            return 1
        return int(match.group(1))

    def _sanitize_topics(self, payload: list | dict | None) -> list[str]:
        if not isinstance(payload, list):
            return []
        return [str(topic) for topic in payload if isinstance(topic, str)]

    def _compute_health_score(
        self,
        has_readme: bool,
        description: str | None,
        archived: bool,
        stars: int,
        open_issues: int,
        topics: list | dict | None,
        pushed_at: str | None,
    ) -> int:
        score = 0

        if has_readme:
            score += 15
        if description:
            score += 10
        if not archived:
            score += 20
        if stars > 0:
            score += 10
        if open_issues <= 50:
            score += 15
        elif open_issues <= 200:
            score += 8

        if isinstance(topics, list) and len(topics) > 0:
            score += 10

        if pushed_at:
            pushed_date = self._parse_iso_date(pushed_at)
            if pushed_date is not None:
                days_since_push = (datetime.now(timezone.utc) - pushed_date).days
                if days_since_push <= 30:
                    score += 20
                elif days_since_push <= 90:
                    score += 12
                elif days_since_push <= 180:
                    score += 6

        return max(0, min(100, score))

    def _build_health_summary(self, score: int) -> str:
        if score >= 80:
            return "Strong repository health with active maintenance signals."
        if score >= 60:
            return "Moderate repository health with room for process improvements."
        return "Low repository health. Maintenance, documentation, and issue hygiene need attention."

    def _parse_iso_date(self, value: str) -> datetime | None:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    def _load_cache(self) -> dict[str, dict]:
        if not self._cache_path.exists():
            return {}

        try:
            payload = json.loads(self._cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

        if not isinstance(payload, dict):
            return {}

        cache: dict[str, dict] = {}
        for key, value in payload.items():
            if isinstance(key, str) and isinstance(value, dict):
                cache[key] = value
        return cache

    def _save_cache(self) -> None:
        try:
            self._cache_path.parent.mkdir(parents=True, exist_ok=True)
            self._cache_path.write_text(json.dumps(self._cache, indent=2), encoding="utf-8")
        except OSError:
            return