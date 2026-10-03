# Reading the pull and writing the report

## General traps (then apply the profile's notes.md, which wins)

- **Lead with the derivative.** Open with what changed: since the last snapshot (KPI lines) and this window vs the prior one (movers). A number with nothing to compare to is context, not news.
- **Small numbers get counts, not percentages.** Under ~100 events, write "49 → 50" and call it flat. Only call it a trend if the weekly series shows the same direction for 3+ weeks.
- **Where the clicks come from.** Compare all-country totals with the profile's market row. A gain that sits entirely outside the market isn't a buyer gain.
- **Position is impression-weighted.** Average position gets *worse* when a page starts showing for new, broader queries. Check clicks and the top query before calling it a ranking loss.
- **Bots.** GA4 Direct traffic with very low engagement, and Clarity 1–3 s sessions from datacenter countries, are usually bots. Report their size as noise. Judge growth on organic search and on engaged sessions.
- **Leads come from the system of record.** Count leads in the CRM or calendar. GA4 conversion events are funnel signals, not a lead count.
- **Classify people before counting.** Tests and staff inflate every early-stage funnel. Only `real` people count. `unconfirmed` gets asked about, never counted either way.
- **Windows differ by source.** GSC ends 2–3 days ago, GA4 ends yesterday, Clarity covers the last 1–3 days. Print each window. Never divide one source's number by another's.
- **Not measured is an answer.** Won deals with no status set, a source that errored, a login that doesn't exist: say "not measured" and where it would be measured.

## Report template

```
**Dashboard:** <artifact link>

**TL;DR:** <one sentence: which way things are moving, and whether anything produced leads>

**What changed**
- <since last snapshot: the KPI lines that moved, with dates>
- <this window vs prior: biggest movers, each tied to a page or query>

| Measure | Now | Prior | Source, window |
|---|---|---|---|
| Leads (real people) | | | CRM, dates |
| Search clicks (all / market) | | | GSC, dates |
| Organic sessions / engaged | | | GA4 Organic Search, dates |
| <only the rows that moved or matter this run; the dashboard carries the rest> | | | |

**Due reads:** watchlist items that are due, each with its result
**Not measured:** <list>

Next: run `/what-next` to turn this into a ranked plan.
```

Keep the table short: the dashboard is the full scoreboard. Drop rows for sources the profile doesn't have. Don't show empty rows. Never add a "do this" list; that is what-next's job.
