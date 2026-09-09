import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from config import settings


def init_db() -> None:
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(settings.db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS blocked_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                max_score REAL NOT NULL,
                threshold REAL NOT NULL,
                latency_ms REAL NOT NULL,
                payload TEXT NOT NULL,
                decision TEXT NOT NULL
            )
            """
        )
        conn.commit()


def log_event(
    *,
    endpoint: str,
    max_score: float,
    threshold: float,
    latency_ms: float,
    payload: str,
    decision: str,
) -> None:
    with sqlite3.connect(settings.db_path) as conn:
        conn.execute(
            """
            INSERT INTO blocked_events
            (timestamp, endpoint, max_score, threshold, latency_ms, payload, decision)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                endpoint,
                max_score,
                threshold,
                latency_ms,
                payload,
                decision,
            ),
        )
        conn.commit()


def fetch_events(limit: int = 500) -> list[dict]:
    with sqlite3.connect(settings.db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT * FROM blocked_events
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
