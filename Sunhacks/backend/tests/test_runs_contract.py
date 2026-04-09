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
    assert body["status"] in {"queued", "succeeded", "failed"}
    assert body["created_at"]


def test_get_run_status_returns_typed_response() -> None:
    client = TestClient(app)

    response = client.get("/api/runs/run-123")

    assert response.status_code == 200
    body = response.json()
    assert body["run_id"] == "run-123"
    assert body["status"] in {"queued", "running", "succeeded", "failed"}
    assert body["updated_at"]


def test_create_run_failure_is_reported_with_stage_diagnostics() -> None:
    client = TestClient(app)
    payload = {
        "repository_id": "repo-fail-health",
        "provider": "github",
        "branch": "main",
    }

    response = client.post("/api/runs", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "failed"

    status_response = client.get(f"/api/runs/{body['run_id']}")
    assert status_response.status_code == 200
    status_body = status_response.json()
    assert status_body["status"] == "failed"
    assert "health stage forced failure" in status_body["message"]


def test_subsequent_run_after_failure_is_accepted() -> None:
    client = TestClient(app)

    fail_payload = {
        "repository_id": "repo-fail-risk",
        "provider": "github",
        "branch": "main",
    }
    ok_payload = {
        "repository_id": "repo-healthy",
        "provider": "github",
        "branch": "main",
    }

    fail_response = client.post("/api/runs", json=fail_payload)
    assert fail_response.status_code == 200
    assert fail_response.json()["status"] == "failed"

    ok_response = client.post("/api/runs", json=ok_payload)
    assert ok_response.status_code == 200
    assert ok_response.json()["status"] == "succeeded"


def test_invalid_create_run_payload_returns_error_response() -> None:
    client = TestClient(app)

    response = client.post("/api/runs", json={"provider": "github"})

    assert response.status_code == 422
    body = response.json()
    assert "error_code" in body
    assert "message" in body
