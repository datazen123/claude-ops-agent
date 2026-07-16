# claude-ops-agent

A small agentic automation demo: Claude reads incoming operations/support
tickets, decides category + priority, drafts a reply, and writes the
structured decision into a CRM via tool use.

All sample data (`data/sample_tickets.json`) is synthetic, written for this
demo - it is not from any real company, client, or system.

## Why this exists

Businesses that run lean ops teams (IT access requests, onboarding,
billing corrections, license renewals) spend a lot of time on triage that
follows a fairly predictable decision process. This demonstrates that
process handed to an LLM agent with tool use, instead of a human doing the
first pass by hand.

## Architecture

```
data/sample_tickets.json
        |
        v
   agent.py  --(Claude API, tool use)-->  mock_crm.py (SQLite)
        |
        v
  printed triage summary
```

- `llm_client.py` - thin provider adapter. Anthropic is the tested backend
  used throughout this repo. An OpenAI-compatible adapter is included for
  the same interface, but has **not** been run against a live OpenAI/Codex
  key in this repo - treat it as reference code until verified.
- `mock_crm.py` - stands in for a real CRM/ticketing API. Exposes
  `triage_ticket` as a Claude tool so the agent's decisions land somewhere
  structured, not just as printed text.
- `agent.py` - the triage loop: one Claude call per ticket, tool use to
  record the result, then a summary report read back from the mock CRM.

## Running it

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your own ANTHROPIC_API_KEY
export $(grep -v '^#' .env | xargs)
python agent.py
```

Built with [Claude Code](https://claude.com/claude-code).
