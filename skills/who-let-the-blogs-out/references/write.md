# Write

Drafts the full article from the brief and returns a versioned markdown file — YAML front-matter carrying the brief's title set, the article body, and a publish checklist naming every image, link, and piece of client evidence still outstanding.

**Reads:** `posts/<slug>/brief.md` · `posts/<slug>/packet.md` · `clients/<c>/brand.md` · `clients/<c>/facts.json` · `posts/<slug>/claims.json` · `posts/<slug>/media.json` *(read-only, for the checklist)*
**Writes:** `posts/<slug>/draft-v(N+1).md` · `posts/<slug>/post.json` (status → `drafted`) · `registry.json`
**Stops at:** Never implies experience absent from the packet or the vault. Never invents credentials, quotes, results, or case studies. Never runs without a brief. Never scores itself. Never changes the brief's `titleSet`.

## Phase 1 — Load the brief, the voice rules, and the headline contract

Read `posts/<slug>/post.json` first: it gives you the client slug, the status, and `currentVersion`. Then read `brief.md`.

**No brief, no draft.** If `brief.md` is missing — or `post.json` still says `idea` or `interviewed` — say so and point at `brief`. Do not improvise an outline and start writing. A draft written without a brief is the exact "nobody thought this through" failure the system exists to prevent: nobody chose the angle, nobody checked whether this keyword is already covered, nobody committed to the reader questions. Producing a polished article on top of that hides the problem instead of surfacing it, and the polish is what makes people trust it.

If `.blog/` doesn't exist at all, say so and point at `brand`.

Then load and follow, without restating them here:

- `references/voice-and-tells.md` — the voice rulebook. Read it before the first sentence, not after the draft exists. Its rules are generative; retrofitting them onto finished prose produces prose that reads retrofitted.
- `references/evidence-rules.md` — the three tiers of assertion and what may never be invented. This is the anti-fabrication mechanism, and tier drift is the failure it catches.
- `references/headline-contract.md` — heading craft, the skim test, and the six title fields you are honoring rather than deciding.

**Do not re-run the research.** `brief` already did the SERP analysis, the format-fit challenge, the cannibalization check, and the claim list. Re-deriving them here produces a second opinion that silently disagrees with the committed one. If the brief looks wrong, say why and stop — that is a reason to re-run `brief`, not a reason to draft around it.

Before drafting, build a working map (in your head or in scratch, not on disk): every numbered reader question in the brief → the outline section that answers it → the specific evidence that makes the answer true → its tier. Evidence comes from the packet (tier 1), a `facts.json` entry by ID (`F-007`, tier 1 or 2 depending on its `source`), a `claims.json` entry by ID (`C-003`, tier 2), or your own reasoning (tier 3). A reader question with nothing in the evidence column is a gap, and you now know it before you've written a paragraph around it rather than after.

### Cadence

`write` does not interview. If the map shows a gap, you have one question you may ask before drafting — *"the brief commits to answering X and the packet has nothing on it; do you want to answer it now, or should I write it from cited research and flag it?"* — asked once, up front, never mid-draft. Then proceed either way. Never ask permission to invent something, and never ask the author to confirm a fact you could have read in the vault.

## Phase 2 — Draft

### Structure

- **One H1**, exactly the brief's `titleSet.h1`. Copy it; do not improve it.
- **Dek** immediately under the H1 as a paragraph, not a heading — the brief's `titleSet.dek` verbatim.
- **Opening:** lead with the reader's problem or a concrete payoff. No throat-clearing, no "in today's landscape." Work the primary keyword in naturally if it fits the sentence; if it doesn't, leave it out — it will appear on its own in a body that actually covers the subject.
- **H2s are the brief's coverage targets**, phrased as the reader's questions rather than keyword slots. Order them the way the reader's thinking moves, not the way the outline happened to be typed.
- **Paragraphs deliberately uneven**, sections asymmetric — the 400 words go where the real expertise is. Lists and tables only for genuinely parallel items.
- **FAQ, conditional:** only when distinct questions remain that the body genuinely didn't answer. Never for length, keywords, or rich results — Google no longer shows FAQ rich results, so an FAQ added for schema is pure padding with a false justification attached.
- **CTA** aligned to the business goal in `brand.md`, not a generic "contact us."

