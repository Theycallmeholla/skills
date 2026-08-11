# Refresh

Returns a keep/update/remove/add change plan — every line carrying a location and a reason — and, when a slug is named, a new draft version in which every stale claim is resolved and everything still accurate survives untouched.

**Reads:** `.blog/registry.json` · `.blog/posts/<slug>/claims.json` · `.blog/clients/<c>/facts.json` · `.blog/posts/<slug>/draft-vN.md` · `.blog/posts/<slug>/brief.md` · SERP (web search)
**Writes:** `.blog/posts/<slug>/draft-v(N+1).md` · `.blog/posts/<slug>/claims.json` · `.blog/posts/<slug>/post.json` · `.blog/registry.json`
**Then runs:** `review`, automatically, whenever a new draft version was written.
**Stops at:** Never rewrites wholesale — accurate material survives verbatim. Never publishes: the live page keeps showing the old text until a human ships the new version.

If `.blog/` doesn't exist, say so, point at `who-let-the-blogs-out brand`, and stop. Refresh is the one command with nothing to fall back on — it exists to read a history that hasn't been written yet.

---

## Two scopes

**`who-let-the-blogs-out refresh`** with no slug is a **survey**: which published posts have decayed, ranked, with the reason for each. It writes nothing.

**`who-let-the-blogs-out refresh <slug>`** is the **refresh** of one post: research, change plan, new draft version, reconciled ledger.

The survey is what lets the no-argument menu say *"4 published posts have claims that expired in June"* instead of listing commands. It is also the honest answer to "is anything rotting?" — a question nobody asks until something already has.

---

## Survey mode — no slug

1. Read `registry.json`. Consider every post with `status` of `published` or `stale`. Drafts can't decay; nothing is live and nothing has accumulated anything to protect.
2. Flag on three signals:
   - **`staleClaims > 0`** — the strongest signal, because a live page is currently asserting something nobody has checked.
   - **Age since `publishedAt`** — no fixed threshold. A pricing or platform-behavior post is suspect at 9 months; a process explainer can hold for three years. Judge by what the post is about, and say which judgment you made.
   - **`currentVersion` never republished** — the registry says version 4 but `publishedAt` predates the last two revisions. That's a post whose live text isn't the text on disk, and it needs saying before anything else.
3. For each flagged post, open `.blog/posts/<slug>/claims.json` and the client's `facts.json` to get the *specific* expiry — a date and a subject, not a count. "2 stale claims" is a number; "the Google title-length claim expired 2026-06-14" is something someone can act on.
4. Rank by **cost of being wrong**, not by age: a live page stating an expired price or a superseded legal threshold outranks a three-year-old post whose only issue is that it's three years old.
5. Recommend, don't run. Give the literal command per post and stop.

The survey writes nothing — not even a `staleClaims` recount, and not a `published` → `stale` status flip. Someone asking "what's decayed?" has not asked for six records to be rewritten. If your count disagrees with the registry's, print both numbers and name the file; the per-post refresh is what reconciles them.

---

## Phase 1 — Find the stale

Staleness has two sources and checking only one is the common miss.

**Source one — the post's own ledger.** In `claims.json`, every claim where `reverifyBy` is on or before today, plus every claim still sitting at `awaiting-client` or carrying `needsVerification: true` with no resolved status. Those last two aren't expired; they were never closed, and they've been live ever since.

**Source two — the client's vault.** Any claim with a `factRef` inherits that vault entry's expiry, so a claim can read `verified` in `claims.json` and still be stale because `F-012` in `facts.json` went past `reverifyBy` in May. Check every `factRef`. If a vault fact is expired or `retired`, note its `usedIn` list — other posts cite the same number and are stale for the same reason. Report those slugs; do not open or edit them. They aren't in this command's Writes, and one command quietly amending four posts is the failure the append-only rule exists to prevent.

