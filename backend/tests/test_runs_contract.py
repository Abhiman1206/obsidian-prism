from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.workers.langchain_orchestrator import get_orchestration_engine


@pytest.fixture(autouse=True)
def _stub_orchestrator_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub the agent tools to avoid real network calls in tests."""
    from app.agents import data_mining_agent
    from app.agents import health_analyst_agent
    from app.agents import report_writer_agent

    # Stub Data Mining Agent to use fake commits without API calls
    original_data_mining_execute = data_mining_agent.DataMiningAgent.execute_deterministic

    def fake_data_mining_execute(self, memory):
        from app.domain.ingestion.normalization import normalize_provider_payload
        from app.domain.ingestion.provider_signals import extract_cadence_signals

        fake_commits = [
            {
                "sha": "abc123",
                "authored_at": "2026-01-10T12:00:00Z",
                "author_email": "engineer@example.com",
                "files": [
                    {"path": "backend/app/main.py", "additions": 30, "deletions": 4},
                    {"path": "backend/app/workers/provider_ingestion.py", "additions": 10, "deletions": 2},
                ],
            },
            {
                "sha": "def456",
                "authored_at": "2026-01-11T12:00:00Z",
                "author_email": "reviewer@example.com",
                "files": [
                    {"path": "backend/app/workers/risk_forecasting.py", "additions": 20, "deletions": 8},
                ],
            },
        ]

        canonical = normalize_provider_payload(
            repository_id=memory.repository_id,
            provider=memory.read("provider", "github"),
            commits=fake_commits,
        )
        cadence = extract_cadence_signals({"issue_opened_count": 4, "issue_closed_count": 5, "deployment_count": 6})

        memory.write(self.name, "raw_commits", fake_commits)
        memory.write(self.name, "canonical_payload", canonical)
        memory.write(self.name, "cadence_signals", cadence)
        memory.write(self.name, "churn", canonical.get("churn", []))

        return {"status": "complete", "agent": self.name, "mode": "deterministic", "commit_count": 2}

    monkeypatch.setattr(data_mining_agent.DataMiningAgent, "execute_deterministic", fake_data_mining_execute)
    monkeypatch.setattr(data_mining_agent.DataMiningAgent, "execute", lambda self, mem, task="": fake_data_mining_execute(self, mem))

    # Stub Health Analyst to skip file fetching / Radon
    original_health_execute = health_analyst_agent.HealthAnalystAgent.execute_deterministic

    def fake_health_execute(self, memory):
        raw_commits = memory.read("raw_commits", [])
        metric_rows = self._derive_fallback_metrics(raw_commits)
        volatility_map = {}
        health_rows = self._score_components(memory.run_id, memory.repository_id, metric_rows, volatility_map)

        memory.write(self.name, "metric_rows", metric_rows)
        memory.write(self.name, "volatility_map", volatility_map)
        memory.write(self.name, "health_rows", health_rows)

        return {"status": "complete", "agent": self.name, "mode": "deterministic", "components_analyzed": len(metric_rows)}

    monkeypatch.setattr(health_analyst_agent.HealthAnalystAgent, "execute_deterministic", fake_health_execute)
    monkeypatch.setattr(health_analyst_agent.HealthAnalystAgent, "execute", lambda self, mem, task="": fake_health_execute(self, mem))

    # Stub Report Writer LLM to use deterministic summary
    monkeypatch.setattr(report_writer_agent.ReportWriterAgent, "_generate_llm_summary",
                        lambda self, report, forecasts, translated: "AI summary generated for testing.")


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


def test_create_run_failure_is_reported_with_stage_diagnostics(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.agents import data_mining_agent

    def failing_execute(self, memory, task=""):
        raise RuntimeError("provider stage forced failure")

    monkeypatch.setattr(data_mining_agent.DataMiningAgent, "execute", failing_execute)

    client = TestClient(app)
    payload = {
        "repository_id": "repo-fail-provider",
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
    assert "provider stage forced failure" in status_body["message"]


def test_subsequent_run_after_failure_is_accepted(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.agents import data_mining_agent

    call_count = {"n": 0}

    def failing_then_ok_execute(self, memory, task=""):
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise RuntimeError("provider stage forced failure")
        # Second call — run normal deterministic path
        from app.domain.ingestion.normalization import normalize_provider_payload
        from app.domain.ingestion.provider_signals import extract_cadence_signals
        fake_commits = [{"sha": "ok-1", "authored_at": "2026-01-10T12:00:00Z", "author_email": "a@b.com", "files": [{"path": "x.py", "additions": 1, "deletions": 0}]}]
        canonical = normalize_provider_payload(repository_id=memory.repository_id, provider="github", commits=fake_commits)
        memory.write(self.name, "raw_commits", fake_commits)
        memory.write(self.name, "canonical_payload", canonical)
        memory.write(self.name, "cadence_signals", extract_cadence_signals({}))
        memory.write(self.name, "churn", canonical.get("churn", []))
        return {"status": "complete", "agent": self.name, "mode": "deterministic", "commit_count": 1}

    monkeypatch.setattr(data_mining_agent.DataMiningAgent, "execute", failing_then_ok_execute)

    client = TestClient(app)

    fail_response = client.post("/api/runs", json={"repository_id": "repo-fail-risk", "provider": "github", "branch": "main"})
    assert fail_response.status_code == 200
    assert fail_response.json()["status"] == "failed"

    ok_response = client.post("/api/runs", json={"repository_id": "repo-healthy", "provider": "github", "branch": "main"})
    assert ok_response.status_code == 200
    assert ok_response.json()["status"] == "succeeded"


def test_invalid_create_run_payload_returns_error_response() -> None:
    client = TestClient(app)

    response = client.post("/api/runs", json={"provider": "github"})

    assert response.status_code == 422
    body = response.json()
    assert "error_code" in body
    assert "message" in body


def test_orchestration_engine_reports_multi_agent() -> None:
    assert get_orchestration_engine() == "langchain-multi-agent"


def test_run_success_message_mentions_multi_agent_pipeline() -> None:
    client = TestClient(app)
    payload = {
        "repository_id": "repo-langchain-ready",
        "provider": "github",
        "branch": "main",
    }

    response = client.post("/api/runs", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "succeeded"

    status_response = client.get(f"/api/runs/{body['run_id']}")
    assert status_response.status_code == 200
    status_body = status_response.json()
    assert "multi-agent" in (status_body.get("message") or "").lower()
