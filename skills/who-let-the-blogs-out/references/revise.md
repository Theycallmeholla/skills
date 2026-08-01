# Revise

Applies the open findings from a review to produce the next draft version, and returns a changelog mapping every finding ID to what actually changed and where — including the ones deliberately accepted and the ones still open.

**Reads:** `posts/<slug>/review-vN.json` · `posts/<slug>/draft-vN.md` · `posts/<slug>/packet.md` · `posts/<slug>/brief.md` *(read-only, for what was promised)* · `clients/<c>/facts.json` · `clients/<c>/opinion-bank.md` · `posts/<slug>/claims.json` *(read-only, for citations)*
**Writes:** `posts/<slug>/draft-v(N+1).md` · `posts/<slug>/review-vN.json` (finding status fields only) · `posts/<slug>/post.json` · `registry.json` (`openFindings`, `currentVersion`, `updated`)
**Stops at:** Never re-scores — that's `review` again. Never introduces a new tell while fixing an old one. Never fabricates to close a `fabrication` finding.

## Phase 0 — Locate the review and the draft it scored

Read `post.json` for the client slug and `currentVersion`. Read the newest `review-v<N>.json` and check its `draftVersion` against `currentVersion`.

If they disagree — a review scored draft-v2 but draft-v3 already exists — stop and point at `review`. Every finding carries a `location` like `H2 'What Google actually wants'`, and applying those locations to text that has already moved means editing the wrong sentences with confidence. Report the mismatch; don't repair it.

**If no finding is `open`, write nothing.** Say the review is fully resolved or accepted and stop. Producing draft-v3 that differs from draft-v2 by nothing is how the version history stops meaning anything, and `refresh` reads that history as a record of real change.

## Phase 1 — Load the open findings and the material they'll need

Pull every finding with `status: "open"`. Findings already `resolved` or `accepted` are closed business — do not reopen one because you disagree with the call.

Then load, without restating them:

- `references/voice-and-tells.md` — the rulebook you are fixing toward. Its **What NOT to do** section is the specific trap this command falls into, so read that section twice.
- `references/evidence-rules.md` — the three tiers. You will be rewriting sentences that got flagged for tier drift, and the rewrite has to land in a real tier.

Read `packet.md`, the client's `facts.json`, and `opinion-bank.md` **before** you start rewriting, not when you hit a gap. This is the inventory of what the author actually said, actually measured, and actually believes. Every fix you make has to be built from something in that inventory or from openly-framed reasoning of your own. Knowing the inventory up front is what stops you from writing a plausible detail at the moment you need one — which is the failure mode, and it arrives mid-sentence, not as a decision.

## Phase 2 — Rank by impact, not by ID order or severity

Severity says how bad a finding is. Impact says how much the draft improves per edit, and those are different numbers. Work in these tiers, using severity only to break ties inside a tier:

1. **Blocking:** `boundary` and `fabrication`. They stop `publish` outright and they cannot be accepted. Phase 3 governs them.
2. **Findings whose fix changes what the article says:** `original-value`, `completeness`, `accuracy`, `intent`, and any `voice-tells` finding about stance, texture, or the 500-companies test. `review` carries this insight forward from the tells model: the strongest tells are absences — no position, no specifics, no evidence trail. Adding one real stance moves `substance` at 35% weight. Deleting nine instances of "leverage" moves `lexicon` at 8%.
3. **Findings about how it says it:** `structure`, `brand-fit`, `conversion`, rhythm and construction `voice-tells`.
4. **Cosmetic:** lexicon hits, `technical-seo` field tweaks, `media` placement.

Work top-down, because the tiers cascade. Rewriting a section to carry a real judgment usually deletes half its banned words and most of its uniform paragraph shapes on its own — do the lexicon pass first and you'll do it twice, and the second pass will be over prose you already threw away. A changelog showing eleven cosmetic fixes and one untouched `original-value` finding is a revision that made the article read better while leaving the reason it fails intact.

## Phase 3 — Apply

### The trap, stated plainly

The characteristic failure of this command is closing a tells finding by installing a different tell. It happens because the finding names a symptom and the fastest edit removes the symptom:

