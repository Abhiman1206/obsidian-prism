"""Structured error envelope helpers for runtime responses."""

from typing import Any


def build_failure(status: str, mode: str, code: str, message: str) -> dict[str, Any]:
    return {
        "status": status,
        "decision": "undetermined",
        "mode": mode,
        "stages": {},
        "error": {
            "code": code,
            "message": message,
        },
    }
