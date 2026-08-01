# Plan

Returns 3–5 candidate topics — each with a primary keyword, an intent, a format-fit verdict, and a cannibalization decision — plus a reserved slug for the ones worth writing. Not an outline.

**Reads:** `.blog/registry.json` · `.blog/clients/<client>/brand.md` · SERP (web search)
**Writes:** `.blog/posts/<slug>/post.json` (status `idea`) · `.blog/registry.json`
**Stops at:** No interview, no deep research, no outline, no prose. Decides the slug only — never the rest of the title set, which needs an angle nobody has found yet.

If `.blog/` doesn't exist, say so, point at `who-let-the-blogs-out brand`, and stop. A plan built against no index can't do the one thing this command exists for.

---

## Phase 1 — Load what's published

Read `registry.json` and build the collision set: every post's `slug`, `primaryKeyword`, `intent`, and `status`. Include in-flight posts (`idea`, `interviewed`, `briefed`, `drafted`), not just `published` — two ideas targeting one keyword is the same collision as two live pages, caught two weeks earlier and for free.

Read the client's `brand.md` for what they sell, who buys it, the named competitors, and the **Never say** list. A candidate that only works if the article says something on that list is dead before the SERP check, and finding that out now costs one line instead of one draft.

The registry only knows posts blog created. If the client has a blog predating this system — three registry entries on a domain with 200 indexed posts — say so plainly. Phase 4 covers it with a site search, but the user should know which check is doing the work.

If `brandProfile` is `partial` or `missing`, note it in one line and continue. Plan still works; the candidates will just skew generic, and that's worth naming rather than hiding.

Do not open `opinion-bank.md` or `facts.json`. They aren't in this command's Reads, and the temptation is real — the bank would sharpen the candidates. `interview` reads it two steps from now, which is where the sharpening belongs.

## Phase 2 — Generate candidates

Draft eight to ten, keep three to five. Overshooting then cutting produces a better shortlist than trying to think of exactly five good ones.

Sources, in order of usefulness: the user's seed topic if they gave one · questions the buyer in `brand.md` actually asks before purchase · the differentiators in `brand.md` that no competitor can claim · obvious gaps in what's already published · adjacent queries the SERP surfaces.

For each candidate record:

- **`primaryKeyword`** — the phrase a real person types, not a topic label. "how much does epoxy garage flooring cost" beats "epoxy flooring pricing considerations."
- **1–2 close variants** — enough to tell whether it's one query or three.
- **`intent`** — one value from the closed enum in `state.md`: `informational` · `commercial` · `transactional` · `navigational` · `local` · `mixed`. Reach for `mixed` last; it's usually two candidates wearing one coat.
- **Who's searching, and what ends the search** — one sentence. If you can't write it, the candidate isn't real yet.

If the user handed you a single keyword and nothing else, still build the field. Run the full check on theirs as candidate one and generate two to four adjacent ones — the comparison is most of this command's value, and a shortlist of one is just agreement.

## Phase 3 — Format-fit challenge

Load `references/research-protocol.md` and run its SERP analysis section. At plan stage you need only three of its outputs: **ranking page types**, **dominant intent**, and **search features**. The subtopic map, freshness pass, and claim ledger belong to `brief` — running them now wastes the work, because the interview usually moves the angle and you'd redo it.

Budget: one to two searches per candidate, roughly eight total. This is triage.

Then challenge the assumption that a blog post is the answer. Most keyword lists are written as if every query deserves an article; the SERP disagrees constantly. Read the top ten and ask what page type is actually winning:

| What the SERP shows | What the searcher wants | Recommend instead |
|---|---|---|
| Calculators, estimators, interactive tools | A number for *their* situation | A calculator page, with a short explainer beneath it |
| Service pages from local firms, a local pack | A provider, not an education | A service page or location page |
| Pricing pages, "starting at" tables | The price | A pricing page |
| Head-to-head comparisons, alternatives lists | A decision between two named things | A comparison page |
| Hubs, template libraries, downloads | An artifact to use | A resource hub |
| Product pages, shopping carousel | To buy | A product page |

Verdict per candidate: `blog-post` or `different-page-type: <type>`, with one line on what to build instead.

A candidate that fails format fit is still reported, never dropped. "This one wants a calculator, not an article" is frequently the most valuable sentence this command produces — writing a *10 Tips for Estimating Driveway Cost* piece for a query where every ranking result computes a number is work that was doomed before the first paragraph.

Format fit is a signal about the query, not a veto on the client. If the client wants an article on a comparison-intent keyword and has a genuine reason, say the SERP disagrees, say what it would take to win anyway, and let them choose.

## Phase 4 — Cannibalization check

This is why the command reads the registry at all.

For each candidate still standing, compare against **every** post in the registry on two axes: keyword overlap and intent. Both matter, and neither is sufficient alone.

- Same intent + overlapping keyword → collision, no matter how different the two titles look.
- Same topic, different intent → usually fine. "how to do local seo" (informational) and "best local seo agency houston" (local/commercial) are different pages serving different people. Say so. Over-flagging is how a check gets ignored, and an ignored check is worse than none.