- `voice-tells` says the draft hedges. You change "results typically vary" to "results can vary depending on several factors." That is a longer hedge. The fix is a condition: *"if your lot is under a quarter acre, skip this entirely."*
- `voice-tells` says there's no texture. You write "last spring a client in Katy called us at 11pm." Nothing in the packet says that. You have closed a `voice-tells` finding by committing a `fabrication` — a strictly worse draft that scores better.
- `voice-tells` says there's no stance. You add "everyone telling you to do X is flat-out wrong." Manufactured contrarianism is forced sass, and it reads exactly as generated as omniscient neutrality does. A stance the author didn't take is a fabrication wearing a personality.
- `rhythm` says paragraphs are uniform. You chop sentences at random. Uneven rhythm comes from cutting what is padding and expanding where the expertise is, so length follows value.
- Any temptation toward deliberate typos, "humanizing" mess, or edits aimed at a detector. The target is writing that survives close reading by an expert in the subject. A classifier is not the reader.

The test that catches all of these: **every edit must trace to something that already exists** — a line in `packet.md`, a fact ID from `facts.json`, a claim ID from `claims.json`, or your own reasoning framed openly as reasoning. If the fix requires material that isn't in the inventory you loaded in Phase 1, the finding does not get closed by writing. It gets escalated or, where the enum allows, accepted.

### Boundary and fabrication findings cannot be closed by writing something better

A `fabrication` finding means the draft asserts experience, a result, or a number the author never supplied. Writing a more plausible version of it is the worst available outcome and the easiest one to reach, because the more plausible version is the one nobody catches. Three legitimate moves:

1. **Cut the claim.** Usually the fastest and rarely as costly as it feels. The paragraph survives without "we've seen this fail on dozens of sites."
2. **Requalify it.** Rewrite to tier 3 — openly framed judgment, "which means the practical ceiling is closer to 65 than 60" — or to tier 2 with a real citation already sitting in `claims.json`. Requalifying is not softening; "in our experience, roughly a third" is still a tier-1 claim in a smaller font.
3. **Go get the real material.** Point at `interview` for a stance or a war story, `verify` for a number or a sourced fact. Leave the finding `open`, say so in the changelog, and name which command retrieves it. A finding honestly left open costs one more round. A finding closed by a better-written invention costs the client a claim they have to defend under their own name.

`boundary` findings work the same way, with one addition: paraphrases count. A boundary against "never call our process proprietary" is not satisfied by "a methodology we developed in-house that nobody else runs." Re-read the offending passage against the "Never say" list in `opinion-bank.md`, not against the sentence the finding quoted.

Neither category can be `accepted`. That's locked in the schema, not a judgment available here.

### Everything else

Fix the finding, not the sentence it quoted. A `completeness` finding says a reader question went unanswered — answering it means a reader with that question closes the tab satisfied: a specific recommendation, the condition where it changes, what happens if they get it wrong. Adding a heading with the question in it and three sentences circling it converts an unanswered finding into a partial one, and `review` will raise it again.

Preserve what wasn't flagged. This is a revision, not a rewrite — accurate, specific material that no finding named stays as written. Rewriting a clean section because you were already in the file destroys the diff `refresh` reads later and hides the edits that mattered inside noise.

You may make small craft fixes in passages you're already rewriting. Record them in the changelog under unflagged edits so the diff stays auditable. What you may not do is allocate a new `BL-` ID — findings are `review`'s to number, and a finding record written by the command that fixes it is a self-issued grade.

### Cadence

Ask at most one batched round of two or three questions, up front, before you edit anything: which findings the author wants to accept rather than fix, and whether a blocked `fabrication` finding should be escalated to `interview` now or carried open into the next round. Then proceed on whatever comes back, including nothing.

Never ask permission finding by finding — nine yes/no prompts is how a revision loop gets abandoned after its second use. Never ask the author to supply a fact you could have read in the vault. Never ask whether to invent something.

## Phase 4 — Mark each finding resolved or accepted

