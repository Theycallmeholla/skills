# Reading the pull, picking opportunities, writing the report

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

## Opportunities: at most 3, each must pass all of these

1. **Buyer test.** Would the person behind this query or visit buy something this business sells (`business.what_it_sells` in the profile)? Name the page or service it leads to. Informational queries from people who'll never buy (how to do X yourself, finding your own account settings) fail, however big the impressions. If the connection has to be argued, it isn't there.
2. **Evidence.** Quote the row: query/page, impressions, clicks, position, window, market share. Clarity or heatmap evidence says what people do on the page.
3. **No open experiment.** Check the watchlist first. A page with a dated read still pending doesn't get changed before that date.
4. **One concrete, sized action**, for example:
   - *Near-miss query* (pos 4–20, real impressions, few clicks): title/meta rewrite toward the query, or an on-page section answering it.
   - *Split query* (the `split:` flag, two pages sharing one query): pick the page that should win, then consolidate or cross-link.
   - *Not indexed*: add internal links from indexed pages, then request indexing in GSC.
   - *Traffic that leaves* (landing sessions with low engagement, shallow scroll, quickbacks): check the heatmap for what's seen and missed; move the next step (CTA, service link) above where attention stops.
   - *Friction* (dead/rage clicks, script errors on a page): look at the exact element in the heatmap first; fix only what's actually broken.
   - *New queries showing up*: a signal about demand; only worth content if it passes the buyer test.

Anything that changes published copy or pages is the owner's decision, so present it as a proposal. Never suggest publishing content just to fill a calendar.

## Report template

```
**TL;DR:** <one sentence: which way things are moving, and whether anything produced leads>

**What changed**
- <since last snapshot: the KPI lines that moved, with dates>
- <this window vs prior: biggest movers, each tied to a page or query>

| Measure | Now | Prior | Source, window |
|---|---|---|---|
| Leads (real people) | | | CRM, dates |
| Search clicks (all / market) | | | GSC, dates |
| Search position / CTR | | | GSC |
| Organic sessions / engaged | | | GA4 Organic Search, dates |
| Indexed / sitemap URLs | | | GSC URL Inspection |
| On-page (sessions, scroll, dead/rage) | | | Clarity, last N days |
| GBP (as labeled on screen) | | | GBP Performance, range as shown |
| Domain Rating | | last snapshot | Ahrefs |

**Do this (max 3):** opportunity → evidence → action → page/service it feeds
**Due reads:** watchlist items that are due, each with its result
**Not measured:** <list>
```

Drop rows for sources the profile doesn't have. Don't show empty rows.
