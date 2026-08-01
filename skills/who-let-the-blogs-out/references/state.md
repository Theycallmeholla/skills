# State Contract

Load this before running any command that writes. It is the vocabulary the whole system speaks — if two commands disagree about what a `status` value means or which IDs are stable, composition quietly breaks and nobody notices until a later command reads garbage.

## Where state lives

```
<working project>/
└── .blog/
    ├── registry.json
    ├── clients/
    │   └── <client-slug>/
    │       ├── brand.md              brand profile — YAML frontmatter + prose
    │       ├── opinion-bank.md       positions, stories, voice, boundaries
    │       ├── facts.json            verified fact vault, with expiry dates
    │       └── notes.md              unstructured drawer
    └── posts/
        └── <post-slug>/
            ├── post.json             identity, status, version pointer, publish record
            ├── packet.md             the Opinion Packet
            ├── brief.md              angle, coverage targets, outline, title set
            ├── claims.json           this post's claim ledger
            ├── media.json            image plan with status
            ├── draft-v1.md           append-only
            ├── review-v1.json        scores + findings for draft-v1
            └── notes.md              unstructured drawer
```

Never write state into this skill's directory. Installed skills are a read-only cache in some environments and are discarded at session end in others — anything written there is silently lost, which is exactly the failure that made the old standalone opinion bank useless.

State is per-project. Two working directories share nothing. For agency work this is the intended shape: run blog from one root and let `clients/` do the partitioning, rather than scattering a bank per client folder.

`.blog/` may not exist. `brand` initializes it. Every other command that finds it missing reports that and points at `brand` — it does not create a partial tree.

## registry.json — the index

Read on every invocation, so it stays small. It holds identity plus exactly two summary numbers per post. Every field here is a field that can go stale, so nothing gets added without earning it.

```json
{
  "version": 1,
  "clients": [
    {
      "slug": "cursive-media",
      "name": "Cursive Media",
      "domain": "cursivemedia.com",
      "brandProfile": "complete",
      "bankEntries": 14,
      "updated": "2026-08-01"
    }
  ],
  "posts": [
    {
      "slug": "local-seo-location-pages",
      "client": "cursive-media",
      "title": "How to Build Location Pages That Do Not Look Mass-Produced",
      "primaryKeyword": "local seo location pages",
      "intent": "informational",
      "status": "published",
      "currentVersion": 3,
      "url": "https://cursivemedia.com/blog/local-seo-location-pages",
      "publishedAt": "2026-02-14",
      "openFindings": 0,
      "staleClaims": 2,
      "updated": "2026-07-30"
    }
  ]
}
```

`openFindings` and `staleClaims` are the only denormalized summary fields. They exist so the no-argument menu can recommend something specific without opening a single record. Resist adding a third.

**`staleClaims` — one definition, used by every command.** A claim counts as stale when all three hold:

1. Its status is not `removed`.
2. It appears in the current draft — `appearsIn` includes `currentVersion`.
3. Its effective expiry has passed, *or* its status is `awaiting-client`.

"Effective expiry" means the claim's own `reverifyBy`, or the linked vault fact's `reverifyBy` when `factRef` is set. `awaiting-client` counts because a claim still waiting on evidence is as unshippable as an expired one, and leaving it out lets a post look clean while resting on something nobody ever supplied.

`verify`, `publish`, and `refresh` all compute this number. They must compute it the same way, or the menu starts recommending work that isn't there.

## Closed enums

These are fixed. Adding a value is a deliberate schema change, not a judgment call made at write time. An open-ended string field produces forty near-synonyms within a month and then nothing can be grouped, filtered, or compared.

| Field | Values |
|---|---|
| `brandProfile` | `missing` · `partial` · `complete` |
| `intent` | `informational` · `commercial` · `transactional` · `navigational` · `local` · `mixed` |
| `status` (post) | `idea` · `interviewed` · `briefed` · `drafted` · `reviewed` · `published` · `stale` · `archived` |
| `status` (claim) | `verified` · `qualified` · `removed` · `awaiting-client` |
| `status` (fact) | `verified` · `qualified` · `retired` |
| `status` (finding) | `open` · `resolved` · `accepted` |
| `status` (asset) | `needed` · `client-supplied` · `sourced` · `generated` · `placed` |
| `severity` | `high` · `medium` · `low` |
| `category` (finding) | `intent` · `accuracy` · `original-value` · `completeness` · `structure` · `brand-fit` · `conversion` · `technical-seo` · `voice-tells` · `media` · `boundary` · `fabrication` |
| `kind` (fact) | `statistic` · `price` · `timeline` · `threshold` · `tool` · `result` · `credential` |
| `source` (fact) | `first-hand` · `primary` · `secondary` · `client-supplied` |
| `role` (asset) | `hero` · `diagram` · `screenshot` · `data-viz` · `proof-photo` · `decorative` |

