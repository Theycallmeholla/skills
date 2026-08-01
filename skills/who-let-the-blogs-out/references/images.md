# Images

Returns a concrete asset plan — for every image this article needs, what it must show, which heading it sits under, who has to produce it, and where it stands — plus the gap list of everything nobody has made yet.

**Reads:** `posts/<slug>/brief.md` · `posts/<slug>/draft-vN.md` · `posts/<slug>/media.json` · `posts/<slug>/post.json` *(read-only, for the client slug and `currentVersion`)*
**Writes:** `posts/<slug>/media.json`
**Stops at:** Never edits the draft — not even to move an `[IMAGE:]` marker. Never writes alt text for an asset that doesn't exist. Never generates final assets unless you were asked and confirmed the list first.

The test every asset has to pass: **does the article get worse without it?** If the honest answer is no, the asset is decoration, and the useful move is to mark it `role: decorative` and give it an empty alt attribute — not to dress it up as a diagram so the plan looks substantive. The failure this command exists to prevent is a photo of a smiling person at a laptop on an article about title tags. That image is not neutral: it costs page weight, it costs the reader a scroll, and it tells them the page was assembled rather than written.

`registry.json` is not in your Writes, and that is deliberate. Nothing in the index derives from the media plan — no status advances, no version increments — and bumping `updated` alone would announce that the post record moved when only its asset list did.

## Phase 1 — Extract concepts

Read `post.json` for the client slug and `currentVersion`, then `brief.md`, then `draft-v<currentVersion>.md`, then `media.json` if it exists.

If `media.json` is missing, this post was likely never briefed. Say so and point at `brief` rather than inventing a plan from the draft alone — the brief is where the article's angle was decided, and image concepts chosen without it tend to illustrate whatever paragraph caught your eye. If there is no draft yet, you can still work from the brief's outline; say which you used, because placements anchored to an outline heading may not survive the draft.

Concepts come from three places, in this order:

1. **The existing `media.json`** — the concepts `brief` committed to. These already have IDs. Carry them forward; don't re-conceive them because you'd have chosen differently.
2. **The draft's `[IMAGE: M-002 — ...]` markers** — where `write` actually put them. A marker whose ID has no entry in `media.json`, or an entry whose ID appears in no marker, is drift: report it, don't silently reconcile it.
3. **The draft prose itself** — this is where you earn your keep. Read for passages doing a job an image does better:
   - 100+ words describing an arrangement in space, a branching decision, or a sequence of steps → a **diagram**. If the prose says "the flow looks like this" and then draws it in sentences, the drawing should be a drawing.
   - An instruction to click, find, or read something in a real interface → an **annotated screenshot** of that exact screen, with the annotation specified: which element the callout points at and what it says.
   - Three or more numbers being compared, or one number changing over time → **data-viz**. Every number in it must trace to a `claims.json` entry or a vault fact. A chart is a claim wearing better clothes, and a chart nobody can source is a fabrication with axes.
   - A before/after the article asserts happened → two real captures or one composite. If the "after" doesn't exist yet, it's `needed` from the client — a mocked-up after is the same lie as an invented case study.
   - Work the client actually did, referenced in the packet → a **proof-photo**, which only they can supply.

Allocate new IDs monotonically from the highest `M-` already in the file, gaps included. `M-004` refers to the same concept forever even if the section it illustrated got cut.

**When a concept's section is gone from the draft:** if the heading was merely renamed, re-anchor it and say so. If the section is genuinely gone and the asset is still `needed`, drop the entry and report the drop — its ID stays burned. If the asset already exists (`client-supplied`, `sourced`, `generated`, `placed`), someone spent money or a site visit on it; leave it in place, flag it as orphaned, and let a human decide. Deleting an asset that exists is how a photo shoot gets paid for twice.

## Phase 2 — Assign roles and placement

**Roles come from the closed enum:** `hero` · `diagram` · `screenshot` · `data-viz` · `proof-photo` · `decorative`.

The middle four carry information the prose can't. Push there. A hero is the most defaulted-to and usually the least valuable asset on the page — it occupies the position of maximum attention to say the least. Keep one only when it does real work: the actual before/after the article is about, the annotated result, the thing that makes someone scroll. If the honest hero concept is "something visually related to the topic," name it `decorative` and let the person laying out the page decide whether the template needs it at all.

A plan of one hero plus three decoratives is how "no relevant images" happens a second time with a JSON file to prove it was planned. At least one asset must carry information the article would otherwise have to describe in words.

**Placement is anchored to a heading, quoted exactly as it appears in the draft:**

```
"after H2 'What actually has to change per city'"
"before H3 'Reading the coverage report'"
"top of post, above H1"
```

Not "paragraph 12." `revise` produces a new draft every time findings close, and paragraph counts shift on the first cut — a numeric anchor is wrong by the next version and nobody notices, because it still looks like a valid answer. A heading is a string a designer can Ctrl-F.

If your placement now disagrees with where the draft's `[IMAGE:]` marker sits, record the placement you believe is right and say the marker disagrees. Moving it is `revise`'s job, or the layout person's. `review` reads both files and will raise it as a `media` finding on its own.

**Captions where they earn their place.** A caption carries what the image can't show about itself: the data source, the date a UI screenshot was taken (interfaces age, and the caption is the only place a reader learns this one is from March), what to notice in a busy screenshot, attribution for client work used with permission. Skip it when the caption would restate labels already in the image — that's the same information twice, and the eye pays for it both times. A caption may be drafted before the asset exists when it carries outside information ("Data: C-007, 12 city pages, Mar–Jun 2026"); leave it `null` when it depends on what the image turns out to show.

## Phase 3 — Set status

The enum is `needed` · `client-supplied` · `sourced` · `generated` · `placed`.

