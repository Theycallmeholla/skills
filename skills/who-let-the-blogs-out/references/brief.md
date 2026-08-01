# Brief

Returns the article's angle, its information-gain thesis, a committed list of reader questions, an outline, real internal links pulled from the registry, the claim list, the title set, and image concepts — with zero body prose.

**Reads:** `posts/<slug>/packet.md` · `clients/<c>/brand.md` · `clients/<c>/opinion-bank.md` · `clients/<c>/facts.json` · `registry.json` · live SERP
**Writes:** `posts/<slug>/brief.md` · `posts/<slug>/claims.json` · `posts/<slug>/media.json` · `posts/<slug>/post.json` (status → `briefed`) · `registry.json`
**Stops at:** Never writes prose paragraphs, not even a sample one to demonstrate tone.

This is the cheap artifact that exists to be rejected. Four of the five failures this system was built for — not thought through, not long enough, no images, facts invented — are decided here and are invisible once a draft exists. A brief that gets waved through has cost the user nothing but the draft it green-lit costs them an hour of reading to discover the same problems.

## Preflight

Load `references/state.md`. If `.blog/` is missing, say so, point at `brand`, and stop — don't create a partial tree.

Read `posts/<slug>/post.json`. Expect status `interviewed`. If `packet.md` doesn't exist, say so and point at `interview` before continuing: without a packet, every source of original value has to come from research alone, and the article will be one any of 500 companies could publish. You can still brief it if the user insists — say plainly that you're briefing an article with no first-hand layer, and record that as the honest state of things.

Read `brand.md`, `opinion-bank.md`, `facts.json`, and the client's published posts in `registry.json` before searching. Reading state first means the SERP gets interpreted against what this client actually knows, rather than summarized in a vacuum.

## Phase 1 — SERP analysis

Load `references/research-protocol.md` and follow its SERP procedure. Don't restate it here and don't re-derive it — it already specifies what to record and how many searches are proportionate.

Two things carry forward into this command specifically:

- **The weaknesses and omissions list** is the raw material for Phase 4. Write it down even when it feels obvious; "every ranking page explains what a doorway page is and none says how Google actually detects one" is the sentence the whole brief hangs off.
- **The recurring subtopics and the People Also Ask entries** are candidate coverage targets, not the final list. They tell you what's table stakes, not what your reader needs.

If the SERP contradicts the `intent` recorded in `post.json` — `plan` classified it informational and the results are all pricing pages and vendor comparisons — say so and update `intent`, since `post.json` is yours to write. Naming the change matters more than making it; a silently reclassified post is one `review` will later fail for intent mismatch with nobody able to explain why.

## Phase 2 — Format fit

Decide from the ranking page types whether an article is the right artifact at all. Values are `article`, `tool`, `comparison`, `location-page`, `hub`, and the frontmatter field carries the rationale, not just the value.

When calculators, comparison tables, or forum threads dominate the first page, an article is competing in a format the query didn't ask for. Stop and say so before spending the rest of the brief: "eight of the ten results are interactive cost calculators; a 1,400-word explainer of the same math is a worse answer to this query than a 40-line calculator would be." Then ask once whether to proceed as an article anyway, reframe the format, or hand it back to `plan`. Proceeding without asking produces a well-executed piece of the wrong thing.

## Phase 3 — Site-context and cannibalization

Follow the site-context section of `research-protocol.md`, with one upgrade it doesn't have: you have `registry.json`, so internal links are real.

**Cannibalization.** Compare the primary keyword and intent against every published post for this client in the registry. Record `cannibalization: none`, or the competing slug plus a decision — `create`, `merge`, `redirect`, or `refresh`. When the honest answer is "updating `local-seo-location-pages` would beat publishing a second page on the same intent," say that plainly and stop for a decision. A system that never recommends killing its own work isn't a gate.

**Internal links.** Pull them from the registry's published posts, with actual slugs and URLs. Both directions:

- *Destinations* — pages this post should link to. Give the anchor text and the reason the link earns its place: `[how we build city pages](/blog/local-seo-location-pages)` — "the doorway-page section needs somewhere to send readers who want the full build process."
- *Sources* — published posts that should now link **to** this one, named by slug, so `publish` has a list rather than an intention.

Placeholders like `INTERNAL: some related page` are the fallback for having no site context. You have site context. If the registry genuinely has zero published posts for this client, write "no internal links available — first post for this client" and leave the section empty. An empty honest section is fine; a fabricated link is a 404 with a plan attached.

## Phase 4 — Angle and information gain

