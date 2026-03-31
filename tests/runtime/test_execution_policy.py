import pytest

from loan_agents.runtime.execution_policy import RuntimeExecutionPolicy, execute_with_policy


def test_execute_with_policy_retries_then_succeeds_with_capped_backoff() -> None:
    calls = {"count": 0}
    sleeps: list[float] = []
    time_values = iter([0.0, 0.0, 0.2, 0.2, 0.3, 0.3])

    def flaky_call() -> str:
        calls["count"] += 1
        if calls["count"] < 3:
            raise RuntimeError("provider transient")
        return "ok"

    policy = RuntimeExecutionPolicy(
        max_retries=3,
        backoff_multiplier=2.0,
        backoff_min_seconds=0.1,
        backoff_max_seconds=0.2,
        requests_per_minute=10,
        run_timeout_seconds=2.0,
    )

    result = execute_with_policy(
        flaky_call,
        policy=policy,
        correlation_id="corr-1",
        stage="document",
        sleep_fn=sleeps.append,
        now_fn=lambda: next(time_values),
    )

    assert result.value == "ok"
    assert result.retry_count == 2
    assert sleeps == [0.1, 0.2]


def test_execute_with_policy_raises_timeout_when_duration_exceeds_cap() -> None:
    policy = RuntimeExecutionPolicy(
        max_retries=0,
        backoff_multiplier=2.0,
        backoff_min_seconds=0.1,
        backoff_max_seconds=0.2,
        requests_per_minute=10,
        run_timeout_seconds=0.1,
    )
    time_values = iter([0.0, 0.5])

    def fast_result() -> str:
        return "ok"

    with pytest.raises(TimeoutError):
        execute_with_policy(
            fast_result,
            policy=policy,
            correlation_id="corr-2",
            stage="document",
            now_fn=lambda: next(time_values),
        )
