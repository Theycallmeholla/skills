---
name: who-let-the-blogs-out
description: >
  Blog and web-content system for agency work — plan topics, interview the author for
  their real take, brief the angle, draft the article, plan images, verify claims, score
  drafts for quality and AI tells, revise, publish, and refresh aging posts. Shorthand
  "wltbo" also triggers it. Commands share a per-client memory of brand voice,
  the author's positions and stories, verified facts with expiry dates, and every
  published post. Use for blog posts, articles, long-form content, refreshes, keyword
  targeting, search intent, titles and H1s, meta descriptions, internal linking,
  cannibalization checks, E-E-A-T, and information gain. Also use when the complaint is
  "it doesn't sound like us", "it reads AI-written", "it's generic", "we already wrote
  this one", "the facts are made up", "there are no images", "it's too thin", or "nobody
  thought this through". Not for social posts, emails, internal comms, case studies
  (case-study-builder), site audits (website-audit), or content calendars
  (content-strategy).
allowed-tools:
  - Bash(python3 scripts/tells_metrics.py *)
---

# Who Let The Blogs Out

`brand · plan · interview · verify · brief · write · images · review · revise · publish · refresh · help`

Shorthand: `wltbo` stands in for the full name — `wltbo write` is `who-let-the-blogs-out write`.

A bare invocation shows a menu built from your actual state. It never auto-runs a command — a bare call means "what should I do?", and answering it by doing something is how a system loses trust in its first week. `help` explains every command in plain language without touching anything.

## Doctrine

Four beliefs every command holds. Everything else is a reference file, loaded only when its command runs.

**1. Published under a name means true under that name.** Nothing is presented or implied as first-hand experience unless it appears in the post's Opinion Packet or the client's fact vault. This is not a style preference — it is the reason the interview exists. A system that writes convincing fake experience is worse than no system, because it produces liabilities that read well.

**2. Depth is coverage, not length.** A post is thin when it leaves the reader's real questions unanswered, not when it runs short. Padding a 900-word complete answer to 1,800 words makes it worse. The brief commits to a set of reader questions; the review fails the draft for each one left open.

**3. The 500-companies test outranks every other score.** If the article would work unchanged for any competitor after swapping the company name, it failed — regardless of how it scored on structure, keywords, or readability. Original value is the only thing that cannot be copied.

**4. Drift is reported, never silently repaired.** A command that finds stale, missing, or malformed state says so and continues doing what it was asked. It does not migrate, reformat, or clean up as a side effect. Nothing erodes trust faster than running a small command and discovering it rewrote six files.

## Setup

Read `.blog/registry.json` once at the start of a session. It is small by design — identity plus two summary counts per post — so a single read tells you what exists without opening a record. Do not re-read it after every command; write to it as commands complete and keep the in-memory copy current.

If `.blog/` does not exist, say so and point at `brand`. Do not create a partial tree as a side effect of some other command — a half-formed state directory is harder to reason about than none.

## Commands

| Command | Category | What it does | Reads | Writes | Reference |
|---|---|---|---|---|---|
| `brand` | Setup | Build or update a client's brand profile; initialize `.blog/` | `clients/<c>/brand.md`, `registry.json` | `clients/<c>/*` (whole dir on first run), `registry.json` | `references/brand.md` |
| `plan` | Setup | Pick what to write next; keyword, intent, format fit, cannibalization | `registry.json`, `clients/<c>/brand.md` | `posts/<slug>/post.json`, `registry.json` | `references/plan.md` |
| `interview` | Capture | Capture the author's stance, stories, specifics, boundaries | `opinion-bank.md`, `brand.md`, `facts.json` | `posts/<slug>/packet.md`, `opinion-bank.md`, `facts.json` | `references/interview.md` |
| `verify` | Capture | Verify claims; promote durable facts to the vault; set expiries | `claims.json`, `facts.json` | `claims.json`, `facts.json`, `registry.json` | `references/verify.md` |
| `brief` | Draft | Angle, information gain, coverage targets, outline, title set | `packet.md`, `brand.md`, `facts.json`, `registry.json` | `brief.md`, `claims.json`, `media.json` | `references/brief.md` |
| `write` | Draft | Draft the article from the brief | `brief.md`, `packet.md`, `brand.md`, `facts.json` | `draft-v(N+1).md`, `post.json` | `references/write.md` |
| `images` | Draft | Concrete asset plan: what each image shows, where, and its status | `brief.md`, `draft-vN.md`, `media.json` | `media.json` | `references/images.md` |
| `review` | Ship | Score on rubric + AI tells; boundary, fabrication, coverage, headings | `draft-vN.md`, `brief.md`, `packet.md`, `brand.md` | `review-vN.json`, `post.json`, `registry.json` | `references/review.md` |
| `revise` | Ship | Apply open findings; produce the next draft version | `review-vN.json`, `draft-vN.md`, `packet.md` | `draft-v(N+1).md`, `review-vN.json` | `references/revise.md` |
| `publish` | Ship | Record the live URL; set re-verify dates; index the post | `post.json`, `claims.json`, `media.json` | `post.json`, `claims.json`, `registry.json` | `references/publish.md` |
| `refresh` | Ship | Find aging posts; re-research; change plan plus a new version | `registry.json`, `claims.json`, `draft-vN.md` | `draft-v(N+1).md`, `claims.json`, `post.json` | `references/refresh.md` |

Read the Reads and Writes columns as the wiring diagram: one command's Writes is the next one's Reads. A command whose row is empty on both sides would be a standalone skill wearing the system's badge — there are none, and there should never be.

## Routing

**1. No argument** → load `references/routing.md` and present its menu. Never auto-run.

**2. An explicit or clearly implied command** → load `references/<command>.md` and follow it. Also load `references/state.md` before any command that writes. If two commands plausibly fit, ask once and then proceed.

**3. Anything else in the domain** → treat it as general blog work. The default is `brief` when a packet exists for the topic, `interview` when it doesn't. Fragment requests — title options only, a meta description, an outline, "does this read AI-written" — are answered from the relevant command's rules without running the whole playbook and without writing state. Say that no state was written, so nobody assumes the post record moved.

**4. `help`, or any question about what the commands do** → load `references/help.md` and follow it. Explain; never run anything. This is the one command that reads no state and writes none — it's a meta-command, not a transition, and that's why it isn't in the table above.

**5. Aliases and deprecations**

- `wltbo` → the full skill name, in any position
- `status` → the bare invocation menu
- `commands`, `options`, `what can you do` → `help`
- `audit`, `score`, `check` → `review`
- `outline`, `research` → `brief`
- `draft`, `post` → `write`
- `seo-blog-writer` → `brief`, then `write` *(retired skill)*
- `blog-topic-interview`, `opinion-interview` → `interview` *(retired skills)*
- `ai-writing-detector` → `review` *(retired skill)*

## State

State lives in `.blog/` in the working project, never inside this skill directory — the skill is a read-only package that may be installed in a shared location, and in Cowork it is discarded at session end. `clients/<slug>/` holds durable memory that outlives any post: brand profile, opinion bank, verified fact vault. `posts/<slug>/` holds one article's record: packet, brief, claim ledger, media plan, and every draft and review version.

Writes are append-only. A new draft is `draft-v(N+1).md`, never an edit to `draft-vN.md`. History is the diff, and `refresh` reads it.

The full contract — schemas, closed enums, ID rules, write rules — is `references/state.md`. Load it before any command that writes.
