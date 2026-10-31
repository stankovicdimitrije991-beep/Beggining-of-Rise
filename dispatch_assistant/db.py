"""SQLite storage for loads and the error log."""

import json
import sqlite3
from datetime import datetime, timezone

from .models import RateCon

STATUSES = ["needs_review", "approved", "booked", "in_transit", "delivered", "invoiced", "rejected"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS loads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    source_file TEXT,
    extractor TEXT,
    status TEXT NOT NULL,
    data TEXT NOT NULL,
    missing TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    source_file TEXT,
    message TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    def add_load(self, rc: RateCon, missing: list[str], source_file: str, extractor: str) -> int:
        now = _now()
        cur = self.conn.execute(
            "INSERT INTO loads (created_at, updated_at, source_file, extractor, status, data, missing)"
            " VALUES (?, ?, ?, ?, 'needs_review', ?, ?)",
            (now, now, source_file, extractor, rc.model_dump_json(), json.dumps(missing)),
        )
        self.conn.commit()
        return cur.lastrowid

    def update_load(self, load_id: int, rc: RateCon, missing: list[str], notes: str) -> None:
        self.conn.execute(
            "UPDATE loads SET data = ?, missing = ?, notes = ?, updated_at = ? WHERE id = ?",
            (rc.model_dump_json(), json.dumps(missing), notes, _now(), load_id),
        )
        self.conn.commit()

    def set_status(self, load_id: int, status: str) -> None:
        if status not in STATUSES:
            raise ValueError(f"Unknown status: {status}")
        self.conn.execute(
            "UPDATE loads SET status = ?, updated_at = ? WHERE id = ?", (status, _now(), load_id)
        )
        self.conn.commit()

    def get_load(self, load_id: int) -> dict | None:
        row = self.conn.execute("SELECT * FROM loads WHERE id = ?", (load_id,)).fetchone()
        return self._row(row) if row else None

    def list_loads(self, query: str = "", status: str = "") -> list[dict]:
        sql, args = "SELECT * FROM loads WHERE 1=1", []
        if status:
            sql += " AND status = ?"
            args.append(status)
        if query:
            sql += " AND (data LIKE ? OR source_file LIKE ?)"
            args += [f"%{query}%", f"%{query}%"]
        rows = self.conn.execute(sql + " ORDER BY id DESC", args).fetchall()
        return [self._row(r) for r in rows]

    def log_error(self, source_file: str, message: str) -> None:
        self.conn.execute(
            "INSERT INTO errors (created_at, source_file, message) VALUES (?, ?, ?)",
            (_now(), source_file, message),
        )
        self.conn.commit()

    def list_errors(self, limit: int = 50) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM errors ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def _row(row: sqlite3.Row) -> dict:
        d = dict(row)
        d["load"] = RateCon.model_validate_json(d.pop("data"))
        d["missing"] = json.loads(d["missing"])
        return d
