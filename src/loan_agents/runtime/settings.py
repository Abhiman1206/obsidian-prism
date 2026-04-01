"""Typed non-interactive runtime settings."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimeSettings:
    LLM_API_KEY: str
    LLM_MODEL: str = "gemini-3-flash-preview"
    LOG_LEVEL: str = "INFO"
    MAX_RETRIES: int = 5
    BACKOFF_MULTIPLIER: float = 2.0
    BACKOFF_MIN_SECONDS: float = 4.0
    BACKOFF_MAX_SECONDS: float = 30.0
    REQUESTS_PER_MINUTE: int = 15
    RUN_TIMEOUT_SECONDS: float = 10.0
    CORS_ALLOWED_ORIGINS: tuple[str, ...] = ("http://localhost:5173",)


def _dotenv_enabled() -> bool:
    raw = os.getenv("RUNTIME_DOTENV", "1")
    return raw.strip().lower() not in {"0", "false", "no", "off"}


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _dotenv_candidates() -> tuple[Path, ...]:
    configured = os.getenv("RUNTIME_DOTENV_PATH")
    if configured is not None:
        value = configured.strip()
        if not value:
            return ()
        return (Path(value).expanduser(),)

    cwd_dotenv = Path.cwd() / ".env"
    root_dotenv = _project_root() / ".env"
    if cwd_dotenv == root_dotenv:
        return (cwd_dotenv,)

    return (cwd_dotenv, root_dotenv)


def _parse_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[len("export ") :].strip()

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue

        parsed = value.strip()
        if len(parsed) >= 2 and parsed[0] == parsed[-1] and parsed[0] in {'"', "'"}:
            parsed = parsed[1:-1]

        values[key] = parsed

    return values


def _load_dotenv_values() -> dict[str, str]:
    if not _dotenv_enabled():
        return {}

    for candidate in _dotenv_candidates():
        if candidate.exists() and candidate.is_file():
            return _parse_dotenv(candidate)

    return {}


def _env_value(name: str, default: str | None, dotenv: dict[str, str]) -> str | None:
    raw = os.getenv(name)
    if raw is not None:
        return raw
    return dotenv.get(name, default)


def _bool_env(name: str, default: bool, dotenv: dict[str, str]) -> bool:
    raw = _env_value(name, None, dotenv)
    if raw is None or not raw.strip():
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int, dotenv: dict[str, str]) -> int:
    raw = _env_value(name, None, dotenv)
    if raw is None or not raw.strip():
        return default
    return int(raw.strip())


def _float_env(name: str, default: float, dotenv: dict[str, str]) -> float:
    raw = _env_value(name, None, dotenv)
    if raw is None or not raw.strip():
        return default
    return float(raw.strip())


def _parse_allowed_origins(raw: str | None) -> tuple[str, ...]:
    if raw is None or not raw.strip():
        return ("http://localhost:5173",)

    values = [item.strip() for item in raw.split(",") if item.strip()]
    if not values:
        raise ValueError("CORS_ALLOWED_ORIGINS must include at least one origin")

    seen: list[str] = []
    for origin in values:
        if not (origin.startswith("http://") or origin.startswith("https://")):
            raise ValueError(
                "CORS_ALLOWED_ORIGINS entries must start with http:// or https://"
            )
        if origin not in seen:
            seen.append(origin)

    return tuple(seen)


def load_cors_allowed_origins() -> tuple[str, ...]:
    dotenv = _load_dotenv_values()
    return _parse_allowed_origins(_env_value("CORS_ALLOWED_ORIGINS", None, dotenv))


def load_cors_allow_credentials() -> bool:
    dotenv = _load_dotenv_values()
    return _bool_env("CORS_ALLOW_CREDENTIALS", False, dotenv)


def load_settings() -> RuntimeSettings:
    dotenv = _load_dotenv_values()

    api_key = (_env_value("LLM_API_KEY", "", dotenv) or "").strip()
    if not api_key:
        raise ValueError("Missing required setting: LLM_API_KEY")

    return RuntimeSettings(
        LLM_API_KEY=api_key,
        LLM_MODEL=(_env_value("LLM_MODEL", "gemini-3-flash-preview", dotenv) or "").strip()
        or "gemini-3-flash-preview",
        LOG_LEVEL=(_env_value("LOG_LEVEL", "INFO", dotenv) or "").strip() or "INFO",
        MAX_RETRIES=_int_env("MAX_RETRIES", 5, dotenv),
        BACKOFF_MULTIPLIER=_float_env("BACKOFF_MULTIPLIER", 2.0, dotenv),
        BACKOFF_MIN_SECONDS=_float_env("BACKOFF_MIN_SECONDS", 4.0, dotenv),
        BACKOFF_MAX_SECONDS=_float_env("BACKOFF_MAX_SECONDS", 30.0, dotenv),
        REQUESTS_PER_MINUTE=_int_env("REQUESTS_PER_MINUTE", 15, dotenv),
        RUN_TIMEOUT_SECONDS=_float_env("RUN_TIMEOUT_SECONDS", 10.0, dotenv),
        CORS_ALLOWED_ORIGINS=load_cors_allowed_origins(),
    )