**Then check `uses_claims`.** A stale claim absent from the current draft's `uses_claims` front-matter list was already edited out — the ledger row needs resolving, the article needs no touch at all. This is the single most useful field in the schema for this command, and skipping it produces edits to text that no longer exists.

**Then read the draft for what the ledger never captured.** Posts written before the ledger existed, or briefed loosely, carry time-sensitive material with no claim row behind it. Scan for: a year in the body or title · prices and ranges · "currently," "as of," "recently" · platform and product behavior ("Google shows FAQ rich results") · competitor feature claims · named tools that may have been renamed, acquired, or shut down · screenshots of interfaces that have since been redesigned · outbound links that may now 404. Each one becomes a new claim row in Phase 6 with a fresh monotonic ID.

Load `references/evidence-rules.md` and apply its verification standards to everything you re-check — same source hierarchy, same dating discipline, same preference for qualifying over deleting. "Roughly a third of," dated and sourced, beats both a wrong precise number and a hole in the paragraph.

## Phase 2 — Re-research intent

Load `references/research-protocol.md` and run its SERP analysis on the post's `primaryKeyword`. Do not assume the intent classification in `brief.md` held. Intent genuinely shifts: a keyword that wanted a how-to guide in 2024 can want a head-to-head comparison now, because two products emerged and the question changed from *how* to *which*.

Compare what you find against the brief's stated intent and coverage targets. Three outcomes:

- **Intent held.** Proceed to Phase 3.
- **Intent narrowed or widened.** Same page type, different emphasis — the SERP now leads with cost where the post leads with process. That's an `update` and an `add` in the change plan, not a rebuild.
- **Intent moved to a different page type.** Every top result is a calculator, or a pricing page, or a comparison table. **Say so and stop before the change plan.** The right answer may be a new page of a different type with this post redirected or demoted to a supporting explainer — which is a `plan` conversation, not a refresh. Polishing an article for a query that no longer wants articles is the most expensive way to fail at this command, because it looks like work.

Budget 3–6 searches. This is a re-check, not the original research.

## Phase 3 — Diff against the current SERP

Three questions, each of which produces change-plan lines:

1. **What's now table stakes that this post doesn't cover?** Subtopics appearing across most ranking pages that the post skips. These are `add` lines.
2. **What has the post kept that stopped mattering?** A section on a workaround for a bug the platform fixed. A comparison against a tool that shut down. These are `remove` lines — and they're the ones that earn the most goodwill, because nobody else deletes anything.
3. **Does the information gain still hold?** Read the `unique_value` line in the draft's front matter and ask whether the ranking set has caught up. A framework that was original two years ago and is now on four competing pages is no longer the reason this page wins. If the gain has eroded, say so plainly and name what would restore it — usually something only the client has: their actual numbers, a scenario they keep hitting, a result they can document. That goes in the plan as an `add` marked *client evidence needed*, per `references/evidence-rules.md`. Do not manufacture a replacement.

## Phase 4 — Cannibalization, in reverse

`plan` checks whether a new post would collide with something published. Refresh checks the opposite: since this post went live, what did the site publish that now competes with it?

Read every registry entry with a later `publishedAt` and compare on both axes — keyword overlap **and** intent. Same intent plus overlapping keyword is a collision no matter how different the titles look; same topic at different intent usually isn't one.

Three outcomes:

- **No collision.** Continue.
- **Collision, and this post should win.** It's older, better linked, and closer to the intent. Refresh it, and name the newer page that should be trimmed or pointed at it.
- **Collision, and the newer page should win.** Then the answer is **merge and redirect**, not refresh. Say which URL survives, what content should move across, and that the 301 is CMS work outside blog. Producing draft-v4 of a page that should be redirected next month is wasted effort in both directions.

## Phase 5 — The change plan

This is the deliverable, not a preamble to the edit. It's what the client reads to see exactly what changed, and what someone reads three months from now trying to explain a ranking movement.

