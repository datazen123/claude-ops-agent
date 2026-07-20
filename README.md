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

**Real, confirmed, currently-active evidence** (verified via
USASpending.gov, not just press): Peraton holds `W91QVN26FA218`, active
**right now** (Feb 2026 → Jan 2029), "USFK J6 IT Support Services (CJS)" -
plus five more named Peraton task orders covering USFK J6/JCC IT support
back to 2019 (`W91QVN20F0440` $47.4M, `W91QVN19F0246` $23.8M, and others).
Peraton, not any of the companies referenced elsewhere in this portfolio,
is the entrenched incumbent across USFK's core J6 IT ecosystem - the
category this repo demonstrates (IT ops/ticket triage) sits squarely
inside that scope. SAIC also holds an active USACISA-P network-operations
task order (`W91QVN25FA418`, $9.8M, through Apr 2026) in the adjacent
network-ops category.

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

## Tests + CI

`test_mock_crm.py` and `test_llm_client.py` cover everything deterministic
(the CRM round-trip, the provider guard clauses) - no API key or network
needed, safe to run in CI on every push:

```bash
pip install -r requirements-dev.txt
pytest -q
```

Writing these tests caught a real bug: `OpenAIClient` was importing the
`openai` package before checking for an API key, so on a machine without
`openai` installed (which is every machine this repo ships to, since that
provider is intentionally untested) it raised the wrong error type. Fixed
by reordering the guard clause - the kind of thing tests exist to catch.

## Security notes

- API keys are read from environment variables only, never hardcoded;
  `.env` is gitignored, `.env.example` ships placeholders only.
- Checked (2026-07-18): this repository's full git history contains zero
  occurrences of any real API key.
- Network calls to the Ask Sage gateway have explicit 30s timeouts to
  avoid an unbounded hang if the endpoint stalls.
- Per-ticket API failures are caught and logged rather than crashing the
  whole batch partway through.
- Dependencies are version-pinned with an upper bound
  (`>=X,<NEXT_MAJOR`), not left open-ended.

Built with [Claude Code](https://claude.com/claude-code).
