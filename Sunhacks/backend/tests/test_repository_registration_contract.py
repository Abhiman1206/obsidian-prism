from fastapi.testclient import TestClient

from app.domain.repositories.connection_repository import REPOSITORY_CONNECTION_REPOSITORY
from app.main import app


def test_register_repository_returns_typed_response() -> None:
    client = TestClient(app)
    payload = {
        "provider": "github",
        "repository_url": "https://github.com/acme/platform",
        "repository_name": "acme/platform",
        "auth": {
            "provider": "github",
            "access_token": "token-123",
            "scopes": ["repo:read"],
        },
    }

    response = client.post("/api/repositories/register", json=payload, headers={"x-user-id": "user-1"})

    assert response.status_code == 200
    body = response.json()
    assert body["repository_id"]
    assert body["provider"] == "github"
    assert body["repository_url"] == payload["repository_url"]
    assert body["authorization_status"] in {"authorized", "pending", "failed"}
    assert body["authorization_reason"] in {
        "authorized_collaborator",
        "missing_repo_access",
        "token_invalid",
        "rate_limited",
        "transient_error",
        "provider_error",
    }
    assert body["run_ready"] is True
    assert body["owner_user_id"] == "user-1"

    connection = REPOSITORY_CONNECTION_REPOSITORY.get(body["repository_id"])
    assert connection is not None
    assert connection.repository_slug == "acme/platform"
    assert connection.token_ciphertext != payload["auth"]["access_token"]


def test_register_repository_supports_gitlab_provider() -> None:
    client = TestClient(app)
    payload = {
        "provider": "gitlab",
        "repository_url": "https://gitlab.com/acme/platform",
        "repository_name": "acme/platform",
        "auth": {
            "provider": "gitlab",
            "access_token": "token-abc",
            "scopes": ["api"],
        },
    }

    response = client.post("/api/repositories/register", json=payload, headers={"x-user-id": "user-2"})

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "gitlab"
    assert body["authorization_status"] == "authorized"
    assert body["authorization_reason"] == "authorized_collaborator"
    assert body["run_ready"] is True


def test_register_repository_validates_provider_and_payload() -> None:
    client = TestClient(app)
    payload = {
        "provider": "bitbucket",
        "repository_url": "https://bitbucket.org/acme/platform",
        "repository_name": "acme/platform",
        "auth": {
            "provider": "bitbucket",
            "access_token": "",
            "scopes": [],
        },
    }

    response = client.post("/api/repositories/register", json=payload)

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "validation_error"
    assert body["message"] == "Request validation failed"


def test_register_repository_rejects_missing_scope_payload() -> None:
    client = TestClient(app)
    payload = {
        "provider": "github",
        "repository_url": "https://github.com/acme/platform",
        "repository_name": "acme/platform",
        "auth": {
            "provider": "github",
            "access_token": "token-123",
            "scopes": [],
        },
    }

    response = client.post("/api/repositories/register", json=payload)

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "validation_error"
    assert body["message"] == "Request validation failed"


def test_register_repository_denies_noaccess_token_in_dev_mode() -> None:
    client = TestClient(app)
    payload = {
        "provider": "github",
        "repository_url": "https://github.com/acme/platform",
        "repository_name": "acme/platform",
        "auth": {
            "provider": "github",
            "access_token": "token-noaccess-demo",
            "scopes": ["repo:read"],
        },
    }

    response = client.post("/api/repositories/register", json=payload, headers={"x-user-id": "user-5"})

    assert response.status_code == 200
    body = response.json()
    assert body["authorization_status"] == "failed"
    assert body["authorization_reason"] == "missing_repo_access"
    assert body["run_ready"] is False