Every line has three parts: **a location**, **the action**, **the reason**. Locations are specific enough to act on — `H2 "What counts as a location page"`, `¶4 under "Pricing"`, `front matter: meta_description`. Reasons name the thing that broke, not the category it belongs to.

```
KEEP    H2 "Why identical city pages get filtered"   Still the best explanation on the SERP; nothing in the top 10 covers the filtering mechanism.
KEEP    ¶1–6 of "Building the template"              Accurate, specific, and the only place the process is written down.
UPDATE  ¶2 under "Title length"                      C-003 expired 2026-06-14. Google's title-link doc still states no character limit — reverified 2026-08-01, source date 2026-05-20. Text stands; only the ledger date changes.
UPDATE  ¶3 under "Pricing"                           F-012 ($1,400 average) expired 2026-05-01 and the client hasn't reconfirmed. Qualify to "as of early 2026" or replace with their current figure.
REMOVE  H3 "Using the FAQ schema for local pages"    Google stopped showing FAQ rich results; the section advises work that now returns nothing.
ADD     New H2 after "Building the template"         6 of the top 10 now answer "how many pages before it looks spammy." The post doesn't, and it's the top PAA entry.
```

**The plan should read mostly `KEEP`.** A published post has accumulated age, links, internal links, and engagement history. Replacing text that's still accurate destroys those signals and buys nothing — the reader wasn't complaining about that paragraph and neither was Google.

So treat a plan that comes back mostly `UPDATE` and `REMOVE` as a signal to re-examine your own judgment before you touch anything. Two legitimate explanations exist: the post was genuinely bad, or the topic genuinely turned over. Both are worth stating out loud, and both usually mean the answer is a new article via `plan` rather than a fifth version of this one. The illegitimate explanation — and the common one — is that rewriting felt more productive than reading carefully. "This paragraph is fine but I'd have phrased it differently" is not a reason to change it.

### Cadence

Present the plan and ask **once**, at most three questions, and only when the answer changes the edit: a vault fact the client must reconfirm before you can state a number, an intent shift big enough that a different page type may be the real answer, or a `remove` that deletes a section the client may have had a reason for. Batch them into one round.

Never ask permission to keep something. Never re-ask the interview — the author's stance lives in `packet.md` and `opinion-bank.md`, neither of which this command reads, and re-interviewing here trains people to skip the round that mattered. When running non-interactively, apply the plan with unresolved items marked `awaiting-client` and say which lines are provisional.

## Phase 6 — Apply

Read `currentVersion` from `post.json` and write `draft-v(N+1).md`. Leave every prior version byte-identical — the diff between `draft-v3.md` and `draft-v4.md` is the permanent record of what this command did, and an edited prior version makes that record a lie.

- **Passages marked KEEP are copied through unchanged.** Not lightly reworded, not "tightened." If you find yourself improving prose that no plan line touched, that's the wholesale rewrite arriving in small pieces.
- **Preserve the heading structure** unless a plan line changes it. Headings are what internal links, jump links, and anyone's notes point at.
- **Front matter changes only where the underlying thing changed.** `word_count` recomputes; `review_date` moves to the next real expiry. The title set stays put unless the article's promise actually changed — and per `references/headline-contract.md`, do not add the current year to a title unless the article now genuinely carries current-year information, because a year in a title is a promise. The `slug` never changes: it's a redirect on a live URL, and this command doesn't get to spend that.
- **Don't bump the visible date without real changes.** A `dateModified` moved for a typo fix is freshness fakery, it's noticed, and the second time it happens the signal is worth less than nothing. If the plan is all `KEEP`, the honest output is a change plan saying so and no new draft version.
- **Update the publish checklist** at the bottom of the draft: dead links found, stale screenshots (a UI shot from a redesigned interface is a `media` problem — name it and point at `who-let-the-blogs-out images`, which owns `media.json`), and anything now marked *client evidence needed*.

## Phase 7 — Re-verify and reconcile state

Update `claims.json` in place — this file is a ledger, not a version, and rows move status rather than being reissued:

