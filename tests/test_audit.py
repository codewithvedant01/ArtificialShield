import os
import sqlite3
import pytest
from app.audit import init_db, log_event, fetch_events
from config import settings

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    # Use a temporary SQLite DB for testing
    test_db = tmp_path / "test_audit.db"
    original_db_path = settings.db_path
    settings.db_path = str(test_db)
    init_db()
    
    yield
    
    settings.db_path = original_db_path

def test_audit_log_schema_and_append():
    log_event(
        request_id="req-123",
        source_label="/test",
        max_score=0.9,
        offending_chunk="bad " * 300,  # Will be truncated
        threshold=0.85,
        action="blocked"
    )
    
    events = fetch_events()
    assert len(events) == 1
    event = events[0]
    
    assert event["request_id"] == "req-123"
    assert event["source_label"] == "/test"
    assert event["max_score"] == 0.9
    assert event["threshold"] == 0.85
    assert event["action"] == "blocked"
    assert len(event["offending_chunk"]) == 1024  # Truncated
    assert "timestamp" in event

    # Verify append-only - fetch directly from sqlite
    with sqlite3.connect(settings.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT request_id FROM audit_log")
        assert len(cursor.fetchall()) == 1