**`needed` is the only status you may set on your own authority.** Every other value asserts that a file exists, and the gap list is computed from exactly this field — an optimistic status silently removes a task from someone's list, and the article ships with a hole where a diagram was assumed. Set `client-supplied` when someone confirmed the file exists or that it's theirs to produce from something they already have; "the client probably has job-site photos" is `needed` with a named ask attached. Set `sourced` or `generated` when told the asset was licensed or created. Set `placed` when told it is in the CMS at its placement.

**`altText` stays `null` until the asset actually exists.** Alt text describes what is visibly in an image. Written for an image nobody has made, it becomes a careful description of an imagined picture — and someone will ship it, because it reads finished. A screen-reader user then gets confidently told about a chart with three bars when the chart that got made has five.

When the asset does exist and you can see it, or its maker described it factually:

- Describe visible content in one sentence. No "image of," no "graphic showing" — assistive tech already announces that it's an image.
- Write from the file, not from the `concept` string. Concept says what it should show; alt says what it does show; those diverge precisely when someone made it slightly differently, which is the case alt text exists to handle.
- For a dense diagram, give the takeaway and let the prose carry the detail. A 200-word alt attribute is unusable — it can't be skimmed, paused, or re-read.
- No keyword stuffing. It has not been a ranking lever for years, and what it actually does is read a keyword salad aloud to someone who needed a description.
- **Decorative assets get `altText: ""`** — an empty string, not a description and not `null`. The empty string is a decision: it tells a screen reader to skip this image. `null` means "not yet known" and will eventually get filled in by someone being helpful.

`media.json` has no field for a filename, a source URL, or a license. Don't add one — the schema in `state.md` is what other commands read, and a key only this command writes is invisible to all of them. Put filenames, stock licenses, and photographer credits in your report and in the post's `notes.md`, which is the drawer for exactly this and isn't yours to write.

### Cadence

You will need to ask who has what. Ask it once, as a single list of specific asks with a name against each, at the end — not one question per asset as you go. Three questions is the ceiling for a round.

Never ask what the brief, the draft, or the packet already answers; a question the state answers teaches the user the system doesn't read its own files, and after that they stop maintaining them. Never ask the user to pick an art direction, a color, or a style — that isn't this command's job and it turns a five-minute gap list into a design review. Ask about generation exactly once, with the list attached, so a "yes" is a complete answer.

## Phase 4 — Report the gap list

Everything still at `needed` is the deliverable. The plan is a record; the gap list is the thing someone has to go do, so it's the part that gets read and it belongs at the top of your report with an owner against every row.

Sort by what blocks publication. A diagram you can commission today outranks a proof-photo that needs a site visit next month, and both outrank a decorative nobody will miss.

## Generating assets

Generating is a separate act the user opts into. If asked, list what would be generated — ID, role, concept, and what you'd make it with — and confirm before making anything. Producing five images nobody asked for is the same class of surprise as a command that rewrites six files: the work might even be good, and it still costs trust, because now nothing you run is predictable.

Generation fits some roles and falsifies others. Diagrams and decoratives generate cleanly. Data-viz generates well when it's built from `claims.json` numbers — that's a chart of verified figures, which is the good case. A generated screenshot is a fabricated interface presented as a real one, and a generated proof-photo is a picture of work that never happened; both are `fabrication`-category failures under the same doctrine that stops the draft inventing a case study. If someone wants a stylized stand-in for a screenshot, it's an `illustration` in spirit and `decorative` in the enum, and the caption has to say it isn't real.

After generating: set `status: "generated"`, then write `altText` from what was actually produced.

## Output

**1. `posts/<slug>/media.json`**, the full file per the schema in `state.md` — `version`, then `assets`, each with `id`, `role`, `concept`, `placement`, `status`, `altText`, `caption` and no other keys. `concept` says what it shows **and why the article is worse without it**, in that order, because the second half is what a reviewer uses to kill the asset if it's decoration.

**2. A chat response** in these four sections, in this order:

```
Gap list — 4 of 6 assets still needed

| ID    | Role       | What it shows                                          | Placement                                   | Who      |
|-------|------------|--------------------------------------------------------|---------------------------------------------|----------|
| M-003 | screenshot | Search Console coverage, callout on the 28 rows reading | after H3 'Reading the coverage report'       | client   |
|       |            | "Crawled – currently not indexed"                       |                                             |          |
| M-002 | diagram    | Which template blocks are shared across 40 city pages   | after H2 'What actually has to change'      | design   |
|       |            | and which are written per city                          |                                             |          |
| M-004 | data-viz   | Position change for the 12 rewritten pages, Mar–Jun     | after H2 'What the rewrite moved'           | you (C-007) |
| M-005 | proof-photo| Crew on the Katy job referenced in the packet           | after H3 'The Katy page'                    | client   |

Plan:   6 assets — 1 diagram, 1 screenshot, 1 data-viz, 1 proof-photo, 2 decorative, no hero
Asks:   Dana — Search Console export and the Katy photos. Both are yours alone to pull.
Drift:  draft-v2's marker for M-004 sits under 'What the rewrite moved'; I anchored it there. M-001's
        section was cut in v2 and it was still `needed`, so I dropped it. ID stays burned.
```

Keep `Asks` to the questions in your Cadence budget. Keep `Drift` to what you found and left alone — report it, don't repair it. If nothing drifted, drop the section rather than writing "none."

Then one line pointing at the next step: `who-let-the-blogs-out review <slug>` if the draft is ready to score, or the specific person who owes you a file.

## Confirm and stop

Plan the assets, anchor them to headings, set honest statuses, and hand back the gap list — but never edit the draft, never write alt text for an image that doesn't exist yet, and never generate an asset that wasn't asked for and confirmed.
