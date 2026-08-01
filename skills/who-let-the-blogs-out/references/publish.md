# Publish

Records a post as live and returns the closed checklist plus the re-verification schedule for every claim in it.

**Reads:** `posts/<slug>/post.json` · `posts/<slug>/claims.json` · `posts/<slug>/media.json` · `posts/<slug>/review-vN.json` · `posts/<slug>/brief.md`
**Writes:** `posts/<slug>/post.json` (status → `published`) · `posts/<slug>/claims.json` · `registry.json` · `posts/<slug>/notes.md` *(drawer entries only — redirects, reviewer names, proceed-anyway acknowledgments)*
**Stops at:** Never pushes to a CMS. Never publishes over an open `boundary` or `fabrication` finding.

## This command records; it does not deploy

Say this in the first line of your response, before anything else. A command named `publish` that doesn't publish is a surprise worth heading off immediately, because someone who assumes otherwise will close the terminal believing the post is live.

The human, or their CMS, puts the article on the web. Blog writes down that it happened: the URL, the date, the version that shipped, and an expiry on every claim. CMS connectors exist and were deliberately left out of v1 — a side-effecting command needs its own gate design, and bolting one onto a recording command is how a system starts publishing things nobody approved.

So run this **after** the post is live and you have the real URL in hand. If it isn't live yet, say so and stop — recording a URL that 404s puts a lie in the registry that `plan` and `brief` will both trust.

## Phase 1 — Gate check

Read the review file matching `currentVersion` in `post.json`. That file is authoritative: `revise` writes resolution status back into it, so a finding still marked `open` there is genuinely still open.

**Two categories block, and cannot be waived.**

Open findings in `boundary` or `fabrication` stop this command. These are the two failures that put someone's name on something they didn't say — a claim the author never made, an experience they never had, a line the client explicitly said never to print. Unlike every other category they are severity-locked to `high` and cannot be `accepted`, so there is no "yes, I know, leave it" path and you should not offer one. Report the finding IDs, quote the evidence, and point at `revise`. If the user insists, the honest answer is that the article can be published by hand — this system just won't record it as shipped clean.

An absent review file is not a clean gate. It means the boundary and fabrication checks never ran, which is different from running and passing. Say that plainly, offer `review`, and if the user still wants the post recorded, write the acknowledgment into `notes.md` with the date so the next person reading the record knows the gate was skipped rather than cleared.

**Four things warn, and the user decides — on the record.**

Each of these is something that genuinely ships broken, and publish is the last cheap moment to name it. List them, then ask once.

1. **Assets still `needed` in `media.json`.** Name the ID, role, and placement: `M-002 diagram, after H2 "Why Google rewrites titles"`. A live post with a missing diagram is the "no relevant images" complaint arriving three weeks late.
2. **Claims still `awaiting-client` or carrying `needsVerification: true` in `claims.json`.** These are the numbers nobody chased. They are already in the article.
3. **Unanswered coverage targets.** Cross-check `brief.md`'s numbered reader questions against open `completeness` findings in the review. Quote the brief's question verbatim — "How do I keep 40 city pages from reading identical?" is more useful than "2 coverage gaps."
4. **A YMYL article with no reviewer.** Load `references/evidence-rules.md` for what counts as YMYL. If the topic is health, legal, financial, or safety-adjacent and no qualified reviewer is recorded, ask who signed off. Their name has no field in `post.json` — the schema is closed and this is not the moment to extend it — so it goes in `notes.md` with the review date.

Open findings in every other category are also worth listing before you proceed: `original-value`, `completeness`, `technical-seo`, whatever is still open. Those can be `accepted`, and often already were. Show the count and the worst two or three so the decision is informed rather than theoretical.

### Cadence

One round, at most three questions, then act:

1. The live URL.
2. The published date, if it isn't today.
3. One consolidated "proceed over these N warnings?" — the whole list in one question, not one question per warning.

Never ask for anything blog can read: the slug, the client, the current version, the title set, which claims exist. Never re-litigate a blocked `boundary` or `fabrication` finding by asking whether the user wants to proceed anyway — the answer doesn't change the outcome, and asking implies it might. If the user has already given the URL and date in their invocation, ask nothing and go.

## Phase 2 — Record URL, date, and the slug that actually shipped

Set in `post.json`: `status: "published"`, `url`, `publishedAt` (ISO `2026-08-01`), `updated`. Leave `currentVersion` pointing at the draft that shipped — that pointer is how `refresh` later knows which text is live.

**Confirm the slug in the live URL matches the one in `post.json`.** `plan` reserved that slug at idea stage precisely because it is a stable page identifier, and CMS defaults, editors, and category prefixes all rewrite slugs quietly. If the live URL is `/blog/seo/location-pages-guide` and the record says `local-seo-location-pages`, the reserved slug lost. Record the real one in `url`, keep the directory name as-is (renaming the post directory would orphan every ID that references it), and write the redirect requirement into `notes.md`:

```
2026-08-01 · Slug drift at publish. Reserved: local-seo-location-pages.
Live: /blog/seo/location-pages-guide. Redirect needed if the reserved path
was ever linked or submitted. Post directory keeps the original name.
```