Do this before outlining, and write both into the frontmatter as one sentence each. Outlining first is how an article gets built out of subtopics and then has a thesis retrofitted onto it — which is exactly the article the 500-companies test exists to catch.

**Angle** — the specific argument this piece makes. "Location pages fail because they're built from a template and filled per-city, when the fix is to build them per-city and template only the chrome."

**Information gain** — what a reader gets here that the ranking pages don't give them. Draw it in this order of strength:

1. The packet — a first-hand story, a number the author actually watched happen, a position they'll defend.
2. The fact vault — a durable client fact the SERP doesn't have.
3. Original analysis of the research — a framework, decision criteria, a calculation, a comparison nobody has made.

If none of the three yields anything, **do not outline the article.** Write the frontmatter through `informationGain`, state the deficit in it directly ("none available — every claim available to this post is already on page one"), name exactly what the client would have to supply to fix it (their actual rollout numbers, three real customer objections, screenshots of the audit output), and recommend killing or reframing the topic. Leave `post.json` at `interviewed`. An article with nothing to add doesn't become one by being outlined well, and the outline is what makes it look ready.

## Phase 5 — Coverage targets

**This is the depth mechanism, and it is why the brief exists.**

Doctrine point 2: depth is coverage, not length. A post reads thin when it answered four questions and the reader had seven — not when it ran 900 words. Padding a complete 900-word answer to 1,800 makes it measurably worse and it still leaves the three questions open. So the brief commits to a numbered list of real reader questions, and `review` raises a `completeness` finding for every one the draft leaves unanswered. That is an enforceable depth target; a word count is a proxy that can be satisfied by writing more of nothing.

Five to nine questions is the normal range. Build them from:

- People Also Ask entries and forum threads — what people actually type
- Objections in the packet — what the author says clients push back with
- The "Never say" and competitor sections of `brand.md` — what this client's buyers ask that the SERP doesn't answer
- The gap from Phase 4 — the question every ranking page ducks

Each one must be phrased as a question a real person would ask, and each must be answerable from the packet, the vault, or cited research. Committing to a question the material can't answer is committing the draft to fabricate — you've built the pressure that produces an invented case study. If a question matters but nothing supports it, either move it to "deliberately does not cover" with the reason, or list the evidence the client must supply.

Set `coverageTargets:` in the frontmatter to the count, and write the numbered questions as the first section of the body.

Then write **What this post deliberately does not cover**, with a reason per item. This fence does two jobs: it stops the draft sprawling into a second article, and it stops `review` flagging an omission that was a decision. "Not covering GBP optimization — separate post, already ranks at `/blog/gbp-categories`."

## Phase 6 — Outline

Load the heading-craft section of `headline-contract.md` and apply it. The short version of why it matters: H2s are the reader's questions taken from Phase 5, not keyword slots, and the skim test — someone reading only the headings comes away with the argument — is the fastest check on whether an outline reasons about something or just enumerates subtopics.

Each outline node gets four things and nothing else:

```
H2: Why Google flags city pages as doorway pages
    closes: Q2, Q5
    uses:   packet — the 40-page rollout that got manually actioned in week three
            F-012 (crawl budget threshold), C-004 (Google doorway-page guidance)
    work:   distinguishes detection from ranking; sets up the per-city build in the next section
```

`work` is the section's job in one phrase — what changes in the reader's head. It is not a topic sentence and it is not the first line of the section. Section depth follows value, not symmetry: three sections of near-identical size is a strong signal the outline was filled rather than thought through.

**This is the phase where the stop boundary breaks.** The temptation is to write one paragraph "to show the tone," and it's a strong one because a sample paragraph genuinely is easier to judge than an outline node. Resist it, because the brief's whole power is that a draft can be measured against it — and a brief containing draft has already agreed with the draft in advance. It also silently anchors `write` to phrasing that was never voice-checked against `voice-and-tells.md`, which is how a tell gets baked in at the outline stage. If the user wants to see the tone, point them at the client's published posts, or run `write` and reject the draft. That's the cheap path, not this one.

## Phase 7 — Title set

Load `references/headline-contract.md` and follow it. Don't restate its rules or its character heuristics here.

Fill all seven keys: `searchTitle`, `h1`, `headline`, `dek`, `metaDescription`, `slug`, `alternates` (two alternate search titles). The set describes one article in different phrasings for different jobs — not one string pasted into six slots.

The `slug` was reserved by `plan` and is copied verbatim. If it now looks wrong, say so and leave it alone: changing a slug after publish costs a redirect, and the brief is not where that decision gets made quietly.

