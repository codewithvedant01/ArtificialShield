import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from config import settings


def init_db() -> None:
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(settings.db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                request_id TEXT NOT NULL,
                source_label TEXT NOT NULL,
                max_score REAL NOT NULL,
                offending_chunk TEXT NOT NULL,
                threshold REAL NOT NULL,
                action TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp 
            ON audit_log(timestamp)
            """
        )
        conn.commit()


def log_event(
    *,
    request_id: str,
    source_label: str,
    max_score: float,
    offending_chunk: str,
    threshold: float,
    action: str,
) -> None:
    # Truncate offending chunk if it's too large, don't store full payload
    truncated_chunk = offending_chunk[:1024]
    
    with sqlite3.connect(settings.db_path) as conn:
        conn.execute(
            """
            INSERT INTO audit_log
            (timestamp, request_id, source_label, max_score, offending_chunk, threshold, action)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                request_id,
                source_label,
                max_score,
                truncated_chunk,
                threshold,
                action,
            ),
        )
        conn.commit()


def fetch_events(limit: int = 500) -> list[dict]:
    with sqlite3.connect(settings.db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT * FROM audit_log
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
