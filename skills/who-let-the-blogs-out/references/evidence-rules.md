# Evidence Rules

Loaded by `verify`, `write`, and `review`. This is the file that decides what the system is allowed to assert, and under whose name.

## The one rule everything else serves

**Nothing is presented or implied as first-hand unless it is in the Opinion Packet or the fact vault.**

Not softened, not hinted at, not implied by phrasing. "We've seen this fail on dozens of sites" is a first-hand claim even though it names nothing. "In our experience" is a first-hand claim. A confident specific number with no source is a first-hand claim by implication, because a reader will assume the author knows it from doing the work.

This matters because the content publishes under a real person's name against a real business. Invented experience is not a style problem — it's a liability that reads well, which is the most dangerous kind.

## Never invent

Credentials · years of experience · customer outcomes · quotes · case studies · proprietary processes · awards · test results · site visits · product usage.

If the article would be stronger with one of these and none exists, the move is to name it in the publish checklist as **client evidence needed** — not to write a plausible version. A checklist item costs the client an email; a fabricated case study costs them a claim they have to defend.

## The three tiers of assertion

Every material statement in a draft falls into one of these. Knowing which tier you're in determines how it must be written.

**Tier 1 — First-hand.** Drawn from the packet or a `source: first-hand` vault fact. May be written in the author's voice: "we stopped recommending this after the third client hit it."

**Tier 2 — Sourced.** Drawn from a primary source, cited. Written as fact with the link: "Google publishes no character limit for the title element." Prefer primary sources over anyone's summary of them. Don't cite one blog because it cites another blog — chase it to the source or drop the claim.

**Tier 3 — Reasoned.** Your own analysis, clearly framed as judgment rather than reporting: "which means the practical ceiling is closer to 65 than 60." Legitimate and often the most valuable content in the article — as long as it isn't dressed up as either of the tiers above.

The failure mode is tier drift: a tier-3 inference gets written with tier-2 confidence, or a tier-2 fact gets written in tier-1 voice. `review` flags both under `fabrication`.

## Verification standards

A claim needs verification when it is a number, a date, a price, a legal or platform behavior, a statistic, a competitor's feature, or anything a reader could check and find wrong.

- **Prefer primary sources.** Official docs, the company's own announcement, the actual statute, the original study.
- **Date everything.** A claim verified in 2024 and unmarked reads as current, and eventually it isn't.
- **Set an expiry.** Prices and platform behaviors decay fastest — 12 months is generous. Statistics and legal facts stretch further. Physical or process facts may not decay at all, but they still get a date so the next reader knows when someone last looked.
- **Qualify rather than delete** when a claim is partly true. "Roughly a third of…" with a dated source beats both a false precise number and a missing fact.

## Freshness

Anything that could have changed in the last 12–24 months gets re-checked before it ships: laws, prices, statistics, product features, platform behavior, and anything with a year in it.

Do not put the current year in a title unless the article genuinely contains current-year information. A year in the title is a promise about the content, and an unkept one is the kind of thing readers notice and remember.

## Promoting a claim to a fact

`verify` promotes a claim into the client's vault when it is **durable and reusable** — something likely to be cited again in a future post. A client's own pricing threshold, a process timeline they actually use, a statistic central to their field.

One-off claims specific to a single article stay in that post's ledger. Promoting everything turns the vault into a junk drawer and destroys the thing that makes it useful: that every entry in it is worth re-verifying when it expires.

When a claim is promoted, set `factRef` on the claim so the two stay linked. The claim then inherits the vault entry's expiry rather than carrying its own.

## YMYL topics

For health, medical, legal, financial, safety, or similarly consequential content:

- Current authoritative sources only. No secondary summaries.
- Distinguish education from professional advice, explicitly, in the text.
- No diagnoses, guarantees, or definitive recommendations unsupported by cited evidence.
- Recommend qualified expert review before publication, and put a reviewer field in the deliverable.

`review` treats an unmarked YMYL article as a high-severity `accuracy` finding. The cost of being wrong here isn't a ranking drop.

## Honest gaps

When the author has no take and no evidence on some aspect, that gets recorded as a gap in the packet and the section is written from cited research in a neutral voice — never in the author's voice, and never with invented conviction.

An honest gap is a better outcome than a fabricated stance every single time. It is also recoverable: a gap in the packet is a question you can go ask, while a fabricated stance is something someone has to notice before it does damage.