### Language and coverage

Cover the subject the way a practitioner would: related entities, supporting concepts, real terminology, the questions that come after the obvious one. All of that arrives through comprehensive coverage, never from a keyword list. If a sentence exists only to hold a phrase, delete it.

**Every coverage target gets answered, not gestured at.** An answer means a reader with that question closes the tab satisfied — a specific recommendation, the condition under which it changes, and what happens if they get it wrong. A heading that names the question and then circles it is worse than omitting the question, because the brief promised it and the reader now believes it was handled. This is where depth actually happens: the brief committed to seven questions because seven is what the reader has, and `review` fails the draft once per unanswered one.

Where the packet gives the author a stance, take it in their voice. Where it gives a gap, write from cited research in a neutral voice — an honest gap beats a fabricated conviction every time, and a gap is recoverable by asking one question later.

### Experience, authority, and anti-fabrication

Every sentence that sounds first-hand must trace to a line in the packet or a `source: first-hand` vault fact. "We've seen this fail on dozens of sites" is a first-hand claim even though it names nothing, and so is a confident unsourced number — the reader assumes you know it from doing the work.

Nothing about credentials, years in business, customer outcomes, quotes, case studies, proprietary processes, awards, test results, site visits, or product usage gets written unless the packet or the vault supplies it. When the article would clearly be stronger with one and none exists, the move is a **client evidence needed** line in the publish checklist. That costs the client one email; a plausible invented case study costs them a claim they have to defend in public under their own name.

Where an author byline, a named reviewer, or an About-page improvement would materially strengthen the page, put it in the checklist rather than writing it into the article.

### Links and evidence

Cite every material claim that needs verification, using the `claims.json` entry's `source` URL — prefer the primary source over anyone's summary of it. Internal links go in only where they help the reader continue a real journey: use the real slugs the brief pulled from the registry, or `[anchor text](INTERNAL: description of target page)` where the brief only identified a destination type. No quotas in either direction — don't add links to hit a number and don't cap the sources a technical piece genuinely needs. Competing SEO articles are positioning intel, never a factual backbone.

Track which claim IDs you actually used. `verify` and `refresh` both depend on `claims.json`'s `appearsIn` reflecting reality, and you are the only command that knows what made it into the prose.

### Images

Place inline markers where the brief's image concepts belong — `[IMAGE: M-002 — diagram of the title-rewrite decision path]` — so `images` and the person laying the page out both know the intended position. Write no alt text for an asset that doesn't exist; alt text describes what is visibly in an image, and inventing it for an imagined picture is worse than leaving it null. Suggest captions only where the caption adds context the image alone can't carry.

### Schema

Recommend structured data only where it fits what's visibly on the page: `Article`/`BlogPosting` for a standard post, `HowTo` for genuine numbered instructions, `LocalBusiness` where the brand profile supports it, `BreadcrumbList` where the site uses breadcrumbs, or `none`. Never default to FAQ schema. Put the recommendation and a one-line rationale in the front-matter, not markup in the body.

### YMYL

For health, medical, legal, financial, or safety content: current authoritative sources only, education explicitly distinguished from professional advice in the text, no diagnoses or guarantees, and a `reviewer` field in the front-matter naming the kind of qualified expert who should sign off before publication. An unmarked YMYL article is a high-severity `accuracy` finding when `review` runs, and the cost of being wrong here isn't a ranking drop.

## Phase 3 — Self-check against boundaries

Run this on yourself before emitting. It is a pass/fail check for the three things that must not ship, **not a score** — scoring belongs to `review`, which reads the rubric and the tells model and has no stake in the draft. A writer that grades its own work grades it generously, every time, and the moment a draft arrives pre-scored nobody re-scores it.

