"""Runtime execution safeguards for retries, backoff, timeout, and rate limits."""

from collections import deque
from dataclasses import dataclass, field
import time
from typing import Any, Callable

from loan_agents.runtime.settings import RuntimeSettings


@dataclass
class InMemoryRateLimiter:
    requests_per_minute: int
    _request_times: deque[float] = field(default_factory=deque)

    def allow_request(self, now_seconds: float) -> bool:
        if self.requests_per_minute <= 0:
            return False
        window_start = now_seconds - 60.0
        while self._request_times and self._request_times[0] <= window_start:
            self._request_times.popleft()
        if len(self._request_times) >= self.requests_per_minute:
            return False
        self._request_times.append(now_seconds)
        return True


@dataclass(frozen=True)
class RuntimeExecutionPolicy:
    max_retries: int
    backoff_multiplier: float
    backoff_min_seconds: float
    backoff_max_seconds: float
    requests_per_minute: int
    run_timeout_seconds: float
    rate_limiter: InMemoryRateLimiter | None = None

    @classmethod
    def from_settings(cls, settings: RuntimeSettings) -> "RuntimeExecutionPolicy":
        return cls(
            max_retries=settings.MAX_RETRIES,
            backoff_multiplier=settings.BACKOFF_MULTIPLIER,
            backoff_min_seconds=settings.BACKOFF_MIN_SECONDS,
            backoff_max_seconds=settings.BACKOFF_MAX_SECONDS,
            requests_per_minute=settings.REQUESTS_PER_MINUTE,
            run_timeout_seconds=settings.RUN_TIMEOUT_SECONDS,
            rate_limiter=InMemoryRateLimiter(settings.REQUESTS_PER_MINUTE),
        )


@dataclass(frozen=True)
class ExecutionResult:
    value: Any
    retry_count: int
    duration_ms: int


class PolicyExecutionError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        failure_category: str,
        retry_count: int,
        stage: str,
        correlation_id: str,
    ) -> None:
        super().__init__(message)
        self.failure_category = failure_category
        self.retry_count = retry_count
        self.stage = stage
        self.correlation_id = correlation_id


class RateLimitExceededError(PolicyExecutionError):
    pass


class TimeoutExceededError(PolicyExecutionError, TimeoutError):
    pass


class ProviderExecutionError(PolicyExecutionError):
    pass


def execute_with_policy(
    callable_fn: Callable[[], Any],
    *,
    policy: RuntimeExecutionPolicy,
    correlation_id: str,
    stage: str,
    sleep_fn: Callable[[float], None] = time.sleep,
    now_fn: Callable[[], float] = time.monotonic,
) -> ExecutionResult:
    limiter = policy.rate_limiter or InMemoryRateLimiter(policy.requests_per_minute)
    if not limiter.allow_request(now_seconds=time.time()):
        raise RateLimitExceededError(
            "Rate limit exceeded",
            failure_category="rate_limit",
            retry_count=0,
            stage=stage,
            correlation_id=correlation_id,
        )

    retry_count = 0
    backoff_seconds = max(policy.backoff_min_seconds, 0.0)

    while True:
        started_at = now_fn()
        try:
            value = callable_fn()
        except Exception as exc:
            if retry_count >= policy.max_retries:
                raise ProviderExecutionError(
                    str(exc),
                    failure_category="provider",
                    retry_count=retry_count,
                    stage=stage,
                    correlation_id=correlation_id,
                ) from exc
            sleep_for = min(max(backoff_seconds, 0.0), max(policy.backoff_max_seconds, 0.0))
            sleep_fn(sleep_for)
            retry_count += 1
            backoff_seconds = min(
                max(policy.backoff_max_seconds, 0.0),
                max(policy.backoff_min_seconds, backoff_seconds * max(policy.backoff_multiplier, 1.0)),
            )
            continue

        elapsed_seconds = now_fn() - started_at
        if elapsed_seconds > policy.run_timeout_seconds:
            raise TimeoutExceededError(
                "Execution timeout exceeded",
                failure_category="timeout",
                retry_count=retry_count,
                stage=stage,
                correlation_id=correlation_id,
            )

        return ExecutionResult(
            value=value,
            retry_count=retry_count,
            duration_ms=max(0, int(elapsed_seconds * 1000)),
        )