Post `status` is a pipeline and the ordering above is the pipeline. `stale` is reachable only from `published`, set by `refresh` or by a claim passing its `reverifyBy` date.

The `intent` values are lifted verbatim from the taxonomy the old seo-blog-writer already used. They were a solved problem; don't re-solve them.

## clients/&lt;slug&gt;/brand.md

Prose, not JSON — it carries voice, and voice does not survive being broken into fields. The frontmatter is the only machine-readable part.

```markdown
---
client: cursive-media
name: Cursive Media
domain: cursivemedia.com
sitemap: https://cursivemedia.com/sitemap.xml
updated: 2026-08-01
source: interview | import | both
---

## What they sell
## Who buys it
## What makes them different (proof, not adjectives)
## Proof points on record
## Competitors — named, with what each does better
## Tone: how they talk, with real examples
## Never say
```

`source: import` marks a profile seeded from `.blog/clients/<slug>/import.json` — the file-drop seam for upstream tooling. If an import exists for the domain, ingest it rather than re-deriving what something else already produced.

## clients/&lt;slug&gt;/import.json

Optional, and written by something outside this skill. If an upstream tool has already analyzed the site, drop its output here in this shape and `brand` will ingest it instead of asking. This skill never names or invokes the producer — the path and the shape are the entire contract, so a crawler, a scraper, an agent, or a hand-written file all work identically.

```json
{
  "domain": "example.com",
  "tone": "plain, direct, lightly technical",
  "offers": ["what they sell, one per entry"],
  "proofPoints": ["claims with something behind them"],
  "competitors": ["named, with what each does better"],
  "source": "what produced this file, and when"
}
```

`audience` and `gaps[]` are honoured when present. Unknown fields are ignored. Every field is treated as site copy, not as the client speaking — `brand` records it with that provenance, and `evidence-rules.md` still governs what `write` may assert from it.

## clients/&lt;slug&gt;/opinion-bank.md

The author's accumulated thinking. Sections: Author profile · Standing positions · Contrarian takes · War stories and first-hand evidence · Voice fingerprints · Boundaries — never publish · Topic log.

`assets/opinion-bank-template.md` is the starting structure for a new client.

Two rules that matter more than the structure: **date every entry**, and **never delete a superseded position** — mark it superseded with the date. A changed mind is some of the best article material a writer has, and deleting it destroys that.

Numbers do not live here. They live in `facts.json`, where they can expire.

## clients/&lt;slug&gt;/facts.json — the fact vault

```json
{
  "version": 1,
  "facts": [
    {
      "id": "F-007",
      "statement": "Sealant on an untreated concrete drive fails in 3-5 years in Gulf Coast humidity.",
      "value": "3-5 years",
      "kind": "threshold",
      "source": "first-hand",
      "sourceUrl": null,
      "verifiedOn": "2026-03-11",
      "reverifyBy": "2027-03-11",
      "status": "verified",
      "usedIn": ["local-seo-location-pages"]
    }
  ]
}
```

The vault is the durable layer; a post's `claims.json` is the per-post layer that cites it. A fact used in three posts is verified once and expires once — which is what makes "these four published posts contain claims that went stale in June" answerable at all.

## posts/&lt;slug&gt;/post.json

```json
{
  "version": 1,
  "slug": "local-seo-location-pages",
  "client": "cursive-media",
  "status": "drafted",
  "primaryKeyword": "local seo location pages",
  "intent": "informational",
  "currentVersion": 2,
  "created": "2026-07-02",
  "updated": "2026-07-30",
  "url": null,
  "publishedAt": null
}
```

## posts/&lt;slug&gt;/claims.json — the claim ledger

```json
{
  "version": 1,
  "claims": [
    {
      "id": "C-003",
      "text": "Google publishes no character limit for the title element.",
      "factRef": null,
      "needsVerification": true,
      "source": "https://developers.google.com/search/docs/appearance/title-link",
      "status": "verified",
      "verifiedOn": "2026-08-01",
      "reverifyBy": "2027-08-01",
      "appearsIn": [2, 3]
    }
  ]
}
```

`factRef` points at a vault entry (`F-007`) when the claim is drawn from one. `appearsIn` lists the draft versions containing the claim, so `refresh` can tell whether a stale claim is still in the live copy or was already edited out.

## posts/&lt;slug&gt;/media.json — the image plan

```json
{
  "version": 1,
  "assets": [
    {
      "id": "M-002",
      "role": "diagram",
      "concept": "what it shows and why the article is worse without it",
      "placement": "after H2 'Why Google rewrites titles'",
      "status": "needed",
      "altText": null,
      "caption": null
    }
  ]
}
```

`altText` stays `null` until the asset actually exists. Alt text describes what is visibly in an image; writing it for an image nobody has made yet produces a description of an imagined picture, which is worse than none.

