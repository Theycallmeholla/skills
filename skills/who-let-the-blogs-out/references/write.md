# Write

Drafts the full article from the brief and returns a versioned markdown file — YAML front-matter carrying the brief's title set, the article body, and a publish checklist naming every image, link, and piece of client evidence still outstanding.

**Reads:** `posts/<slug>/brief.md` · `posts/<slug>/research-vN.md` · `posts/<slug>/packet.md` · `clients/<c>/brand.md` · `clients/<c>/opinion-bank.md` · `clients/<c>/facts.json` · `posts/<slug>/claims.json` · `posts/<slug>/media.json` *(read-only, for the checklist)*
**Writes:** `posts/<slug>/draft-v(N+1).md` · `posts/<slug>/post.json` · `registry.json`
**Then runs:** `review`, automatically. A draft never reaches the author unscored.
**Stops at:** Never implies experience absent from the packet or the vault. Never invents credentials, quotes, results, or case studies. Never runs without a brief. Never scores itself. Never changes the brief's `titleSet`.

## Phase 1 — Load the brief, the voice rules, and the headline contract

Read `posts/<slug>/post.json` first: it gives you the client slug, the status, and `currentVersion`. Then read `brief.md`.

**No brief, no draft.** If `brief.md` is missing — or `post.json` still says `idea` or `interviewed` — say so and point at `brief`. Do not improvise an outline and start writing. A draft written without a brief is the exact "nobody thought this through" failure the system exists to prevent: nobody chose the angle, nobody checked whether this keyword is already covered, nobody committed to the reader questions. Producing a polished article on top of that hides the problem instead of surfacing it, and the polish is what makes people trust it.

If `.blog/` doesn't exist at all, say so and point at `brand`.

Then load and follow, without restating them here:

- `references/voice-and-tells.md` — the voice rulebook. Read it before the first sentence, not after the draft exists. Its rules are generative; retrofitting them onto finished prose produces prose that reads retrofitted.
- `references/evidence-rules.md` — the three tiers of assertion and what may never be invented. This is the anti-fabrication mechanism, and tier drift is the failure it catches.
- `references/headline-contract.md` — heading craft, the skim test, and the six title fields you are honoring rather than deciding.

**Read the research file the brief names.** `brief.md`'s frontmatter carries a `research` key pointing at `research-vN.md` — the SERP teardown, the table-stakes subtopics, the reader questions found in the wild, the practitioner terminology, the entity list, and the weaknesses that produced the gap.

This is the evidence behind the brief's conclusions, and it is the reason this command can write with any specificity at all. The brief tells you the angle; the research tells you what the ranking pages actually said, at what depth, and what they ducked — which is what lets a section land as "the four guides on page one all stop at the template and none of them says what happens on the 40th page" rather than as a generic claim of novelty.

Read its `connectors` block too. Research gathered while a connector was `degraded` or `unavailable` is thinner than it looks, and a draft resting on it should say less confidently what the SERP contains.

**Do not re-run the research.** `brief` already did the SERP analysis, the teardown, the discourse pass, the format-fit challenge, the cannibalization check, and the claim list. Re-deriving them here produces a second opinion that silently disagrees with the committed one. If the brief looks wrong, say why and stop — that is a reason to re-run `brief`, not a reason to draft around it.

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

### Sections that stand on their own

Each H2 section should make sense read alone. Its central claim should not depend on "as we saw above" or "building on the previous section" to be recoverable — a reader who lands mid-page from a search result, or skims to the section that matches their question, should get a complete answer there.

This is a reader-first rule that happens to survive passage-level retrieval. It is **not** chunking, not question-shaped headings, and not a word band. Google's own guidance says there is no requirement to break content into small pieces and no need to write in a particular way for generative search; sections that stand alone are simply better for the person reading them, and that is the whole justification.

Cross-references are fine where they add something. What breaks the rule is a section whose point is *unavailable* without the one before it.

### Language, entities, and coverage

Cover the subject the way a practitioner would: related entities, supporting concepts, real terminology, the questions that come after the obvious one. All of that arrives through comprehensive coverage, never from a keyword list. If a sentence exists only to hold a phrase, delete it.

**One canonical entity, named consistently.** The brief's `canonicalEntity` is what this page is about; the research file's `entities` list is what a knowledgeable author would inevitably mention alongside it. Use the field's real terminology from the research — including terms whose meaning has shifted, used the way the field currently uses them — and don't rotate synonyms for the same thing across the draft. Synonym rotation reads as padding to a person and as ambiguity to anything parsing the page.

