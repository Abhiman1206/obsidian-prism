"""Test configuration — ensures in-memory SQLite for all tests."""

import os
import pytest

# Force in-memory SQLite for testing
os.environ["DATABASE_PATH"] = ":memory:"


@pytest.fixture(autouse=True)
def _init_test_db():
    """Initialize a fresh in-memory database before each test."""
    from app.infra.database import reset_connection, init_db
    reset_connection()
    init_db()
    yield
    reset_connection()
