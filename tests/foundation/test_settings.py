import pytest

from loan_agents.runtime.redaction import redact_secret
from loan_agents.runtime.settings import load_settings


def test_missing_llm_api_key_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(ValueError):
        load_settings()


def test_settings_default_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "secret-key")
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    settings = load_settings()
    assert settings.LLM_MODEL == "gemini-3-flash-preview"
    assert settings.LOG_LEVEL == "INFO"


def test_redaction_masks_non_empty_values() -> None:
    assert redact_secret("super-secret") == "***REDACTED***"