That is the drawer's job — a judgment call with no field to live in, which is exactly why every entity has one.

**Confirm the visible date.** Load `references/headline-contract.md` for why this matters: the rendered "Updated" date and `dateModified` disagreeing is a real inconsistency readers and parsers both see, and a date bumped without anything changing is worse than a stale one. If fetching the live URL is available, fetch it and compare the visible date to what you're recording. If it isn't, ask the user to eyeball it and say in the report that the date was recorded unverified. A date recorded from the CMS's assumption rather than the page's actual output is the kind of drift nobody finds for a year.

## Phase 3 — Set `reverifyBy` on every claim

This is the phase that makes `refresh` possible at all. A claim with no expiry never goes stale, never surfaces in a staleness scan, and never gets found again — it just quietly ages into being wrong on a live page. Every claim leaving this command carries a date.

**Don't overwrite an expiry that already exists.** `verify` set it deliberately, calibrated to that specific claim. Overwriting it with a default throws away the better judgment.

**Where one is missing, apply a default by claim kind** and say which default you applied, per claim, in the report. `references/evidence-rules.md` owns the calibration reasoning — load it. Its guidance, turned into defaults:

| Claim is about | Default | Why |
|---|---|---|
| A price, a platform behavior, a product feature | **6 months** | These decay fastest; evidence-rules calls 12 months already generous for them |
| A statistic, a study, a research finding | **12 months** | New data lands annually at best |
| A law, a regulation, a standard | **12 months** | Slower to change, more expensive to be wrong about |
| A process, a physical fact, a durable threshold | **24 months** | May not decay at all, but still gets a date so the next reader knows when someone last looked |
| Anything you can't classify | **12 months** | The safe middle. Say you defaulted rather than guessing a kind. |

**Two special cases.**

A claim with a `factRef` inherits its expiry from the vault entry — one fact used in three posts is verified once and expires once. If such a claim has a null `reverifyBy`, the vault entry is the thing that needs fixing, and `facts.json` is not in this command's Writes. Report it, name the fact ID, point at `verify`, and leave the claim's field null rather than inventing a date that will disagree with the vault's.

A claim still `awaiting-client` gets a deliberately short expiry — **90 days** — so the next staleness scan surfaces it while the article is still fresh in someone's memory. It shipped unverified; the short leash is the compensation.

Claims with `status: "removed"` are not in the article and get no expiry. Setting one would seed a permanent false positive in every future `refresh`.

## Phase 4 — Index

Update the post's entry in `registry.json` in the same operation as the `post.json` write: `status`, `url`, `publishedAt`, `currentVersion`, `title` (the `h1`), `primaryKeyword`, `intent`, `updated`, and the two summary counts — `openFindings` from the review file, `staleClaims` counted as claims whose `reverifyBy` is already in the past (normally zero at publish; non-zero means a vault-inherited expiry lapsed before the post went live, which is worth saying out loud).

This step is not bookkeeping. The registry is the only thing future commands read before they open a record, so an unindexed published post is invisible to the entire system going forward: `plan`'s cannibalization check will happily approve a near-duplicate keyword, `brief` will never suggest an internal link to it, and `refresh` will never find its aging claims. The post exists on the web and not in the system's memory, which is the specific failure this whole state directory was built to prevent.

If the post has no registry entry at all — it should, `plan` created it — add one rather than skipping. That's completing this command's own write, not repairing someone else's drift.

## Output

A chat response in this order. No file artifact beyond the three state writes and any drawer entry.

```
Recorded, not deployed — blog wrote the record; the post was published by you/your CMS.

## <slug> — published
https://cursivemedia.com/blog/local-seo-location-pages · 2026-08-01 · draft-v3

### Gate
No open boundary or fabrication findings.        ← or: BLOCKED, with IDs
2 other findings open and accepted: BL-009 original-value, BL-014 technical-seo

### Checklist
Closed:  9 of 11
Open:    M-002 diagram (status `needed`) — placement after H2 "Why Google rewrites titles"
         C-007 awaiting-client — the 40-page rollout turnaround range
         Coverage target 6: "What does this cost to maintain?" — partial

### Re-verification schedule — 8 claims
C-001  2027-03-11  inherited from F-007 (vault)
C-003  2027-08-01  set by verify
C-005  2027-02-01  default applied: 6mo, platform behavior
C-007  2026-10-30  default applied: 90d, awaiting-client
(every claim, every date, defaults labeled as defaults)

### Notes
Slug drift: live path is /blog/seo/location-pages-guide — redirect noted in notes.md
Visible "Updated" date confirmed against the live page.

Written: post.json (published) · claims.json (8 expiries) · registry.json · notes.md
Next: `refresh` will surface this post when its first claim expires — 2026-10-30.
```

Name the next expiry date explicitly in the last line. It turns an abstract schedule into a specific thing that will happen, and it's the sentence that makes someone believe `refresh` is real.

Report drift without fixing it: a media asset with no `role`, a claim ID the brief never mentioned, a review file for a version that doesn't exist. Say what's malformed, name the file and field, and finish the publish record you were asked for.

## Confirm and stop

Record the post, expire every claim, index it — but never push to a CMS, and never record a publish over an open `boundary` or `fabrication` finding.
