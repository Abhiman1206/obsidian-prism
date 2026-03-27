"""Typed non-interactive runtime settings."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeSettings:
    LLM_API_KEY: str
    LLM_MODEL: str = "gemini-3-flash-preview"
    LOG_LEVEL: str = "INFO"


def load_settings() -> RuntimeSettings:
    api_key = os.getenv("LLM_API_KEY", "").strip()
    if not api_key:
        raise ValueError("Missing required setting: LLM_API_KEY")

    return RuntimeSettings(
        LLM_API_KEY=api_key,
        LLM_MODEL=os.getenv("LLM_MODEL", "gemini-3-flash-preview").strip() or "gemini-3-flash-preview",
        LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO").strip() or "INFO",
    )