1. **Every first-hand-sounding sentence traced.** Walk the draft and name the packet line or fact ID behind each one. Anything you can't trace gets rewritten into tier 2 with a citation, into tier 3 as openly framed judgment, or cut.
2. **Every item on the client's "Never say" list absent.** Read that section of `brand.md` again against the finished text — those lists exist because someone got burned, and the phrasing usually creeps back in during drafting rather than being consciously chosen.
3. **Every coverage target answered.** Walk the brief's numbered list against the finished sections. Anything unanswered gets written or gets named in the checklist and in your return message — never quietly dropped.
4. **Title set unchanged.** If the article ended up making a different argument than the brief promised, keep the title set as-is and say so plainly in your return message so `review` can raise it. A brief the draft can silently overwrite has stopped being a gate.

Then run the tells checklist at the bottom of `voice-and-tells.md` and fix what it catches. `scripts/tells_metrics.py <path>` gives a mechanical read; treat it as a smoke alarm, not a grade.

## Phase 4 — Emit the version

Read `currentVersion` from `post.json` and write `draft-v(N+1).md`. Leave `draft-vN.md` byte-identical — `refresh` and `revise` read history as a diff, and an edited prior version makes that diff a lie. Then set `post.json`'s `currentVersion` to N+1, `status` to `drafted`, and `updated` to today, and update this post's row in `registry.json` in the same operation: `status`, `currentVersion`, `title` (the H1), `updated`. Leave `openFindings` alone — that's `review`'s field.

If anything you read was malformed or stale — a claim ledger with IDs the brief never mentions, a `facts.json` entry past its `reverifyBy` — report it and keep drafting. Don't repair it.

## Output

The file at `posts/<slug>/draft-v(N+1).md`, in this shape:

```markdown
---
search_title: "Local SEO Location Pages: A Scalable Framework | Cursive Media"
h1: "How to Build Location Pages That Do Not Look Mass-Produced"
headline: "How to Build Location Pages That Do Not Look Mass-Produced"
dek: "A practical framework for creating useful city pages at scale."
meta_description: "Learn how to create useful, differentiated location pages without producing thin or repetitive local SEO content."
slug: local-seo-location-pages
title_alternates: ["Alt search title 2", "Alt search title 3"]
primary_keyword: "local seo location pages"
search_intent: informational
unique_value: "One sentence: what this article gives the reader that page one doesn't."
schema_recommendation: "BlogPosting — standard editorial post, no step sequence to mark up."
reviewer: "YMYL only — the kind of qualified expert who should sign off. Omit otherwise."
review_date: "2027-08-01 — time-sensitive claims only. Omit otherwise."
word_count: 1840
---

# How to Build Location Pages That Do Not Look Mass-Produced

[dek paragraph]

[article body, with [IMAGE: M-002 — ...] markers in place]

---

## Publish checklist
- [ ] Replace INTERNAL link placeholders with real URLs
- [ ] Image concepts: M-002 diagram after H2 "Why Google rewrites titles" — status `needed`
- [ ] Client evidence needed: the actual turnaround range for a 40-page city rollout
- [ ] [post-specific: schema validation, expert review, an unanswered coverage target]
```

Front-matter fields are copied from the brief's `titleSet` verbatim. `word_count` counts the body, not the front-matter or the checklist. Omit `reviewer` and `review_date` entirely when they don't apply — an empty field reads as an unanswered question.

Then, in chat, three or four lines: the version you wrote, the angle you took, any coverage target you could not answer and why, and anything the draft did that the brief did not anticipate. Not a recap of the article. Point at `images` if assets are still `needed`, and at `review` for scoring.

## Confirm and stop

Draft it, self-check it, version it — but never invent experience the packet doesn't hold, never rewrite the brief's title set, and never score your own draft.
