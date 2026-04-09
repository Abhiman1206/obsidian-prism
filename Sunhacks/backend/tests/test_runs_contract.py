from fastapi.testclient import TestClient

from app.main import app


def test_create_run_returns_typed_response() -> None:
    client = TestClient(app)
    payload = {
        "repository_id": "repo-123",
        "provider": "github",
        "branch": "main",
    }

    response = client.post("/api/runs", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["run_id"]
    assert body["status"] in {"queued", "running", "succeeded", "failed"}
    assert body["created_at"]


def test_get_run_status_returns_typed_response() -> None:
    client = TestClient(app)

    response = client.get("/api/runs/run-123")

    assert response.status_code == 200
    body = response.json()
    assert body["run_id"] == "run-123"
    assert body["status"] in {"queued", "running", "succeeded", "failed"}
    assert body["updated_at"]


def test_invalid_create_run_payload_returns_error_response() -> None:
    client = TestClient(app)

    response = client.post("/api/runs", json={"provider": "github"})

    assert response.status_code == 422
    body = response.json()
    assert "error_code" in body
    assert "message" in body
