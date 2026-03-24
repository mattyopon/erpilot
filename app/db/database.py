"""SQLite database layer for ERPilot.

Uses aiosqlite for async operations. Stores data as JSON blobs per entity type
for rapid prototyping. Production version would use proper relational schema.
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from typing import Any

DB_PATH = os.environ.get("DATABASE_PATH", "erpilot.db")


def _get_connection(db_path: str | None = None) -> sqlite3.Connection:
    """Get a synchronous SQLite connection."""
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str | None = None) -> None:
    """Initialize database tables."""
    conn = _get_connection(db_path)
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS fitgap_sessions (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                module_id TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );
            CREATE TABLE IF NOT EXISTS fitgap_reports (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                module_id TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );
            CREATE TABLE IF NOT EXISTS issues (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );
            CREATE TABLE IF NOT EXISTS risks (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );
            CREATE TABLE IF NOT EXISTS weekly_reports (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );
            CREATE TABLE IF NOT EXISTS test_suites (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );
            CREATE TABLE IF NOT EXISTS training_materials (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );
            CREATE TABLE IF NOT EXISTS meeting_minutes (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );
        """)
        conn.commit()
    finally:
        conn.close()


def _serialize(obj: Any) -> str:
    """Serialize a Pydantic model or dict to JSON string."""
    if hasattr(obj, "model_dump"):
        data = obj.model_dump()
    elif isinstance(obj, dict):
        data = obj
    else:
        data = obj
    return json.dumps(data, default=str, ensure_ascii=False)


def _deserialize(json_str: str) -> dict[str, Any]:
    """Deserialize JSON string to dict."""
    return json.loads(json_str)


# ---------------------------------------------------------------------------
# Generic CRUD operations
# ---------------------------------------------------------------------------
def save_entity(
    table: str,
    entity_id: str,
    data: Any,
    project_id: str | None = None,
    module_id: str | None = None,
    db_path: str | None = None,
) -> None:
    """Save an entity to the database."""
    conn = _get_connection(db_path)
    try:
        now = datetime.utcnow().isoformat()
        json_data = _serialize(data)
        if module_id is not None:
            conn.execute(
                f"INSERT OR REPLACE INTO {table} (id, project_id, module_id, data, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (entity_id, project_id, module_id, json_data, now),
            )
        elif project_id is not None:
            conn.execute(
                f"INSERT OR REPLACE INTO {table} (id, project_id, data, created_at) "
                "VALUES (?, ?, ?, ?)",
                (entity_id, project_id, json_data, now),
            )
        else:
            conn.execute(
                f"INSERT OR REPLACE INTO {table} (id, data, created_at) "
                "VALUES (?, ?, ?)",
                (entity_id, json_data, now),
            )
        conn.commit()
    finally:
        conn.close()


def get_entity(
    table: str,
    entity_id: str,
    db_path: str | None = None,
) -> dict[str, Any] | None:
    """Get an entity by ID."""
    conn = _get_connection(db_path)
    try:
        row = conn.execute(
            f"SELECT data FROM {table} WHERE id = ?", (entity_id,)
        ).fetchone()
        if row is None:
            return None
        return _deserialize(row["data"])
    finally:
        conn.close()


def list_entities(
    table: str,
    project_id: str | None = None,
    db_path: str | None = None,
) -> list[dict[str, Any]]:
    """List entities, optionally filtered by project_id."""
    conn = _get_connection(db_path)
    try:
        if project_id is not None:
            rows = conn.execute(
                f"SELECT data FROM {table} WHERE project_id = ? ORDER BY created_at DESC",
                (project_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                f"SELECT data FROM {table} ORDER BY created_at DESC"
            ).fetchall()
        return [_deserialize(row["data"]) for row in rows]
    finally:
        conn.close()


def delete_entity(
    table: str,
    entity_id: str,
    db_path: str | None = None,
) -> bool:
    """Delete an entity by ID. Returns True if deleted."""
    conn = _get_connection(db_path)
    try:
        cursor = conn.execute(
            f"DELETE FROM {table} WHERE id = ?", (entity_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def count_entities(
    table: str,
    project_id: str | None = None,
    db_path: str | None = None,
) -> int:
    """Count entities in a table."""
    conn = _get_connection(db_path)
    try:
        if project_id is not None:
            row = conn.execute(
                f"SELECT COUNT(*) as cnt FROM {table} WHERE project_id = ?",
                (project_id,),
            ).fetchone()
        else:
            row = conn.execute(
                f"SELECT COUNT(*) as cnt FROM {table}"
            ).fetchone()
        return row["cnt"] if row else 0
    finally:
        conn.close()