Then run the site-context check from `research-protocol.md` — `site:<domain> "<topic>"` — because the registry only knows what blog made. If no domain is available in `brand.md`, say the check ran against the registry only, so nobody mistakes a partial answer for a clean one.

Every candidate gets exactly one decision:

- **`create`** — nothing on the site serves this intent. Proceed to Phase 5.
- **`refresh-existing`** — an existing post already targets it and would rank if brought current. Route to `who-let-the-blogs-out refresh <slug>`.
- **`merge`** — two or more thin existing pages split one intent between them; this candidate should become the consolidation rather than a third fragment. Name the pages and which URL should survive.
- **`redirect`** — an existing page already owns this and a weaker duplicate should point at it. Name both URLs.

**A `refresh-existing` verdict is a win, and say so in those words.** The existing post already holds its accumulated links, its age, and every internal link pointing at it. A new article on the same intent doesn't add to that — it splits it, and the two pages take turns outranking each other while both underperform the one page that used to work. Returning five candidates where two come back `refresh-existing` means two articles' worth of work saved and two rankings protected. That's the command doing its job, not failing to find work.

Plan reports `merge` and `redirect`; it doesn't execute them. Consolidating pages and setting 301s is CMS and server work outside blog entirely. Name the action and who does it.

If a registry entry is missing `primaryKeyword` or `intent`, the check against that entry is incomplete. Name the entry, mark the affected candidates' decisions provisional, and continue. Report drift; don't repair it.

## Phase 5 — Reserve the slug

Only for candidates whose decision is `create`. A `refresh-existing` or `merge` candidate gets no post record — creating one for a post you just recommended against writing fills the registry with ghosts that the no-argument menu will faithfully recommend forever.

Slug rules live in `references/headline-contract.md` under working targets: 3–7 meaningful words, lowercase, hyphenated, no stop words. Load it rather than trusting memory.

The slug carries the keyword's *meaning*, not the keyword's *string*. `how to build location pages for local seo` becomes `local-seo-location-pages`, not `how-to-build-location-pages-for-local-seo`. It has one job — never changing — and it's read by people scanning a URL bar and by whoever runs `who-let-the-blogs-out interview <slug>` next week.

Check the proposed slug against every slug in the registry and against the live site. A slug that collides with an existing URL is a redirect on its first day, which is the exact cost this reservation exists to avoid.

Then write, in one operation:

1. `posts/<slug>/post.json` — schema per `state.md`, with `status: "idea"`, `currentVersion: 0` (no draft exists; `write` sets 1), `url: null`, `publishedAt: null`, and `created`/`updated` set to today.
2. The matching `registry.json` post entry — same slug, client, `primaryKeyword`, `intent`, `status: "idea"`, `openFindings: 0`, `staleClaims: 0`.

Set the registry entry's **`title` to `null`**. There is no title yet, and a placeholder written now is the anchor this whole command is built to avoid — everything downstream would quietly steer toward it. The slug is the human-readable handle until `brief` decides the real title set.

If `posts/<slug>/` already exists, don't overwrite it. Report what's there, pick a different slug or stop, and let the user decide.

## Phase 6 — Decide

Rank the `create` candidates on four things, in this order:

1. **Does the client have something first-hand to bring?** A keyword where they have no story, no data, and no scar tissue produces a generic article no matter how well it's written. The 500-companies test starts here, not at review.
2. **Buyer proximity** — how close is this searcher to needing what the client sells?
3. **Beatability** — is the ranking set weak, dated, or repetitive, or is it three excellent pages from people with more authority?
4. **Internal-link fit** — does anything already published naturally point at this, and vice versa?

Recommend one to run next, in one or two sentences, and give the literal next command: `who-let-the-blogs-out interview <slug>`.

Then stop. Don't run it.

### Cadence

Ask at most one round, at most three questions, and only when the answer changes which candidates exist — no client named and the registry has several, or `brand.md` is thin enough that you'd be guessing at the buyer, or two candidates rank identically and only the user knows which service line matters this quarter.

Never ask what the SERP can answer. Never ask what they think about the topic, what their angle is, or what stories they'd tell — that is the entire interview, it arrives two commands from now, and asking it here trains people to answer everything twice and then skip the round that mattered.

## Output

A chat response, in this order. No file beyond the state writes in Phase 5.

1. **`## What's already published`** — post count, and the subset relevant to any candidate's collision check. One line each.
2. **`## Candidates`** — a table: Keyword · Intent · Format fit · Decision · Slug (or `—`).
3. **`## Per candidate`** — one block each, in the table's order: keyword and variants · who's searching and what ends the search · the SERP read in two or three lines (page types, features, dominant intent) · format-fit verdict with the recommended page type when it isn't a blog post · cannibalization decision naming the specific existing post · reserved slug, or why none.
4. **`## Recommendation`** — the one to write next, the reason, and the exact next command.
5. **`## Written`** — the literal paths written. If every candidate came back non-`create`, write `Nothing written.` and say why in one line — that outcome is a result, not an error.

## Confirm and stop

Candidates, verdicts, decisions, and slugs. No interview, no deep research, no outline, no prose, and no title beyond the slug — the article's promise needs an angle this command hasn't looked for yet, and a title guessed now would quietly steer everything downstream.
