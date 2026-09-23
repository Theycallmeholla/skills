# Review

Returns two scores on opposite scales and a ranked findings list with stable IDs, quoting evidence for each — and touches nothing.

**Reads:** `posts/<slug>/draft-vN.md`, `posts/<slug>/brief.md`, `posts/<slug>/research-vN.md`, `posts/<slug>/packet.md`, `clients/<c>/brand.md`, `clients/<c>/opinion-bank.md`, `clients/<c>/voice-baseline.json` *(when present)*, `posts/<slug>/claims.json`, `posts/<slug>/media.json`
**Writes:** `posts/<slug>/review-vN.json`, `posts/<slug>/post.json` (status → `reviewed`), `registry.json` (`openFindings`, `status`)
**Stops at:** NEVER EDITS THE DRAFT. Not a typo, not a banned word, not a heading level.

That prohibition is in caps because it is the one the model is most tempted to break — you will read a sentence with an obvious fix and the fix will take four seconds. Do it once and the system loses the ability to say "score it, don't touch it," which is the entire reason `review` and `revise` are different commands. Every fix you can see goes in a finding; `revise` applies it.

Load `references/governing-rules.md` before scoring. Three rules change what this command raises: Rule 1 (a draft that argues a different thesis is an `intent` finding at `high`), Rule 3 (a claim written stronger than its source supports is an `accuracy` finding at `high`), and Rule 4 (a stance the packet doesn't record is a `fabrication`, not voice). Rule 9 governs the chat report — see Output.

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

### Client thresholds beat global ones, where they exist

If `clients/<c>/voice-baseline.json` exists, use its `calibrated` values in place of the script's globals for the metrics it covers, and the globals for everything else. **Say in the report which thresholds came from where.** A finding raised against a global threshold when a baseline exists but deliberately excluded that metric should be legible as exactly that.

The point is that an author who genuinely writes with em-dashes at 5 per 1,000 was being flagged on every draft forever, because the global threshold had never met them. A calibrated baseline stops charging a writer for their own voice.

Three things the baseline may never do, and the file records refusals in `refused` for exactly this reason:

- **It cannot tighten a rhythm threshold past the global floor.** A corpus more uniform than the tell threshold does not license more uniformity; uniformity is a symptom, not a house style. Report the refusal rather than silently applying the global.
- **It cannot calibrate lexicon at all.** "Delve," "leverage," "seamless" are not a style worth preserving.
- **It cannot touch the judgment layer.** Substance, texture, audience fit, and the author-value check are scored by reading, and no corpus can teach the system that this client is allowed to have no opinion.

No baseline is the normal case, not a gap. Fall back to globals and say so in one line.

If code execution is unavailable, estimate these by reading and say so in the report. An estimate labeled as an estimate is useful; an estimate presented as a measurement is a lie the next command inherits.

Under ~150 words: warn that scores are noisy, skip the rhythm category, and renormalize the remaining weights.

## Phase 2 — Judgment pass

Read the full draft and score what no script can.

- **Stance.** Is there at least one judgment a reader could disagree with? Are weak options given false equal weight? Are hedges standing in for actual conditions — "results typically vary" where "if your lot is under a quarter acre, skip this" belongs?
- **Texture.** Numbers, dates, prices, named tools, durations, edge cases, failure modes — versus adjectives. Placeholder-people anecdotes ("imagine Sarah, a small business owner"). "Studies show" with nothing cited. Does anything here suggest someone actually did the work?
- **Audience awareness.** Are basics the intended reader obviously knows being explained? Are their real objections answered or dodged? Explaining the obvious while ducking the hard question is a double tell.
- **The author-value check.** Does this article contain meaningful value specific to this author or business — real experience, a real example, a real number, a real process, a perspective only they have? If the honest answer is no, that is a `high` `original-value` finding, and the fix named in it is *"strengthen it with X"*, never *"disagree with something."* This is a heavy question, and it sits at priority 6 — it does not outrank the thesis, the evidence, or the search intent. An article that agrees with the consensus and adds a practitioner's specifics passes. An article that manufactured a fight to look original fails twice: here, and under `fabrication`.
- **Manufactured contrarianism.** A stance in the draft that appears nowhere in the packet or the bank is a `fabrication` finding, not a strength. "A stance the author didn't take is a fabrication wearing a personality." Check every confident disagreement against `packet.md` before scoring it as voice.
- **Structural intent.** Are sections evenly sized regardless of value? Does the conclusion restate the intro? Does anything digress, or does it march through an outline?

Score five weighted categories, each 0–100 where higher is more tell-like:

| Category | Weight | Primary evidence |
|---|---:|---|
| Substance & stance (`substance`) | 35% | Judgment pass: author-value check, stance, false balance, hedging |
| Texture & specificity (`texture`) | 25% | Judgment pass: specifics, anecdote authenticity, evidence trail |
| Rhythm & structure (`rhythm`) | 20% | Script CVs plus judgment: uniformity, symmetric sections, signposts, restated conclusion |
| Constructions & tics (`constructions`) | 12% | Script: triads, em dashes, "not just X but Y", bold and colon density, bullet share |
| Lexicon (`lexicon`) | 8% | Script: banned-phrase hits per 1000 words |

Overall is the weighted sum. Bands: **0–20 clean** · **21–40 light tells** · **41–60 noticeable** · **61–80 reads generated** · **81–100 template-grade**.

**Calibration guardrails.** These are the reason the model is worth running at all:

- The strongest tells are absences — no stance, no texture, no evidence trail — not word choices. A draft with zero banned words can still land at 70 because it commits to nothing.
- Cap each low-weight category's influence at its weight. No halo effects. A text with genuine stance and texture never scores above 40 on lexicon hits alone; twelve instances of "leverage" is a 12-point problem in an 8%-weight category, not a verdict on the article.
- Spotless mechanics cannot rescue a text with no author-specific value. Substance is scored on content, not polish.
- **Agreement is not a tell.** A draft that says what the sources say, and adds the author's own examples and process, has substance. Do not raise `substance` because nothing in the piece picks a fight. If you find yourself lowering `substance` because the prose reads smoothly, you have inverted the model.

`references/voice-and-tells.md` owns the rule set behind all five categories. Load it and run its tells checklist rather than re-deriving the rules.

## Phase 3 — Rubric scoring

Score the eight categories in `references/quality-rubric.md` at their stated weights, 0–100 higher-is-better, and compute the weighted overall. Use `brief.md` for what was promised, `brand.md` for voice and audience, `claims.json` for whether accuracy is actually resolved, and `media.json` for whether the image plan was honored.

Two rubric categories have hard evidence available, so use it rather than impressions: `accuracy` cannot score above 60 with an unresolved row in `claims.json` (`needsVerification: true` and no status), and `completeness` is set by Phase 5, not by feel.

### What the research could actually see

Read the `connectors` and `teardown` blocks in `research-vN.md` before scoring `original-value` or `completeness`. Both categories rest on a claim about the competitive set — "this says something page one doesn't" — and that claim is only as good as the look someone took at page one.

- **A `degraded` or `unavailable` connector** means part of the SERP was never observed. `searchFeatures: null` is normal and costs nothing; a degraded search backbone is not.
- **`teardown: { planned: 8, fetched: 2 }`** means the information-gain argument rests on a quarter of the intended evidence.

Neither caps the score numerically — a two-page teardown can still surface a real gap, and the test run proved it can. What it does is bound what the review may **assert**. Score the gap the draft claims, and say in the report that the competitive picture behind it was partial, naming the numbers. A confident `original-value: 90` on research that read two of eight pages is a judgment the file itself contradicts.

If `research-vN.md` is absent entirely — a post briefed before v2 — say so once and score from `brief.md` alone. That is a real limitation, not a finding against the draft.

## Phase 4 — Boundary and fabrication check

These are the two failures that put someone's name on something they didn't say. Both are severity-locked to `high`, and neither can ever be `accepted` — there is no version of "leave it" for publishing a claim the author didn't make.

**Boundary.** Read the "Never say" section of `clients/<c>/opinion-bank.md` and the same section in `brand.md`. Check every item against the draft, including paraphrases — a boundary against "never call our process proprietary" is violated by "a methodology we developed in-house that nobody else runs." Quote the offending sentence in the finding. Category `boundary`.

**Thesis fidelity.** Read `brief.md`'s `thesis` key, then read the draft's opening, its H2s, and its close. Does the article argue that thesis? A draft that drifted into a more novel argument — the research turned up a nuance and the draft made it the point — is an `intent` finding at `high`, quoting the thesis and the sentence that departs from it. Rule 1. This is checked before anything else in this phase, because a well-executed draft of the wrong article scores well on every other axis.

**Source over-reach.** Apply the source-interpretation hierarchy in `evidence-rules.md` to every sourced claim. Raise an `accuracy` finding at `high` for any band escalation: an implication written as an explicit statement, a source's silence written as a denial, a scoped instruction written as a general prohibition, a one-paragraph qualifier promoted to the article's headline. Quote both the draft's sentence and what the source actually says. This is the same severity as a fabricated experience claim, because the result is identical — a sentence the client has to defend that nobody said.

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

**Two audiences, and the difference matters.** `review-v<N>.json` is the machine record — full scores, every finding, every ID, every consequence. It is written in full, always, exactly as specified above. The **chat response** is for a person, and under Rule 9 it is not the JSON read aloud.

### Default chat response

Load `references/reporting.md`. Lead with what blocks, then what's worth fixing, then where it is.

```
## why-respond-to-google-reviews — draft-v2

**Blocking — has to change before this ships**
- The post says you've done this for dozens of clients. You never told me that. Cut it, or give me the real number.

**Worth fixing (3)**
- The middle section restates what's already ranking. It needs your take on what actually changes for a business.
- Two of the reader questions the brief committed to never get answered: what it costs to keep up, and what to do about a review you can't fix.
- The "88% of consumers" figure has no primary source I could find.

**Reads fine otherwise.** Voice is close, structure holds, nothing crosses your boundaries list.

Findings: .blog/posts/why-respond-to-google-reviews/review-v2.json
Next: `wltbo revise why-respond-to-google-reviews`
```

Rules for that response:

- **Translate every finding into the thing it is about.** Not `BL-014 fabrication high`; the sentence and what's wrong with it.
- **No score tables by default.** Two numbers at most, and only if they say something — "reads a bit generic in the middle" beats `substance 28 / texture 35`.
- **No category names, no IDs, no weights, no metric densities, no threshold sourcing, no connector or teardown blocks.** All of that is in the JSON.
- **Rank by what the user should do first**, not by severity order or discovery order.
- **Say what's fine.** A review that only lists problems reads as a verdict on the writer. One line on what holds up keeps the report usable.

### When the full detail comes out

The user asks — "show me all the findings," "what did it score," "give me the numbers." Then give them everything: both score tables, every category, every finding with its ID, the threshold sourcing, the research-coverage caveat. They asked for the machinery; hand it over complete.

Also surface detail unprompted when it **blocks completion** or reveals a **real quality problem** — but translated, per the rules above.

### The two scores, when shown

When you do show them: side by side, never blended, with the one-line note that neither is an authorship verdict, and with the threshold source named. Bands: **0–20 clean** · **21–40 light tells** · **41–60 noticeable** · **61–80 reads generated** · **81–100 template-grade**.

### Fix recommendations

Rank by expected impact, not by order found. Never recommend fake typos, invented anecdotes, fabricated experience, manufactured disagreement, or detector-evasion tricks — fixes add stance the author actually holds, specificity, and asymmetry. If asked to compare two draft versions, score both and show per-category deltas naming which edits moved which categories.

## Confirm and stop

Scores and findings only. The draft file is not yours to edit — hand every fix to `revise`. And the report a person reads is prose about the article, not a dump of the record you just wrote.