Deciding the title set here — before drafting rather than after — is the reason it works. The draft is then written toward a promise it already made, instead of having a headline retrofitted onto whatever came out, which is why so many posts have a title the body doesn't deliver.

## Phase 8 — Claims and images

**`claims.json`.** Enumerate every material claim the article will make — every number, date, price, platform behavior, statistic, competitor feature, or anything a reader could check and find wrong. Allocate IDs monotonically per post from `C-001`.

Cross-reference `facts.json` first. A claim already in the vault gets `factRef: "F-012"`, `needsVerification: false`, the vault entry's `status`, and its `reverifyBy` inherited rather than reset. No re-verification: that's the entire point of the vault — one fact used in three posts is verified once and expires once.

Everything else leaves this command as pending, carrying `needsVerification: true`, `verifiedOn: null`, `source` set to the intended primary source when you know it, and `status: "awaiting-client"`. Note the wart plainly when you report: the claim `status` enum holds four outcomes and no "pending" value, so `needsVerification` is what carries pending-ness and `awaiting-client` reads as "awaiting evidence," from the client or from a source. Don't invent a fifth enum value to fix it — enums are closed, and adding one is a deliberate schema change, not a call made at write time.

Do not verify anything here. `verify` chases sources and sets expiries; `brief` decides what will need chasing. Running the verification inside the brief makes the cheap artifact expensive, which defeats the reason it comes first.

**`media.json`.** Three to six concepts is normal. Each asset gets an ID from `M-001`, a `role` from the enum (`hero`, `diagram`, `screenshot`, `data-viz`, `proof-photo`, `decorative`), a `concept` that says what it shows **and why the article is worse without it**, and a `placement` naming a real outline heading.

`status` is `needed`, or `client-supplied` when the packet says the client already has the photo. `altText` and `caption` stay `null`. Alt text describes what is visibly in an image; writing it now produces a careful description of an imagined picture, which is worse than none — a screen-reader user gets confidently told about something that isn't there.

A plan that is one hero plus three decoratives is how "no relevant images" happens a second time. At least one asset should carry information the prose can't: the diagram of the flow, the screenshot of the actual audit output, the before/after of the page that got actioned.

## Output

Two artifacts and one chat response.

**1. `posts/<slug>/brief.md`** — frontmatter keys in this order: `post`, `client`, `version`, `angle`, `informationGain`, `formatFit`, `cannibalization`, `coverageTargets`, `titleSet` (with `searchTitle`, `h1`, `headline`, `dek`, `metaDescription`, `slug`, `alternates`). Then these six sections, in this order, and no others:

```
## Reader questions this must answer      numbered, the count in coverageTargets
## Outline                                H2/H3 nodes with closes / uses / work
## Claims to make (→ claims.json)         ID, text, factRef or the source to chase
## Internal links (from registry, real slugs only)   destinations, then sources
## Image concepts (→ media.json)          ID, role, what it shows, placement
## What this post deliberately does not cover        each with its reason
```

**2. `claims.json` and `media.json`** written per the schemas in `state.md`; `post.json` status → `briefed` with `updated` set; `registry.json`'s post entry updated in the same operation with `title` (the `h1`), `primaryKeyword`, `intent`, `status`, and `updated`. `openFindings` and `staleClaims` are not yours to set.

**3. Chat response** — six lines, no more:

```
Angle:              one sentence
Information gain:   one sentence
Format:             article — SERP is 9/10 explainers, no tool competition
Cannibalization:    none
Coverage:           7 questions committed — review fails the draft on each one left open
Claims / images:    11 claims (3 vault-backed, 8 to verify) · 4 image concepts
```

Then the single next step: `who-let-the-blogs-out verify <slug>` when claims need chasing, otherwise `who-let-the-blogs-out write <slug>`. If any state was malformed or stale, report it in one line and leave it alone — repair is a deliberate act, never a side effect of briefing.

### Cadence

Questions only at three points, and only when the answer isn't already in state: format fit is wrong, cannibalization says merge or refresh, or information gain came up empty. Two questions maximum per round, one round per decision, always with your recommendation attached so a "yes" is a valid answer.

Never ask what's already in the packet, the brand profile, the opinion bank, or the registry — asking a question the state answers is how a user learns the system doesn't read its own files, and after that they stop maintaining them. Never ask for a target word count; that's what Phase 5 replaced.

## Confirm and stop

The brief names, structures, and commits — it does not draft. No prose paragraph, no sample section, not one line "to show the tone."
