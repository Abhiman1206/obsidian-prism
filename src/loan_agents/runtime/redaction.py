"""Secret redaction helpers used by runtime logs and errors."""


def redact_secret(value: str) -> str:
    if value:
        return "***REDACTED***"
    return value
