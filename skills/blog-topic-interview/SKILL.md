---
name: blog-topic-interview
description: >-
  Standalone version of the interview step from who-let-the-blogs-out. Before a blog
  post is written under someone's name, asks what they actually think about the topic —
  their stance, real examples, numbers, and what must never be said — then saves an
  Opinion Packet and a per-client opinion bank in the project's .blog/ folder, using the
  same files and rules as who-let-the-blogs-out so a project can move to the full system
  without migrating anything. Use when the user says "interview me about this topic",
  "get my take first", "ask me what I think before you write", or "update my opinion
  bank", or names this skill. If who-let-the-blogs-out is installed, use its interview
  command instead; this skill is for setups that have only this step. Blog and article
  topics only — not emails, docs, or social posts.
---

# Blog Topic Interview

A post published under someone's name should say what that person actually thinks. This skill collects the things nobody else can supply — their stance, their real stories, their numbers, their boundaries — before any drafting starts, and files them where every later post can find them.

It is the `interview` command of who-let-the-blogs-out, packaged on its own. The rules are not paraphrased here; they are the same files.

## Run it

1. Load `references/governing-rules.md`, `references/state.md`, and `references/reporting.md`.
2. Follow `references/interview.md` from top to bottom, with the one override below.

Everything in `interview.md` applies as written: at most three questions at a time, never re-ask what the bank already answers, every opinion-bank entry carries provenance, numbers go to `facts.json`, and the packet lands at `.blog/posts/<slug>/packet.md`.

## The one override: no `.blog/` yet

`interview.md` says that when `.blog/` is missing you should point at `brand`. This skill doesn't have `brand`, so create the same starting tree that `brand` creates, and nothing more.

Settle the client slug first: lowercase and hyphenated, from the domain or business name (`cursivemedia.com` → `cursive-media`). It appears in every path and is never renamed, so show it to the user before writing anything.

```
.blog/
├── registry.json              {"version": 1, "clients": [<client row>], "posts": []}
└── clients/<slug>/
    ├── brand.md               frontmatter + the seven headings from state.md
    ├── opinion-bank.md        assets/opinion-bank-template.md, minus its ## Specifics section
    ├── facts.json             {"version": 1, "facts": []}
    └── notes.md               a single `# Notes — <name>` heading
```

- **Client row:** `slug`, `name`, `domain` (or `null`), `brandProfile: "missing"`, `bankEntries: 0`, `updated` set to today.
- **`brand.md`:** frontmatter with `client`, `name`, `domain`, `sitemap: null`, `updated`, `source: null`. Under each of the seven headings, write `**Not captured.** Ask in the next brand pass.` Never fill a brand section from guesses about the business.
- **Leave `posts/` alone** until `interview.md` creates the post folder.

If `.blog/` exists but this client doesn't, create `clients/<slug>/` with the same four files and add the client row. Create the client folder whole, never file by file.

Then say once, in one line, that the brand profile is empty and that who-let-the-blogs-out's `brand` command fills it if they adopt the full system.

**Never write into this skill's own folder.** `assets/opinion-bank-template.md` is only ever copied out. A bank saved inside a skill is lost when the skill is updated, and it carries one client's private positions into every other project.

## Names that point outside this skill

The shared files mention other who-let-the-blogs-out commands. Where one says to hand off to a command this skill doesn't have, stop and name the next step. Don't improvise it.

- `brief` and `write` → the `seo-blog-writer` skill runs both, or who-let-the-blogs-out if installed.
- `brand`, `plan`, `verify`, `images`, `review`, `revise`, `publish`, `refresh`, `export` → only in who-let-the-blogs-out.

## Hand off

When the packet is written, the next step is the brief and draft. Say that `seo-blog-writer` picks up from `.blog/posts/<slug>/packet.md`.

The files under `references/` and `assets/` are copies of who-let-the-blogs-out's and are checked against it in CI. Change the originals, never these.
