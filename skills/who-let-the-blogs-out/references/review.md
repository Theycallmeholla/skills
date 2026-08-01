# Review

Returns two scores on opposite scales and a ranked findings list with stable IDs, quoting evidence for each — and touches nothing.

**Reads:** `posts/<slug>/draft-vN.md`, `posts/<slug>/brief.md`, `posts/<slug>/packet.md`, `clients/<c>/brand.md`, `clients/<c>/opinion-bank.md`, `posts/<slug>/claims.json`, `posts/<slug>/media.json`
**Writes:** `posts/<slug>/review-vN.json`, `posts/<slug>/post.json` (status → `reviewed`), `registry.json` (`openFindings`, `status`)
**Stops at:** NEVER EDITS THE DRAFT. Not a typo, not a banned word, not a heading level.

That prohibition is in caps because it is the one the model is most tempted to break — you will read a sentence with an obvious fix and the fix will take four seconds. Do it once and the system loses the ability to say "score it, don't touch it," which is the entire reason `review` and `revise` are different commands. Every fix you can see goes in a finding; `revise` applies it.

## The two scores, and why they are never blended

**Rubric: 0–100, higher is better.** Eight weighted categories in `references/quality-rubric.md`. Load it and follow it — don't restate the categories here.

**Tells: 0–100, higher is WORSE.** Five weighted categories below. It measures the density of the pattern cluster readers recognize as generated.

A single blended number would let clean mechanics disguise an article that says nothing — 90 rubric and 15 tells is a good post; 90 rubric and 62 tells is a well-organized post that reads like a machine wrote it, and averaging them to 76 hides exactly the problem you ran the command to find. Report both, side by side, always. Never compute a combined figure, even as a convenience.

Neither score is an authorship verdict. Detectors are unreliable in both directions, plenty of humans write in these patterns, and well-edited AI output avoids them. Say so in the report. What you are measuring is tell density, which is real and actionable.

## Phase 0 — Locate the draft

Take `currentVersion` from the registry entry for the slug; confirm `posts/<slug>/draft-v<N>.md` exists. If the highest draft on disk is newer than the registry says, score the file on disk and report the disagreement in one line. Reporting drift is the job; repairing it is not.

If `posts/<slug>/review-v<N>.json` already exists for that same draft version, do not overwrite it. Append-only means a review file is the record of one draft, and re-scoring the same bytes produces a second opinion nobody can reconcile with the first. Report the existing scores and finding statuses instead, and say that a fresh score needs a new draft version from `revise`.

**Stateless mode.** `who-let-the-blogs-out review <path-to-file>` with no post record is permitted and writes nothing. It's the `ai-writing-detector` escape hatch for emails, landing copy, and anything outside the blog pipeline. Run the mechanical and judgment passes, report the tells score, and skip everything downstream of it — rubric, coverage, boundary, and headline checks all need a brief and a client that don't exist. Say plainly that no state was written.

## Phase 1 — Mechanical pass

Run `python3 scripts/tells_metrics.py posts/<slug>/draft-v2.md`. It returns JSON: lexicon hits, signpost phrases and paragraph openers, hedge density, em-dash / triad / bold / colon densities, "not just X but Y" frames, paragraph and sentence rhythm as coefficients of variation, bullet share, and a `reference_thresholds` block.

Read the thresholds as rules of thumb, not verdicts — that's what the script's own note says. A lower CV means more uniform means more tell-like. A technical audience tolerates more structure than a narrative one, so a 0.31 sentence CV in a spec-adjacent piece is worth less than the same number in a customer story.

If code execution is unavailable, estimate these by reading and say so in the report. An estimate labeled as an estimate is useful; an estimate presented as a measurement is a lie the next command inherits.

Under ~150 words: warn that scores are noisy, skip the rhythm category, and renormalize the remaining weights.

## Phase 2 — Judgment pass

Read the full draft and score what no script can.

- **Stance.** Is there at least one judgment a reader could disagree with? Are weak options given false equal weight? Are hedges standing in for actual conditions — "results typically vary" where "if your lot is under a quarter acre, skip this" belongs?
- **Texture.** Numbers, dates, prices, named tools, durations, edge cases, failure modes — versus adjectives. Placeholder-people anecdotes ("imagine Sarah, a small business owner"). "Studies show" with nothing cited. Does anything here suggest someone actually did the work?
- **Audience awareness.** Are basics the intended reader obviously knows being explained? Are their real objections answered or dodged? Explaining the obvious while ducking the hard question is a double tell.
- **The 500-companies test.** Could this be published by 500 other companies after swapping names and cities? This is the heaviest single question in the model and it outranks every other score in the system.
- **Structural intent.** Are sections evenly sized regardless of value? Does the conclusion restate the intro? Does anything digress, or does it march through an outline?

