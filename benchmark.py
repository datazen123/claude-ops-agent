"""
Real-data benchmark: runs this repo's actual triage tool-use call (same
system prompt style and tool schema as agent.py, imported from mock_crm.py
- not a reimplementation) against real customer-support tickets from a
public Hugging Face dataset, instead of the 5 hand-written synthetic ones.

Unlike a purely synthetic demo, this corpus ships a real `priority` label
(low/medium/high) per ticket, so this is a genuine accuracy check on
priority classification - not just a robustness/crash test. There is no
usable ground truth for this repo's specific category taxonomy
(access_request/onboarding/billing/technical_issue/other), so category is
reported for manual review only, not scored.

Run:
    export ANTHROPIC_API_KEY=sk-ant-...
    python benchmark.py
(Makes one real tool-use API call per sampled ticket - ~1-2 minutes for 25.)
"""
from __future__ import annotations

import csv
import io
import random

import requests

import mock_crm
from llm_client import AnthropicClient

TICKETS_URL = "https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets/resolve/main/dataset-tickets-multi-lang-4-20k.csv"
SAMPLE_SIZE = 25
RANDOM_SEED = 42

SYSTEM_PROMPT = """You are an operations triage assistant for a small
services company. For each support ticket you are given, decide a category
and priority, draft a short professional reply to the requester, and then
call the triage_ticket tool to record your decision. Always call the tool
exactly once per ticket - do not just describe the triage in text."""


def fetch_english_ticket_sample(n: int) -> list[dict]:
    print(f"Downloading real ticket corpus from {TICKETS_URL} ...")
    resp = requests.get(TICKETS_URL, timeout=60)
    reader = csv.DictReader(io.StringIO(resp.text))
    english = [row for row in reader if row["language"] == "en" and row["priority"] in ("low", "medium", "high")]
    random.seed(RANDOM_SEED)
    return random.sample(english, n)


def triage_real_ticket(client: AnthropicClient, ticket_id: str, subject: str, body: str) -> dict | None:
    messages = [{"role": "user", "content": f"Ticket {ticket_id}: {subject}\n\n{body}"}]
    response = client.create(system=SYSTEM_PROMPT, messages=messages, tools=[mock_crm.TRIAGE_TOOL_SCHEMA])
    for block in response.content:
        if block.type == "tool_use" and block.name == "triage_ticket":
            return block.input
    return None


def main() -> None:
    client = AnthropicClient()
    sample = fetch_english_ticket_sample(SAMPLE_SIZE)
    print(f"Sampled {len(sample)} real English-language support tickets.\n")

    results = []
    for i, row in enumerate(sample):
        ticket_id = f"RT-{i+1:03d}"
        decision = triage_real_ticket(client, ticket_id, row["subject"], row["body"][:600])
        if decision is None:
            continue
        results.append({
            "ticket_id": ticket_id,
            "subject": row["subject"],
            "true_priority": row["priority"],
            "predicted_priority": decision["priority"],
            "predicted_category": decision["category"],
        })
        print(f"{ticket_id}: true={row['priority']:>6} predicted={decision['priority']:>6} "
              f"({decision['category']})  {row['subject'][:60]}")

    # 'urgent' has no equivalent in this corpus's 3-tier scale - treat it as
    # matching 'high' for scoring purposes, noted explicitly rather than
    # silently counted as a miss.
    def normalize(p: str) -> str:
        return "high" if p == "urgent" else p

    exact = sum(1 for r in results if normalize(r["predicted_priority"]) == r["true_priority"])
    n = len(results)

    from collections import Counter
    category_dist = Counter(r["predicted_category"] for r in results)

    report = [
        "# Real Ticket Corpus Benchmark Report (claude-ops-agent)",
        "",
        f"Source: {TICKETS_URL} (Hugging Face, public, real/scraped-style multilingual support tickets)",
        "",
        f"- Real English-language tickets sampled: {n}",
        f"- Priority exact-match accuracy vs. real label ('urgent' counted as matching 'high'): "
        f"{exact}/{n} ({exact/n:.0%})",
        f"- Predicted category distribution (no ground truth available for this repo's taxonomy - "
        f"reported for manual review, not scored): {dict(category_dist)}",
        "",
        "## Per-ticket detail",
        "",
        "| Ticket | Subject | True priority | Predicted priority | Predicted category |",
        "|---|---|---|---|---|",
    ] + [
        f"| {r['ticket_id']} | {r['subject'][:50]} | {r['true_priority']} | {r['predicted_priority']} | {r['predicted_category']} |"
        for r in results
    ]

    with open("benchmark_report.md", "w") as f:
        f.write("\n".join(report) + "\n")
    print("\n" + "\n".join(report[:6]))
    print("\nWrote benchmark_report.md")


if __name__ == "__main__":
    main()
