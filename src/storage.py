"""Small SQLite repository used by the Streamlit application."""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import sqlite3
from typing import Any

DB_PATH = Path(__file__).resolve().parents[1] / "quality_checker.db"


def _connect(path: Path = DB_PATH) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize(path: Path = DB_PATH) -> None:
    with _connect(path) as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY, invoice_number TEXT NOT NULL, kind TEXT NOT NULL,
            payload TEXT NOT NULL, created_at TEXT NOT NULL,
            UNIQUE(invoice_number, kind)
        );
        CREATE TABLE IF NOT EXISTS verifications (
            id INTEGER PRIMARY KEY, invoice_number TEXT NOT NULL, status TEXT NOT NULL,
            quality_score REAL NOT NULL, result TEXT NOT NULL, decision TEXT NOT NULL DEFAULT 'pending',
            reviewer_note TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_records_invoice ON records(invoice_number);
        CREATE INDEX IF NOT EXISTS idx_verifications_invoice ON verifications(invoice_number);
        """)


def upsert_record(kind: str, payload: dict[str, Any], path: Path = DB_PATH) -> None:
    invoice = str(payload["invoice_number"]).strip()
    now = datetime.now().isoformat(timespec="seconds")
    with _connect(path) as db:
        db.execute("""INSERT INTO records(invoice_number, kind, payload, created_at) VALUES(?,?,?,?)
            ON CONFLICT(invoice_number, kind) DO UPDATE SET payload=excluded.payload, created_at=excluded.created_at""",
            (invoice, kind, json.dumps(payload, default=str), now))


def list_records(kind: str, path: Path = DB_PATH) -> list[dict[str, Any]]:
    with _connect(path) as db:
        rows = db.execute("SELECT payload FROM records WHERE kind=? ORDER BY created_at DESC", (kind,)).fetchall()
    return [json.loads(row["payload"]) for row in rows]


def get_record(invoice_number: str, kind: str, path: Path = DB_PATH) -> dict[str, Any] | None:
    with _connect(path) as db:
        row = db.execute("SELECT payload FROM records WHERE invoice_number=? AND kind=?", (invoice_number, kind)).fetchone()
    return json.loads(row["payload"]) if row else None


def save_verification(invoice_number: str, result: dict[str, Any], path: Path = DB_PATH) -> int:
    with _connect(path) as db:
        cursor = db.execute("INSERT INTO verifications(invoice_number,status,quality_score,result,created_at) VALUES(?,?,?,?,?)",
            (invoice_number, result["status"], result["quality_score"], json.dumps(result), datetime.now().isoformat(timespec="seconds")))
        return int(cursor.lastrowid)


def list_verifications(path: Path = DB_PATH) -> list[dict[str, Any]]:
    with _connect(path) as db:
        rows = db.execute("SELECT * FROM verifications ORDER BY created_at DESC").fetchall()
    return [{**dict(row), "result": json.loads(row["result"])} for row in rows]


def decide(verification_id: int, decision: str, note: str, path: Path = DB_PATH) -> None:
    if decision not in {"approved", "rejected", "pending"}:
        raise ValueError("Invalid review decision.")
    with _connect(path) as db:
        db.execute("UPDATE verifications SET decision=?, reviewer_note=? WHERE id=?", (decision, note.strip(), verification_id))