Score five weighted categories, each 0–100 where higher is more tell-like:

| Category | Weight | Primary evidence |
|---|---:|---|
| Substance & stance (`substance`) | 35% | Judgment pass: 500-companies test, stance, false balance, hedging |
| Texture & specificity (`texture`) | 25% | Judgment pass: specifics, anecdote authenticity, evidence trail |
| Rhythm & structure (`rhythm`) | 20% | Script CVs plus judgment: uniformity, symmetric sections, signposts, restated conclusion |
| Constructions & tics (`constructions`) | 12% | Script: triads, em dashes, "not just X but Y", bold and colon density, bullet share |
| Lexicon (`lexicon`) | 8% | Script: banned-phrase hits per 1000 words |

Overall is the weighted sum. Bands: **0–20 clean** · **21–40 light tells** · **41–60 noticeable** · **61–80 reads generated** · **81–100 template-grade**.

**Calibration guardrails.** These are the reason the model is worth running at all:

- The strongest tells are absences — no stance, no texture, no evidence trail — not word choices. A draft with zero banned words can still land at 70 because it commits to nothing.
- Cap each low-weight category's influence at its weight. No halo effects. A text with genuine stance and texture never scores above 40 on lexicon hits alone; twelve instances of "leverage" is a 12-point problem in an 8%-weight category, not a verdict on the article.
- Spotless mechanics cannot rescue a text that fails the 500-companies test. Substance is scored on content, not polish. If you find yourself lowering `substance` because the prose reads smoothly, you have inverted the model.

`references/voice-and-tells.md` owns the rule set behind all five categories. Load it and run its tells checklist rather than re-deriving the rules.

## Phase 3 — Rubric scoring

Score the eight categories in `references/quality-rubric.md` at their stated weights, 0–100 higher-is-better, and compute the weighted overall. Use `brief.md` for what was promised, `brand.md` for voice and audience, `claims.json` for whether accuracy is actually resolved, and `media.json` for whether the image plan was honored.

Two rubric categories have hard evidence available, so use it rather than impressions: `accuracy` cannot score above 60 with an unresolved row in `claims.json` (`needsVerification: true` and no status), and `completeness` is set by Phase 5, not by feel.

## Phase 4 — Boundary and fabrication check

These are the two failures that put someone's name on something they didn't say. Both are severity-locked to `high`, and neither can ever be `accepted` — there is no version of "leave it" for publishing a claim the author didn't make.

**Boundary.** Read the "Never say" section of `clients/<c>/opinion-bank.md` and the same section in `brand.md`. Check every item against the draft, including paraphrases — a boundary against "never call our process proprietary" is violated by "a methodology we developed in-house that nobody else runs." Quote the offending sentence in the finding. Category `boundary`.

**Fabrication.** Load `references/evidence-rules.md` and apply its three tiers. Every sentence that sounds first-hand — "we've seen this fail on dozens of sites," "in our experience," a confident specific number with no source — gets traced to `packet.md` or a `source: first-hand` entry in the client's fact vault via `claims.json`. No trace, it's a finding. Also flag tier drift in either direction: a tier-3 inference written with tier-2 confidence, or a tier-2 sourced fact written in the author's voice. Category `fabrication`.

Say explicitly in the report when either category has an open finding, because both block `publish`.

## Phase 5 — Coverage check against the brief

This is the depth mechanism and the reason "not long enough" never needs a word count.

Read the numbered reader questions under **Reader questions this must answer** in `brief.md`. That list is the depth target: seven real questions, not 1,500 words. Walk them one at a time and mark each **answered**, **partially answered**, or **unanswered** — a question the draft names in a heading and then talks around is partial, not answered.

Every unanswered question is one `completeness` finding, quoting the brief's question verbatim and naming where in the draft it should have landed. Every partial one is a `completeness` finding at `medium`. Do not collapse three open questions into one finding called "coverage gaps" — `revise` fixes what it can see, and a merged finding gets half-fixed and closed.

Also check the brief's **What this post deliberately does not cover** list. A draft that wandered into declared out-of-scope territory is padding, and padding is a `completeness` finding too — the failure mode of depth-as-coverage is a writer who hits the questions and then keeps going.

`completeness` in the rubric is set by this phase: seven targets with two unanswered is not an 85.

## Phase 6 — Headline contract check

Load `references/headline-contract.md` and run the checklist at the bottom of it against the draft's front matter and heading structure. Findings land in `structure` for craft and `technical-seo` for field coordination — no new category.

