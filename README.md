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
  used throughout this repo. OpenAI and Ask Sage adapters are included for
  the same interface, but have **not** been run against live credentials in
  this repo - treat them as reference code until verified.
- `mock_crm.py` - stands in for a real CRM/ticketing API. Exposes
  `triage_ticket` as a Claude tool so the agent's decisions land somewhere
  structured, not just as printed text.
- `agent.py` - the triage loop: one Claude call per ticket, tool use to
  record the result, then a summary report read back from the mock CRM.

## Real-data benchmark

`agent.py` above runs over 5 hand-written synthetic tickets - good for
showing the architecture, but small and clean. `benchmark.py` calls the
exact same triage logic (same system prompt, same `triage_ticket` tool
schema imported from `mock_crm.py` - not a reimplementation) against 25
real support tickets sampled from a public
[Hugging Face dataset](https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets)
of real/scraped-style multilingual customer support tickets, which ships an
actual `priority` label per ticket - a genuine accuracy check, not just a
robustness test.

**Actual measured result** (25 real English-language tickets, full detail
in `benchmark_report.md`):

| Metric | Result |
|---|---|
| Priority exact-match vs. the corpus's own label | 11/25 (44%) |

**The interesting part is *which* tickets missed, and in which direction.**
Several "mismatches" look like the corpus's own labels are the noisy ones,
not Claude's judgment: three healthcare-data-breach tickets labeled only
`medium`/`high` by the source data were classified `urgent` by Claude - a
defensible call given the subject matter, arguably more correct than the
label. Conversely, several marketing/brand-strategy inquiries labeled
`high` in the source were classified `low` - again a reasonable read for an
IT/ops triage context. Unlike the security-triage repo's benchmark (where
ground truth is an objective, official CVSS score), this corpus's priority
labels reflect whatever judgment calls its original human labelers made -
reported honestly as a real, imperfect real-world label, not a strict
ground truth.

```bash
python benchmark.py
```

## Deployment path

This demo calls the Anthropic API directly, which is the right choice for a
portfolio piece. A production version of this for a DoD-adjacent client would
run through whatever gateway that client has actually authorized - most
commonly:

- **[Ask Sage](https://www.asksage.ai/)** - the multi-model gateway built for
  the Defense Industrial Base specifically (not just uniformed personnel),
  IL5/IL6 authorized. `llm_client.py` includes an `AskSageClient` built from
  Ask Sage's [public API docs](https://github.com/Ask-Sage/AskSage-Open-Source-Community),
  though its documented `/query` endpoint has no tool-use parameter, so the
  CRM-sync pattern here would need a different integration shape there.
- **[GenAI.mil](https://www.war.gov/)** - CDAO's enterprise platform for
  military/civilian personnel (IL5/CUI), currently running Google Gemini,
  xAI Grok, and OpenAI's ChatGPT.
- **AWS GovCloud Bedrock** - Claude itself is available here at IL5+, and in
  the AWS Secret region at IL6, independent of direct-to-Anthropic contracts.

Worth knowing: Claude's status specifically at the DoD-contract level has
been politically contested since early 2026 (a designation dispute, since
partly reversed by a court injunction) - it isn't currently on GenAI.mil's
provider list. That's a reason to keep this adapter provider-agnostic rather
than assuming Claude is the delivery vehicle for any given client, not a
reason to avoid building with Claude.

## Running it

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your own ANTHROPIC_API_KEY
export $(grep -v '^#' .env | xargs)
python agent.py
```

Built with [Claude Code](https://claude.com/claude-code).
