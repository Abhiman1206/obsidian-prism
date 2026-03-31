"""Secret redaction helpers used by runtime logs and errors."""

from typing import Any


SENSITIVE_KEY_PARTS = ("secret", "token", "password", "api_key")


def redact_secret(value: str) -> str:
    if value:
        return "***REDACTED***"
    return value


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(part in lowered for part in SENSITIVE_KEY_PARTS)


def _is_sensitive_value(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    stripped = value.strip()
    return bool(stripped) and stripped.lower().startswith("bearer ")


def redact_value(value: Any) -> Any:
    if isinstance(value, dict):
        return redact_mapping(value)
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    if _is_sensitive_value(value):
        return "***REDACTED***"
    return value


def redact_mapping(payload: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in payload.items():
        if _is_sensitive_key(key):
            redacted[key] = "***REDACTED***"
            continue
        redacted[key] = redact_value(value)
    return redacted
