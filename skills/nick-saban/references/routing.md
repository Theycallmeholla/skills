# Orientation Routing

Loaded for the read-only intent: a bare invocation, `help`, `what next`, `what should I do`, `where do I stand`, "help me with my Claude Code setup." The job is to look at what actually exists and lead with the one or two most useful next steps, not to dump the full command table on someone who just wants to know what to do.

**This route writes nothing.** Not an audit record, not a note, not a registry refresh. A request for guidance is not approval to act on that guidance — the recommendation *is* the deliverable, and the turn ends there. A user asking "what's next?" and getting a completed audit they didn't ask for is the specific failure this file exists to prevent. Asking *what is wrong* (`audit`, `score`, `check`) is the other intent and routes to `check-playbook`, which does write.

## Read first

- `.claude/nick-saban/registry.json`, if it exists.
- `.claude/nick-saban/notes.md`, if it exists — only the `worked … awaiting re-check` lines.
- `git status --porcelain` — cheap, tells you if the tree is dirty.
- `git log -1 --format=%cI -- CLAUDE.md .claude/` — cheap, tells you when the harness itself last changed.

## Then pick, in this order

1. **No `.claude/nick-saban/` and no `CLAUDE.md`** → lead with `kickoff`. "There's no playbook here yet — want me to scaffold one?"
2. **No `.claude/nick-saban/` but `CLAUDE.md` exists** → lead with `check-playbook`. "There's a setup here already — worth scoring it before anyone changes it."
3. **`registry.json` shows `openHigh > 0`** → lead with whichever of `drill` / `adjust` owns the highest-severity open finding's rung (see `state.md`'s rung-ownership table), and quote that finding's `claim` verbatim so the recommendation is concrete, not generic. First set aside findings that `notes.md` marks `worked … awaiting re-check` with a date after `lastAuditAt`: they've been acted on, and only a re-check can close them. (Declines are already left out of `openHigh` by `build_registry.py`.) If that sets aside every open high, lead with `check-playbook <their categories>` instead.
4. **Open findings exist, all medium/low** → lead with whichever rung-owner (`drill` or `adjust`) has more open findings assigned to it; name the count.
5. **An order exists with `lastAttest: null` and the tree is dirty** → lead with `watch-film <slug>`, naming how many criteria are still unverified.
6. **`lastAuditAt` predates the last commit touching `CLAUDE.md` or `.claude/`** → lead with `check-playbook`. "The last score is older than your most recent config change — it might not reflect what's actually here now."
7. **None of the above** → run `scouting-report` and show the full command table below it, since there's nothing urgent enough to lead with.

## Output

End with the standard `Next` block from `SKILL.md` — on this route it's the whole response:

```
### Next

**Do this:** `<exact command, with arguments>`
<one-line reason drawn from what you actually found — the finding's own claim,
the staleness you measured, the order with unmet criteria>

**Instead, if <specific condition>:** `<alternative command>`
```

Two picks maximum, and **state which one you'd choose**. "You could run check-playbook or drill" is not an answer to "what should I do?" — it hands the decision back to someone who asked precisely because they didn't want to make it. The full command table stays out unless the user asks for `commands`.

Then always close with this one line, verbatim. It's a pointer, not the command table, so it doesn't compete with the pick above:

```
Also here: `gameplan` before building (write down what "done" means) · `watch-film` after (check the diff against it) · `/nick-saban commands` for everything else.
```

Without it, a bare invocation only ever points at the next fix, and a user can run the whole audit-and-fix loop without learning that the before/after-a-change commands exist. A secret-shopper run on 2026-10-07 hit exactly that.

**Never auto-run anything.** A bare invocation is a question, not a green light. Even when the answer is obvious, ask for a one-word confirmation before doing something that writes files — and recommending a command in the block above is not that confirmation.
