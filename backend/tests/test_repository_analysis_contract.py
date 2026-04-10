from fastapi.testclient import TestClient

from app.api.routes import repositories
from app.main import app


def test_repository_analysis_returns_structured_response() -> None:
    class _MockAnalyzer:
        def analyze_repository(self, repository_url: str) -> dict:
            assert repository_url == "https://github.com/Abhiman1206/AI_APP.git"
            return {
                "provider": "github",
                "repository_url": "https://github.com/Abhiman1206/AI_APP",
                "repository_name": "Abhiman1206/AI_APP",
                "description": "AI repository",
                "default_branch": "main",
                "stars": 12,
                "forks": 4,
                "watchers": 3,
                "open_issues": 1,
                "contributor_count": 5,
                "archived": False,
                "has_readme": True,
                "primary_language": "Python",
                "languages": [
                    {"language": "Python", "bytes": 1000, "percentage": 80.0},
                ],
                "topics": ["ai"],
                "recent_commits": [
                    {
                        "sha": "abc123",
                        "message": "Add inference flow",
                        "author": "abhiman",
                        "committed_at": "2026-04-10T00:00:00Z",
                        "url": "https://github.com/Abhiman1206/AI_APP/commit/abc123",
                    }
                ],
                "pushed_at": "2026-04-10T00:00:00Z",
                "health": {
                    "score": 84,
                    "summary": "Strong repository health with active maintenance signals.",
                },
            }

    repositories._analyzer = _MockAnalyzer()
    client = TestClient(app)

    response = client.post(
        "/api/repositories/analyze",
        json={"repository_url": "https://github.com/Abhiman1206/AI_APP.git"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "github"
    assert body["repository_name"] == "Abhiman1206/AI_APP"
    assert {"score", "summary"}.issubset(body["health"].keys())
    assert isinstance(body["languages"], list)
    assert isinstance(body["recent_commits"], list)


def test_repository_analysis_validates_payload() -> None:
    client = TestClient(app)

    response = client.post("/api/repositories/analyze", json={"repository_url": ""})

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "validation_error"
    assert body["message"] == "Request validation failed"
