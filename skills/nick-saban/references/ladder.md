# The Enforcement Ladder

Loaded by `kickoff`, `check-playbook`, `adjust`, and `drill` — the four commands that either pick a rung for a new requirement or act on one someone else already picked.

## Why a ladder instead of a checklist

An instruction can be true and still not happen. "Always run the formatter" is a completely reasonable thing to want, and it will still be ignored on a tired pass through a long `CLAUDE.md`, because prose competes with everything else in context for attention. The ladder is a way of asking, for every requirement: *if this got ignored tomorrow, what's the cheapest change that would make ignoring it impossible?*

```
prose  →  scoped-rule  →  skill  →  hook  →  permission  →  ci  →  test
(weakest, cheapest to write)                    (strongest, hardest to ignore)
```

## What each rung actually is

- **prose** — a sentence in `CLAUDE.md` or a reference file. Advisory. Costs nothing to write, costs attention every session, and is trivially ignored under pressure.
- **scoped-rule** — the same sentence, but living in `.claude/rules/` and loaded only when relevant, instead of in the root file paid for on every session. Same enforcement strength as prose; the win here is entirely a context-budget win, not a compliance win.
- **skill** — a full on-demand procedure, loaded only when invoked. Stronger than prose because the procedure is complete and can't be half-remembered, but still advisory — nothing forces the skill to be invoked.
- **hook** — a script that runs automatically on an event (`PostToolUse`, `PreToolUse`, etc.). The requirement now executes without anyone deciding to run it. This is the first rung where "ignoring it" stops being possible in the normal course of work.
- **permission** — a `settings.json` allow/deny rule. Doesn't just remind the agent not to do something; makes the action unavailable.
- **ci** — a pipeline gate. Enforced not just in this session but on every future change, by every contributor, including humans.
- **test** — a specific assertion that fails when the requirement is violated. The strongest rung: it names the exact behavior and breaks loudly the moment that behavior regresses.

## Picking a rung

**The rule is "lowest sufficient," not "highest available."** A hook for something a one-line rule would have caught is its own kind of waste — more code to maintain, more places a repo's automation can break, more surface for the exact "overengineering" failure mode the source material warns about. Ask, in order:

1. Would a plain rule actually get read and followed here? If genuinely yes (the requirement is rare, low-stakes, and the repo is small enough that context isn't crowded), stop at `prose` or `scoped-rule`.
2. Is this something an agent does occasionally and needs full instructions for, but doesn't need enforced every time? → `skill`.
3. Does this need to happen automatically, every time, without anyone remembering to ask for it? → `hook`.
4. Is this about restricting what's *possible*, not just what's *done*? → `permission`.
5. Does this need to hold across every future contributor and every future session, not just this one? → `ci`.
6. Is there a specific, nameable behavior whose regression should break a build? → `test`.

**Ownership for routing purposes:** `adjust` works `prose` / `scoped-rule` / `skill` findings. `drill` works `hook` / `permission` / `ci` / `test` findings. This split exists because the four higher rungs write executable code or config that can wedge every future session if done carelessly — they need per-mechanism approval before writing. The three lower rungs are text changes an agent can make in one pass.

## Re-picking a rung on an existing requirement

The same rule applies in reverse. A requirement is misplaced when:

- **Under-enforced**: it's on `prose` but nothing has actually followed it in practice (repeated findings with the same signal across passes is direct evidence of this).
- **Over-enforced**: it's on `hook` or `permission` but a plain rule would have worked just as well, and now there's a script to maintain for something that was never actually being violated.

Both are findings worth raising. The second is rarer but real, and worth naming explicitly when you see it — the goal is proportionate enforcement, not maximum enforcement.