**Every coverage target gets answered, not gestured at.** An answer means a reader with that question closes the tab satisfied — a specific recommendation, the condition under which it changes, and what happens if they get it wrong. A heading that names the question and then circles it is worse than omitting the question, because the brief promised it and the reader now believes it was handled. This is where depth actually happens: the brief committed to seven questions because seven is what the reader has, and `review` fails the draft once per unanswered one.

Where the packet gives the author a stance, take it in their voice. Where it gives a gap, write from cited research in a neutral voice — an honest gap beats a fabricated conviction every time, and a gap is recoverable by asking one question later.

### Experience, authority, and anti-fabrication

Every sentence that sounds first-hand must trace to a line in the packet or a `source: first-hand` vault fact. "We've seen this fail on dozens of sites" is a first-hand claim even though it names nothing, and so is a confident unsourced number — the reader assumes you know it from doing the work.

Nothing about credentials, years in business, customer outcomes, quotes, case studies, proprietary processes, awards, test results, site visits, or product usage gets written unless the packet or the vault supplies it. When the article would clearly be stronger with one and none exists, the move is a **client evidence needed** line in the publish checklist. That costs the client one email; a plausible invented case study costs them a claim they have to defend in public under their own name.

Where an author byline, a named reviewer, or an About-page improvement would materially strengthen the page, put it in the checklist rather than writing it into the article.

### Links and evidence

Cite every material claim that needs verification, using the `claims.json` entry's `source` URL — prefer the primary source over anyone's summary of it. Internal links go in only where they help the reader continue a real journey: use the real slugs the brief pulled from the registry, or `[anchor text](INTERNAL: description of target page)` where the brief only identified a destination type. No quotas in either direction — don't add links to hit a number and don't cap the sources a technical piece genuinely needs. Competing SEO articles are positioning intel, never a factual backbone.

Record which claim IDs you actually used in the draft's `uses_claims` front-matter list, and which opinion-bank entries in `uses_bank`. `verify`, `review`, and `refresh` all depend on those lists reflecting reality, and you are the only command that knows what made it into the prose. They live in the draft rather than in `claims.json` or the bank precisely so the prose and the list can never disagree — same file, same write.

### Images

Place inline markers where the brief's image concepts belong — `[IMAGE: M-002 — diagram of the title-rewrite decision path]` — so `images` and the person laying the page out both know the intended position. Write no alt text for an asset that doesn't exist; alt text describes what is visibly in an image, and inventing it for an imagined picture is worse than leaving it null. Suggest captions only where the caption adds context the image alone can't carry.

### Schema

Choose structured data only where it fits what's visibly on the page: `Article`/`BlogPosting` for a standard post, `HowTo` for genuine numbered instructions, `LocalBusiness` where the brand profile supports it, `BreadcrumbList` where the site uses breadcrumbs, or `none`. Never default to FAQ schema.

The recommendation and a one-line rationale go in the front-matter. The **markup itself** goes in the paste-ready block at the bottom of the file, never inline in the body — see Output.

Validate the JSON-LD with `mcp__schema-org__validate_jsonld` before emitting it. A typo'd property or wrong nesting produces markup that parses as nothing, silently. If the validator is unavailable, emit the markup anyway and say it went out unvalidated.

The validator checks schema.org vocabulary. It cannot check that the markup describes what is actually visible on the page — that judgment is yours and it is the rule that matters more.

### Do not implement these