Update the finding objects in the **old** `review-v<N>.json` in place. This is the one permitted mutation in an append-only system, and it's narrow on purpose: `status`, `resolvedIn`, `resolvedBy`, `acceptedReason`. Scores, claims, consequences, categories, severities, and IDs stay byte-identical.

Do not write a new review file. `revise` computed no scores, and a review file carrying findings with an invented or absent score block is a corrupt record that the next command reads as real. The statuses belong to the review that raised the findings; the next score belongs to the next `review`.

- **`resolved`** — `resolvedIn` is the new draft version number (`3`), `resolvedBy` is one line naming the edit ("cut the unsourced dozens-of-sites claim from ¶2").
- **`accepted`** — `acceptedReason` names who accepted it, what is being lived with, and why. *"Client hasn't supplied the 40-page rollout timeline; shipping without it and carrying it as client-evidence-needed in the checklist. Accepted by the author 2026-08-01."* Acceptance is the author's call, not yours — you may propose it, and a finding accepted because the fix looked like work is how the field stops meaning anything. Without acceptance, though, every future review re-raises the same item forever and the system becomes a nag people stop running, so use it honestly rather than avoiding it.
- **`open`** — leave all three fields `null`. Partially fixed is `open`. There is no half-resolved status, and inventing one by writing prose into `resolvedBy` while leaving `status: "open"` gives the next reader two contradictory answers.

Then write `draft-v(N+1).md`, leaving `draft-vN.md` byte-identical. Keep the front matter from the prior draft unless a finding named a field in it. Set `post.json`'s `currentVersion` to N+1, `status` to `drafted` — the new version has not been scored, and saying otherwise makes the pipeline lie about where the post is — and `updated` to today. Update the post's row in `registry.json` in the same operation: `currentVersion`, `updated`, and `openFindings` set to the count still `open` after this pass.

Optional smoke check: `python3 scripts/tells_metrics.py posts/<slug>/draft-v3.md` on the new version and the old one, compared only on the specific metrics the findings named — did the em-dash density actually drop, did the hedge count actually fall. Do not compute a tells score, report an overall number, or write anything from it. That is `review`'s job on the next pass, and a number produced here is one nobody can reconcile with the real one.

## Output

The new draft file, plus this in chat:

```
## local-seo-location-pages — draft-v2 → draft-v3

**9 findings: 6 resolved · 1 accepted · 2 still open**

### Changelog
BL-014  fabrication     resolved   opening, ¶2
        was  "we've rebuilt this for dozens of clients"
        now  cut — no packet line or first-hand fact behind it

BL-011  original-value  resolved   H2 'What Google actually wants'
        was  restated the ranking pages with no added judgment
        now  takes the packet's position that title rewrites are a
             relevance signal worth reading, not a bug to fight

(one block per finding: ID, category, new status, location, was → now)

### Accepted
BL-009  completeness — client hasn't supplied the 40-page rollout timeline.
        Shipping without it, carried as client-evidence-needed. Author, 2026-08-01.

### Still open — carried into the next review under these IDs
BL-006  fabrication  high  — "cuts bounce roughly 20%" has no source.
        Not closable by rewriting. Run `verify`, or cut the number.
BL-013  completeness medium — reader question 3 needs the maintenance
        cost the packet doesn't have. Run `interview`.

### Unflagged edits
Tightened two paragraphs in the intro while rewriting around BL-011.

Written: posts/local-seo-location-pages/draft-v3.md ·
         review-v2.json (finding status fields only) ·
         post.json (currentVersion 3) · registry.json (openFindings: 2)
Next: `who-let-the-blogs-out review local-seo-location-pages` — revise never scores its own output.
```

The changelog is the deliverable, not the draft. A revision nobody can audit is a revision nobody trusts, and "applied the feedback" is not auditable. Every ID gets a line, including the ones that didn't move — a finding that silently vanishes from the report is indistinguishable from one that was quietly ignored.

## Confirm and stop

Apply the findings, version the draft, mark each one resolved or accepted — but never score the result, never trade one tell for another, and never close a fabrication or boundary finding by writing a more convincing version of it.
