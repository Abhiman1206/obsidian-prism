import pytest
from pathlib import Path

from loan_agents.runtime.redaction import redact_secret
from loan_agents.runtime.settings import load_cors_allowed_origins, load_settings


@pytest.fixture(autouse=True)
def disable_dotenv_auto_load(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RUNTIME_DOTENV", "0")


def test_missing_llm_api_key_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(ValueError):
        load_settings()


def test_settings_default_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "secret-key")
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("MAX_RETRIES", raising=False)
    monkeypatch.delenv("BACKOFF_MIN_SECONDS", raising=False)
    monkeypatch.delenv("BACKOFF_MAX_SECONDS", raising=False)
    monkeypatch.delenv("REQUESTS_PER_MINUTE", raising=False)

    settings = load_settings()
    assert settings.LLM_MODEL == "gemini-3-flash-preview"
    assert settings.LOG_LEVEL == "INFO"
    assert settings.MAX_RETRIES == 5
    assert settings.BACKOFF_MIN_SECONDS == 4.0
    assert settings.BACKOFF_MAX_SECONDS == 30.0
    assert settings.REQUESTS_PER_MINUTE == 15


def test_redaction_masks_non_empty_values() -> None:
    assert redact_secret("super-secret") == "***REDACTED***"


def test_default_cors_allowed_origins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)

    origins = load_cors_allowed_origins()

    assert origins == ("http://localhost:5173",)


def test_invalid_cors_origin_raises_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "localhost:5173")

    with pytest.raises(ValueError):
        load_cors_allowed_origins()


def test_settings_load_from_dotenv_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        "LLM_API_KEY=dotenv-secret\nLLM_MODEL=gemini-dotenv\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("RUNTIME_DOTENV", "1")
    monkeypatch.setenv("RUNTIME_DOTENV_PATH", str(dotenv))
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    settings = load_settings()

    assert settings.LLM_API_KEY == "dotenv-secret"
    assert settings.LLM_MODEL == "gemini-dotenv"
