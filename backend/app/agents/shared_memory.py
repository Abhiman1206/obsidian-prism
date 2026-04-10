"""Shared Epistemic Memory — central scratchpad for multi-agent communication.

Each agent writes structured results here. The supervisor and downstream agents
read from the same memory to maintain a unified ground truth across the pipeline.
All writes are tagged with agent name and timestamp for auditability.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from app.infra.database import get_db


class EpistemicMemory:
    """Run-scoped shared memory for multi-agent orchestration."""

    def __init__(self, run_id: str, repository_id: str) -> None:
        self.run_id = run_id
        self.repository_id = repository_id
        self._state: dict[str, Any] = {}

    def write(self, agent_name: str, key: str, value: Any) -> None:
        """Write a value to shared memory, tagged with agent and timestamp."""
        self._state[key] = value

        # Persist to SQLite for post-mortem analysis
        try:
            conn = get_db()
            conn.execute(
                """INSERT INTO agent_memory (run_id, agent_name, key, value_json, written_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    self.run_id,
                    agent_name,
                    key,
                    json.dumps(value, default=str),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()
        except Exception:
            pass  # Memory write failure should not break pipeline

    def read(self, key: str, default: Any = None) -> Any:
        """Read a value from shared memory."""
        return self._state.get(key, default)

    def has(self, key: str) -> bool:
        """Check if a key exists in memory."""
        return key in self._state

    def keys(self) -> list[str]:
        """List all keys currently in memory."""
        return list(self._state.keys())

    def snapshot(self) -> dict[str, Any]:
        """Return a full JSON-serializable snapshot of current memory state."""
        return dict(self._state)
