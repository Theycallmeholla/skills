# Drill

Works the findings whose remedy sits on the `hook`, `permission`, `ci`, or `test` rungs — moving each requirement down to the lowest rung that actually holds, and deleting the prose it supersedes.

**Reads:** latest `audits/` record filtered to those four rungs; `verificationSurface` from that record; `notes.md`; `references/ladder.md`
**Writes:** `.claude/hooks/**`, `.claude/settings.json`, `.github/workflows/**` (or wherever CI is actually configured), `package.json#scripts` or `Makefile`, `notes.md`
**Stops at:** Never writes anything without showing the exact file diff and getting approval, one mechanism per round — never batch these. Never weakens or removes an existing guard. Never writes application tests — drafts one and stops, since that crosses into work the user should own. Never marks a finding resolved; that's `check-playbook`'s job alone. Never writes `waived.json` directly — if the user declines a proposed mechanism, load `references/decline.md` and follow it instead of just moving on silently.

## Why this one is slower than `adjust`

A hook that's subtly wrong doesn't just fail to help — it can block every future session until someone notices and removes it. A `settings.json` permission rule that's too broad does nothing; one that's too narrow can lock the user out of their own repo mid-task. This is the entire reason `drill` gets a stricter approval discipline than `adjust`: the failure modes here are worse than doing nothing, where `adjust`'s worst case is a slightly-off sentence.

## Phase 1: Select

Take the findings whose `rung` is `hook`, `permission`, `ci`, or `test` from the latest audit record. Group by rung — permission changes are usually quick and low-risk to review together; hooks and CI gates deserve individual attention.

## Phase 2: Pick the rung (re-confirm, don't just trust the record)

The finding already suggests a rung, but confirm it's still the right one given `ladder.md`'s "lowest sufficient" rule — a finding recorded weeks ago might be better served by a lighter mechanism than the one that seemed necessary at the time, or the repo might have grown enough that something originally fine as a hook now needs to be a CI gate to hold across contributors.

## Phase 3: Draft the mechanism

Write the actual hook script, permission rule, or CI step — not a description of one. For a hook, include what event it binds to and exactly what it runs. For a permission rule, show the literal `settings.json` diff. For a test, draft it and explicitly hand it to the user rather than adding it yourself (see the stop condition above) — name the specific behavior it should assert and let them place it in their suite.

Always pair the new mechanism with the deletion of the prose it replaces. Leaving the old sentence in `CLAUDE.md` after the hook exists is exactly the kind of paid-for-nothing content `check-playbook`'s `context` category exists to catch, and leaving it there defeats the purpose of drilling it in the first place.

## Phase 4: Dry-run if possible

Before asking for approval, if you can safely test the mechanism without side effects (e.g., run the hook script against a scratch file, validate the `settings.json` syntax), do so and mention the result. A mechanism you've verified to at least parse and run is a materially different approval ask than one you haven't touched.

## Phase 5: Approve, one at a time

Show the exact diff — the new file or the exact settings.json change — and the CLAUDE.md deletion together, as one unit, and wait for explicit approval before writing. Do not queue up multiple mechanisms and ask for one blanket approval; that's the batching this command explicitly must not do.

## Phase 6: Write

On approval, write the mechanism and delete the superseded prose in the same pass. Do not touch the finding's status in the audit record — leave that to the next `check-playbook`.

## Output

Per mechanism approved:

```
### <finding id>: <one-line description of the mechanism>

**Adds:** <file path and what it does>
**Removes:** <the CLAUDE.md line(s) it replaces>

[the actual diff]

Approve to write this?
```

After all approved mechanisms are written:

```
Wrote <N> mechanisms. Run `check-playbook` to confirm they're holding —
nothing here marks these findings resolved; the next check-playbook does that
by observing the signals stop firing.
```

## Confirm and stop

One mechanism per approval round, always. Never weakens an existing guard. Never writes an application test outright. Never asserts a finding is resolved.
