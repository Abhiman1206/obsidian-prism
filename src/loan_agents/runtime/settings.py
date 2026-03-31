"""Typed non-interactive runtime settings."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeSettings:
    LLM_API_KEY: str
    LLM_MODEL: str = "gemini-3-flash-preview"
    LOG_LEVEL: str = "INFO"
    MAX_RETRIES: int = 2
    BACKOFF_MULTIPLIER: float = 2.0
    BACKOFF_MIN_SECONDS: float = 0.1
    BACKOFF_MAX_SECONDS: float = 2.0
    REQUESTS_PER_MINUTE: int = 60
    RUN_TIMEOUT_SECONDS: float = 10.0


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    return int(raw.strip())


def _float_env(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    return float(raw.strip())


def load_settings() -> RuntimeSettings:
    api_key = os.getenv("LLM_API_KEY", "").strip()
    if not api_key:
        raise ValueError("Missing required setting: LLM_API_KEY")

    return RuntimeSettings(
        LLM_API_KEY=api_key,
        LLM_MODEL=os.getenv("LLM_MODEL", "gemini-3-flash-preview").strip() or "gemini-3-flash-preview",
        LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO").strip() or "INFO",
        MAX_RETRIES=_int_env("MAX_RETRIES", 2),
        BACKOFF_MULTIPLIER=_float_env("BACKOFF_MULTIPLIER", 2.0),
        BACKOFF_MIN_SECONDS=_float_env("BACKOFF_MIN_SECONDS", 0.1),
        BACKOFF_MAX_SECONDS=_float_env("BACKOFF_MAX_SECONDS", 2.0),
        REQUESTS_PER_MINUTE=_int_env("REQUESTS_PER_MINUTE", 60),
        RUN_TIMEOUT_SECONDS=_float_env("RUN_TIMEOUT_SECONDS", 10.0),
    )
