# Tests, ranking, and sizing

Every candidate from `candidates.py` goes through the four tests below. Anything that fails one goes to **Not doing, and why**, never into the plan. The profile's `notes.md` wins wherever it is stricter.

## The four tests (all must pass)

1. **Buyer test.** Would the person behind this query, visit or lead buy something this business sells (`business.what_it_sells` in the profile)? Name the page or service the action feeds. Informational queries from people who'll never buy (how to do X yourself, finding your own account settings) fail, however big the impressions. If the connection has to be argued, it isn't there.
2. **Evidence.** Quote the row exactly as the snapshot has it: query or page, the numbers, the source, the window, and the market share where there is one. Clarity or heatmap evidence says what people do on the page. No row, no action.
3. **No open experiment.** Read every watchlist line `candidates.py` attached, plus the whole Open section. Its date matching only catches pages named by path, so a line that names the page in words ("the legit post") blocks it just as much. A page with a dated read still pending doesn't get changed before that date. A line saying a fix was already tried ("a title rewrite already ran here, don't propose another") rules out that fix for good, though a different kind of action may still pass. A read that's in **Done** frees the page. Don't invent a new hold date for it. If you think its window was too short to judge, say that in the Why line, and still propose the best action that isn't a repeat.
4. **One concrete, sized action**, for example:
   - *Near-miss query* (pos 4–20, real impressions, few clicks): rewrite the title/meta toward the query, or add a section on the page that answers it.
   - *Split query* (two pages sharing one query): pick the page that should win, then consolidate or cross-link.
   - *Not indexed*: add internal links from indexed pages, then request indexing in GSC.
   - *Traffic that leaves* (low-engagement landings, shallow scroll, quickbacks): check the heatmap for what's seen and missed; move the next step (CTA, service link) above where attention stops.
   - *Friction* (dead/rage clicks, script errors): look at the exact element in the heatmap first; fix only what's actually broken. Dead clicks on plain text are usually text selection.
   - *Unconfirmed lead*: the owner follows up, then confirms or rules the person out. Record the answer in `profile.json` `people`.
   - *Proven lead channel*: more of what already produced real bookings (referral asks, directory reviews, partner listings).
   - *Page climbing but stuck on page two after its own fix*: strengthen it from outside instead of editing it again. Add links to it from related posts and from the service page it feeds, where the sentence already fits. Check the site source for which related pages don't link to it yet; that count is the evidence.
   - *New queries showing up*: a signal about demand. Only worth content if it passes the buyer test and the business's editorial rules.

## Ranking: closest to a booked customer first

Rank by how directly the action can produce a real lead, then by effort. Impressions don't decide rank.

| Tier | What it is | Why it ranks here |
|---|---|---|
| 1 | Leads and deals already in reach: unconfirmed bookings, follow-ups, pipeline status | Money that exists now. Usually minutes of owner time. |
| 2 | Channels that already produced real bookings (from `source:` tags, the owner's labels in `people.confirmed_real`, `notes.md`) | Proven to convert. If most bookings came from referrals, a referral ask beats any SEO change. |
| 3 | Buyer traffic that arrives and leaves (landing leaks, friction on service or contact pages) | The visitor is already here; fixing the page converts existing traffic. |
| 4 | Search demand near page one that passes the buyer test | Real, but slower and less certain. Clicks aren't leads. |
| 5 | Plumbing and long shots: indexing, new demand, technical | Needed, rarely urgent. |

Within a tier, put first whatever is smaller effort with stronger evidence. A tier-4 action only beats a tier-2 one when the tier-2 one is blocked or the owner has dropped it.

**Deferred tasks keep their rank.** When the owner has put a task off ("not this week"), rank it where its evidence puts it, even at #1, and add its history to the Why line ("deferred 09-30 and 10-01"). Deferring doesn't make a proven lever weaker; hiding it would make the plan less honest. It leaves the ranking only when the owner explicitly drops it ("drop it", "never"). Record that in the watchlist item, and then list it once under Not doing.

## Sizing

- **Effort:** S (under an hour), M (an afternoon), L (more). Say who does it: owner, Claude, or both.
- **How we'll know:** the read that settles it. That means a dated watchlist entry (the date when the effect could show: about 4 weeks for search changes, the call date for a lead, 2 weeks for a page conversion fix with enough traffic), the baseline row quoted now, and the exact read to make. Counts under ~100 get compared as counts, never percentages.
- If the traffic is too small for any read to settle it (say a page with 3 sessions a month), say so. The action may still be right, but don't promise a measurable result.

## What zero looks like

"Nothing worth changing this week" is a real answer when every candidate is blocked or fails a test. Still show the one-line **Holding off** with dates, because it tells the owner the board was checked and when each blocked item frees up. Keep the full Not-doing list ready for when they ask.