One boundary to report honestly: Google's concern is **visual** heading prominence, and blog emits markdown. Whether the rendered H1 outranks every H2 is a CMS template decision no amount of markdown discipline controls. So report prominence as a recommendation carrying that caveat, not a pass/fail. A checklist item that silently means "we hope so" is worse than one marked "verify in the template."

The exception: if the post has a live `url` in the registry, fetch the rendered page and check for real. At that point it stops being advisory and becomes a factual `structure` finding.

## Phase 7 — Emit findings

Every finding needs four things or it isn't one.

**A stable ID.** `BL-001`, monotonic per post. Scan every existing `review-v*.json` in the post directory for the highest `BL-NNN` and continue from there. Never reuse, never renumber to close a gap.

**Carry-forward, not re-issue.** A finding still open from `review-v1.json` that draft-v2 didn't fix appears in `review-v2.json` with **the same ID**. Allocating `BL-014` for what was already `BL-006` destroys the one thing IDs are for — being able to say "you closed six of nine, these three are still open." A finding marked `accepted` in a prior review is not re-raised at all; re-raising accepted findings is exactly how a review tool becomes a nag people stop running. The exception is `boundary` and `fabrication`, which can't be accepted in the first place.

**A category from the closed enum**, no exceptions and no near-synonyms: `intent` · `accuracy` · `original-value` · `completeness` · `structure` · `brand-fit` · `conversion` · `technical-seo` · `voice-tells` · `media` · `boundary` · `fabrication`.

**A `consequence`** — the specific thing that breaks if nobody acts. Not a restatement of the claim in worse words. "Publishes as an article any competitor could have written, so it earns no link and no repeat reader" is a consequence. "Reduces quality" is not. If you can't write what concretely goes wrong, you have a preference, not a finding — drop it. Findings you can't defend are how a review report gets skimmed instead of read.

Also give each finding a `location` precise enough to act on (`H2 'What Google actually wants'`, `paragraph 3`, `front matter: metaDescription`) and a `claim` that quotes the evidence — one sentence maximum. The report analyzes the draft, it doesn't reproduce it.

Severity: `high` when it blocks publishing or misleads a reader, `medium` when it costs the post real value, `low` when it's craft. `boundary` and `fabrication` are locked to `high` regardless of how minor the instance looks.

Write `posts/<slug>/review-v<N>.json` in the schema from `references/state.md` with `status: "open"` on every finding and the three resolution fields `null`. Then update the post's `openFindings` in `registry.json` in the same operation, along with `updated`. A registry that lags its records starts recommending things that aren't true.

Set `post.json` status to `reviewed` and mirror it in the registry alongside `openFindings`. This is the only status transition this command makes, and it says "a score exists for the current draft" — nothing more. It does not mean the findings were addressed; `revise` moves the post back toward `drafted` when it produces the next version.

Leave every other field in `post.json` alone. `currentVersion` in particular belongs to whichever command wrote the draft.

## Output

Deliver in chat, in this order, plus the JSON file:

```
## <slug> — draft-v2

**Rubric 78/100** (higher is better)  ·  **Tells 34/100 — light tells** (higher is worse)
Two scales, never blended. Neither is an authorship verdict.

| Rubric category | Score | Weight |    | Tells category | Score | Weight |
(both tables, side by side or stacked — every category, both scales)

### Blocking
BL-014  fabrication  high  — <one line>   ← blocks publish
(or: "None. No boundary or fabrication findings.")

### Coverage — 5 of 7 reader questions answered
3. "How do I keep 40 city pages from reading identical?"  unanswered
6. "What does this cost to maintain?"                     partial

### Findings — 9 open, worst first
BL-014  fabrication      high    front matter, ¶2  "we've rebuilt this for dozens of clients"
        → not in packet or vault; publishes an experience claim the author can't defend
(one block per finding: ID, category, severity, location, quoted evidence, consequence)

### Headline contract
Pass/fail per check, with visual prominence marked as a recommendation and why.

### Top fixes, ranked by score impact
1. ... (name the category and the points it recovers — a stance fix outranks deleting every "delve")

Written: posts/<slug>/review-v2.json · registry.json (openFindings: 9)
```

Rank fixes by expected impact, not by order found. Never recommend fake typos, invented anecdotes, fabricated experience, or detector-evasion tricks — fixes add stance, specificity, and asymmetry, they never manufacture fake humanity. If asked to compare two draft versions, score both and show per-category deltas naming which edits moved which categories.

## Confirm and stop

Scores and findings only. The draft file is not yours to edit — hand every fix to `revise`.
