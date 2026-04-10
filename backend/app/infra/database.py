"""SQLite database infrastructure for persistent storage."""

from __future__ import annotations

import json
import os
import sqlite3
import threading
from pathlib import Path

_DB_LOCK = threading.Lock()
_CONNECTION: sqlite3.Connection | None = None


def _resolve_db_path() -> str:
    env_path = os.getenv("DATABASE_PATH")
    if env_path:
        return env_path
    return str(Path(__file__).resolve().parents[2] / "data" / "pei.db")


def get_db() -> sqlite3.Connection:
    """Return a thread-safe SQLite connection (singleton)."""
    global _CONNECTION
    if _CONNECTION is not None:
        return _CONNECTION

    with _DB_LOCK:
        if _CONNECTION is not None:
            return _CONNECTION
        db_path = _resolve_db_path()
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        _CONNECTION = conn
        return conn


def reset_connection() -> None:
    """Close and reset the DB connection (for testing)."""
    global _CONNECTION
    with _DB_LOCK:
        if _CONNECTION is not None:
            _CONNECTION.close()
            _CONNECTION = None


def init_db() -> None:
    """Create all tables if they don't exist."""
    conn = get_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            repository_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            branch TEXT,
            status TEXT NOT NULL DEFAULT 'queued',
            message TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS health_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            repository_id TEXT NOT NULL,
            component_id TEXT NOT NULL,
            score REAL NOT NULL,
            factors_json TEXT,
            contributors_json TEXT,
            measured_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS risk_forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            repository_id TEXT NOT NULL,
            component_id TEXT NOT NULL,
            horizon_days INTEGER NOT NULL DEFAULT 90,
            risk_probability REAL NOT NULL,
            confidence REAL NOT NULL,
            top_signals_json TEXT,
            forecasted_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS executive_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            report_id TEXT NOT NULL,
            executive_summary TEXT,
            cost_of_inaction REAL,
            report_json TEXT NOT NULL,
            generated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS lineage_records (
            lineage_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            repository_id TEXT NOT NULL,
            artifact_type TEXT NOT NULL,
            artifact_id TEXT NOT NULL,
            source_provider TEXT NOT NULL,
            source_locator TEXT NOT NULL,
            claim_ref TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS checkpoints (
            repository_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            last_sha TEXT,
            last_processed_at TEXT,
            status TEXT NOT NULL DEFAULT 'idle',
            PRIMARY KEY (repository_id, provider)
        );

        CREATE TABLE IF NOT EXISTS agent_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            agent_name TEXT NOT NULL,
            key TEXT NOT NULL,
            value_json TEXT NOT NULL,
            written_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_health_scores_run ON health_scores(run_id);
        CREATE INDEX IF NOT EXISTS idx_risk_forecasts_run ON risk_forecasts(run_id);
        CREATE INDEX IF NOT EXISTS idx_executive_reports_run ON executive_reports(run_id);
        CREATE INDEX IF NOT EXISTS idx_lineage_run ON lineage_records(run_id);
        CREATE INDEX IF NOT EXISTS idx_agent_memory_run ON agent_memory(run_id);
        """
    )
    conn.commit()
