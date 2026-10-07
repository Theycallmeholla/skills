# Kickoff

Scaffolds a complete, coherent playbook for a project that has none, sized to what the repo actually is rather than a generic template, and writes a baseline audit record so the first `scouting-report` has something to compare against.

**Reads:** repo probe (package manager, test runner, CI config, VCS, stack, existing conventions); `references/ladder.md`; `references/findings.md`
**Writes:** `CLAUDE.md`, `.claude/rules/`, `.claude/agents/`, `.claude/settings.json`, `.claude/hooks/`, `registry.json`, `audits/001.json`
**Stops at:** Never touches application source or tests. Refuses to run if `CLAUDE.md` or `.claude/nick-saban/` already exists — points at `check-playbook` instead, since scaffolding over an existing setup is how work gets silently destroyed.

## Phase 0: Refuse if there's already something here

Before anything else, check for `CLAUDE.md` and `.claude/nick-saban/`. If either exists, stop and say so: "This repo already has a playbook — run `check-playbook` to see where it stands, or ask me to `kickoff` again explicitly if you really want a from-scratch rebuild." Don't silently overwrite. If the user does explicitly confirm a rebuild, treat the old files as something to review and fold in, not just delete.

## Phase 1: Probe the repo

Figure out, by actually looking rather than asking first:

- Language(s), package manager, and how dependencies are installed
- Test runner and the actual command to invoke it (read `package.json#scripts`, not just guess from the language)
- Typecheck, lint, and build commands, same way
- CI config, if any, and what it currently runs
- VCS state — is this a fresh repo, does it have history, are there existing branches suggesting multiple contributors or parallel work
- Existing conventions worth preserving — a `.editorconfig`, an existing lint config, a monorepo structure, anything that should shape what gets written rather than being overwritten by a generic template

Size the scaffold to what you find. A five-file weekend project doesn't need the same `.claude/rules/` structure as a monorepo with three deployable services — over-scaffolding a small repo is itself a `bounds`-category problem waiting to be flagged on the very first `check-playbook`.

## Phase 2: Propose before writing

Show the user the full tree you intend to create and the actual contents of each file — not a description of what it will contain. This is the one command in the system that writes a large amount of new material at once, so it earns an upfront review the way `drill`'s per-mechanism approval does for its own reasons.

What to draft:
- `CLAUDE.md` — commands, non-obvious gotchas discovered in Phase 1, architecture notes, and a short evidence-and-scope discipline section (name the verify commands, ask for the smallest viable diff). Keep it lean; this file is a cost paid every session. Don't restate anything the repo already makes obvious.
- `.claude/rules/` — only for genuinely path- or domain-scoped conventions found in Phase 1 (e.g. a frontend/backend split). Skip this directory entirely if nothing in the repo justifies it yet.
- `.claude/agents/` — only if the repo's shape suggests a genuinely isolated subagent is worth predefining (e.g. a security-review agent for a repo handling auth). Most kickoffs won't need this.
- `.claude/settings.json` — sane default permissions: no destructive git unrestricted, a deny rule on `.env`/credentials/production config if any are visible, and a `Bash` allow scoped to what Phase 1 actually found in use rather than a blanket allow.
- `.claude/hooks/` — only for something Phase 1 gives concrete evidence needs automatic enforcement right away (e.g. a formatter already configured but not wired to run automatically). Don't invent hooks speculatively — that's the over-enforcement failure mode `ladder.md` warns about.

## Phase 3: Write on approval

Once approved, write every file, then assemble a baseline `audits/001.json` — not from a real detection pass (there's nothing to find yet in a freshly-scaffolded repo, by construction), but as the record format's first entry. Use `scripts/merge_pass.py` with an empty raw-findings array and **`--pass-type scaffold`**, then `scripts/build_registry.py`, rather than hand-writing pass 1 differently from every pass after it.

`--pass-type scaffold` is what stops this record from claiming a score of 100. An empty findings list here means "nothing was looked for," which is not the same fact as "nothing is wrong" — and a metric where the best possible number also means *unexamined* is a metric that has to be explained away every time someone reads it. The record scores `null` with `status: "unassessed"` instead. Report it that way in the output; never round it up to a number.

## Output

```
## Kickoff complete

Scaffolded for: <one-line description of what was detected about the repo>

**Created:**
[file tree]

**State: UNASSESSED** — this pass scaffolded the playbook; no detection has run
against it yet. That is not a score of 100, and don't report it as one.

### Next

**Do this:** `check-playbook`
Scores what was just scaffolded and gives you a real baseline — right now there's
a playbook but no evidence it holds.

**Instead, if you want to start building immediately:** `gameplan <what you're building>`
The audit will still be there afterward.
```

## Confirm and stop

Never touches application source or tests. Never runs against a repo that already has a playbook without explicit confirmation to rebuild. Never writes a hook without showing its exact contents first.
