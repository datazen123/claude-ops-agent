"""
Claude-powered ops ticket triage agent.

Reads synthetic support/ops tickets, has Claude classify + prioritize each one
and draft a reply, then has Claude call the `triage_ticket` tool to write the
decision into a mock CRM (SQLite). Prints a summary report at the end.

Run:
    export ANTHROPIC_API_KEY=sk-ant-...
    python agent.py
"""
from __future__ import annotations

import json
from pathlib import Path

import mock_crm
from llm_client import AnthropicClient

SYSTEM_PROMPT = """You are an operations triage assistant for a small services
company. For each support ticket you are given, decide a category and
priority, draft a short professional reply to the requester, and then call
the triage_ticket tool to record your decision. Always call the tool exactly
once per ticket - do not just describe the triage in text."""


def triage_one(client: AnthropicClient, ticket: dict) -> None:
    mock_crm.upsert_ticket(ticket["ticket_id"], ticket["subject"])

    messages = [
        {
            "role": "user",
            "content": (
                f"Ticket {ticket['ticket_id']}: {ticket['subject']}\n\n"
                f"{ticket['body']}"
            ),
        }
    ]

    response = client.create(
        system=SYSTEM_PROMPT,
        messages=messages,
        tools=[mock_crm.TRIAGE_TOOL_SCHEMA],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "triage_ticket":
            result = mock_crm.triage_ticket(**block.input)
            print(f"  -> {result}")
        elif block.type == "text" and block.text.strip():
            print(f"  (model note: {block.text.strip()[:120]})")


def main() -> None:
    mock_crm.reset_db()
    client = AnthropicClient()

    tickets = json.loads((Path(__file__).parent / "data" / "sample_tickets.json").read_text())

    print(f"Triaging {len(tickets)} synthetic tickets with Claude...\n")
    for ticket in tickets:
        print(f"[{ticket['ticket_id']}] {ticket['subject']}")
        triage_one(client, ticket)
        print()

    print("=== Triage summary (from mock CRM) ===")
    for row in mock_crm.list_tickets():
        print(f"{row['ticket_id']:>7} | {row['priority']:>6} | {row['category']:<16} | {row['subject']}")


if __name__ == "__main__":
    main()
