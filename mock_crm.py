"""
Tiny SQLite-backed stand-in for a real CRM/ticketing API.

Exposes a couple of functions as Claude tool-use targets so the agent in
agent.py can actually write structured results somewhere, instead of just
printing text.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "crm.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    category TEXT,
    priority TEXT,
    status TEXT DEFAULT 'open',
    draft_response TEXT
);
"""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(SCHEMA)
    return conn


def reset_db() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    _connect().close()


def upsert_ticket(ticket_id: str, subject: str) -> None:
    conn = _connect()
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO tickets (ticket_id, subject) VALUES (?, ?)",
            (ticket_id, subject),
        )
    conn.close()


def triage_ticket(ticket_id: str, category: str, priority: str, draft_response: str) -> str:
    """Tool target: record the agent's triage decision for a ticket."""
    conn = _connect()
    with conn:
        conn.execute(
            """
            UPDATE tickets
            SET category = ?, priority = ?, draft_response = ?, status = 'triaged'
            WHERE ticket_id = ?
            """,
            (category, priority, draft_response, ticket_id),
        )
    conn.close()
    return f"Ticket {ticket_id} triaged as {priority}/{category}."


def list_tickets() -> list[dict]:
    conn = _connect()
    rows = conn.execute(
        "SELECT ticket_id, subject, category, priority, status, draft_response FROM tickets"
    ).fetchall()
    conn.close()
    cols = ["ticket_id", "subject", "category", "priority", "status", "draft_response"]
    return [dict(zip(cols, row)) for row in rows]


TRIAGE_TOOL_SCHEMA = {
    "name": "triage_ticket",
    "description": "Record the triage decision (category, priority, draft response) for a support ticket in the CRM.",
    "input_schema": {
        "type": "object",
        "properties": {
            "ticket_id": {"type": "string"},
            "category": {
                "type": "string",
                "enum": ["access_request", "onboarding", "billing", "technical_issue", "other"],
            },
            "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
            "draft_response": {"type": "string", "description": "A short draft reply to send the requester."},
        },
        "required": ["ticket_id", "category", "priority", "draft_response"],
    },
}