Every item below is either explicitly rejected by [Google's AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) or is a vendor correlation being sold as a rule. They recur constantly in SEO advice, including in otherwise-good tooling, and each one costs the reader something:

- **llms.txt** — Google states it neither harms nor helps
- **Fixed answer word bands** ("definitions in 25-50 words", "answers in 40-60 words") — no provider documents a length threshold for citation
- **FAQPage schema as a citation play** — Google no longer shows FAQ rich results; an FAQ added for markup is padding with a false justification
- **Chunking content into small pieces** — "There's no requirement to break your content into tiny pieces"
- **Rewriting specifically for AI** — "You don't need to write in a specific way just for generative AI"
- **Flesch-score or readability targets** — vendor-reported association, never a calibrated effect
- **Source quotas** ("cite N sources per section") — cite what the claims need
- **Treating vendor citation-share datasets as causal**

The durable levers are the ones this command already enforces: a genuine point of view, claims traceable to named dated sources, sections that stand alone, substantive freshness, and structured data that matches visible content.

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

`drafted` is what you set and it is momentary: `review` runs next and moves it to `reviewed`. Set it honestly anyway rather than anticipating the chain — if `review` fails to run, the record should say what actually happened.

**Record what the draft used.** `uses_claims` lists every claim ID that made it into the prose; `uses_bank` lists every opinion-bank entry (`S-004`, `P-002`) you drew on. Both go in the front matter of the draft you just wrote.

These are not bookkeeping. `verify`, `publish`, and `refresh` all read them to know what the live article actually asserts — the staleness count depends on the first, and tracing a superseded position to the posts still arguing it depends on the second. You are the only command that knows what survived the writing, and the lists live in the draft precisely so the prose and the record can never disagree.

If anything you read was malformed or stale — a claim ledger with IDs the brief never mentions, a `facts.json` entry past its `reverifyBy` — report it and keep drafting. Don't repair it.

## Phase 5 — Hand off to `review`

Run `review` on the version you just wrote. Always, with no flag to skip it.

This is a chained command, not a mode of this one: `review` reads the rubric and the tells model, writes `review-v(N+1).json`, and moves `post.json` to `reviewed`. Both commands keep their own declared paths, and the rule that a writer never grades its own work is preserved — `review` has no stake in the draft.

The point is that the author reads the article and its findings together, instead of forming an opinion about a draft before anything has scored it. **Lead your report with any `boundary` or `fabrication` findings the review raised.** Those two are severity-locked, cannot be accepted, and block `publish` — better learned now than at publish time.

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
canonical_entity: "local SEO location pages"
search_intent: informational
unique_value: "One sentence: what this article gives the reader that page one doesn't."
schema_recommendation: "BlogPosting — standard editorial post, no step sequence to mark up."
reviewer: "YMYL only — the kind of qualified expert who should sign off. Omit otherwise."
review_date: "2027-08-01 — time-sensitive claims only. Omit otherwise."
word_count: 1840
research: research-v1.md
uses_claims: [C-001, C-003, C-007]
uses_bank: [S-004, P-002]
---

# How to Build Location Pages That Do Not Look Mass-Produced

[dek paragraph]

[article body, with [IMAGE: M-002 — ...] markers in place]

---

## Publish checklist
- [ ] Replace INTERNAL link placeholders with real URLs
- [ ] Image concepts: M-002 diagram after H2 "Why Google rewrites titles" — status `needed`
- [ ] Client evidence needed: the actual turnaround range for a 40-page city rollout
- [ ] Retrievability: primary content is crawlable text, not JS-gated; robots.txt doesn't block the crawlers this client cares about
- [ ] [post-specific: expert review, an unanswered coverage target]

---

## CMS fields — paste block

**Excerpt**
[2-3 sentences. What the post is and what the reader leaves with.]

**Category**
[one value from brand.md's taxonomy]

**Tags**
[values from brand.md's taxonomy, never invented]

**JSON-LD** — validated, or `none` with a one-line reason
```json
{ "@context": "https://schema.org", "@type": "BlogPosting", ... }
```
```

Front-matter title fields are copied from the brief's `titleSet` verbatim. `canonical_entity` comes from the brief. `word_count` counts the body — not the front-matter, checklist, or paste block. Omit `reviewer` and `review_date` entirely when they don't apply; an empty field reads as an unanswered question.

### The paste block

Everything a CMS editor asks for that the front-matter doesn't already carry, delimited so it can be copied without dragging the article along. It exists here rather than in `publish` because `publish` runs *after* the post is live — fields delivered then arrive after they were needed.

**Category and tags come from `brand.md`'s `taxonomy` block and are never invented.** Invented tags produce forty near-synonyms across a client's blog inside a few months, after which nothing can be grouped or filtered. If the client has no taxonomy recorded, propose values and say plainly that no vocabulary exists yet — that's a gap for `brand`, not a licence to freestyle.

**`none` is a valid JSON-LD output.** When nothing on the page warrants markup, say so with the reason. Do not emit `BlogPosting` because a field looked empty, and never emit `FAQPage`.

Then, in chat: **any `boundary` or `fabrication` findings from the chained review, first and by ID**, then three or four lines — the version you wrote, the angle you took, any coverage target you could not answer and why, and anything the draft did that the brief did not anticipate. Then the review's headline scores.

Not a recap of the article. Point at `images` if assets are still `needed`, and at `revise` when findings are open. Don't point at `review` — it already ran.

## Confirm and stop

Draft it, self-check it, version it — but never invent experience the packet doesn't hold, never rewrite the brief's title set, and never score your own draft.
