# Verify

Returns the post's claim ledger with a status, a source, and an expiry date on every row — plus any durable facts promoted into the client's vault — and changes no prose.

**Reads:** `posts/<slug>/claims.json` · `clients/<c>/facts.json` · `posts/<slug>/post.json` *(read-only, for `currentVersion`)* · `posts/<slug>/draft-vN.md` *(read-only, front matter only, for `uses_claims`)* · `registry.json`
**Writes:** `posts/<slug>/claims.json` · `clients/<c>/facts.json` · `registry.json` (`staleClaims` and the post row's `updated`)
**Stops at:** Never edits a draft. A claim that can't stand gets marked `removed` and reported; `revise` is what takes it out of the prose.

That separation exists because verification and rewriting fail differently. Fixing a sentence while you're checking it means the check and the edit land in one unreviewable motion, and nobody can later tell whether the number changed because the source said so or because the sentence read better the other way.

Load `references/evidence-rules.md` and follow it. It owns the verification standards, the three tiers of assertion, the promotion criteria, and the YMYL rules. This file is the procedure for applying them; it does not restate them. For source ranking, `references/research-protocol.md` has the ordered preference list — use it rather than re-deriving one.

## Two modes, one playbook

**Pre-draft verification** — `who-let-the-blogs-out verify <slug>`. Run after `brief`, before `write`. The brief enumerated what the article will assert; this settles each one so the draft is built on verified material instead of having facts retrofitted into finished sentences. Retrofitting is how a paragraph survives with its rhetorical shape intact after the number underneath it turned out to be wrong.

**Standing re-verification** — `who-let-the-blogs-out verify <client>`. Walks the whole vault for entries past `reverifyBy`, re-checks them, and recomputes `staleClaims` for every post in each entry's `usedIn`. Same phases, different scope. Because vault-backed claims resolve their expiry through `factRef`, re-verifying one fact clears the staleness of every post citing it in a single write — that is the entire reason the vault exists.

Scope discipline in standing mode: open a post's `claims.json` only when that post has a claim carrying its own expiry, or when its `staleClaims` needs recomputing. Opening all forty ledgers to touch three of them is how a small command turns into a long one.

## Phase 1 — Load the ledger

Read `claims.json`. Missing means the post was never briefed — say so, point at `who-let-the-blogs-out brief <slug>`, and stop rather than inventing a ledger from a draft. Read `facts.json` for the client (absent is normal; treat it as an empty vault and create it with `version: 1` and an empty array only if you actually promote something).

Sort into three piles before you chase anything:

- **Already settled.** `needsVerification: false` with a `factRef` whose vault entry is unexpired. Skip these entirely and say so in the report. Re-checking a fact the vault verified three months ago is the exact work the vault was built to eliminate.
- **Expired.** Effective expiry is in the past — the fact's `reverifyBy` when `factRef` is set, the claim's own when it isn't. These need the full treatment again, not a date bump.
- **Open.** `needsVerification: true`. `brief` leaves these as `awaiting-client` because the claim enum has no `pending` value; the pending-ness lives in `needsVerification`. Don't add a fifth enum value to tidy this — enums are closed by design.

Note anything malformed — a claim with no `text`, a `factRef` pointing at an `F-` ID that isn't in the vault, IDs out of sequence — in one line and keep going. Reporting drift is the job; repairing it isn't.

## Phase 2 — Verify against sources

For each open or expired claim, chase the primary source and record the URL you actually opened, not the one you'd expect to exist. Record the source's own publication or last-updated date alongside your `verifiedOn` — a 2021 study verified today is verified, and also five years old, and the second fact matters to whoever reads this next year.

Then set one status from the closed enum:

| Status | When | What it means downstream |
|---|---|---|
| `verified` | Primary source says exactly this | `write` may assert it plainly with the citation |
| `qualified` | Partly true, or true within stated bounds | `write` must carry the qualifier into the prose |
| `removed` | Contradicted, unsourceable, or the source retracted | `revise` deletes or rewrites the sentence; `write` never uses it |
| `awaiting-client` | Only the client can settle it | Goes to the publish checklist as client evidence needed |

**`qualified` is the underused one, and it is often the right answer.** "Roughly a third of local searches" attached to a dated source beats both a false precise number and a hole where a fact should be. Reach for it whenever the source supports the shape of the claim but not its precision, or supports it under conditions the draft didn't state. Preserve the hedge inside the claim `text` itself, not in a comment — the qualifier has to survive into the prose, and the only field `write` reads is the text.

Three things that go wrong here:

- **Verifying from memory.** Model priors are not a source. If you cannot open something and record a URL, the claim is not verified — it stays open and the report says why. Every command downstream treats `verified` as load-bearing, so a status set on recall is a lie the whole system inherits.
- **Blog-to-blog chains.** Don't cite one article because it cites another. Chase to the study, the statute, the vendor's own docs — or mark it `removed` and say the trail died.
- **Silent scope creep in the claim text.** If the source supports a narrower statement than the ledger row, rewrite the row narrower and mark it `qualified`. Rewriting the claim to match the evidence is this command's job; rewriting the paragraph around it is not.

If the post is YMYL — health, legal, financial, safety — `evidence-rules.md`'s YMYL section raises the bar on what counts as a source and requires a named reviewer. Load it before you start rather than discovering it at the report.

If no research tooling is available in this session, verify nothing, mark nothing, and say plainly which claims still need a source. An honest "couldn't check these six" is recoverable; six claims stamped `verified` by guesswork are not.

## Phase 3 — Promote durables

This phase is the crux of the command, and over-promoting is the failure mode.

A claim earns a vault entry only when it is **durable and reusable** — likely to be cited again in a post that doesn't exist yet. The test that settles most cases: *would you spend ten minutes re-verifying this in a year?* If the honest answer is no, it belongs in this post's ledger and nowhere else.

**Promote:**

- *"We won't take on a rebuild under $6,000."* The client's own floor price. It will surface in every pricing, scoping, or qualification post they ever run. `kind: price`, `source: first-hand`.
- *"A full location-page rebuild runs 6–8 weeks from kickoff."* A process timeline they quote to prospects weekly. `kind: timeline`.
- *"Google publishes no character limit for the title element."* Platform behavior central to their field, cited in anything touching titles or meta. `kind: tool`, `source: primary`.
- *"46% of Google searches have local intent."* A statistic at the center of what this client sells, with a dated primary source. `kind: statistic`, `source: secondary` unless you reached the original study.

**Don't promote:**

- *"Katy updated its sign ordinance in March 2026."* True, sourced, and interesting to exactly one article. Stays as `C-004`.
- *"Competitor X shipped a bulk page generator in June."* A competitor feature in a comparison post — volatile, and framed for this article's argument. Ledger only.
- *"This client's July campaign returned 3.1x."* One result in one case-study-adjacent post. Numbers about a single engagement don't generalize; the process behind them might, and that's a different entry.
- Anything already in the vault under different wording. Point `factRef` at the existing `F-` ID instead of minting a near-duplicate. Two entries for one fact means two expiry dates, and within a year they disagree.

The reason for the discipline: a vault where every entry is worth re-verifying stays worth reading. A vault holding four hundred one-off claims from thirty articles is a junk drawer — standing re-verification against it becomes an all-day job nobody runs, and the moment nobody runs it, the expiry dates are decoration.

**Writing the entry.** Allocate IDs monotonically per client from the existing `facts.json` (never reuse, never renumber to close a gap), fill the schema in `state.md`, pick `kind` and `source` from the closed lists, and append this post's slug to `usedIn`.

**Then link the two.** Set `factRef: "F-021"` on the claim and set the claim's own `reverifyBy` to `null`. The vault entry now owns the expiry, and every reader of either file follows one date. If an earlier `brief` copied a date into the claim, overwrite it with `null` and mention it once in the report — that's this command's own field in its own declared file, not a tidy-up of someone else's state.

Two dates for one fact is how ledgers rot. Standing re-verification pushes the fact from 2027-03 to 2028-03; the copy in the claim still reads 2027-03; six months later a menu recommends a refresh for a claim that was re-verified in the spring, and after two of those nobody trusts the staleness number again.

## Phase 4 — Set expiries

`evidence-rules.md` sets the principle. This turns it into a date. Every claim gets one — including the ones that will never change, because the date's real job is telling the next reader when someone last looked.

| Kind of claim | Span | Why |
|---|---|---|
| Prices, vendor plans, rate cards | 6–12 months | Fastest decay of anything in the vault; 12 months is generous, not cautious |
| Platform behavior, product features, APIs | 12 months | Google, Meta, and every SaaS ship changes without announcing them where you looked |
| Laws, ordinances, regulatory thresholds | 12–24 months | Slower, but an expired legal claim is the most expensive kind to be wrong about |
| Statistics and study findings | 24 months | The number holds; its currency doesn't. A 2024 stat cited in 2027 reads as neglect |
| Process timelines, thresholds, methods | 12–24 months | These track how the client actually works, and that changes quietly |
| Physical, mechanical, definitional facts | 24–36 months | Concrete cures the same way it always has — the date says a human checked, not that it decayed |

Adjust for the source, not just the category. A vendor's pricing page that changed twice this year earns 6 months. A statute that hasn't been amended since 2019 earns the long end. When a claim sits between two rows, take the shorter one: an early re-check costs ten minutes, and a late one costs a published article asserting something false.

## Phase 5 — Report and update the registry

`staleClaims` on the post's registry row drives the no-argument menu's refresh recommendation, so it has to be exactly right — a number that overstates trains people to ignore the menu, and one that understates lets a wrong claim sit in a live article.

Count a claim toward `staleClaims` when all three hold:

1. Its status is not `removed` — a claim already marked for deletion is `revise`'s problem, not a staleness signal.
2. It is in the current copy: the `uses_claims` list in `draft-v<currentVersion>.md`'s front matter includes its ID. If no draft exists yet, count every non-`removed` claim, since none has been written out.
3. Either its effective expiry (the fact's when `factRef` is set, its own when not) is in the past, or its status is `awaiting-client`.

Write the count and the post row's `updated` in the same operation as the ledger write. `openFindings`, `status`, `currentVersion`, and the client rows aren't yours — `review`, `publish`, and `brand` own those.

One boundary worth naming: a published post whose claim just expired is now factually `stale`, and `post.json` is not in this command's writes. Report it — "`local-seo-location-pages` has 2 expired claims in the live copy" — and let `refresh` move the status. Reaching into `post.json` to set it here would be exactly the silent side-effect the state contract's rule 5 is about.

## Output

One chat response. Files written, no new files created beyond `facts.json` if the vault didn't exist.

```
## local-seo-location-pages — claim ledger

11 claims  ·  7 verified · 2 qualified · 1 removed · 1 awaiting client
3 skipped (vault-backed, unexpired)

| ID    | Status          | Claim                                  | Source                | Expires  |
|-------|-----------------|----------------------------------------|-----------------------|----------|
| C-001 | verified        | Google publishes no title char limit   | developers.google.com | via F-021|
| C-004 | qualified       | Roughly a third of local searches...   | thinkwithgoogle 2025  | 2028-08  |
| C-007 | removed         | 53% of users abandon after 3s          | trail died at a blog  | —        |
| C-009 | awaiting-client | Their audit turnaround is 5 days       | client only           | —        |

### Promoted to the vault
F-021  Google publishes no character limit for the title element  ·  tool · primary · 2027-08-01
       linked from C-001 (claim expiry cleared to null)
Not promoted: C-004 (one-off to this article), C-011 (near-duplicate of F-014 — linked instead)

### Needs the client
C-009  audit turnaround in business days  → publish checklist, client evidence needed

### Expiring soonest
F-018  $6,000 rebuild floor  ·  2026-11-14  (3 months)

Written: posts/local-seo-location-pages/claims.json · clients/cursive-media/facts.json
         registry.json (staleClaims: 1)
Next: blog write local-seo-location-pages — C-007 is out; the outline section it
      supported needs a different piece of evidence.
```

Order the ledger table by status severity — `removed` and `awaiting-client` first, since those are the rows that change what gets written — not by ID. End with the single next step: `who-let-the-blogs-out write <slug>` in pre-draft mode, `who-let-the-blogs-out refresh <slug>` when standing re-verification found expired claims in published copy.

### Cadence

Ask the user only about claims no source can settle — the client's own turnaround, their internal threshold, whether a result is theirs to publish. Batch two or three at a time with your best guess attached, so a "yes" is a complete answer: *"Audit turnaround — 5 business days, or is that the rush number?"*

Never ask what a source can answer; going to the client for something on a public docs page is how a user learns the command doesn't do its own work. Never ask permission to mark a claim `removed` — mark it, report it, and let them override. And don't ask about every unresolved claim in one wall; three questions with recommendations get answered, and fourteen get skipped, after which nobody runs this command again.

## Confirm and stop

Statuses, sources, expiries, and vault promotions only. The draft is not yours to touch — every claim that must come out of the prose goes to `revise` as a marked row.
