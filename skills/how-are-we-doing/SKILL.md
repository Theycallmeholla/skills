---
name: how-are-we-doing
description: Per-business snapshot of how a website and its digital footprint are performing and which way they are moving. Covers Search Console clicks, rankings, near-miss queries and movers, Google indexing of every sitemap URL, GA4, Microsoft Clarity (scroll depth, dead/rage clicks, heatmaps), Google Business Profile, CRM leads (GoHighLevel), and Domain Rating. Leads with what changed since the last snapshot and names the few opportunities worth acting on. Each business gets a profile, made once by auto-discovering existing access plus a short setup questionnaire. Use when someone asks "how are we doing", "how is the site doing", "any leads", "are we growing", "what changed", "SEO check", "analytics check", "check GSC", "where are people clicking", "heatmaps", "digital footprint", or "what should we work on next". Also use to set up a new business ("add a client", "set up how-are-we-doing for X") and when a dated watchlist read comes due.
---

# How are we doing

Give one honest, fast read of how a business is showing up online and **which way it's moving**. Every number is measured and labeled with its source and window, or it says "not measured". Opportunities come from the data and must pass the buyer test.

This skill works for any business. Everything specific to one business lives in its **profile folder**, never in this skill.

`<skill dir>` below means the folder this SKILL.md is in.

## Where profiles live

`<project root>/.claude/how-are-we-doing/<business-slug>/`, where the project root is whatever directory Claude is running in:

```
profile.json     sources + pointers to credentials (never values), market, people, noise
.env             this business's API keys (from templates/.env.example); never committed
notes.md         business context the reader must apply (why certain numbers mislead)
watchlist.md     dated reads, parked changes, standing checks
history/         one snapshot per run (<date>.json), the basis for "what changed"
custom/          optional scripts named in profile.json "commands"
clarity-calls.json  Clarity API call ledger (10/day limit)
```

**Pick the profile:**
1. List `.claude/how-are-we-doing/*/profile.json` under the current directory.
2. If exactly one exists, use it.
3. If several exist, use the one the user named. If they didn't name one, ask with AskUserQuestion.
4. If none exists, or the user asks to add a business, run **Setup**.

**Keep profiles private.** They hold keys (`.env`), client contact IDs and names. Before writing one inside a git repo, check `git check-ignore <path>`. If it isn't ignored, add `.claude/how-are-we-doing/` to that repo's `.gitignore` and tell the user you did. Deploy scripts that rsync through `.gitignore` also depend on this. Never copy a profile into the skills repo.

## Setup (first run for a business)

Read `references/setup.md` and follow it. In short:
1. Run `scripts/discover.py --root . --domain <domain>`. It finds the access that already exists: env key names, which Search Console and GA4 properties each service-account key can read, the site's tags (GA4, GTM, Clarity), sitemaps, and MCP servers.
2. Ask only what discovery couldn't answer, with AskUserQuestion (the questionnaire is in `references/setup.md`).
3. Write `profile.json` (start from `templates/profile.example.json`), `notes.md` and `watchlist.md`.
4. Run `--check` (below) until nothing the user wants is broken. Show the table.
5. Do a first pull, show it, and confirm the profile is right.

## Connections: what it needs and what works

```bash
python3 <skill dir>/scripts/pull.py --profile <profile dir> --check
```

It lists every source this skill can read, with what that source needs and its status. Each status comes from one real test call, not from a key merely existing:
`OK` connected · `WARN` to confirm (MCP- or browser-based, which the script can't call) · `FAIL` broken, with the exact error and the fix · `--` not set up, with how to add it.
Clarity isn't live-tested by default (10 calls/day); add `--test-clarity` to spend one. For a `WARN` GA4-via-MCP row, make one tiny report call yourself (1 day, `sessions`) and report the result.
Show this table whenever the user asks what's connected, what the skill needs, or why a source is missing.


## Run

**0. Check.** Run `--check` first. A broken source is reported up front, not discovered halfway through the report. If everything is OK, say so in one line and move on.

**1. Pull, all in one parallel batch.** Tell the user it takes about 10 s to 3 min; the first indexing pass is the slow part.

- **Script:** `python3 <skill dir>/scripts/pull.py --profile <profile dir>`. Add `--days 7` for "this week" or `--no-inspect` to skip indexing. It prints a summary that opens with **SINCE LAST SNAPSHOT** and saves `history/<today>.json`. A failed source prints `ERROR` with the exact message: quote it, mark that source unavailable, and continue.
- **GA4 when the profile says `method: "mcp"`:** make the calls listed in `references/sources.md` → GA4 with the named MCP tool, current window vs prior, exact dates.
- **Right now (optional):** if a GA4 MCP has a realtime report tool, show active users from the last 30 minutes. That's the only truly real-time number. GSC lags 2–3 days and Clarity's API covers the last 1–3 days.
- **Browser reads** listed under `browser` in the profile (Clarity heatmaps, Google Business Profile, anything else behind a login): follow `references/sources.md`. Only do these when the profile says a login exists, and only for pages the pull flagged or the user asked about. Heatmaps are the evidence for *why* a page's numbers look the way they do. Screenshots of every page are not the point.

**2. Read it.** Apply `references/reading.md` (the general traps) and then the profile's `notes.md` (this business's traps). notes.md wins when they conflict.

**3. Opportunities.** At most 3, each passing every test in `references/reading.md`. Fewer is fine. "Nothing worth changing this week" is a valid answer.

**4. Ask what only the owner knows.** Unconfirmed leads, unknown tool users, anything the data can't settle: one AskUserQuestion each. Record answers in `profile.json` (`people.confirmed_real` / `people.internal_contact_ids`, with a short label).

**5. Report.** Use the template in `references/reading.md`: TL;DR, **what changed**, a scoreboard with sources, opportunities, due reads, and what's not measured. If the user will share it, offer an artifact page in one line.

**6. Close the loop.** Update `watchlist.md`: move read items to Done with their result, and add anything this run parked, with a date and baseline. The snapshot in `history/` is the record, so don't write a memory per run. Save a memory only for a durable, cross-session fact about the business (a new access gotcha, a confirmed lead source).

## Rules that never bend

- **Measured or "not measured".** No estimates next to measured numbers, no "probably", no invented ratios. If something is unknown, say where it would be measured.
- **Counts at small volume.** 49 → 50 clicks is "flat". Don't turn single-digit changes into percentages.
- **Leads come from the system of record** (the CRM or calendar), never from GA4 events alone. GA4 misses some and counts tests.
- **Never guess an API, endpoint, or UI path.** `references/sources.md` holds what's been verified. Anything else gets checked against vendor docs first.
- **Credentials:** read values only inside scripts, from the pointer in the profile. Never print, log, or store a value, and never ask for one in chat. The user pastes keys into the profile's `.env` themselves.