Three distinct values, and the difference matters: `null` means "not known yet," an empty string `""` means "deliberately empty because this image is decorative and a screen reader should skip it," and a description means the asset exists and this is what's in it. Collapsing the first two loses the ability to tell an unfinished plan from a finished one.

## posts/&lt;slug&gt;/review-vN.json — scores and findings

One file per draft version. Never mutated except to move a finding's `status`, `resolvedIn`, `resolvedBy`, or `acceptedReason`.

```json
{
  "version": 1,
  "draftVersion": 2,
  "reviewedOn": "2026-08-01",
  "scores": {
    "rubric": { "overall": 82, "intent": 90, "accuracy": 85, "originalValue": 70,
                "completeness": 75, "structure": 85, "brandFit": 80,
                "conversion": 80, "technicalSeo": 90 },
    "tells":  { "overall": 24, "substance": 20, "texture": 30, "rhythm": 25,
                "constructions": 20, "lexicon": 15 }
  },
  "findings": [
    {
      "id": "BL-011",
      "category": "original-value",
      "severity": "high",
      "location": "H2 'What Google actually wants'",
      "claim": "This section restates the ranking pages with no added judgment.",
      "consequence": "Publishes as an article any competitor could have written, so it earns no link and no repeat reader.",
      "status": "open",
      "resolvedIn": null,
      "resolvedBy": null,
      "acceptedReason": null
    }
  ]
}
```

Rubric scores run 0–100 where higher is better. Tells scores run 0–100 where **higher is worse** — they measure the density of generated-writing patterns. Keeping the two scales opposite is deliberate: a single blended number would let clean mechanics disguise an article that says nothing.

## Five schema rules

**1. IDs are stable and never reused.** `BL-011`, `F-007`, `C-003`, `M-002` refer to the same thing forever, across every version. Allocate monotonically — per post for findings, claims, and media; per client for facts. This is what lets a later command say "you closed six of nine, these three are still open" without re-deriving anything.

**2. Every enum is closed.** See the table above.

**3. Findings can be `accepted`.** Some findings are deliberate choices already made — a stance you're keeping despite the risk, a section you know is thin because the client hasn't supplied the data. Without a way to record "yes, I know, leave it," every review re-raises them forever and the system becomes a nag people stop running. This one field is the difference between a tool that gets used and one that gets abandoned.

   The exception: `boundary` and `fabrication` findings are severity-locked to `high` and cannot be accepted. Those are the two failures that put someone's name on something they didn't say, and there is no version of "leave it" that's acceptable.

**4. Claims are falsifiable.** Every finding requires a `consequence` — the specific thing that breaks. If you can't write what goes wrong, it isn't a finding, it's a preference. Requiring the field enforces that at the schema level instead of hoping a playbook says it convincingly enough.

**5. Every entity has an unstructured drawer.** `notes.md` per post and per client. Judgment calls, user corrections, context that fits no field. Without a drawer, people jam prose into structured fields and the enums rot.

## Write rules

**1. Declared paths only.** Each command's header names exactly what it reads and writes. Undeclared paths are untouchable, even when editing one would be convenient.

**2. Append-only.** New draft → `draft-v(N+1).md`. New review → `review-v(N+1).json`. Never mutate a prior version. Disk is free; a lost history is not, and `refresh` reads the history to tell what actually changed.

**3. IDs allocated once, monotonically.** Never reused, never renumbered — not even to close a gap left by a deleted item.

**4. The registry is derived.** Any command that changes something the registry mirrors — a post's status, `currentVersion`, `openFindings`, `staleClaims`, `url`, a client's `brandProfile` or `bankEntries` — updates the index in the same operation. A registry that lags its records is worse than no registry, because the menu starts recommending things that aren't true.

The converse also holds: a command that changes nothing the registry mirrors leaves it alone. `images` writes a media plan and touches no registry field, so it does not bump `updated` — a timestamp change with nothing behind it falsely announces that the post record moved.

**5. Report drift; don't repair it.** A command that finds malformed or stale state says so and continues with what it was asked to do. It does not migrate, reformat, or tidy as a side effect. This is the rule that gets violated first and hurts most — someone runs `review` on one draft and discovers six files were rewritten.

## Initializing

`brand` creates `.blog/`, `registry.json` with empty arrays, and the client directory **whole** — `brand.md`, `opinion-bank.md` (from `assets/opinion-bank-template.md`), `facts.json`, and `notes.md`. Creating the client directory complete rather than lazily means `interview` never has to work out whether a missing bank is a new client or a lost file, which is a distinction it cannot make and would guess wrong on.

Post directories are created by whichever command first needs them — `plan` or `interview` — using the schemas above with `version: 1` and an empty items array.

When a file exists but doesn't match its schema, report the mismatch, name the file and field, and continue without writing to it. Rule 5 applies: repair is a deliberate act, requested explicitly, never a side effect.
