import pytest

from loan_agents.runtime.execution_policy import InMemoryRateLimiter, RuntimeExecutionPolicy, execute_with_policy


def test_rate_limiter_blocks_burst_and_recovers_after_window() -> None:
    limiter = InMemoryRateLimiter(requests_per_minute=2)

    assert limiter.allow_request(now_seconds=0.0) is True
    assert limiter.allow_request(now_seconds=1.0) is True
    assert limiter.allow_request(now_seconds=2.0) is False
    assert limiter.allow_request(now_seconds=61.0) is True


def test_execute_with_policy_raises_when_rate_limited() -> None:
    policy = RuntimeExecutionPolicy(
        max_retries=0,
        backoff_multiplier=2.0,
        backoff_min_seconds=0.1,
        backoff_max_seconds=0.2,
        requests_per_minute=0,
        run_timeout_seconds=1.0,
    )

    with pytest.raises(RuntimeError):
        execute_with_policy(
            lambda: "ok",
            policy=policy,
            correlation_id="corr-rate",
            stage="document",
        )
