# Gameplan

Interviews the repo and the user, then writes a work order for one upcoming change: goal, scope, explicit exclusions, constraints, and numbered acceptance criteria — each bound to a verify command that actually exists in this repo, not an aspirational one.

**Reads:** repo; the latest audit record's `verificationSurface` and any open `verification`-category findings
**Writes:** `orders/<slug>.md`, `registry.json`
**Stops at:** Never implements anything, never writes application code. Never binds a criterion to a command that isn't in `verificationSurface` without explicitly marking that criterion `unverifiable` and saying so out loud — a criterion nobody can check is worse than no criterion, because it looks like a guarantee. Ends at the written contract; building it is a separate session, deliberately starting with a clean context rather than one full of interview back-and-forth.

## Why this exists separately from just describing the feature

A description of what to build tells an agent what to do. It doesn't tell a *different* agent, later, how to check whether the first one actually did it — and by the time the work is "done," everyone's incentive is to believe it worked. Writing the acceptance criteria before the work starts, each one tied to a command that already runs in this repo, means `watch-film` isn't grading against a moving target or a vibe.

## Phase 1: Check the verification surface first

Before interviewing about the feature, look at the latest audit's `verificationSurface`. If it's stale or missing (no `check-playbook` has ever run, or it predates recent changes), say so and offer to run `check-playbook` first — writing criteria against commands you haven't confirmed exist defeats the point.

If there are open `verification`-category findings (e.g. no test command documented at all), that constrains what kind of criteria are even possible here — flag it plainly rather than writing hopeful criteria around a gap that should really be fixed with `drill` first.

## Phase 2: Interview

Two or three questions per round, not a form. Cover:

- What's the goal, in one or two sentences?
- What's explicitly out of scope — what should look untouched in the diff even though it's adjacent?
- What are the constraints (no new dependencies, must reuse existing X, must not change public API shape, etc.)?
- What would make this obviously wrong if it happened (edge cases, the failure mode the user is actually worried about)?

If the user can't yet answer what "done" looks like in checkable terms, stop and say this belongs on a `whiteboard` first — `gameplan` is for a change whose shape is already known well enough to contract, not for open-ended exploration.

## Phase 3: Draft numbered criteria

Each criterion needs plain-language text and one of three `verify` types:

- **A real command**, pulled from `verificationSurface` (or a specific invocation of one — `npm test -- imports/threshold`, not just `npm test`, when the criterion is that specific).
- **A diff-review check**, for criteria that are genuinely checkable but not by running a command — "no new dependency added," "the existing function's lines are untouched." Write `verify: "diff-review: <what to look for>"` rather than `unverifiable`. This isn't a gap — it's exactly what `watch-film`'s diff-scanning phase exists to do, and marking it `unverifiable` undersells a criterion that's perfectly checkable, just by reading rather than running.
- **`unverifiable`**, reserved for criteria that genuinely can't be checked either way — no command exists and no diff review would settle it either. This should be rare; if you find yourself reaching for it often, the criterion is probably too vague to be an acceptance criterion at all. Say so to the user rather than writing a soft one.

## Phase 4: Bind and confirm

Show the full draft — goal, scope, exclusions, constraints, and the criteria table with their verify commands — before writing. This is the contract; both sides should read it once, together, before it's final.

## Phase 5: Write

```markdown
---
slug: <kebab-case>
title: <human title>
created: <ISO date>
criteria:
  - id: AC-1
    text: <plain language>
    verify: <exact command>
    status: unmet
    evidence: null
outOfScope:
  - <item>
lastAttest: null
---

# <title>

## Goal
## Current behavior
## Desired behavior
## Constraints
## Interfaces affected
## Edge cases
## Completion report format
```

Fill in the body sections from the interview. Then run `scripts/build_registry.py` to add this order to the registry.

## Output

```
## Gameplan: <title>

Wrote `orders/<slug>.md` — <N> acceptance criteria, <M> bound to real verify
commands, <K> marked unverifiable (name them if any).

Out of scope: <list>

Build this in a fresh session, then run `watch-film <slug>` against the diff
when it's done.
```

## Confirm and stop

Never implements, never writes code. Never claims a criterion is checkable when it isn't. Ends at the contract.
