# No-Argument Routing

Loaded when the user invokes this skill with no specific command in mind — "help me with my Claude Code setup," a bare mention of the skill, or similar. The job is to look at what actually exists and lead with the one or two most useful next steps, not to dump the full command table on someone who just wants to know what to do.

## Read first

- `.claude/nick-saban/registry.json`, if it exists.
- `git status --porcelain` — cheap, tells you if the tree is dirty.
- `git log -1 --format=%cI -- CLAUDE.md .claude/` — cheap, tells you when the harness itself last changed.

## Then pick, in this order

1. **No `.claude/nick-saban/` and no `CLAUDE.md`** → lead with `kickoff`. "There's no playbook here yet — want me to scaffold one?"
2. **No `.claude/nick-saban/` but `CLAUDE.md` exists** → lead with `check-playbook`. "There's a setup here already — worth scoring it before anyone changes it."
3. **`registry.json` shows `openHigh > 0`** → lead with whichever of `drill` / `adjust` owns the highest-severity open finding's rung (see `state.md`'s rung-ownership table), and quote that finding's `claim` verbatim so the recommendation is concrete, not generic.
4. **Open findings exist, all medium/low** → lead with whichever rung-owner (`drill` or `adjust`) has more open findings assigned to it; name the count.
5. **An order exists with `lastAttest: null` and the tree is dirty** → lead with `watch-film <slug>`, naming how many criteria are still unverified.
6. **`lastAuditAt` predates the last commit touching `CLAUDE.md` or `.claude/`** → lead with `check-playbook`. "The last score is older than your most recent config change — it might not reflect what's actually here now."
7. **None of the above** → run `scouting-report` and show the full command table below it, since there's nothing urgent enough to lead with.

Present two or three picks max, each with the exact command to type and a one-line reason drawn from what you actually found — not a generic description of what the command does. The full command table (from `SKILL.md`) goes below the recommendation as a fallback, not above it.

**Never auto-run anything.** A bare invocation is a question, not a green light. Even when the answer is obvious, ask for a one-word confirmation before doing something that writes files.