- Reconfirmed claims get a new `verifiedOn`, a new `reverifyBy`, and their source re-dated.
- Changed claims move to `qualified` with the qualifying language recorded, or to `removed` when the text came out.
- Claims the client must answer become `awaiting-client`.
- New claims found in Phase 1 get new IDs, allocated monotonically from the highest `C-NNN` already in the file. Never renumber, never reuse — `C-003` means one thing forever.
- **Write `uses_claims` in the new draft's front matter**, listing every claim still in the prose and omitting the ones you removed. Same for `uses_bank`. The next refresh depends on this being right, and you are the only command that knows what survived the edit.

Then, in the same operation:

- `post.json` — `currentVersion` to N+1, `updated` to today, `status` to `drafted`. Leave `url` and `publishedAt` exactly as they are: the page is still live, it's just live at an older version, and `publish` is what reconciles them. If Phase 2 or Phase 5 ended with no new draft — intent moved, or merge-and-redirect is the answer — set `status` to `stale` instead, which is the value that keeps the post on the menu until someone deals with it.
- `registry.json` — the same `status`, `currentVersion`, `updated`, and `staleClaims` recounted from the reconciled ledger. `title` changes only if the H1 did.

`facts.json` is read, never written. A vault fact that needs a new expiry is `verify`'s job — that's the command that owns the vault, and its edits ripple into every post citing the fact. Name the expired fact IDs and point at `who-let-the-blogs-out verify <client>`.

Anything malformed you hit along the way — a claim ID the brief never mentions, a `uses_claims` entry pointing at a claim absent from the ledger — gets reported in one line and left alone. Refresh reports drift; it doesn't repair it. A legacy `appearsIn` key still sitting in `claims.json` is not drift and is not reported: it is deprecated and ignored, per the state contract.

---

## Output

**Survey mode** — a chat response, nothing written:

```
## Aging posts — 4 of 11 published need attention

blog refresh title-tag-length-guide   2 claims expired 2026-06-14 (Google title behavior) · published 2025-03-02
blog refresh epoxy-garage-cost        F-012 (avg. price) expired 2026-05-01 · cited by 3 posts
blog refresh local-seo-location-pages v4 on disk, v2 published 2026-02-14 — live text is two versions behind
blog refresh gbp-optimization-guide   published 2024-09-11, no stale claims — age only, platform-behavior topic

## Clean
7 posts, nothing expiring before 2027-01.
```

**Single-post mode** — a chat response in this order, plus the file writes:

1. **`## <slug> — refresh`** — current live version, publish date, and the one-line verdict: refresh, merge-and-redirect, or wrong-page-type-now.
2. **`## Stale inventory`** — every expired claim and vault fact, with ID, expiry date, what it asserts, and whether it still appears in the live version.
3. **`## Intent re-check`** — held / narrowed / moved, with what the SERP shows now versus what `brief.md` recorded.
4. **`## SERP diff`** — new table stakes, what stopped mattering, and whether the original information gain still holds.
5. **`## Cannibalization`** — newer posts competing with this one, and the decision. `None` is a valid and common answer.
6. **`## Change plan`** — the KEEP / UPDATE / REMOVE / ADD table, in that order, with the keep count stated first: *"14 of 19 sections keep."*
7. **`## Claim ledger`** — reverified / qualified / removed / awaiting-client / new, with IDs.
8. **`## Written`** — literal paths. If no new draft was warranted, `No new draft version — see change plan` and one line on why.

`review` then runs automatically on the new version — a refreshed draft is still a draft, and this command does not score its own work. Report its findings alongside the change plan, leading with any `boundary` or `fabrication` results. When the plan was all `KEEP` and no new version was written, nothing is scored and nothing chains.

## Confirm and stop

Deliver the change plan and the next draft version. Keep everything that's still true and still good — a mostly-`KEEP` plan is this command succeeding, not underdelivering — and never mark the post published: the live page changes when a human ships it.
