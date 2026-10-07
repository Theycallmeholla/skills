---
name: seo-blog-writer
description: >-
  Standalone version of the brief, verify, write, review, and revise steps from
  who-let-the-blogs-out. Researches what ranks for a keyword, commits to the reader questions
  the post must answer, verifies claims, drafts the article under the author's real stance,
  and scores the draft for quality and AI tells, saving everything in the project's .blog/
  folder with the same files and rules as who-let-the-blogs-out. Picks up the Opinion Packet
  that blog-topic-interview writes. Use when the user names this skill, or asks for an SEO
  blog post, a keyword-targeted article, title or meta description options, or an outline.
  Runs on its own whether or not who-let-the-blogs-out is installed; it hands off only when
  the user is working in who-let-the-blogs-out. Never invents experience, credentials,
  results, or opinions the author didn't give.
---

# SEO Blog Writer

Writes a blog post that deserves to rank: it answers every question the searcher actually has, says something page one doesn't, and never claims experience the author didn't supply.

These are who-let-the-blogs-out's `brief`, `verify`, `write`, `review`, and `revise` commands, packaged on their own. The rules are not paraphrased here; they are the same files.

## Before anything

Load `references/governing-rules.md`, `references/state.md`, and `references/reporting.md`. The priority order in `governing-rules.md` outranks every step below: the author's thesis is sticky, every claim stays inside its evidence, and nothing first-hand gets written that the author didn't give.

## The flow

1. **Packet.** Look for `.blog/posts/<slug>/packet.md`. If it's missing, say in one line that the post will have no first-hand layer and that `blog-topic-interview` fixes that in a few questions. Proceed only if the user wants to.
2. **Brief.** Follow `references/brief.md`. It does the research, fixes the angle under the packet's thesis, and commits to the reader questions.
3. **Verify.** When the brief left claims needing a source, follow `references/verify.md`.
4. **Write.** Follow `references/write.md`. It chains into `references/review.md` automatically, so the draft arrives already scored.
5. **Revise.** When the user wants the findings fixed, follow `references/revise.md`. It chains back into review.

**Stop after the brief** unless the user asked for a finished draft in one go. The brief is the cheap thing to reject before an expensive draft exists. Even in one go, stop wherever `brief.md` says to stop for a decision: wrong format, a page that already covers this, nothing original to add, or a required search tool that's down.

## Overrides to the shared files

The shared files assume the rest of who-let-the-blogs-out exists. Three places change here.

**No `.blog/` yet.** `brief.md` says to point at `brand`. Instead, create the same starting tree `brand` creates; these files are added to the brief's declared writes for this run only. Settle the client slug first from the business name, lowercase and hyphenated (`Cursive Media` → `cursive-media`; the domain only when there's no name), and show it before writing.

```
.blog/
├── registry.json              {"version": 1, "clients": [<client row>], "posts": []}
└── clients/<slug>/
    ├── brand.md               frontmatter + the seven headings from state.md
    ├── opinion-bank.md        assets/opinion-bank-template.md, copied whole
    ├── facts.json             {"version": 1, "facts": []}
    └── notes.md               a single `# Notes — <name>` heading
```

The client row is `slug`, `name`, `domain` (or `null`), `brandProfile: "missing"`, `bankEntries: 0`, and `updated`. `brand.md` gets frontmatter with `client`, `name`, `domain`, `sitemap: null`, and `updated`, leaving out `source` and `taxonomy` until `brand` runs, and `**Not captured.** Ask in the next brand pass.` under each heading. Never fill a brand section from guesses about the business. If `.blog/` exists but the client doesn't, create the client folder whole the same way.

**No post record yet.** `plan` normally reserves the slug. Settle it from the primary keyword instead: short, lowercase, hyphenated, no stop words. Show it, then create `posts/<slug>/post.json` per `state.md` with `status: "idea"` and `null` for anything not yet known, and add its row to `registry.json`.

**"Next" lines.** The shared files end reports with `wltbo <command>`. Here, name the next step in plain words instead, such as "say 'write it'" or "say 'fix these'".

**Never write into this skill's own folder.** Everything goes in the project's `.blog/`. `assets/opinion-bank-template.md` is only ever copied out.

## Names that point outside this skill

Where a shared file hands off to a command this skill doesn't have, stop and name it. Don't improvise it.

- `interview` → the `blog-topic-interview` skill.
- `plan`, `brand`, `images`, `publish`, `refresh`, `export` → only in who-let-the-blogs-out. `write` still places image markers and lists them in the publish checklist.

## Small requests

Title options, a meta description, an outline, or "does this read AI-written": answer from the matching file's rules without running the whole flow and without writing state. `headline-contract.md` covers titles and meta descriptions, `brief.md` Phase 7 covers outlines, and `review.md`'s stateless mode scores any file or pasted text.

Updating an article that's already published belongs to who-let-the-blogs-out's `refresh`. Say so rather than rewriting it from here.

The files under `references/`, `scripts/`, and `assets/` are copies of who-let-the-blogs-out's and are checked against it in CI. Change the originals, never these.
